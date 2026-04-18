#!/bin/bash

# Frontend Startup Script
# Tendworks Private Limited

set -e

echo "🎨 Starting Leave Agent Manager Dashboard..."
echo "=========================================="

# Check if in frontend directory
if [ ! -f "app.py" ]; then
    echo "Error: Please run this script from the frontend directory"
    exit 1
fi

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

# Check if backend is running
echo "🔍 Checking backend API..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ Backend API is running"
else
    echo "⚠️  Warning: Backend API is not responding"
    echo "   Please start the backend first:"
    echo "   cd .. && python -m uvicorn app.main:app --reload"
    echo ""
    read -p "Continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Starting dashboard..."
echo "🌐 Dashboard: http://localhost:8501"
echo ""

# Start Streamlit
streamlit run app.py
