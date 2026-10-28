"""Synthetic Class 10 training questions: the book's question types with new numbers, solved by the same templates that wrote the
book (data/src10/_*.py), so every step carries sympy checks. An item is kept only when every check passes.

These are for TRAINING and for a synthetic test set with numbers never used in training; they are never the answer key.

    generate(per_type, seed0=0, avoid=())  -> list of items (one or more parts each), all marked synthetic
"""
import pathlib
import random
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools", ROOT / "data" / "src", ROOT / "data" / "src10"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from build_dataset import verify  # noqa: E402
import _complex as cx  # noqa: E402
import _frac as fr  # noqa: E402
import _func as fu  # noqa: E402
import _gen as g  # noqa: E402
import _mat as mt  # noqa: E402
import _quad as qd  # noqa: E402
from _helpers import P, S  # noqa: E402

R = sp.Rational
X = g.X

UNITS = {1: "Complex Numbers", 2: "Quadratic Equations and Inequalities", 3: "Matrices and Determinants", 4: "Functions and Graphs",
         5: "Algebraic Fractions", 6: "Vectors in Plane", 7: "Trigonometry", 8: "Chords and Arcs of a Circle",
         9: "Tangent and Angles of a Circle", 11: "Information Handling", 12: "Probability"}


def nz(rng, lo=-9, hi=9):
    v = 0
    while v == 0:
        v = rng.randint(lo, hi)
    return v


def item(unit, question, parts):
    return {"kind": "synthetic", "number": "", "page": 0, "question": question, "parts": parts, "unit": unit, "unit_title": UNITS[unit],
            "synthetic": True, "class": 10}


def ctex(z):
    return cx.ctex(z)


# ------------------------------------------------------------------------------------------ unit 1


def complex_arith(rng):
    z1, z2 = cx.C(nz(rng), nz(rng)), cx.C(nz(rng), nz(rng))
    op = rng.choice("+-*/")
    p = cx.p_arith("", z1, z2, op)
    return item(1, r"Simplify and write in the form $a+bi$: " + p["prompt"], [p | {"prompt": ""}])


def complex_inverse(rng):
    z = cx.C(nz(rng), nz(rng))
    p = cx.p_multiplicative_inverse("", z)
    return item(1, rf"Find the multiplicative inverse of ${ctex(z)}$.", [p | {"prompt": ""}])


def complex_modulus(rng):
    z = cx.C(nz(rng), nz(rng))
    p = cx.p_modulus("", z)
    return item(1, rf"Find the modulus of the complex number ${ctex(z)}$.", [p | {"prompt": ""}])


def complex_ipower(rng):
    n = rng.randint(-40, 60)
    p = cx.p_ipower("", n)
    return item(1, rf"Simplify: $i^{{{n}}}$", [p | {"prompt": ""}])


# ------------------------------------------------------------------------------------------ unit 2


def quad_factor(rng):
    a, b, c, d = rng.choice([1, 1, 2, 3]), nz(rng, -7, 7), rng.choice([1, 1, 2]), nz(rng, -7, 7)
    poly = sp.expand((a * X - b) * (c * X - d))
    if sp.Poly(poly, X).LC() < 0 or len(set(sp.solve(poly, X))) < 2:
        return None
    eq = f"{sp.sstr(poly)} = 0"
    p = g.q_solve("", eq, "factor")
    return item(2, f"Solve the following quadratic equation by factorization method: {p['prompt']}", [p | {"prompt": ""}])


def quad_formula(rng):
    a, b, c = rng.choice([1, 1, 2, 3]), nz(rng, -9, 9), nz(rng, -9, 9)
    D = b * b - 4 * a * c
    if D <= 0 or sp.sqrt(D).is_Rational:
        return None
    eq = f"{a}*x**2 + ({b})*x + ({c}) = 0"
    p = g.q_solve("", eq, "formula")
    return item(2, f"Use quadratic formula to solve the following equation: {p['prompt']}", [p | {"prompt": ""}])


def quad_square(rng):
    r1, r2 = nz(rng, -8, 8), nz(rng, -8, 8)
    if r1 == r2:
        return None
    poly = sp.expand((X - r1) * (X - r2))
    p = g.q_solve("", f"{sp.sstr(poly)} = 0", "square")
    return item(2, f"Solve the following quadratic equation by completing square method: {p['prompt']}", [p | {"prompt": ""}])


