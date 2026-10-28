"""Step templates for complex numbers (Class 10, Unit 1). Every step carries sympy checks that use I (never a bare i,
which the verifier treats as an ordinary positive number).

  ctex(z)   LaTeX of a complex number written a + bi (fractions and roots as LaTeX)
  py(z)     the same number as a sympy expression string, for checks
  add, sub, mul, div, square, recip   -> (steps, value)
  each part helper -> P(...) ready for an item
"""
import re

import sympy as sp

from _helpers import P, S, T

I = sp.I


def exact(x):
    """An exact sympy number. nsimplify only for decimals: on exact numbers it guesses closed forms (it once turned -1358
    into a product of fractional powers that is merely numerically equal)."""
    x = sp.sympify(x)
    return sp.expand(sp.nsimplify(x, rational=True) if x.has(sp.Float) else x)


def C(a, b=0):
    return exact(a) + exact(b) * I


def _num(x):
    return sp.latex(exact(x))


def ctex(z):
    z = exact(z)
    a, b = sp.re(z), sp.im(z)
    if b == 0:
        return _num(a)
    if b == 1:
        im = "i"
    elif b == -1:
        im = "-i"
    elif b.is_Rational and not b.is_Integer:
        im = ("-" if b < 0 else "") + _num(abs(b)) + "i"
    elif b.is_Integer:
        im = _num(b) + "i"
    else:                                              # irrational coefficient
        sign = "-" if b.could_extract_minus_sign() else ""
        mag = abs(b)
        # a bare root is written i\sqrt{7}, as the book does; anything else (e.g. \frac{\sqrt{5}}{21}) keeps i after it
        im = sign + ("i" + _num(mag) if mag.is_Pow else _num(mag) + "i")
    if a == 0:
        return im
    return _num(a) + (" " if im.startswith("-") else " + ") + (im if not im.startswith("-") else "- " + im[1:])


def py(z):
    return "(" + sp.sstr(exact(z)) + ")"


def paren(z):
    return r"\left(" + ctex(z) + r"\right)"


def ans(z):
    return "$" + ctex(z) + "$"


# ------------------------------------------------------------------------------------------ operations


def add(z1, z2, sign=1):
    a, b, c, d = sp.re(z1), sp.im(z1), sp.re(z2), sp.im(z2)
    r = sp.expand(z1 + sign * z2)
    op = "+" if sign > 0 else "-"
    steps = [S(rf"{paren(z1)} {op} {paren(z2)} = ({_num(a)} {op} {paren(c) if c < 0 else _num(c)}) + ({_num(b)} {op} {paren(d) if d < 0 else _num(d)})i",
               "Add (or subtract) the real parts together and the imaginary parts together.",
               "حقیقی حصوں کو آپس میں اور خیالی حصوں کو آپس میں جمع (یا تفریق) کریں۔",
               f"{py(z1)} {op} {py(z2)} == {py(r)}"),
             S(rf"= {ctex(r)}", "Simplify each part.", "ہر حصے کو سادہ کریں۔", f"{py(a)} {op} {py(c)} == {py(sp.re(r))}")]
    return steps, r


def mul(z1, z2):
    a, b, c, d = sp.re(z1), sp.im(z1), sp.re(z2), sp.im(z2)
    r = sp.expand(z1 * z2)
    steps = [S(rf"{paren(z1)}{paren(z2)} = {_num(a * c)} {'+' if a * d >= 0 else '-'} {_num(abs(a * d))}i {'+' if b * c >= 0 else '-'} {_num(abs(b * c))}i {'+' if b * d >= 0 else '-'} {_num(abs(b * d))}i^2",
               "Multiply each term of the first bracket by each term of the second.",
               "پہلی قوسین کے ہر رکن کو دوسری قوسین کے ہر رکن سے ضرب دیں۔",
               f"{py(z1)}*{py(z2)} == {py(a * c)} + {py(a * d + b * c)}*I + {py(b * d)}*I**2"),
             S(rf"= {_num(a * c)} {'+' if a * d + b * c >= 0 else '-'} {_num(abs(a * d + b * c))}i {'-' if b * d >= 0 else '+'} {_num(abs(b * d))} = {ctex(r)}",
               "Put $i^2 = -1$ and collect the real and imaginary parts.",
               "$i^2 = -1$ رکھیں اور حقیقی اور خیالی حصے اکٹھے کریں۔",
               "I**2 == -1", f"{py(z1)}*{py(z2)} == {py(r)}")]
    return steps, r


