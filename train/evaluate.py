"""Evaluate retrieval and generation. Run it before training (baseline) and after (tuned).

Retrieval (--no-retrieval to skip)
  The knowledge base is the whole real book, as in production. Queries are paraphrases of the
  held-out real items, which the embedding model never saw in training.
  Metrics: Recall@1, Recall@3, MRR.

Generation (--no-generation to skip)
  Two test sets, both unseen during training:
    real   held-out real book items (the honest test: genuine questions from the textbook)
    synth  synthetic questions with new numbers
  Every test question is ONE part (a multi-part question is split, as the tutor does). The retrieved
  neighbours go into the prompt, exactly as in training and in production. A reply that fails its own
  checks is retried (--attempts, first greedy then sampled). Metrics per set:
    json_valid          the reply parses as the solution JSON
    verified_step_rate  share of the model's own sympy checks that are true
    fully_verified      JSON valid, has at least one check, and every check is true
    answer_match        final answer equals the known answer after normalising the text
                        (a strict string comparison: it can undercount correct answers written
                        in a different but equivalent form)

Usage:
  python train/evaluate.py --tag base                                   # base model, no adapter
  python train/evaluate.py --tag tuned --gen-adapter train/out/gen-lora --embed-model train/out/embed-ft
"""
import argparse
import json
import os
import pathlib
import re
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "train"))

import rag  # noqa: E402
from build_dataset import verify  # noqa: E402
from make_dataset import load_items, neighbours_text, variants  # noqa: E402
import modelsolve  # noqa: E402
from answer_match import answer_ok, norm_ans  # noqa: E402
from solution_io import parse_solution  # noqa: E402


def pick(items, limit):
    if not limit or limit >= len(items):
        return items
    step = len(items) / limit
    return [items[int(i * step)] for i in range(limit)]


def retrieval_eval(real_items, ev):
    """Knowledge base = whole real book. A query succeeds when its own item is retrieved."""
    index = rag.Index([c for it in real_items for c in rag.chunk_item(it)], use_embeddings=True)
    hit1 = hit3 = rr = n = 0
    for it in ev:
        for q in variants(it):
            ids = []
            for h in index.search(q, k=20):
                if h["id"] not in ids:
                    ids.append(h["id"])
            n += 1
            if it["id"] in ids:
                r = ids.index(it["id"]) + 1
                rr += 1 / r
                hit1 += r == 1
                hit3 += r <= 3
    return {"queries": n, "recall@1": round(hit1 / n, 3), "recall@3": round(hit3 / n, 3), "mrr": round(rr / n, 3)}


def score_solution(raw, gold):
    """-> dict of per-item results for one model reply."""
    res = {"json_valid": False, "repaired": False, "checks": 0, "checks_ok": 0, "fully_verified": False,
           "answer_match": False, "answer_exact": False, "model_answers": []}
    try:
        sol, res["repaired"] = parse_solution(raw)
        parts = sol["parts"]
        assert isinstance(parts, list) and parts
    except Exception:
        return res
    res["json_valid"] = True
    for p in parts:
        for st in p.get("steps", []):
            for chk in st.get("check", []):
                res["checks"] += 1
                try:
                    res["checks_ok"] += bool(verify(chk))
                except Exception:
                    pass
        res["model_answers"].append(p.get("answer", ""))
    gold_answers = [p["answer"] for p in gold["parts"]]
    # an item whose own solution has no computed steps (e.g. naming a number rational) has nothing to check
    gold_has_checks = any(st.get("check") for p in gold["parts"] for st in p["steps"])
    res["fully_verified"] = res["checks_ok"] == res["checks"] and (res["checks"] > 0 or not gold_has_checks)
    same_shape = len(res["model_answers"]) == len(gold_answers)
    res["answer_exact"] = same_shape and all(norm_ans(m) == norm_ans(g) for m, g in zip(res["model_answers"], gold_answers))
    res["answer_match"] = same_shape and all(answer_ok(m, g) for m, g in zip(res["model_answers"], gold_answers))
    return res


