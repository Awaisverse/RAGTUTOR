"""Step builders shared by several exercise files: fractions, averages between numbers, the field properties."""
from sympy import Rational

from _helpers import P, S, T


def tex_rat(r):
    """sympy Rational -> LaTeX (positive values)."""
    return str(int(r.p)) if r.q == 1 else rf"\frac{{{int(r.p)}}}{{{int(r.q)}}}"


def R(x):
    """sympy Rational -> text that the sympy checks can read."""
    return f"Rational({int(x.p)},{int(x.q)})"


def between_part(label, lo_tex, hi_tex, lo, hi, m1, m2):
    """Two rational numbers between lo and hi: the average of the two numbers, then the average of that and hi."""
    return P(label, [
        S(rf"\frac{{{lo_tex}+{hi_tex}}}{{2}} = {tex_rat(m1)}", "The average of two numbers lies between them. This is the first rational number.",
          "دو اعداد کا اوسط ان کے درمیان ہوتا ہے۔ یہ پہلا ناطق عدد ہے۔", f"({R(lo)}+{R(hi)})/2 == {R(m1)}"),
        S(rf"\frac{{{tex_rat(m1)}+{hi_tex}}}{{2}} = {tex_rat(m2)}", f"Take the average of {tex_rat(m1)} and the larger number to get a second rational number.",
          f"{tex_rat(m1)} اور بڑے عدد کا اوسط لیں، یہ دوسرا ناطق عدد ہے۔", f"({R(m1)}+{R(hi)})/2 == {R(m2)}"),
        T(f"Check: {lo_tex} < {tex_rat(m1)} < {tex_rat(m2)} < {hi_tex}.", f"تصدیق: {lo_tex} < {tex_rat(m1)} < {tex_rat(m2)} < {hi_tex}۔",
          f"{R(lo)} < {R(m1)}", f"{R(m1)} < {R(m2)}", f"{R(m2)} < {R(hi)}"),
    ], rf"${tex_rat(m1)}$ and ${tex_rat(m2)}$", prompt=rf"${lo_tex}$ and ${hi_tex}$")


def distributive_parts(a, b, c, first="i", second="ii"):
    """Verify a(b+c) = ab+ac and (a+b)c = ac+bc for the fractions a, b, c."""
    s_bc, s_ab = b + c, a + b
    left, right = a * s_bc, a * b + a * c
    left2, right2 = s_ab * c, a * c + b * c
    p1 = [
        S(rf"\text{{LHS}} = a(b+c) = {tex_rat(a)}\left({tex_rat(b)}+{tex_rat(c)}\right) = {tex_rat(a)}\left({tex_rat(s_bc)}\right) = {tex_rat(left)}",
          "First add inside the bracket, then multiply by a.", "پہلے قوسین کے اندر جمع کریں، پھر a سے ضرب دیں۔",
          f"{R(b)}+{R(c)} == {R(s_bc)}", f"{R(a)}*({R(s_bc)}) == {R(left)}"),
        S(rf"\text{{RHS}} = ab+ac = {tex_rat(a * b)}+{tex_rat(a * c)} = {tex_rat(right)}",
          "Multiply a by b and by c separately, then add.", "a کو b اور c سے الگ الگ ضرب دیں، پھر جمع کریں۔",
          f"{R(a)}*{R(b)} + {R(a)}*{R(c)} == {R(right)}"),
        T("LHS = RHS, so a(b+c) = ab+ac is verified.", "LHS = RHS ہے، لہذا a(b+c) = ab+ac کی تصدیق ہوگئی۔", f"{R(left)} == {R(right)}"),
    ]
    p2 = [
        S(rf"\text{{LHS}} = (a+b)c = \left({tex_rat(a)}+{tex_rat(b)}\right){tex_rat(c)} = {tex_rat(s_ab)}\cdot{tex_rat(c)} = {tex_rat(left2)}",
          "First add inside the bracket, then multiply by c.", "پہلے قوسین کے اندر جمع کریں، پھر c سے ضرب دیں۔",
          f"{R(a)}+{R(b)} == {R(s_ab)}", f"({R(s_ab)})*{R(c)} == {R(left2)}"),
        S(rf"\text{{RHS}} = ac+bc = {tex_rat(a * c)}+{tex_rat(b * c)} = {tex_rat(right2)}",
          "Multiply a by c and b by c separately, then add.", "a کو c سے اور b کو c سے الگ الگ ضرب دیں، پھر جمع کریں۔",
          f"{R(a)}*{R(c)} + {R(b)}*{R(c)} == {R(right2)}"),
        T("LHS = RHS, so (a+b)c = ac+bc is verified.", "LHS = RHS ہے، لہذا (a+b)c = ac+bc کی تصدیق ہوگئی۔", f"{R(left2)} == {R(right2)}"),
    ]
    return [P(first, p1, rf"Verified: ${tex_rat(left)} = {tex_rat(right)}$", prompt="Left distributive property"),
            P(second, p2, rf"Verified: ${tex_rat(left2)} = {tex_rat(right2)}$", prompt="Right distributive property")]


