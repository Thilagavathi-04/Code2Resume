#!/bin/bash

echo "🔧 Installing fine-tuning dependencies..."
echo "This may take 10-15 minutes depending on your internet speed."
echo ""

# Activate virtual environment
source env/bin/activate

# Install unsloth and dependencies
echo "📦 Installing unsloth..."
pip install "unsloth[colab-new] @ git+https://github.com/unslothai/unsloth.git"

echo "📦 Installing TRL and datasets..."
pip install trl datasets

echo "📦 Installing PEFT and accelerate..."
pip install peft accelerate

echo "📦 Installing bitsandbytes for 4-bit quantization..."
pip install bitsandbytes

echo ""
echo "✅ Installation complete!"
echo ""
echo "To start fine-tuning, run:"
echo "  ./run_finetune.sh"
