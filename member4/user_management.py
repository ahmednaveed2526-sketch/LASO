"""
user_management.py - User Validation and Profile Management
Member 4's main file
"""

import re
import hashlib
from datetime import datetime
from typing import Tuple, Optional, Dict, Any, List

class UserManagement:
    def __init__(self, database=None):
        """
        Initialize with database connection (provided by Member 1)
        """
        self.db = database
        self.errors = []
        
    # ==================== VALIDATION METHODS ====================
    
    def validate_email(self, email: str) -> Tuple[bool, str]:
        """
        Validate email format and check for duplicates
        Returns: (is_valid, error_message)
        """
        if not email:
            return False, "Email is required"
        
        # Email regex pattern
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        
        if not re.match(email_pattern, email):
            return False, "Invalid email format. Example: user@domain.com"
        
        # Check for duplicate email if database is available
        if self.db:
            try:
                existing_user = self.db.get_user_by_email(email)
                if existing_user:
                    return False, "Email already registered. Please use a different email."
            except Exception as e:
                print(f"Database check error (can be ignored during testing): {e}")
                
        return True, "Email is valid"
    
    def validate_phone(self, phone: str) -> Tuple[bool, str]:
        """
        Validate phone number for Sri Lanka format
        Returns: (is_valid, error_message)
        """
        if not phone:
            return False, "Phone number is required"
        
        # Remove spaces, dashes, parentheses
        clean_phone = re.sub(r'[\s\-\(\)]', '', phone)
        
        if not clean_phone.isdigit():
            return False, "Phone number must contain only digits"
        
        # Check Sri Lankan phone format: 07XXXXXXXX or 7XXXXXXXX
        if len(clean_phone) == 9 and clean_phone.startswith('7'):
            pass
        elif len(clean_phone) == 10 and clean_phone.startswith('07'):
            pass
        else:
            return False, "Phone number must be 9-10 digits starting with 7 or 07"
            
        return True, "Phone number is valid"
    
    def validate_password(self, password: str, confirm_password: str = None) -> Tuple[bool, str]:
        """
        Validate password strength
        Returns: (is_valid, error_message)
        """
        if not password:
            return False, "Password is required"
        
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        
        # Check for at least one uppercase letter
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        
        # Check for at least one lowercase letter
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        
        # Check for at least one digit
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one number"
        
        # Check for at least one special character
        special_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        if not any(c in special_chars for c in password):
            return False, "Password must contain at least one special character (!@#$%^&*)"
        
        # Check if passwords match
        if confirm_password is not None and password != confirm_password:
            return False, "Passwords do not match"
        
        return True, "Password is strong"
    
    def validate_name(self, name: str) -> Tuple[bool, str]:
        """
        Validate name
        Returns: (is_valid, error_message)
        """
        if not name or not name.strip():
            return False, "Name is required"
        
        if len(name.strip()) < 2:
            return False, "Name must be at least 2 characters long"
        
        if not re.match(r'^[a-zA-Z\s\-\'.]+$', name):
            return False, "Name contains invalid characters"
        
        return True, "Name is valid"
    
    def validate_address(self, address: str) -> Tuple[bool, str]:
        """
        Validate address format (for Member 3)
        Returns: (is_valid, error_message)
        """
        if not address:
            return False, "Address is required"
        
        if len(address.strip()) < 5:
            return False, "Address is too short"
        
        if ',' not in address and ' ' not in address:
            return False, "Please provide a complete address (e.g., 123 Galle Road, Colombo)"
        
        return True, "Address is valid"
    
    def validate_district(self, district: str) -> Tuple[bool, str]:
        """
        Validate Sri Lankan district
        Returns: (is_valid, error_message)
        """
        if not district or not district.strip():
            return False, "District is required"
        
        sri_lanka_districts = [
            "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", 
            "Nuwara Eliya", "Galle", "Matara", "Hambantota", "Jaffna",
            "Kilinochchi", "Mannar", "Vavuniya", "Mullaitivu", "Batticaloa",
            "Ampara", "Trincomalee", "Kurunegala", "Puttalam", "Anuradhapura",
            "Polonnaruwa", "Badulla", "Moneragala", "Ratnapura", "Kegalle"
        ]
        
        if district.strip() not in sri_lanka_districts:
            return False, f"'{district}' is not a valid Sri Lankan district"
        
        return True, "District is valid"
    
    def validate_service_type(self, service_type: str) -> Tuple[bool, str]:
        """
        Validate service type for providers
        Returns: (is_valid, error_message)
        """
        valid_services = [
            "plumbing", "electrical", "carpentry", "masonry", 
            "painting", "appliance", "ac", "cleaning"
        ]
        
        if not service_type:
            return False, "Service type is required for providers"
        
        if service_type not in valid_services:
            return False, f"'{service_type}' is not a valid service type"
        
        return True, "Service type is valid"
    
    def validate_user_input(self, email: str, password: str, confirm_password: str, 
                           phone: str = None, name: str = None, 
                           district: str = None, address: str = None,
                           service_type: str = None, **kwargs) -> Tuple[bool, str]:
        """
        Complete user input validation
        Returns: (is_valid, error_message)
        """
        # Validate name
        if name is not None:
            is_valid, error = self.validate_name(name)
            if not is_valid:
                return False, error
        
        # Validate email
        is_valid, error = self.validate_email(email)
        if not is_valid:
            return False, error
        
        # Validate password
        is_valid, error = self.validate_password(password, confirm_password)
        if not is_valid:
            return False, error
        
        # Validate phone if provided
        if phone:
            is_valid, error = self.validate_phone(phone)
            if not is_valid:
                return False, error
        
        # Validate district if provided
        if district:
            is_valid, error = self.validate_district(district)
            if not is_valid:
                return False, error
        
        # Validate address if provided
        if address:
            is_valid, error = self.validate_address(address)
            if not is_valid:
                return False, error
        
        # Validate service type if provided
        if service_type:
            is_valid, error = self.validate_service_type(service_type)
            if not is_valid:
                return False, error
        
        return True, "All inputs are valid"
    
    # ==================== PASSWORD HASHING ====================
    
    def hash_password(self, password: str) -> str:
        """Hash password for secure storage using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a plain password against a hashed password"""
        return self.hash_password(plain_password) == hashed_password
    
    def get_password_strength(self, password: str) -> Dict[str, Any]:
        """Get detailed password strength analysis"""
        requirements = {
            'length': len(password) >= 8,
            'uppercase': any(c.isupper() for c in password),
            'lowercase': any(c.islower() for c in password),
            'digit': any(c.isdigit() for c in password),
            'special': any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password)
        }
        
        met_count = sum(requirements.values())
        
        if met_count == 5:
            strength = "Strong"
            score = 100
        elif met_count >= 4:
            strength = "Good"
            score = 80
        elif met_count >= 3:
            strength = "Fair"
            score = 60
        elif met_count >= 2:
            strength = "Weak"
            score = 40
        else:
            strength = "Very Weak"
            score = 20
        
        return {
            'score': score,
            'strength': strength,
            'requirements': requirements,
            'met_count': met_count,
            'total': 5
        }
    
    # ==================== PROFILE MANAGEMENT ====================
    
    def create_user_profile(self, user_type: str, email: str, password: str, 
                           name: str, phone: str, district: str = None,
                           address: str = None, **kwargs) -> Tuple[bool, str, Optional[int]]:
        """
        Create a complete user profile with validation
        Returns: (success, message, user_id)
        """
        service_type = kwargs.get('service_type')
        if user_type == 'provider' and not service_type:
            return False, "Service type is required for providers", None
        
        is_valid, error = self.validate_user_input(
            email=email,
            password=password,
            confirm_password=password,
            phone=phone,
            name=name,
            district=district,
            address=address,
            service_type=service_type
        )
        
        if not is_valid:
            return False, error, None
        
        if not self.db:
            test_user_id = 1
            return True, "Profile created (test mode)", test_user_id
        
        try:
            hashed_password = self.hash_password(password)
            
            user_data = {
                'email': email,
                'password': hashed_password,
                'name': name.strip(),
                'phone': phone,
                'user_type': user_type,
                'district': district,
                'address': address,
                'created_at': datetime.now().isoformat(),
                'is_active': True
            }
            
            user_id = self.db.register_user(user_data)
            
            if not user_id:
                return False, "Failed to create user account", None
            
            if user_type == 'provider':
                provider_data = {
                    'user_id': user_id,
                    'service_type': service_type,
                    'description': kwargs.get('description', ''),
                    'experience_years': kwargs.get('experience_years', 0),
                    'hourly_rate': kwargs.get('hourly_rate', 0),
                    'latitude': kwargs.get('lat', 0.0),
                    'longitude': kwargs.get('lon', 0.0),
                    'district': district,
                    'address': address,
                    'phone': phone
                }
                self.db.create_provider(provider_data)
                
            elif user_type == 'customer':
                customer_data = {
                    'user_id': user_id,
                    'district': district,
                    'address': address,
                    'phone': phone,
                    'preferences': kwargs.get('preferences', '')
                }
                self.db.create_customer(customer_data)
            
            return True, f"{user_type.capitalize()} registered successfully", user_id
            
        except Exception as e:
            return False, f"Error creating profile: {str(e)}", None
    
    def update_user_profile(self, user_id: int, **kwargs) -> Tuple[bool, str]:
        """Update user profile with validation"""
        if not self.db:
            return True, "Profile updated (test mode)"
        
        try:
            for field, value in kwargs.items():
                if field == 'email':
                    is_valid, error = self.validate_email(value)
                    if not is_valid:
                        return False, error
                elif field == 'phone':
                    is_valid, error = self.validate_phone(value)
                    if not is_valid:
                        return False, error
                elif field == 'password':
                    is_valid, error = self.validate_password(value)
                    if not is_valid:
                        return False, error
                elif field == 'name':
                    is_valid, error = self.validate_name(value)
                    if not is_valid:
                        return False, error
                elif field == 'district':
                    is_valid, error = self.validate_district(value)
                    if not is_valid:
                        return False, error
                elif field == 'address':
                    is_valid, error = self.validate_address(value)
                    if not is_valid:
                        return False, error
            
            if 'password' in kwargs:
                kwargs['password'] = self.hash_password(kwargs['password'])
            
            self.db.update_user(user_id, kwargs)
            return True, "Profile updated successfully"
            
        except Exception as e:
            return False, f"Error updating profile: {str(e)}"
    
    def get_user_profile(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Retrieve complete user profile"""
        if not self.db:
            return {
                "id": user_id, 
                "name": "Test User", 
                "email": "test@email.com",
                "phone": "0712345678",
                "user_type": "customer",
                "district": "Colombo",
                "address": "123 Test Street",
                "created_at": datetime.now().isoformat(),
                "is_active": True
            }
        
        try:
            user_data = self.db.get_user_by_id(user_id)
            return user_data
        except Exception as e:
            print(f"Error retrieving profile: {e}")
            return None
    
    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email address"""
        if not self.db:
            return None
        
        try:
            return self.db.get_user_by_email(email)
        except Exception as e:
            print(f"Error retrieving user by email: {e}")
            return None
    
    def authenticate_user(self, email: str, password: str) -> Tuple[bool, Optional[Dict[str, Any]]]:
        """Authenticate a user"""
        if not self.db:
            if email == "test@email.com" and password == "Test@1234":
                return True, {
                    "id": 1,
                    "email": email,
                    "name": "Test User",
                    "user_type": "customer"
                }
            return False, None
        
        try:
            user = self.db.get_user_by_email(email)
            if not user:
                return False, None
            
            if self.verify_password(password, user.get('password', '')):
                user.pop('password', None)
                return True, user
            
            return False, None
            
        except Exception as e:
            print(f"Authentication error: {e}")
            return False, None


# ==================== TESTING ====================

if __name__ == "__main__":
    print("🧪 Testing User Management System...")
    um = UserManagement()
    
    print("\n📧 Testing Email Validation:")
    test_emails = [
        ("john@example.com", True),
        ("invalid-email", False),
        ("test@domain.com", True),
        ("", False)
    ]
    for email, expected in test_emails:
        is_valid, msg = um.validate_email(email)
        status = "✅" if is_valid == expected else "❌"
        print(f"  {status} '{email}': {is_valid}")
    
    print("\n🔐 Testing Password Validation:")
    test_passwords = [
        ("Test@1234", True),
        ("weak", False),
        ("Abc@123", False),
        ("Test@12345", True)
    ]
    for pw, expected in test_passwords:
        is_valid, msg = um.validate_password(pw)
        status = "✅" if is_valid == expected else "❌"
        print(f"  {status} '{pw}': {is_valid}")
    
    print("\n✅ User Management System tests complete!")