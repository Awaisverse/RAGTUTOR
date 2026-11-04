"""Step templates for Class 11, Unit 1 (Complex Numbers), on top of the Class 10 complex-number templates.

Every step carries sympy checks. In checks, I is the imaginary unit and single letters are positive symbols, so a
cube root of unity is always written out as (-1 + sqrt(3)*I)/2, never as a letter.
"""
import math
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src10"))
from _complex import C, I, P, S, T, ans, ctex, exact, paren, py  # noqa: E402,F401

Z = sp.Symbol("z")
OMEGA = "((-1 + sqrt(3)*I)/2)"          # w in checks
OMEGA2 = "((-1 - sqrt(3)*I)/2)"


def L(x):
    return sp.latex(exact(x) if not isinstance(x, sp.Basic) or not x.free_symbols else x)


def ctex2(z):
    """x + iy where x or y may be a sum of surds: each part factored and the sign written once,
    e.g. \\frac{7(\\sqrt{2} + \\sqrt{6})}{4} - \\frac{7(\\sqrt{6} - \\sqrt{2})}{4}i."""
    z = exact(z)
    a, b = sp.re(z), sp.im(z)
    if not (a.is_Add or b.is_Add):
        return ctex(z)
    ta, tb = surd_tex(a), surd_tex(b)
    if b == 0:
        return ta
    neg = tb.startswith("-")
    tb = tb[1:].strip() if neg else tb
    if a == 0:
        return ("-" if neg else "") + tb + "i"
    return f"{ta} {'-' if neg else '+'} {tb}i"


def surd_tex(p):
    """A real number that is a sum of rational multiples of square roots, written with the common factor outside:
    7*sqrt(6)/4 + 7*sqrt(2)/4 -> \\frac{7}{4}\\left(\\sqrt{6} + \\sqrt{2}\\right); 5/2 - 9*sqrt(2)/2 -> \\frac{1}{2}\\left(5 - 9\\sqrt{2}\\right)."""
    p = sp.expand(p)
    if not p.is_Add:
        return sp.latex(p)
    terms = []
    for t in p.as_ordered_terms():
        c, rad = t.as_coeff_Mul()
        terms.append((sp.Rational(c), rad))
    terms.sort(key=lambda cr: (0 if cr[1] == 1 else 1, -float(cr[1])))
    g = sp.Rational(sp.gcd_list([abs(c.p) for c, _ in terms]), sp.ilcm(*[c.q for c, _ in terms]))
    sign = -1 if terms[0][0] < 0 else 1
    inner = ""
    for k, (c, rad) in enumerate(terms):
        m = c / (g * sign)
        body = (sp.latex(rad) if rad != 1 else "")
        coef = sp.latex(abs(m)) if (abs(m) != 1 or rad == 1) else ""
        piece = f"{coef}{body}"
        inner += (piece if m > 0 else "-" + piece) if k == 0 else (f" + {piece}" if m > 0 else f" - {piece}")
    head = ("-" if sign < 0 else "") + ("" if g == 1 else sp.latex(g))
    return rf"{head}\left({inner}\right)"


# ------------------------------------------------------------------------------------------ square roots


