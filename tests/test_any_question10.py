"""Any Class 10 question the student types is SOLVED (not answered with a book example), and the answer is right.
Run: python tests/test_any_question10.py [--n 10]

Angles tested, for every question type of Units 1-12:
  * new random numbers (seeded), never the book's
  * many wordings: 'Solve ...', 'Find the roots of ...', '... solve kro', the method named or not, question first or last
  * many ways of typing: plain text, unicode x², phone-typed x2, LaTeX in $...$, CAPITALS and extra spaces, terms moved across '='
  * an INDEPENDENT oracle: sympy (or plain enumeration) computes the right answer from the question itself, never through
    the templates the engine uses; a solved answer that disagrees is a WRONG answer and fails the test
  * through the real server (/api/answer, class 10): the reply must be mode 'solved' with checked steps, not a book example
  * traps: questions outside the engine (a cubic, a 3-by-3 inverse, nonsense) must be declined, never answered wrongly
Pass: 0 wrong answers anywhere, and at least 95% of the generated questions solved for every type.
"""
import argparse
import itertools
import json
import math
import os
import pathlib
import random
import re
import statistics
import sys
import time
from fractions import Fraction

os.environ["TUTOR_NO_ENV_FILE"] = "1"
os.environ["NO_EMBEDDINGS"] = "1"
os.environ["MODEL_BACKEND"] = "local"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import sympy as sp  # noqa: E402

import engine10  # noqa: E402

x, y = sp.symbols("x y")
LOC = {"x": x, "y": y, "Matrix": sp.Matrix, "Interval": sp.Interval, "Union": sp.Union, "FiniteSet": sp.FiniteSet, "oo": sp.oo,
       "sqrt": sp.sqrt, "pi": sp.pi, "I": sp.I, "Rational": sp.Rational, "Complement": sp.Complement, "Reals": sp.S.Reals}


def nz(r, lo=-9, hi=9):
    v = 0
    while v == 0:
        v = r.randint(lo, hi)
    return v


def term(c, v, first=False):
    """Coefficient and variable as a student types it: x, -x, 3x."""
    if c == 0:
        return ""
    body = (v if abs(c) == 1 else f"{abs(c)}{v}") if v else str(abs(c))
    sign = ("-" if c < 0 else "") if first else (" - " if c < 0 else " + ")
    return sign + body


def poly_text(cs, style="ascii", var="x"):
    """[a, b, c] -> '3x^2 - 7x + 2' in a typing style."""
    n = len(cs) - 1
    out = ""
    for k, c in enumerate(cs):
        p = n - k
        v = "" if p == 0 else (var if p == 1 else {"ascii": f"{var}^{p}", "unicode": f"{var}{'²' if p == 2 else '³'}", "phone": f"{var}{p}",
                                                     "latex": f"{var}^{{{p}}}"}[style])
        out += term(c, v, first=(out == ""))
    out = out or "0"
    return out.replace(" ", "") if style == "phone" else out


def vals(item):
    return [sp.sympify(v, locals=LOC) for v in item["parts"][0].get("values", [])]


def same(a, b, tol=None):
    try:
        if tol is not None:
            return abs(float(a) - float(b)) <= tol
        if isinstance(a, sp.MatrixBase) or isinstance(b, sp.MatrixBase):
            return sp.Matrix(a) == sp.Matrix(b)
        if isinstance(a, sp.Set) or isinstance(b, sp.Set):
            return sp.simplify(a.symmetric_difference(b)) == sp.S.EmptySet if hasattr(a, "symmetric_difference") else a == b
        return sp.simplify(sp.sympify(a) - sp.sympify(b)) == 0
    except Exception:
        return False


# ------------------------------------------------------------------------------------------ generators: (question, oracle check)
# each returns (text, check(item) -> True when right)


