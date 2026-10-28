"""General step templates for Class 10 (Units 2-12). Every computed line carries a sympy check.

Expressions are written once, in sympy syntax (x**2 - 3*x + 2), and shown on the board as LaTeX made from that same text,
so the line a student sees is exactly the line that was checked.

  tex(s)            LaTeX of a sympy-syntax string, kept in the order written (not re-sorted)
  eq_chain(lines)   a chain of equations; each line is checked to be the previous one times a constant or a polynomial
                    (so "cross-multiply", "multiply both sides by 2" and "rearrange" are all verified)
  q_* helpers       full quadratic-equation solutions (factorization, completing the square, formula, graph)
  graph(...)        drawing commands for a graph on the board (axes, curves, labelled points)

Check strings are evaluated by tools/build_dataset.verify, where single letters are positive symbols and R is Rational.
Names that sympy reserves (S, N, Q, O, E, I, C) must not be used as variables in checks: use two-letter names instead.
"""
import math
import re

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr

from _helpers import P, S, T

R = sp.Rational
_LETTERS = "abcdfghjklmnpqrstuvwxyz"
LOC = {c: sp.Symbol(c) for c in _LETTERS}
LOC.update({"R": R, "sqrt": sp.sqrt, "pi": sp.pi, "I": sp.I, "Abs": sp.Abs, "Rational": R})
X = LOC["x"]


def ex(s):
    """A sympy expression from a string (evaluated) or a value."""
    return sp.sympify(s, locals=LOC) if isinstance(s, str) else sp.sympify(s)


def _clean(t):
    t = re.sub(r"(?<![\w}.])1 \\frac\{1\}", r"\\frac{1}", t)          # 1 \frac{1}{x-1}  ->  \frac{1}{x-1}
    t = re.sub(r"- 1 \\frac\{1\}", r"- \\frac{1}", t)
    t = t.replace(r"\cdot", r"\times") if r"\cdot \left(" in t else t
    t = re.sub(r"\+ -", "- ", t)
    return t


def tex(s):
    """LaTeX of a sympy-syntax string in the order written; a sympy value is printed normally."""
    if not isinstance(s, str):
        return sp.latex(s)
    e = parse_expr(s, evaluate=False, local_dict=LOC)
    return _clean(sp.latex(e, order="none"))


def ps(v):
    """A value as a parenthesised sympy string for checks."""
    return "(" + sp.sstr(sp.sympify(v)) + ")"


def num(v):
    return sp.latex(sp.nsimplify(v) if isinstance(v, float) else sp.sympify(v))


def split_eq(line):
    """'lhs = rhs' -> (lhs, rhs). '<=' '>=' are not equations."""
    m = re.split(r"(?<![<>=!])=(?!=)", line)
    if len(m) != 2:
        raise ValueError(f"not an equation: {line!r}")
    return m[0].strip(), m[1].strip()


def eq_tex(line):
    l, r = split_eq(line)
    return f"{tex(l)} = {tex(r)}"


def diff(line):
    l, r = split_eq(line)
    return ex(l) - ex(r)


# ------------------------------------------------------------------------------------------ explanations

EXPLAIN = {
    "same": ("Simplify and rearrange the terms.", "ارکان کو سادہ کر کے ترتیب دیں۔"),
    "move": ("Move all the terms to one side.", "تمام ارکان کو ایک طرف لے جائیں۔"),
    "expand": ("Multiply out the brackets.", "قوسین کھول کر ضرب دیں۔"),
    "const": ("Multiply (or divide) both sides by the same number.", "دونوں اطراف کو ایک ہی عدد سے ضرب (یا تقسیم) دیں۔"),
    "clear": ("Multiply both sides by the denominators (cross-multiply) to clear the fractions.",
              "کسور ختم کرنے کے لیے دونوں اطراف کو نسب نماؤں سے ضرب دیں (کراس ضرب)۔"),
}


