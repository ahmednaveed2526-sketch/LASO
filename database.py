# database.py - LASO App Backend
# Member 1: Backend Developer

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple


class Database:
    """Main database class for LASO App"""
    
    def __init__(self, db_path="laso_app.db"):
        """Constructor - creates database connection"""
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Create all tables"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Table 1: Users
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    email TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    user_type TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Table 2: Customers
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS customers (
                    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Table 3: Providers (with location for Member 3)
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS providers (
                    provider_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    business_name TEXT NOT NULL,
                    service_type TEXT NOT NULL,
                    phone TEXT NOT NULL,
                    address TEXT NOT NULL,
                    description TEXT,
                    latitude REAL,
                    longitude REAL,
                    average_rating REAL DEFAULT 0.0,
                    total_ratings INTEGER DEFAULT 0,
                    FOREIGN KEY (user_id) REFERENCES users(user_id)
                )
            ''')
            
            # Table 4: Reviews
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS reviews (
                    review_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_id INTEGER NOT NULL,
                    customer_id INTEGER NOT NULL,
                    rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
                    comment TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (provider_id) REFERENCES providers(provider_id),
                    FOREIGN KEY (customer_id) REFERENCES customers(customer_id),
                    UNIQUE(provider_id, customer_id)
                )
            ''')
            
            # Table 5: Messages
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    sender_id INTEGER NOT NULL,
                    receiver_id INTEGER NOT NULL,
                    message TEXT NOT NULL,
                    is_read INTEGER DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (sender_id) REFERENCES users(user_id),
                    FOREIGN KEY (receiver_id) REFERENCES users(user_id)
                )
            ''')
            
            conn.commit()
            print("✅ Database tables created")
    
    # ========== USER METHODS ==========
    
    def register_user(self, email: str, password: str, user_type: str) -> Tuple[bool, int, str]:
        """Register a new user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO users (email, password, user_type) VALUES (?, ?, ?)",
                    (email, password, user_type)
                )
                return (True, cursor.lastrowid, "Registration successful")
        except sqlite3.IntegrityError:
            return (False, -1, "Email already exists")
        except Exception as e:
            return (False, -1, f"Error: {str(e)}")
    
    def login_user(self, email: str, password: str) -> Tuple[bool, int, str]:
        """Authenticate user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT user_id, user_type FROM users WHERE email = ? AND password = ?",
                (email, password)
            )
            result = cursor.fetchone()
            if result:
                return (True, result[0], result[1])
            return (False, -1, "Invalid email or password")
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """Get user by ID"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========== CUSTOMER METHODS ==========
    
    def create_customer_profile(self, user_id: int, full_name: str, phone: str, address: str) -> Tuple[bool, int]:
        """Create customer profile"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO customers (user_id, full_name, phone, address) VALUES (?, ?, ?, ?)",
                    (user_id, full_name, phone, address)
                )
                return (True, cursor.lastrowid)
        except Exception as e:
            return (False, -1)
    
    def get_customer_by_user_id(self, user_id: int) -> Optional[Dict]:
        """Get customer by user_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM customers WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    # ========== PROVIDER METHODS ==========
    
    def create_provider_profile(self, user_id: int, business_name: str, service_type: str, 
                                phone: str, address: str, description: str = "", 
                                latitude: float = None, longitude: float = None) -> Tuple[bool, int]:
        """Create provider profile with location"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO providers (user_id, business_name, service_type, phone, address, description, latitude, longitude)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, business_name, service_type, phone, address, description, latitude, longitude))
                return (True, cursor.lastrowid)
        except Exception as e:
            return (False, -1)
    
    def get_provider_by_user_id(self, user_id: int) -> Optional[Dict]:
        """Get provider by user_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM providers WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_provider_by_id(self, provider_id: int) -> Optional[Dict]:
        """Get provider by provider_id"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM providers WHERE provider_id = ?", (provider_id,))
            row = cursor.fetchone()
            return dict(row) if row else None
    
    def get_all_providers(self, service_type: str = None) -> List[Dict]:
        """Get all providers (with lat/lon for Member 3)"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            if service_type:
                cursor.execute("SELECT * FROM providers WHERE service_type = ?", (service_type,))
            else:
                cursor.execute("SELECT * FROM providers")
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== RATING METHODS ==========
    
    def add_review(self, provider_id: int, customer_id: int, rating: int, comment: str) -> Tuple[bool, str]:
        """Add a review"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO reviews (provider_id, customer_id, rating, comment) VALUES (?, ?, ?, ?)",
                    (provider_id, customer_id, rating, comment)
                )
                self._update_provider_rating(provider_id)
                return (True, "Review added")
        except sqlite3.IntegrityError:
            return (False, "Already reviewed this provider")
    
    def _update_provider_rating(self, provider_id: int):
        """Update provider's average rating"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "SELECT AVG(rating), COUNT(*) FROM reviews WHERE provider_id = ?",
                (provider_id,)
            )
            avg_rating, total = cursor.fetchone()
            cursor.execute(
                "UPDATE providers SET average_rating = ?, total_ratings = ? WHERE provider_id = ?",
                (avg_rating or 0, total or 0, provider_id)
            )
    
    def get_provider_reviews(self, provider_id: int) -> List[Dict]:
        """Get all reviews for a provider"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reviews WHERE provider_id = ? ORDER BY created_at DESC", (provider_id,))
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== MESSAGING METHODS ==========
    
    def send_message(self, sender_id: int, receiver_id: int, message: str) -> Tuple[bool, int]:
        """Send a message"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO messages (sender_id, receiver_id, message) VALUES (?, ?, ?)",
                (sender_id, receiver_id, message)
            )
            return (True, cursor.lastrowid)
    
    def get_messages(self, user_id: int) -> List[Dict]:
        """Get all messages for a user"""
        with sqlite3.connect(self.db_path) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(
                "SELECT * FROM messages WHERE receiver_id = ? ORDER BY created_at DESC",
                (user_id,)
            )
            return [dict(row) for row in cursor.fetchall()]
    
    # ========== SAMPLE DATA FOR TESTING ==========
    
    def seed_sample_data(self):
        """Add test data"""
        # Add provider
        success, user_id, _ = self.register_user("plumber@test.com", "pass123", "provider")
        if success:
            self.create_provider_profile(
                user_id, "Quick Plumber", "Plumbing", "555-0101", 
                "123 Main St", "24/7 service", 40.7128, -74.0060
            )
        
        # Add customer
        success, user_id, _ = self.register_user("customer@test.com", "pass123", "customer")
        if success:
            self.create_customer_profile(user_id, "John Doe", "555-0202", "456 Oak St")
        
        print("✅ Sample data added")


# ========== TEST YOUR BACKEND ==========
if __name__ == "__main__":
    print("=" * 50)
    print("LASO APP - BACKEND DATABASE TEST")
    print("=" * 50)
    
    # Create database
    db = Database()
    
    # Test 1: Register
    print("\n📝 Test 1: Register user")
    success, user_id, msg = db.register_user("test@example.com", "password123", "customer")
    print(f"   Result: {success}, User ID: {user_id}")
    
    # Test 2: Login
    print("\n📝 Test 2: Login")
    success, user_id, user_type = db.login_user("test@example.com", "password123")
    print(f"   Result: {success}, Type: {user_type}")
    
    # Test 3: Create profile
    print("\n📝 Test 3: Create customer profile")
    if success:
        success, cust_id = db.create_customer_profile(user_id, "Test User", "1234567890", "Test Address")
        print(f"   Result: {success}, Customer ID: {cust_id}")
    
    # Test 4: Add sample data
    print("\n📝 Test 4: Add sample providers")
    db.seed_sample_data()
    
    # Test 5: Get all providers
    print("\n📝 Test 5: Get all providers")
    providers = db.get_all_providers()
    print(f"   Found {len(providers)} providers")
    for p in providers:
        print(f"   - {p['business_name']} (lat: {p['latitude']}, lon: {p['longitude']})")
    
    print("\n" + "=" * 50)
    print("✅ BACKEND COMPLETE! Ready to share with team")
    print("=" * 50)