def quad_nature(rng):
    a, b, c = rng.randint(1, 7), rng.randint(-12, 12), rng.randint(-9, 9)
    if c == 0:
        return None
    poly = f"{a}*x**2 + ({b})*x + ({c})"
    p = qd.nature("", poly)
    return item(2, f"Examine the nature of roots of the following quadratic equation: {p['prompt']}", [p | {"prompt": ""}])


def quad_form(rng):
    r1, r2 = R(nz(rng, -9, 9), rng.choice([1, 1, 2, 3, 5])), R(nz(rng, -9, 9), rng.choice([1, 1, 2]))
    if r1 == r2:
        return None
    p = qd.roots_to_eq("", r1, r2)
    return item(2, f"Form a quadratic equation whose roots are {p['prompt']}", [p | {"prompt": ""}])


def quad_ineq(rng):
    r1, r2 = sorted({nz(rng, -6, 6), nz(rng, -6, 6)})
    if r1 == r2:
        return None
    poly = sp.sstr(sp.expand((X - r1) * (X - r2)))
    op = rng.choice(["<", ">", "<=", ">="])
    p = qd.inequality("", poly, op)
    return item(2, f"Solve the following inequality: {p['prompt']}", [p | {"prompt": ""}])


# ------------------------------------------------------------------------------------------ unit 3


def rmat(rng, lo=-6, hi=9):
    return mt.M([[rng.randint(lo, hi) for _ in range(2)] for _ in range(2)])


def mat_product(rng):
    A, B = rmat(rng), rmat(rng)
    steps, v = mt.mul(A, B)
    return item(3, rf"If $A = {mt.mtex(A)}$ and $B = {mt.mtex(B)}$, then find $AB$.", [P("", steps, mt.ans(v))])


def mat_inverse(rng):
    A = rmat(rng)
    if A.det() == 0:
        return None
    steps, v = mt.inv(A)
    return item(3, rf"Find multiplicative inverse of the matrix ${mt.mtex(A)}$.", [P("", steps, mt.ans(v))])


def mat_det(rng):
    A = rmat(rng)
    steps, v = mt.det(A)
    return item(3, rf"Find the value of the determinant ${mt.mtex(A, True)}$.", [P("", steps, f"${sp.latex(v)}$")])


def mat_system(rng):
    x0, y0 = nz(rng, -6, 6), nz(rng, -6, 6)
    A = rmat(rng, -5, 6)
    if A.det() == 0:
        return None
    B = A * mt.M([x0, y0])
    method = rng.choice(["cramer", "inverse"])
    steps, vals = (mt.cramer if method == "cramer" else mt.inverse_solve)(A, B)
    eqs = rf"{mt._eq_tex(A[0, 0], A[0, 1], B[0], ('x', 'y'))},\ {mt._eq_tex(A[1, 0], A[1, 1], B[1], ('x', 'y'))}"
    name = "Use Cramer's rule to solve" if method == "cramer" else "Solve by matrix inversion method"
    return item(3, f"{name} the following pair of linear equations: ${eqs}$", [P("", steps, mt.sys_answer(vals))])


# ------------------------------------------------------------------------------------------ unit 4


def lin(rng):
    return f"{nz(rng, -6, 6)}*x + ({rng.randint(-9, 9)})"


def fn_compose(rng):
    f, gg = lin(rng), rng.choice([lin(rng), f"x**2 + ({rng.randint(-5, 5)})"])
    p, _ = fu.compose("", "f", f, "g", gg)
    return item(4, rf"If $f(x) = {sp.latex(fu.fx(f))}$ and $g(x) = {sp.latex(fu.fx(gg))}$, find $(f\circ g)(x)$.", [p | {"prompt": ""}])


def fn_abs_eq(rng):
    a, b, k = nz(rng, -5, 5), rng.randint(-9, 9), rng.randint(1, 12)
    inner = f"{a}*x + ({b})"
    t = sp.latex(fu.fx(inner))
    p = fu.abs_equation("", inner, k, f"$|{t}| = {k}$")
    return item(4, f"Solve and express the solution on number line: $|{t}| = {k}$", [p | {"prompt": ""}])