def eq_chain(lines, var=None, first_explain=None):
    """Steps for a chain of equations. lines: 'lhs = rhs' strings or (line, en, ur) tuples.
    Line k is accepted only when (lhs_k - rhs_k) = r * (lhs_{k-1} - rhs_{k-1}) with r a non-zero constant or polynomial."""
    steps, prev = [], None
    for k, item in enumerate(lines):
        line, en, ur = (item, None, None) if isinstance(item, str) else (item[0], item[1], item[2])
        l, r = split_eq(line)
        checks = []
        if prev is None:
            en, ur = (en, ur) if en else (first_explain or ("Write the given equation.", "دی گئی مساوات لکھیں۔"))
        else:
            pl, pr = split_eq(prev)
            d0, d1 = ex(pl) - ex(pr), ex(l) - ex(r)
            ratio = sp.cancel(sp.together(d1 / d0)) if d0 != 0 else None
            if ratio is None or ratio == 0:
                raise ValueError(f"line {line!r} does not follow from {prev!r}")
            ok_poly = all(ratio.is_polynomial(s) for s in ratio.free_symbols) if ratio.free_symbols else True
            if not ok_poly:
                raise ValueError(f"line {line!r} is not the previous line times a polynomial (ratio {ratio})")
            if not en:
                if ratio.free_symbols:
                    en, ur = EXPLAIN["clear"]
                elif ratio == 1:
                    en, ur = EXPLAIN["same"]
                else:
                    en, ur = EXPLAIN["const"]
            if ratio == 1:
                checks.append(f"({l}) - ({r}) == ({pl}) - ({pr})")
            else:
                checks.append(f"({l}) - ({r}) == ({sp.sstr(ratio)})*(({pl}) - ({pr}))")
        steps.append(S(eq_tex(line), en, ur, *checks))
        prev = line
    return steps


def roots_line(var, roots, poly_str, en=None, ur=None):
    """'x = r1, x = r2' with a substitution check for each root in the polynomial."""
    v = str(var)
    checks = [f"({poly_str}).subs({v}, {ps(r)}) == 0" for r in roots]
    texs = r",\quad ".join(f"{v} = {tex_root(r)}" for r in roots)
    return S(texs, en or "Each root makes the equation true (put it back to check).",
             ur or "ہر جذر مساوات کو درست کرتا ہے (واپس رکھ کر جانچ لیں)۔", *checks)


def tex_root(r):
    r = sp.nsimplify(r) if isinstance(r, float) else sp.sympify(r)
    if r.is_Rational:
        return sp.latex(r)
    # (p + q sqrt(d)) / s written with the rational part first, as students write it
    r = sp.radsimp(r)
    num_, den = sp.fraction(sp.together(r))
    num_ = sp.expand(num_)
    if den.is_number and den < 0:
        num_, den = -num_, -den
    const = num_.as_independent(sp.Pow, as_Add=True)[0] if num_.is_Add else (num_ if num_.is_Rational else 0)
    surd = sp.expand(num_ - const)
    st = sp.latex(surd)
    body = (sp.latex(const) + (" " if st.startswith("-") else " + ") + st) if const != 0 else st
    return body if den == 1 else rf"\frac{{{body}}}{{{sp.latex(den)}}}"


def sset(roots):
    return r"\{" + ", ".join(tex_root(r) for r in roots) + r"\}"


def order_roots(roots):
    roots = [sp.nsimplify(r) for r in roots]
    if all(r.is_Rational for r in roots):
        return sorted(set(roots))
    return sorted(set(roots), key=lambda r: -float(r))          # surds: the + root first


# ------------------------------------------------------------------------------------------ quadratics


def _poly_str(p, var=X):
    return sp.sstr(sp.expand(p))


