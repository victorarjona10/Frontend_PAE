#!/bin/bash
# Quick start script for OmniTrack Frontend

echo "🧳 OmniTrack Frontend - Quick Start"
echo "===================================="
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.10 or higher."
    exit 1
fi

echo "✓ Python found: $(python3 --version)"

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip not found. Please install pip."
    exit 1
fi

echo "✓ pip found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
pip3 install -r requirements.txt

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Check backend connection (optional)
echo "🔍 Checking backend connection..."
if curl -s http://localhost:8000/health > /dev/null 2>&1; then
    echo "✓ Backend API is reachable at http://localhost:8000"
    echo "  Mode: Real Backend API"
else
    echo "⚠️  Backend API not reachable at http://localhost:8000"
    echo "  Mode: Simulation (local data generation)"
fi

echo ""
echo "🚀 Starting Streamlit app..."
echo "   Access at: http://localhost:8501"
echo ""
echo "📝 Login credentials (API mode):"
echo "   Admin:      admin / password"
echo "   Passenger:  passenger_1 / password"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Start Streamlit
streamlit run PAE_frontend.py
