"""Training questions made by the solver engine: new numbers, every step checked, final answer checked against sympy.

Each Exercise 1.2 style generator (train/ex12_gen.py) writes a question in two ways, typed and LaTeX. The engine solves the
LaTeX form; the solution is kept only if its final answer equals the generator's own answer from sympy. The model then learns
from solutions that are right by construction, in the same step style the engine (and the book) use.
"""
import pathlib
import random
import re
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "train", ROOT / "tools", ROOT / "data" / "src"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mathtext  # noqa: E402
import solvers  # noqa: E402
from ex12_gen import GENERATORS  # noqa: E402


def _answer_values(item):
    out = []
    for part in item["parts"]:
        a = part["answer"].replace("$", " ").replace("\\ ", " ")
        for piece in [x for x in a.split(",") if x.strip()] if "=" in a else [a]:
            out.append(sp.sympify(mathtext.parse_math(piece.split("=")[-1].strip())))
    return out


def _matches(item, gold):
    try:
        vals = _answer_values(item)
        return len(vals) == len(gold) and all(sp.simplify(sp.nsimplify(v) - sp.nsimplify(g)) == 0 or abs(float(sp.N(v - g))) < 1e-9 for v, g in zip(vals, gold))
    except Exception:
        return False


def engine_items(per_type, seed0=0, avoid=()):
    """per_type engine-solved items for every Exercise 1.2 type. `avoid` is a set of question texts to skip."""
    out, seen = [], set(avoid)
    for name, gen in GENERATORS.items():
        rng = random.Random(f"engine-{seed0}-{name}")
        made = tries = 0
        slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
        while made < per_type and tries < per_type * 25:
            tries += 1
            q = gen(rng)
            if q is None:
                continue
            typed, latex, gold = q
            item = solvers.solve(latex)
            if not item or item["question"] in seen or not _matches(item, gold):
                continue
            seen.add(item["question"])
            item = {**item, "id": f"eng-{slug}-{seed0}-{made}", "kind": "engine", "synthetic": True, "asked": [typed, latex],
                    "unit": 1, "unit_title": "Real Numbers"}
            out.append(item)
            made += 1
    return out
