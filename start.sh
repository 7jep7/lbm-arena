#!/bin/bash

# LBM Arena Backend Startup Script

echo "🎮 Starting LBM Arena Backend..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update the .env file with your actual API keys and database URL"
fi

# Create database tables (optional - only if DATABASE_URL is configured)
echo "Creating database tables..."
python create_db.py 2>/dev/null || echo "Database creation skipped (DATABASE_URL not configured)"

# Run tests
echo "Running setup tests..."
python test_setup.py

echo ""
echo "🚀 To start the server, run:"
echo "   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000"
echo ""
echo "📚 API documentation will be available at:"
echo "   http://localhost:8000/docs"
