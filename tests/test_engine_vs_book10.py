"""The Class 10 engine solves the book's own questions WITHOUT the stored solutions, and its answers agree with the book.
Run: python tests/test_engine_vs_book10.py

Each part of every book question (stem + part, as a student would type it) goes to engine10.solve. When the engine solves it,
its final answer must agree with the book's checked answer (answer_match: same numbers and signs in order; a form the matcher
cannot compare is listed for review). Reported: how many book parts the engine solves on its own, per unit, and 0 disagreements.
"""
import json
import os
import pathlib
import sys

os.environ["TUTOR_NO_ENV_FILE"] = "1"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.stdout.reconfigure(encoding="utf-8")

import sympy as sp  # noqa: E402

import engine10  # noqa: E402
from answer_match import answer_ok  # noqa: E402
from modelsolve import explode  # noqa: E402


def _quantities(text):
    """Every value stated in an answer, as numbers or (when it contains x) as sympy expressions: 'x = 2,\\ y = 3' -> [2, 3];
    'Variance = 3.55, SD = 1.88' -> [3.55, 1.88]; 'f^{-1}(x) = \\frac{x+1}{9}, x \\ge 0' -> [(x+1)/9]."""
    import re
    import mathtext
    t = str(text).replace("$", " ")
    t = re.sub(r"\b(?:cm|m)\s*\^\s*\{?\s*[23]\s*\}?", " ", t)                       # cm^2 is a unit, not a square
    t = re.sub(r"\\text\{[^}]*\}|\\operatorname\{[^}]*\}|\\circ|\^\s*\{?\s*\\circ\s*\}?|\b(?:cm|m|mm|km|rad|radians?|units?|hours?|Rs\.?)\b", " ", t)
    t = re.sub(r"x\s*<\s*(-?[\d.]+)\s*or\s*x\s*>\s*(-?[\d.]+)", r"x \\in (-\\infty, \1) \\cup (\2, \\infty)", t)   # x < a or x > b as intervals
    t = re.sub(r"[a-zA-Z]+\^\{-1\}\(x\)\s*=", "=", t)
    out = []
    for piece in re.split(r",\\?\s|;|\\approx|\band\b", t):
        if re.search(r"\\(?:ge|le|ne)\b|<|>", piece):
            continue                                           # a domain note, not a value
        rhs = piece.split("=")[-1].strip(" ,.")
        if not rhs or re.fullmatch(r"[A-Za-z]+", rhs):
            continue
        try:
            e = mathtext.parse_math(rhs)
            e = e.subs({s: sp.Symbol(s.name) for s in e.free_symbols})
            out.append(e)
        except Exception:
            pass
    return out


def _number_seq(text):
    """All numbers of an answer in order, fractions and surds evaluated: '(-\\infty, -\\frac{1}{10}) \\cup' -> [-0.1, ...]."""
    import re
    t = re.sub(r"\b(?:cm|m)\s*\^\s*\{?\s*[23]\s*\}?", " ", str(text).replace("$", " "))
    t = re.sub(r"(-?)\s*\\frac\{(-?\d+(?:\.\d+)?)\}\{(\d+(?:\.\d+)?)\}", lambda m: f" {m.group(1)}{float(m.group(2)) / float(m.group(3))} ", t)
    t = re.sub(r"(\d*)\s*\\sqrt\{(\d+)\}", lambda m: f" {(float(m.group(1)) if m.group(1) else 1) * float(m.group(2)) ** 0.5} ", t)
    return [float(v) for v in re.findall(r"-?\d+(?:\.\d+)?", t)]


def same_values(eng, book_part):
    a, b = _number_seq(eng["parts"][0]["answer"]), _number_seq(book_part["answer"])
    if a and len(a) == len(b) and all(abs(u - v) <= 0.01 * max(1.0, abs(v)) for u, v in zip(a, b)):
        return True
    return _same_quantities(eng, book_part)


def _same_quantities(eng, book_part):
    """Second opinion when the text forms differ: every value the book states must appear in the engine's answer (numbers within
    1%, which allows the book's rounding; expressions in x must be equal)."""
    have, want = _quantities(eng["parts"][0]["answer"]), _quantities(book_part["answer"])
    if not want or not have:
        return False
    for w in want:
        ok = False
        for h in have:
            try:
                if w.free_symbols or h.free_symbols:
                    ok = sp.simplify(w - h) == 0
                else:
                    ok = abs(float(w) - float(h)) <= 0.01 * max(1.0, abs(float(w)))
            except Exception:
                ok = False
            if ok:
                break
        if not ok:
            return False
    return True


per_unit, wrong = {}, []
for f in sorted((ROOT / "data" / "book10").glob("unit*.json")):
    u = json.loads(f.read_text(encoding="utf-8"))
    tried = got = agree = 0
    for it in u["items"]:
        if it["id"].startswith(("c10-rev", )) and it["number"] == "1":          # multiple-choice blocks: not something to compute
            continue
        for cut, part in zip(explode(it), it["parts"]):
            tried += 1
            eng = engine10.solve(cut["question"])
            if not eng:
                continue
            got += 1
            if answer_ok(eng["parts"][0]["answer"], part["answer"]) or answer_ok(part["answer"], eng["parts"][0]["answer"]) or same_values(eng, part):
                agree += 1
            else:
                wrong.append(f"{it['id']} ({part['label'] or '-'}): engine {eng['parts'][0]['answer'][:90]}  |  book {part['answer'][:90]}  |  Q: {cut['question'][:120]}")
    per_unit[u["unit"]] = (u["title"], tried, got, agree)

print(f"{'unit':5} {'title':38} {'parts':>6} {'solved':>7} {'agree':>6}")
for k, (t, a, b, c) in per_unit.items():
    print(f"{k:5d} {t:38} {a:6d} {b:7d} {c:6d}")
print(f"TOTAL {'':38} {sum(v[1] for v in per_unit.values()):6d} {sum(v[2] for v in per_unit.values()):7d} {sum(v[3] for v in per_unit.values()):6d}")
if wrong:
    print(f"\n{len(wrong)} disagreements (engine vs book):")
    for w in wrong:
        print("  -", w)
    sys.exit(1)
print("engine vs book: every part the engine solved agrees with the book")
