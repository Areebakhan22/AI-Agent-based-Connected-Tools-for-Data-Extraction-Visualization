#!/bin/bash
# Start backend API server for React diagrams

echo "Starting SysML Diagram Backend Server..."
echo ""

# Check if virtual environment exists
if [ -d "venv" ]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Install backend dependencies if needed
if [ ! -f "backend/.deps_installed" ]; then
    echo "Installing backend dependencies..."
    pip install -r backend/requirements.txt
    touch backend/.deps_installed
fi

# Start the server
cd backend
python api_server.py

