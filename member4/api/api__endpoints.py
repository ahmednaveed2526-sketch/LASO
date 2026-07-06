"""
api_endpoints.py - Flask API Endpoints
Connects frontend to Member 4 functionality
"""

from flask import Flask, request, jsonify, session
from flask_cors import CORS
import sys
import os

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from member4.user_management import UserManagement
from member4.communication import Communication

# Initialize Flask app
app = Flask(__name__)
app.secret_key = 'laso_secret_key_2026'
CORS(app)  # Enable CORS for frontend

# Initialize your classes
user_mgmt = UserManagement()  # Will connect to database when Member 1 provides it
comm = Communication()        # Will connect to database when Member 1 provides it

# ==================== HEALTH CHECK ====================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Member 4 - User & Communication Service',
        'version': '1.0.0'
    })

# ==================== USER VALIDATION ENDPOINTS ====================

@app.route('/api/validate/email', methods=['POST'])
def validate_email():
    """Validate email address"""
    data = request.json
    email = data.get('email', '')
    
    is_valid, error = user_mgmt.validate_email(email)
    
    return jsonify({
        'valid': is_valid,
        'error': error if not is_valid else None
    })

@app.route('/api/validate/phone', methods=['POST'])
def validate_phone():
    """Validate phone number"""
    data = request.json
    phone = data.get('phone', '')
    
    is_valid, error = user_mgmt.validate_phone(phone)
    
    return jsonify({
        'valid': is_valid,
        'error': error if not is_valid else None
    })

@app.route('/api/validate/password', methods=['POST'])
def validate_password():
    """Validate password strength"""
    data = request.json
    password = data.get('password', '')
    confirm = data.get('confirm_password', '')
    
    is_valid, error = user_mgmt.validate_password(password, confirm)
    
    # Also get password strength analysis
    strength_analysis = user_mgmt.get_password_strength(password)
    
    return jsonify({
        'valid': is_valid,
        'error': error if not is_valid else None,
        'strength': strength_analysis
    })

@app.route('/api/validate/all', methods=['POST'])
def validate_all():
    """Validate all user inputs"""
    data = request.json
    
    is_valid, error = user_mgmt.validate_user_input(
        email=data.get('email', ''),
        password=data.get('password', ''),
        confirm_password=data.get('confirm_password', ''),
        phone=data.get('phone', ''),
        name=data.get('name', ''),
        district=data.get('district', ''),
        address=data.get('address', ''),
        service_type=data.get('service_type')
    )
    
    return jsonify({
        'valid': is_valid,
        'error': error if not is_valid else None
    })

# ==================== USER AUTHENTICATION ENDPOINTS ====================

@app.route('/api/auth/register', methods=['POST'])
def register_user():
    """Register a new user"""
    data = request.json
    
    success, message, user_id = user_mgmt.create_user_profile(
        user_type=data.get('user_type'),
        email=data.get('email'),
        password=data.get('password'),
        name=data.get('name'),
        phone=data.get('phone'),
        district=data.get('district'),
        address=data.get('address'),
        service_type=data.get('service_type'),
        description=data.get('description', ''),
        experience_years=data.get('experience_years', 0),
        hourly_rate=data.get('hourly_rate', 0),
        lat=data.get('lat', 0.0),
        lon=data.get('lon', 0.0),
        preferences=data.get('preferences', '')
    )
    
    if success:
        user_data = user_mgmt.get_user_profile(user_id)
        if user_data:
            user_data.pop('password', None)
            
            session['user_id'] = user_id
            session['user_type'] = data.get('user_type')
            
            return jsonify({
                'success': True,
                'message': message,
                'user': user_data
            })
    
    return jsonify({
        'success': False,
        'message': message
    }), 400

@app.route('/api/auth/login', methods=['POST'])
def login_user():
    """Authenticate and login user"""
    data = request.json
    email = data.get('email', '')
    password = data.get('password', '')
    
    success, user_data = user_mgmt.authenticate_user(email, password)
    
    if success and user_data:
        session['user_id'] = user_data['id']
        session['user_type'] = user_data['user_type']
        
        return jsonify({
            'success': True,
            'user': user_data
        })
    
    return jsonify({
        'success': False,
        'message': 'Invalid email or password'
    }), 401

@app.route('/api/auth/logout', methods=['POST'])
def logout_user():
    """Logout user"""
    session.clear()
    return jsonify({
        'success': True,
        'message': 'Logged out successfully'
    })

@app.route('/api/auth/session', methods=['GET'])
def get_session():
    """Get current session user"""
    if 'user_id' in session:
        user_data = user_mgmt.get_user_profile(session['user_id'])
        if user_data:
            user_data.pop('password', None)
            return jsonify({
                'authenticated': True,
                'user': user_data
            })
    
    return jsonify({
        'authenticated': False,
        'user': None
    })

# ==================== USER PROFILE ENDPOINTS ====================

