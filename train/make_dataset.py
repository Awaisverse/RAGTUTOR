"""Build training data from the verified book, following RAG principles.

Outputs (in --out, default train/out/data):
  embed_pairs.jsonl   (anchor, positive) question paraphrases, same item = positive
  gen_sft.jsonl       chat examples: system = solver rules + RETRIEVED neighbours (never the item itself),
                      user = a question variant, assistant = the verified solution JSON
  split.json          which items are train / eval (split by unit, so eval units are never seen)

Why these choices:
  * Neighbours come from the TRAIN split only and exclude the item itself (leave-one-out), so the
    generator learns to use retrieved context the same way it will at answer time.
  * Question variants stand in for real student phrasings until paraphrases are written.
  * Splitting by unit prevents paraphrases of the same item from leaking across train and eval.

Usage:  python train/make_dataset.py --eval-units 2
"""
import argparse
import json
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from prompts import SOLVE_RULES  # noqa: E402
import rag  # noqa: E402

random.seed(0)


def load_items():
    items = []
    for path in sorted((ROOT / "data" / "book").glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            items.append(it)
    return items


def variants(item):
    """Question phrasings a student might type. Used as anchors and as user turns."""
    out = {item["question"].strip()}
    out.add(rag.normalize(item["question"]))
    for p in item["parts"]:
        if p.get("prompt"):
            out.add(p["prompt"].strip())
    # strip the leading words "Find", "Express", "Simplify" etc. to give a short query form
    out.add(re.sub(r"^(find|express|simplify|verify|identify|convert|represent|rationalize)\s+", "",
                   item["question"].strip(), flags=re.I))
    return [v for v in out if len(v) >= 8]


def solution_json(item):
    """The exact shape the generator must output (matches prompts.SOLVE_RULES)."""
    return json.dumps({
        "id": "gen-" + item["id"],
        "kind": "generated",
        "number": item.get("number", ""),
        "page": item.get("page", 0),
        "question": item["question"],
        "parts": [{"label": p.get("label", ""), "prompt": p.get("prompt", ""),
                   "figure": p.get("figure"), "steps": p["steps"], "answer": p["answer"]}
                  for p in item["parts"]],
    }, ensure_ascii=False)


def split(items, eval_units):
    if eval_units:
        units = sorted({it["unit"] for it in items})
        held = set(units[-eval_units:])
        train = [it for it in items if it["unit"] not in held]
        ev = [it for it in items if it["unit"] in held]
    else:  # not enough units: hold out every 5th item
        ev = [it for i, it in enumerate(items) if i % 5 == 4]
        train = [it for i, it in enumerate(items) if i % 5 != 4]
    return train, ev


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--eval-units", type=int, default=0, help="hold out the last N units for evaluation")
    ap.add_argument("--neighbours", type=int, default=3)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    items = load_items()
    train, ev = split(items, args.eval_units)
    if not train:
        sys.exit("no training items after split")

    # Index built from TRAIN chunks only, with TF-IDF so this step needs no model download.
    train_chunks = [c for it in train for c in rag.chunk_item(it)]
    index = rag.Index(train_chunks, use_embeddings=False)

    pairs, sft = [], []
    for it in train:
        vs = variants(it)
        for a in vs:
            for b in vs:
                if a != b:
                    pairs.append({"anchor": a, "positive": b, "id": it["id"]})

        # neighbours: retrieve by the item's own question, leave the item itself out
        hits = index.search(it["question"], k=args.neighbours + 1)
        neigh = [h for h in hits if h["id"] != it["id"]][: args.neighbours]
        neigh_items = {x["id"]: x for x in train}
        examples = "\n\n".join(
            f"EXAMPLE {i+1} ({h['id']}):\n" + json.dumps(
                {"question": neigh_items[h["id"]]["question"], "parts": neigh_items[h["id"]]["parts"]},
                ensure_ascii=False)
            for i, h in enumerate(neigh))
        for v in vs:
            sft.append({"messages": [
                {"role": "system", "content": SOLVE_RULES + "\n\n" + examples},
                {"role": "user", "content": v},
                {"role": "assistant", "content": solution_json(it)},
            ], "id": it["id"]})

    with open(out / "embed_pairs.jsonl", "w", encoding="utf-8") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    with open(out / "gen_sft.jsonl", "w", encoding="utf-8") as f:
        for s in sft:
            f.write(json.dumps(s, ensure_ascii=False) + "\n")
    (out / "split.json").write_text(json.dumps({
        "train": [it["id"] for it in train], "eval": [it["id"] for it in ev],
        "eval_units": args.eval_units, "neighbours": args.neighbours,
    }, indent=1), encoding="utf-8")
    print(f"items: train {len(train)}, eval {len(ev)} | embed pairs {len(pairs)} | sft examples {len(sft)}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
