# app.py - Central Integration Server for LASO App
import os
import sys
import warnings
import sqlite3
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

# Suppress unclosed SQLite connection ResourceWarnings globally across all threads
warnings.showwarning = lambda *a, **kw: None

# Force UTF-8 encoding for standard output to avoid UnicodeEncodeError on Windows terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ----------------------------------------------------
# 1. Add Modular Component Subfolders to Python Path
# ----------------------------------------------------
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(CURRENT_DIR, 'LASO - Back End'))
sys.path.append(os.path.join(CURRENT_DIR, 'Mem 3'))
sys.path.append(os.path.join(CURRENT_DIR, 'member4'))
sys.path.append(os.path.join(CURRENT_DIR, 'Rating _system'))

# ----------------------------------------------------
# 2. Imports from Team Modules
# ----------------------------------------------------
try:
    from database import Database
    print("[OK] Imported Member 1 Database Module successfully.")
except ImportError as e:
    print(f"Error importing Database module: {e}")
    sys.exit(1)

try:
    from location_service import LocationService, get_location_service
    print("[OK] Imported Member 3 Location & Search Module successfully.")
except ImportError as e:
    print(f"Error importing Location module: {e}")
    sys.exit(1)

try:
    from user_management import UserManagement
    from communication import Communication
    print("[OK] Imported Member 4 Validation & Communication Module successfully.")
except ImportError as e:
    print(f"Error importing Validation/Communication module: {e}")
    sys.exit(1)

try:
    from rating_sys import RatingSystem
    from models import ServiceCategory
    print("[OK] Imported Member 5 Rating System Module successfully.")
except ImportError as e:
    print(f"Error importing Rating System module: {e}")
    sys.exit(1)

