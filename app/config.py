import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'test_secret')
    DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:password@localhost:5432/webhook_db')
    WEBHOOK_PORT = int(os.getenv('PORT', 8000))
    SIGNATURE_HEADER = 'X-Razorpay-Signature'