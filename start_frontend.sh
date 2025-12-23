#!/bin/bash
# Start React frontend development server

echo "Starting React Frontend..."
echo ""

cd frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm install
fi

# Start development server
echo "Starting Vite development server..."
echo "Frontend will be available at: http://localhost:3000"
echo ""
npm run dev

