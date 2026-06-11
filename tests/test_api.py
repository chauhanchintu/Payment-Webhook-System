import pytest
import json
import hmac
import hashlib
from fastapi.testclient import TestClient
from app.main import app
from app.config import Config

client = TestClient(app)

def generate_signature(payload: bytes) -> str:
    """Generate test signature"""
    return hmac.new(
        Config.SECRET_KEY.encode('utf-8'),
        payload,
        hashlib.sha256
    ).hexdigest()

def test_webhook_valid_signature():
    """Test webhook endpoint with valid signature"""
    with open('mock_payloads/payment_authorized.json', 'rb') as f:
        payload = f.read()
    
    signature = generate_signature(payload)
    
    response = client.post(
        '/webhook/payments',
        content=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': signature
        }
    )
    
    assert response.status_code == 200
    assert response.json()['status'] == 'success'

def test_webhook_invalid_signature():
    """Test webhook endpoint with invalid signature"""
    with open('mock_payloads/payment_authorized.json', 'rb') as f:
        payload = f.read()
    
    response = client.post(
        '/webhook/payments',
        content=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': 'invalid_signature'
        }
    )
    
    assert response.status_code == 403

def test_webhook_invalid_json():
    """Test webhook endpoint with invalid JSON"""
    response = client.post(
        '/webhook/payments',
        content=b'invalid json',
        headers={
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': 'some_signature'
        }
    )
    
    assert response.status_code == 400

def test_duplicate_event():
    """Test that duplicate events are ignored"""
    with open('mock_payloads/payment_authorized.json', 'rb') as f:
        payload = f.read()
    
    signature = generate_signature(payload)
    
    # First request
    response1 = client.post(
        '/webhook/payments',
        content=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': signature
        }
    )
    
    # Duplicate request
    response2 = client.post(
        '/webhook/payments',
        content=payload,
        headers={
            'Content-Type': 'application/json',
            'X-Razorpay-Signature': signature
        }
    )
    
    assert response2.json()['status'] == 'ignored'

def test_get_payment_events():
    """Test GET endpoint for payment events"""
    # First create some events
    for payload_file in ['payment_authorized.json', 'payment_captured.json']:
        with open(f'mock_payloads/{payload_file}', 'rb') as f:
            payload = f.read()
        
        signature = generate_signature(payload)
        client.post(
            '/webhook/payments',
            content=payload,
            headers={
                'Content-Type': 'application/json',
                'X-Razorpay-Signature': signature
            }
        )
    
    # Query events
    response = client.get('/payments/pay_004/events')
    assert response.status_code == 200
    events = response.json()
    assert len(events) > 0
    assert 'event_type' in events[0]
    assert 'received_at' in events[0]

def test_get_nonexistent_payment():
    """Test GET endpoint for non-existent payment"""
    response = client.get('/payments/nonexistent/events')
    assert response.status_code == 404