#!/bin/bash

# LBM Arena - Full Stack Startup Script

echo "🎮 Starting LBM Arena - Full Stack"
echo "=================================="

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: requirements.txt not found. Please run this script from the project root."
    exit 1
fi

# Start backend
echo "🚀 Starting Backend..."
echo "---------------------"

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install -q -r requirements.txt

# Start the FastAPI server in the background
echo "Starting FastAPI server on http://localhost:8000..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload > backend.log 2>&1 &
BACKEND_PID=$!

# Wait a moment for the backend to start
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running on http://localhost:8000"
    echo "📚 API Documentation: http://localhost:8000/docs"
else
    echo "❌ Backend failed to start. Check backend.log for details."
    exit 1
fi

# Start frontend
echo ""
echo "🌐 Starting Frontend..."
echo "----------------------"

# Check if Python has a simple HTTP server
if command -v python3 > /dev/null; then
    cd frontend
    echo "Starting frontend server on http://localhost:3000..."
    python3 -m http.server 3000 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    cd ..
    
    # Wait a moment for the frontend to start
    sleep 2
    
    if curl -s http://localhost:3000 > /dev/null; then
        echo "✅ Frontend is running on http://localhost:3000"
    else
        echo "❌ Frontend failed to start. Check frontend.log for details."
    fi
else
    echo "❌ Python3 not found. Cannot start frontend server."
fi

echo ""
echo "🎉 LBM Arena is now running!"
echo "============================="
echo "🖥️  Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📖 API Docs: http://localhost:8000/docs"
echo ""
echo "📋 Process IDs:"
echo "   Backend PID: $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   Frontend PID: $FRONTEND_PID"
fi
echo ""
echo "🛑 To stop the servers:"
echo "   kill $BACKEND_PID"
if [ ! -z "$FRONTEND_PID" ]; then
    echo "   kill $FRONTEND_PID"
fi
echo ""
echo "📜 Logs:"
echo "   Backend: tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "Press Ctrl+C to stop monitoring, but servers will keep running."

# Keep the script running to show live logs
trap 'echo "Monitoring stopped. Servers are still running."; exit 0' INT

echo "Monitoring logs (Ctrl+C to stop monitoring):"
echo "============================================="
tail -f backend.log frontend.log 2>/dev/null
