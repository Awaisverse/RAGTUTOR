"""Generators of NEW Exercise 1.2 style questions: each returns (typed text, LaTeX text, correct values from sympy) or None.

Shared by tests/test_ex12.py (accuracy of the engine) and train/engine_data.py (training data for the model).
The correct values come from sympy directly, never from the engine.
"""
import sympy as sp

R = sp.Rational
SQ = lambda n: sp.sqrt(n)  # noqa: E731
X, Y, Z = (sp.Symbol(c, positive=True) for c in "xyz")
NONSQ = [2, 3, 5, 6, 7, 10, 11, 13]


def sgn(s):
    return "+" if s > 0 else "-"


# ------------------------------------------------------------------------------------------------ Q1 rationalize
def g_rat_binomial(rng):
    a, p, r, s = rng.randint(1, 15), rng.randint(1, 9), rng.choice(NONSQ), rng.choice([1, -1])
    return (f"rationalize {a}/({p}{sgn(s)}sqrt{r})", rf"Rationalize the denominator of $\frac{{{a}}}{{{p}{sgn(s)}\sqrt{{{r}}}}}$.", [a / (p + s * SQ(r))])


def g_rat_single(rng):
    a, b, c = rng.sample(NONSQ, 3)
    s = rng.choice([1, -1])
    return (f"rationalize (sqrt{a}{sgn(s)}sqrt{b})/sqrt{c}", rf"Rationalize the denominator of $\frac{{\sqrt{{{a}}}{sgn(s)}\sqrt{{{b}}}}}{{\sqrt{{{c}}}}}$.", [(SQ(a) + s * SQ(b)) / SQ(c)])


def g_rat_conjugate_pair(rng):
    a, b, c = rng.randint(2, 9), rng.randint(1, 6), rng.choice(NONSQ)
    return (f"rationalize ({a}-{b}sqrt{c})/({a}+{b}sqrt{c})", rf"Rationalize the denominator of $\frac{{{a}-{b}\sqrt{{{c}}}}}{{{a}+{b}\sqrt{{{c}}}}}$.", [(a - b * SQ(c)) / (a + b * SQ(c))])


def g_rat_two_roots(rng):
    a, b = rng.sample(NONSQ, 2)
    return (f"rationalize (sqrt{a}-sqrt{b})/(sqrt{a}+sqrt{b})", rf"Rationalize the denominator of $\frac{{\sqrt{{{a}}}-\sqrt{{{b}}}}}{{\sqrt{{{a}}}+\sqrt{{{b}}}}}$.", [(SQ(a) - SQ(b)) / (SQ(a) + SQ(b))])


def g_rat_coefficient(rng):
    d, e, f, g = rng.randint(2, 6), rng.choice(NONSQ), *rng.sample(NONSQ, 2)
    return (f"rationalize {d}sqrt{e}/(sqrt{f}+sqrt{g})", rf"Rationalize the denominator of $\frac{{{d}\sqrt{{{e}}}}}{{\sqrt{{{f}}}+\sqrt{{{g}}}}}$.", [d * SQ(e) / (SQ(f) + SQ(g))])


# ------------------------------------------------------------------------------------------------ Q2 / Q5 numeric powers
def g_pow_fraction(rng):
    u, v, q, p = *rng.sample([2, 3, 4, 5], 2), rng.choice([2, 3, 4]), rng.randint(1, 3)
    return (f"simplify ({u ** q}/{v ** q})^(-{p}/{q})", rf"Simplify $\left(\frac{{{u ** q}}}{{{v ** q}}}\right)^{{-\frac{{{p}}}{{{q}}}}}$.", [R(v, u) ** p])


def g_pow_chain(rng):
    a, b, c, d = rng.sample([2, 3, 4, 5, 7], 2) + rng.sample([2, 3, 4, 5, 7], 2)
    m, k = rng.randint(1, 3), rng.randint(1, 3)
    e, f = rng.sample([2, 3, 5, 7, 9], 2)
    return (f"({a}/{b})^(-{m}) / ({c}/{d})^{k} * {e}/{f}", rf"Simplify $\left(\frac{{{a}}}{{{b}}}\right)^{{-{m}}} \div \left(\frac{{{c}}}{{{d}}}\right)^{{{k}}} \times \frac{{{e}}}{{{f}}}$.",
            [R(b, a) ** m / R(c, d) ** k * R(e, f)])


def g_pow_quotient(rng):
    x, q1, p1, y, q2, p2 = rng.randint(2, 5), rng.choice([2, 3]), rng.randint(1, 3), rng.randint(2, 5), rng.choice([2, 3]), rng.randint(1, 3)
    return (f"({x ** q1})^(-{p1}/{q1}) / ({y ** q2})^(-{p2}/{q2})", rf"Simplify $({x ** q1})^{{-\frac{{{p1}}}{{{q1}}}}} \div ({y ** q2})^{{-\frac{{{p2}}}{{{q2}}}}}$.",
            [R(x) ** -p1 / R(y) ** -p2])


