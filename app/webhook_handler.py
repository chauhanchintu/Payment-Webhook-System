import hmac
import hashlib
import json
from typing import Tuple, Optional, Dict, Any
from fastapi import HTTPException, Request
from datetime import datetime

from app.config import Config
from app.database import db_manager

class WebhookHandler:
    def __init__(self):
        self.secret = Config.SECRET_KEY.encode('utf-8')
    
    def verify_signature(self, payload: bytes, signature: str) -> bool:
        """Verify webhook signature using HMAC-SHA256"""
        if not signature:
            return False
        
        expected = hmac.new(
            self.secret,
            payload,
            hashlib.sha256
        ).hexdigest()
        
        # Constant time comparison to prevent timing attacks
        return hmac.compare_digest(expected, signature)
    
    def parse_razorpay_payload(self, payload_data: Dict[str, Any]) -> Tuple[str, str, str]:
        """Parse Razorpay format payload"""
        event_type = payload_data.get('event', '')
        payload_content = payload_data.get('payload', {})
        
        # Extract payment entity
        payment_entity = payload_content.get('payment', {}).get('entity', {})
        payment_id = payment_entity.get('id', '')
        
        # Extract event ID
        event_id = payload_data.get('id', '')
        
        # Fallback: create event_id if not provided
        if not event_id:
            event_id = f"{event_type}_{payment_id}_{int(datetime.utcnow().timestamp())}"
        
        return event_id, payment_id, event_type
    
    def process_webhook(self, request: Request) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """Process incoming webhook request"""
        # Read raw body
        raw_body = request.state.raw_body
        
        # Verify signature
        signature = request.headers.get(Config.SIGNATURE_HEADER, '')
        if not self.verify_signature(raw_body, signature):
            return False, None, "Invalid or missing signature"
        
        # Parse JSON
        try:
            payload = json.loads(raw_body.decode('utf-8'))
        except json.JSONDecodeError:
            return False, None, "Invalid JSON payload"
        
        # Parse payload based on format
        try:
            # Try Razorpay format first
            event_id, payment_id, event_type = self.parse_razorpay_payload(payload)
            
            if not payment_id:
                raise ValueError("Could not extract payment_id from payload")
            
            # Process with idempotency
            session = db_manager.get_session()
            try:
                saved_event = db_manager.save_event(
                    session, event_id, payment_id, event_type, payload
                )
                
                if not saved_event:
                    return True, None, "Duplicate event ignored"
                
                return True, {"event_id": event_id, "payment_id": payment_id}, None
            finally:
                session.close()
                
        except Exception as e:
            return False, None, f"Error processing payload: {str(e)}"

webhook_handler = WebhookHandler()