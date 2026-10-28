"""Build training and evaluation data, following RAG principles.

Data sources
  REAL       the hand-solved, sympy-verified book items (data/book/*.json).
  SYNTHETIC  new questions of the same types with computed, sympy-verified solutions (train/synth.py).
  ENGINE     new Exercise 1.2 style questions solved by the rule engine, final answer checked against sympy
             (train/engine_data.py). The model learns solutions that are right by construction.

One part per example: a multi-part question is split so the model answers (i), (ii), ... one at a time. Short replies
fit the token limit and a slip in one part cannot spoil the others.

Protocol (prevents leakage and measures real generalisation)
  * With --eval-prefix ex1.2- every Exercise 1.2 item is held out, so that exercise is the real test.
  * Some REAL items are held out (the real test set). The model never trains on them, and they are
    different questions from anything synthetic, so the score on them shows how well the model
    handles genuine book questions it has not seen.
  * A separate SYNTHETIC test set uses numbers that never appear in the synthetic training set.
  * Training examples put RETRIEVED neighbours in the prompt (leave-one-out: never the item itself),
    so the generator learns to use retrieved context exactly as it will at answer time.

Outputs (in --out, default train/out/data)
  embed_pairs.jsonl   (anchor, positive) paraphrase pairs for the embedding model
  gen_sft.jsonl       chat examples: system = rules + neighbours, user = question, assistant = solution JSON
  pool.json           every training item (one part each), so evaluation rebuilds the same retrieval pool
  real_eval.json      the held-out real items, one part each
  synth_train.json    the synthetic + engine training items (one part each)
  synth_eval.json     synthetic + engine test items with numbers never used in training
  split.json          real train / real eval ids (whole items) and the settings used

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

from prompts import SOLVE_RULES, solve_rules  # noqa: E402
import mathtext  # noqa: E402
import rag  # noqa: E402
from engine_data import engine_items  # noqa: E402
from modelsolve import examples_text, explode_all  # noqa: E402
from synth import generate  # noqa: E402

random.seed(0)


def load_items(klass="9"):
    """The real book of a class: Class 9 is data/book, Class 10 is data/book10."""
    items = []
    for path in sorted((ROOT / "data" / ("book" if str(klass) == "9" else f"book{klass}")).glob("unit*.json")):
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


def split_real(items, eval_units, eval_every, eval_prefix=""):
    if eval_prefix:
        return ([it for it in items if not it["id"].startswith(eval_prefix)],
                [it for it in items if it["id"].startswith(eval_prefix)])
    if eval_units:
        units = sorted({it["unit"] for it in items})
        held = set(units[-eval_units:])
        return [it for it in items if it["unit"] not in held], [it for it in items if it["unit"] in held]
    ev = [it for i, it in enumerate(items) if i % eval_every == eval_every - 1]
    tr = [it for i, it in enumerate(items) if i % eval_every != eval_every - 1]
    return tr, ev


def neighbours_text(index, pool_by_id, item, k, budget=3500):
    return examples_text(index, pool_by_id, item["question"], k, budget, exclude_id=item["id"])


def leak_free(synthetic, real):
    """Drop synthetic questions that repeat a real book question or one of its parts.
    The real items are the honest test, so nothing the model trains on may be a copy of them."""
    real_norm = [rag.normalize(r["question"]) for r in real]
    kept, dropped = [], 0
    for s in synthetic:
        q = rag.normalize(s["question"])
        part_prompts = [rag.normalize(p.get("prompt", "")) for p in s["parts"]]
        copy = q in real_norm or any(len(pp) >= 7 and pp in rn for pp in part_prompts for rn in real_norm)
        if copy:
            dropped += 1
        else:
            kept.append(s)
    if dropped:
        print(f"leak guard: dropped {dropped} synthetic items that duplicate real book questions")
    return kept


def not_in_test(items, real_eval):
    """Drop training items that ask a held-out question: same numbers, signs and instruction (mathtext.same_question)."""
    kept = [s for s in items if not any(mathtext.same_question(s["question"], ev)[0] for ev in real_eval)]
    if len(kept) != len(items):
        print(f"leak guard: dropped {len(items) - len(kept)} training items that ask a held-out question")
    return kept


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--eval-units", type=int, default=0, help="hold out the last N real units")
    ap.add_argument("--eval-every", type=int, default=2, help="else hold out every Nth real item")
    ap.add_argument("--synth-per-type", type=int, default=25)
    ap.add_argument("--synth-eval-per-type", type=int, default=2)
    ap.add_argument("--eval-prefix", default="", help="hold out every real item whose id starts with this, e.g. ex1.2-")
    ap.add_argument("--engine-per-type", type=int, default=20, help="engine-solved Exercise 1.2 style items per type")
    ap.add_argument("--engine-eval-per-type", type=int, default=2)
    ap.add_argument("--neighbours", type=int, default=2)
    ap.add_argument("--context-chars", type=int, default=3500, help="size limit for the retrieved examples in a prompt")
    ap.add_argument("--class", dest="klass", default="9", help="9 (default) or 10: which book to train on")
    args = ap.parse_args()
    rules = solve_rules(args.klass)

    out = pathlib.Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    real = load_items(args.klass)
    real_train_whole, real_eval_whole = split_real(real, args.eval_units, args.eval_every, args.eval_prefix)
    real_train, real_eval = explode_all(real_train_whole), explode_all(real_eval_whole)

    if str(args.klass) == "10":
        # Class 10: new numbers for every book question type, solved by the same checked templates (train/synth10.py)
        from synth10 import generate as generate10
        syn_train = leak_free(generate10(args.synth_per_type, seed0=0), real)
        syn_eval = leak_free(generate10(args.synth_eval_per_type, seed0=100000, avoid={s["question"] for s in syn_train}), real)
        eng_train, eng_eval = [], []
    else:
        syn_train = leak_free(generate(args.synth_per_type, seed0=0), real)
        syn_eval = leak_free(generate(args.synth_eval_per_type, seed0=100000,
                                      avoid={s["question"] for s in syn_train}), real)
        eng_train = engine_items(args.engine_per_type, seed0=0)
        eng_eval = engine_items(args.engine_eval_per_type, seed0=100000, avoid={e["question"] for e in eng_train})
    syn_train = explode_all(not_in_test(syn_train + eng_train, real_eval))
    syn_eval = explode_all(not_in_test(syn_eval + eng_eval, real_eval))
    if not real_train and not syn_train:
        sys.exit("no training items")

    pool = real_train + syn_train
    pool_by_id = {it["id"]: it for it in pool}
    index = rag.Index([c for it in pool for c in rag.chunk_item(it)], use_embeddings=False)

    pairs, sft = [], []
    for it in pool:
        vs = variants(it) if not it.get("synthetic") else [it["question"], rag.normalize(it["question"]), *(it.get("asked") or [])]
        for a in vs:
            for b in vs:
                if a != b:
                    pairs.append({"anchor": a, "positive": b, "id": it["id"]})
        ex = neighbours_text(index, pool_by_id, it, args.neighbours, args.context_chars)
        users = [it["question"]] + list(it.get("asked") or []) if it.get("synthetic") else variants(it)
        for v in users:
            sft.append({"messages": [
                {"role": "system", "content": rules + "\n\n" + ex},
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
    (out / "pool.json").write_text(json.dumps(pool, ensure_ascii=False), encoding="utf-8")
    (out / "real_eval.json").write_text(json.dumps(real_eval, ensure_ascii=False), encoding="utf-8")
    (out / "synth_train.json").write_text(json.dumps(syn_train, ensure_ascii=False), encoding="utf-8")
    (out / "synth_eval.json").write_text(json.dumps(syn_eval, ensure_ascii=False), encoding="utf-8")
    (out / "split.json").write_text(json.dumps({
        "train": [it["id"] for it in real_train_whole], "eval": [it["id"] for it in real_eval_whole],
        "synth_train": len(syn_train), "synth_eval": len(syn_eval),
        "neighbours": args.neighbours, "class": str(args.klass),
    }, indent=1), encoding="utf-8")

    print(f"real:  train {len(real_train)}  test {len(real_eval)} (one part each)")
    print(f"synth: train {len(syn_train)}  test {len(syn_eval)}")
    print(f"embedding pairs {len(pairs)} | generator examples {len(sft)}")
    print(f"written to {out}")


if __name__ == "__main__":
    main()