def g_quadratic(r):
    while True:
        a, b, c = r.choice([1, 1, 2, 3, 4, 5, 6]), r.randint(-12, 12), r.randint(-15, 15)
        if c and b * b - 4 * a * c >= 0:
            break
    roots = sorted(sp.solve(a * x ** 2 + b * x + c, x), key=float)
    style = r.choice(["ascii", "unicode", "phone", "latex"])
    lhs = poly_text([a, b, c], style)
    eq = f"{lhs} = 0"
    if r.random() < 0.3 and style != "latex":                       # move the constant across
        eq = f"{poly_text([a, b, 0], style)} = {-c}"
    rational = sp.sqrt(b * b - 4 * a * c).is_Rational
    wording = r.choice(["Solve {e}", "solve the equation {e}", "Find the roots of {e}", "{e} solve kro", "SOLVE   {e}", "what are the values of x if {e}",
                        "Use quadratic formula to solve {e}", "solve by completing square method: {e}"] +
                       (["Solve by factorization: {e}"] if rational else []))
    q = wording.format(e=f"${eq}$" if style == "latex" else eq)
    return q, lambda it: len(vals(it)) == len(roots) and all(same(u, v) for u, v in zip(sorted(vals(it), key=float), roots))


def g_rational_eq(r):
    while True:
        p, q_, k = nz(r, -6, 6), nz(r, -6, 6), r.choice([1, 2, 3, 4, 5, 6, 8, 10, 12])
        if p == q_:
            continue
        E = 1 / (x - p) - 1 / (x - q_) - sp.Rational(1, k)
        num = sp.fraction(sp.together(E))[0]
        roots = sp.solve(E, x)
        if len(roots) == 2 and all(v.is_real for v in roots) and sp.degree(num, x) == 2:
            roots = sorted(roots, key=float)
            break
    t = r.choice([f"1/(x-{p}) - 1/(x-{q_}) = 1/{k}".replace("--", "+"), rf"$\frac{{1}}{{x-{p}}}-\frac{{1}}{{x-{q_}}}=\frac{{1}}{{{k}}}$".replace("--", "+")])
    return f"Solve {t}", lambda it: sorted(vals(it), key=float) and all(same(u, v) for u, v in zip(sorted(vals(it), key=float), roots))


def g_nature(r):
    a, b, c = r.randint(1, 9), r.randint(-12, 12), nz(r, -10, 10)
    return r.choice(["Find the nature of roots of {e}", "examine the nature of the roots: {e}", "Discriminant of {e}?"]).format(e=f"{poly_text([a, b, c])} = 0"), \
        lambda it: same(vals(it)[0], b * b - 4 * a * c)


def g_form(r):
    r1, r2 = nz(r, -9, 9), sp.Rational(nz(r, -9, 9), r.choice([1, 1, 2, 3]))
    if r1 == r2:
        r2 += 1
    t = r.choice(["Form a quadratic equation whose roots are {a} and {b}", "find the quadratic equation with roots {a}, {b}"]).format(a=r1, b=r2)
    return t, lambda it: sp.simplify(sp.Poly(vals(it)[0], x).monic().as_expr() - sp.expand((x - r1) * (x - r2))) == 0


def g_ineq(r):
    a, b = sorted(r.sample(range(-8, 9), 2))
    op = r.choice(["<", ">", "<=", ">="])
    shown = {"<": "<", ">": ">", "<=": r.choice(["<=", "≤"]), ">=": r.choice([">=", "≥"])}[op]
    E = sp.expand((x - a) * (x - b))
    sol = sp.solveset({"<": sp.Lt, ">": sp.Gt, "<=": sp.Le, ">=": sp.Ge}[op](E, 0), x, sp.S.Reals)
    return f"Solve {poly_text(sp.Poly(E, x).all_coeffs())} {shown} 0", lambda it: vals(it)[0] == sol


def mat_text(M, style):
    rows = [[int(v) for v in M.row(i)] for i in range(M.rows)]
    if style == "list":
        return "[" + ", ".join("[" + ", ".join(map(str, rw)) + "]" for rw in rows) + "]"
    if style == "semi":
        return "[" + "; ".join(" ".join(map(str, rw)) for rw in rows) + "]"
    return r"$\begin{bmatrix}" + r"\\".join("&".join(map(str, rw)) for rw in rows) + r"\end{bmatrix}$"


