"""Class 11, Unit 1 - Complex Numbers (Punjab/PECTAA, 2025): Exercises 1.1-1.5.

Question statements: the handwritten notes (11th/, Hassan Mehboob) checked against two typed solution sets on MathCity
(Mehreen Kanwal & Rana Ali Hasan, Unit 1; Prof. Muhammad Irfan Dogar, Exercises 1.1-1.3); where they disagree the
majority reading is used and the difference is recorded in a key_note. Every step is checked with sympy; the final
answers are checked against data/answers11/unit01.json (kept out of git).
"""
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src10"))
from _c11 import OMEGA, OMEGA2, Z, L, arg_of, cis, product_check, roots_answer, sqrt_steps, _minus  # noqa: E402
from _complex import C, I, P, S, T, ans, ctex, div, exact, mul, p_equal_parts, paren, py, square  # noqa: E402
from _helpers import Q  # noqa: E402

UNIT = {"unit": 1, "title": "Complex Numbers", "title_ur": "مختلط اعداد", "class": 11, "items": []}
ITEMS = UNIT["items"]
R = sp.Rational


def ex(eid, number, question, parts, exercise, figure_h=None, note=None):
    it = Q(f"c11-{eid}-q{number}", "exercise", number, 0, question, parts, exercise=exercise)
    if figure_h:
        it["figure_h"] = figure_h
    ITEMS.append(it)
    return it


def note(part, en, ur):
    part["key_note"] = {"en": en, "ur": ur}
    return part


def _par(k):
    return f"({sp.latex(k)})" if k < 0 else sp.latex(k)


def eliminate(e1, e2, names=("x", "y")):
    """Solve a1 u + b1 v = c1, a2 u + b2 v = c2 (rational coefficients) by elimination, every line written and checked.
    e1, e2: (a, b, c). -> (steps, (u, v))."""
    (a1, b1, c1), (a2, b2, c2) = [tuple(sp.Rational(t) for t in e) for e in (e1, e2)]
    u, v = names
    U, V = sp.symbols(f"{u} {v}")
    sol = sp.solve([a1 * U + b1 * V - c1, a2 * U + b2 * V - c2], [U, V], dict=True)[0]
    uval, vval = sol[U], sol[V]

    def eq(a, b, c):
        return sp.latex(sp.Eq(a * U + b * V, c, evaluate=False))
    steps = []
    if a1 != 0 and a2 != 0:
        lc = sp.ilcm(abs(int(a1)), abs(int(a2))) if a1.is_Integer and a2.is_Integer else abs(a1 * a2)
        k1, k2 = lc / a1, lc / a2
        nb, nc = k1 * b1 - k2 * b2, k1 * c1 - k2 * c2
        steps.append(S(rf"{eq(k1 * a1, k1 * b1, k1 * c1)} \quad (1) \times {_par(k1)},\qquad {eq(k2 * a2, k2 * b2, k2 * c2)} \quad (2) \times {_par(k2)}",
                       f"Make the coefficients of ${u}$ equal: multiply equation (1) by ${sp.latex(k1)}$ and equation (2) by ${sp.latex(k2)}$.",
                       f"${u}$ کے عددی سر برابر کریں: مساوات (1) کو ${sp.latex(k1)}$ سے اور (2) کو ${sp.latex(k2)}$ سے ضرب دیں۔"))
        steps.append(S(rf"{sp.latex(nb)}{v} = {sp.latex(nc)} \Rightarrow {v} = {sp.latex(vval)}", f"Subtract the two equations: ${u}$ cancels; divide to find ${v}$.",
                       f"دونوں مساوات تفریق کریں: ${u}$ کٹ جاتا ہے؛ تقسیم کر کے ${v}$ معلوم کریں۔", f"({sp.sstr(nb)})*({sp.sstr(vval)}) == {sp.sstr(nc)}"))
        steps.append(S(rf"{sp.latex(a1)}{u} + ({sp.latex(b1)})\left({sp.latex(vval)}\right) = {sp.latex(c1)} \Rightarrow {u} = {sp.latex(uval)}",
                       f"Put ${v} = {sp.latex(vval)}$ in equation (1) and solve for ${u}$.", f"${v} = {sp.latex(vval)}$ کو مساوات (1) میں رکھ کر ${u}$ معلوم کریں۔",
                       f"({sp.sstr(a1)})*({sp.sstr(uval)}) + ({sp.sstr(b1)})*({sp.sstr(vval)}) == {sp.sstr(c1)}"))
    else:                                               # one equation has only one unknown
        each = (a1 == 0 or b1 == 0) and (a2 == 0 or b2 == 0)
        steps.append(S(rf"{u} = {sp.latex(uval)},\quad {v} = {sp.latex(vval)}",
                       "Each equation has only one unknown: solve each one directly." if each else "One equation has a single unknown: solve it, then put the value in the other.",
                       "ہر مساوات میں صرف ایک نامعلوم ہے: ہر ایک کو سیدھا حل کریں۔" if each else "ایک مساوات میں ایک ہی نامعلوم ہے: اسے حل کر کے قیمت دوسری میں رکھیں۔",
                       f"({sp.sstr(a1)})*({sp.sstr(uval)}) + ({sp.sstr(b1)})*({sp.sstr(vval)}) == {sp.sstr(c1)}"))
    return steps, (uval, vval)


