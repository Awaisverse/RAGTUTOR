"""Deepen thin stored solutions into full teacher-style working, offline, and keep only what the computer can check.

Some stored solutions are correct but terse (one line from question to answer). For each such part, the high-end Gemini model
on Vertex AI (your service account) writes a detailed solution: what is given, the rule and why it applies, the substitution,
the computation, the conclusion - in English and Urdu. It is KEPT only when:
  * the final answer is the same as the stored, verified answer;
  * every step that computes something (an "=" with numbers) carries a sympy check, and every check is true;
  * every step has both English and Urdu;
  * the original part's own checks still pass (they are appended to the last step).
Parts with drawings are left alone (their figures belong to their steps).

Results are overlays: data/enrich/class<K>/<item-id>__<label>.json, applied by tools/build_dataset.py, which re-verifies
every check at build time. Overlays carry the answer they were made for; if the source answer changes, the overlay is ignored.

  python tools/enrich_steps.py --class 10 [--max-steps 1] [--limit 20] [--workers 4]
Resumable: parts that already have an overlay (or a recorded rejection) are skipped.
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

PROMPT = """You are an experienced Pakistani mathematics teacher (Class {klass}, Punjab textbook). Below is a CORRECT but very short
solution. Rewrite it as a full, detailed, step-by-step solution a student can follow, without changing the final answer.

Unit: {unit}
Question: {question}
Part: {part}
Short verified solution (JSON): {steps}
Final answer (must stay exactly the same): {answer}

Write 3 to 8 steps. Typical shape: what is given / what is asked; the rule or theorem and why it applies here; substituting the
values; each calculation on its own line; the conclusion that states the final answer.

Return ONLY one JSON object:
{{"steps": [{{"math": "<one LaTeX line, no $ signs, may be empty for a pure explanation>",
             "en": "<short English explanation, inline maths in $...$>",
             "ur": "<the same explanation in Urdu, inline maths in $...$>",
             "check": ["<sympy equality>", ...]}}, ...],
  "answer": "<the same final answer>"}}

Checks (very important): every step whose math line computes something (an "=" with numbers) needs at least one check: a
Python/sympy equality "lhs == rhs" that is TRUE. Use sqrt(), pi, I (imaginary unit), R(a,b) for fractions, ** for powers,
Abs(). Angles in degrees must be converted: sin(30*pi/180). No LaTeX, no units, no % signs, no words inside checks.
Do not introduce any number that does not follow from the question. Do not round unless the short solution rounds."""

_lock = threading.Lock()


def overlay_path(klass, item_id, label):
    safe = re.sub(r"[^A-Za-z0-9._-]+", "_", item_id)
    return ROOT / "data" / "enrich" / f"class{klass}" / f"{safe}__{label or '_'}.json"


def _gemini(prompt):
    import vertex_models
    return vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=6000, temperature=0.0,
                                  model=os.environ.get("VERTEX_MODEL") or "gemini-4-argon")


def _repair_latex(t):
    """A single backslash in the model's JSON turns frac into a form feed and times into a tab: put the LaTeX back."""
    b = chr(92)
    t = t.replace(chr(12), b + "f").replace(chr(9), b + "t").replace(chr(8), b + "b").replace(chr(11), b + "v").replace(chr(13), b + "r")
    return re.sub(r"\n(?=[A-Za-z])", lambda m: b + "n", t)


def _numeric_calculation(math):
    """A line that calculates with numbers (where arithmetic slips happen) - not a formula such as |z| = sqrt(a^2 + b^2),
    whose only digits are exponents or subscripts, and not a symbolic relation."""
    t = re.sub(r"[\^_]\s*(\{[^{}]*\}|\w)", " ", math)          # exponents and subscripts are not calculations
    t = re.sub(r"\\(?:frac|sqrt|times|div|cdot|left|right|circ|quad|qquad|,|;|text\{[^}]*\})", " ", t)
    t = re.sub(r"\\(?:sin|cos|tan|cot|sec|csc|log|ln|angle|pi|degree)\b", " ", t)   # functions and constants: still numeric
    words = re.sub(r"\\[A-Za-z]+", " x ", t)                 # any other command (alpha, theta, overline ...) is a symbol
    letters = re.sub(r"\bi\b", " ", re.sub(r"[^A-Za-z]+", " ", words))
    return bool(re.search(r"\d", t)) and not letters.strip()