def fn_combine(rng):
    f, gg = lin(rng), lin(rng)
    op = rng.choice("+-*")
    sym = {"+": "+", "-": "-", "*": r"\cdot"}[op]
    p = fu.combine("", "f", f, "g", gg, op, "")
    return item(4, rf"If $f(x) = {sp.latex(fu.fx(f))}$, $g(x) = {sp.latex(fu.fx(gg))}$, then find $f(x) {sym} g(x)$.", [p])


# ------------------------------------------------------------------------------------------ unit 5


def frac_reduce(rng):
    a, b, c = nz(rng, -7, 7), nz(rng, -7, 7), nz(rng, -7, 7)
    if len({a, b, c}) < 3:
        return None
    num, den = sp.expand((X - a) * (X - b)), sp.expand((X - a) * (X - c))
    t = rf"\frac{{{sp.latex(num)}}}{{{sp.latex(den)}}}"
    p = fr.reduce("", sp.sstr(num), sp.sstr(den), f"${t}$")
    return item(5, f"Reduce the following rational expression to lowest form: ${t}$", [p | {"prompt": ""}])


def frac_add(rng):
    a, b = nz(rng, -6, 6), nz(rng, -6, 6)
    if a == b:
        return None
    s = rng.choice("+-")
    terms = [("+", str(nz(rng, 1, 5)), f"x - ({a})"), (s, str(nz(rng, 1, 5)), f"x - ({b})")]
    t = rf"\frac{{{terms[0][1]}}}{{{sp.latex(X - a)}}} {s} \frac{{{terms[1][1]}}}{{{sp.latex(X - b)}}}"
    p = fr.combine("", terms, f"${t}$")
    return item(5, f"Simplify: ${t}$", [p | {"prompt": ""}])


# ------------------------------------------------------------------------------------------ unit 6, 8, 9


import unit06 as u6  # noqa: E402  (the vector helpers live in the unit file)


def vec_unit(rng):
    v = (nz(rng), nz(rng))
    steps, u = u6.unit_steps(v)
    return item(6, rf"Find a unit vector in the direction of the vector $\underline{{a}} = {u6.vt(v)}$.", [P("", steps, f"${u6.vt(u)}$")])


def vec_combo(rng):
    a, b = (nz(rng), nz(rng)), (nz(rng), nz(rng))
    k1, k2 = nz(rng, -5, 5), nz(rng, -5, 5)
    steps, v, expr = u6.combo([k1, k2], [a, b], "ab")
    return item(6, rf"If $\underline{{a}} = {u6.vt(a)}$ and $\underline{{b}} = {u6.vt(b)}$, then find ${expr}$.", [P("", steps, f"${u6.vt(v)}$")])


TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15), (12, 16, 20)]


def chord_length(rng):
    d, h, r = rng.choice(TRIPLES)
    if rng.random() < 0.5:
        d, h = h, d
    steps = [S(rf"AM = \sqrt{{r^2 - d^2}} = \sqrt{{{r}^2 - {d}^2}} = {h}", "Pythagoras in the right triangle formed by the radius, the distance and half the chord.",
               "رداس، فاصلہ اور آدھے وتر سے بننے والی قائمہ مثلث میں فیثا غورث۔", f"sqrt({r}**2 - {d}**2) == {h}"),
             S(rf"\text{{Chord}} = 2 \times {h} = {2 * h}\ \text{{cm}}", "The perpendicular from the centre bisects the chord.", "مرکز سے عمود وتر کی تنصیف کرتا ہے۔",
               f"2*sqrt({r}**2 - {d}**2) == {2 * h}")]
    return item(8, f"Calculate the length of a chord which stands at a distance of {d} cm from the centre of a circle whose radius is {r} cm.", [P("", steps, f"${2 * h}$ cm")])


def sector(rng):
    r, th = rng.randint(2, 15), R(rng.randint(1, 30), 10)
    l, A = r * th, R(1, 2) * r * r * th
    steps = [S(rf"\ell = r\theta = {r} \times {sp.latex(th)} = {sp.latex(l)}\ \text{{cm}}", "Arc length.", "قوس کی لمبائی۔", f"{r}*({sp.sstr(th)}) == {sp.sstr(l)}"),
             S(rf"A = \frac{{1}}{{2}}r^2\theta = \frac{{1}}{{2}}({r})^2({sp.latex(th)}) = {sp.latex(A)}\ \text{{cm}}^2", "Area of a sector.", "قطاع کا رقبہ۔",
               f"R(1,2)*{r}**2*({sp.sstr(th)}) == {sp.sstr(A)}")]
    return item(9, rf"Find $\ell$ and area of sector, when $r = {r}$ cm, $\theta = {float(th):g}$ radian.", [P("", steps, rf"$\ell = {sp.latex(l)}$ cm, $A = {sp.latex(A)}$ cm$^2$")])