def div(n, d):
    """n / d by multiplying with the conjugate of d."""
    dc = sp.conjugate(d)
    num = sp.expand(n * dc)
    den = sp.expand(d * dc)
    r = sp.expand(num / den)
    steps = [S(rf"\frac{{{ctex(n)}}}{{{ctex(d)}}} \times \frac{{{ctex(dc)}}}{{{ctex(dc)}}}",
               f"Multiply the numerator and the denominator by the conjugate of the denominator, ${ctex(dc)}$.",
               f"شمار کنندہ اور نسب نما کو نسب نما کے مزدوج ${ctex(dc)}$ سے ضرب دیں۔",
               f"{py(n)}/{py(d)} == {py(n)}*{py(dc)}/({py(d)}*{py(dc)})"),
             S(rf"= \frac{{{ctex(num)}}}{{{_num(sp.re(d))}^2 + {_num(abs(sp.im(d)))}^2}} = \frac{{{ctex(num)}}}{{{_num(den)}}}",
               "In the denominator $(a+bi)(a-bi) = a^2 + b^2$; multiply out the numerator using $i^2=-1$.",
               "نسب نما میں $(a+bi)(a-bi) = a^2 + b^2$؛ شمار کنندہ کو $i^2=-1$ کے ساتھ ضرب دیں۔",
               f"{py(d)}*{py(dc)} == {py(den)}", f"{py(n)}*{py(dc)} == {py(num)}"),
             S(rf"= {ctex(r)}", "Divide each part by the denominator and simplify.", "ہر حصے کو نسب نما سے تقسیم کر کے سادہ کریں۔",
               f"{py(n)}/{py(d)} == {py(r)}")]
    return steps, r


def square(z):
    a, b = sp.re(z), sp.im(z)
    r = sp.expand(z ** 2)
    steps = [S(rf"{paren(z)}^2 = ({_num(a)})^2 + 2({_num(a)})({ctex(b * I)}) + ({ctex(b * I)})^2",
               "Use $(a+b)^2 = a^2 + 2ab + b^2$.", "$(a+b)^2 = a^2 + 2ab + b^2$ استعمال کریں۔",
               f"{py(z)}**2 == {py(a)}**2 + 2*{py(a)}*{py(b * I)} + {py(b * I)}**2"),
             S(rf"= {_num(a ** 2)} {'+' if 2 * a * b >= 0 else '-'} {_num(abs(2 * a * b))}i - {_num(b ** 2)} = {ctex(r)}",
               "Put $i^2 = -1$ and simplify.", "$i^2 = -1$ رکھ کر سادہ کریں۔", f"{py(z)}**2 == {py(r)}")]
    return steps, r


def recip(z):
    steps, r = div(sp.Integer(1), z)
    return [S(rf"{paren(z)}^{{-1}} = \frac{{1}}{{{ctex(z)}}}", "A power $-1$ means one over the number.", "طاقت $-1$ کا مطلب ہے ایک تقسیم وہ عدد۔",
              f"{py(z)}**(-1) == 1/{py(z)}")] + steps, r


# ------------------------------------------------------------------------------------------ parts

FOUR = ("Since $i^4 = 1$, adding or removing multiples of 4 in the power does not change the value.",
        "چونکہ $i^4 = 1$، طاقت میں 4 کے مضرب جمع یا تفریق کرنے سے قیمت نہیں بدلتی۔")
VALUES = ("Use $i^1 = i,\\ i^2 = -1,\\ i^3 = -i,\\ i^4 = 1$.", "$i^1 = i,\\ i^2 = -1,\\ i^3 = -i,\\ i^4 = 1$ استعمال کریں۔")


def ipow_tex(n):
    r = n % 4
    return r, {0: "1", 1: "i", 2: "-1", 3: "-i"}[r]


