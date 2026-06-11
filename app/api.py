from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

from app.database import db_manager

router = APIRouter()

class PaymentEventResponse(BaseModel):
    event_type: str
    received_at: str

@router.get("/payments/{payment_id}/events", response_model=List[PaymentEventResponse])
async def get_payment_events(payment_id: str):
    """
    Get all payment status events for a specific payment ID
    
    Returns events in chronological order
    """
    if not payment_id or not payment_id.strip():
        raise HTTPException(status_code=400, detail="Invalid payment_id")
    
    events = db_manager.get_payment_events(payment_id)
    
    if not events:
        raise HTTPException(
            status_code=404, 
            detail=f"No events found for payment_id: {payment_id}"
        )
    
    return events

@router.get("/payments/{payment_id}/events/latest")
async def get_latest_payment_event(payment_id: str):
    """Get the latest payment event for a payment ID"""
    events = db_manager.get_payment_events(payment_id)
    
    if not events:
        raise HTTPException(status_code=404, detail="Payment not found")
    
    return events[-1]  # Last event is the latest due to chronological order

@router.get("/webhook/stats")
async def get_webhook_stats():
    """Get statistics about processed webhooks"""
    from sqlalchemy import func
    from app.database import PaymentEvent, db_manager
    
    session = db_manager.get_session()
    try:
        total_events = session.query(func.count(PaymentEvent.id)).scalar()
        unique_payments = session.query(func.count(func.distinct(PaymentEvent.payment_id))).scalar()
        
        return {
            "total_events": total_events,
            "unique_payments": unique_payments,
            "status": "active"
        }
    finally:
        session.close()