def eq_parts(label, given_tex, lhs_rows, rhs_rows, lhs_py, rhs_py, names=("x", "y"), prompt=""):
    """Equality of complex numbers with real unknowns, worked in full: expand each side, compare parts, eliminate.
    lhs_rows / rhs_rows: LaTeX lines of the expansion, the last one in (real) + (imaginary)i form."""
    u, v = names
    syms = {n: sp.Symbol(n, real=True) for n in names}
    lhs = sp.expand(sp.sympify(lhs_py, locals={**syms, "I": I}))
    rhs = sp.expand(sp.sympify(rhs_py, locals={**syms, "I": I}))
    lre, lim, rre, rim = sp.re(lhs), sp.im(lhs), sp.re(rhs), sp.im(rhs)
    plain = {n: sp.Symbol(n) for n in names}
    steps = [S(given_tex, "Write the given equation.", "دی گئی مساوات لکھیں۔")]
    for k, t in enumerate(lhs_rows):
        sq = "i^2" in t
        steps.append(S(t, ("Multiply out the left side, put $i^2 = -1$ and group the real and imaginary parts." if sq else
                           "Group the real terms and the imaginary terms of the left side."),
                       ("بائیں جانب کو ضرب دیں، $i^2 = -1$ رکھیں اور حقیقی اور خیالی حصے اکٹھے کریں۔" if sq else "بائیں جانب کے حقیقی اور خیالی ارکان اکٹھے کریں۔"),
                       *([f"expand({lhs_py}) == expand(({sp.sstr(lre.subs({syms[n]: plain[n] for n in names}))}) + I*({sp.sstr(lim.subs({syms[n]: plain[n] for n in names}))}))"]
                         if k == len(lhs_rows) - 1 else [])))
    for k, t in enumerate(rhs_rows):
        sq = "i^2" in t
        steps.append(S(t, ("Multiply out on the right side and put $i^2 = -1$." if sq else "Work out the right side."),
                       ("دائیں جانب ضرب دیں اور $i^2 = -1$ رکھیں۔" if sq else "دائیں جانب کو حل کریں۔"),
                       *([f"expand({rhs_py}) == {py(rhs)}"] if k == len(rhs_rows) - 1 else [])))
    a1, b1 = [sp.expand(lre).coeff(syms[n]) for n in names]
    c1 = rre - (lre - a1 * syms[u] - b1 * syms[v])
    a2, b2 = [sp.expand(lim).coeff(syms[n]) for n in names]
    c2 = rim - (lim - a2 * syms[u] - b2 * syms[v])
    steps.append(S(rf"{sp.latex(lre)} = {sp.latex(rre)} \quad (1),\qquad {sp.latex(lim)} = {sp.latex(rim)} \quad (2)",
                   "Equal complex numbers have equal real parts and equal imaginary parts.", "برابر مختلط اعداد کے حقیقی حصے برابر اور خیالی حصے برابر ہوتے ہیں۔"))
    if (sp.expand(lre) - a1 * syms[u] - b1 * syms[v]) != 0 or (sp.expand(lim) - a2 * syms[u] - b2 * syms[v]) != 0:
        steps.append(S(rf"{sp.latex(sp.Eq(a1 * syms[u] + b1 * syms[v], c1, evaluate=False))} \quad (1),\qquad {sp.latex(sp.Eq(a2 * syms[u] + b2 * syms[v], c2, evaluate=False))} \quad (2)",
                       "Move the constant terms to the right side.", "مستقل ارکان کو دائیں طرف لے جائیں۔"))
    est, (uv, vv) = eliminate((a1, b1, c1), (a2, b2, c2), names)
    steps += est
    vals = {u: uv, v: vv}
    chk = lhs_py
    for n, val in vals.items():
        chk = re.sub(rf"\b{n}\b", f"({sp.sstr(val)})", chk)
    steps.append(S(rf"\text{{Check: }} {u} = {sp.latex(uv)},\ {v} = {sp.latex(vv)} \Rightarrow \text{{both sides are equal}}",
                   "Put the values back into the equation: both sides come out equal.", "قیمتیں مساوات میں واپس رکھیں: دونوں اطراف برابر آتے ہیں۔",
                   f"expand({chk}) == {py(rhs)}"))
    return P(label, steps, f"${u} = {sp.latex(uv)},\\ {v} = {sp.latex(vv)}$", prompt=prompt)


import re  # noqa: E402

# ================================================================================================== Exercise 1.1


def mi_pair(label, a, b):
    z = C(a, b)
    m = exact(a) ** 2 + exact(b) ** 2
    inv = exact(1 / z)
    ra, rb = sp.re(inv), sp.im(inv)
    steps = [
        S(r"(a, b)^{-1} = \left(\frac{a}{a^2 + b^2},\ \frac{-b}{a^2 + b^2}\right)",
          "The multiplicative inverse of the ordered pair $(a, b)$, that is of $a + bi$, is $\\left(\\frac{a}{a^2+b^2}, \\frac{-b}{a^2+b^2}\\right)$.",
          "ترتیب وار جوڑے $(a, b)$ یعنی $a + bi$ کا ضربی معکوس $\\left(\\frac{a}{a^2+b^2}, \\frac{-b}{a^2+b^2}\\right)$ ہے۔"),
        S(rf"a = {L(a)},\ b = {L(b)}:\quad a^2 + b^2 = ({L(a)})^2 + ({L(b)})^2 = {L(m)}", "Read off $a$ and $b$ and find $a^2 + b^2$.",
          "$a$ اور $b$ پڑھ کر $a^2 + b^2$ معلوم کریں۔", f"({py(a)})**2 + ({py(b)})**2 == {py(m)}"),
        S(rf"\left({L(a)}, {L(b)}\right)^{{-1}} = \left(\frac{{{L(a)}}}{{{L(m)}}},\ \frac{{{L(-exact(b))}}}{{{L(m)}}}\right) = \left({L(ra)},\ {L(rb)}\right)",
          "Substitute and simplify.", "قیمتیں رکھ کر سادہ کریں۔", f"{py(a)}/{py(m)} == {py(ra)}", f"-{py(b)}/{py(m)} == {py(rb)}"),
        S(rf"\text{{Check: }} ({ctex(z)})({ctex(inv)}) = 1", "A number times its inverse is 1.", "کسی عدد اور اس کے معکوس کا حاصل ضرب 1 ہوتا ہے۔",
          f"{py(z)}*{py(inv)} == 1"),
    ]
    return P(label, steps, rf"$\left({L(ra)},\ {L(rb)}\right)$", prompt=rf"$({L(a)}, {L(b)})$")


ex("ex1.1", 1, "Find the multiplicative inverse of each of the following numbers: (i) $(-4, 7)$ (ii) $(\\sqrt{2}, -\\sqrt{5})$ (iii) $(1, 0)$", [
    mi_pair("i", -4, 7), mi_pair("ii", sp.sqrt(2), -sp.sqrt(5)), mi_pair("iii", 1, 0)], "1.1")


