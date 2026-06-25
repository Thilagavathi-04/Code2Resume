#!/bin/bash

# Code2Resume Startup Script with Database Check
echo "🚀 Starting Code2Resume..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Check if virtual environment exists
if [ ! -d "env" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Activate virtual environment
source env/bin/activate

# Check if database exists
if [ ! -f "users.db" ]; then
    echo "📦 Database not found. Initializing..."
    python scripts/init_db.py
    if [ $? -ne 0 ]; then
        echo "❌ Database initialization failed!"
        exit 1
    fi
else
    echo "✓ Database found"
fi

# Verify database schema
echo "🔍 Verifying database schema..."
python tests/test_db.py
if [ $? -ne 0 ]; then
    echo "⚠️  Database schema mismatch detected!"
    read -p "Reset database? (yes/no): " response
    if [ "$response" = "yes" ]; then
        echo "🔄 Resetting database..."
        python scripts/init_db.py
        python tests/test_db.py
    else
        echo "❌ Cannot continue with invalid schema"
        exit 1
    fi
fi

# Start the server
echo ""
echo "✨ Starting FastAPI server..."
echo "🌐 Server will be available at: http://localhost:8001"
echo "📝 Login page: http://localhost:8001/"
echo "📝 Register page: http://localhost:8001/register"
echo ""
echo "Press CTRL+C to stop the server"
echo "─────────────────────────────────────────────────────"

python -m uvicorn backend.app:app --reload --host 0.0.0.0 --port 8001