def p_ipower(label, n, coef=1):
    r, val = ipow_tex(n)
    value = coef * I ** n
    c = "" if coef == 1 else str(coef)
    lead = rf"{c}i^{{{n}}}"
    steps = [S(rf"{lead} = {c}i^{{{n}}}\cdot (i^4)^{{{(r - n) // 4}}} = {c}i^{{{r}}}", *FOUR, f"{coef}*I**({n}) == {coef}*I**{r}"),
             S(rf"= {ctex(value)}", *VALUES, f"{coef}*I**({n}) == {py(value)}")]
    return P(label, steps, ans(value), prompt=f"${lead}$")




def p_arith(label, z1, z2, op):
    if op == "+":
        steps, r = add(z1, z2, 1)
    elif op == "-":
        steps, r = add(z1, z2, -1)
    elif op == "*":
        steps, r = mul(z1, z2)
    else:
        steps, r = div(z1, z2)
    sym = {"+": "+", "-": "-", "*": "", "/": r"\div"}[op]
    prompt = f"${paren(z1)} {sym} {paren(z2)}$" if op != "*" else f"${paren(z1)}{paren(z2)}$"
    return P(label, steps, ans(r), prompt=prompt)


def p_additive_inverse(label, z):
    return P(label, [S(rf"z = {ctex(z)} \Rightarrow -z = -\left({ctex(z)}\right) = {ctex(-z)}",
                       "The additive inverse of $z$ is $-z$: change the sign of both parts.",
                       "$z$ کا جمعی معکوس $-z$ ہے: دونوں حصوں کی علامت بدل دیں۔",
                       f"{py(z)} + {py(-z)} == 0")], ans(-z), prompt=f"${ctex(z)}$")


def p_multiplicative_inverse(label, z):
    a, b = sp.re(z), sp.im(z)
    r = sp.expand(1 / z)
    m = a ** 2 + b ** 2
    return P(label, [
        S(rf"z^{{-1}} = \left(\frac{{a}}{{a^2+b^2}}, \frac{{-b}}{{a^2+b^2}}\right), \quad a = {_num(a)},\ b = {_num(b)}",
          "For $z = a + bi$ the multiplicative inverse is $\\frac{a}{a^2+b^2} - \\frac{b}{a^2+b^2}i$.",
          "$z = a + bi$ کا ضربی معکوس $\\frac{a}{a^2+b^2} - \\frac{b}{a^2+b^2}i$ ہے۔"),
        S(rf"a^2 + b^2 = ({_num(a)})^2 + ({_num(b)})^2 = {_num(m)}", "Find $a^2 + b^2$.", "$a^2 + b^2$ معلوم کریں۔", f"{py(a)}**2 + {py(b)}**2 == {py(m)}"),
        S(rf"z^{{-1}} = \frac{{{_num(a)}}}{{{_num(m)}}} + \frac{{{_num(-b)}}}{{{_num(m)}}}i = {ctex(r)}", "Substitute and simplify.", "قیمتیں رکھ کر سادہ کریں۔",
          f"1/{py(z)} == {py(r)}", f"{py(z)}*{py(r)} == 1"),
    ], ans(r), prompt=f"${ctex(z)}$")


def p_modulus(label, z):
    a, b = sp.re(z), sp.im(z)
    m = sp.sqrt(a ** 2 + b ** 2)
    return P(label, [
        S(rf"|z| = \sqrt{{a^2+b^2}} = \sqrt{{({_num(a)})^2 + ({_num(b)})^2}}", "The modulus of $a+bi$ is $\\sqrt{a^2+b^2}$.",
          "$a+bi$ کا مقیاس $\\sqrt{a^2+b^2}$ ہے۔"),
        S(rf"= \sqrt{{{_num(a ** 2 + b ** 2)}}} = {_num(m)}", "Add the squares and take the square root.", "مربعوں کو جمع کر کے جذر لیں۔",
          f"sqrt({py(a)}**2 + {py(b)}**2) == {py(m)}", f"Abs({py(z)}) == {py(m)}"),
    ], f"${_num(m)}$", prompt=f"${ctex(z)}$")