def real_imag(label, prompt, pre, value_steps, value):
    a, b = sp.re(value), sp.im(value)
    steps = pre + value_steps + [S(rf"\operatorname{{Re}} = {L(a)},\quad \operatorname{{Im}} = {L(b)}",
                                   "Read off the real part and the coefficient of $i$.", "حقیقی حصہ اور $i$ کا عددی سر پڑھ لیں۔",
                                   f"re({py(value)}) == {py(a)}", f"im({py(value)}) == {py(b)}")]
    return P(label, steps, rf"$\operatorname{{Re}} = {L(a)},\ \operatorname{{Im}} = {L(b)}$", prompt=prompt)


_s2, _n2 = square(C(-2, 3))
_d2, _v2 = div(_n2, C(1, 1))
_s4, _n4 = square(C(4, 3))
_d4, _v4 = div(_n4, C(4, -3))
ex("ex1.1", 2, "Separate into real and imaginary parts (write as a simple complex number): (i) $\\frac{2-7i}{4+5i}$ (ii) $\\frac{(-2+3i)^2}{1+i}$ "
   "(iii) $\\frac{i}{1+i}$ (iv) $\\frac{(4+3i)^2}{4-3i}$", [
       real_imag("i", "$\\frac{2-7i}{4+5i}$", [], *div(C(2, -7), C(4, 5))),
       real_imag("ii", "$\\frac{(-2+3i)^2}{1+i}$", [T("First square the numerator.", "پہلے شمار کنندہ کا مربع لیں۔")] + _s2, _d2, _v2),
       note(real_imag("iii", "$\\frac{i}{1+i}$", [], *div(I, C(1, 1))),
            "The handwritten notes write $i - i^2 = 1 - i$ and get $\\frac{1}{2} - \\frac{i}{2}$; in fact $i - i^2 = 1 + i$, so the answer is $\\frac{1}{2} + \\frac{1}{2}i$.",
            "ہاتھ کے نوٹس میں $i - i^2 = 1 - i$ لکھا ہے؛ درست $i - i^2 = 1 + i$ ہے، اس لیے جواب $\\frac{1}{2} + \\frac{1}{2}i$ ہے۔"),
       real_imag("iv", "$\\frac{(4+3i)^2}{4-3i}$", [T("First square the numerator.", "پہلے شمار کنندہ کا مربع لیں۔")] + _s4, _d4, _v4)], "1.1")

A, B = sp.symbols("a b", real=True)
ex("ex1.1", 3, "Prove that $\\bar{z} = z$ iff $z$ is real.", [P("", [
    S(r"\text{Let } z = a + bi,\quad \bar{z} = a - bi", "Write $z$ and its conjugate in terms of the real numbers $a$ and $b$.",
      "$z$ اور اس کے مزدوج کو حقیقی اعداد $a$ اور $b$ کی صورت میں لکھیں۔", "conjugate(a + b*I) == a - b*I"),
    S(r"\text{Suppose } \bar{z} = z:\quad a - bi = a + bi", "First direction: assume $\\bar z = z$ and show $z$ is real.",
      "پہلی سمت: فرض کریں $\\bar z = z$ اور ثابت کریں کہ $z$ حقیقی ہے۔"),
    S(r"0 = (a + bi) - (a - bi) = 2bi \Rightarrow b = 0", "Subtract: only the imaginary parts remain, so $b = 0$.",
      "تفریق کریں: صرف خیالی حصے بچتے ہیں، اس لیے $b = 0$۔", "(a + b*I) - (a - b*I) == 2*b*I"),
    S(r"z = a + 0i = a \in \mathbb{R}", "With $b = 0$, $z$ has no imaginary part: it is real.", "$b = 0$ ہونے سے $z$ کا کوئی خیالی حصہ نہیں: یہ حقیقی ہے۔"),
    S(r"\text{Conversely, } z = a \in \mathbb{R} \Rightarrow \bar{z} = a - 0i = a = z", "Second direction: a real number is its own conjugate.",
      "دوسری سمت: حقیقی عدد کا مزدوج وہی عدد ہوتا ہے۔", "conjugate(a) == a"),
    S(r"\therefore\ \bar{z} = z \iff z \text{ is real}", "Both directions are proved.", "دونوں سمتیں ثابت ہو گئیں۔")],
    "$\\bar{z} = z \\iff z$ is real")], "1.1")

ex("ex1.1", 4, "For $z \\in C$, show that: (i) $\\frac{z+\\bar{z}}{2} = \\operatorname{Re}(z)$ (ii) $\\frac{z-\\bar{z}}{2i} = \\operatorname{Im}(z)$ (iii) $|z|^2 = z\\bar{z}$", [
    P("i", [S(r"z = a + bi,\quad \bar{z} = a - bi,\quad \operatorname{Re}(z) = a", "Let $z = a + bi$ with $a, b$ real.", "فرض کریں $z = a + bi$ جہاں $a, b$ حقیقی ہیں۔"),
            S(r"\frac{z + \bar{z}}{2} = \frac{a + bi + a - bi}{2} = \frac{2a}{2} = a", "Add: the imaginary parts cancel.", "جمع کریں: خیالی حصے کٹ جاتے ہیں۔",
              "((a + b*I) + (a - b*I))/2 == a"),
            S(r"= \operatorname{Re}(z)", "This is the real part of $z$.", "یہ $z$ کا حقیقی حصہ ہے۔")], "proved: $\\frac{z+\\bar z}{2} = a = \\operatorname{Re}(z)$",
      prompt="$\\frac{z+\\bar{z}}{2} = \\operatorname{Re}(z)$"),
    P("ii", [S(r"\frac{z - \bar{z}}{2i} = \frac{(a + bi) - (a - bi)}{2i} = \frac{2bi}{2i} = b", "Subtract: the real parts cancel, then divide by $2i$.",
               "تفریق کریں: حقیقی حصے کٹ جاتے ہیں، پھر $2i$ سے تقسیم کریں۔", "((a + b*I) - (a - b*I))/(2*I) == b"),
             S(r"= \operatorname{Im}(z)", "This is the imaginary part of $z$.", "یہ $z$ کا خیالی حصہ ہے۔")], "proved: $\\frac{z-\\bar z}{2i} = b = \\operatorname{Im}(z)$",
      prompt="$\\frac{z-\\bar{z}}{2i} = \\operatorname{Im}(z)$"),
    P("iii", [S(r"|z| = \sqrt{a^2 + b^2} \Rightarrow |z|^2 = a^2 + b^2", "Square the modulus.", "مقیاس کا مربع لیں۔", "sqrt(a**2 + b**2)**2 == a**2 + b**2"),
              S(r"z\bar{z} = (a + bi)(a - bi) = a^2 - b^2 i^2 = a^2 + b^2", "Multiply $z$ by its conjugate; $i^2 = -1$.", "$z$ کو اس کے مزدوج سے ضرب دیں؛ $i^2 = -1$۔",
                "expand((a + b*I)*(a - b*I)) == a**2 + b**2"),
              S(r"\therefore\ |z|^2 = z\bar{z}", "Both equal $a^2 + b^2$.", "دونوں $a^2 + b^2$ کے برابر ہیں۔")], "proved: $|z|^2 = a^2 + b^2 = z\\bar z$",
      prompt="$|z|^2 = z\\bar{z}$")], "1.1")

