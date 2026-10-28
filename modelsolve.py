"""Ask the trained model for a solution, check it with sympy, and ask again if a check fails.

The model is wrong sometimes; its own `check` strings tell us when. A reply is accepted when it is valid JSON, has at least one
check and every check is true. Otherwise the next attempt samples with a little randomness (the first attempt is greedy), and
after the last attempt the reply with the most true checks is returned, marked unverified, never presented as certain.

A multi-part question is answered one part at a time: the stem plus (i), then the stem plus (ii), ... as in training.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
for p in (ROOT, ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build_dataset import verify  # noqa: E402
from prompts import SOLVE_RULES  # noqa: E402
from solution_io import parse_solution  # noqa: E402
from solvers.common import labels, part_markers  # noqa: E402

TEMPERATURES = (0.0, 0.5, 0.8)


def explode(item):
    """One item per part: question = the stem plus that part's text, a single part in the answer."""
    parts = item["parts"]
    if len(parts) < 2:
        return [item]
    pieces = part_markers(item["question"])           # [stem, text of (i), text of (ii), ...]
    stem = pieces[0]
    out = []
    for i, p in enumerate(parts):
        label = p.get("label") or str(i + 1)
        text = pieces[i + 1] if len(pieces) == len(parts) + 1 else (p.get("prompt") or "").strip()
        asked = " ".join(x for x in (stem, text if text else f"({label})") if x)
        out.append({**item, "id": f"{item['id']}-{label}", "question": asked,
                    "parts": [{**p, "label": "", "prompt": ""}], "asked": []})
    return out


def explode_all(items):
    return [e for it in items for e in explode(it)]


def examples_text(index, by_id, question, k=2, budget=3500, exclude_id=None):
    """The k nearest solved examples as prompt text, stopping before the prompt grows past `budget` characters
    (the first example is always kept). Training, evaluation and the tutor all build their prompts with this."""
    seen, texts = set(), []
    for h in index.search(question, k=k * 3):
        if h["id"] == exclude_id or h["id"] in seen or h["id"] not in by_id:
            continue
        seen.add(h["id"])
        e = by_id[h["id"]]
        text = f"EXAMPLE {len(texts) + 1} ({e['id']}):\n" + json.dumps({"question": e["question"], "parts": e["parts"]}, ensure_ascii=False)
        if texts and sum(len(t) for t in texts) + len(text) > budget:
            break
        texts.append(text)
        if len(texts) == k:
            break
    return "\n\n".join(texts)


def check_solution(sol):
    """-> (number of checks, list of the checks that are false or cannot be evaluated)."""
    total, bad = 0, []
    for part in sol.get("parts", []):
        for step in part.get("steps", []):
            for chk in step.get("check", []):
                total += 1
                try:
                    ok = bool(verify(chk))
                except Exception:
                    ok = False
                if not ok:
                    bad.append(chk)
    return total, bad


def attempt(question, examples_text, attempts=3, max_new_tokens=2500, generate=None, rules=None):
    """-> {"solution": dict or None, "raw": the chosen reply, "raws": every reply, "bad": false checks, "checks": int,
    "verified": bool, "tries": attempts used}. `generate(messages, max_new_tokens, temperature)` defaults to the local model.
    `rules` is the system prompt's rule text (prompts.solve_rules(klass)); the Class 9 rules by default."""
    if generate is None:
        import local_models
        generate = local_models.generate
    messages = [{"role": "system", "content": (rules or SOLVE_RULES) + "\n\n" + examples_text},
                {"role": "user", "content": question}]
    best, raws = None, []
    for t in TEMPERATURES[:max(1, attempts)]:
        raw = generate(messages, max_new_tokens=max_new_tokens, temperature=t)
        raws.append(raw)
        try:
            sol, _ = parse_solution(raw)
            if not isinstance(sol.get("parts"), list) or not sol["parts"]:
                continue
        except Exception:
            continue
        total, bad = check_solution(sol)
        verified = total > 0 and not bad
        rank = (verified, total > 0, (total - len(bad)) / max(1, total))
        if best is None or rank > best["rank"]:
            best = {"solution": sol, "raw": raw, "bad": bad, "checks": total, "verified": verified, "rank": rank, "tries": len(raws)}
        if verified:
            break
    if best is None:
        return {"solution": None, "raw": raws[-1] if raws else "", "raws": raws, "bad": [], "checks": 0, "verified": False, "tries": len(raws)}
    best.pop("rank")
    best["raws"] = raws
    best["tries"] = len(raws)
    return best


def solve_question(question, examples_for, attempts=3, max_new_tokens=2500, generate=None):
    """Answer the whole question. `examples_for(text)` returns the retrieved examples to put in the prompt.
    -> a solution dict with `verified`, `unverified_checks`, `tries` (per part), or None if the model gave nothing usable."""
    pieces = part_markers(question)
    if len(pieces) < 3:                                  # no part markers, or a lone "(i)"
        r = attempt(question, examples_for(question), attempts, max_new_tokens, generate)
        sol = r["solution"]
        if sol is None:
            return None
        sol.update(verified=r["verified"], unverified_checks=r["bad"], tries=[r["tries"]])
        return sol
    stem, texts = pieces[0], pieces[1:]
    parts, bad, tries, verified = [], [], [], True
    for label, text in zip(labels(len(texts)), texts):
        q = f"{stem} {text}".strip()
        r = attempt(q, examples_for(q), attempts, max_new_tokens, generate)
        sol = r["solution"]
        if sol is None:
            return None
        part = dict(sol["parts"][0])
        part.update(label=label, prompt=text)
        parts.append(part)
        bad += r["bad"]
        tries.append(r["tries"])
        verified = verified and r["verified"]
    return {"id": "gen-" + "".join(c for c in question.lower()[:40] if c.isalnum()), "kind": "generated", "number": "", "page": 0,
            "question": question, "parts": parts, "verified": verified, "unverified_checks": bad, "tries": tries}
