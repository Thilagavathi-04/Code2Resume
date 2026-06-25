# Fine-Tuning Guide for Code2Resume

This guide walks you through fine-tuning Qwen2.5-Coder-3B model on your GitHub project data.

## 📋 Prerequisites

- NVIDIA GPU with CUDA support (RTX 2050 or better)
- At least 4GB VRAM
- Training data (generated from GitHub analysis)
- Python environment activated

## 🚀 Quick Start

### Step 1: Install Dependencies

```bash
chmod +x install_finetune_deps.sh
./install_finetune_deps.sh
```

This will install:
- `unsloth` - Fast LLM training framework
- `trl` - Transformer Reinforcement Learning
- `datasets` - Hugging Face datasets
- `peft` - Parameter-Efficient Fine-Tuning
- `accelerate` - Distributed training
- `bitsandbytes` - 4-bit quantization

⏱️ **Time:** ~10-15 minutes

### Step 2: Prepare Training Data

Training data should already be generated from analyzing GitHub profiles. Check:

```bash
ls Git_details/*/fine_tune_data.jsonl
```

You should see files like:
- `Git_details/username/fine_tune_data.jsonl`

Each file contains training examples in Alpaca format:
```json
{
  "instruction": "What is the project X about?",
  "input": "",
  "output": "Project description..."
}
```

### Step 3: Run Fine-Tuning

```bash
chmod +x run_finetune.sh
./run_finetune.sh
```

⏱️ **Time:** ~20-30 minutes (60 training steps)

**What happens:**
1. Loads Qwen2.5-Coder-3B-Instruct base model (4-bit quantized)
2. Adds LoRA adapters (16-rank)
3. Trains on your GitHub project data
4. Saves fine-tuned LoRA weights to `./lora_model`

**Training Configuration:**
- Batch size: 1 (with 8x gradient accumulation)
- Learning rate: 2e-4
- Max steps: 60
- Optimizer: AdamW 8-bit
- Sequence length: 2048 tokens

### Step 4: Merge LoRA Weights

After training completes:

```bash
python merge_lora.py
```

This merges the LoRA adapters into the base model and saves to `./merged_model`.

⏱️ **Time:** ~5 minutes

## 🔄 Converting to Ollama (Optional)

To use the fine-tuned model with Ollama, you need to convert it to GGUF format:

### Option 1: Use llama.cpp

```bash
# Clone llama.cpp
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
make

# Convert to GGUF
python convert.py ../merged_model --outfile ../model.gguf --outtype f16

# Quantize (optional, for smaller size)
./quantize ../model.gguf ../model-q4.gguf q4_k_m
```

### Option 2: Use Ollama directly

If your model is already in GGUF format:

```bash
# Create model in Ollama
ollama create resume-coder -f Modelfile

# Test it
ollama run resume-coder "What projects do I have?"
```

## 📊 Monitoring Training

During training, you'll see output like:

```
Step 1/60: Loss = 2.45
Step 10/60: Loss = 1.89
Step 20/60: Loss = 1.45
...
```

**Good signs:**
- ✅ Loss decreasing steadily
- ✅ No CUDA out of memory errors
- ✅ Training completes all 60 steps

**Warning signs:**
- ⚠️ Loss not decreasing (may need more data)
- ⚠️ NaN losses (reduce learning rate)
- ⚠️ OOM errors (reduce batch size further)

## 🎯 Adjusting Hyperparameters

Edit `fine_tune.py` to adjust:

```python
# Increase training duration
max_steps = 100  # Default: 60

# Adjust learning rate
learning_rate = 1e-4  # Default: 2e-4

# Increase LoRA rank (better quality, more VRAM)
r = 32  # Default: 16

# Change batch size (if you have more VRAM)
per_device_train_batch_size = 2  # Default: 1
```

## 🐛 Troubleshooting

### CUDA Out of Memory
```
RuntimeError: CUDA out of memory
```
**Solution:** Close other applications, reduce batch size, or reduce sequence length.

### Model Not Found
```
ModelNotFoundError: unsloth/Qwen2.5-Coder-3B-Instruct-bnb-4bit
```
**Solution:** Check internet connection. Model will auto-download (~2GB).

### No Training Data
```
❌ No training data found!
```
**Solution:** Run GitHub analysis first through the web app to generate training data.

### Import Error: unsloth
```
ModuleNotFoundError: No module named 'unsloth'
```
**Solution:** Run `./install_finetune_deps.sh` first.

## 📈 Expected Results

After fine-tuning, your model should:
- ✅ Better understand your specific projects
- ✅ Generate more accurate resume descriptions
- ✅ Use correct technical terminology
- ✅ Match your coding style and domain

## 🔍 Testing the Model

Create a test script:

```python
from unsloth import FastLanguageModel

model, tokenizer = FastLanguageModel.from_pretrained(
    "lora_model",
    max_seq_length=2048,
    load_in_4bit=True
)

model = FastLanguageModel.for_inference(model)

# Test prompt
prompt = """Below is an instruction that describes a task.

### Instruction:
Write a resume bullet point for my web scraping project.

### Response:
"""

inputs = tokenizer([prompt], return_tensors="pt").to("cuda")
outputs = model.generate(**inputs, max_new_tokens=128)
print(tokenizer.decode(outputs[0]))
```

## 📚 Additional Resources

- [Unsloth Documentation](https://github.com/unslothai/unsloth)
- [LoRA Paper](https://arxiv.org/abs/2106.09685)
- [Qwen2.5 Technical Report](https://github.com/QwenLM/Qwen2.5)
- [TRL Documentation](https://huggingface.co/docs/trl)

## 💡 Tips

1. **More data = better results**: Analyze more GitHub profiles to increase training samples
2. **Domain-specific**: Fine-tune separately for ML, Web Dev, etc. if you have focused projects
3. **Iterate**: Try different hyperparameters if results aren't satisfactory
4. **Evaluate**: Test on held-out projects before deploying

## 🎓 Understanding the Process

**What is Fine-Tuning?**
Taking a pre-trained model (Qwen2.5-Coder) and adapting it to your specific use case (resume generation from your projects).

**What is LoRA?**
Low-Rank Adaptation - trains small adapter weights instead of the entire model, saving memory and time.

**Why 4-bit Quantization?**
Reduces memory usage from 12GB to ~3GB, making it possible to train on consumer GPUs.

**Training Pipeline:**
```
Base Model → Add LoRA → Train on your data → Merge → Deploy
```