_m5, _n5 = mul(C(2, -1), C(1, -3))
_d5, _v5 = div(_n5, C(3, -2))
ex("ex1.1", 5, "If $z_1 = 2+i$, $z_2 = 3-2i$, $z_3 = 1+3i$ then express $\\frac{\\bar{z}_1\\bar{z}_3}{z_2}$ in the form of $a+ib$.", [P("", [
    S(r"\bar{z}_1 = 2 - i,\quad \bar{z}_3 = 1 - 3i,\quad z_2 = 3 - 2i", "Write the conjugates: change the sign of the imaginary part.",
      "مزدوج لکھیں: خیالی حصے کی علامت بدل دیں۔", "conjugate(2 + I) == 2 - I", "conjugate(1 + 3*I) == 1 - 3*I"),
    S(r"\frac{\bar{z}_1\bar{z}_3}{z_2} = \frac{(2 - i)(1 - 3i)}{3 - 2i}", "Put the conjugates in the numerator; multiply them first.",
      "شمار کنندہ میں مزدوج اعداد رکھیں؛ پہلے انہیں ضرب دیں۔")] + _m5 + _d5, ans(_v5))], "1.1")


def modulus_part(label, prompt, expr_tex, value):
    a, b = sp.re(value), sp.im(value)
    m = sp.sqrt(a ** 2 + b ** 2)
    return P(label, [
        S(rf"{expr_tex} = {ctex(value)}", "Substitute $z_1 = 2 + 7i$, $z_2 = -5 + 3i$ (and their conjugates) and collect real and imaginary parts.",
          "$z_1 = 2 + 7i$ اور $z_2 = -5 + 3i$ (اور ان کے مزدوج) رکھ کر حقیقی اور خیالی حصے اکٹھے کریں۔"),
        S(rf"|{ctex(value)}| = \sqrt{{({L(a)})^2 + ({L(b)})^2}} = \sqrt{{{L(a ** 2 + b ** 2)}}} = {L(m)}", "Modulus $\\sqrt{a^2 + b^2}$.",
          "مقیاس $\\sqrt{a^2 + b^2}$۔", f"Abs({py(value)}) == {sp.sstr(m)}")], f"${L(m)}$", prompt=prompt)


z1, z2 = C(2, 7), C(-5, 3)
v6 = [exact(2 * z1 - 4 * z2), exact(3 * z1 + 2 * sp.conjugate(z1)), exact(-7 * z2 + 2 * sp.conjugate(z2))]
s6 = exact(z1 + z2)
ex("ex1.1", 6, "If $z_1 = 2+7i$ and $z_2 = -5+3i$, then evaluate the following: (i) $|2z_1 - 4z_2|$ (ii) $|3z_1 + 2\\bar{z}_1|$ (iii) $|-7z_2 + 2\\bar{z}_2|$ "
   "(iv) $|(z_1+z_2)^3|$", [
       modulus_part("i", "$|2z_1 - 4z_2|$", r"2z_1 - 4z_2 = (4 + 14i) - (-20 + 12i)", v6[0]),
       modulus_part("ii", "$|3z_1 + 2\\bar{z}_1|$", r"3z_1 + 2\bar{z}_1 = (6 + 21i) + (4 - 14i)", v6[1]),
       note(modulus_part("iii", "$|-7z_2 + 2\\bar{z}_2|$", r"-7z_2 + 2\bar{z}_2 = (35 - 21i) + (-10 - 6i)", v6[2]),
            "The handwritten notes stop at $\\sqrt{25^2 + 27^2}$; it equals $\\sqrt{1354}$.", "ہاتھ کے نوٹس $\\sqrt{25^2 + 27^2}$ پر رک جاتے ہیں؛ اس کی قیمت $\\sqrt{1354}$ ہے۔"),
       P("iv", [S(r"|(z_1 + z_2)^3| = |z_1 + z_2|^3", "The modulus of a power is the power of the modulus: $|z^n| = |z|^n$.",
                  "طاقت کا مقیاس، مقیاس کی طاقت ہے: $|z^n| = |z|^n$۔"),
                S(rf"z_1 + z_2 = (2 + 7i) + (-5 + 3i) = {ctex(s6)}", "Add the two numbers.", "دونوں اعداد جمع کریں۔", f"{py(z1)} + {py(z2)} == {py(s6)}"),
                S(r"|-3 + 10i| = \sqrt{9 + 100} = \sqrt{109}", "Find the modulus.", "مقیاس معلوم کریں۔", f"Abs({py(s6)}) == sqrt(109)"),
                S(r"|z_1 + z_2|^3 = (\sqrt{109})^3 = 109\sqrt{109}", "Cube it: $(\\sqrt{109})^2 = 109$.", "مکعب لیں: $(\\sqrt{109})^2 = 109$۔",
                  f"Abs(({py(s6)})**3) == 109*sqrt(109)")], "$109\\sqrt{109}$", prompt="$|(z_1+z_2)^3|$")], "1.1")