def standard_form(eq, var=X, show_first=True):
    """Steps that bring 'lhs = rhs' to a x^2 + b x + c = 0 (a > 0, whole-number coefficients with no common factor).
    Returns (steps, poly)."""
    l, r = split_eq(eq)
    L, Rr = ex(l), ex(r)
    lines = [eq] if show_first else []
    nl, dl = sp.fraction(sp.together(L))
    nr, dr = sp.fraction(sp.together(Rr))
    cur_l, cur_r = l, r
    if dl != 1 or dr != 1:
        if L.is_Add and dl != 1 and len(L.args) > 1 and any(sp.fraction(a)[1] != 1 for a in L.args):
            lines.append((f"({sp.sstr(nl)})/({sp.sstr(dl)}) = {r}", "Add the fractions on the left over a common denominator.",
                          "بائیں طرف کی کسور کو مشترک نسب نما پر جمع کریں۔"))
        if sp.gcd(dl, dr).free_symbols:
            lcd = sp.lcm(dl, dr)
            ml, mr = sp.cancel(lcd / dl), sp.cancel(lcd / dr)
        else:                                           # no common factor: cross-multiply, keeping the denominators as written
            lcd, ml, mr = dl * dr, dr, dl

        def _times(n_, m_):
            if m_ == 1:
                return sp.sstr(n_)
            if n_ == 1:
                return sp.sstr(m_)
            return f"({sp.sstr(n_)})*({sp.sstr(m_)})"
        cur_l, cur_r = _times(nl, ml), _times(nr, mr)
        en_ur = EXPLAIN["clear"] if (ml != 1 and mr != 1) else (f"Multiply both sides by ${sp.latex(lcd)}$ to clear the fractions.",
                                                               f"کسور ختم کرنے کے لیے دونوں اطراف کو ${sp.latex(lcd)}$ سے ضرب دیں۔")
        lines.append((f"{cur_l} = {cur_r}", *en_ur))
    el, er = sp.expand(ex(cur_l)), sp.expand(ex(cur_r))
    if sp.sstr(el) != cur_l.strip() or sp.sstr(er) != cur_r.strip():
        lines.append((f"{sp.sstr(el)} = {sp.sstr(er)}", *EXPLAIN["expand"]))
    poly = sp.expand(el - er)
    if sp.Poly(poly, var).LC() < 0:
        poly = -poly
    den = sp.ilcm(*[sp.fraction(c)[1] for c in sp.Poly(poly, var).all_coeffs()])
    poly = sp.expand(poly * den)
    g = sp.gcd_list([int(c) for c in sp.Poly(poly, var).all_coeffs()])
    lines.append((f"{_poly_str(poly)} = 0", *EXPLAIN["move"]))
    if den != 1:
        lines[-1] = (lines[-1][0], "Move all terms to one side and multiply by " + str(den) + " to clear the fractions.",
                     "تمام ارکان ایک طرف لے جائیں اور کسور ختم کرنے کے لیے " + str(den) + " سے ضرب دیں۔")
    if g != 1:
        poly = sp.expand(poly / g)
        lines.append((f"{_poly_str(poly)} = 0", f"Divide both sides by {g}.", f"دونوں اطراف کو {g} سے تقسیم کریں۔"))
    # drop consecutive duplicates
    out = []
    for ln in lines:
        key = ln if isinstance(ln, str) else ln[0]
        if out and (out[-1] if isinstance(out[-1], str) else out[-1][0]).replace(" ", "") == key.replace(" ", ""):
            continue
        out.append(ln)
    return eq_chain(out, var), poly


def coeffs(poly, var=X):
    a, b, c = [sp.Integer(0)] * (3 - len(sp.Poly(poly, var).all_coeffs())) + sp.Poly(poly, var).all_coeffs()
    return a, b, c


def _signed(v, first=False):
    v = sp.sympify(v)
    if first:
        return sp.latex(v)
    return ("- " + sp.latex(-v)) if v < 0 else ("+ " + sp.latex(v))