def associative_parts(a, b, c, first="i", second="ii"):
    """Verify a+(b+c) = (a+b)+c and a(bc) = (ab)c."""
    l1, r1 = a + (b + c), (a + b) + c
    l2, r2 = a * (b * c), (a * b) * c
    p1 = [
        S(rf"\text{{LHS}} = a+(b+c) = {tex_rat(a)}+\left({tex_rat(b)}+{tex_rat(c)}\right) = {tex_rat(a)}+{tex_rat(b + c)} = {tex_rat(l1)}",
          "Add b and c first, then add a.", "پہلے b اور c کو جمع کریں، پھر a جمع کریں۔", f"{R(b)}+{R(c)} == {R(b + c)}", f"{R(a)}+{R(b + c)} == {R(l1)}"),
        S(rf"\text{{RHS}} = (a+b)+c = \left({tex_rat(a)}+{tex_rat(b)}\right)+{tex_rat(c)} = {tex_rat(a + b)}+{tex_rat(c)} = {tex_rat(r1)}",
          "Add a and b first, then add c.", "پہلے a اور b کو جمع کریں، پھر c جمع کریں۔", f"{R(a)}+{R(b)} == {R(a + b)}", f"{R(a + b)}+{R(c)} == {R(r1)}"),
        T("LHS = RHS, so the associative property of addition is verified.", "LHS = RHS ہے، لہذا جمع کے لیے خاصیت تلازم کی تصدیق ہوگئی۔", f"{R(l1)} == {R(r1)}"),
    ]
    p2 = [
        S(rf"\text{{LHS}} = a(bc) = {tex_rat(a)}\left({tex_rat(b)} \cdot {tex_rat(c)}\right) = {tex_rat(a)} \cdot {tex_rat(b * c)} = {tex_rat(l2)}",
          "Multiply b and c first, then multiply by a.", "پہلے b اور c کو ضرب دیں، پھر a سے ضرب دیں۔", f"{R(b)}*{R(c)} == {R(b * c)}", f"{R(a)}*{R(b * c)} == {R(l2)}"),
        S(rf"\text{{RHS}} = (ab)c = \left({tex_rat(a)} \cdot {tex_rat(b)}\right){tex_rat(c)} = {tex_rat(a * b)} \cdot {tex_rat(c)} = {tex_rat(r2)}",
          "Multiply a and b first, then multiply by c.", "پہلے a اور b کو ضرب دیں، پھر c سے ضرب دیں۔", f"{R(a)}*{R(b)} == {R(a * b)}", f"{R(a * b)}*{R(c)} == {R(r2)}"),
        T("LHS = RHS, so the associative property of multiplication is verified.", "LHS = RHS ہے، لہذا ضرب کے لیے خاصیت تلازم کی تصدیق ہوگئی۔", f"{R(l2)} == {R(r2)}"),
    ]
    return [P(first, p1, rf"Verified: ${tex_rat(l1)} = {tex_rat(r1)}$", prompt="With respect to addition"),
            P(second, p2, rf"Verified: ${tex_rat(l2)} = {tex_rat(r2)}$", prompt="With respect to multiplication")]