ex("ex1.1", 7, "Show that: $i^{n+1} + i^{n+2} + i^{n+3} + i^{n+4} = 0$, for all $n \\in N$.", [note(P("", [
    S(r"i^{n+1} + i^{n+2} + i^{n+3} + i^{n+4} = i^n\left(i + i^2 + i^3 + i^4\right)", "Take $i^n$ common: $i^{n+k} = i^n\\, i^k$.",
      "$i^n$ مشترک لیں: $i^{n+k} = i^n\\, i^k$۔", "I**5 + I**6 + I**7 + I**8 == I**4*(I + I**2 + I**3 + I**4)"),
    S(r"= i^n\left(i - 1 - i + 1\right)", "Use $i^2 = -1$, $i^3 = -i$, $i^4 = 1$.", "$i^2 = -1$، $i^3 = -i$، $i^4 = 1$ استعمال کریں۔",
      "I + I**2 + I**3 + I**4 == I - 1 - I + 1"),
    S(r"= i^n \cdot 0 = 0", "The bracket is zero, so the whole sum is zero for every natural $n$.", "قوسین صفر ہے، اس لیے ہر قدرتی $n$ کے لیے مجموعہ صفر ہے۔",
      "I - 1 - I + 1 == 0")], "proved: the sum is $i^n \\cdot 0 = 0$"),
    "One typed solution set writes the powers as $4n+1, \\dots, 4n+4$; the handwritten notes and the other typed set have $n+1, \\dots, n+4$, used here (the proof covers both).",
    "ایک ٹائپ شدہ حل میں طاقتیں $4n+1$ وغیرہ ہیں؛ ہاتھ کے نوٹس اور دوسرے حل میں $n+1$ وغیرہ ہیں، جو یہاں لی گئی ہیں۔")], "1.1")

_d8, _v8 = div(C(1, 1), C(1, -1))
ex("ex1.1", 8, "Find the least positive value of $n$, if $\\left(\\frac{1+i}{1-i}\\right)^{2n} = 1$", [P("", [
    T("Simplify the fraction inside the bracket first.", "پہلے قوسین کے اندر کی کسر کو سادہ کریں۔")] + _d8 + [
    S(r"\left(\frac{1+i}{1-i}\right)^{2n} = i^{2n} = (i^2)^n = (-1)^n", "Put $\\frac{1+i}{1-i} = i$.", "$\\frac{1+i}{1-i} = i$ رکھیں۔", "I**2 == -1"),
    S(r"(-1)^n = 1 \iff n \text{ is even}", "$(-1)^n$ is $1$ only for even $n$.", "$(-1)^n$ صرف جفت $n$ کے لیے $1$ ہے۔", "(-1)**1 == -1", "(-1)**2 == 1"),
    S(r"\text{least positive } n = 2", "The smallest positive even number is 2. Check: $i^4 = 1$.", "سب سے چھوٹا مثبت جفت عدد 2 ہے۔ جانچ: $i^4 = 1$۔",
      "((1 + I)/(1 - I))**4 == 1", "((1 + I)/(1 - I))**2 == -1")], "$n = 2$")], "1.1")

ex("ex1.1", 9, "Show that, the value of $i^n$ for $n \\in N$ and $n > 4$ is $i^r$, where $r$ is the remainder when $n$ is divided by $4$.", [P("", [
    S(r"n = 4q + r,\quad q \in \mathbb{N},\ 0 \le r < 4", "Divide $n$ by 4: quotient $q$, remainder $r$.", "$n$ کو 4 سے تقسیم کریں: حاصل قسمت $q$، باقی $r$۔"),
    S(r"i^n = i^{4q + r} = (i^4)^q\, i^r", "Use the laws of indices.", "قوت نما کے قوانین استعمال کریں۔"),
    S(r"i^4 = (i^2)^2 = (-1)^2 = 1", "The fourth power of $i$ is 1.", "$i$ کی چوتھی طاقت 1 ہے۔", "I**4 == 1"),
    S(r"i^n = 1^q\, i^r = i^r", "So only the remainder decides the value. Example: $i^{23} = i^{4(5)+3} = i^3 = -i$.",
      "اس لیے قیمت صرف باقی سے طے ہوتی ہے۔ مثال: $i^{23} = i^3 = -i$۔", "I**23 == I**3", "I**23 == -I")], "proved: $i^n = (i^4)^q i^r = i^r$")], "1.1")


# ================================================================================================== Exercise 1.2

ex("ex1.2", 1, "Find the values of $x$ and $y$ in each of the following: (i) $x+iy+2-3i = i(5-i)(3+4i)$ (ii) $(x+iy)(1-i) = (2-3i)(-5+5i)\\left(-i\\frac{3}{5}\\right)$ "
   "(iii) $\\frac{x}{2+i} + \\frac{y}{3-i} = 4+5i$", [
       eq_parts("i", r"x + iy + 2 - 3i = i(5 - i)(3 + 4i)",
                [r"x + iy + 2 - 3i = (x + 2) + (y - 3)i"],
                [r"(5 - i)(3 + 4i) = 15 + 20i - 3i - 4i^2 = 19 + 17i", r"i(19 + 17i) = 19i + 17i^2 = -17 + 19i"],
                "x + I*y + 2 - 3*I", "I*(5 - I)*(3 + 4*I)", prompt="$x+iy+2-3i = i(5-i)(3+4i)$"),
       eq_parts("ii", r"(x + iy)(1 - i) = (2 - 3i)(-5 + 5i)\left(-\frac{3}{5}i\right)",
                [r"(x + iy)(1 - i) = x - xi + yi - yi^2 = (x + y) + (y - x)i"],
                [r"(2 - 3i)(-5 + 5i) = -10 + 10i + 15i - 15i^2 = 5 + 25i", r"(5 + 25i)\left(-\frac{3}{5}i\right) = -3i - 15i^2 = 15 - 3i"],
                "(x + I*y)*(1 - I)", "(2 - 3*I)*(-5 + 5*I)*(-3*I/5)", prompt="$(x+iy)(1-i) = (2-3i)(-5+5i)\\left(-i\\frac{3}{5}\\right)$"),
       eq_parts("iii", r"\frac{x}{2 + i} + \frac{y}{3 - i} = 4 + 5i \;\Rightarrow\; x(3 - i) + y(2 + i) = (4 + 5i)(2 + i)(3 - i)",
                [r"x(3 - i) + y(2 + i) = 3x - xi + 2y + yi = (3x + 2y) + (y - x)i"],
                [r"(2 + i)(3 - i) = 6 - 2i + 3i - i^2 = 7 + i \quad (\text{the common denominator})",
                 r"(4 + 5i)(7 + i) = 28 + 4i + 35i + 5i^2 = 23 + 39i"],
                "x*(3 - I) + y*(2 + I)", "(4 + 5*I)*(2 + I)*(3 - I)", prompt="$\\frac{x}{2+i} + \\frac{y}{3-i} = 4+5i$")], "1.2")

