"""Add the teacher's interpretation to every step of every stored solution, offline, with Vertex AI.

For each step the model writes "why" (en + ur): the rule or idea behind the step and what its result tells us - beyond the
short instruction already shown. For the part it writes "meaning": what the final answer means for the question. The math
lines are NOT changed, so every sympy check still stands. An explanation is kept only when:
  * it has exactly one entry per step, each with English and Urdu;
  * it brings in no number that is not already in the question, the working or the answer (no invented values);
  * the meaning of the answer is given in both languages.
Overlays: data/explain/class<K>/<item-id>__<label>.json, applied by tools/build_dataset.py only while the math lines are
exactly the ones explained.

  python tools/explain_steps.py --class 10 [--limit 20] [--workers 6] [--retry-rejected]
"""
import argparse
import json
import os
import pathlib
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))
from enrich_steps import _repair_latex  # noqa: E402

PROMPT = """You are an experienced, kind Pakistani mathematics teacher (Class {klass}, Punjab textbook). Below is a CORRECT,
computer-checked solution, step by step. Do not change or redo it. For EACH step, write a short interpretation that a
student would hear from a good teacher: WHY this step is done (the rule, definition or idea, named plainly) and WHAT its
result tells us / how it moves us toward the answer. Do not just repeat the step's instruction. 1-3 sentences each.
Then write the MEANING of the final answer: what it says about the question (and, where natural, how to check it).

Unit: {unit}
Question: {question}
Part: {part}
Steps (JSON, numbered): {steps}
Final answer: {answer}

Rules: use only numbers that appear in the question or the steps; inline maths in $...$ (LaTeX); Urdu in clear simple
Urdu script with maths in $...$.
Return ONLY JSON:
{{"why": [{{"en": "...", "ur": "..."}}, ... exactly {n} entries, one per step in order],
  "meaning": {{"en": "...", "ur": "..."}}}}"""

_lock = threading.Lock()
NUM = re.compile(r"\d+(?:\.\d+)?")


def overlay_path(klass, item_id, label):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", item_id)
    return ROOT / "data" / "explain" / f"class{klass}" / f"{safe}__{label or '_'}.json"


def _gemini(prompt):
    import vertex_models
    return vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=8000, temperature=0.0,
                                  model=os.environ.get("VERTEX_MODEL") or "gemini-4-argon")


def _numbers(text):
    t = re.sub(r"\\(?:frac|sqrt|left|right)", " ", text or "")
    return {n.rstrip("0").rstrip(".") if "." in n else n for n in NUM.findall(t)}


def validate(out, it, p):
    why, meaning = out.get("why"), out.get("meaning") or {}
    if not isinstance(why, list) or len(why) != len(p["steps"]):
        return None, f"needs {len(p['steps'])} entries, got {len(why) if isinstance(why, list) else 'none'}"
    allowed = _numbers(" ".join([it["question"], p.get("prompt", ""), p["answer"]] +
                                [s.get("math", "") + " " + s.get("en", "") + " " + " ".join(s.get("check", [])) for s in p["steps"]]))
    allowed |= {str(k) for k in range(0, 11)} | {"90", "180", "270", "360", "100"}   # ordinals, right angles, percent
    clean = []
    for k, w in enumerate(why, 1):
        en, ur = (_repair_latex(str((w or {}).get(x, ""))).strip() for x in ("en", "ur"))
        if not en or not ur:
            return None, f"step {k} lacks English or Urdu"
        extra = _numbers(en) - allowed
        if extra:
            return None, f"step {k} brings in numbers not in the working: {sorted(extra)[:5]}"
        clean.append({"en": en, "ur": ur})
    m_en, m_ur = (_repair_latex(str(meaning.get(x, ""))).strip() for x in ("en", "ur"))
    if not m_en or not m_ur:
        return None, "the meaning of the answer is missing"
    if _numbers(m_en) - allowed:
        return None, f"meaning brings in numbers not in the working: {sorted(_numbers(m_en) - allowed)[:5]}"
    return {"why": clean, "meaning": {"en": m_en, "ur": m_ur}}, None


def parts(klass):
    folder = ROOT / "data" / ("book" if klass == "9" else f"book{klass}")
    for f in sorted(folder.glob("unit*.json")):
        unit = json.loads(f.read_text(encoding="utf-8"))
        for it in unit["items"]:
            for p in it["parts"]:
                yield unit, it, p


def explain_one(klass, unit, it, p, generate):
    path = overlay_path(klass, it["id"], p.get("label", ""))
    rejected = path.with_suffix(".rejected.json")
    math = [s.get("math", "") for s in p["steps"]]
    if rejected.exists():
        return "skip"
    if path.exists():
        old = json.loads(path.read_text(encoding="utf-8"))
        if old.get("math") == math and old.get("answer_ref") == p["answer"]:
            return "skip"                             # explained already, for these very steps
    steps = [{"n": k, "math": s.get("math", ""), "instruction": s.get("en", "")} for k, s in enumerate(p["steps"], 1)]
    prompt = PROMPT.format(klass=klass, unit=f"{unit['unit']} - {unit['title']}", question=it["question"],
                           part=f"({p.get('label')}) {p.get('prompt', '')}" if p.get("label") else "(whole question)",
                           steps=json.dumps(steps, ensure_ascii=False), answer=p["answer"], n=len(steps))
    res, reason = None, ""
    for attempt in range(2):
        try:
            raw = generate(prompt if attempt == 0 else prompt + f"\n\nYour previous answer was rejected: {reason}. Fix it.")
            m = re.search(r"\{.*\}", raw or "", re.S)
            res, reason = validate(json.loads(m.group(0)) if m else {}, it, p)
        except Exception as exc:
            res, reason = None, f"error: {exc}"
        if res:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    if res:
        path.write_text(json.dumps({"item": it["id"], "label": p.get("label", ""), "answer_ref": p["answer"], "math": math, **res,
                                    "source": "gemini-4-argon via Vertex AI", "made": time.strftime("%Y-%m-%d")},
                                   ensure_ascii=False, indent=1), encoding="utf-8")
        return "kept"
    rejected.write_text(json.dumps({"item": it["id"], "label": p.get("label", ""), "reason": reason}, ensure_ascii=False), encoding="utf-8")
    return "rejected"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="klass", default="10")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--retry-rejected", action="store_true")
    a = ap.parse_args()
    env = ROOT / ".env.local"
    if env.exists() and not os.environ.get("TUTOR_NO_ENV_FILE"):
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip() and k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")
    todo = list(parts(a.klass))
    if a.retry_rejected:
        for f in (ROOT / "data" / "explain" / f"class{a.klass}").glob("*.rejected.json"):
            f.unlink()
    if a.limit:
        todo = todo[:a.limit]
    print(f"class {a.klass}: {len(todo)} parts", flush=True)
    counts = {"kept": 0, "rejected": 0, "skip": 0}
    t0 = time.time()

    def run(job):
        r = explain_one(a.klass, *job, generate=_gemini)
        with _lock:
            counts[r] += 1
            done = sum(counts.values())
            if done % 25 == 0 or done == len(todo):
                print(f"  {done}/{len(todo)}  kept {counts['kept']}  rejected {counts['rejected']}  skipped {counts['skip']}  "
                      f"({time.time() - t0:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(run, todo))
    print("done:", counts, flush=True)


if __name__ == "__main__":
    main()
