#!/bin/bash

# Leave Agent Backend - Startup Script
# Tendworks Private Limited

set -e

echo "🚀 Starting Leave Review Agent Backend..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Generate mock data if not exists
if [ ! -f "data/team_schedules.json" ]; then
    echo "📊 Generating mock data..."
    python -m app.mock_data
else
    echo "✅ Mock data already exists"
fi

# Check for .env file
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: .env file not found. Creating from .env.example..."
    cp .env.example .env
    echo "   Please edit .env and add your GEMINI_API_KEY"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Starting server..."
echo "📍 API: http://localhost:8000"
echo "📖 Docs: http://localhost:8000/docs"
echo "❤️  Health: http://localhost:8000/health"
echo ""

# Start the server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
