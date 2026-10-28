"""Templates for Unit 5 (algebraic fractions): reduce to lowest terms, add/subtract over the L.C.D., multiply/divide.
Every line is checked to equal the original expression."""
import sympy as sp

from _helpers import P, S

SYMS = {c: sp.Symbol(c) for c in "abcdfghjklmnpqrstuvwxyz"}


def E(s):
    return sp.sympify(s, locals=SYMS)


def L(e):
    return sp.latex(e)


def F(e):
    """Factored LaTeX of a polynomial."""
    return sp.latex(sp.factor(e))


def frac(n, d):
    if d == 1:
        return L(n)
    return rf"\frac{{{L(n) if not isinstance(n, str) else n}}}{{{L(d) if not isinstance(d, str) else d}}}"


def ffrac(n, d):
    """A fraction with both parts factored."""
    return rf"\frac{{{F(n)}}}{{{F(d)}}}" if sp.simplify(d - 1) != 0 else F(n)


def nice(e):
    """The final answer: one fraction, numerator and denominator factored."""
    n, d = sp.fraction(sp.factor(sp.cancel(sp.together(e))))
    n, d = sp.factor(n), sp.factor(d)
    if d.could_extract_minus_sign() and not n.could_extract_minus_sign():
        n, d = -n, -d
    if n.could_extract_minus_sign() and not n.is_Add and d.is_Mul and sum(isinstance(f_, sp.Add) for f_ in d.args) > 1:
        return rf"-\frac{{{F(-n)}}}{{{F(d)}}}"                      # -2/((x - 1)(x + 1)), not 2/((-x - 1)(x - 1))
    if n.could_extract_minus_sign() and d.is_Mul and not any(isinstance(a, sp.Add) for a in sp.preorder_traversal(n)):
        # move the minus into a bracket of the denominator: -3b^2c / (20(b - 1))  ->  3b^2c / (20(1 - b))
        fs = list(d.args)
        for k, f_ in enumerate(fs):
            if f_.is_Add:
                fs[k] = sp.UnevaluatedExpr(sp.Add(*[-t for t in f_.args][::-1], evaluate=False))
                n, d = -n, sp.Mul(*fs, evaluate=False)
                return rf"\frac{{{F(n)}}}{{{sp.latex(d)}}}"
    return ffrac(n, d) if d != 1 else F(n)


def py(e):
    return "(" + sp.sstr(e) + ")"


def reduce(label, num, den, prompt):
    N, D = E(num), E(den)
    val = N / D
    steps = [S(frac(N, D), "Write the fraction.", "کسر لکھیں۔"),
             S(rf"= {ffrac(N, D)}", "Factorize the numerator and the denominator.", "شمار کنندہ اور نسب نما کی تجزی کریں۔",
               f"{py(sp.factor(N))}/{py(sp.factor(D))} == {py(N)}/{py(D)}"),
             S(rf"= {nice(val)}", "Cancel the common factors.", "مشترک اجزاء کاٹ دیں۔", f"{py(sp.cancel(val))} == {py(N)}/{py(D)}")]
    return P(label, steps, f"${nice(val)}$", prompt=prompt)


