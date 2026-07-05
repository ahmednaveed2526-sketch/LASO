# app.py - API Server (The "Waiter" between HTML and your database)
from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database

# Create the API server
app = Flask(__name__)
CORS(app)  # This allows HTML/JS to talk to your server

# Connect to your database
db = Database()

# ============================================
# These are the "doors" that HTML/JS can knock on
# ============================================

@app.route('/api/register', methods=['POST'])
def register():
    """HTML calls this when user signs up"""
    data = request.get_json()
    success, user_id, message = db.register_user(
        data['email'], 
        data['password'], 
        data['user_type']
    )
    return jsonify({
        'success': success, 
        'user_id': user_id, 
        'message': message
    })

@app.route('/api/login', methods=['POST'])
def login():
    """HTML calls this when user logs in"""
    data = request.get_json()
    success, user_id, user_type = db.login_user(
        data['email'], 
        data['password']
    )
    return jsonify({
        'success': success, 
        'user_id': user_id, 
        'user_type': user_type
    })

@app.route('/api/providers', methods=['GET'])
def get_providers():
    """HTML calls this to show all service providers"""
    providers = db.get_all_providers()
    return jsonify(providers)

@app.route('/api/providers/<int:provider_id>', methods=['GET'])
def get_provider(provider_id):
    """HTML calls this to show one provider's details"""
    provider = db.get_provider_by_id(provider_id)
    return jsonify(provider)

@app.route('/api/customer/profile', methods=['POST'])
def create_customer_profile():
    """HTML calls this after registration"""
    data = request.get_json()
    success, customer_id = db.create_customer_profile(
        data['user_id'],
        data['full_name'],
        data['phone'],
        data['address']
    )
    return jsonify({'success': success, 'customer_id': customer_id})

@app.route('/api/review', methods=['POST'])
def add_review():
    """HTML calls this when customer submits a rating"""
    data = request.get_json()
    success, message = db.add_review(
        data['provider_id'],
        data['customer_id'],
        data['rating'],
        data['comment']
    )
    return jsonify({'success': success, 'message': message})

@app.route('/api/message', methods=['POST'])
def send_message():
    """HTML calls this when user sends a chat message"""
    data = request.get_json()
    success, msg_id = db.send_message(
        data['sender_id'],
        data['receiver_id'],
        data['message']
    )
    return jsonify({'success': success, 'message_id': msg_id})

# ============================================
# This starts your API server
# ============================================
if __name__ == '__main__':
    print("=" * 50)
    print("🚀 LASO APP API SERVER RUNNING")
    print("=" * 50)
    print("📍 Your API is available at: http://localhost:5000")
    print("")
    print("📋 Endpoints (doors) available:")
    print("   POST http://localhost:5000/api/register")
    print("   POST http://localhost:5000/api/login")
    print("   GET  http://localhost:5000/api/providers")
    print("   POST http://localhost:5000/api/review")
    print("   POST http://localhost:5000/api/message")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)