ex("ex1.2", 2, "If $z_1 = -13+24i$ and $z_2 = x+iy$, find the real values of $x$ and $y$ such that $z_1 - z_2 = -27+15i$.", [
    eq_parts("", r"z_1 - z_2 = -27 + 15i \Rightarrow (-13 + 24i) - (x + iy) = -27 + 15i",
             [r"(-13 + 24i) - (x + iy) = (-13 - x) + (24 - y)i"], [],
             "-13 + 24*I - (x + I*y)", "-27 + 15*I")], "1.2")


def sq_eq(label, w, prompt, pre=None, exact_ans=True):
    steps, root = sqrt_steps(w, names=("a", "b"))   # x and y are the unknowns here
    a, b = sp.re(root), sp.im(root)
    steps = (pre or []) + [S(rf"(x + iy)^2 = {ctex(w)} \Rightarrow x + iy = \pm\sqrt{{{ctex(w)}}}", "Take the square root of both sides.",
                            "دونوں اطراف کا جذر لیں۔")] + steps + [
        S(rf"x + iy = \pm\left({ctex(root)}\right) \Rightarrow x = \pm {L(a)},\ y = \pm {L(b) if b > 0 else L(-b)}",
          "Compare real and imaginary parts; $x$ and $y$ take the signs together (both upper or both lower).",
          "حقیقی اور خیالی حصوں کا موازنہ کریں؛ $x$ اور $y$ کی علامتیں ساتھ ساتھ لی جاتی ہیں۔", f"({py(root)})**2 == {py(w)}")]
    sgn = "" if b > 0 else "-"
    answer = rf"$x = {L(a)},\ y = {L(b)}$ or $x = {L(-a)},\ y = {L(-b)}$"
    return P(label, steps, answer, prompt=prompt)


_d3, _w3 = div(C(-3, 2), C(3, 1))


def _q3iii(p):
    """The roots of -7/10 + 9i/10 do not simplify: write them as single square roots with decimals."""
    xs = r"\sqrt{\frac{\sqrt{130} - 7}{20}}"
    ys = r"\sqrt{\frac{\sqrt{130} + 7}{20}}"
    p["steps"][-1] = S(rf"x = \pm{xs} \approx \pm 0.469,\quad y = \pm{ys} \approx \pm 0.959",
                       "Compare real and imaginary parts. With $a = -\\frac{7}{10}$: $\\frac{|z| - a}{2}$ and $\\frac{|z| + a}{2}$ are "
                       "$\\frac{\\sqrt{130} + 7}{20}$ and $\\frac{\\sqrt{130} - 7}{20}$; $x$ and $y$ take the same sign because $2xy = \\frac{9}{10} > 0$.",
                       "حقیقی اور خیالی حصوں کا موازنہ کریں۔ $a = -\\frac{7}{10}$ کے ساتھ $\\frac{|z| + a}{2} = \\frac{\\sqrt{130} - 7}{20}$ اور "
                       "$\\frac{|z| - a}{2} = \\frac{\\sqrt{130} + 7}{20}$؛ $x$ اور $y$ کی علامت ایک ہی ہے کیونکہ $2xy = \\frac{9}{10} > 0$۔",
                       "((sqrt(130) - 7)/20) - ((sqrt(130) + 7)/20) == -R(7,10)",
                       "4*((sqrt(130) - 7)/20)*((sqrt(130) + 7)/20) == R(81,100)")
    p["answer"] = rf"$x = {xs} \approx 0.469,\ y = {ys} \approx 0.959$ or $x \approx -0.469,\ y \approx -0.959$"
    return p


ex("ex1.2", 3, "Find the values of $x$ and $y$ if: (i) $(x+iy)^2 = 25+60i$ (ii) $(x+iy)^2 = 64+48i$ (iii) $(x+iy)^2 = \\frac{2i-3}{3+i}$", [
    sq_eq("i", C(25, 60), "$(x+iy)^2 = 25+60i$"),
    sq_eq("ii", C(64, 48), "$(x+iy)^2 = 64+48i$"),
    note(_q3iii(sq_eq("iii", _w3, "$(x+iy)^2 = \\frac{2i-3}{3+i}$", pre=[S(r"\frac{2i - 3}{3 + i} = \frac{-3 + 2i}{3 + i}", "First write the right side as a simple complex number.",
                                                                     "پہلے دائیں جانب کو سادہ مختلط عدد بنائیں۔")] + _d3)),
         "The handwritten notes rationalise with $3 - i$ in the denominator by mistake and get $\\frac{-11 + 3i}{10}$; with the printed $3 + i$ the value is "
         "$\\frac{-7 + 9i}{10}$, so $x \\approx \\pm 0.469$, $y \\approx \\pm 0.959$ (one typed solution rounds to $0.46$, $0.97$).",
         "ہاتھ کے نوٹس میں نسب نما غلطی سے $3 - i$ لیا گیا ہے؛ درست قیمت $\\frac{-7 + 9i}{10}$ ہے، اس لیے $x \\approx \\pm 0.469$، $y \\approx \\pm 0.959$۔")], "1.2")

