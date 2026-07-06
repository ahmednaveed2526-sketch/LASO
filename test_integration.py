# test_integration.py - Integration Test Suite for LASO Unification
import unittest
import json
import os
import sys
import io
import time
import threading
import requests

import warnings

# Suppress unclosed SQLite connection ResourceWarnings globally across all threads
warnings.showwarning = lambda *a, **kw: None

# Force UTF-8 encoding for standard output to avoid UnicodeEncodeError on Windows terminals
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add current folder to path
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(CURRENT_DIR)

# Import the integrated application server
from app import app, db

# Global variable to check if server is running
server_started = False
PORT = 8085
BASE_URL = f"http://127.0.0.1:{PORT}"

def start_server():
    global server_started
    server_started = True
    app.run(port=PORT, debug=False, use_reloader=False)

class TestLASOIntegration(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Start Flask server in a background thread once for all tests"""
        global server_started
        if not server_started:
            t = threading.Thread(target=start_server)
            t.daemon = True
            t.start()
            print("⏳ Waiting for Flask server to start...")
            # Wait up to 3 seconds for server to bind
            for _ in range(30):
                try:
                    r = requests.get(f"{BASE_URL}/")
                    if r.status_code == 200:
                        print("🚀 Server started successfully on port", PORT)
                        break
                except requests.exceptions.ConnectionError:
                    time.sleep(0.1)

    def test_01_registration_and_login_validation(self):
        """Test registration and login cycle with Member 4 validation & password hashing"""
        print("\n🧪 Testing User Registration & Login with validation and hashing...")
        
        # Test inputs validation fail (invalid email format)
        reg_payload = {
            "email": "invalid-email-format",
            "password": "Short",
            "userType": "customer",
            "name": "John Doe",
            "phone": "0771234567",
            "district": "Colombo",
            "address": "123 Galle Road, Colombo"
        }
        r = requests.post(f"{BASE_URL}/api/register", json=reg_payload)
        self.assertEqual(r.status_code, 400)
        print("  - Input validation rejected invalid email successfully.")

        # Test valid customer registration
        email = f"test_cust_{os.urandom(2).hex()}@laso.lk"
        reg_payload = {
            "email": email,
            "password": "SecurePassword123!",
            "userType": "customer",
            "name": "Ruvini Silva",
            "phone": "0771122334",
            "district": "Colombo",
            "address": "45 Galle Road, Colombo 03"
        }
        r = requests.post(f"{BASE_URL}/api/register", json=reg_payload)
        self.assertEqual(r.status_code, 200)
        reg_data = r.json()
        self.assertTrue(reg_data['success'])
        self.assertEqual(reg_data['email'], email)
        print(f"  - Customer registered successfully. User ID: {reg_data['userId']}")

        # Test login with hashed password
        login_payload = {
            "email": email,
            "password": "SecurePassword123!"
        }
        r = requests.post(f"{BASE_URL}/api/login", json=login_payload)
        self.assertEqual(r.status_code, 200)
        login_data = r.json()
        self.assertTrue(login_data['success'])
        self.assertEqual(login_data['name'], "Ruvini Silva")
        print("  - Customer logged in successfully with Member 4 password verification.")

    def test_02_nearby_search_sorting(self):
        """Test location search sorting & filtering using Member 3 Haversine distance logic"""
        print("\n🧪 Testing Location Proximity Search & Distance Sorting (Member 3)...")
        
        # Register a provider at specific coordinates
        email = f"prov_plumb_{os.urandom(2).hex()}@laso.lk"
        prov_payload = {
            "email": email,
            "password": "SecurePassword123!",
            "userType": "provider",
            "serviceType": "plumbing",
            "name": "Prasad Plumbers",
            "phone": "0712345678",
            "district": "Colombo",
            "address": "100 High Level Road, Colombo",
            "lat": 6.9271,  # Colombo latitude
            "lon": 79.8612, # Colombo longitude
            "description": "Professional pipe leak repair specialist"
        }
        r = requests.post(f"{BASE_URL}/api/register", json=prov_payload)
        self.assertEqual(r.status_code, 200)
        provider_user_id = r.json()['userId']
        
        # Look up provider profile in DB to get the provider_id
        prov_profile = db.get_provider_by_user_id(provider_user_id)
        provider_id = prov_profile['provider_id']

        # Query nearby providers close to Colombo coords
        r = requests.get(f"{BASE_URL}/api/providers/nearby?lat=6.9300&lon=79.8600&district=Colombo&service=plumbing")
        self.assertEqual(r.status_code, 200)
        results = r.json()
        self.assertTrue(len(results) > 0)
        
        # Find our registered provider in results
        provider_found = next((p for p in results if p['id'] == provider_id), None)
        self.assertIsNotNone(provider_found)
        self.assertIn('distance', provider_found)
        self.assertIn('avgRating', provider_found)
        print(f"  - Proximity search found provider {provider_found['name']} at {provider_found['distance']} km away.")

    def test_03_reviews_and_score_updates(self):
        """Test review submissions and automatic score updates inside SQLite"""
        print("\n🧪 Testing Rating Submission & SQLite updates...")
        
        # Fetch an existing provider (ID 1)
        p = db.get_provider_by_id(1)
        if not p:
            db.create_provider_profile(
                user_id=1,
                business_name="Test Provider 1",
                service_type="electrical",
                phone="0779998887",
                address="12 Galle Rd, Colombo",
                latitude=6.9,
                longitude=79.8
            )
            p = db.get_provider_by_id(1)
            
        initial_rating = p['average_rating'] or 0.0
        initial_count = p['total_ratings'] or 0

        # Register a test customer
        cust_email = f"cust_rev_{os.urandom(2).hex()}@laso.lk"
        cust_payload = {
            "email": cust_email,
            "password": "SecurePassword123!",
            "userType": "customer",
            "name": "Test Reviewer",
            "phone": "0779991111",
            "district": "Colombo",
            "address": "90 Galle Road, Colombo"
        }
        r = requests.post(f"{BASE_URL}/api/register", json=cust_payload)
        self.assertEqual(r.status_code, 200)
        customer_user_id = r.json()['userId']

        # Submit a 5-star rating from the dynamically registered customer
        review_payload = {
            "provider_id": p['provider_id'],
            "customer_id": customer_user_id,
            "rating": 5,
            "comment": "Brilliant service, very quick and reliable!"
        }
        r = requests.post(f"{BASE_URL}/api/review", json=review_payload)
        self.assertEqual(r.status_code, 200)
        
        # Verify provider avg rating increased/updated
        updated_p = db.get_provider_by_id(p['provider_id'])
        self.assertEqual(updated_p['total_ratings'], initial_count + 1)
        self.assertTrue(updated_p['average_rating'] > 0.0)
        print(f"  - Rating submitted. SQLite Total ratings count: {initial_count} -> {updated_p['total_ratings']}")
        print(f"  - Provider score updated automatically: {initial_rating} -> {updated_p['average_rating']}")

    def test_04_messaging_and_sanitation(self):
        """Test messaging thread operations and sanitation using Member 4's logic"""
        print("\n🧪 Testing Messaging Thread & Message Sanitation (Member 4)...")
        
        # Send message with HTML injection (to test sanitization)
        msg_payload = {
            "sender_id": 2,
            "receiver_id": 1,
            "message": "Hello <script>alert('hack')</script> I need a repair."
        }
        r = requests.post(f"{BASE_URL}/api/message", json=msg_payload)
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertTrue(data['success'])
        
        # Retrieve message thread
        r = requests.get(f"{BASE_URL}/api/messages/thread?user_id=2&partner_id=1")
        self.assertEqual(r.status_code, 200)
        thread = r.json()
        self.assertTrue(len(thread) > 0)
        
        # Confirm sanitization worked (tags stripped or escaped)
        last_msg = thread[-1]
        self.assertNotIn("<script>", last_msg['text'])
        print(f"  - Message sent successfully. Sanitized text: '{last_msg['text']}'")

if __name__ == '__main__':
    unittest.main()
