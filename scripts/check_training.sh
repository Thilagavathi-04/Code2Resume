#!/bin/bash

echo "📊 Fine-tuning Progress Monitor"
echo "================================"
echo ""

LOG_FILE="finetune_run.log"

if [ ! -f "$LOG_FILE" ]; then
    echo "❌ Log file not found: $LOG_FILE"
    echo "Make sure fine-tuning is running"
    exit 1
fi

echo "Recent output:"
echo "---"
tail -30 "$LOG_FILE"
echo "---"
echo ""

# Extract training steps if available
STEPS=$(grep -o "Step [0-9]*/60" "$LOG_FILE" | tail -1)
if [ -n "$STEPS" ]; then
    echo "Current: $STEPS"
fi

# Check for completion
if grep -q "Fine-tuning complete" "$LOG_FILE"; then
    echo "✅ Training completed!"
elif grep -q "Error\|Traceback\|Failed" "$LOG_FILE"; then
    echo "⚠️  Errors detected - check log file"
else
    echo "🏋️  Training in progress..."
fi

echo ""
echo "To see live output: tail -f $LOG_FILE"