# ----------------------------------------------------
# 3. Extend Member 1's SQLite Database with missing methods
# ----------------------------------------------------
# This avoids modifying Member 1's file directly, preserving their work
# while providing all methods needed by Member 4's communication layer.
class ExtendedDatabase(Database):
    def get_user_by_email(self, email: str):
        """Get user record by email (needed for user validation check)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE email = ?", (email.strip().lower(),))
            row = cursor.fetchone()
            return dict(row) if row else None

    def get_customer_by_id(self, customer_id: int):
        """Get customer profile by customer_id (needed to look up customer names for reviews)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
            row = cursor.fetchone()
            return dict(row) if row else None

    def update_provider_profile(self, user_id: int, business_name: str, phone: str, address: str, description: str) -> bool:
        """Update provider profile details"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE providers
                SET business_name = ?, phone = ?, address = ?, description = ?
                WHERE user_id = ?
            """, (business_name, phone, address, description, user_id))
            return cursor.rowcount > 0

    def add_review(self, provider_id: int, customer_id: int, rating: int, comment: str):
        """Override add_review to fix database lock collision in Member 1's SQLite code"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reviews (provider_id, customer_id, rating, comment) VALUES (?, ?, ?, ?)",
                    (provider_id, customer_id, rating, comment)
                )
        except sqlite3.IntegrityError:
            return (False, "Already reviewed this provider")
        except Exception as e:
            return (False, f"Error: {str(e)}")

        # Calculate and update ratings in a separate transaction after the INSERT is committed
        self._update_provider_rating(provider_id)
        return (True, "Review added")

    # --- Messaging / Communication Adaptation ---
    def save_message(self, message_data):
        """Save a new chat message into the messages table"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message, is_read) VALUES (?, ?, ?, ?)",
                (message_data['sender_id'], message_data['receiver_id'], message_data['message'], 1 if message_data['is_read'] else 0)
            )
            return cursor.lastrowid

    def get_user_messages(self, user_id, include_read=True):
        """Get all messages sent or received by a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if include_read:
                cursor.execute("SELECT * FROM messages WHERE sender_id = ? OR receiver_id = ? ORDER BY created_at DESC", (user_id, user_id))
            else:
                cursor.execute("SELECT * FROM messages WHERE (sender_id = ? OR receiver_id = ?) AND is_read = 0 ORDER BY created_at DESC", (user_id, user_id))
            rows = cursor.fetchall()
            return [self._map_message_row(dict(r)) for r in rows]

    def get_chat_history(self, user1_id, user2_id, limit=50):
        """Get conversation history between two specific users"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?) ORDER BY created_at ASC LIMIT ?",
                (user1_id, user2_id, user2_id, user1_id, limit)
            )
            rows = cursor.fetchall()
            return [self._map_message_row(dict(r)) for r in rows]

    def get_conversations(self, user_id):
        """Get all conversation threads for a user with the last message of each thread"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            # Fetch latest message per partner
            cursor.execute("""
                SELECT 
                    CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS partner_id,
                    message AS last_message,
                    created_at AS timestamp,
                    is_read
                FROM messages
                WHERE message_id IN (
                    SELECT MAX(message_id)
                    FROM messages
                    WHERE sender_id = ? OR receiver_id = ?
                    GROUP BY CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END
                )
                ORDER BY created_at DESC
            """, (user_id, user_id, user_id, user_id))
            rows = cursor.fetchall()
            
            conversations = []
            for r in rows:
                partner_id = r['partner_id']
                
                # Fetch partner's profile information
                cursor.execute("SELECT user_type, email FROM users WHERE user_id = ?", (partner_id,))
                u_row = cursor.fetchone()
                partner_name = "Unknown User"
                partner_service = ""
                
                if u_row:
                    user_type = u_row['user_type']
                    if user_type == 'provider':
                        cursor.execute("SELECT business_name, service_type FROM providers WHERE user_id = ?", (partner_id,))
                        p_row = cursor.fetchone()
                        if p_row:
                            partner_name = p_row['business_name']
                            partner_service = p_row['service_type']
                    else:
                        cursor.execute("SELECT full_name FROM customers WHERE user_id = ?", (partner_id,))
                        c_row = cursor.fetchone()
                        if c_row:
                            partner_name = c_row['full_name']
                
                conversations.append({
                    'partnerId': partner_id,
                    'partnerName': partner_name,
                    'partnerService': partner_service,
                    'lastMessage': r['last_message'],
                    'timestamp': r['timestamp']
                })
            return conversations

    def mark_message_as_read(self, message_id):
        """Mark a single message as read"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_read = 1 WHERE message_id = ?", (message_id,))
            return cursor.rowcount > 0

    def mark_all_messages_read(self, user_id, partner_id):
        """Mark all received messages in a thread as read"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE messages SET is_read = 1 WHERE receiver_id = ? AND sender_id = ?", (user_id, partner_id))
            return cursor.rowcount

    def _map_message_row(self, row):
        """Helper to map SQLite messages table fields to dict format for Member 4 & frontend"""
        return {
            'id': row['message_id'],
            'sender_id': row['sender_id'],
            'receiver_id': row['receiver_id'],
            'senderId': row['sender_id'],
            'receiverId': row['receiver_id'],
            'message': row['message'],
            'text': row['message'],
            'sent_at': row['created_at'],
            'timestamp': row['created_at'],
            'is_read': bool(row['is_read']),
            'is_deleted_by_sender': False,
            'is_deleted_by_receiver': False
        }


# Initialize Database using Member 1's SQLite file
DB_PATH = os.path.join(CURRENT_DIR, 'LASO - Back End', 'laso_app.db')
db = ExtendedDatabase(db_path=DB_PATH)

# Initialize Member 4 logic classes
user_manager = UserManagement(database=db)
comm_service = Communication(database=db)

# Initialize Member 3 location service
loc_service = LocationService()

# ----------------------------------------------------
# 4. Helper Mapping Mappers (Bridges Database & Frontend/Search formats)
# ----------------------------------------------------
def map_provider_for_frontend(p):
    """Maps database provider dictionary to the keys expected by Member 3 search and frontend"""
    # Get user email
    user_record = db.get_user_by_id(p['user_id'])
    email = user_record['email'] if user_record else ""
    
    return {
        'id': p['provider_id'],
        'provider_id': p['provider_id'],
        'user_id': p['user_id'],
        'name': p['business_name'],
        'business_name': p['business_name'],
        'category': p['service_type'],
        'service_type': p['service_type'],
        'serviceType': p['service_type'], # used in frontend JS
        'phone': p['phone'],
        'address': p['address'],
        'description': p['description'] or '',
        'latitude': p['latitude'],
        'longitude': p['longitude'],
        'lat': p['latitude'], # frontend JS
        'lon': p['longitude'], # frontend JS
        'rating': p['average_rating'] or 0.0,
        'avgRating': round(p['average_rating'] or 0.0, 1), # frontend JS
        'reviewsCount': p['total_ratings'] or 0, # frontend JS
        'total_reviews': p['total_ratings'] or 0,
        'available': True,
        'email': email
    }

# ----------------------------------------------------
# 5. Web Server Configuration (Flask)
# ----------------------------------------------------
app = Flask(__name__)
CORS(app) # Allow HTML/JS to connect

# Serve static frontend files directly (Convenience method to access the app easily)
@app.route('/')
def root():
    return send_from_directory(os.path.join(CURRENT_DIR, 'frontend'), 'index.html')

# Serve static frontend folder
@app.route('/frontend/<path:filename>')
def serve_frontend(filename):
    return send_from_directory(os.path.join(CURRENT_DIR, 'frontend'), filename)

# ----------------------------------------------------
# 6. REST API Endpoints
# ----------------------------------------------------

# --- User & Provider Management ---

@app.route('/api/register', methods=['POST'])
def register():
    """Register a customer or service provider with Member 4 input validation & security hashing"""
    data = request.get_json()
    
    # 1. Validation check using Member 4's user_management module
    service_type = data.get('serviceType') or data.get('service_type')
    is_valid, error_msg = user_manager.validate_user_input(
        email=data.get('email'),
        password=data.get('password'),
        confirm_password=data.get('password'), # assume passwords match
        phone=data.get('phone'),
        name=data.get('name'),
        district=data.get('district'),
        address=data.get('address'),
        service_type=service_type if data.get('userType') == 'provider' else None
    )
    
    if not is_valid:
        print(f"❌ Registration Validation Failed: {error_msg}")
        return jsonify({'success': False, 'message': error_msg}), 400

    # 2. Hash password using Member 4's SHA-256 algorithm
    hashed_password = user_manager.hash_password(data['password'])

    # 3. Create user record in SQLite via Member 1's database core
    success, user_id, message = db.register_user(
        data['email'].strip().lower(), 
        hashed_password, 
        data['userType']
    )
    
    if not success:
        print(f"❌ Database Registration Failed: {message}")
        return jsonify({'success': False, 'message': message}), 400

    # 4. Populate Profile (Customer vs Provider) in SQLite
    if data['userType'] == 'customer':
        db.create_customer_profile(
            user_id=user_id,
            full_name=data['name'],
            phone=data['phone'],
            address=data.get('address', '')
        )
    elif data['userType'] == 'provider':
        lat = data.get('lat')
        lon = data.get('lon')
        db.create_provider_profile(
            user_id=user_id,
            business_name=data['name'],
            service_type=service_type,
            phone=data['phone'],
            address=data['address'],
            description=data.get('description', ''),
            latitude=float(lat) if lat else None,
            longitude=float(lon) if lon else None
        )

    # 5. Return session format expected by frontend JS
    return jsonify({
        'success': True,
        'userId': user_id,
        'userType': data['userType'],
        'name': data['name'],
        'email': data['email'],
        'phone': data['phone'],
        'district': data.get('district', 'Colombo'),
        'address': data.get('address', '')
    })

@app.route('/api/login', methods=['POST'])
def login():
    """Authenticate user with Member 4 password verification and load their SQLite profile details"""
    data = request.get_json()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # 1. Fetch user from SQLite
    user = db.get_user_by_email(email)
    if not user:
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    # 2. Verify hashed password using Member 4's user_management helper
    if not user_manager.verify_password(password, user['password']):
        return jsonify({'success': False, 'message': 'Invalid email or password'}), 401

    user_id = user['user_id']
    user_type = user['user_type']

    # 3. Retrieve profile information
    name = ""
    phone = ""
    address = ""
    district = "Colombo" # Default fallback

    if user_type == 'customer':
        profile = db.get_customer_by_user_id(user_id)
        if profile:
            name = profile['full_name']
            phone = profile['phone']
            address = profile['address'] or ''
    elif user_type == 'provider':
        profile = db.get_provider_by_user_id(user_id)
        if profile:
            name = profile['business_name']
            phone = profile['phone']
            address = profile['address']
            # Determine district from address
            for d in ["Colombo", "Gampaha", "Kalutara", "Kandy", "Galle", "Matara", "Jaffna"]:
                if d.lower() in address.lower():
                    district = d
                    break

    # 4. Return session data format expected by frontend auth handlers
    return jsonify({
        'success': True,
        'userId': user_id,
        'userType': user_type,
        'name': name,
        'email': email,
        'phone': phone,
        'district': district,
        'address': address
    })


# --- Location-Based Provider Search (Member 3 & Member 1) ---

@app.route('/api/providers/nearby', methods=['GET'])
def get_nearby_providers():
    """Location Search sorting & filtering nearby service providers using Member 3 Haversine logic"""
    # Fetch parameters
    lat_val = request.args.get('lat')
    lon_val = request.args.get('lon')
    district = request.args.get('district', '')
    service = request.args.get('service', '')
    query = request.args.get('query', '')

    # Load all providers from SQLite database
    db_providers = db.get_all_providers()
    mapped_providers = [map_provider_for_frontend(p) for p in db_providers]

    # Hook database providers into Member 3 LocationService
    loc_service.set_providers(mapped_providers)

    # Perform proximity and keyword search sorting
    if lat_val and lon_val:
        try:
            lat = float(lat_val)
            lon = float(lon_val)
            # Find nearby providers (within default 15km radius) sorted by distance
            results = loc_service.search_providers(
                query=query,
                user_lat=lat,
                user_lon=lon,
                category=service or None,
                radius=15.0 # default radius limit
            )
            return jsonify(results)
        except ValueError:
            pass # fallback if coords are not floats

    # Fallback to simple filtering if coordinates are absent
    filtered = mapped_providers
    if service:
        filtered = [p for p in filtered if p['category'].lower() == service.lower()]
    if query:
        q = query.lower()
        filtered = [p for p in filtered if q in p['name'].lower() or q in p['description'].lower()]
        
    return jsonify(filtered)


# --- Provider Profiles & Reviews (Member 5 & Member 1) ---

@app.route('/api/provider/<int:provider_id>', methods=['GET'])
def get_provider_details(provider_id):
    """Retrieve detailed provider profile and all reviews from SQLite"""
    # 1. Fetch provider details
    p = db.get_provider_by_id(provider_id)
    if not p:
        return jsonify({'message': 'Provider not found'}), 404
        
    mapped_p = map_provider_for_frontend(p)

    # 2. Fetch reviews for provider from SQLite
    db_reviews = db.get_provider_reviews(provider_id)
    
    # 3. Format reviews & look up customer names (needed for frontend UI render)
    formatted_reviews = []
    for r in db_reviews:
        customer = db.get_customer_by_id(r['customer_id'])
        customer_name = customer['full_name'] if customer else "Anonymous"
        formatted_reviews.append({
            'id': r['review_id'],
            'providerId': r['provider_id'],
            'customerName': customer_name,
            'rating': r['rating'],
            'comment': r['comment'],
            'date': r['created_at'].split()[0] if r['created_at'] else ""
        })
        
    mapped_p['reviews'] = formatted_reviews
    return jsonify(mapped_p)

@app.route('/api/review', methods=['POST'])
def add_review():
    """Submit a rating and comment for a provider using Member 1's DB average updates"""
    data = request.get_json()
    provider_id = data.get('provider_id')
    customer_user_id = data.get('customer_id') # user_id from frontend
    rating = int(data.get('rating', 5))
    comment = data.get('comment', '')

    # 1. Look up SQLite customer_id using user_id
    customer = db.get_customer_by_user_id(customer_user_id)
    if not customer:
        return jsonify({'success': False, 'message': 'Customer profile not found'}), 404
    customer_id = customer['customer_id']

    # 2. Save review to SQLite (database class automatically updates the provider's score!)
    success, message = db.add_review(
        provider_id=provider_id,
        customer_id=customer_id,
        rating=rating,
        comment=comment
    )

    return jsonify({'success': success, 'message': message})