def factor_steps(poly, var=X):
    """Split the middle term, group, factor, and solve. Returns (steps, roots)."""
    a, b, c = coeffs(poly, var)
    v = str(var)
    ps_ = _poly_str(poly)
    steps = []
    if b == 0 and c == 0:
        raise ValueError("degenerate")
    ac = a * c
    pair = None
    for p in sorted({d for d in sp.divisors(abs(ac))} | {-d for d in sp.divisors(abs(ac))}, key=abs) if ac != 0 else [0]:
        q = b - p
        if p * q == ac:
            for (u, w) in ((p, q), (q, p)):
                k1 = sp.gcd(a, u)
                if (a // k1) != 0 and w % (a // k1) == 0:
                    pair = (u, w)
                    break
        if pair:
            break
    if pair is None:
        raise ValueError(f"{poly} does not factor over the integers")
    u, w = pair
    k1 = sp.gcd(a, u)
    A1, B1 = a // k1, u // k1
    k2 = w // A1
    if c != k2 * B1:
        raise ValueError("grouping failed")
    def cx(c_, t_, first=False):
        """A coefficient times a term, written as a student would: x not 1x, - x not -1x."""
        c_ = sp.Integer(c_)
        body = t_ if abs(c_) == 1 else f"{abs(c_)}*{t_}"
        if first:
            return ("-" if c_ < 0 else "") + body
        return (" - " if c_ < 0 else " + ") + body

    def cn(c_):
        return (" - " if c_ < 0 else " + ") + str(abs(c_))
    split = cx(a, f"{v}**2", True) + cx(u, v) + cx(w, v) + cn(c)
    inner = f"({cx(A1, v, True)}{cn(B1)})"
    group = (cx(k1, f"{v}*{inner}", True) if k1 != 1 else f"{v}*{inner}") + cx(k2, inner)
    fac = f"({cx(k1, v, True)}{cn(k2)})*{inner}"
    steps += eq_chain([f"{ps_} = 0",
                       (f"{split} = 0", f"Split the middle term: $({sp.latex(u)}) \\times ({sp.latex(w)}) = {sp.latex(ac)}$ "
                        f"(= $a \\times c$) and $({sp.latex(u)}) + ({sp.latex(w)}) = {sp.latex(b)}$ (= $b$).",
                        f"درمیانی رکن کو توڑیں: $({sp.latex(u)}) \\times ({sp.latex(w)}) = {sp.latex(ac)}$ (= $a \\times c$) اور "
                        f"$({sp.latex(u)}) + ({sp.latex(w)}) = {sp.latex(b)}$ (= $b$)۔"),
                       (f"{group} = 0", "Take out the common factor from each pair.", "ہر جوڑے سے مشترک جزو باہر نکالیں۔"),
                       (f"{fac} = 0", "Take out the common bracket.", "مشترک قوسین باہر نکالیں۔")], var,
                      first_explain=("Start from the standard form.", "معیاری شکل سے شروع کریں۔"))
    f1 = sp.expand(k1 * var + k2)
    f2 = sp.expand(A1 * var + B1)
    roots = sorted({sp.Rational(-k2, k1), sp.Rational(-B1, A1)})
    steps.append(S(rf"{sp.latex(f1)} = 0 \quad\text{{or}}\quad {sp.latex(f2)} = 0",
                   "A product is zero only when one of its factors is zero.", "حاصل ضرب صفر تب ہوتا ہے جب کوئی ایک جزو صفر ہو۔"))
    steps.append(roots_line(var, roots, ps_))
    return steps, roots


def completing_square_steps(poly, var=X):
    a, b, c = coeffs(poly, var)
    v = str(var)
    h = sp.Rational(b, 2 * a)
    k = sp.Rational(b * b - 4 * a * c, 4 * a * a)
    lines = [f"{_poly_str(poly)} = 0",
             (f"{a}*{v}**2 {'+' if b >= 0 else '-'} {abs(b)}*{v} = {-c}", "Move the constant term to the right side.",
              "مستقل رکن کو دائیں طرف لے جائیں۔")]
    bb = sp.Rational(b, a)
    if a != 1:
        lines.append((f"{v}**2 {'+' if bb >= 0 else '-'} {sp.sstr(abs(bb))}*{v} = {sp.sstr(sp.Rational(-c, a))}",
                      f"Divide both sides by {a}, so the coefficient of ${v}^2$ is 1.", f"دونوں اطراف کو {a} سے تقسیم کریں تاکہ ${v}^2$ کا عددی سر 1 ہو۔"))
    lines.append((f"{v}**2 {'+' if bb >= 0 else '-'} {sp.sstr(abs(bb))}*{v} + ({sp.sstr(abs(h))})**2 = {sp.sstr(sp.Rational(-c, a))} + ({sp.sstr(abs(h))})**2",
                  f"Add $\\left(\\frac{{1}}{{2}} \\times \\text{{coefficient of }}{v}\\right)^2 = \\left({sp.latex(abs(h))}\\right)^2$ to both sides.",
                  f"دونوں اطراف میں $\\left({sp.latex(abs(h))}\\right)^2$ جمع کریں (${v}$ کے عددی سر کا آدھا، اس کا مربع)۔"))
    lines.append((f"({v} {'+' if h >= 0 else '-'} {sp.sstr(abs(h))})**2 = {sp.sstr(k)}", "The left side is now a perfect square.",
                  "اب بائیں طرف مکمل مربع ہے۔"))
    steps = eq_chain(lines, var, first_explain=("Start from the standard form.", "معیاری شکل سے شروع کریں۔"))
    if k < 0:
        steps.append(S(rf"\left({v} {'+' if h >= 0 else '-'} {sp.latex(abs(h))}\right)^2 = {sp.latex(k)} < 0",
                       "A square cannot be negative, so there is no real root.", "مربع منفی نہیں ہو سکتا، اس لیے کوئی حقیقی جذر نہیں۔",
                       f"{ps(k)} < 0"))
        return steps, []
    rt = sp.sqrt(k)
    steps.append(S(rf"{v} {'+' if h >= 0 else '-'} {sp.latex(abs(h))} = \pm\sqrt{{{sp.latex(k)}}} = \pm {sp.latex(rt)}",
                   "Take the square root of both sides (both signs).", "دونوں اطراف کا جذر لیں (دونوں علامات کے ساتھ)۔",
                   f"sqrt({ps(k)}) == {ps(rt)}"))
    roots = order_roots([-h + rt, -h - rt])
    steps.append(S(rf"{v} = {sp.latex(-h)} \pm {sp.latex(rt)}", f"Move ${sp.latex(h)}$ to the right side.",
                   f"${sp.latex(h)}$ کو دائیں طرف لے جائیں۔", *[f"({v} + {ps(h)})**2 == {ps(k)}".replace(v, ps(r_), 1) for r_ in roots]))
    steps.append(roots_line(var, roots, _poly_str(poly)))
    return steps, roots


def formula_steps(poly, var=X):
    a, b, c = coeffs(poly, var)
    v = str(var)
    D = b * b - 4 * a * c
    steps = [S(rf"a = {sp.latex(a)},\quad b = {sp.latex(b)},\quad c = {sp.latex(c)}",
               f"Compare with $a{v}^2 + b{v} + c = 0$.", f"$a{v}^2 + b{v} + c = 0$ سے موازنہ کریں۔"),
             S(rf"{v} = \frac{{-b \pm \sqrt{{b^2 - 4ac}}}}{{2a}} = \frac{{-({sp.latex(b)}) \pm \sqrt{{({sp.latex(b)})^2 - 4({sp.latex(a)})({sp.latex(c)})}}}}{{2({sp.latex(a)})}}",
               "Put $a$, $b$ and $c$ in the quadratic formula.", "دو درجی کلیہ میں $a$، $b$ اور $c$ کی قیمتیں رکھیں۔"),
             S(rf"{v} = \frac{{{sp.latex(-b)} \pm \sqrt{{{sp.latex(b * b)} {_signed(-4 * a * c)}}}}}{{{sp.latex(2 * a)}}} = \frac{{{sp.latex(-b)} \pm \sqrt{{{sp.latex(D)}}}}}{{{sp.latex(2 * a)}}}",
               "Work out $b^2 - 4ac$.", "$b^2 - 4ac$ معلوم کریں۔", f"({b})**2 - 4*({a})*({c}) == {D}")]
    if D < 0:
        steps.append(S(rf"b^2 - 4ac = {sp.latex(D)} < 0", "The number under the root is negative: no real roots.",
                       "جذر کے نیچے عدد منفی ہے: کوئی حقیقی جذر نہیں۔", f"{D} < 0"))
        return steps, []
    rt = sp.sqrt(D)
    if rt.is_Rational:
        steps.append(S(rf"{v} = \frac{{{sp.latex(-b)} + {sp.latex(rt)}}}{{{sp.latex(2 * a)}}} \quad\text{{or}}\quad {v} = \frac{{{sp.latex(-b)} - {sp.latex(rt)}}}{{{sp.latex(2 * a)}}}",
                       f"$\\sqrt{{{sp.latex(D)}}} = {sp.latex(rt)}$; take the + sign and the - sign.",
                       f"$\\sqrt{{{sp.latex(D)}}} = {sp.latex(rt)}$؛ + اور - دونوں علامات لیں۔", f"sqrt({D}) == {rt}"))
    roots = order_roots([(-b + rt) / (2 * a), (-b - rt) / (2 * a)])
    steps.append(roots_line(var, roots, _poly_str(poly), "Simplify each root (put it back in the equation to check).",
                            "ہر جذر کو سادہ کریں (مساوات میں رکھ کر جانچ لیں)۔"))
    return steps, roots


def answer_roots(var, roots):
    if not roots:
        return r"$\text{no real roots}$"
    return "$" + r",\ ".join(f"{var} = {tex_root(r)}" for r in roots) + "$"


def q_solve(label, eq, method, prompt=None, var=X):
    """A full part: standard form, then the method ('factor', 'square', 'formula')."""
    steps, poly = standard_form(eq, var)
    f = {"factor": factor_steps, "square": completing_square_steps, "formula": formula_steps}[method]
    more, roots = f(poly, var)
    if more and steps and more[0]["math"] == steps[-1]["math"]:
        more = more[1:]
    steps += more
    steps.append(S(rf"\text{{S.S}} = {sset(roots)}" if roots else r"\text{S.S} = \{\}", "Write the solution set.", "حل سیٹ لکھیں۔"))
    return P(label, steps, answer_roots(var, roots), prompt=prompt or f"${eq_tex(eq)}$")


# ------------------------------------------------------------------------------------------ graphs on the board


class Graph:
    """Maps maths coordinates to the board's 100-wide figure space and makes drawing commands."""

    def __init__(self, xr, yr, h=60, xstep=None, ystep=None):
        self.x0, self.x1 = float(xr[0]), float(xr[1])
        self.y0, self.y1 = float(yr[0]), float(yr[1])
        self.h = h
        self.xstep = xstep or _nice_step(self.x1 - self.x0)
        self.ystep = ystep or _nice_step(self.y1 - self.y0)

    def X(self, x):
        return round(float(6 + (float(x) - self.x0) / (self.x1 - self.x0) * 88), 2)

    def Y(self, y):
        return round(float(self.h - 5 - (float(y) - self.y0) / (self.y1 - self.y0) * (self.h - 10)), 2)

    def axes(self):
        out = []
        oy = self.Y(min(max(0, self.y0), self.y1))
        ox = self.X(min(max(0, self.x0), self.x1))
        out.append({"t": "line", "p": [6, oy, 94, oy], "arrow": True})
        out.append({"t": "line", "p": [ox, self.h - 5, ox, 5], "arrow": True})
        out.append({"t": "text", "p": [95, oy - 2], "s": "x"})
        out.append({"t": "text", "p": [ox + 1.5, 4], "s": "y"})
        k = math.ceil(self.x0 / self.xstep)
        while k * self.xstep <= self.x1:
            v = k * self.xstep
            if v != 0:
                out.append({"t": "line", "p": [self.X(v), oy - 1, self.X(v), oy + 1]})
                out.append({"t": "text", "p": [self.X(v) - 1.5, oy + 4], "s": _fmt(v)})
            k += 1
        k = math.ceil(self.y0 / self.ystep)
        while k * self.ystep <= self.y1:
            v = k * self.ystep
            if v != 0:
                out.append({"t": "line", "p": [ox - 1, self.Y(v), ox + 1, self.Y(v)]})
                out.append({"t": "text", "p": [ox + 1.5, self.Y(v)], "s": _fmt(v)})
            k += 1
        return out

    def curve(self, f, n=80):
        """f: a sympy expression in x. Pieces outside the y-range are cut off."""
        fn = sp.lambdify(X, ex(f), "math")
        out, pts = [], []
        for j in range(n + 1):
            x = self.x0 + (self.x1 - self.x0) * j / n
            try:
                y = float(fn(x))
            except Exception:
                y = None
            if y is not None and self.y0 <= y <= self.y1:
                pts += [self.X(x), self.Y(y)]
            elif len(pts) >= 4:
                out.append({"t": "poly", "p": pts})
                pts = []
            else:
                pts = []
        if len(pts) >= 4:
            out.append({"t": "poly", "p": pts})
        return out

    def vline(self, x0):
        return [{"t": "line", "p": [self.X(x0), 5, self.X(x0), self.h - 5]}]

    def point(self, x, y, label=None):
        out = [{"t": "dot", "p": [self.X(x), self.Y(y)]}]
        if label:
            out.append({"t": "text", "p": [self.X(x) + 1.5, self.Y(y) - 3], "s": label})
        return out


def _nice_step(span):
    for s in (0.1, 0.2, 0.25, 0.5, 1, 2, 5, 10, 20, 25, 50, 100):
        if span / s <= 10:
            return s
    return 200


def _fmt(v):
    return str(int(v)) if float(v).is_integer() else f"{v:g}"


def pt_label(x, y):
    return f"({_fmt_frac(x)}, {_fmt_frac(y)})"


def _fmt_frac(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):.2f}")


