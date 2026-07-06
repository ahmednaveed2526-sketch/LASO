"""
test_validation.py - Complete test suite for Member 4
Run this to verify all functionality works
"""

import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from member4.user_management import UserManagement
from member4.communication import Communication

def test_user_management():
    print("\n" + "="*60)
    print("🧪 TESTING USER MANAGEMENT SYSTEM")
    print("="*60)
    
    um = UserManagement()
    
    # Test 1: Valid customer registration
    print("\n📝 Test 1: Valid Customer Registration")
    success, msg, user_id = um.create_user_profile(
        user_type='customer',
        email='customer@test.com',
        password='Test@1234',
        name='John Doe',
        phone='0712345678',
        district='Colombo',
        address='123 Galle Road, Colombo 03'
    )
    print(f"  Result: {'✅' if success else '❌'} {msg}")
    if success:
        print(f"  User ID: {user_id}")
    
    # Test 2: Valid provider registration
    print("\n📝 Test 2: Valid Provider Registration")
    success, msg, user_id = um.create_user_profile(
        user_type='provider',
        email='provider@test.com',
        password='Secure@1234',
        name='Service Pro',
        phone='0778765432',
        district='Kandy',
        address='45 Peradeniya Road, Kandy',
        service_type='plumbing',
        description='Expert plumbing services with 10 years experience',
        experience_years=10,
        hourly_rate=75,
        lat=7.2906,
        lon=80.6337
    )
    print(f"  Result: {'✅' if success else '❌'} {msg}")
    if success:
        print(f"  User ID: {user_id}")
    
    # Test 3: Invalid email
    print("\n📝 Test 3: Invalid Email")
    success, msg, _ = um.create_user_profile(
        user_type='customer',
        email='invalid-email',
        password='Test@1234',
        name='John Doe',
        phone='0712345678'
    )
    print(f"  Result: {'✅' if not success else '❌'} {msg}")
    
    # Test 4: Weak password
    print("\n📝 Test 4: Weak Password")
    success, msg, _ = um.create_user_profile(
        user_type='customer',
        email='test2@example.com',
        password='weak',
        name='John Doe',
        phone='0712345678'
    )
    print(f"  Result: {'✅' if not success else '❌'} {msg}")
    
    # Test 5: Invalid phone number
    print("\n📝 Test 5: Invalid Phone Number")
    success, msg, _ = um.create_user_profile(
        user_type='customer',
        email='test3@example.com',
        password='Test@1234',
        name='John Doe',
        phone='123456789'
    )
    print(f"  Result: {'✅' if not success else '❌'} {msg}")
    
    # Test 6: Provider without service type
    print("\n📝 Test 6: Provider Without Service Type")
    success, msg, _ = um.create_user_profile(
        user_type='provider',
        email='provider2@test.com',
        password='Secure@1234',
        name='Service Pro 2',
        phone='0778765433',
        district='Colombo'
    )
    print(f"  Result: {'✅' if not success else '❌'} {msg}")
    
    # Test 7: Password strength analysis
    print("\n📝 Test 7: Password Strength Analysis")
    passwords = [
        ('weak', 'Very Weak'),
        ('Test@123', 'Weak'),
        ('Test@1234', 'Strong'),
        ('Test@12345', 'Strong'),
        ('NoSpecial123', 'Fair')
    ]
    for pw, expected in passwords:
        result = um.get_password_strength(pw)
        status = "✅" if result['strength'] == expected else "❌"
        print(f"  {status} '{pw}': {result['strength']} (Score: {result['score']})")

def test_communication():
    print("\n" + "="*60)
    print("📬 TESTING COMMUNICATION SYSTEM")
    print("="*60)
    
    comm = Communication()
    
    # Test 1: Send message
    print("\n📝 Test 1: Send Message")
    success, msg, msg_id = comm.send_message(
        sender_id=1,
        receiver_id=2,
        subject="Service Inquiry",
        message="Hello, I would like to know about your plumbing services."
    )
    print(f"  Result: {'✅' if success else '❌'} {msg}")
    if success:
        print(f"  Message ID: {msg_id}")
    
    # Test 2: Send another message
    print("\n📝 Test 2: Send Reply")
    success, msg, msg_id2 = comm.send_message(
        sender_id=2,
        receiver_id=1,
        subject="RE: Service Inquiry",
        message="Hi! I can come tomorrow at 10 AM. Is that okay?"
    )
    print(f"  Result: {'✅' if success else '❌'} {msg}")
    if success:
        print(f"  Message ID: {msg_id2}")
    
    # Test 3: Get messages for user
    print("\n📝 Test 3: Get Messages")
    messages = comm.get_messages(user_id=1)
    print(f"  Found {len(messages)} messages:")
    for msg in messages[:3]:
        print(f"    - {msg.get('subject', 'No subject')}: {msg['message'][:50]}...")
        print(f"      From: {msg['sender_id']}, To: {msg['receiver_id']}")
        print(f"      Read: {msg['is_read']}")
    
    # Test 4: Get chat history
    print("\n📝 Test 4: Get Chat History")
    history = comm.get_chat_history(user1_id=1, user2_id=2)
    print(f"  Found {len(history)} messages in chat:")
    for msg in history:
        print(f"    {msg['sender_id']} -> {msg['receiver_id']}: {msg['message'][:40]}...")
    
    # Test 5: Get conversations
    print("\n📝 Test 5: Get Conversations")
    conversations = comm.get_conversations(user_id=1)
    print(f"  Found {len(conversations)} conversations:")
    for conv in conversations:
        print(f"    - Partner: {conv['partner_id']}")
        print(f"      Last: {conv['last_message'][:50]}...")
        print(f"      Unread: {conv.get('unread_count', 0)}")
    
    # Test 6: Mark as read
    if msg_id:
        print("\n📝 Test 6: Mark as Read")
        success = comm.mark_as_read(msg_id)
        print(f"  {'✅' if success else '❌'} Message {msg_id} marked as read")
    
    # Test 7: Get unread count
    print("\n📝 Test 7: Get Unread Count")
    unread = comm.get_unread_count(user_id=1)
    print(f"  User 1 has {unread} unread messages")
    
    # Test 8: Template messages - FIXED: unpack 3 values
    print("\n📝 Test 8: Template Messages")
    templates = [
        ('booking_confirmation', {'service': 'plumbing', 'date': '2026-07-05'}),
        ('review_request', {'link': 'https://laso.lk/review'}),
        ('payment_confirmation', {'amount': 'Rs. 5000'})
    ]
    for template_type, kwargs in templates:
        # FIXED: send_template_message returns 3 values (success, msg, msg_id)
        success, msg, msg_id = comm.send_template_message(1, 2, template_type, **kwargs)
        status = "✅" if success else "❌"
        print(f"  {status} {template_type}: {msg}")
    
    # Test 9: Delete message
    if msg_id:
        print("\n📝 Test 9: Delete Message")
        success, msg = comm.delete_message(msg_id, user_id=1)
        print(f"  {'✅' if success else '❌'} {msg}")

def run_all_tests():
    print("\n" + "="*60)
    print("🏁 RUNNING COMPLETE TEST SUITE FOR MEMBER 4")
    print("="*60)
    
    test_user_management()
    test_communication()
    
    print("\n" + "="*60)
    print("✅ ALL TESTS COMPLETED!")
    print("="*60)

if __name__ == "__main__":
    run_all_tests()