@app.route('/api/provider/profile', methods=['GET'])
def get_provider_profile():
    """Get active provider's profile using their user_id"""
    user_id = request.args.get('id')
    if not user_id:
        return jsonify({'message': 'Missing user id'}), 400

    p = db.get_provider_by_user_id(int(user_id))
    if not p:
        return jsonify({'message': 'Profile not found'}), 404

    return jsonify(map_provider_for_frontend(p))

@app.route('/api/provider/profile/update', methods=['POST'])
def update_provider_profile():
    """Update profile details of a service provider"""
    data = request.get_json()
    user_id = data.get('id')
    name = data.get('name')
    phone = data.get('phone')
    address = data.get('address')
    description = data.get('description', '')

    if not user_id:
        return jsonify({'success': False, 'message': 'Missing user id'}), 400

    success = db.update_provider_profile(
        user_id=int(user_id),
        business_name=name,
        phone=phone,
        address=address,
        description=description
    )

    return jsonify({'success': success})


# --- Communication / Chat system (Member 4 & Member 1) ---

@app.route('/api/conversations', methods=['GET'])
def get_conversations():
    """Retrieve all conversations for a user with the latest thread preview"""
    user_id_val = request.args.get('user_id')
    if not user_id_val:
        return jsonify({'message': 'Missing user_id'}), 400
    
    conversations = db.get_conversations(int(user_id_val))
    return jsonify(conversations)

