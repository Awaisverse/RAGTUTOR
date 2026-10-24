"""Fine-tune the embedding model on paraphrase pairs (contrastive learning).

Base model: BAAI/bge-small-en-v1.5 (Hugging Face). Output: a sentence-transformers folder that
the server loads through the EMB_MODEL environment variable.

Loss: MultipleNegativesRankingLoss. Each batch pairs a question with its paraphrase; every other
question in the batch is a negative, so the model learns to pull paraphrases together and push
different questions apart.

Keep the new model only if eval Recall@3 improves (see train/evaluate.py). This script does not
decide that for you.

Usage:  python train/train_embeddings.py --data train/out/data --out train/out/embed-ft
"""
import argparse
import json
import pathlib
import random

from sentence_transformers import InputExample, SentenceTransformer, losses
from torch.utils.data import DataLoader

ROOT = pathlib.Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="BAAI/bge-small-en-v1.5")
    ap.add_argument("--data", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--out", default=str(ROOT / "train" / "out" / "embed-ft"))
    ap.add_argument("--epochs", type=int, default=3)
    ap.add_argument("--batch", type=int, default=32)
    ap.add_argument("--lr", type=float, default=2e-5)
    args = ap.parse_args()

    rows = [json.loads(l) for l in open(pathlib.Path(args.data) / "embed_pairs.jsonl", encoding="utf-8")]
    random.seed(0)
    random.shuffle(rows)
    examples = [InputExample(texts=[r["anchor"], r["positive"]]) for r in rows]
    print(f"pairs: {len(examples)}")

    model = SentenceTransformer(args.base)
    loader = DataLoader(examples, shuffle=True, batch_size=args.batch)
    loss = losses.MultipleNegativesRankingLoss(model)
    model.fit(
        train_objectives=[(loader, loss)],
        epochs=args.epochs,
        warmup_steps=max(1, int(0.1 * len(loader) * args.epochs)),
        optimizer_params={"lr": args.lr},
        show_progress_bar=True,
    )
    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    model.save(str(out))
    print("saved", out)


if __name__ == "__main__":
    main()