def p_real_imag(label, prompt_tex, steps, value):
    """Real and imaginary parts after the working in `steps` produced `value`."""
    a, b = sp.re(value), sp.im(value)
    steps = steps + [S(rf"\operatorname{{Re}}(z) = {_num(a)}, \quad \operatorname{{Im}}(z) = {_num(b)}",
                       "Read off the real part and the coefficient of $i$.", "حقیقی حصہ اور $i$ کا عددی سر پڑھ لیں۔",
                       f"re({py(value)}) == {py(a)}", f"im({py(value)}) == {py(b)}")]
    return P(label, steps, rf"$\operatorname{{Re}} = {_num(a)},\ \operatorname{{Im}} = {_num(b)}$", prompt=prompt_tex)


# ------------------------------------------------------------------------------------------ equations


def _sub_values(expr_py, values):
    """Replace the unknown names in a sympy-syntax string by (value)."""
    out = expr_py
    for name, v in values.items():
        out = re.sub(rf"\b{name}\b", f"({sp.sstr(v)})", out)
    return out


def p_equal_parts(label, lhs_py, rhs_py, unknowns, prompt_tex, lhs_tex=None):
    """Solve an equation between complex numbers whose unknowns are real, by comparing real and imaginary parts."""
    syms = {u: sp.Symbol(u, real=True) for u in unknowns}
    loc = {**syms, "I": I}
    lhs, rhs = sp.sympify(lhs_py, locals=loc), sp.sympify(rhs_py, locals=loc)
    diff = sp.expand(lhs - rhs)
    re_eq, im_eq = sp.expand(sp.re(diff)), sp.expand(sp.im(diff))
    sol = sp.solve([re_eq, im_eq], list(syms.values()), dict=True)
    if len(sol) != 1 or any(s not in sol[0] for s in syms.values()):     # e.g. x + y = 8: one real equation, two unknowns
        raise ValueError(f"{label}: no unique solution for {lhs_py} = {rhs_py}")
    sol = sol[0]
    vals = {u: sol[s] for u, s in syms.items()}
    L = sp.expand(lhs)
    lre, lim = sp.re(L), sp.im(L)
    rre, rim = sp.re(sp.expand(rhs)), sp.im(sp.expand(rhs))
    eq1 = rf"{sp.latex(lre)} = {sp.latex(rre)}"
    eq2 = rf"{sp.latex(lim)} = {sp.latex(rim)}"
    steps = [
        S(rf"{lhs_tex or sp.latex(lhs)} = {sp.latex(rhs)} \;\Rightarrow\; ({sp.latex(lre)}) + ({sp.latex(lim)})i = {ctex(rhs)}",
          "Expand the left side with $i^2=-1$ and write it as (real part) + (imaginary part)$i$.",
          "بائیں جانب کو $i^2=-1$ سے پھیلا کر (حقیقی حصہ) + (خیالی حصہ)$i$ کی صورت میں لکھیں۔",
          f"expand({_sub_values(lhs_py, {u: sp.Symbol(u) for u in unknowns})}) == expand(({sp.sstr(lre)}) + ({sp.sstr(lim)})*I)"),
        S(rf"{eq1} \quad\text{{and}}\quad {eq2}",
          "Two complex numbers are equal only when their real parts are equal and their imaginary parts are equal.",
          "دو مختلط اعداد تب برابر ہوتے ہیں جب ان کے حقیقی حصے برابر ہوں اور خیالی حصے بھی برابر ہوں۔"),
        S(r",\quad ".join(rf"{u} = {sp.latex(v)}" for u, v in vals.items()),
          "Solve these two equations together.", "ان دونوں مساوات کو اکٹھے حل کریں۔",
          f"{_sub_values(sp.sstr(re_eq), vals)} == 0", f"{_sub_values(sp.sstr(im_eq), vals)} == 0"),
        S(r"\text{Check: } " + rf"{lhs_tex or sp.latex(lhs)}\Big|_{{{', '.join(f'{u}={sp.latex(v)}' for u, v in vals.items())}}} = {ctex(rhs)}",
          "Put the values back into the given equation: both sides agree.", "قیمتیں دی گئی مساوات میں رکھیں: دونوں اطراف برابر ہیں۔",
          f"{_sub_values(lhs_py, vals)} == {rhs_py}"),
    ]
    answer = "$" + r",\ ".join(f"{u} = {sp.latex(v)}" for u, v in vals.items()) + "$"
    return P(label, steps, answer, prompt=prompt_tex)


