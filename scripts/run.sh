#!/bin/bash

# Code2Resume - Full Stack Startup Script
echo "🚀 Starting Code2Resume..."
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

PROJECT_ROOT=$(pwd)

# Check if backend virtual environment exists
if [ ! -d "env" ] && [ ! -d ".venv" ]; then
    echo "❌ Backend virtual environment not found!"
    echo "Please run: uv sync"
    exit 1
fi

# Check if React frontend dependencies are installed
if [ ! -d "frontend-react/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend-react
    npm install
    cd "$PROJECT_ROOT"
fi

echo ""
echo "✨ Starting services..."
echo ""

# Show ollama model info
if command -v ollama &> /dev/null; then
    if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        ACTIVE_MODEL=$(ollama ps 2>/dev/null | awk 'NR==2{print $1}')
        if [ -n "$ACTIVE_MODEL" ]; then
            echo "🦙 Ollama model in use: $ACTIVE_MODEL"
        else
            echo "🦙 Ollama model: ${DEFAULT_MODEL:-mistral:latest} (not yet loaded)"
        fi
    else
        echo "⚠️  Ollama is installed but not running (start it with: ollama serve)"
    fi
else
    echo "⚠️  Ollama not found in PATH"
fi
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [ -n "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
        echo "   ✓ Backend stopped"
    fi
    if [ -n "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
        echo "   ✓ Frontend stopped"
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup INT TERM EXIT

# Start backend
echo "📡 Starting FastAPI backend on http://localhost:8001..."
if [ -d "env" ]; then
    source env/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
fi

export PYTHONPATH="$PROJECT_ROOT/backend:$PYTHONPATH"

# Show Ollama model info
OLLAMA_HOST="${OLLAMA_HOST:-http://localhost:11434}"
echo "🤖 Ollama Configuration:"
echo "   Host: $OLLAMA_HOST"
DEFAULT_MODEL="${DEFAULT_MODEL:-mistral:latest}"
FALLBACK_MODEL="${FALLBACK_MODEL:-llama3.1:8b}"
echo "   Default Model: $DEFAULT_MODEL"
echo "   Fallback Model: $FALLBACK_MODEL"

# Check if Ollama is running
if curl -s "$OLLAMA_HOST/api/tags" > /dev/null 2>&1; then
    echo "   Status: Connected"
    AVAILABLE_MODELS=$(curl -s "$OLLAMA_HOST/api/tags" 2>/dev/null | python3 -c "import sys,json; [print(f'     - {m[\"name\"]}') for m in json.load(sys.stdin).get('models',[])]" 2>/dev/null)
    if [ -n "$AVAILABLE_MODELS" ]; then
        echo "   Available Models:"
        echo "$AVAILABLE_MODELS"
    fi
    # Check if default model exists
    if echo "$AVAILABLE_MODELS" | grep -q "$DEFAULT_MODEL"; then
        echo "   ✓ Default model found"
    else
        echo "   ⚠ Default model '$DEFAULT_MODEL' not found. Pull it with: ollama pull $DEFAULT_MODEL"
    fi
else
    echo "   Status: Not running (start Ollama first: ollama serve)"
fi
echo ""
python -m uvicorn backend.app.main:app --reload --host 0.0.0.0 --port 8001 > backend.log 2>&1 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Check if backend started successfully
if ! kill -0 $BACKEND_PID 2>/dev/null; then
    echo "❌ Backend failed to start. Check backend.log for details."
    exit 1
fi

echo "   ✓ Backend started (PID: $BACKEND_PID)"

# Start React frontend
echo "⚛️  Starting React frontend on http://localhost:5173..."
cd frontend-react
npm run dev > ../frontend.log 2>&1 &
FRONTEND_PID=$!
cd "$PROJECT_ROOT"

# Wait for frontend to start
sleep 3

echo "   ✓ Frontend started (PID: $FRONTEND_PID)"

echo ""
echo "─────────────────────────────────────────────────────"
echo "✅ Code2Resume is running!"
echo ""
echo "   Backend:  http://localhost:8001"
echo "   Frontend: http://localhost:5173"
echo "   API Docs: http://localhost:8001/docs"
echo ""
echo "   🤖 Ollama Model: $DEFAULT_MODEL"
echo "   🔄 Fallback:     $FALLBACK_MODEL"
echo "─────────────────────────────────────────────────────"
echo ""
echo "Press CTRL+C to stop all services"
echo ""

# Wait for background processes
wait