def g_pow_big_fraction(rng):
    (u, q1, p1), (v, q2, p2) = [(rng.randint(2, 4), rng.choice([2, 3, 4]), rng.randint(1, 3)) for _ in range(2)]
    (w, q3, p3), (z, q4, p4) = [(rng.randint(2, 4), rng.choice([2, 3, 4]), rng.randint(1, 3)) for _ in range(2)]
    top = f"({u ** q1})^({p1}/{q1}) * ({v ** q2})^({p2}/{q2})"
    bot = f"({w ** q3})^({p3}/{q3}) * ({z ** q4})^({p4}/{q4})"
    gold = R(u) ** p1 * R(v) ** p2 / (R(w) ** p3 * R(z) ** p4)
    tex = lambda b, q, p: rf"({b ** q})^{{\frac{{{p}}}{{{q}}}}}"  # noqa: E731
    return (f"simplify ({top}) / ({bot})", rf"Simplify $\frac{{{tex(u, q1, p1)} \times {tex(v, q2, p2)}}}{{{tex(w, q3, p3)} \times {tex(z, q4, p4)}}}$.", [gold])


# ------------------------------------------------------------------------------------------------ Q2 symbolic exponent
def g_pow_unknown(rng):
    p = rng.choice([2, 3, 5])
    k = rng.choice([1, 2])                     # bases p and p**k
    A_ = rng.choice([2, 4]) if k == 2 else rng.choice([1, 2, 3])
    # every term is c * B^(m n + d) with k*m = A_ so that all terms share the power p^(A_ n)
    def term(rng):
        kk = rng.choice([1, 2]) if A_ % 2 == 0 else 1
        m = A_ // kk
        return rng.randint(1, 6), p ** kk, m, rng.randint(0, 3)

    def build(terms):
        asc, lat, val = [], [], 0
        for i, (c, B, m, d) in enumerate(terms):
            sign = rng.choice([1, -1]) if i else 1
            exp_a = f"{m}n+{d}" if m != 1 else f"n+{d}"
            asc.append((("+" if sign > 0 else "-") if i else "") + f"{c}*{B}^({exp_a})")
            lat.append((("+" if sign > 0 else "-") if i else "") + rf"{c}\times {B}^{{{exp_a}}}")
            val += sign * c * R(p) ** (sp.log(B, p) * d) * 1
        return "".join(asc), "".join(lat)

    n_terms, d_terms = [term(rng) for _ in range(rng.choice([1, 2]))], [term(rng) for _ in range(rng.choice([1, 2]))]
    n = sp.Symbol("n", positive=True)
    signs_n = [1] + [rng.choice([1, -1]) for _ in n_terms[1:]]
    signs_d = [1] + [rng.choice([1, -1]) for _ in d_terms[1:]]

    def render(terms, signs):
        asc, lat, expr = "", "", 0
        for i, ((c, B, m, d), s) in enumerate(zip(terms, signs)):
            ex = (f"{m}n" if m != 1 else "n") + (f"+{d}" if d else "")
            lead = ("+" if s > 0 else "-") if i else ("" if s > 0 else "-")
            asc += lead + f"{c}*{B}^({ex})"
            lat += lead + rf"{c}\times {B}^{{{ex}}}"
            expr += s * c * B ** (m * n + d)
        return asc, lat, expr
    na, nl, ne = render(n_terms, signs_n)
    da, dl, de = render(d_terms, signs_d)
    ratio = sp.simplify(ne / de)
    if ratio.free_symbols or ratio == 0 or de.subs(n, 1) == 0 or sp.simplify(de.subs(n, 2)) == 0:
        return None
    return (f"simplify ({na})/({da})", rf"Simplify $\frac{{{nl}}}{{{dl}}}$.", [ratio])


def g_var_root(rng):
    m = rng.choice([2, 3, 5, 7])
    a, b, c = rng.randint(1, 3), rng.randint(1, 3), rng.randint(1, 3)
    d, e = rng.randint(1, 6), rng.randint(1, 6)
    k = rng.choice([1, 1, 2, 3])                # a numeric coefficient k^m in front: it must NOT be dropped
    ex, ey, ez = a * m, b * m + d, c * m + e
    coef_asc, coef_lat = (f"{k ** m}*", rf"{k ** m}\times ") if k > 1 else ("", "")
    asc = f"({coef_asc}x^{ex}*y^{ey}*z^{ez}/(y^{d}*z^{e}))^(1/{m})"
    lat = rf"\sqrt[{m}]{{\frac{{{coef_lat}x^{{{ex}}}\times y^{{{ey}}}\times z^{{{ez}}}}}{{y^{{{d}}}z^{{{e}}}}}}}"
    return (f"simplify {asc}", rf"Simplify ${lat}$.", [k * X ** a * Y ** b * Z ** c])