def p_system(label, a1, b1, c1, a2, b2, c2, prompt_tex):
    """a1 z + b1 w = c1, a2 z + b2 w = c2 with complex coefficients: eliminate z, find w, then z."""
    k = sp.expand(a2 * b1 - a1 * b2)
    rhs = sp.expand(a2 * c1 - a1 * c2)
    w = exact(sp.radsimp(rhs / k))
    z = exact(sp.radsimp((c1 - b1 * w) / a1))
    steps = [
        S(rf"{paren(a2)}\,[{paren(a1)}z + {paren(b1)}w] - {paren(a1)}\,[{paren(a2)}z + {paren(b2)}w] = {paren(a2)}{paren(c1)} - {paren(a1)}{paren(c2)}",
          "Multiply equation (i) by the $z$-coefficient of (ii) and (ii) by the $z$-coefficient of (i), then subtract: $z$ cancels.",
          "مساوات (i) کو (ii) کے $z$ کے عددی سر سے اور (ii) کو (i) کے $z$ کے عددی سر سے ضرب دے کر تفریق کریں: $z$ ختم ہو جاتا ہے۔"),
        S(rf"\left({ctex(k)}\right) w = {ctex(rhs)}", "Simplify both sides with $i^2 = -1$.", "دونوں اطراف کو $i^2 = -1$ سے سادہ کریں۔",
          f"{py(a2)}*{py(b1)} - {py(a1)}*{py(b2)} == {py(k)}", f"{py(a2)}*{py(c1)} - {py(a1)}*{py(c2)} == {py(rhs)}"),
        S(rf"w = \frac{{{ctex(rhs)}}}{{{ctex(k)}}} = {ctex(w)}", "Divide, using the conjugate of the denominator.",
          "نسب نما کے مزدوج کی مدد سے تقسیم کریں۔", f"{py(rhs)}/{py(k)} == {py(w)}"),
        S(rf"z = \frac{{{ctex(c1)} - {paren(b1)}{paren(w)}}}{{{ctex(a1)}}} = {ctex(z)}", "Put $w$ in equation (i) and solve for $z$.",
          "$w$ کی قیمت مساوات (i) میں رکھ کر $z$ معلوم کریں۔", f"({py(c1)} - {py(b1)}*{py(w)})/{py(a1)} == {py(z)}"),
        S(r"\text{Check in (ii): } " + rf"{paren(a2)}{paren(z)} + {paren(b2)}{paren(w)} = {ctex(c2)}",
          "Both equations are satisfied.", "دونوں مساوات پوری ہوتی ہیں۔",
          f"{py(a1)}*{py(z)} + {py(b1)}*{py(w)} == {py(c1)}", f"{py(a2)}*{py(z)} + {py(b2)}*{py(w)} == {py(c2)}"),
    ]
    return P(label, steps, f"$z = {ctex(z)},\\ w = {ctex(w)}$", prompt=prompt_tex)


def p_verify(label, prompt_tex, lhs_tex, lhs_steps, lhs_val, rhs_tex, rhs_steps, rhs_val, law_en, law_ur):
    """Verify a property: work out the left side, then the right side, and compare."""
    steps = [T(r"Left-hand side: $" + lhs_tex + "$", "بائیں جانب: $" + lhs_tex + "$")] + lhs_steps + \
            [T(r"Right-hand side: $" + rhs_tex + "$", "دائیں جانب: $" + rhs_tex + "$")] + rhs_steps + \
            [S(rf"{lhs_tex} = {ctex(lhs_val)} = {rhs_tex}", law_en, law_ur, f"{py(lhs_val)} == {py(rhs_val)}")]
    return P(label, steps, f"verified: both sides $= {ctex(lhs_val)}$", prompt=prompt_tex)