@app.route('/api/messages/thread', methods=['GET'])
def get_message_thread():
    """Get the message history between two specific users"""
    user_id_val = request.args.get('user_id')
    partner_id_val = request.args.get('partner_id')

    if not user_id_val or not partner_id_val:
        return jsonify({'message': 'Missing user_id or partner_id'}), 400

    history = db.get_chat_history(int(user_id_val), int(partner_id_val))
    return jsonify(history)

@app.route('/api/message', methods=['POST'])
def send_message():
    """Send a chat message utilizing Member 4's communication sanitation and Member 1's SQLite storage"""
    data = request.get_json()
    sender_id = int(data.get('sender_id'))
    receiver_id = int(data.get('receiver_id'))
    message = data.get('message', '')

    # Call Member 4's communication layer to sanitize & store message in the DB
    success, msg, msg_id = comm_service.send_message(
        sender_id=sender_id,
        receiver_id=receiver_id,
        message=message
    )

    if not success:
        return jsonify({'success': False, 'message': msg}), 400

    return jsonify({
        'success': True,
        'message_id': msg_id,
        'senderId': sender_id,
        'receiverId': receiver_id,
        'text': message,
        'timestamp': db._map_message_row({'message_id': msg_id, 'sender_id': sender_id, 'receiver_id': receiver_id, 'message': message, 'is_read': 0, 'created_at': 'Just now'})['timestamp']
    })


# ----------------------------------------------------
# 7. Start Server
# ----------------------------------------------------
if __name__ == '__main__':
    print("=" * 55)
    print("[START] LASO SERVICE LOCATING MOBILE APP BACKEND RUNNING")
    print("=" * 55)
    print("  Server address: http://localhost:8000")
    print("  REST endpoints enabled:")
    print("  - POST http://localhost:8000/api/register")
    print("  - POST http://localhost:8000/api/login")
    print("  - GET  http://localhost:8000/api/providers/nearby")
    print("  - GET  http://localhost:8000/api/provider/<id>")
    print("  - POST http://localhost:8000/api/review")
    print("  - GET  http://localhost:8000/api/conversations")
    print("  - GET  http://localhost:8000/api/messages/thread")
    print("  - POST http://localhost:8000/api/message")
    print("=" * 55)
    app.run(debug=True, host='0.0.0.0', port=8000)