al = sp.Symbol("alpha", real=True)
ex("ex1.2", 4, "If $z_1 = 2+3i$ and $z_2 = 1-\\alpha$, find the real value of $\\alpha$ such that $\\operatorname{Im}(z_1 z_2) = 7$.", [note(P("", [
    S(r"z_1 z_2 = (2 + 3i)(1 - \alpha) = 2(1 - \alpha) + 3(1 - \alpha)i", "Multiply: $1 - \\alpha$ is a real number, so it multiplies both parts.",
      "ضرب دیں: $1 - \\alpha$ حقیقی عدد ہے، اس لیے دونوں حصوں کو ضرب دیتا ہے۔", "expand((2 + 3*I)*(1 - q)) == 2*(1 - q) + 3*(1 - q)*I"),
    S(r"\operatorname{Im}(z_1 z_2) = 3(1 - \alpha) = 7", "The imaginary part must equal 7.", "خیالی حصہ 7 کے برابر ہونا چاہیے۔"),
    S(r"3 - 3\alpha = 7 \Rightarrow -3\alpha = 4 \Rightarrow \alpha = -\frac{4}{3}", "Solve for $\\alpha$.", "$\\alpha$ معلوم کریں۔", "3*(1 - (-R(4,3))) == 7"),
    S(r"\text{Check: } (2 + 3i)\left(1 + \tfrac{4}{3}\right) = \tfrac{14}{3} + 7i", "The imaginary part is 7.", "خیالی حصہ 7 ہے۔",
      "im((2 + 3*I)*(1 + R(4,3))) == 7")], "$\\alpha = -\\frac{4}{3}$"),
    "The question is printed $z_2 = 1 - \\alpha$ in the handwritten notes and one typed solution set (answer $-\\frac{4}{3}$); another typed set reads "
    "$z_2 = 1 - \\alpha i$, which would give $\\alpha = -2$.",
    "ہاتھ کے نوٹس اور ایک ٹائپ شدہ حل میں $z_2 = 1 - \\alpha$ ہے (جواب $-\\frac{4}{3}$)؛ دوسرے حل میں $1 - \\alpha i$ پڑھا گیا ہے جس سے $\\alpha = -2$ آتا ہے۔")], "1.2")

ex("ex1.2", 5, "If $z_1 = x+iy$ and $z_2 = a+bi$, find $x, y, a$ and $b$ such that $z_1 + z_2 = 10+4i$ and $z_1 - z_2 = 6+2i$.", [P("", [
    S(r"(z_1 + z_2) + (z_1 - z_2) = (10 + 4i) + (6 + 2i) \Rightarrow 2z_1 = 16 + 6i", "Add the two equations: $z_2$ cancels.",
      "دونوں مساوات جمع کریں: $z_2$ کٹ جاتا ہے۔", "(10 + 4*I) + (6 + 2*I) == 16 + 6*I"),
    S(r"z_1 = 8 + 3i", "Divide by 2.", "2 سے تقسیم کریں۔", "(16 + 6*I)/2 == 8 + 3*I"),
    S(r"(z_1 + z_2) - (z_1 - z_2) = (10 + 4i) - (6 + 2i) \Rightarrow 2z_2 = 4 + 2i \Rightarrow z_2 = 2 + i", "Subtract the two equations: $z_1$ cancels.",
      "دونوں مساوات تفریق کریں: $z_1$ کٹ جاتا ہے۔", "((10 + 4*I) - (6 + 2*I))/2 == 2 + I"),
    S(r"x + iy = 8 + 3i \Rightarrow x = 8,\ y = 3;\quad a + bi = 2 + i \Rightarrow a = 2,\ b = 1", "Compare real and imaginary parts.",
      "حقیقی اور خیالی حصوں کا موازنہ کریں۔", "(8 + 3*I) + (2 + I) == 10 + 4*I", "(8 + 3*I) - (2 + I) == 6 + 2*I")], "$x = 8,\\ y = 3,\\ a = 2,\\ b = 1$")], "1.2")

ex("ex1.2", 6, "Show that $\\forall\\, z_1, z_2 \\in C$, $\\overline{z_1 z_2} = \\bar{z}_1 \\bar{z}_2$.", [P("", [
    S(r"z_1 = a + bi,\quad z_2 = c + di", "Let $z_1$ and $z_2$ be any two complex numbers ($a, b, c, d$ real).", "فرض کریں $z_1$ اور $z_2$ کوئی دو مختلط اعداد ہیں۔"),
    S(r"z_1 z_2 = (ac - bd) + (ad + bc)i", "Multiply.", "ضرب دیں۔", "expand((a + b*I)*(c + d*I)) == (a*c - b*d) + (a*d + b*c)*I"),
    S(r"\overline{z_1 z_2} = (ac - bd) - (ad + bc)i", "Conjugate: change the sign of the imaginary part.", "مزدوج: خیالی حصے کی علامت بدلیں۔"),
    S(r"\bar{z}_1 \bar{z}_2 = (a - bi)(c - di) = (ac - bd) - (ad + bc)i", "Multiply the conjugates.", "مزدوج اعداد کو ضرب دیں۔",
      "expand((a - b*I)*(c - d*I)) == (a*c - b*d) - (a*d + b*c)*I"),
    S(r"\therefore\ \overline{z_1 z_2} = \bar{z}_1 \bar{z}_2", "Both sides are the same complex number.", "دونوں اطراف ایک ہی مختلط عدد ہیں۔",
      "conjugate((a + b*I)*(c + d*I)) == (a - b*I)*(c - d*I)")], "proved: both sides equal $(ac - bd) - (ad + bc)i$")], "1.2")


def sqrt_part(label, z, draw=None):
    steps, root = sqrt_steps(z)
    steps.append(S(rf"\text{{The square roots are }} {ctex(root)} \text{{ and }} {ctex(-root)}", "The two roots are negatives of each other.",
                   "دونوں جذر ایک دوسرے کے منفی ہیں۔", f"({py(-root)})**2 == {py(z)}", draw=draw))
    return P(label, steps, rf"$\pm\left({ctex(root)}\right)$", prompt=f"${ctex(z)}$")