def table_step(expr, xs, var=X, name="y"):
    """A table of values with a check for each value."""
    e = ex(expr)
    ys = [e.subs(var, x) for x in xs]
    row1 = " & ".join(sp.latex(x) for x in xs)
    row2 = " & ".join(sp.latex(y) for y in ys)
    checks = [f"({expr}).subs({var}, {ps(x)}) == {ps(y)}" for x, y in zip(xs, ys)]
    return S(rf"\begin{{array}}{{c|{'c' * len(xs)}}} {var} & {row1} \\ \hline {name} & {row2} \end{{array}}",
             f"Make a table of values: put each ${var}$ in ${name} = {tex(expr)}$.",
             f"قیمتوں کا جدول بنائیں: ہر ${var}$ کو ${name} = {tex(expr)}$ میں رکھیں۔", *checks), ys


def explain(en, ur, *checks, math_="", draw=None):
    return S(math_, en, ur, *checks, draw=draw)


# ------------------------------------------------------------------------------------------ items


def maker(items):
    """ex(eid, number, question, parts, exercise) appends a Class 10 item, as unit01 does."""
    from _helpers import Q

    def ex_(eid, number, question, parts, exercise, figure_h=None):
        it = Q(f"c10-{eid}-q{number}", "review" if exercise.startswith("Review") else "exercise", number, 0,
               question, parts, exercise=exercise)
        if figure_h:
            it["figure_h"] = figure_h
        items.append(it)
        return it
    return ex_


def mcq(label, prompt, options, correct, steps):
    letter = "abcd"[correct]
    opt = options[correct]
    shown = opt if opt.startswith("\text") or "$" in opt else opt
    return P(label, steps + [S(rf"\text{{Answer: ({letter}) }} {shown}", "Choose the option that matches the working.",
                               "وہ جواب چنیں جو حل سے مطابقت رکھتا ہو۔")], f"({letter}) ${opt}$",
             prompt=prompt + " " + " ".join(f"({'abcd'[k]}) ${o}$" for k, o in enumerate(options)))


def txt(s):
    """Plain words inside maths."""
    return r"\text{" + s + "}"
