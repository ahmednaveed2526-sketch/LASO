"""
communication.py - Messaging System
Member 4's second file
"""

from datetime import datetime
from typing import List, Dict, Any, Optional, Tuple
import re

class Communication:
    def __init__(self, database=None):
        """Initialize with database connection (provided by Member 1)"""
        self.db = database
        self.messages_cache = []
        self._init_test_data()
    
    def _init_test_data(self):
        """Initialize test message data for development"""
        if not self.messages_cache:
            self.messages_cache = [
                {
                    'id': 1,
                    'sender_id': 1,
                    'receiver_id': 2,
                    'subject': 'Service Inquiry',
                    'message': 'Hello! I need a plumber for my kitchen sink.',
                    'sent_at': datetime.now().isoformat(),
                    'is_read': False,
                    'is_deleted_by_sender': False,
                    'is_deleted_by_receiver': False
                },
                {
                    'id': 2,
                    'sender_id': 2,
                    'receiver_id': 1,
                    'subject': 'RE: Service Inquiry',
                    'message': 'Hi! Yes, I can come tomorrow at 10 AM.',
                    'sent_at': datetime.now().isoformat(),
                    'is_read': True,
                    'is_deleted_by_sender': False,
                    'is_deleted_by_receiver': False
                }
            ]
    
    # ==================== MESSAGE OPERATIONS ====================
    
    def send_message(self, sender_id: int, receiver_id: int, 
                     message: str, subject: str = "") -> Tuple[bool, str, Optional[int]]:
        """Send a message between users"""
        if not message or not message.strip():
            return False, "Message cannot be empty", None
        
        if sender_id == receiver_id:
            return False, "Cannot send message to yourself", None
        
        if len(message) > 5000:
            return False, "Message exceeds maximum length (5000 characters)", None
        
        message = self._sanitize_message(message)
        subject = self._sanitize_message(subject)[:200] if subject else ""
        
        if self.db:
            try:
                message_data = {
                    'sender_id': sender_id,
                    'receiver_id': receiver_id,
                    'subject': subject,
                    'message': message,
                    'sent_at': datetime.now().isoformat(),
                    'is_read': False,
                    'is_deleted_by_sender': False,
                    'is_deleted_by_receiver': False
                }
                message_id = self.db.save_message(message_data)
                return True, "Message sent successfully", message_id
            except Exception as e:
                return False, f"Error sending message: {str(e)}", None
        
        new_id = len(self.messages_cache) + 1
        self.messages_cache.append({
            'id': new_id,
            'sender_id': sender_id,
            'receiver_id': receiver_id,
            'subject': subject,
            'message': message,
            'sent_at': datetime.now().isoformat(),
            'is_read': False,
            'is_deleted_by_sender': False,
            'is_deleted_by_receiver': False
        })
        return True, "Message sent successfully", new_id
    
    def get_messages(self, user_id: int, include_read: bool = True) -> List[Dict[str, Any]]:
        """Get all messages for a user"""
        if self.db:
            try:
                return self.db.get_user_messages(user_id, include_read)
            except Exception as e:
                print(f"Error retrieving messages: {e}")
                return []
        
        messages = [
            msg for msg in self.messages_cache
            if (msg['sender_id'] == user_id or msg['receiver_id'] == user_id)
            and not (msg['sender_id'] == user_id and msg['is_deleted_by_sender'])
            and not (msg['receiver_id'] == user_id and msg['is_deleted_by_receiver'])
        ]
        
        if not include_read:
            messages = [msg for msg in messages if not msg['is_read']]
        
        messages.sort(key=lambda x: x['sent_at'], reverse=True)
        return messages
    
    def get_chat_history(self, user1_id: int, user2_id: int, limit: int = 50) -> List[Dict[str, Any]]:
        """Get conversation history between two users"""
        if self.db:
            try:
                return self.db.get_chat_history(user1_id, user2_id, limit)
            except Exception as e:
                print(f"Error retrieving chat history: {e}")
                return []
        
        messages = [
            msg for msg in self.messages_cache
            if (msg['sender_id'] == user1_id and msg['receiver_id'] == user2_id) or
               (msg['sender_id'] == user2_id and msg['receiver_id'] == user1_id)
        ]
        
        messages.sort(key=lambda x: x['sent_at'])
        
        if len(messages) > limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_conversations(self, user_id: int) -> List[Dict[str, Any]]:
        """Get all conversations for a user with latest message"""
        if self.db:
            try:
                return self.db.get_conversations(user_id)
            except Exception as e:
                print(f"Error retrieving conversations: {e}")
                return []
        
        all_messages = self.get_messages(user_id)
        
        if not all_messages:
            return []
        
        conversations = {}
        for msg in all_messages:
            partner_id = msg['receiver_id'] if msg['sender_id'] == user_id else msg['sender_id']
            if partner_id not in conversations:
                conversations[partner_id] = {
                    'partner_id': partner_id,
                    'last_message': msg['message'],
                    'timestamp': msg['sent_at'],
                    'subject': msg.get('subject', ''),
                    'unread_count': 1 if not msg['is_read'] and msg['receiver_id'] == user_id else 0
                }
            else:
                if msg['sent_at'] > conversations[partner_id]['timestamp']:
                    conversations[partner_id]['last_message'] = msg['message']
                    conversations[partner_id]['timestamp'] = msg['sent_at']
                    conversations[partner_id]['subject'] = msg.get('subject', '')
                
                if not msg['is_read'] and msg['receiver_id'] == user_id:
                    conversations[partner_id]['unread_count'] = conversations[partner_id].get('unread_count', 0) + 1
        
        result = list(conversations.values())
        result.sort(key=lambda x: x['timestamp'], reverse=True)
        return result
    
    def mark_as_read(self, message_id: int) -> bool:
        """Mark a message as read"""
        if self.db:
            try:
                return self.db.mark_message_as_read(message_id)
            except Exception as e:
                print(f"Error marking message as read: {e}")
                return False
        
        for msg in self.messages_cache:
            if msg['id'] == message_id:
                msg['is_read'] = True
                return True
        return False
    
    def mark_all_read(self, user_id: int, partner_id: int) -> int:
        """Mark all messages from a partner as read"""
        if self.db:
            try:
                return self.db.mark_all_messages_read(user_id, partner_id)
            except Exception as e:
                print(f"Error marking all messages as read: {e}")
                return 0
        
        count = 0
        for msg in self.messages_cache:
            if (msg['sender_id'] == partner_id and msg['receiver_id'] == user_id and not msg['is_read']):
                msg['is_read'] = True
                count += 1
        return count
    
    def delete_message(self, message_id: int, user_id: int) -> Tuple[bool, str]:
        """Delete a message for a specific user"""
        if self.db:
            try:
                message = self.db.get_message(message_id)
                if not message:
                    return False, "Message not found"
                
                if message['sender_id'] == user_id:
                    self.db.mark_message_deleted_by_sender(message_id)
                elif message['receiver_id'] == user_id:
                    self.db.mark_message_deleted_by_receiver(message_id)
                else:
                    return False, "User not authorized to delete this message"
                
                return True, "Message deleted successfully"
            except Exception as e:
                return False, f"Error deleting message: {str(e)}"
        
        for msg in self.messages_cache:
            if msg['id'] == message_id:
                if msg['sender_id'] == user_id:
                    msg['is_deleted_by_sender'] = True
                elif msg['receiver_id'] == user_id:
                    msg['is_deleted_by_receiver'] = True
                else:
                    return False, "User not authorized to delete this message"
                return True, "Message deleted successfully"
        
        return False, "Message not found"
    
    def get_unread_count(self, user_id: int) -> int:
        """Get count of unread messages for a user"""
        if self.db:
            try:
                return self.db.get_unread_count(user_id)
            except Exception as e:
                print(f"Error getting unread count: {e}")
                return 0
        
        messages = self.get_messages(user_id, include_read=False)
        return len([m for m in messages if m['receiver_id'] == user_id])
    
    def get_message(self, message_id: int) -> Optional[Dict[str, Any]]:
        """Get a single message by ID"""
        if self.db:
            try:
                return self.db.get_message(message_id)
            except Exception as e:
                print(f"Error retrieving message: {e}")
                return None
        
        for msg in self.messages_cache:
            if msg['id'] == message_id:
                return msg.copy()
        return None
    
    # ==================== TEMPLATE MESSAGES ====================
    
    def send_template_message(self, sender_id: int, receiver_id: int, 
                             template_type: str, **kwargs) -> Tuple[bool, str]:
        """Send a template message"""
        templates = {
            'booking_request': "Hello! I would like to book your {service} service. Please let me know your availability.",
            'booking_confirmation': "Your booking for {service} has been confirmed for {date}.",
            'review_request': "Thank you for using our service! Would you mind leaving a review?",
            'payment_confirmation': "Payment of {amount} has been received. Thank you!",
            'service_completed': "Your service has been marked as completed."
        }
        
        if template_type not in templates:
            return False, f"Template '{template_type}' not found"
        
        try:
            message = templates[template_type].format(**kwargs)
        except KeyError as e:
            return False, f"Missing parameter for template: {e}"
        
        return self.send_message(sender_id, receiver_id, message, f"Template: {template_type}")
    
    # ==================== UTILITY METHODS ====================
    
    def _sanitize_message(self, text: str) -> str:
        """Sanitize message to prevent XSS"""
        if not text:
            return ""
        
        text = re.sub(r'<[^>]*>', '', text)
        text = re.sub(r'<script.*?</script>', '', text, flags=re.DOTALL)
        text = text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        return text
    
    def get_message_preview(self, message: str, max_length: int = 50) -> str:
        """Get a truncated preview of a message"""
        if len(message) <= max_length:
            return message
        return message[:max_length] + "..."


# ==================== TESTING ====================

if __name__ == "__main__":
    print("📬 Testing Communication System...")
    comm = Communication()
    
    print("\n✉️ Testing Send Message:")
    success, msg, msg_id = comm.send_message(1, 2, "Hello, this is a test message!", "Test Subject")
    status = "✅" if success else "❌"
    print(f"  {status} {msg} (ID: {msg_id})")
    
    print("\n📨 Testing Get Messages:")
    messages = comm.get_messages(2)
    print(f"  Found {len(messages)} messages")
    
    print("\n💬 Testing Get Conversations:")
    conversations = comm.get_conversations(1)
    print(f"  Found {len(conversations)} conversations")
    
    print("\n✅ Communication System tests complete!")