def g_matrix(r):
    A = sp.Matrix(2, 2, lambda i, j: r.randint(-7, 9))
    while A.det() == 0:
        A = sp.Matrix(2, 2, lambda i, j: r.randint(-7, 9))
    B = sp.Matrix(2, 2, lambda i, j: r.randint(-7, 9))
    st = r.choice(["list", "semi", "latex"])
    kind = r.choice(["inv", "det", "mul", "add", "sub", "adj", "tr"])
    At, Bt = mat_text(A, st), mat_text(B, st)
    if kind == "inv":
        return r.choice([f"Find the inverse of A = {At}", f"If A = {At}, find A^-1 (multiplicative inverse)"]), lambda it: same(vals(it)[0], A.inv())
    if kind == "det":
        return r.choice([f"Find the determinant of A = {At}", f"evaluate the determinant of {At}"]), lambda it: same(vals(it)[0], A.det())
    if kind == "adj":
        return f"Find the adjoint of A = {At}", lambda it: same(vals(it)[0], A.adjugate())
    if kind == "tr":
        return f"Find the transpose of A = {At}", lambda it: same(vals(it)[0], A.T)
    if kind == "mul":
        return r.choice([f"If A = {At} and B = {Bt}, find AB", f"A = {At}, B = {Bt}. Find the product AB"]), lambda it: same(vals(it)[0], A * B)
    if kind == "add":
        return f"If A = {At} and B = {Bt}, find A + B", lambda it: same(vals(it)[0], A + B)
    return f"If A = {At} and B = {Bt}, find A - B", lambda it: same(vals(it)[0], A - B)


def lin_text(a, b, c, style):
    t = (term(a, "x", True) + term(b, "y")) + f" = {c}"
    return t.replace(" ", "") if style == "tight" else t


def g_system(r):
    xs, ys = nz(r, -7, 7), nz(r, -7, 7)
    while True:
        a, b, c, d = (nz(r, -6, 6) for _ in range(4))
        if a * d - b * c:
            break
    st = r.choice(["spaced", "tight"])
    e1, e2 = lin_text(a, b, a * xs + b * ys, st), lin_text(c, d, c * xs + d * ys, st)
    t = r.choice(["Solve {p} and {q}", "Use Cramer's rule to solve: {p}, {q}", "Solve by matrix inversion method {p}, {q}", "find x and y: {p} ; {q}"]).format(p=e1, q=e2)
    return t, lambda it: [sp.nsimplify(v) for v in vals(it)] == [xs, ys]


def g_function(r):
    a, b, c = nz(r, -6, 6), r.randint(-9, 9), r.randint(-5, 5)
    f, gx = a * x + b, x ** 2 + c
    ft, gt = f"{term(a, 'x', True)}{term(b, '')}", f"x^2{term(c, '')}"
    kind = r.choice(["fog", "gof", "inv", "val", "sum", "prod"])
    head = f"If f(x) = {ft} and g(x) = {gt}"
    if kind == "fog":
        return r.choice([f"{head}, find (fog)(x)", f"{head}, find f(g(x))", f"{head} find fog(x)"]), lambda it: same(vals(it)[0], f.subs(x, gx))
    if kind == "gof":
        return f"{head}, find (g o f)(x)", lambda it: same(vals(it)[0], gx.subs(x, f))
    if kind == "inv":
        return r.choice([f"f(x) = {ft}, find f^-1(x)", f"Find the inverse of f(x) = {ft}"]), lambda it: same(f.subs(x, vals(it)[0]), x)
    if kind == "val":
        k = r.randint(-6, 6)
        return f"{head}, find f({k})", lambda it: same(vals(it)[0], f.subs(x, k))
    if kind == "sum":
        return f"{head}, find f(x) + g(x)", lambda it: same(vals(it)[0], f + gx)
    return f"{head}, find f(x) * g(x)", lambda it: same(vals(it)[0], f * gx)


