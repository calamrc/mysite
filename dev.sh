#!/bin/bash
# Development script for running the full-stack application

echo "🎄 Gift Exchange App - Development Mode"
echo "========================================"

# Check if we have the required tools
command -v python >/dev/null 2>&1 || { echo "❌ Python is required but not installed."; exit 1; }
command -v node >/dev/null 2>&1 || { echo "❌ Node.js is required but not installed."; exit 1; }
command -v npm >/dev/null 2>&1 || { echo "❌ npm is required but not installed."; exit 1; }

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Setting up Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🐍 Activating Python virtual environment..."
source venv/bin/activate || source venv/Scripts/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
pip install -r requirements.txt

# Check if frontend dependencies are installed
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing Node.js dependencies..."
    cd frontend
    npm install
    cd ..
fi

# Build frontend for production (served by Flask)
echo "🏗️  Building frontend for production..."
cd frontend
npm run build
cd ..

# Start backend in background
echo "🚀 Starting Flask backend (http://localhost:5000)..."
python flask_app.py &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 2

# Start frontend in background
echo "🎨 Starting Vue.js frontend (http://localhost:5173)..."
cd frontend
npm run dev &
FRONTEND_PID=$!

cd ..

echo ""
echo "✅ Development servers started!"
echo ""
echo "🌐 Frontend (Vue SPA): http://localhost:5173"
echo "🔧 Backend API: http://localhost:5000/api"
echo ""
echo "💡 Press Ctrl+C to stop all servers"

# Function to kill background processes
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
