#!/bin/bash

echo "🚀 Starting Qwen2.5-Coder-3B Fine-tuning"
echo "========================================"
echo ""
echo "⚠️  Important Notes:"
echo "  - This will use your GPU (RTX 2050)"
echo "  - Expected time: 15-30 minutes"
echo "  - Memory usage: ~3.5GB VRAM"
echo ""
read -p "Press Enter to continue or Ctrl+C to cancel..."

# Navigate to project root
cd "$(dirname "$0")/.."

# Activate environment
source env/bin/activate

# Check CUDA availability
python -c "import torch; print(f'CUDA Available: {torch.cuda.is_available()}'); print(f'Device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else \"CPU\"}')"

echo ""
echo "Starting fine-tuning..."
cd fine-tuning/scripts && python fine_tune.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Fine-tuning completed successfully!"
    echo ""
    echo "📁 Model saved to: ./data/lora_model"
    echo ""
    echo "Next steps to use with Ollama:"
    echo "  1. Merge LoRA weights: cd fine-tuning/scripts && python merge_lora.py"
    echo "  2. Convert to GGUF: (requires llama.cpp)"
    echo "  3. Import to Ollama: ollama create mymodel -f Modelfile"
else
    echo ""
    echo "❌ Fine-tuning failed. Check the error messages above."
    exit 1
fi
