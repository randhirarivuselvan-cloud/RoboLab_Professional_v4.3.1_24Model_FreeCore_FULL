from __future__ import annotations
import argparse, json, os
from pathlib import Path

def load_jsonl(path):
    rows=[]
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line=line.strip()
            if line:
                rows.append(json.loads(line))
    return rows

def train_role(role: str):
    cfg_path = Path("training/configs") / f"{role}.json"
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    base = os.getenv("ROBO_BASE_MODEL")
    if not base:
        raise RuntimeError("ROBO_BASE_MODEL is required. Set it to a supported pretrained causal/instruction model.")
    # Imports are delayed so the codebase can be inspected/compiled without ML packages installed.
    from datasets import Dataset
    from transformers import AutoTokenizer, AutoModelForCausalLM, TrainingArguments, Trainer
    from peft import LoraConfig, get_peft_model, TaskType

    rows = load_jsonl(cfg["dataset"])
    texts = []
    for row in rows:
        parts = row.get("messages", [])
        texts.append("\n".join(f'{m["role"]}: {m["content"]}' for m in parts))

    tokenizer = AutoTokenizer.from_pretrained(base, use_fast=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(base, device_map="auto")
    lora = LoraConfig(
        r=cfg["lora"]["r"], lora_alpha=cfg["lora"]["alpha"],
        lora_dropout=cfg["lora"]["dropout"],
        target_modules=cfg["lora"]["target_modules"],
        task_type=TaskType.CAUSAL_LM
    )
    model = get_peft_model(model, lora)

    ds = Dataset.from_dict({"text": texts})
    def tok(batch):
        return tokenizer(batch["text"], truncation=True, max_length=cfg["training"]["max_seq_length"])
    ds = ds.map(tok, batched=True, remove_columns=["text"])

    args = TrainingArguments(
        output_dir=cfg["output_dir"],
        num_train_epochs=cfg["training"]["epochs"],
        learning_rate=cfg["training"]["learning_rate"],
        per_device_train_batch_size=cfg["training"]["per_device_train_batch_size"],
        gradient_accumulation_steps=cfg["training"]["gradient_accumulation_steps"],
        logging_steps=1,
        save_strategy="epoch",
        report_to="none",
    )
    trainer = Trainer(model=model, args=args, train_dataset=ds)
    trainer.train()
    model.save_pretrained(cfg["output_dir"])
    tokenizer.save_pretrained(cfg["output_dir"])
    print(f"TRAINED: {role}")

if __name__ == "__main__":
    ap=argparse.ArgumentParser()
    ap.add_argument("role")
    args=ap.parse_args()
    train_role(args.role)
