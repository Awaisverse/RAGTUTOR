"""Synthetic Class 11 (Unit 1, Complex Numbers) items with NEW numbers, solved by the Class 11 engine (engine11), whose
templates wrote the book. Every step of every item is checked with sympy before it is kept.

    generate(per_type, seed0=0, avoid=()) -> list of items like the book's
"""
import pathlib
import random
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "train"))

import sympy as sp  # noqa: E402

import engine11  # noqa: E402
from synth10 import all_checks_pass  # noqa: E402

I = sp.I
Z = sp.Symbol("z")


def _c(z):
    a, b = int(sp.re(z)), int(sp.im(z))
    if b == 0:
        return f"{a}"
    if a == 0:
        return f"{b}i"
    return f"{a}{'+' if b >= 0 else '-'}{abs(b)}i"


def t_sqrt(r):
    p, q = r.randint(-9, 9), r.randint(1, 9)
    w = sp.expand((p + q * I) ** 2)
    return f"Find the square roots of {_c(w)}" if sp.im(w) else None


def t_xy(r):
    p, q = r.randint(1, 9), r.randint(1, 9)
    return f"Find the real values of x and y if (x+iy)^2 = {_c(sp.expand((p + q * I) ** 2))}"


def t_quad(r):
    a = r.choice([1, 1, 2, 3])
    h, k = r.randint(-6, 6), r.randint(1, 6)
    b, c = -2 * a * h, a * (h * h + k * k)
    return f"Solve {a if a > 1 else ''}z^2 {'+' if b >= 0 else '-'} {abs(b)}z + {c} = 0 by completing square method"


def t_factor2(r):
    h, k = r.randint(-6, 6), r.randint(1, 6)
    b, c = -2 * h, h * h + k * k
    return f"Factorize z^2 {'+' if b >= 0 else '-'} {abs(b)}z + {c}"


def t_quartic(r):
    m, n = r.randint(1, 6), r.randint(1, 7)
    poly = sp.expand((Z ** 2 - m * m) * (Z ** 2 + n * n))
    return "Factorize " + sp.sstr(poly).replace("**", "^").replace("*", "") + " into linear factors"


def t_cubic(r):
    a, n = r.randint(-5, 5), r.randint(1, 6)
    poly = sp.expand((Z - a) * (Z ** 2 + n * n))
    return "Solve " + sp.sstr(poly).replace("**", "^").replace("*", "") + " = 0"


def t_cube(r):
    c = r.randint(2, 7) * r.choice([1, -1])
    return f"Find the three cube roots of {c ** 3}"


def t_fourth(r):
    return f"Find the four fourth roots of {r.randint(2, 7) ** 4}"


def t_polar(r):
    k = r.randint(1, 6)
    z = sp.expand(k * r.choice([1 + I, 1 - I, -1 + I, -1 - I, I, -I, 1, -1]))
    return f"Express {_c(z)} in polar form"


def t_inverse(r):
    a, b = r.randint(-9, 9), r.randint(1, 9) * r.choice([1, -1])
    return f"Find the multiplicative inverse of ({a}, {b})"


def t_zeros(r):
    a, n = r.randint(-4, 4), r.randint(1, 4)
    at = r.choice([v for v in range(-3, 4) if v != a])
    k = r.choice([1, 2, 3, -1, -2])
    val = k * (at - a) * (at * at + n * n)
    return f"Find a polynomial P(z) of degree 3 with zeros {a}, {n}i, -{n}i and satisfying P({at}) = {val}"


def t_arith(r):
    z1, z2 = r.randint(-9, 9) + r.randint(-9, 9) * I, r.randint(1, 9) + r.randint(1, 9) * I
    return f"Simplify ({_c(z1)})/({_c(z2)})"


X_ = sp.Symbol("x")


def _q(e):
    return sp.sstr(sp.expand(e)).replace("**", "^").replace("*", "")


def t_maxmin(r):                                      # Unit 3
    a = r.choice([1, 2, 3, -1, -2])
    return f"Find the maximum or minimum value of f(x) = {_q(a * X_**2 + r.randint(-12, 12) * X_ + r.randint(-15, 15))} by completing square"


def t_sketch(r):
    a = r.choice([1, -1])
    h, k = r.randint(-4, 4), r.randint(-6, 6)
    return f"Sketch f(x) = {_q(a * (X_ - h)**2 + k)}. Find its maximum or minimum point, domain and range"


def t_qinverse(r):
    a, h, k = r.choice([1, 2, 3]), r.randint(-5, 5), r.randint(-9, 9)
    return f"Find the inverse of f(x) = {_q(a * (X_ - h)**2 + k)}, x {r.choice(['>=', '<='])} {h}. Also find domain and range"


def t_absq(r):
    return f"Solve |{_q(X_**2 - r.randint(1, 6)**2)}| = {r.randint(1, 20)}"


TYPES = {"square roots": t_sqrt, "x and y from a square": t_xy, "completing the square": t_quad, "factorize quadratic": t_factor2,
         "quartic factors": t_quartic, "cubic equation": t_cubic, "cube roots": t_cube, "fourth roots": t_fourth, "polar form": t_polar,
         "inverse of a pair": t_inverse, "polynomial from zeros": t_zeros, "division": t_arith,
         "maximum or minimum": t_maxmin, "sketch a parabola": t_sketch, "inverse of a quadratic": t_qinverse, "absolute value equation": t_absq}


def generate(per_type, seed0=0, avoid=()):
    out, seen = [], set(avoid)
    for name, gen in TYPES.items():
        rng = random.Random(f"synth11-{seed0}-{name}")
        made = tries = 0
        slug = name.replace(" ", "-")
        while made < per_type and tries < per_type * 20:
            tries += 1
            q = gen(rng)
            if not q or q in seen:
                continue
            it = engine11.solve(q)
            if not it or not all_checks_pass(it):
                continue
            seen.add(q)
            it = dict(it, id=f"syn11-{slug}-{seed0}-{made}", kind="synthetic", unit=1, unit_title="Complex Numbers")
            out.append(it)
            made += 1
    return out


if __name__ == "__main__":
    items = generate(int(sys.argv[1]) if len(sys.argv) > 1 else 3)
    print(len(items), "items over", len(TYPES), "types")
    for it in items[:: max(1, len(items) // 6)]:
        print(" ", it["question"], "->", it["parts"][0]["answer"][:80])
