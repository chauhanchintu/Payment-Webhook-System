from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging
from typing import Dict, Any

from app.webhook_handler import webhook_handler
from app.database import db_manager
from app.api import router as api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events"""
    logger.info("Starting up webhook system...")
    # Initialize database tables
    from app.database import Base
    Base.metadata.create_all(db_manager.engine)
    yield
    logger.info("Shutting down...")

# Create FastAPI app
app = FastAPI(
    title="Payment Webhook System",
    description="Minimal webhook system for payment status updates",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def capture_raw_body(request: Request, call_next):
    """Capture raw request body for signature verification"""
    raw_body = await request.body()
    request.state.raw_body = raw_body
    response = await call_next(request)
    return response

@app.post("/webhook/payments")
async def webhook_receiver(request: Request):
    """Receive and process payment webhook events"""
    success, result, error = webhook_handler.process_webhook(request)
    
    if not success:
        if "signature" in error.lower():
            raise HTTPException(status_code=403, detail=error)
        elif "json" in error.lower():
            raise HTTPException(status_code=400, detail=error)
        else:
            raise HTTPException(status_code=400, detail=error)
    
    if result is None:
        # Duplicate event
        return JSONResponse(
            status_code=200,
            content={"status": "ignored", "message": "Duplicate event received"}
        )
    
    logger.info(f"Processed webhook: {result}")
    return JSONResponse(
        status_code=200,
        content={"status": "success", "data": result}
    )

# Include API routes
app.include_router(api_router)

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "system": "payment-webhook"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=Config.WEBHOOK_PORT,
        reload=True
    )