def validate(out, part):
    """-> (steps, None) when the detailed solution can be trusted, else (None, reason)."""
    from answer_match import answer_ok
    from build_dataset import verify
    steps = out.get("steps")
    if not isinstance(steps, list) or not 3 <= len(steps) <= 8:
        return None, "needs 3 to 8 steps"
    if len(part["steps"]) >= 3 and len(steps) <= len(part["steps"]):
        return None, f"not more detailed than the {len(part['steps'])} steps already there: split the working into more steps"
    if not answer_ok(str(out.get("answer", "")), part["answer"]) and str(out.get("answer", "")).replace(" ", "") != part["answer"].replace(" ", ""):
        return None, f"answer changed: {str(out.get('answer'))[:60]!r} vs {part['answer'][:60]!r}"
    clean = []
    for k, s in enumerate(steps, 1):
        if not isinstance(s, dict):
            return None, f"step {k} is not an object"
        math, en, ur = (_repair_latex(str(s.get(k, ""))).strip() for k in ("math", "en", "ur"))
        checks = [str(c).strip() for c in (s.get("check") or []) if str(c).strip()]
        if not en or not ur:
            return None, f"step {k} lacks English or Urdu"
        if "=" in math and _numeric_calculation(math) and not checks:
            return None, f"step {k} computes something without a check: {math[:60]!r}"
        for c in checks:
            try:
                ok = verify(c)
            except Exception as exc:
                return None, f"step {k} check cannot be read: {c[:60]!r} ({exc})"
            if not ok:
                return None, f"step {k} check is false: {c[:80]!r}"
        step = {"math": math, "en": en, "ur": ur}
        if checks:
            step["check"] = checks
        clean.append(step)
    original = [c for s in part["steps"] for c in s.get("check", [])]
    if original:                                     # the stored solution's own checks still hold at the end
        clean[-1]["check"] = clean[-1].get("check", []) + [c for c in original if c not in clean[-1].get("check", [])]
    return clean, None


def thin_parts(klass, max_steps, with_drawings=False):
    folder = ROOT / "data" / ("book" if klass == "9" else f"book{klass}")
    for f in sorted(folder.glob("unit*.json")):
        unit = json.loads(f.read_text(encoding="utf-8"))
        for it in unit["items"]:
            for p in it["parts"]:
                drawn = any(s.get("draw") for s in p["steps"]) or p.get("figure")
                if len(p["steps"]) > max_steps or (drawn and not with_drawings) or (with_drawings and not drawn):
                    continue
                yield unit, it, p


def enrich_one(klass, unit, it, p, generate):
    path = overlay_path(klass, it["id"], p.get("label", ""))
    rejected = path.with_suffix(".rejected.json")
    if path.exists() or rejected.exists():
        return "skip"
    question = it["question"]
    prompt = PROMPT.format(klass=klass, unit=f"{unit['unit']} - {unit['title']}", question=question,
                           part=f"({p.get('label')}) {p.get('prompt', '')}" if p.get("label") else "(whole question)",
                           steps=json.dumps([{k: v for k, v in st.items() if k != "draw"} for st in p["steps"]], ensure_ascii=False), answer=p["answer"])
    reason, steps = "", None
    for attempt in range(2):                         # one retry: a false check is often fixed on a second try
        try:
            raw = generate(prompt if attempt == 0 else prompt + f"\n\nYour previous answer was rejected: {reason}. Fix it.")
            m = re.search(r"\{.*\}", raw or "", re.S)
            out = json.loads(m.group(0)) if m else {}
            steps, reason = validate(out, p)
        except Exception as exc:
            steps, reason = None, f"error: {exc}"
        if steps:
            break
    path.parent.mkdir(parents=True, exist_ok=True)
    draws = [d for st in p["steps"] for d in (st.get("draw") or [])]
    if steps and draws:                              # the figure is drawn at the first step, then the detailed working follows
        steps[0]["draw"] = draws
    if steps:
        data = {"item": it["id"], "label": p.get("label", ""), "answer_ref": p["answer"], "steps": steps, "keeps_drawing": bool(draws),
                "source": "gemini-4-argon via Vertex AI, verified by sympy", "made": time.strftime("%Y-%m-%d")}
        path.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
        return "kept"
    rejected.write_text(json.dumps({"item": it["id"], "label": p.get("label", ""), "reason": reason}, ensure_ascii=False), encoding="utf-8")
    return "rejected"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="klass", default="10")
    ap.add_argument("--max-steps", type=int, default=1)
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--retry-rejected", action="store_true")
    ap.add_argument("--drawings", action="store_true", help="the parts WITH a figure: keep the figure on the first step")
    a = ap.parse_args()
    env = ROOT / ".env.local"                         # the Vertex service account, for this local run only
    if env.exists() and not os.environ.get("TUTOR_NO_ENV_FILE"):
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip() and k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")
    todo = list(thin_parts(a.klass, a.max_steps, a.drawings))
    if a.retry_rejected:
        for _, it, p in todo:
            r = overlay_path(a.klass, it["id"], p.get("label", "")).with_suffix(".rejected.json")
            if r.exists():
                r.unlink()
    if a.limit:
        todo = todo[:a.limit]
    print(f"class {a.klass}: {len(todo)} parts with <= {a.max_steps} step(s) and no drawing", flush=True)
    counts = {"kept": 0, "rejected": 0, "skip": 0}
    t0 = time.time()

    def run(job):
        r = enrich_one(a.klass, *job, generate=_gemini)
        with _lock:
            counts[r] += 1
            done = sum(counts.values())
            if done % 5 == 0 or done == len(todo):
                print(f"  {done}/{len(todo)}  kept {counts['kept']}  rejected {counts['rejected']}  skipped {counts['skip']}  "
                      f"({time.time() - t0:.0f}s)", flush=True)

    with ThreadPoolExecutor(max_workers=a.workers) as ex:
        list(ex.map(run, todo))
    print("done:", counts, flush=True)


if __name__ == "__main__":
    main()
