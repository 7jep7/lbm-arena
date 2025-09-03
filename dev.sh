#!/bin/bash

echo "🎮 LBM Arena - Quick Start (Conda)"
echo "=================================="

# Set conda environment path on the big partition
CONDA_ENV_PATH="/mnt/nvme0n1p8/conda-envs/lbm-arena"
CONDA_ENV_NAME="lbm-arena"

# Initialize conda for this shell
source "$(conda info --base)/etc/profile.d/conda.sh"

# Check if conda environment exists
if [ ! -d "$CONDA_ENV_PATH" ]; then
    echo "📦 Creating conda environment on big partition..."
    echo "   Location: $CONDA_ENV_PATH"
    
    # Option 1: Create from environment.yml (recommended)
    if [ -f "environment.yml" ]; then
        conda env create -f environment.yml -p "$CONDA_ENV_PATH"
    else
        # Option 2: Create basic environment and use pip
        conda create -p "$CONDA_ENV_PATH" python=3.11 -y
        conda activate "$CONDA_ENV_PATH"
        pip install -r requirements.txt
    fi
else
    echo "� Using existing conda environment..."
    conda activate "$CONDA_ENV_PATH"
fi

# Ensure environment is activated
if [[ "$CONDA_PREFIX" != "$CONDA_ENV_PATH" ]]; then
    echo "🔄 Activating conda environment..."
    conda activate "$CONDA_ENV_PATH"
fi

# Install/update dependencies if using pip method
if [ -f "requirements.txt" ] && [ ! -f "environment.yml" ]; then
    echo "📦 Installing/updating dependencies..."
    pip install -q -r requirements.txt
fi

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
