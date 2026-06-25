import os
import torch
from unsloth import FastLanguageModel
from trl import SFTTrainer
from transformers import TrainingArguments
from datasets import load_dataset

def fine_tune_model(username: str):
    """
    Fine-tunes Llama 3.1 8B on the user's specific GitHub data.
    Optimized for RTX 2050 (4GB VRAM) using Unsloth & QLoRA.
    """
    
    # 1. Configuration
    model_name = "unsloth/Meta-Llama-3.1-8B-bnb-4bit" # Pre-quantized 4-bit model
    max_seq_length = 2048
    dtype = None # Auto detection
    load_in_4bit = True 

    # Data Path
    data_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "Git_details", username, "fine_tune_data.jsonl")
    
    if not os.path.exists(data_file):
        return {"status": "error", "message": "No training data found. Please analyze repos first."}

    print(f"🚀 Starting fine-tuning for user: {username}")
    print(f"📂 Loading data from: {data_file}")

    # 2. Load Model & Tokenizer
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name = model_name,
        max_seq_length = max_seq_length,
        dtype = dtype,
        load_in_4bit = load_in_4bit,
    )

    # 3. Add LoRA Adapters
    model = FastLanguageModel.get_peft_model(
        model,
        r = 16,
        target_modules = ["q_proj", "k_proj", "v_proj", "o_proj",
                          "gate_proj", "up_proj", "down_proj",],
        lora_alpha = 16,
        lora_dropout = 0,
        bias = "none",
        use_gradient_checkpointing = "unsloth", 
        random_state = 3407,
        use_rslora = False,
        loftq_config = None,
    )

    # 4. Load Dataset
    dataset = load_dataset("json", data_files=data_file, split="train")

    # 5. Formatting Function (Alpaca Style)
    alpaca_prompt = """Below is an instruction that describes a task, paired with an input that provides further context. Write a response that appropriately completes the request.

### Instruction:
{}

### Input:
{}

### Response:
{}"""

    def formatting_prompts_func(examples):
        instructions = examples["instruction"]
        inputs       = examples["input"]
        outputs      = examples["output"]
        texts = []
        for instruction, input, output in zip(instructions, inputs, outputs):
            text = alpaca_prompt.format(instruction, input, output) + tokenizer.eos_token
            texts.append(text)
        return { "text" : texts, }

    dataset = dataset.map(formatting_prompts_func, batched = True)

    # 6. Training Arguments (Optimized for 4GB VRAM)
    training_args = TrainingArguments(
        per_device_train_batch_size = 2,
        gradient_accumulation_steps = 4,
        warmup_steps = 5,
        max_steps = 60, # Short run for quick adaptation
        learning_rate = 2e-4,
        fp16 = not torch.cuda.is_bf16_supported(),
        bf16 = torch.cuda.is_bf16_supported(),
        logging_steps = 1,
        optim = "adamw_8bit",
        weight_decay = 0.01,
        lr_scheduler_type = "linear",
        seed = 3407,
        output_dir = f"fine_tuned_models/{username}",
    )

    # 7. Trainer
    trainer = SFTTrainer(
        model = model,
        tokenizer = tokenizer,
        train_dataset = dataset,
        dataset_text_field = "text",
        max_seq_length = max_seq_length,
        dataset_num_proc = 2,
        packing = False, 
        args = training_args,
    )

    # 8. Train
    trainer_stats = trainer.train()

    # 9. Save Model (LoRA Adapters only)
    output_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "fine_tuned_models", username)
    model.save_pretrained(output_path)
    tokenizer.save_pretrained(output_path)
    
    # 10. Convert to GGUF for Ollama (Optional/Advanced step usually done manually)
    # For now, we just save the adapters.
    
    return {"status": "success", "message": f"Model fine-tuned and saved to {output_path}"}

if __name__ == "__main__":
    # Test run
    fine_tune_model("test_user")
