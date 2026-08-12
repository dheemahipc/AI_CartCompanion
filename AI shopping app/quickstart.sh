#!/bin/bash

# ShopAssist AI - Quick Start Script
# Sets up and starts the FastAPI backend + React frontend

set -e

echo "🛍️  ShopAssist AI - Quick Start"
echo "=============================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION found"

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt not found. Please run this script from the retail-data-copilot directory."
    exit 1
fi

# Setup virtual environment
if [ ! -d ".venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv .venv
fi

echo "📦 Installing Python dependencies..."
.venv/bin/pip install -r requirements.txt
echo "✅ Python dependencies installed"
echo ""

# Check .env file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys:"
    echo "   GROQ_API_KEY=your_groq_api_key_here"
    echo ""
    exit 1
fi

# Check if Groq API key is set
if grep -q "GROQ_API_KEY=" .env && ! grep -q "GROQ_API_KEY=$" .env; then
    echo "✅ Groq API key found in .env"
else
    echo "⚠️  Groq API key not configured in .env"
    echo "   Please add: GROQ_API_KEY=your_groq_api_key_here"
    exit 1
fi

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd frontend
if command -v bun &> /dev/null; then
    bun install
else
    npm install
fi
cd ..
echo "✅ Frontend dependencies installed"
echo ""

# Start services
echo "🚀 Starting ShopAssist AI..."
echo ""

# Start backend
echo "  Starting FastAPI backend on http://localhost:8000..."
PYTHONUNBUFFERED=1 .venv/bin/python -m uvicorn app.app:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to be ready
echo "  Waiting for backend to load knowledge base..."
sleep 5
until curl -s http://localhost:8000/health > /dev/null 2>&1; do
    sleep 2
done
echo "  ✅ Backend ready"

# Start frontend
echo "  Starting React frontend on http://localhost:3000..."
cd frontend
if command -v bun &> /dev/null; then
    bun run dev &
else
    npm run dev &
fi
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 ShopAssist AI is running!"
echo "   Frontend: http://localhost:3000"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop both services."

# Trap Ctrl+C to kill both processes
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit" INT TERM
wait
