"""Shared helpers for the solvers: LaTeX in the book's style, step/part builders, and the verification gate."""
import hashlib
import pathlib
import re
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools", ROOT / "data" / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from _helpers import P, S, T  # noqa: E402,F401
from build_dataset import verify  # noqa: E402
import mathtext  # noqa: E402,F401

R = sp.Rational


def py(e):
    """sympy expression -> text that the sympy checks (and the build) can read back."""
    return sp.sstr(e)


def tex_sum(e):
    """A sum in the book's order: the constant first, then positive terms, then negative terms (4 - sqrt3, sqrt5 - sqrt2)."""
    e = sp.expand(e)
    terms = list(sp.Add.make_args(e))

    def key(t):
        neg = t.could_extract_minus_sign()
        return (0 if t.is_Rational else 1, 1 if (neg and not t.is_Rational) else 0, sp.default_sort_key(abs(t) if neg else t))

    out = ""
    for i, t in enumerate(sorted(terms, key=key)):
        neg = t.could_extract_minus_sign()
        body = sp.latex(-t if neg else t)
        if i == 0:
            out += ("-" if neg else "") + body
        else:
            out += (" - " if neg else " + ") + body
    return out


def tex(e):
    """LaTeX for a number or expression; a sum over an integer denominator is shown as one fraction."""
    e = sp.sympify(e)
    if e.is_Rational:
        return sp.latex(e)
    n, d = sp.fraction(sp.together(e))
    if d != 1 and d.is_Integer and n.is_Add:
        return rf"\frac{{{tex_sum(n)}}}{{{sp.latex(d)}}}"
    return tex_sum(e) if e.is_Add else sp.latex(e)


def paren(e):
    return rf"\left({tex(e)}\right)" if sp.sympify(e).is_Add else tex(e)


def solved_item(question, parts, source="solver"):
    """An item shaped like the stored book items, so the page shows it the same way."""
    uid = hashlib.md5(question.encode("utf-8")).hexdigest()[:8]
    return {"id": f"solved-{uid}", "kind": "solved", "source": source, "number": "", "page": 0, "unit": 0,
            "unit_title": "Solved for your question", "question": question, "parts": parts, "verified": True}


def failed_checks(item):
    """Every sympy check in the solution that is false (or unreadable). The solver returns nothing unless this is empty."""
    bad = []
    for p in item["parts"]:
        for i, st in enumerate(p["steps"]):
            for chk in st.get("check", []):
                try:
                    ok = verify(chk)
                except Exception:
                    ok = False
                if not ok:
                    bad.append(f"step {i + 1}: {chk}")
    return bad


def part_markers(text):
    """Split 'q (i) A (ii) B' into [stem, 'A', 'B']; with no markers returns [text]."""
    pieces = re.split(r"\(\s*(?:i{1,3}|iv|vi{0,3}|ix|x)\s*\)", text, flags=re.I)
    return [p.strip() for p in pieces]


def labels(n):
    return ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x"][:n]


def first_math_start(text):
    """Index where the maths begins in 'rationalize the denominator of 3/(sqrt5+sqrt2)'."""
    m = re.search(r"[\d(\\]|sqrt|root|√", text)
    return m.start() if m else len(text)