def combine(label, terms, prompt):
    """terms: list of (sign, num, den) strings. Add/subtract over the L.C.D."""
    T = [(s, E(n), E(d)) for s, n, d in terms]
    total = sum((1 if s == "+" else -1) * n / d for s, n, d in T)

    def show(parts):
        out = ""
        for k, (s, n, d) in enumerate(parts):
            out += ("" if k == 0 and s == "+" else f" {s} ") + rf"\frac{{{n}}}{{{d}}}"
        return out
    steps = [S(show([(s, L(n), L(d)) for s, n, d in T]), "Write the expression.", "عبارت لکھیں۔"),
             S("= " + show([(s, F(n), F(d)) for s, n, d in T]), "Factorize each denominator.", "ہر نسب نما کی تجزی کریں۔",
               f"{py(sum((1 if s == '+' else -1) * sp.factor(n) / sp.factor(d) for s, n, d in T))} == {py(total)}")]
    lcd = sp.factor(sp.lcm_list([d for _, _, d in T]))
    pieces = []
    num_total = 0
    for s, n, d in T:
        m = sp.factor(sp.cancel(lcd / d))
        pieces.append((s, n, m))
        num_total += (1 if s == "+" else -1) * n * m
    numtex = ""
    for k, (s, n, m) in enumerate(pieces):
        nt = F(n) if n.is_Atom or n.is_Mul or n.is_Pow else rf"\left({F(n)}\right)"
        mt = "" if m == 1 else (F(m) if (m.is_Atom or m.is_Pow) else rf"\left({F(m)}\right)" if m.is_Add else F(m))
        term = nt if m == 1 else (rf"{nt}{mt}" if not nt.lstrip("-").isdigit() or True else nt)
        if n == 1 and m != 1:
            term = mt
        numtex += ("" if k == 0 and s == "+" else f" {s} ") + term
    steps.append(S(rf"= \frac{{{numtex}}}{{{F(lcd)}}}", f"The L.C.D. is ${F(lcd)}$; write each numerator over it.",
                   f"ل.م.م (L.C.D.) ${F(lcd)}$ ہے؛ ہر شمار کنندہ اس پر لکھیں۔", f"{py(num_total)}/{py(lcd)} == {py(total)}"))
    expanded = sp.expand(num_total)
    steps.append(S(rf"= \frac{{{L(expanded)}}}{{{F(lcd)}}}", "Multiply out and collect like terms in the numerator.", "شمار کنندہ میں ضرب دے کر متشابہ ارکان اکٹھے کریں۔",
                   f"{py(expanded)}/{py(lcd)} == {py(total)}"))
    final = nice(total)
    if final.replace(" ", "") != rf"\frac{{{L(expanded)}}}{{{F(lcd)}}}".replace(" ", ""):
        steps.append(S(rf"= {final}", "Factorize the numerator and cancel any common factor.", "شمار کنندہ کی تجزی کر کے مشترک جزو کاٹ دیں۔",
                       f"{py(sp.cancel(total))} == {py(total)}"))
    return P(label, steps, f"${final}$", prompt=prompt)


def muldiv(label, factors, prompt):
    """factors: list of (op, num, den) with op '' for the first, '*' or '/'."""
    T = [(op, E(n), E(d)) for op, n, d in factors]
    total = 1
    for op, n, d in T:
        total = total * (d / n if op == "/" else n / d)
    sym = {"": "", "*": r"\times", "/": r"\div"}
    steps = [S(" ".join(f"{sym[op]} {frac(n, d)}" for op, n, d in T).strip(), "Write the expression.", "عبارت لکھیں۔"),
             S("= " + " ".join(f"{sym[op]} {ffrac(n, d)}" for op, n, d in T).strip(), "Factorize every numerator and denominator.",
               "ہر شمار کنندہ اور نسب نما کی تجزی کریں۔")]
    if any(op == "/" for op, _, _ in T):
        steps.append(S("= " + " ".join(f"{'' if k == 0 else r'\times'} {ffrac(d, n) if op == '/' else ffrac(n, d)}" for k, (op, n, d) in enumerate(T)).strip(),
                       "Dividing by a fraction is multiplying by its reciprocal (turn the fraction after $\\div$ upside down).",
                       "کسر سے تقسیم کرنا اس کے معکوس سے ضرب دینا ہے ($\\div$ کے بعد والی کسر الٹ دیں)۔"))
    final = nice(total)
    steps.append(S(rf"= {final}", "Cancel the common factors.", "مشترک اجزاء کاٹ دیں۔", f"{py(sp.cancel(total))} == {py(total)}"))
    return P(label, steps, f"${final}$", prompt=prompt)