@app.route('/api/user/profile', methods=['GET'])
def get_profile():
    """Get user profile"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400
    
    user_data = user_mgmt.get_user_profile(user_id)
    
    if user_data:
        user_data.pop('password', None)
        return jsonify(user_data)
    
    return jsonify({'error': 'User not found'}), 404

@app.route('/api/user/profile/update', methods=['POST'])
def update_profile():
    """Update user profile"""
    data = request.json
    user_id = data.get('user_id')
    
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400
    
    update_data = {k: v for k, v in data.items() if k != 'user_id'}
    
    success, message = user_mgmt.update_user_profile(user_id, **update_data)
    
    if success:
        return jsonify({
            'success': True,
            'message': message
        })
    
    return jsonify({
        'success': False,
        'message': message
    }), 400

# ==================== MESSAGING ENDPOINTS ====================

@app.route('/api/messages/send', methods=['POST'])
def send_message():
    """Send a message"""
    data = request.json
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    message = data.get('message', '')
    subject = data.get('subject', '')
    
    if not sender_id or not receiver_id:
        return jsonify({'error': 'Sender and receiver IDs required'}), 400
    
    try:
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)
    except ValueError:
        return jsonify({'error': 'Invalid user IDs'}), 400
    
    success, msg, message_id = comm.send_message(sender_id, receiver_id, message, subject)
    
    if success:
        return jsonify({
            'success': True,
            'message': msg,
            'message_id': message_id
        })
    
    return jsonify({
        'success': False,
        'message': msg
    }), 400

@app.route('/api/messages/<int:user_id>', methods=['GET'])
def get_messages(user_id):
    """Get all messages for a user"""
    include_read = request.args.get('include_read', 'true').lower() == 'true'
    messages = comm.get_messages(user_id, include_read)
    return jsonify(messages)

@app.route('/api/messages/thread/<int:user1_id>/<int:user2_id>', methods=['GET'])
def get_chat_history(user1_id, user2_id):
    """Get chat history between two users"""
    limit = request.args.get('limit', 50, type=int)
    history = comm.get_chat_history(user1_id, user2_id, limit)
    return jsonify(history)

@app.route('/api/messages/read/<int:message_id>', methods=['POST'])
def mark_read(message_id):
    """Mark a message as read"""
    success = comm.mark_as_read(message_id)
    return jsonify({
        'success': success,
        'message_id': message_id
    })

@app.route('/api/messages/read-all', methods=['POST'])
def mark_all_read():
    """Mark all messages from a partner as read"""
    data = request.json
    user_id = data.get('user_id')
    partner_id = data.get('partner_id')
    
    if not user_id or not partner_id:
        return jsonify({'error': 'User ID and partner ID required'}), 400
    
    count = comm.mark_all_read(user_id, partner_id)
    return jsonify({
        'success': True,
        'count': count
    })

@app.route('/api/messages/delete/<int:message_id>', methods=['DELETE'])
def delete_message(message_id):
    """Delete a message for a user"""
    user_id = request.args.get('user_id')
    if not user_id:
        return jsonify({'error': 'User ID required'}), 400
    
    try:
        user_id = int(user_id)
    except ValueError:
        return jsonify({'error': 'Invalid user ID'}), 400
    
    success, message = comm.delete_message(message_id, user_id)
    
    if success:
        return jsonify({'success': True, 'message': message})
    
    return jsonify({'success': False, 'message': message}), 400

@app.route('/api/conversations/<int:user_id>', methods=['GET'])
def get_conversations(user_id):
    """Get all conversations for a user"""
    conversations = comm.get_conversations(user_id)
    return jsonify(conversations)

@app.route('/api/messages/unread/<int:user_id>', methods=['GET'])
def get_unread_count(user_id):
    """Get unread message count for a user"""
    count = comm.get_unread_count(user_id)
    return jsonify({
        'user_id': user_id,
        'unread_count': count
    })

# ==================== TEMPLATE MESSAGE ENDPOINTS ====================

@app.route('/api/messages/template', methods=['POST'])
def send_template_message():
    """Send a template message"""
    data = request.json
    sender_id = data.get('sender_id')
    receiver_id = data.get('receiver_id')
    template_type = data.get('template_type')
    template_data = data.get('template_data', {})
    
    if not sender_id or not receiver_id or not template_type:
        return jsonify({'error': 'Sender ID, receiver ID, and template type required'}), 400
    
    try:
        sender_id = int(sender_id)
        receiver_id = int(receiver_id)
    except ValueError:
        return jsonify({'error': 'Invalid user IDs'}), 400
    
    success, message = comm.send_template_message(
        sender_id, receiver_id, template_type, **template_data
    )
    
    if success:
        return jsonify({'success': True, 'message': message})
    
    return jsonify({'success': False, 'message': message}), 400

# ==================== ERROR HANDLERS ====================

@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def server_error(error):
    return jsonify({'error': 'Internal server error'}), 500

# ==================== RUN SERVER ====================

if __name__ == '__main__':
    print("🚀 Starting LASO Member 4 API Server...")
    print("📡 Server running at: http://localhost:8000")
    print("📋 Available endpoints:")
    print("  - /api/health - Health check")
    print("  - /api/auth/register - Register user")
    print("  - /api/auth/login - Login user")
    print("  - /api/auth/logout - Logout user")
    print("  - /api/auth/session - Get session")
    print("  - /api/validate/* - Validation endpoints")
    print("  - /api/messages/* - Messaging endpoints")
    print("  - /api/conversations/* - Conversation endpoints")
    print("  - /api/user/profile/* - Profile endpoints")
    print("\n⚡ Press Ctrl+C to stop the server")
    
    app.run(debug=True, host='0.0.0.0', port=8000)