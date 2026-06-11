# API Documentation - Payment Webhook System

## Base URL

http://localhost:8000


## Authentication

All webhook requests require signature verification using HMAC-SHA256 with the shared secret `test_secret`.

---

## Endpoints

### 1. Webhook Receiver
Receive payment status updates from payment providers.

**Endpoint:** `POST /webhook/payments`

**Headers:**
| Header | Value |
|--------|-------|
| Content-Type | application/json |
| X-Razorpay-Signature | HMAC-SHA256 signature of the request body |

**Request Body Example (Razorpay format):**
```json
{
  "event": "payment.authorized",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_014",
        "status": "authorized",
        "amount": 5000,
        "currency": "INR"
      }
    }
  },
  "created_at": 1751889865,
  "id": "evt_auth_014"
}

Success Response (200 OK):

{
  "status": "success",
  "data": {
    "event_id": "evt_auth_014",
    "payment_id": "pay_014"
  }
}


Duplicate Event Response (200 OK):

{
  "status": "ignored",
  "message": "Duplicate event received"
}

Error Responses:

Status Code	Description
400	Invalid JSON payload
403	Invalid or missing signature
500	Internal server error


2. Get Payment Events
Retrieve all status updates for a specific payment.

Endpoint: GET /payments/{payment_id}/events

Path Parameters:

Parameter	Type	Required	Description
payment_id	string	Yes	Unique identifier of the payment
Success Response (200 OK):


[
  {
    "event_type": "payment.failed",
    "received_at": "2025-07-07T10:34:45Z"
  },
  {
    "event_type": "payment.authorized",
    "received_at": "2025-07-08T12:00:00Z"
  },
  {
    "event_type": "payment.captured",
    "received_at": "2025-07-08T12:01:23Z"
  }
]


Error Responses:

Status Code	Description
400	Invalid payment_id
404	No events found for the payment_id


3. Get Latest Payment Event
Retrieve the most recent status update for a payment.

Endpoint: GET /payments/{payment_id}/events/latest

Path Parameters:

Parameter	Type	Required	Description
payment_id	string	Yes	Unique identifier of the payment
Success Response (200 OK):


{
  "event_type": "payment.captured",
  "received_at": "2025-07-08T12:01:23Z"
}


Error Response (404 Not Found):

{
  "detail": "Payment not found"
}


4. Webhook Statistics
Get statistics about processed webhooks.

Endpoint: GET /webhook/stats

Success Response (200 OK):


{
  "total_events": 42,
  "unique_payments": 15,
  "status": "active"
}

5. Health Check
Check if the service is running.

Endpoint: GET /health

Success Response (200 OK):

{
  "status": "healthy",
  "system": "payment-webhook"
}

Signature Generation
The signature is generated using HMAC-SHA256:

Python Example:

import hmac
import hashlib

secret = "test_secret"
payload = open('payload.json', 'rb').read()
signature = hmac.new(
    secret.encode('utf-8'),
    payload,
    hashlib.sha256
).hexdigest()

# Send with header: X-Razorpay-Signature: {signature}

Command Line Example:

# Generate signature
SIGNATURE=$(python -c "
import hmac, hashlib
with open('mock_payloads/payment_authorized.json', 'rb') as f:
    payload = f.read()
    sig = hmac.new(b'test_secret', payload, hashlib.sha256).hexdigest()
    print(sig)
")

# Send request
curl -X POST http://localhost:8000/webhook/payments \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: $SIGNATURE" \
  -d @mock_payloads/payment_authorized.json

  Testing with cURL
1. Send a valid webhook:

curl -X POST http://localhost:8000/webhook/payments \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: your_generated_signature" \
  -d @mock_payloads/payment_authorized.json


  2. Send webhook with invalid signature (should return 403):

  curl -X POST http://localhost:8000/webhook/payments \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: invalid_signature" \
  -d @mock_payloads/payment_authorized.json

3. Query payment events:

curl http://localhost:8000/payments/pay_014/events

4. Query latest event:

curl http://localhost:8000/payments/pay_014/events/latest

5. Get statistics:

curl http://localhost:8000/webhook/stats

6. Health check:

curl http://localhost:8000/health

Mock Payload Examples

payment_authorized.json

{
  "event": "payment.authorized",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_014",
        "status": "authorized",
        "amount": 5000,
        "currency": "INR"
      }
    }
  },
  "created_at": 1751889865,
  "id": "evt_auth_014"
}


payment_captured.json

{
  "event": "payment.captured",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_004",
        "status": "captured",
        "amount": 4000,
        "currency": "INR"
      }
    }
  },
  "created_at": 1751886985,
  "id": "evt_cap_004"
}

payment_failed.json

{
  "event": "payment.failed",
  "payload": {
    "payment": {
      "entity": {
        "id": "pay_001",
        "status": "failed",
        "amount": 1000,
        "currency": "INR"
      }
    }
  },
  "created_at": 1751886085,
  "id": "evt_fail_001"
}


Data Storage Schema
Payment Events Table
Column	Type	Description
id	Integer	Auto-incrementing primary key
event_id	String(255)	Unique event identifier (unique index)
payment_id	String(255)	Payment identifier (indexed)
event_type	String(100)	Type of event
payload	Text	Complete JSON payload
received_at	DateTime	When the event was received
created_at	DateTime	When the record was created

Error Handling
The system handles the following error scenarios:

Scenario	HTTP Status	Response
Missing signature header	403	{"detail": "Invalid or missing signature"}
Invalid signature	403	{"detail": "Invalid or missing signature"}
Malformed JSON	400	{"detail": "Invalid JSON payload"}
Duplicate event_id	200	{"status": "ignored", "message": "Duplicate event received"}
Payment not found	404	{"detail": "No events found for payment_id: xxx"}
Invalid payment_id	400	{"detail": "Invalid payment_id"}

Rate Limiting
Current implementation does not include rate limiting. For production, consider adding:

Redis-based rate limiter

Nginx rate limiting

FastAPI middleware for rate limiting


Support
For issues or questions, please open an issue on GitHub:
https://github.com/chauhanchintu/Payment-Webhook-System/issues



### Step 2: Commit the changes
1. Scroll down to **"Commit changes"** section
2. Commit message: `docs: Add complete API documentation`
3. Click **"Commit changes"**

## Fix 3: Also Check app/__init__.py

I noticed `app/_init_.py` (with underscore) instead of `app/__init__.py` (with double underscore). 

### Fix the filename:
1. Click on `app/_init_.py`
2. Click the trash icon 🗑️ to delete it
3. Click **"Add file"** → **"Create new file"**
4. Path: `app/__init__.py` (with double underscores on both sides)
5. Content: Leave empty or add:
   ```python
   # Payment Webhook System package


   
