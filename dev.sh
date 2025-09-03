#!/bin/bash

echo "🎮 LBM Arena - Quick Start"
echo "=========================="

# Setup backend
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Create .env if needed
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "⚠️  Created .env file - update with your API keys if needed"
fi

# Start backend in background
echo "🚀 Starting backend on http://localhost:8000..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check backend health
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend running"
else
    echo "❌ Backend failed to start"
    exit 1
fi

# Start frontend
echo "🌐 Starting frontend on http://localhost:3000..."
cd frontend
python3 -m http.server 3000 > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 2
echo "✅ Frontend running"

echo ""
echo "🎯 Ready for testing!"
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both servers"

# Trap Ctrl+C to clean up
trap 'echo "Stopping servers..."; kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT

# Keep script running
wait