# ------------------------------------------------------------------------------------------ unit 11, 12


import unit11 as u11  # noqa: E402
import unit12 as u12  # noqa: E402


def dispersion(rng):
    data = [rng.randint(10, 60) for _ in range(rng.randint(5, 7))]
    steps, m, v, s = u11.dispersion(data)
    return item(11, "Find the variance and standard deviation of the data: " + ", ".join(map(str, data)) + ".",
                [P("", steps, f"Variance = {u11.fmt(v, 2)}, SD = {u11.fmt(s, 2)}")])


def dice_sum(rng):
    k = rng.randint(2, 12)
    kind = rng.choice(["sum", "product", "difference"])
    if kind == "sum":
        ev, t = (lambda s: s[0] + s[1] == k), f"a sum of {k}"
    elif kind == "product":
        k = rng.choice([4, 6, 8, 12, 18, 24])
        ev, t = (lambda s: s[0] * s[1] == k), f"a product of {k}"
    else:
        k = rng.randint(0, 5)
        ev, t = (lambda s: abs(s[0] - s[1]) == k), f"a difference of {k}"
    p, _ = u12.event_part("", u12.DICE2, "two dice, 36 outcomes", ev, "")
    return item(12, f"Two dice are rolled. Find the probability of getting {t}.", [p])


def cards(rng):
    a_name, a = rng.choice([("red", 26), ("black", 26), ("hearts", 13), ("spades", 13), ("kings", 4), ("aces", 4)])
    repl = rng.random() < 0.5
    p = u12.two_draws("", a, a - (0 if repl else 1), 52, 52 if repl else 51, "", "With replacement." if repl else "Without replacement.")
    return item(12, f"Two cards are drawn from a standard deck of 52 cards {'with' if repl else 'without'} replacement. Find the probability that both are {a_name}.", [p])


TYPES = {"complex arithmetic": complex_arith, "complex inverse": complex_inverse, "complex modulus": complex_modulus, "powers of i": complex_ipower,
         "quadratic by factorization": quad_factor, "quadratic formula": quad_formula, "completing the square": quad_square, "nature of roots": quad_nature,
         "equation from roots": quad_form, "quadratic inequality": quad_ineq, "matrix product": mat_product, "matrix inverse": mat_inverse, "determinant": mat_det,
         "linear system by matrices": mat_system, "composition": fn_compose, "absolute value equation": fn_abs_eq, "operations on functions": fn_combine,
         "reduce a fraction": frac_reduce, "add fractions": frac_add, "unit vector": vec_unit, "vector combination": vec_combo, "chord length": chord_length,
         "arc and sector": sector, "variance and standard deviation": dispersion, "dice probability": dice_sum, "card probability": cards}


def all_checks_pass(it):
    for part in it["parts"]:
        for st in part["steps"]:
            for c in st.get("check", []):
                try:
                    if not verify(c):
                        return False
                except Exception:
                    return False
    return any(st.get("check") for part in it["parts"] for st in part["steps"])


def generate(per_type, seed0=0, avoid=()):
    out, seen = [], set(avoid)
    for name, gen in TYPES.items():
        rng = random.Random(f"synth10-{seed0}-{name}")
        made = tries = 0
        slug = name.replace(" ", "-")
        while made < per_type and tries < per_type * 30:
            tries += 1
            try:
                it = gen(rng)
            except Exception:
                it = None
            if not it or it["question"] in seen or not all_checks_pass(it):
                continue
            seen.add(it["question"])
            it["id"] = f"syn10-{slug}-{seed0}-{made}"
            out.append(it)
            made += 1
    return out


if __name__ == "__main__":
    items = generate(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
    by = {}
    for it in items:
        by[it["unit"]] = by.get(it["unit"], 0) + 1
    print(len(items), "items, by unit:", dict(sorted(by.items())))
    print(items[0]["question"], "->", items[0]["parts"][0]["answer"])
