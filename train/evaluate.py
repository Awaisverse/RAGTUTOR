"""Evaluate retrieval and generation on the held-out split. Run before and after each fine-tune.

Retrieval (no generator needed):
  Recall@1, Recall@3, MRR for held-out questions and their paraphrases, searching only TRAIN chunks.
  Compares the base embedding model with the fine-tuned one (--embed-model).

Generation (needs the generator; skip with --no-generation):
  For each held-out question: retrieve TRAIN neighbours, generate, parse JSON, run every sympy check.
  Reports JSON validity, verified-step rate and the fraction of fully verified solutions.

Usage:
  python train/evaluate.py --embed-model BAAI/bge-small-en-v1.5 --no-generation
  python train/evaluate.py --embed-model train/out/embed-ft --gen-adapter train/out/gen-lora
"""
import argparse
import json
import os
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "train"))

import rag  # noqa: E402
from build_dataset import verify  # noqa: E402
from make_dataset import load_items, variants  # noqa: E402
from prompts import SOLVE_RULES  # noqa: E402


def retrieval_eval(all_items, ev):
    """The knowledge base is the WHOLE book (as in production). What is held out is the embedding
    model's training: eval items' paraphrases were never used to fine-tune it. A query for an eval
    item succeeds if the item itself is retrieved."""
    chunks = [c for it in all_items for c in rag.chunk_item(it)]
    index = rag.Index(chunks, use_embeddings=True)
    hit1 = hit3 = rr = n = 0
    for it in ev:
        for q in variants(it):
            ids = []
            for h in index.search(q, k=20):
                if h["id"] not in ids:  # several parts per item: keep the first rank per item
                    ids.append(h["id"])
            n += 1
            if it["id"] in ids:
                r = ids.index(it["id"]) + 1
                rr += 1 / r
                hit1 += r == 1
                hit3 += r <= 3
    return {"queries": n, "recall@1": round(hit1 / n, 3), "recall@3": round(hit3 / n, 3),
            "mrr": round(rr / n, 3)}


def generation_eval(train, ev, args):
    import local_models  # imported here: needs torch and the generator
    if args.gen_adapter:
        os.environ["GEN_ADAPTER"] = args.gen_adapter
        local_models.GEN_ADAPTER = args.gen_adapter
    chunks = [c for it in train for c in rag.chunk_item(it)]
    index = rag.Index(chunks, use_embeddings=False)
    by_id = {it["id"]: it for it in train}
    valid = verified_steps = total_steps = fully = 0
    for it in ev:
        hits = index.search(it["question"], k=args.neighbours)
        ex = "\n\n".join(f"EXAMPLE {i+1} ({h['id']}):\n" + json.dumps(
            {"question": by_id[h["id"]]["question"], "parts": by_id[h["id"]]["parts"]}, ensure_ascii=False)
            for i, h in enumerate(hits) if h["id"] in by_id)
        raw = local_models.generate([
            {"role": "system", "content": SOLVE_RULES + "\n\n" + ex},
            {"role": "user", "content": it["question"]},
        ], max_new_tokens=3000)
        m = re.search(r"\{.*\}", raw, re.S)
        try:
            sol = json.loads(m.group(0))
        except Exception:
            print("  invalid JSON for", it["id"])
            continue
        valid += 1
        bad = 0
        for p in sol.get("parts", []):
            for st in p.get("steps", []):
                for chk in st.get("check", []):
                    total_steps += 1
                    try:
                        ok = verify(chk)
                    except Exception:
                        ok = False
                    if ok:
                        verified_steps += 1
                    else:
                        bad += 1
        fully += (bad == 0)
    n = len(ev)
    return {"items": n, "json_valid": valid / n, "verified_step_rate": verified_steps / max(1, total_steps),
            "fully_verified": fully / n}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--embed-model", default="BAAI/bge-small-en-v1.5")
    ap.add_argument("--gen-adapter", default="")
    ap.add_argument("--neighbours", type=int, default=3)
    ap.add_argument("--no-generation", action="store_true")
    ap.add_argument("--report", default=str(ROOT / "train" / "out" / "eval_report.json"))
    args = ap.parse_args()

    os.environ["EMB_MODEL"] = args.embed_model
    rag.EMB_MODEL = args.embed_model
    split = json.loads((pathlib.Path(args.data) / "split.json").read_text(encoding="utf-8"))
    items = {it["id"]: it for it in load_items()}
    train = [items[i] for i in split["train"]]
    ev = [items[i] for i in split["eval"]]

    report = {"embed_model": args.embed_model, "gen_adapter": args.gen_adapter,
              "train_items": len(train), "eval_items": len(ev)}
    report["retrieval"] = retrieval_eval(list(items.values()), ev)
    if not args.no_generation:
        report["generation"] = generation_eval(train, ev, args)
    pathlib.Path(args.report).parent.mkdir(parents=True, exist_ok=True)
    pathlib.Path(args.report).write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps(report, indent=1))


if __name__ == "__main__":
    main()