def g_abs(r):
    a, b, k = nz(r, -5, 5), r.randint(-9, 9), r.randint(1, 12)
    inner = f"{term(a, 'x', True)}{term(b, '')}"
    op = r.choice(["=", "=", "<", "<=", ">", ">="])
    E = sp.Abs(a * x + b)
    if op == "=":
        roots = sorted(set(sp.solve(a * x + b - k, x) + sp.solve(a * x + b + k, x)), key=float)
        return f"Solve |{inner}| = {k}", lambda it: sorted(vals(it), key=float) == roots
    sol = sp.solveset({"<": sp.Lt, ">": sp.Gt, "<=": sp.Le, ">=": sp.Ge}[op](E, k), x, sp.S.Reals)
    return f"Solve and show on number line: |{inner}| {op} {k}", lambda it: vals(it)[0] == sol


def g_fraction(r):
    p, q_, s = r.sample([v for v in range(-7, 8) if v], 3)
    kind = r.choice(["reduce", "add", "sub"])
    if kind == "reduce":
        n, d = sp.expand((x - p) * (x - q_)), sp.expand((x - p) * (x - s))
        E = n / d
        t = f"({sp.sstr(n).replace('**', '^').replace('*', '')})/({sp.sstr(d).replace('**', '^').replace('*', '')})"
        return r.choice([f"Reduce to lowest form: {t}", f"simplify {t}"]), lambda it: same(vals(it)[0], E)
    k1, k2 = r.randint(1, 6), r.randint(1, 6)
    sg = "+" if kind == "add" else "-"
    E = k1 / (x - p) + (1 if sg == "+" else -1) * k2 / (x - q_)
    t = f"{k1}/(x - {p}) {sg} {k2}/(x - {q_})".replace("- -", "+ ")
    return f"Simplify: {t}", lambda it: same(vals(it)[0], E)


def vec_text(a, b):
    return f"{term(a, 'i', True)}{term(b, 'j')}"


def g_vector(r):
    a, b, c, d = (nz(r, -9, 9) for _ in range(4))
    kind = r.choice(["mag", "unit", "combo", "ab"])
    if kind == "mag":
        return r.choice([f"Find the magnitude of a = {vec_text(a, b)}", f"find |v| if v = {vec_text(a, b)}"]), lambda it: same(vals(it)[0], sp.sqrt(a * a + b * b))
    if kind == "unit":
        m = sp.sqrt(a * a + b * b)
        return f"Find a unit vector in the direction of a = {vec_text(a, b)}", lambda it: same(vals(it)[0], a / m) and same(vals(it)[1], b / m)
    if kind == "ab":
        return f"Find the vector AB where A({a}, {b}) and B({c}, {d})", lambda it: [sp.nsimplify(v) for v in vals(it)] == [c - a, d - b]
    k1, k2 = nz(r, -4, 4), nz(r, -4, 4)
    expr = f"{'' if k1 == 1 else '-' if k1 == -1 else k1}a {'+' if k2 > 0 else '-'} {'' if abs(k2) == 1 else abs(k2)}b"
    return f"If a = {vec_text(a, b)} and b = {vec_text(c, d)}, find {expr}", lambda it: [sp.nsimplify(v) for v in vals(it)] == [k1 * a + k2 * c, k1 * b + k2 * d]


def g_trig(r):
    f = r.choice(["sin", "cos", "tan"])
    d = r.choice([30, 45, 60, 120, 135, 150, 210, 225, 240, 300, 315, 330])
    v = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan}[f](sp.pi * d / 180)
    t = r.choice([f"Find the value of {f} {d}°", f"find {f}({d})", f"evaluate {f} {d} degrees without calculator"])
    return t, lambda it: same(vals(it)[0], v)