def generation_eval(name, items, pool, args, items_out):
    import local_models  # needs torch and the generator model
    pool_by_id = {it["id"]: it for it in pool}
    index = rag.Index([c for it in pool for c in rag.chunk_item(it)], use_embeddings=False)
    keys = ("json_valid", "repaired", "checks", "checks_ok", "fully_verified", "answer_match", "answer_exact")
    tot, first = {"n": len(items), **{k: 0 for k in keys}}, {k: 0 for k in keys}
    tries = 0
    for i, it in enumerate(items, 1):
        t0 = time.time()
        r_all = modelsolve.attempt(
            it["question"], neighbours_text(index, pool_by_id, it, args.neighbours, args.context_chars),
            attempts=args.attempts, max_new_tokens=args.max_new_tokens)
        r = score_solution(r_all["raw"], it)                 # the reply the tutor would show
        r1 = score_solution(r_all["raws"][0], it)            # the first (greedy) reply alone
        tries += r_all["tries"]
        for k in keys:
            tot[k] += int(r[k])
            first[k] += int(r1[k])
        items_out.append({"set": name, "id": it["id"], "question": it["question"], **r, "tries": r_all["tries"],
                          "first_answer_match": r1["answer_match"], "first_fully_verified": bool(r1["fully_verified"]),
                          "gold_answers": [p["answer"] for p in it["parts"]], "raw_head": r_all["raw"][:300], "raw": r_all["raw"][:8000]})
        print(f"  [{name} {i}/{len(items)}] valid={r['json_valid']} checks={r['checks_ok']}/{r['checks']} "
              f"answer={r['answer_match']} tries={r_all['tries']} ({time.time() - t0:.0f}s)", flush=True)
    n = max(1, tot["n"])
    return {"items": tot["n"], "attempts": args.attempts, "avg_tries": round(tries / n, 2),
            "json_valid": round(tot["json_valid"] / n, 3), "repaired_replies": tot["repaired"],
            "verified_step_rate": round(tot["checks_ok"] / max(1, tot["checks"]), 3),
            "fully_verified": round(tot["fully_verified"] / n, 3), "answer_match": round(tot["answer_match"] / n, 3),
            "answer_exact": round(tot["answer_exact"] / n, 3),
            "first_try": {"json_valid": round(first["json_valid"] / n, 3), "fully_verified": round(first["fully_verified"] / n, 3),
                          "answer_match": round(first["answer_match"] / n, 3)}}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", default=str(ROOT / "train" / "out" / "data"))
    ap.add_argument("--tag", default="eval")
    ap.add_argument("--embed-model", default="BAAI/bge-small-en-v1.5")
    ap.add_argument("--gen-model", default="Qwen/Qwen2.5-Math-1.5B-Instruct",
                    help="base generator: a Hugging Face id (downloaded on first use) or a local folder")
    ap.add_argument("--gen-adapter", default="", help="LoRA folder; empty means the plain base model")
    ap.add_argument("--no-retrieval", action="store_true")
    ap.add_argument("--no-generation", action="store_true")
    ap.add_argument("--limit-real", type=int, default=0)
    ap.add_argument("--limit-synth", type=int, default=0)
    ap.add_argument("--neighbours", type=int, default=2)
    ap.add_argument("--max-new-tokens", type=int, default=2500)
    ap.add_argument("--context-chars", type=int, default=3500, help="size limit for the retrieved examples in a prompt")
    ap.add_argument("--attempts", type=int, default=3, help="tries per question: greedy, then sampled when a check fails")
    ap.add_argument("--report", default="")
    args = ap.parse_args()

    report_path = pathlib.Path(args.report or ROOT / "train" / "out" / f"eval_{args.tag}.json")
    rag.EMB_MODEL = args.embed_model
    data = pathlib.Path(args.data)
    split = json.loads((data / "split.json").read_text(encoding="utf-8"))
    real = {it["id"]: it for it in load_items()}
    real_eval_whole = [real[i] for i in split["eval"]]               # whole book items, for retrieval
    pool = json.loads((data / "pool.json").read_text(encoding="utf-8"))   # training items, one part each
    real_eval = json.loads((data / "real_eval.json").read_text(encoding="utf-8"))   # held-out items, one part each
    syn_eval = json.loads((data / "synth_eval.json").read_text(encoding="utf-8"))
    real_train = [it for it in pool if not it.get("synthetic")]

    report = {"tag": args.tag, "embed_model": args.embed_model, "gen_model": args.gen_model,
              "gen_adapter": args.gen_adapter or None,
              "real_train": len(real_train), "real_test": len(real_eval), "synth_test": len(syn_eval)}
    if not args.no_retrieval:
        report["retrieval"] = retrieval_eval(list(real.values()), real_eval_whole)
        print("retrieval:", report["retrieval"], flush=True)
    items_out = []
    if not args.no_generation:
        import local_models
        local_models.GEN_MODEL = args.gen_model
        local_models.GEN_ADAPTER = args.gen_adapter  # empty string = no adapter
        report["generation"] = {
            "real": generation_eval("real", pick(real_eval, args.limit_real), pool, args, items_out),
            "synth": generation_eval("synth", pick(syn_eval, args.limit_synth), pool, args, items_out),
        }
        print(json.dumps(report["generation"], indent=1), flush=True)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=1), encoding="utf-8")
    if items_out:
        with open(report_path.with_name(report_path.stem + "_items.jsonl"), "w", encoding="utf-8") as f:
            for r in items_out:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print("saved", report_path)


if __name__ == "__main__":
    main()