ex("ex1.2", 7, "Find the square root of the following complex numbers: (i) $-7-24i$ (ii) $8-6i$ (iii) $-15-36i$ (iv) $119+120i$", [
    sqrt_part("i", C(-7, -24)), sqrt_part("ii", C(8, -6)), sqrt_part("iii", C(-15, -36)), sqrt_part("iv", C(119, 120))], "1.2")


def argand(points):
    """Argand diagram: axes from -6 to 6, each point with dashed lines to the axes and its label."""
    from _gen import Graph
    g = Graph((-6, 6), (-5, 5), h=60, xstep=1, ystep=1)
    out = g.axes()
    for (x, y, lab) in points:
        X, Y = g.X(x), g.Y(y)
        out += [{"t": "line", "p": [X, Y, X, g.Y(0)], "dash": True}, {"t": "line", "p": [X, Y, g.X(0), Y], "dash": True},
                {"t": "dot", "p": [X, Y]}, {"t": "text", "p": [X + (1.5 if x > 0 else -16), Y - 2], "s": lab}]
    return out


_r8 = C(5, -2 * sp.sqrt(3))
p8 = sqrt_part("", C(13, -20 * sp.sqrt(3)), draw=argand([(5, float(-2 * sp.sqrt(3)), "(5, -3.46)"), (-5, float(2 * sp.sqrt(3)), "(-5, 3.46)")]))
p8["steps"][-1]["en"] = ("The two roots are $5 - 2\\sqrt{3}i \\approx 5 - 3.46i$ and $-5 + 2\\sqrt{3}i \\approx -5 + 3.46i$; on the Argand diagram they are the points "
                         "$(5, -3.46)$ and $(-5, 3.46)$, opposite each other through the origin.")
p8["steps"][-1]["ur"] = "دونوں جذر $5 - 2\\sqrt{3}i$ اور $-5 + 2\\sqrt{3}i$ ہیں؛ آرگنڈ شکل میں یہ نقاط $(5, -3.46)$ اور $(-5, 3.46)$ ہیں، مبدا کے آمنے سامنے۔"
p8["prompt"] = ""
ex("ex1.2", 8, "Find the square root of $13 - 20\\sqrt{3}i$ and represent them on an Argand diagram.", [p8], "1.2", figure_h=60)

ex("ex1.2", 9, "Find the real values of $x$ and $y$ if $(-7+i)(x+iy) + (-1-5i) = i(11-i)$.", [
    eq_parts("", r"(-7 + i)(x + iy) + (-1 - 5i) = i(11 - i)",
             [r"-7x - 7yi + xi + yi^2 - 1 - 5i = (-7x - y - 1) + (x - 7y - 5)i"],
             [r"i(11 - i) = 11i - i^2 = 1 + 11i"],
             "(-7 + I)*(x + I*y) + (-1 - 5*I)", "I*(11 - I)")], "1.2")
ex("ex1.2", 10, "Find the real values of $x$ and $y$ if $(5-2i)(x+iy) + 3 = i(11-i) - 4i$.", [
    eq_parts("", r"(5 - 2i)(x + iy) + 3 = i(11 - i) - 4i",
             [r"5x + 5yi - 2xi - 2yi^2 + 3 = (5x + 2y + 3) + (5y - 2x)i"],
             [r"i(11 - i) - 4i = 11i - i^2 - 4i = 1 + 7i"],
             "(5 - 2*I)*(x + I*y) + 3", "I*(11 - I) - 4*I")], "1.2")
ex("ex1.2", 11, "Find the real values of $u$ and $v$ if $\\frac{u-2}{2+i} + \\frac{v-3}{2-i} = 4i$.", [
    eq_parts("", r"\frac{u - 2}{2 + i} + \frac{v - 3}{2 - i} = 4i \;\Rightarrow\; (u - 2)(2 - i) + (v - 3)(2 + i) = 4i(2 + i)(2 - i)",
             [r"2u - ui - 4 + 2i + 2v + vi - 6 - 3i = (2u + 2v - 10) + (v - u - 1)i"],
             [r"(2 + i)(2 - i) = 4 - i^2 = 5 \quad (\text{the common denominator})", r"4i \times 5 = 20i"],
             "(u - 2)*(2 - I) + (v - 3)*(2 + I)", "4*I*(2 + I)*(2 - I)", names=("u", "v"))], "1.2")

ex("ex1.2", 12, "If $z_1 = 4+5i$ and $z_2 = \\alpha - 2i$, find the real values of $\\alpha$ such that $\\operatorname{Re}(z_1 z_2) = 20$.", [P("", [
    S(r"z_1 z_2 = (4 + 5i)(\alpha - 2i) = 4\alpha - 8i + 5\alpha i - 10i^2", "Multiply each term.", "ہر رکن کو ضرب دیں۔",
      "expand((4 + 5*I)*(q - 2*I)) == 4*q - 8*I + 5*q*I + 10"),
    S(r"= (4\alpha + 10) + (5\alpha - 8)i", "Put $i^2 = -1$ and collect parts.", "$i^2 = -1$ رکھ کر حصے اکٹھے کریں۔"),
    S(r"\operatorname{Re}(z_1 z_2) = 4\alpha + 10 = 20 \Rightarrow 4\alpha = 10 \Rightarrow \alpha = \frac{5}{2}", "The real part must be 20.",
      "حقیقی حصہ 20 ہونا چاہیے۔", "4*R(5,2) + 10 == 20", "re((4 + 5*I)*(R(5,2) - 2*I)) == 20")], "$\\alpha = \\frac{5}{2}$")], "1.2")


# Exercises 1.3-1.5 are written in their own files and run here, in this module's namespace (same ex(), note(), helpers).
_HERE = pathlib.Path(__file__).resolve().parent
for _part in ("_ex13.py", "_ex14.py", "_ex15.py"):
    if (_HERE / _part).exists():
        exec(compile((_HERE / _part).read_text(encoding="utf-8"), str(_HERE / _part), "exec"))
