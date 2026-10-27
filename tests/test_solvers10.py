"""Class 10 engine (complex numbers). Run: python tests/test_solvers10.py [--n 30]

A. BOOK      every stored Class 10 question part the engine reads must give the stored answer.
B. NEW       new numbers, typed and as LaTeX: the answer must equal sympy's own value (computed here, not by the engine).
C. REFUSAL   questions outside its types are refused, never guessed.
Wrong answers fail the test; questions it does not read are reported only.
"""
import argparse
import json
import pathlib
import random
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "train"))

import solvers10  # noqa: E402
from answer_match import answer_ok  # noqa: E402

I = sp.I


def value_of(answer):
    t = solvers10._to_py(answer.replace("$", "").replace(" ", ""))
    return sp.nsimplify(solvers10._value(t))


def same(engine_answer, gold):
    try:
        return sp.simplify(value_of(engine_answer) - gold) == 0
    except Exception:
        return False


def ztex(z, typed):
    a, b = sp.re(z), sp.im(z)
    sign = "+" if b >= 0 else "-"
    bb = abs(b)
    ib = "i" if bb == 1 else f"{bb}i"
    return f"({a}{sign}{ib})" if typed else f"({a} {sign} {ib})"


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=30)
    args = ap.parse_args()
    wrong, notes = [], []

    # A. book
    read = agree = 0
    for f in sorted((ROOT / "data" / "book10").glob("unit*.json")):
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            stem = it["question"].split("(i)")[0].strip()
            for p in it["parts"]:
                if not p.get("prompt") or "verified" in p["answer"] or p["answer"].startswith("("):
                    continue
                q = f"{stem} {p['prompt']}" if len(it["parts"]) > 1 else it["question"]
                got = solvers10.solve(q)
                if got is None:
                    continue
                read += 1
                if answer_ok(got["parts"][0]["answer"], p["answer"]):
                    agree += 1
                else:
                    wrong.append(f"BOOK {it['id']} ({p['label']}): engine {got['parts'][0]['answer']} vs book {p['answer']}")
    notes.append(f"A. book parts read by the engine: {read}; same answer as stored: {agree}")

    # B. new numbers
    rng = random.Random(7)
    stats = {}

    def rc():
        return sp.Integer(rng.choice([v for v in range(-9, 10) if v])) + sp.Integer(rng.choice([v for v in range(-9, 10) if v])) * I

    def check(kind, text, gold):
        s = stats.setdefault(kind, [0, 0, 0])
        got = solvers10.solve(text)
        if got is None:
            s[2] += 1
            return
        ans = got["parts"][0]["answer"]
        ok = same(ans, gold) if not isinstance(gold, dict) else all(f"{k} = {sp.latex(v)}" in ans for k, v in gold.items())
        if ok:
            s[0] += 1
        else:
            s[1] += 1
            wrong.append(f"NEW {kind}: {text!r} -> {ans} (expected {gold})")

    for _ in range(args.n):
        z1, z2 = rc(), rc()
        for typed in (True, False):
            for op, f in (("+", z1 + z2), ("-", z1 - z2), ("", z1 * z2), ("/" if typed else r" \div ", z1 / z2)):
                check(f"arith {op.strip() or '*'}", f"Simplify and write in the form a+bi: {ztex(z1, typed)}{op}{ztex(z2, typed)}", sp.expand(f))
        n = rng.randint(-40, 60)
        check("power of i", f"Simplify i^{n}" if n >= 0 else f"Simplify $i^{{{n}}}$", I ** n)
        check("modulus", f"Find the modulus of {ztex(z1, True)[1:-1]}", sp.Abs(z1))
        check("multiplicative inverse", f"Find multiplicative inverse of {ztex(z1, True)[1:-1]}", sp.expand(1 / z1))
        check("additive inverse", f"Write additive inverse of {ztex(z1, True)[1:-1]}", -z1)
        check("square", f"Simplify {ztex(z1, True)}^2", sp.expand(z1 ** 2))
        check("reciprocal", f"Simplify {ztex(z1, True)}^-1", sp.expand(1 / z1))
        x0, y0 = rng.randint(-9, 9), rng.randint(-9, 9)
        p, q = rc(), rc()
        if sp.expand(sp.re(p) * sp.im(q) - sp.im(p) * sp.re(q)) != 0:
            rhs = sp.expand(p * x0 + q * y0)
            check("find x and y", f"Find the values of x and y: {ztex(p, True)}x + {ztex(q, True)}y = {ztex(rhs, True)[1:-1]}", {"x": x0, "y": y0})
        a1, b1, a2, b2, z0, w0 = rc(), rc(), rc(), rc(), rc(), rc()
        if sp.expand(a1 * b2 - a2 * b1) != 0:
            c1, c2 = sp.expand(a1 * z0 + b1 * w0), sp.expand(a2 * z0 + b2 * w0)
            text = (f"Solve for z and w: ${ztex(a1, False)}z + {ztex(b1, False)}w = {ztex(c1, False)}$ and "
                    f"${ztex(a2, False)}z + {ztex(b2, False)}w = {ztex(c2, False)}$")
            got = solvers10.solve(text)
            s = stats.setdefault("z, w system", [0, 0, 0])
            if got is None:
                s[2] += 1
            else:
                ans = got["parts"][0]["answer"]
                zs, ws = ans.replace("$", "").split(r",\ w = ")
                if same("$" + zs.replace("z = ", "") + "$", z0) and same("$" + ws + "$", w0):
                    s[0] += 1
                else:
                    s[1] += 1
                    wrong.append(f"NEW system: {text!r} -> {ans} (expected z={z0}, w={w0})")
    notes.append("B. new numbers, per type:   solved / WRONG / not read")
    for k, (ok, bad, none) in stats.items():
        notes.append(f"     {k:24} {ok:4} {bad:6} {none:6}")

    # C. refusal
    unknown = ["Rationalize the denominator of 3/(2+sqrt5)", "Find the area of a circle of radius 7", "who wrote Hamlet",
               "Express 0.25 as p/q", "Solve x^2 - 5x + 6 = 0", "2+5i"]
    accepted = [q for q in unknown if solvers10.solve(q)]
    notes.append(f"C. outside its types but answered: {accepted}")
    for q in accepted:
        wrong.append(f"REFUSAL: answered {q!r}")

    print("\n".join(notes))
    if wrong:
        print(f"\n{len(wrong)} PROBLEM(S):")
        for w in wrong[:25]:
            print("  -", w)
        sys.exit(1)
    print("\nno wrong answers")


if __name__ == "__main__":
    main()
