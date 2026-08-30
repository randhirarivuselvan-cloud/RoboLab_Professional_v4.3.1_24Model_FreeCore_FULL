from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line:
            rows.append(json.loads(line))
    if not rows:
        raise ValueError("Training dataset is empty")
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description="Fine-tune a code-capable base model for RoboLab with LoRA/QLoRA.")
    parser.add_argument("--base-model", required=True)
    parser.add_argument("--data", default="training/data/robolab_train.jsonl")
    parser.add_argument("--output", default="artifacts/robolab-adapter")
    parser.add_argument("--epochs", type=int, default=2)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--grad-accum", type=int, default=16)
    parser.add_argument("--lr", type=float, default=2e-4)
    parser.add_argument("--max-length", type=int, default=4096)
    args = parser.parse_args()

    try:
        from datasets import Dataset
        from peft import LoraConfig, get_peft_model
        from transformers import AutoModelForCausalLM, AutoTokenizer, Trainer, TrainingArguments
    except ImportError as exc:
        raise SystemExit(
            "Install training dependencies from requirements-model-training.txt before running this script."
        ) from exc

    rows = read_jsonl(Path(args.data))
    tokenizer = AutoTokenizer.from_pretrained(args.base_model, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    def render(row: dict) -> str:
        system = row.get("system", "You are RoboLab, a careful robotics coding assistant.")
        instruction = row["instruction"]
        response = row["response"]
        return f"<|system|>\n{system}\n<|user|>\n{instruction}\n<|assistant|>\n{response}"

    dataset = Dataset.from_list(rows)

    def tokenize(batch):
        return tokenizer(batch["text"], truncation=True, max_length=args.max_length)

    dataset = dataset.map(lambda x: {"text": render(x)})
    tokenized = dataset.map(tokenize, batched=True, remove_columns=dataset.column_names)

    model = AutoModelForCausalLM.from_pretrained(args.base_model, device_map="auto", torch_dtype="auto")
    lora = LoraConfig(
        r=32,
        lora_alpha=64,
        lora_dropout=0.05,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        task_type="CAUSAL_LM",
    )
    model = get_peft_model(model, lora)
    model.print_trainable_parameters()

    training_args = TrainingArguments(
        output_dir=args.output,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=args.batch_size,
        gradient_accumulation_steps=args.grad_accum,
        learning_rate=args.lr,
        logging_steps=10,
        save_strategy="epoch",
        bf16=True,
        report_to=[],
    )
    trainer = Trainer(model=model, args=training_args, train_dataset=tokenized)
    trainer.train()
    model.save_pretrained(args.output)
    tokenizer.save_pretrained(args.output)
    print(f"Saved RoboLab LoRA adapter to {args.output}")


if __name__ == "__main__":
    main()