def g_triangle(r):
    while True:
        a, b, c = r.randint(3, 15), r.randint(3, 15), r.randint(3, 15)
        if a + b > c and a + c > b and b + c > a:
            break
    if r.random() < 0.5:
        s = (a + b + c) / 2
        A = math.sqrt(s * (s - a) * (s - b) * (s - c))
        return f"Find the area of triangle ABC with a = {a} cm, b = {b} cm, c = {c} cm", lambda it: same(vals(it)[0], A, 0.006)
    gm = r.randint(20, 150)
    A = 0.5 * a * b * math.sin(math.radians(gm))
    return f"Calculate the area of triangle ABC in which a = {a}, b = {b}, gamma = {gm}", lambda it: same(vals(it)[0], A, 0.006)


TRIPLES = [(3, 4, 5), (5, 12, 13), (8, 15, 17), (6, 8, 10), (7, 24, 25), (9, 12, 15), (12, 16, 20), (20, 21, 29)]


def g_circle(r):
    d, h, rad = r.choice(TRIPLES)
    kind = r.choice(["chord", "radius", "dist", "tangent", "sector", "theta"])
    if kind == "chord":
        return f"Find the length of a chord which is at a distance of {d} cm from the centre of a circle of radius {rad} cm", lambda it: same(vals(it)[0], 2 * h)
    if kind == "radius":
        return f"A chord {2 * h} cm long is {d} cm from the centre. Find the radius of the circle.", lambda it: same(vals(it)[0], rad)
    if kind == "dist":
        return f"In a circle of radius {rad} cm, a chord is {2 * h} cm long. Find the distance of the chord from the centre.", lambda it: same(vals(it)[0], d)
    if kind == "tangent":
        return f"A point is {rad} cm away from the centre of a circle of radius {d} cm. Find the length of the tangent.", lambda it: same(vals(it)[0], h)
    rr = r.randint(2, 20)
    if kind == "sector":
        th = sp.Rational(r.randint(1, 30), 10)
        return f"Find the arc length and sector area if r = {rr} cm and theta = {float(th):g} radians", \
            lambda it: same(vals(it)[0], rr * th) and same(vals(it)[1], sp.Rational(1, 2) * rr ** 2 * th)
    l = r.randint(1, 40)
    return f"Find theta if arc length l = {l} cm and radius r = {rr} cm", lambda it: same(vals(it)[0], sp.Rational(l, rr))


def g_stats(r):
    data = [r.randint(5, 95) for _ in range(r.randint(5, 9))]
    kind = r.choice(["sd", "range", "mean", "median"])
    lst = ", ".join(map(str, data))
    if kind == "sd":
        m = Fraction(sum(data), len(data))
        var = sum((Fraction(v) - m) ** 2 for v in data) / len(data)
        return r.choice([f"Find the variance and standard deviation of {lst}", f"standard deviation of the data: {lst}"]), \
            lambda it: same(vals(it)[1], sp.Rational(var.numerator, var.denominator))
    if kind == "range":
        return f"Find the range of {lst}", lambda it: same(vals(it)[0], max(data) - min(data))
    if kind == "mean":
        return f"Find the mean of {lst}", lambda it: same(vals(it)[0], sp.Rational(sum(data), len(data)))
    d = sorted(data)
    n = len(d)
    pos = sp.Rational(n + 1, 2)
    lo = int(pos)
    med = d[lo - 1] + (pos - lo) * (d[min(lo, n - 1)] - d[lo - 1])
    return f"Find the median and quartiles of {lst}", lambda it: same(vals(it)[0], med)


