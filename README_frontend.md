## LASO front-end end points

## Backend API Integration Contracts

All endpoints are configured in `frontend/js/api.js`. You can toggle between the **Mock Database** (stored in `localStorage` for visual testing) and the **Real Python Backend** by editing `api.js`:

```javascript
export const USE_MOCK_API = false; // Toggle to false to use the real Python backend
export const API_BASE_URL = 'http://localhost:8000'; // Replace with the real backend address
```

Below are the JSON endpoints the frontend expects from the Python backend:

### 1. User Registration (`/api/register`)
- **Method**: `POST`
- **Request Payload (Customer)**:
  ```json
  {
    "name": "Azaam Customer",
    "email": "azaam@laso.lk",
    "phone": "0771112223",
    "password": "password123",
    "district": "Colombo",
    "address": "Bambalapitiya, Colombo",
    "userType": "customer"
  }
  ```
- **Request Payload (Provider)**:
  ```json
  {
    "name": "Amal Perera",
    "email": "amal@laso.lk",
    "phone": "0771234567",
    "password": "password123",
    "district": "Colombo",
    "address": "123 Galle Road, Colombo 3",
    "userType": "provider",
    "serviceType": "plumbing",
    "lat": 6.9271,
    "lon": 79.8612,
    "description": "24/7 plumbing emergency service. Leak repairs."
  }
  ```
- **Response**:
  ```json
  {
    "userId": "usr_901",
    "userType": "customer",
    "name": "Azaam Customer",
    "email": "azaam@laso.lk"
  }
  ```

### 2. User Login (`/api/login`)
- **Method**: `POST`
- **Request Payload**:
  ```json
  {
    "email": "azaam@laso.lk",
    "password": "password123"
  }
  ```
- **Response**:
  ```json
  {
    "userId": "usr_901",
    "userType": "customer",
    "name": "Azaam Customer",
    "email": "azaam@laso.lk",
    "district": "Colombo",
    "address": "Bambalapitiya, Colombo"
  }
  ```

### 3. Fetch Nearby Providers (`/api/providers/nearby`)
- **Method**: `GET`
- **Query Parameters**:
  - `lat`: Customer's latitude (float)
  - `lon`: Customer's longitude (float)
  - `district`: Filter by district name (string)
  - `service`: Optional service category code (string, e.g. `plumbing`)
  - `query`: Optional keyword search filter (string)
- **Response**: Sorted array of provider objects (closest first):
  ```json
  [
    {
      "id": "p1",
      "name": "Amal Perera",
      "email": "amal@laso.lk",
      "phone": "0771234567",
      "serviceType": "plumbing",
      "district": "Colombo",
      "address": "123 Galle Road, Colombo 3",
      "lat": 6.9271,
      "lon": 79.8612,
      "description": "24/7 plumbing emergency service...",
      "avgRating": 4.8,
      "reviewsCount": 3,
      "distance": 0.8
    }
  ]
  ```

### 4. Fetch Provider Details & Reviews (`/api/provider/{id}`)
- **Method**: `GET`
- **Response**:
  ```json
  {
    "id": "p1",
    "name": "Amal Perera",
    "phone": "0771234567",
    "serviceType": "plumbing",
    "district": "Colombo",
    "address": "123 Galle Road, Colombo 3",
    "lat": 6.9271,
    "lon": 79.8612,
    "description": "24/7 plumbing emergency service...",
    "avgRating": 4.8,
    "reviewsCount": 3,
    "reviews": [
      {
        "id": "r1",
        "customerName": "Harsha Bandara",
        "rating": 5,
        "comment": "Amal was extremely quick to arrive...",
        "date": "2026-05-15"
      }
    ]
  }
  ```

### 5. Submit Rating and Review (`/api/review`)
- **Method**: `POST`
- **Request Payload**:
  ```json
  {
    "provider_id": "p1",
    "customer_id": "c1",
    "rating": 5,
    "comment": "Excellent quality of work!"
  }
  ```
- **Response**:
  ```json
  {
    "id": "r_105",
    "providerId": "p1",
    "customerName": "Azaam Customer",
    "rating": 5,
    "comment": "Excellent quality of work!",
    "date": "2026-06-07"
  }
  ```

### 6. Send Messages (`/api/message`)
- **Method**: `POST`
- **Request Payload**:
  ```json
  {
    "sender_id": "c1",
    "receiver_id": "p1",
    "message": "Hello, is tomorrow morning free?"
  }
  ```
- **Response**:
  ```json
  {
    "id": "msg_401",
    "senderId": "c1",
    "receiverId": "p1",
    "text": "Hello, is tomorrow morning free?",
    "timestamp": "2026-06-07T14:20:00Z"
  }
  ```

### 7. Fetch Active Conversations (`/api/conversations`)
- **Method**: `GET`
- **Query Parameters**: `user_id={id}`
- **Response**:
  ```json
  [
    {
      "partnerId": "p1",
      "partnerName": "Amal Perera",
      "partnerService": "plumbing",
      "lastMessage": "Yes, I can come by Colombo around 10:00 AM.",
      "timestamp": "2026-06-07T14:10:00Z"
    }
  ]
  ```

### 8. Fetch Thread Messages (`/api/messages/thread`)
- **Method**: `GET`
- **Query Parameters**: `user_id={id}&partner_id={partnerId}`
- **Response**: Array of chronological messages:
  ```json
  [
    {
      "id": "msg_001",
      "senderId": "c1",
      "receiverId": "p1",
      "text": "Hello Amal, do you have time tomorrow?",
      "timestamp": "2026-06-07T14:00:00.000Z"
    },
    {
      "id": "msg_002",
      "senderId": "p1",
      "receiverId": "c1",
      "text": "Yes, I can come by Colombo around 10:00 AM.",
      "timestamp": "2026-06-07T14:10:00.000Z"
    }
  ]
  ```

### 9. Update Provider Profile (`/api/provider/profile/update`)
- **Method**: `POST`
- **Request Payload**:
  ```json
  {
    "id": "p1",
    "phone": "0771234567",
    "district": "Colombo",
    "address": "123 Galle Road, Colombo 3",
    "lat": 6.9271,
    "lon": 79.8612,
    "description": "Updated service description details."
  }
  ```
- **Response**:
  ```json
  {
    "success": true
  }
  ```

---

## CORS Requirements for the Backend Team

Because the frontend runs from a local server (e.g. `http://127.0.5.1:5500` or `http://localhost:8080`) and requests are dispatched via the `fetch` API, the Python backend **must enable CORS** (Cross-Origin Resource Sharing).

### CORS Implementation in Python (Flask/FastAPI)

If you are building the backend in **FastAPI**, add the following middleware:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Or specify ["http://localhost:8080", "http://127.0.5.1:5500"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

If you are building the backend in **Flask**, use the `flask-cors` package:
```python
from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})
```
