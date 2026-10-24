"""LoRA fine-tune the maths generator on verified solutions (Hugging Face transformers + peft).

Base: Qwen/Qwen2.5-Math-1.5B-Instruct. Only the assistant reply (the solution JSON) is trained;
the system rules, retrieved examples and question are masked out of the loss, so the model learns
"given retrieved examples and a question, write the verified solution", not to copy the prompt.

Precision: bf16 on GPUs that support it (A100, L4), fp16 otherwise (T4 on free Colab).

Usage:  python train/train_generator.py --data train/out/data --out train/out/gen-lora
"""
import argparse
import json
import pathlib
import random

import torch
from peft import LoraConfig, get_peft_model
from torch.utils.data import Dataset
from transformers import (AutoModelForCausalLM, AutoTokenizer, DataCollatorForSeq2Seq,
                          Trainer, TrainingArguments)

ROOT = pathlib.Path(__file__).resolve().parent.parent


class ChatSFT(Dataset):
    """Tokenises a chat example and masks every token except the final assistant reply."""

    def __init__(self, rows, tok, max_len):
        self.items = []
        for r in rows:
            msgs = r["messages"]
            prompt = tok.apply_chat_template(msgs[:-1], tokenize=False, add_generation_prompt=True)
            full = prompt + msgs[-1]["content"] + tok.eos_token
            p_ids = tok(prompt, add_special_tokens=False)["input_ids"]
            f_ids = tok(full, add_special_tokens=False)["input_ids"][:max_len]
            labels = [-100] * min(len(p_ids), len(f_ids)) + f_ids[len(p_ids):]
            self.items.append({"input_ids": f_ids, "attention_mask": [1] * len(f_ids), "labels": labels})

    def __len__(self):
        return len(self.items)

    def __getitem__(self, i):
        return self.items[i]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="Qwen/Qwen2.5-Math-1.5B-Instruct")
    ap.add_argument("--data", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--out", default=str(ROOT / "train" / "out" / "gen-lora"))
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--lr", type=float, default=1e-4)
    ap.add_argument("--max-len", type=int, default=2048)
    ap.add_argument("--rank", type=int, default=16)
    ap.add_argument("--max-steps", type=int, default=-1, help="for a quick smoke test")
    args = ap.parse_args()

    use_cuda = torch.cuda.is_available()
    bf16 = use_cuda and torch.cuda.is_bf16_supported()
    dtype = torch.bfloat16 if bf16 else (torch.float16 if use_cuda else torch.float32)

    tok = AutoTokenizer.from_pretrained(args.base)
    model = AutoModelForCausalLM.from_pretrained(args.base, dtype=dtype)
    model.gradient_checkpointing_enable()
    model.enable_input_require_grads()  # needed for LoRA + gradient checkpointing
    model = get_peft_model(model, LoraConfig(
        r=args.rank, lora_alpha=2 * args.rank, lora_dropout=0.05, task_type="CAUSAL_LM",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))
    if dtype == torch.float16:
        # fp16 mixed precision cannot unscale fp16 gradients: keep the small LoRA weights in fp32
        for prm in model.parameters():
            if prm.requires_grad:
                prm.data = prm.data.float()
    model.print_trainable_parameters()

    rows = [json.loads(l) for l in open(pathlib.Path(args.data) / "gen_sft.jsonl", encoding="utf-8")]
    random.seed(0)
    random.shuffle(rows)
    ds = ChatSFT(rows, tok, args.max_len)
    print(f"sft examples: {len(ds)}")

    accum = 8
    total_steps = max(1, -(-len(ds) // accum)) * args.epochs
    targs = TrainingArguments(
        output_dir=str(pathlib.Path(args.out) / "checkpoints"),
        num_train_epochs=args.epochs,
        max_steps=args.max_steps,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=accum,
        learning_rate=args.lr,
        lr_scheduler_type="cosine",
        warmup_steps=max(1, int(0.05 * total_steps)),
        logging_steps=5,
        save_strategy="no",
        bf16=bf16,
        fp16=(use_cuda and not bf16),
        gradient_checkpointing=True,
        report_to="none",
    )
    trainer = Trainer(model=model, args=targs, train_dataset=ds,
                      data_collator=DataCollatorForSeq2Seq(tok, padding=True, label_pad_token_id=-100))
    trainer.train()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(str(out))  # adapter only, a few MB
    tok.save_pretrained(str(out))
    print("saved adapter to", out)


if __name__ == "__main__":
    main()