def g_prob(r):
    kind = r.choice(["dice_sum", "dice_prod", "dice_even", "coins", "die", "bag"])
    space2 = list(itertools.product(range(1, 7), repeat=2))
    if kind == "dice_sum":
        k = r.randint(2, 12)
        p = Fraction(sum(a + b == k for a, b in space2), 36)
        return r.choice([f"Two dice are rolled. Find the probability of getting a sum of {k}", f"two dice thrown, probability that the sum is {k}"]), \
            lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))
    if kind == "dice_prod":
        k = r.choice([4, 6, 8, 12, 18, 24, 36])
        p = Fraction(sum(a * b == k for a, b in space2), 36)
        return f"Two dice are rolled. What is the probability that the product is {k}?", lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))
    if kind == "dice_even":
        w = r.choice(["even", "odd", "prime"])
        primes = {2, 3, 5, 7, 11}
        p = Fraction(sum({"even": (a + b) % 2 == 0, "odd": (a + b) % 2 == 1, "prime": a + b in primes}[w] for a, b in space2), 36)
        return f"Two dice are rolled, find the probability that the sum is {w}", lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))
    if kind == "coins":
        n = r.choice([2, 3, 4])
        k = r.randint(0, n)
        q = r.choice(["exactly", "at least", "at most"])
        space = list(itertools.product("HT", repeat=n))
        cnt = {"exactly": lambda s: s.count("H") == k, "at least": lambda s: s.count("H") >= k, "at most": lambda s: s.count("H") <= k}[q]
        p = Fraction(sum(cnt(s) for s in space), len(space))
        word = {2: "two", 3: "three", 4: "four"}[n]
        return f"{word.capitalize()} coins are tossed. Find the probability of getting {q} {k} heads", lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))
    if kind == "die":
        k = r.randint(1, 5)
        p = Fraction(sum(v > k for v in range(1, 7)), 6)
        return f"A die is rolled. Find the probability of getting a number greater than {k}", lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))
    cols = r.sample(["red", "white", "green", "black", "blue"], 3)
    ns = [r.randint(1, 9) for _ in cols]
    pick = r.randrange(3)
    neg = r.random() < 0.3
    k = sum(ns) - ns[pick] if neg else ns[pick]
    p = Fraction(k, sum(ns))
    desc = ", ".join(f"{n} {c}" for n, c in zip(ns, cols))
    return f"A bag contains {desc} balls. A ball is drawn at random. Find the probability that it is {'not ' if neg else ''}{cols[pick]}", \
        lambda it: same(vals(it)[0], sp.Rational(p.numerator, p.denominator))


def g_complex(r):
    a, b, c, d = (nz(r, -9, 9) for _ in range(4))
    op = r.choice(["+", "-", "*", "/"])
    z1, z2 = a + b * sp.I, c + d * sp.I
    v = {"+": z1 + z2, "-": z1 - z2, "*": z1 * z2, "/": z1 / z2}[op]
    t = f"({a}{'+' if b > 0 else '-'}{abs(b)}i) {op} ({c}{'+' if d > 0 else '-'}{abs(d)}i)"
    return f"Simplify {t}", lambda it: _complex_ok(it, v)


def _complex_ok(it, v):
    """Read 'a + bi' from the displayed answer (LaTeX) and compare with the true value."""
    import mathtext
    ans = it["parts"][0]["answer"].replace("$", "")
    py = mathtext.latex_to_py(ans) if "\\" in ans else ans
    py = re.sub(r"(\d|\))\s*i\b", r"\1*I", py)
    py = re.sub(r"(?<![A-Za-z*])i\b", "I", py)
    try:
        got = sp.sympify(py, locals={"I": sp.I, "sqrt": sp.sqrt})
    except Exception:
        return False
    return same(got, v)


TYPES = {"quadratic equation": g_quadratic, "fractional equation": g_rational_eq, "nature of roots": g_nature, "equation from roots": g_form,
         "quadratic inequality": g_ineq, "matrix operations": g_matrix, "linear system": g_system, "functions": g_function, "absolute value": g_abs,
         "algebraic fractions": g_fraction, "vectors": g_vector, "trig exact values": g_trig, "triangle area": g_triangle, "circles": g_circle,
         "statistics": g_stats, "probability": g_prob, "complex numbers": g_complex}