def g_cube(rng):
    a, b = rng.choice(["a", "p", "m"]), rng.choice(["b", "q", "k"])
    ea, eb = rng.choice([1, 2]), rng.choice([1, 2])
    A_, B_ = sp.Symbol(a, positive=True), sp.Symbol(b, positive=True)
    u, w = A_ ** R(1, 3) ** 1 * 1, B_ ** R(eb, 3)
    u = A_ ** R(ea, 3)
    s = rng.choice([1, -1])
    first = f"{a}^({ea}/3){sgn(s)}{b}^({eb}/3)"
    second = f"{a}^({2 * ea}/3){'-' if s > 0 else '+'}{a}^({ea}/3)*{b}^({eb}/3)+{b}^({2 * eb}/3)"
    gold = A_ ** ea + s * B_ ** eb
    lat = rf"\left({a}^{{\frac{{{ea}}}{{3}}}}{sgn(s)}{b}^{{\frac{{{eb}}}{{3}}}}\right)\times\left({a}^{{\frac{{{2 * ea}}}{{3}}}}{'-' if s > 0 else '+'}{a}^{{\frac{{{ea}}}{{3}}}}{b}^{{\frac{{{eb}}}{{3}}}}+{b}^{{\frac{{{2 * eb}}}{{3}}}}\right)"
    return (f"simplify ({first})*({second})", rf"Simplify ${lat}$.", [gold])


# ------------------------------------------------------------------------------------------------ Q3 value of x, Q4 find p q
def g_value_of_x(rng):
    a, b = rng.randint(2, 7), rng.choice([2, 3, 5, 6, 7, 8, 10])
    if a * a - b in (0, 1, -1) or a * a < b:
        return None
    xv = a + SQ(b)
    targets = rng.sample([("x+1/x", rf"x+\frac{{1}}{{x}}", xv + 1 / xv), ("x-1/x", rf"x-\frac{{1}}{{x}}", xv - 1 / xv),
                          ("x^2+1/x^2", rf"x^2+\frac{{1}}{{x^2}}", xv ** 2 + 1 / xv ** 2), ("x^2-1/x^2", rf"x^2-\frac{{1}}{{x^2}}", xv ** 2 - 1 / xv ** 2),
                          ("x^4+1/x^4", rf"x^4+\frac{{1}}{{x^4}}", xv ** 4 + 1 / xv ** 4), ("(x-1/x)^2", rf"\left(x-\frac{{1}}{{x}}\right)^2", (xv - 1 / xv) ** 2)], rng.randint(2, 4))
    asc = f"If x = {a}+sqrt{b} then find the value of: " + " ".join(f"({lab}) {t[0]}" for lab, t in zip(["i", "ii", "iii", "iv"], targets))
    lat = rf"If $x = {a}+\sqrt{{{b}}}$ then find the value of: " + " ".join(f"({lab}) ${t[1]}$" for lab, t in zip(["i", "ii", "iii", "iv"], targets))
    return asc, lat, [t[2] for t in targets]


def g_find_pq(rng):
    a, b, c = rng.randint(1, 9), rng.randint(1, 5), rng.choice([2, 3, 5, 6, 7])
    d, e = rng.randint(1, 9), rng.randint(1, 5)
    if d * d - e * e * c == 0:
        return None
    res = sp.radsimp((a - b * SQ(c)) / (d + e * SQ(c)))
    p = sp.simplify(res.subs(SQ(c), 0))
    q = sp.simplify((res - p) / SQ(c))
    return (f"find the rational numbers p and q such that ({a}-{b}sqrt{c})/({d}+{e}sqrt{c}) = p+q*sqrt{c}",
            rf"Find the rational numbers $p$ and $q$ such that $\frac{{{a}-{b}\sqrt{{{c}}}}}{{{d}+{e}\sqrt{{{c}}}}} = p+q\sqrt{{{c}}}$.", [p, q])


GENERATORS = {
    "Q1 a/(p+sqrt r)": g_rat_binomial, "Q1 (sqrt a +- sqrt b)/sqrt c": g_rat_single, "Q1 (a-b sqrt c)/(a+b sqrt c)": g_rat_conjugate_pair,
    "Q1 (sqrt a - sqrt b)/(sqrt a + sqrt b)": g_rat_two_roots, "Q1 d sqrt e/(sqrt f + sqrt g)": g_rat_coefficient,
    "Q2 (u^q/v^q)^(-p/q)": g_pow_fraction, "Q2 chain of powers": g_pow_chain, "Q2 a^(-p/q) / b^(-r/s)": g_pow_quotient,
    "Q2 powers with unknown n": g_pow_unknown, "Q2 root of x,y,z powers": g_var_root,
    "Q3 x = a + sqrt b": g_value_of_x, "Q4 find p and q": g_find_pq,
    "Q5 fraction of fractional powers": g_pow_big_fraction, "Q5 (u+w)(u^2-uw+w^2)": g_cube,
}
