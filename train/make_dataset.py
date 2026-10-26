"""Build training and evaluation data, following RAG principles.

Data sources
  REAL       the hand-solved, sympy-verified book items (data/book/*.json).
  SYNTHETIC  new questions of the same types with computed, sympy-verified solutions (train/synth.py).

Protocol (prevents leakage and measures real generalisation)
  * Some REAL items are held out (the real test set). The model never trains on them, and they are
    different questions from anything synthetic, so the score on them shows how well the model
    handles genuine book questions it has not seen.
  * A separate SYNTHETIC test set uses numbers that never appear in the synthetic training set.
  * Training examples put RETRIEVED neighbours in the prompt (leave-one-out: never the item itself),
    so the generator learns to use retrieved context exactly as it will at answer time.

Outputs (in --out, default train/out/data)
  embed_pairs.jsonl   (anchor, positive) paraphrase pairs for the embedding model
  gen_sft.jsonl       chat examples: system = rules + neighbours, user = question, assistant = solution JSON
  synth_train.json    the synthetic training items (so evaluation can rebuild the same retrieval pool)
  synth_eval.json     the synthetic test items
  split.json          real train / real eval ids and the settings used

Usage:  python train/make_dataset.py --synth-per-type 25
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
sys.path.insert(0, str(ROOT / "train"))

from prompts import SOLVE_RULES  # noqa: E402
import rag  # noqa: E402
from synth import generate  # noqa: E402

random.seed(0)


def load_items():
    items = []
    for path in sorted((ROOT / "data" / "book").glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            it["unit_title"] = unit["title"]
            items.append(it)
    return items


def variants(item):
    """Question phrasings a student might type. Used as anchors and as user turns."""
    out = {item["question"].strip()}
    out.add(rag.normalize(item["question"]))
    for p in item["parts"]:
        if p.get("prompt"):
            out.add(p["prompt"].strip())
    out.add(re.sub(r"^(find|express|simplify|verify|identify|convert|represent|rationalize)\s+", "",
                   item["question"].strip(), flags=re.I))
    return [v for v in sorted(out) if len(v) >= 8]


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


def split_real(items, eval_units, eval_every):
    if eval_units:
        units = sorted({it["unit"] for it in items})
        held = set(units[-eval_units:])
        return [it for it in items if it["unit"] not in held], [it for it in items if it["unit"] in held]
    ev = [it for i, it in enumerate(items) if i % eval_every == eval_every - 1]
    tr = [it for i, it in enumerate(items) if i % eval_every != eval_every - 1]
    return tr, ev


def neighbours_text(index, pool_by_id, item, k):
    hits = index.search(item["question"], k=k * 3)
    seen, out = set(), []
    for h in hits:
        if h["id"] == item["id"] or h["id"] in seen or h["id"] not in pool_by_id:
            continue
        seen.add(h["id"])
        out.append(pool_by_id[h["id"]])
        if len(out) == k:
            break
    return "\n\n".join(
        f"EXAMPLE {i+1} ({e['id']}):\n" + json.dumps({"question": e["question"], "parts": e["parts"]}, ensure_ascii=False)
        for i, e in enumerate(out))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--eval-units", type=int, default=0, help="hold out the last N real units")
    ap.add_argument("--eval-every", type=int, default=2, help="else hold out every Nth real item")
    ap.add_argument("--synth-per-type", type=int, default=25)
    ap.add_argument("--synth-eval-per-type", type=int, default=2)
    ap.add_argument("--neighbours", type=int, default=2)
    args = ap.parse_args()

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    real = load_items()
    real_train, real_eval = split_real(real, args.eval_units, args.eval_every)
    syn_train = generate(args.synth_per_type, seed0=0)
    syn_eval = generate(args.synth_eval_per_type, seed0=100000, avoid={s["question"] for s in syn_train})
    if not real_train and not syn_train:
        sys.exit("no training items")

    pool = real_train + syn_train
    pool_by_id = {it["id"]: it for it in pool}
    index = rag.Index([c for it in pool for c in rag.chunk_item(it)], use_embeddings=False)

    pairs, sft = [], []
    for it in pool:
        vs = variants(it) if not it.get("synthetic") else [it["question"], rag.normalize(it["question"])]
        for a in vs:
            for b in vs:
                if a != b:
                    pairs.append({"anchor": a, "positive": b, "id": it["id"]})
        ex = neighbours_text(index, pool_by_id, it, args.neighbours)
        users = [it["question"]] if it.get("synthetic") else variants(it)
        for v in users:
            sft.append({"messages": [
                {"role": "system", "content": SOLVE_RULES + "\n\n" + ex},
                {"role": "user", "content": v},
                {"role": "assistant", "content": solution_json(it)},
            ], "id": it["id"], "synthetic": bool(it.get("synthetic"))})
    random.shuffle(sft)

    def dump_jsonl(name, rows):
        with open(out / name, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")

    dump_jsonl("embed_pairs.jsonl", pairs)
    dump_jsonl("gen_sft.jsonl", sft)
    (out / "synth_train.json").write_text(json.dumps(syn_train, ensure_ascii=False), encoding="utf-8")
    (out / "synth_eval.json").write_text(json.dumps(syn_eval, ensure_ascii=False), encoding="utf-8")
    (out / "split.json").write_text(json.dumps({
        "train": [it["id"] for it in real_train], "eval": [it["id"] for it in real_eval],
        "synth_train": len(syn_train), "synth_eval": len(syn_eval),
        "neighbours": args.neighbours,
    }, indent=1), encoding="utf-8")

    print(f"real:  train {len(real_train)}  test {len(real_eval)}")
    print(f"synth: train {len(syn_train)}  test {len(syn_eval)}")
    print(f"embedding pairs {len(pairs)} | generator examples {len(sft)}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
