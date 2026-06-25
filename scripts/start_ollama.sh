#!/bin/bash

# Script to start Ollama and ensure qwen2.5-coder:3b model is available

echo "🚀 Starting Ollama service..."

# Check if Ollama is installed
if ! command -v ollama &> /dev/null; then
    echo "❌ Ollama is not installed!"
    echo "Please install it from: https://ollama.ai"
    exit 1
fi

# Start Ollama in the background if not already running
if ! pgrep -f "ollama serve" > /dev/null; then
    echo "Starting Ollama server..."
    nohup ollama serve > /tmp/ollama.log 2>&1 &
    sleep 3
    echo "✅ Ollama server started"
else
    echo "✅ Ollama server is already running"
fi

# Check if model exists
echo "🔍 Checking for qwen2.5-coder:3b model..."
if ollama list | grep -q "qwen2.5-coder:3b"; then
    echo "✅ Model qwen2.5-coder:3b is already available"
else
    echo "📥 Model not found. Pulling qwen2.5-coder:3b..."
    echo "This may take a few minutes depending on your internet speed..."
    ollama pull qwen2.5-coder:3b
    
    if [ $? -eq 0 ]; then
        echo "✅ Model qwen2.5-coder:3b pulled successfully!"
    else
        echo "❌ Failed to pull model"
        exit 1
    fi
fi

echo ""
echo "🎉 Setup complete! Ollama is ready with qwen2.5-coder:3b"
echo "You can now start the FastAPI server"
