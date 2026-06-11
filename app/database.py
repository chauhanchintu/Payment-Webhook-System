from sqlalchemy import create_engine, Column, String, DateTime, Text, Integer, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from datetime import datetime
from typing import Optional
import json

from app.config import Config

Base = declarative_base()

class PaymentEvent(Base):
    __tablename__ = 'payment_events'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    event_id = Column(String(255), unique=True, nullable=False, index=True)
    payment_id = Column(String(255), nullable=False, index=True)
    event_type = Column(String(100), nullable=False)
    payload = Column(Text, nullable=False)
    received_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    __table_args__ = (
        Index('idx_payment_received', 'payment_id', 'received_at'),
    )

class DatabaseManager:
    def __init__(self):
        self.engine = create_engine(
            Config.DATABASE_URL,
            poolclass=QueuePool,
            pool_size=10,
            max_overflow=20,
            pool_pre_ping=True
        )
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)
    
    def get_session(self) -> Session:
        return self.SessionLocal()
    
    def save_event(self, session: Session, event_id: str, payment_id: str, 
                   event_type: str, payload: dict) -> Optional[PaymentEvent]:
        """Save event with idempotency check"""
        # Check for duplicate event
        existing = session.query(PaymentEvent).filter(
            PaymentEvent.event_id == event_id
        ).first()
        
        if existing:
            return None
        
        # Create new event
        event = PaymentEvent(
            event_id=event_id,
            payment_id=payment_id,
            event_type=event_type,
            payload=json.dumps(payload)
        )
        session.add(event)
        session.commit()
        return event
    
    def get_payment_events(self, payment_id: str) -> list:
        """Get all events for a payment ID in chronological order"""
        session = self.get_session()
        try:
            events = session.query(PaymentEvent).filter(
                PaymentEvent.payment_id == payment_id
            ).order_by(PaymentEvent.received_at.asc()).all()
            
            return [
                {
                    "event_type": event.event_type,
                    "received_at": event.received_at.isoformat() + "Z"
                }
                for event in events
            ]
        finally:
            session.close()

db_manager = DatabaseManager()