# Payment Webhook System

A minimal, secure webhook listener system for payment status updates from providers like Razorpay and PayPal.

## Features

- 🔐 Secure signature verification using HMAC-SHA256
- 🔄 Idempotent event processing to prevent duplicates
- 💾 Persistent storage with PostgreSQL/SQLite
- 📊 RESTful API for querying payment events
- 🚀 High performance with async FastAPI
- 🐳 Docker support for easy deployment

## Prerequisites

- Python 3.11+
- PostgreSQL (or use SQLite for testing)
- Docker (optional)

## Quick Start

### Local Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/payment-webhook-system.git
cd payment-webhook-system