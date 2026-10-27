"""Exercise 1.2 accuracy: NEW questions of every Exercise 1.2 type, in two writing styles. Run: python tests/test_ex12.py [--n 30]

For each type a generator makes a question with fresh numbers, writes it as a student would TYPE it and as LaTeX (what a
photo would give), and knows the correct answer from sympy, independently of the engine. The test fails on any WRONG answer;
a question the engine cannot read is counted separately.
"""
import argparse
import random
import sys
import pathlib

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tests"))
sys.path.insert(0, str(ROOT / "train"))
import mathtext  # noqa: E402
import solvers  # noqa: E402

from ex12_gen import GENERATORS, R, SQ, X, Y, Z  # noqa: E402


def answer_values(item):
    out = []
    for p in item["parts"]:
        a = p["answer"].replace("$", " ")
        for piece in [x for x in a.replace("\\ ", " ").split(",") if x.strip()] if "=" in a else [a]:
            out.append(sp.sympify(mathtext.parse_math(piece.split("=")[-1].strip())))
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    args = ap.parse_args()
    bad, rows = [], []
    for name, gen in GENERATORS.items():
        rng = random.Random(name)
        solved = wrong = unread = made = 0
        tries = 0
        while made < args.n and tries < args.n * 10:
            tries += 1
            q = gen(rng)
            if q is None:
                continue
            made += 1
            asc, lat, gold = q
            for style, text in (("typed", asc), ("latex", lat)):
                got = solvers.solve(text)
                if got is None:
                    unread += 1
                    if len([1 for b in bad if b.startswith("UNREAD " + name)]) < 2:
                        bad.append(f"UNREAD {name} [{style}]: {text[:110]}")
                    continue
                try:
                    vals = answer_values(got)
                    ok = len(vals) == len(gold) and all(sp.simplify(sp.nsimplify(v) - sp.nsimplify(g)) == 0 or abs(float(sp.N(v - g))) < 1e-9 for v, g in zip(vals, gold))
                except Exception as exc:
                    ok = False
                    vals = f"unreadable answer {exc}"
                if ok:
                    solved += 1
                else:
                    wrong += 1
                    bad.append(f"WRONG {name} [{style}]: {text[:100]}\n      engine {vals}\n      gold   {gold}")
        rows.append((name, solved, wrong, unread))
    total = [sum(r[i] for r in rows) for i in (1, 2, 3)]
    print(f"{'type':42} {'solved':>7} {'WRONG':>6} {'not read':>9}")
    for name, s, w, u in rows:
        print(f"{name:42} {s:7d} {w:6d} {u:9d}")
    print(f"{'TOTAL':42} {total[0]:7d} {total[1]:6d} {total[2]:9d}")
    for b in bad[:30]:
        print("  -", b)
    sys.exit(1 if total[1] else 0)


if __name__ == "__main__":
    main()
