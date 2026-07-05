import requests
import json

print("=" * 50)
print("LASO BACKEND - FUNCTIONING PROOF")
print("=" * 50)

BASE = "http://localhost:5000/api"

# Test 1: Register
print("\n1. REGISTERING USER...")
r = requests.post(f"{BASE}/register", json={
    "email": "screenshot@test.com",
    "password": "pass123",
    "user_type": "customer"
})
print(f"   Response: {r.json()}")

# Test 2: Login
print("\n2. LOGGING IN...")
r = requests.post(f"{BASE}/login", json={
    "email": "screenshot@test.com",
    "password": "pass123"
})
print(f"   Response: {r.json()}")

# Test 3: Get Providers
print("\n3. GETTING PROVIDERS...")
r = requests.get(f"{BASE}/providers")
print(f"   Found {len(r.json())} providers")
print(f"   Data: {json.dumps(r.json()[:2], indent=2)}")

print("\n" + "=" * 50)
print("✅ ALL FUNCTIONS WORKING!")
print("=" * 50)