A3 = sp.Matrix([[1, 2, 3], [0, 1, 4], [5, 6, 0]])
# outside the book's types: each must be declined, or answered correctly (never answered wrongly)
TRAPS = [("Solve x^3 - 6x^2 + 11x - 6 = 0", lambda it: sorted(vals(it), key=float) == [1, 2, 3]),
         ("Find the inverse of [[1,2,3],[0,1,4],[5,6,0]]", lambda it: same(vals(it)[0], A3.inv())),
         ("what is the capital of France", lambda it: False), ("solve sin x = 2", lambda it: False),
         ("Find the probability that it rains tomorrow", lambda it: False), ("simplify the poem", lambda it: False),
         ("Solve x^2 + 1 = 0 in real numbers please", lambda it: vals(it) == [] and "no real" in it["parts"][0]["answer"]), ("2 + 2", lambda it: False)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=10, help="questions per type")
    ap.add_argument("--seed", type=int, default=2026)
    args = ap.parse_args()
    sys.stdout.reconfigure(encoding="utf-8")
    import server
    client = server.app.test_client()
    fails, rows = [], []
    t0 = time.time()
    for name, gen in TYPES.items():
        r = random.Random(f"{args.seed}-{name}")
        asked = solved = right = via_server = 0
        for _ in range(args.n):
            q, ok = gen(r)
            asked += 1
            it = engine10.solve(q)
            if not it:
                fails.append(f"NOT SOLVED [{name}] {q}")
                continue
            solved += 1
            try:
                good = ok(it)
            except Exception as exc:
                good = False
                q += f"  (oracle error {exc})"
            if good:
                right += 1
            else:
                fails.append(f"WRONG [{name}] {q}  ->  {it['parts'][0]['answer'][:120]}  values={it['parts'][0].get('values')}")
            if asked % 3 == 1:                                  # every third question also goes through the real server
                d = client.post("/api/answer", json={"question": q, "class": 10}).get_json()
                if d.get("mode") == "solved" and d["item"]["parts"]:
                    via_server += 1
                elif d.get("mode") == "book" and server.really_same(q, server.data("10")["by_id"][d["item"]["id"]], None if not d["item"].get("part_label") else
                                                                     next(i for i, p in enumerate(server.data("10")["by_id"][d["item"]["id"]]["parts"])
                                                                          if (p.get("label") or str(i + 1)) == d["item"]["part_label"])):
                    via_server += 1                             # genuinely the book's own question: its checked solution is shown
                else:
                    fails.append(f"SERVER [{name}] {q} -> mode {d.get('mode')}")
        rows.append((name, asked, solved, right, via_server))
        if solved < 0.95 * asked:
            fails.append(f"COVERAGE [{name}] only {solved}/{asked} solved")
    trap_bad = []
    for q, ok in TRAPS:
        it = engine10.solve(q)
        if it:
            try:
                good = ok(it)
            except Exception:
                good = False
            if not good:
                trap_bad.append(f"{q} -> {it['parts'][0]['answer'][:60]}")
    for tb in trap_bad:
        fails.append(f"TRAP answered wrongly: {tb}")

    print(f"{'type':24} {'asked':>6} {'solved':>7} {'right':>6} {'server':>7}")
    for name, a, s, rt, sv in rows:
        print(f"{name:24} {a:6d} {s:7d} {rt:6d} {sv:7d}")
    tot = [sum(r_[k] for r_ in rows) for k in (1, 2, 3)]
    print(f"{'TOTAL':24} {tot[0]:6d} {tot[1]:7d} {tot[2]:6d}   traps declined or right: {len(TRAPS) - len(trap_bad)}/{len(TRAPS)}   ({time.time() - t0:.0f}s)")
    wrong = [f for f in fails if f.startswith(("WRONG", "TRAP"))]
    if fails:
        print(f"\n{len(fails)} problems:")
        for f in fails[:80]:
            print("  -", f)
    if fails:
        sys.exit(1)
    print("any question: all tests passed (0 wrong)")


if __name__ == "__main__":
    main()
