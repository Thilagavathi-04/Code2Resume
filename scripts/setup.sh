#!/bin/bash

# Code2Resume Setup Script
echo "🚀 Setting up Code2Resume with uv..."

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    echo "❌ uv is not installed. Please install it: https://github.com/astral-sh/uv"
    echo "   curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

echo "✅ uv detected"

# Configure uv to use 'env' directory
export UV_PROJECT_ENVIRONMENT=env

# Install Python dependencies
echo "📥 Installing Python dependencies..."
uv sync

echo "✅ Setup complete! Run ./run.sh to start the app."
cd backend
# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed. Please install Ollama first:"
    echo "   Visit: https://ollama.ai"
    echo "   Or run: curl -fsSL https://ollama.ai/install.sh | sh"
    exit 1
fi
echo "✅ Ollama detected"

# Check if Ollama service is running
if ! curl -s http://localhost:11434/api/version &> /dev/null; then
    echo "🔄 Starting Ollama service..."
    ollama serve &
    sleep 3
    
    if ! curl -s http://localhost:11434/api/version &> /dev/null; then
        echo "❌ Failed to start Ollama service"
        exit 1
    fi
fi
echo "✅ Ollama service is running"

# Pull required models
echo "🤖 Pulling required AI models..."
echo "   This may take some time depending on your internet connection..."

# Pull Llama3.1:8B (primary model now)
echo "📥 Pulling llama3.1:8b..."
ollama pull llama3.1:8b

# Create environment file
if [ ! -f .env ]; then
    echo "⚙️ Creating environment configuration..."
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "✅ Created .env file"
    else
        touch .env
        echo "✅ Created empty .env file"
    fi
else
    echo "✅ .env file already exists"
fi

echo ""
echo "🎉 Setup completed!"
echo ""
echo "To start Code2Resume:"
echo "Run: ./run.sh"
echo ""
