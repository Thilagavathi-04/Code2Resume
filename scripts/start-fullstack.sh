#!/bin/bash

# Start Full Stack Application
# This script starts both the FastAPI backend and React frontend

cd "$(dirname "$0")/.."

echo "🚀 Starting Code2Resume Full Stack Application"
echo "================================================"
echo ""
echo "Backend API: http://localhost:8001"
echo "Frontend: http://localhost:5173"
echo ""

# Function to cleanup background processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    exit 0
}

trap cleanup EXIT INT TERM

# Start Backend
echo "📦 Starting FastAPI Backend..."
uv run uvicorn backend.app:app --host 0.0.0.0 --port 8001 --reload &
BACKEND_PID=$!
echo "✅ Backend started (PID: $BACKEND_PID)"

# Wait for backend to start
sleep 3

# Start Frontend
echo ""
echo "⚛️  Starting React Frontend..."
cd frontend-react
npm run dev &
FRONTEND_PID=$!
echo "✅ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "================================================"
echo "✨ Application is running!"
echo "================================================"
echo "Backend API: http://localhost:8001"
echo "Frontend: http://localhost:5173"
echo "API Docs: http://localhost:8001/docs"
echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for both processes
wait