def sqrt_steps(z, names=("x", "y")):
    X_, Y_ = names
    """Square roots of z = x + iy by the formula sqrt(z) = +-(sqrt((|z|+x)/2) + i(y/|y|) sqrt((|z|-x)/2))."""
    x, y = sp.re(z), sp.im(z)
    m = sp.sqrt(x ** 2 + y ** 2)
    m = sp.nsimplify(m) if m.is_number else m
    sgn = 1 if y >= 0 else -1
    p = sp.sqrt(sp.radsimp((m + x) / 2))
    q = sp.sqrt(sp.radsimp((m - x) / 2))
    p, q = sp.radsimp(sp.sqrtdenest(p)), sp.radsimp(sp.sqrtdenest(q))
    root = exact(p + sgn * q * I)
    steps = [
        S(rf"z = {ctex(z)}:\quad {X_} = {L(x)},\ {Y_} = {L(y)}", f"Write $z = {X_} + i{Y_}$ and read off ${X_}$ and ${Y_}$.",
          f"$z = {X_} + i{Y_}$ لکھیں اور ${X_}$ اور ${Y_}$ پڑھ لیں۔"),
        S(rf"|z| = \sqrt{{{X_}^2 + {Y_}^2}} = \sqrt{{({L(x)})^2 + ({L(y)})^2}} = \sqrt{{{L(x ** 2 + y ** 2)}}} = {L(m)}",
          "Find the modulus of $z$.", "$z$ کا مقیاس معلوم کریں۔", f"sqrt(({py(x)})**2 + ({py(y)})**2) == {sp.sstr(m)}"),
        S(r"\sqrt{z} = \pm\left(\sqrt{\frac{|z| + X}{2}} + i\,\frac{Y}{|Y|}\sqrt{\frac{|z| - X}{2}}\right)".replace("X", X_).replace("Y", Y_),
          "Use the square-root formula; $\\frac{Y}{|Y|}$ is $+1$ when $Y > 0$ and $-1$ when $Y < 0$.".replace("Y", Y_),
          "جذر کا کلیہ استعمال کریں؛ $\\frac{Y}{|Y|}$ کی قیمت $Y > 0$ پر $+1$ اور $Y < 0$ پر $-1$ ہے۔".replace("Y", Y_)),
        S(rf"\sqrt{{{ctex(z)}}} = \pm\left(\sqrt{{\frac{{{L(m)} + ({L(x)})}}{{2}}}} {'+' if sgn > 0 else '-'} i\sqrt{{\frac{{{L(m)} - ({L(x)})}}{{2}}}}\right)",
          f"Substitute $|z| = {L(m)}$, ${X_} = {L(x)}$; here ${Y_} {'>' if sgn > 0 else '<'} 0$, so the sign inside is ${'+' if sgn > 0 else '-'}$.",
          f"$|z| = {L(m)}$ اور ${X_} = {L(x)}$ رکھیں؛ یہاں ${Y_} {'>' if sgn > 0 else '<'} 0$ ہے، اس لیے اندر کی علامت ${'+' if sgn > 0 else '-'}$ ہے۔"),
        S(rf"= \pm\left(\sqrt{{{L(sp.radsimp((m + x) / 2))}}} {'+' if sgn > 0 else '-'} i\sqrt{{{L(sp.radsimp((m - x) / 2))}}}\right) = \pm\left({ctex(root)}\right)",
          "Simplify each square root.", "ہر جذر کو سادہ کریں۔", f"({py(root)})**2 == {py(z)}"),
    ]
    return steps, root


# ------------------------------------------------------------------------------------------ polynomials


def factors_tex(roots, lead=1, var="z"):
    out = "" if lead == 1 else (L(lead) if lead != -1 else "-")
    for r in roots:
        out += rf"\left({var} {'-' if True else ''} {paren(r)}\right)" if False else rf"({var} {_minus(r)})"
    return out


def _minus(r):
    """z - r written neatly: z - 2, z + 3, z - 2i, z - (1 + i)."""
    r = exact(r)
    if sp.im(r) == 0:
        return f"- {L(r)}" if r >= 0 else f"+ {L(-r)}"
    if sp.re(r) == 0:
        b = sp.im(r)
        return f"- {ctex(r)}" if b > 0 else f"+ {ctex(-r)}"
    a, b = sp.re(r), sp.im(r)                         # z - (a + bi) = z - a - bi, written term by term
    re_part = f"- {L(a)}" if a > 0 else f"+ {L(-a)}"
    im_part = ctex(-b * I)
    return f"{re_part} {'- ' + im_part[1:].strip() if im_part.startswith('-') else '+ ' + im_part}"


def poly_py(expr):
    return sp.sstr(sp.expand(expr)).replace("z", "z")


def product_check(roots, lead, poly):
    prod = lead * sp.Mul(*[(Z - r) for r in roots])
    return f"expand({sp.sstr(prod)}) == {sp.sstr(sp.expand(poly))}"


def roots_answer(roots, var="z"):
    return "$" + var + " = " + ",\\ ".join(ctex(r) for r in roots) + "$"


# ------------------------------------------------------------------------------------------ polar form


def arg_of(z):
    """Principal argument in (-pi, pi], exact when possible."""
    return sp.simplify(sp.arg(exact(z)))


def cis(r, t, deg=False):
    t_tex = L(t) + (r"^\circ" if deg else "")
    rr = "" if r == 1 else L(r)
    return rf"{rr}\left(\cos {_wrap(t_tex)} + i\sin {_wrap(t_tex)}\right)"


def _wrap(t):
    return t if t.lstrip("-").replace("\\", "").isalnum() or t.startswith(r"\frac") and not t.startswith("-") else rf"\left({t}\right)"


def quadrant_name(z):
    x, y = sp.re(z), sp.im(z)
    if x > 0 and y >= 0:
        return "I"
    if x <= 0 and y > 0:
        return "II"
    if x < 0 and y <= 0:
        return "III"
    return "IV"
