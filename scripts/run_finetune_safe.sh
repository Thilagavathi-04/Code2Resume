#!/bin/bash

echo "🧹 Preparing GPU for Fine-tuning"
echo "================================"
echo ""

# Check current GPU usage
echo "Current GPU Memory Usage:"
nvidia-smi --query-gpu=memory.used,memory.total --format=csv,noheader,nounits

USED=$(nvidia-smi --query-gpu=memory.used --format=csv,noheader,nounits)
TOTAL=$(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits)

echo "Used: ${USED}MB / ${TOTAL}MB"
echo ""

if [ "$USED" -gt 1000 ]; then
    echo "⚠️  High GPU memory usage detected!"
    echo ""
    echo "Recommendations to free up VRAM:"
    echo "  1. Close web browsers (especially Zen/Chrome/Firefox)"
    echo "  2. Close other GPU applications"
    echo "  3. Restart your display manager if needed"
    echo ""
    echo "Current GPU processes:"
    nvidia-smi --query-compute-apps=pid,name,used_memory --format=csv
    echo ""
    read -p "Try to continue anyway? (y/n) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Exiting. Free up GPU memory and try again."
        exit 1
    fi
fi

echo "🚀 Starting fine-tuning with memory optimizations..."
echo "  - Sequence length: 1024 (reduced from 2048)"
echo "  - LoRA rank: 8 (reduced from 16)"
echo "  - Batch size: 1"
echo ""

# Navigate to project root
cd "$(dirname "$0")/.."

# Set memory management env vars
export PYTORCH_CUDA_ALLOC_CONF=expandable_segments:True

# Activate environment and run
source env/bin/activate
cd fine-tuning/scripts && python fine_tune.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Fine-tuning completed successfully!"
else
    echo ""
    echo "❌ Fine-tuning failed. Check error messages above."
    echo ""
    echo "If you got OOM (Out of Memory) error:"
    echo "  - Close ALL browser windows"
    echo "  - Close other GPU applications"
    echo "  - Reduce max_steps in fine_tune.py (try 30 instead of 60)"
fi
