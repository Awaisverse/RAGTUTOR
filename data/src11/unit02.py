"""Class 11, Unit 2 - Functions and Graphs (Punjab/PECTAA, 2025): Exercises 2.1 and 2.2.

Question statements: three solution sets (Mehreen Kanwal & Rana Ali Hasan, typed; Ammar Mujahid, whose pages quote the
textbook's own question text; handwritten notes of Exercise 2.1). Every answer was also worked out independently with
sympy; where the sets differ, the textbook's printed text is followed and the difference is noted on the part. Ammar's
"Q11-Q13" (cube root graph, stock growth, pollutant) are the textbook's Examples 11-13, not exercise questions.
Every step is checked with sympy.
"""
import math
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src10"))
from _gen import Graph, table_step  # noqa: E402
from _helpers import P, Q, S  # noqa: E402

UNIT = {"unit": 2, "title": "Functions and Graphs", "title_ur": "تفاعلات اور گراف", "class": 11, "items": []}
ITEMS = UNIT["items"]
R = sp.Rational
X = sp.Symbol("x")
L = sp.latex


def ex(eid, number, question, parts, exercise, figure_h=None):
    it = Q(f"c11-{eid}-q{number}", "exercise", number, 0, question, parts, exercise=exercise)
    if figure_h:
        it["figure_h"] = figure_h
    ITEMS.append(it)
    return it


def note(part, en, ur):
    part["key_note"] = {"en": en, "ur": ur}
    return part


def sgn(v):
    return "+" if v >= 0 else "-"


def ps(v):
    return "(" + sp.sstr(sp.nsimplify(v)) + ")"


def near(expr, value, k):
    return f"Abs(({expr}) - ({value})) <= {0.5 * 10 ** (-k) + 1e-9}"


def rows(label, prompt, rs, answer):
    """Steps given as (math, en, ur, checks[, drawing])."""
    return P(label, [S(r[0], r[1], r[2], *r[3], draw=r[4] if len(r) > 4 else None) for r in rs], answer, prompt=prompt)


def relabel(cmds, xl, yl, notes=()):
    """Name the axes (instead of x and y) and add curve labels [(x, y, text)] given in figure units."""
    out = [dict(c, s={"x": xl, "y": yl}[c["s"]]) if c.get("t") == "text" and c.get("s") in ("x", "y") else c for c in cmds]
    return out + [{"t": "text", "p": [px, py], "s": s} for px, py, s in notes]


def cbrt(v):
    return math.copysign(abs(v) ** (1 / 3), v)


def pcurve(g, fn, n=160):
    """Polyline of y = fn(x) inside the graph window (fn is a plain Python function)."""
    out, pts = [], []
    for j in range(n + 1):
        x = g.x0 + (g.x1 - g.x0) * j / n
        try:
            y = fn(x)
        except (ValueError, ZeroDivisionError, OverflowError):
            y = None
        if y is not None and g.y0 <= y <= g.y1:
            pts += [g.X(x), g.Y(y)]
        else:
            if len(pts) >= 4:
                out.append({"t": "poly", "p": pts})
            pts = []
    if len(pts) >= 4:
        out.append({"t": "poly", "p": pts})
    return out


# ================================================================================================== Exercise 2.1

ex("ex2.1", 1, "Given that: (a) $f(x) = x^2 - 1$ (b) $f(x) = \\sqrt{2x + 3}$. Find: (i) $f(-3)$ (ii) $f(0)$ (iii) $f(x - 2)$ (iv) $f(x^2 + 3)$", [
    rows("a", "$f(x) = x^2 - 1$", [
        (r"\text{(i)}\ f(-3) = (-3)^2 - 1 = 9 - 1 = 8", "Put $x = -3$ in the rule $f(x) = x^2 - 1$.", "قاعدہ $f(x) = x^2 - 1$ میں $x = -3$ رکھیں۔", ["(-3)**2 - 1 == 8"]),
        (r"\text{(ii)}\ f(0) = 0^2 - 1 = -1", "Put $x = 0$.", "$x = 0$ رکھیں۔", ["0**2 - 1 == -1"]),
        (r"\text{(iii)}\ f(x - 2) = (x - 2)^2 - 1 = x^2 - 4x + 4 - 1 = x^2 - 4x + 3", "Replace every $x$ by $(x - 2)$ and expand.",
         "ہر $x$ کی جگہ $(x - 2)$ رکھ کر پھیلائیں۔", ["expand((x - 2)**2 - 1) == x**2 - 4*x + 3"]),
        (r"\text{(iv)}\ f(x^2 + 3) = (x^2 + 3)^2 - 1 = x^4 + 6x^2 + 9 - 1 = x^4 + 6x^2 + 8", "Replace every $x$ by $(x^2 + 3)$ and expand.",
         "ہر $x$ کی جگہ $(x^2 + 3)$ رکھ کر پھیلائیں۔", ["expand((x**2 + 3)**2 - 1) == x**4 + 6*x**2 + 8"])],
        "(i) $8$; (ii) $-1$; (iii) $x^2 - 4x + 3$; (iv) $x^4 + 6x^2 + 8$"),
    rows("b", "$f(x) = \\sqrt{2x + 3}$", [
        (r"\text{(i)}\ f(-3) = \sqrt{2(-3) + 3} = \sqrt{-6 + 3} = \sqrt{-3}", "Put $x = -3$: the number under the root is negative, so $f(-3)$ is not a real number ($-3$ is not in the domain $x \\ge -\\frac{3}{2}$).",
         "$x = -3$ رکھیں: جذر کے نیچے منفی عدد آتا ہے، اس لیے $f(-3)$ حقیقی عدد نہیں ($-3$ ڈومین $x \\ge -\\frac{3}{2}$ میں نہیں)۔", ["2*(-3) + 3 == -3"]),
        (r"\text{(ii)}\ f(0) = \sqrt{2(0) + 3} = \sqrt{3}", "Put $x = 0$.", "$x = 0$ رکھیں۔", ["sqrt(2*0 + 3) == sqrt(3)"]),
        (r"\text{(iii)}\ f(x - 2) = \sqrt{2(x - 2) + 3} = \sqrt{2x - 4 + 3} = \sqrt{2x - 1}", "Replace $x$ by $(x - 2)$ under the root and simplify.",
         "جذر کے نیچے $x$ کی جگہ $(x - 2)$ رکھ کر سادہ کریں۔", ["expand(2*(x - 2) + 3) == 2*x - 1"]),
        (r"\text{(iv)}\ f(x^2 + 3) = \sqrt{2(x^2 + 3) + 3} = \sqrt{2x^2 + 6 + 3} = \sqrt{2x^2 + 9}", "Replace $x$ by $(x^2 + 3)$ under the root and simplify.",
         "جذر کے نیچے $x$ کی جگہ $(x^2 + 3)$ رکھ کر سادہ کریں۔", ["expand(2*(x**2 + 3) + 3) == 2*x**2 + 9"])],
        "(i) $\\sqrt{-3}$, undefined in $\\mathbb{R}$; (ii) $\\sqrt{3}$; (iii) $\\sqrt{2x - 1}$; (iv) $\\sqrt{2x^2 + 9}$")], "2.1")


ex("ex2.1", 2, "Find $\\frac{f(a+h) - f(a)}{h}$ and simplify where: (i) $f(x) = 4x + 7$ (ii) $f(x) = \\sin x$ (iii) $f(x) = x^3 + x^2 - 1$ (iv) $f(x) = \\tan x$", [
    rows("i", "$f(x) = 4x + 7$", [
        (r"f(a + h) = 4(a + h) + 7 = 4a + 4h + 7,\quad f(a) = 4a + 7", "Put $x = a + h$ and $x = a$ in the rule.", "قاعدے میں $x = a + h$ اور $x = a$ رکھیں۔",
         ["expand(4*(a + h) + 7) == 4*a + 4*h + 7"]),
        (r"\frac{f(a + h) - f(a)}{h} = \frac{4a + 4h + 7 - 4a - 7}{h} = \frac{4h}{h}", "Subtract; $4a$ and $7$ cancel.", "تفریق کریں؛ $4a$ اور $7$ کٹ جاتے ہیں۔", []),
        (r"= 4 \quad (h \ne 0)", "Cancel $h$.", "$h$ کاٹ دیں۔", ["((4*(a + h) + 7) - (4*a + 7))/h == 4"])], "$4$"),
    rows("ii", "$f(x) = \\sin x$", [
        (r"\frac{f(a + h) - f(a)}{h} = \frac{\sin(a + h) - \sin a}{h}", "Put $x = a + h$ and $x = a$.", "$x = a + h$ اور $x = a$ رکھیں۔", []),
        (r"\sin P - \sin Q = 2\cos\frac{P + Q}{2}\sin\frac{P - Q}{2}", "Use the sum-to-product formula.", "مجموعے کو حاصل ضرب میں بدلنے کا کلیہ استعمال کریں۔", []),
        (r"\sin(a + h) - \sin a = 2\cos\left(\frac{2a + h}{2}\right)\sin\frac{h}{2} = 2\cos\left(a + \frac{h}{2}\right)\sin\frac{h}{2}", "Here $P = a + h$, $Q = a$.",
         "یہاں $P = a + h$، $Q = a$۔", ["sin(a + h) - sin(a) == 2*cos(a + h/2)*sin(h/2)"]),
        (r"\frac{f(a + h) - f(a)}{h} = \frac{2\cos\left(a + \frac{h}{2}\right)\sin\frac{h}{2}}{h},\quad h \ne 0", "Divide by $h$.", "$h$ سے تقسیم کریں۔",
         ["(sin(a + h) - sin(a))/h == 2*cos(a + h/2)*sin(h/2)/h"])], "$\\frac{2\\cos\\left(a + \\frac{h}{2}\\right)\\sin\\frac{h}{2}}{h}$"),
    rows("iii", "$f(x) = x^3 + x^2 - 1$", [
        (r"f(a + h) = (a + h)^3 + (a + h)^2 - 1 = a^3 + 3a^2h + 3ah^2 + h^3 + a^2 + 2ah + h^2 - 1", "Put $x = a + h$ and expand both powers.",
         "$x = a + h$ رکھ کر دونوں طاقتیں پھیلائیں۔", ["expand((a + h)**3 + (a + h)**2 - 1) == a**3 + 3*a**2*h + 3*a*h**2 + h**3 + a**2 + 2*a*h + h**2 - 1"]),
        (r"f(a + h) - f(a) = 3a^2h + 3ah^2 + h^3 + 2ah + h^2", "Subtract $f(a) = a^3 + a^2 - 1$.", "$f(a) = a^3 + a^2 - 1$ تفریق کریں۔",
         ["expand((a + h)**3 + (a + h)**2 - 1 - (a**3 + a**2 - 1)) == 3*a**2*h + 3*a*h**2 + h**3 + 2*a*h + h**2"]),
        (r"\frac{f(a + h) - f(a)}{h} = 3a^2 + 3ah + h^2 + 2a + h,\quad h \ne 0", "Every term has $h$: divide by $h$.", "ہر رکن میں $h$ ہے: $h$ سے تقسیم کریں۔",
         ["((a + h)**3 + (a + h)**2 - 1 - (a**3 + a**2 - 1))/h == 3*a**2 + 3*a*h + h**2 + 2*a + h"])], "$3a^2 + 3ah + h^2 + 2a + h$"),
    rows("iv", "$f(x) = \\tan x$", [
        (r"\frac{f(a + h) - f(a)}{h} = \frac{\tan(a + h) - \tan a}{h}", "Put $x = a + h$ and $x = a$.", "$x = a + h$ اور $x = a$ رکھیں۔", []),
        (r"\tan(a + h) - \tan a = \frac{\sin(a + h)}{\cos(a + h)} - \frac{\sin a}{\cos a} = \frac{\sin(a + h)\cos a - \cos(a + h)\sin a}{\cos(a + h)\cos a}", "Write $\\tan = \\frac{\\sin}{\\cos}$ and take the L.C.M.",
         "$\\tan = \\frac{\\sin}{\\cos}$ لکھ کر ذو اضعاف اقل لیں۔", ["tan(a + h) - tan(a) == (sin(a + h)*cos(a) - cos(a + h)*sin(a))/(cos(a + h)*cos(a))"]),
        (r"\sin(a + h)\cos a - \cos(a + h)\sin a = \sin\big((a + h) - a\big) = \sin h", "The numerator is $\\sin(P - Q) = \\sin P\\cos Q - \\cos P\\sin Q$.",
         "شمار کنندہ $\\sin(P - Q) = \\sin P\\cos Q - \\cos P\\sin Q$ ہے۔", ["sin(a + h)*cos(a) - cos(a + h)*sin(a) == sin(h)"]),
        (r"\frac{f(a + h) - f(a)}{h} = \frac{\sin h}{h\cos(a + h)\cos a},\quad h \ne 0", "Divide by $h$.", "$h$ سے تقسیم کریں۔",
         ["(tan(a + h) - tan(a))/h == sin(h)/(h*cos(a + h)*cos(a))"])], "$\\frac{\\sin h}{h\\cos(a + h)\\cos a}$")], "2.1")


ex("ex2.1", 3, "Express the following: (a) The area $A$ of a square as a function of its perimeter $P$. (b) The circumference $C$ of a circle as a function of its area $A$. "
   "(c) The surface area $S$ of a cube as a function of its volume $V$.", [
    rows("a", "Area $A$ of a square in terms of its perimeter $P$", [
        (r"P = 4s \Rightarrow s = \frac{P}{4}", "Let the side be $s$; the perimeter is $4s$.", "ضلع $s$ لیں؛ احاطہ $4s$ ہے۔", []),
        (r"A = s^2 = \left(\frac{P}{4}\right)^2 = \frac{P^2}{16}", "Area of a square is side squared.", "مربع کا رقبہ ضلع کا مربع ہے۔", ["(p/4)**2 == p**2/16"]),
        (r"A(P) = \frac{P^2}{16},\quad P > 0", "A length is positive.", "لمبائی مثبت ہوتی ہے۔", [])], "$A(P) = \\frac{P^2}{16}$, $P > 0$"),
    rows("b", "Circumference $C$ of a circle in terms of its area $A$", [
        (r"A = \pi r^2 \Rightarrow r = \sqrt{\frac{A}{\pi}}", "Let the radius be $r$; make $r$ the subject (take the positive root).", "رداس $r$ لیں؛ $r$ کو موضوع بنائیں (مثبت جذر)۔",
         ["pi*(sqrt(a/pi))**2 == a"]),
        (r"C = 2\pi r = 2\pi\sqrt{\frac{A}{\pi}} = 2\sqrt{\frac{\pi^2 A}{\pi}} = 2\sqrt{\pi A}", "Put $r$ in $C = 2\\pi r$ and take $\\pi$ under the root.",
         "$r$ کو $C = 2\\pi r$ میں رکھیں اور $\\pi$ کو جذر کے اندر لے جائیں۔", ["2*pi*sqrt(a/pi) == 2*sqrt(pi*a)"]),
        (r"C(A) = 2\sqrt{\pi A},\quad A > 0", "An area is positive.", "رقبہ مثبت ہوتا ہے۔", [])], "$C(A) = 2\\sqrt{\\pi A}$, $A > 0$"),
    rows("c", "Surface area $S$ of a cube in terms of its volume $V$", [
        (r"V = s^3 \Rightarrow s = V^{1/3}", "Let the edge be $s$; take the cube root.", "کنارہ $s$ لیں؛ مکعب جذر لیں۔", ["(v**R(1,3))**3 == v"]),
        (r"S = 6s^2 = 6\left(V^{1/3}\right)^2 = 6V^{2/3}", "A cube has 6 square faces, each of area $s^2$.", "مکعب کے 6 مربع رخ ہیں، ہر ایک کا رقبہ $s^2$۔", ["6*(v**R(1,3))**2 == 6*v**R(2,3)"]),
        (r"S(V) = 6V^{2/3},\quad V > 0", "A volume is positive.", "حجم مثبت ہوتا ہے۔", [])], "$S(V) = 6V^{2/3}$, $V > 0$")], "2.1")


ex("ex2.1", 4, "Find the domain and the range of the function $g$ defined below: (i) $g(x) = 5 - x$ (ii) $g(x) = \\sqrt{x + 2}$ "
   "(iii) $g(x) = \\begin{cases} 6x + 7, & x \\le -2 \\\\ 4 - 3x, & x > -2 \\end{cases}$ (iv) $g(x) = |x - 5|$ (v) $g(x) = \\frac{x + 2}{3 - x}$", [
    rows("i", "$g(x) = 5 - x$", [
        (r"\text{Dom}(g) = \mathbb{R}", "$5 - x$ is defined for every real $x$.", "$5 - x$ ہر حقیقی $x$ کے لیے معین ہے۔", []),
        (r"y = 5 - x \Rightarrow x = 5 - y", "For the range, solve $y = g(x)$ for $x$.", "رینج کے لیے $y = g(x)$ سے $x$ معلوم کریں۔", ["5 - (5 - y) == y"]),
        (r"\text{Range}(g) = \mathbb{R}", "$x = 5 - y$ is real for every real $y$, so every real number is a value of $g$.", "ہر حقیقی $y$ کے لیے $x = 5 - y$ حقیقی ہے، اس لیے ہر حقیقی عدد $g$ کی قیمت ہے۔", [])],
        "Domain $\\mathbb{R}$; range $\\mathbb{R}$"),
    rows("ii", "$g(x) = \\sqrt{x + 2}$", [
        (r"x + 2 \ge 0 \Rightarrow x \ge -2", "A square root is real only when the number under it is not negative.", "جذر صرف تب حقیقی ہے جب اس کے نیچے عدد منفی نہ ہو۔", []),
        (r"\text{Dom}(g) = [-2, \infty)", "The domain.", "ڈومین۔", ["sqrt(-2 + 2) == 0"]),
        (r"\sqrt{x + 2} \ge 0;\quad y \ge 0 \Rightarrow x = y^2 - 2 \ge -2", "A square root is never negative, and every $y \\ge 0$ comes from $x = y^2 - 2$.",
         "جذر کبھی منفی نہیں، اور ہر $y \\ge 0$ کے لیے $x = y^2 - 2$ ملتا ہے۔", ["sqrt((y**2 - 2) + 2) == y"]),
        (r"\text{Range}(g) = [0, \infty)", "The range.", "رینج۔", [])], "Domain $[-2, \\infty)$; range $[0, \\infty)$"),
    rows("iii", "$g(x) = 6x + 7$ for $x \\le -2$, $4 - 3x$ for $x > -2$", [
        (r"\text{Dom}(g) = (-\infty, -2] \cup (-2, \infty) = \mathbb{R}", "The two pieces together cover every real $x$.", "دونوں حصے مل کر ہر حقیقی $x$ کو شامل کرتے ہیں۔", []),
        (r"x \le -2:\ 6x + 7 \le 6(-2) + 7 = -5 \Rightarrow (-\infty, -5]", "First piece: $6x + 7$ increases, so its largest value is at $x = -2$.",
         "پہلا حصہ: $6x + 7$ بڑھتا ہے، اس لیے سب سے بڑی قیمت $x = -2$ پر ہے۔", ["6*(-2) + 7 == -5"]),
        (r"x > -2:\ 4 - 3x < 4 - 3(-2) = 10 \Rightarrow (-\infty, 10)", "Second piece: $4 - 3x$ decreases, so it stays below its value $10$ at $x = -2$ (not reached).",
         "دوسرا حصہ: $4 - 3x$ گھٹتا ہے، اس لیے $x = -2$ والی قیمت $10$ سے کم رہتا ہے (10 تک نہیں پہنچتا)۔", ["4 - 3*(-2) == 10"]),
        (r"\text{Range}(g) = (-\infty, -5] \cup (-\infty, 10) = (-\infty, 10)", "Join the two sets of values.", "دونوں سیٹ ملائیں۔", [])],
        "Domain $\\mathbb{R}$; range $(-\\infty, 10)$"),
    rows("iv", "$g(x) = |x - 5|$", [
        (r"\text{Dom}(g) = \mathbb{R}", "$|x - 5|$ is defined for every real $x$.", "$|x - 5|$ ہر حقیقی $x$ کے لیے معین ہے۔", []),
        (r"|x - 5| \ge 0;\quad y \ge 0 \Rightarrow x = 5 + y \text{ gives } |x - 5| = y", "An absolute value is never negative, and every $y \\ge 0$ is reached.",
         "مطلق قیمت کبھی منفی نہیں، اور ہر $y \\ge 0$ حاصل ہوتا ہے۔", ["Abs((5 + y) - 5) == y"]),
        (r"\text{Range}(g) = [0, \infty)", "The range.", "رینج۔", [])], "Domain $\\mathbb{R}$; range $[0, \\infty)$"),
    rows("v", "$g(x) = \\frac{x + 2}{3 - x}$", [
        (r"3 - x \ne 0 \Rightarrow x \ne 3;\quad \text{Dom}(g) = \mathbb{R} \setminus \{3\}", "A fraction is undefined when its denominator is zero.", "نسب نما صفر ہو تو کسر معین نہیں۔", []),
        (r"y = \frac{x + 2}{3 - x} \Rightarrow 3y - xy = x + 2 \Rightarrow x(1 + y) = 3y - 2", "Solve $y = g(x)$ for $x$: cross-multiply and collect the $x$ terms.",
         "$y = g(x)$ سے $x$ معلوم کریں: طرفین کی ضرب کر کے $x$ والے ارکان اکٹھے کریں۔", []),
        (r"x = \frac{3y - 2}{y + 1},\quad y \ne -1", "Divide by $1 + y$; this needs $y \\ne -1$.", "$1 + y$ سے تقسیم کریں؛ اس کے لیے $y \\ne -1$۔",
         ["simplify((((3*y - 2)/(y + 1)) + 2)/(3 - (3*y - 2)/(y + 1))) == y"]),
        (r"y = -1:\ \frac{x + 2}{3 - x} = -1 \Rightarrow x + 2 = x - 3 \Rightarrow 2 = -3 \ (\text{impossible})", "The value $-1$ is never reached.", "قیمت $-1$ کبھی حاصل نہیں ہوتی۔", []),
        (r"\text{Range}(g) = \mathbb{R} \setminus \{-1\}", "The range.", "رینج۔", [])], "Domain $\\mathbb{R} \\setminus \\{3\\}$; range $\\mathbb{R} \\setminus \\{-1\\}$")], "2.1")


ex("ex2.1", 5, "Given $f(x) = x^3 - ax^2 + bx + 1$. If $f(2) = -3$ and $f(-1) = 0$, find the values of $a$ and $b$.", [
    rows("", "", [
        (r"f(2) = 8 - 4a + 2b + 1 = -3 \Rightarrow -4a + 2b = -12 \Rightarrow -2a + b = -6 \quad (1)", "Put $x = 2$ and use $f(2) = -3$.", "$x = 2$ رکھیں اور $f(2) = -3$ استعمال کریں۔",
         ["2**3 + 1 == 9", "9 - 12 == -3"]),
        (r"f(-1) = -1 - a - b + 1 = 0 \Rightarrow a + b = 0 \quad (2)", "Put $x = -1$ and use $f(-1) = 0$.", "$x = -1$ رکھیں اور $f(-1) = 0$ استعمال کریں۔", []),
        (r"(1) - (2):\ -3a = -6 \Rightarrow a = 2", "Subtract (2) from (1): $b$ cancels.", "(1) میں سے (2) تفریق کریں: $b$ کٹ جاتا ہے۔", []),
        (r"b = -a = -2", "Put $a = 2$ in (2).", "(2) میں $a = 2$ رکھیں۔", []),
        (r"\text{Check: } f(x) = x^3 - 2x^2 - 2x + 1:\ f(2) = -3,\ f(-1) = 0", "Both conditions hold.", "دونوں شرائط پوری ہوتی ہیں۔",
         ["2**3 - 2*2**2 - 2*2 + 1 == -3", "(-1)**3 - 2*(-1)**2 - 2*(-1) + 1 == 0"])], "$a = 2,\\ b = -2$")], "2.1")


Q6 = [
    rows("i", "Height at $x = 1,\\ 1.5,\\ 1.7$ s", [
        (r"h(1) = 40 - 10(1)^2 = 40 - 10 = 30 \text{ m}", "(a) Put $x = 1$.", "(a) $x = 1$ رکھیں۔", ["40 - 10*1**2 == 30"]),
        (r"h(1.5) = 40 - 10(2.25) = 40 - 22.5 = 17.5 \text{ m}", "(b) Put $x = 1.5$.", "(b) $x = 1.5$ رکھیں۔", ["40 - 10*R(3,2)**2 == R(35,2)"]),
        (r"h(1.7) = 40 - 10(2.89) = 40 - 28.9 = 11.1 \text{ m}", "(c) Put $x = 1.7$.", "(c) $x = 1.7$ رکھیں۔", ["40 - 10*R(17,10)**2 == R(111,10)"])],
        "(a) $30$ m (b) $17.5$ m (c) $11.1$ m"),
    rows("ii", "When does the stone strike the ground?", [
        (r"h(x) = 0 \Rightarrow 40 - 10x^2 = 0", "On the ground the height is zero.", "زمین پر اونچائی صفر ہے۔", []),
        (r"x^2 = 4 \Rightarrow x = 2 \quad (x = -2 \text{ rejected: time is not negative})", "Solve; time cannot be negative.", "حل کریں؛ وقت منفی نہیں ہو سکتا۔", ["40 - 10*2**2 == 0"]),
        (r"\text{The stone strikes the ground after } 2 \text{ seconds}", "The answer.", "جواب۔", [])], "after $2$ seconds")]
note(Q6[0], "The book's wording says the stone falls from 60 m, but its formula gives $h(0) = 40$ m; the heights are worked from the printed formula "
            "$h(x) = 40 - 10x^2$, as in every solution set.",
     "کتاب میں 60 میٹر لکھا ہے مگر فارمولا $h(0) = 40$ میٹر دیتا ہے؛ اونچائیاں چھپے ہوئے فارمولے $h(x) = 40 - 10x^2$ سے نکالی گئی ہیں۔")
ex("ex2.1", 6, "A stone falls from a height of 60 m on the ground. The height $h$ after $x$ seconds is approximately given by $h(x) = 40 - 10x^2$. "
   "(i) What is the height of the stone when: (a) $x = 1$ sec (b) $x = 1.5$ sec (c) $x = 1.7$ sec? (ii) When does the stone strike the ground?", Q6, "2.1")


ex("ex2.1", 7, "Consider the function $f(x) = 3x - 5$. (i) Determine the domain and range of $f(x)$. (ii) Is the function $f$ one-to-one? Justify your answer. "
   "(iii) Is the function onto if the codomain is all real numbers?", [
    rows("i", "Domain and range of $f(x) = 3x - 5$", [
        (r"\text{Dom}(f) = \mathbb{R}", "$3x - 5$ is defined for every real $x$.", "$3x - 5$ ہر حقیقی $x$ کے لیے معین ہے۔", []),
        (r"y = 3x - 5 \Rightarrow x = \frac{y + 5}{3}", "Solve for $x$: real for every real $y$.", "$x$ معلوم کریں: ہر حقیقی $y$ کے لیے حقیقی۔", ["3*((y + 5)/3) - 5 == y"]),
        (r"\text{Range}(f) = \mathbb{R}", "The range.", "رینج۔", [])], "Domain $\\mathbb{R}$; range $\\mathbb{R}$"),
    rows("ii", "Is $f$ one-to-one?", [
        (r"f(x_1) = f(x_2) \Rightarrow 3x_1 - 5 = 3x_2 - 5", "Suppose two inputs give the same output.", "فرض کریں دو داخلی قیمتیں ایک ہی نتیجہ دیتی ہیں۔", []),
        (r"3x_1 = 3x_2 \Rightarrow x_1 = x_2", "Add 5 and divide by 3.", "5 جمع کر کے 3 سے تقسیم کریں۔", []),
        (r"\text{So } f \text{ is one-to-one}", "Equal outputs only come from equal inputs: distinct elements have distinct images.", "برابر نتیجے صرف برابر داخلی قیمتوں سے آتے ہیں: مختلف ارکان کے عکس مختلف ہیں۔", [])],
        "one-to-one"),
    rows("iii", "Is $f$ onto $\\mathbb{R}$?", [
        (r"\text{Take any } y \in \mathbb{R}:\ x = \frac{y + 5}{3} \in \mathbb{R}", "For any real $y$ in the codomain, this $x$ is a real number.", "کوڈومین کے ہر حقیقی $y$ کے لیے یہ $x$ حقیقی عدد ہے۔", []),
        (r"f\left(\frac{y + 5}{3}\right) = 3\cdot\frac{y + 5}{3} - 5 = y", "It is mapped to $y$.", "یہ $y$ پر جاتا ہے۔", ["3*((y + 5)/3) - 5 == y"]),
        (r"\text{So } f \text{ is onto } \mathbb{R}", "Every element of the codomain is an image.", "کوڈومین کا ہر رکن کسی کا عکس ہے۔", [])], "onto")], "2.1")


ex("ex2.1", 8, "Let $f: \\mathbb{R} \\to \\mathbb{R}$ be defined by $f(x) = \\frac{2x - 3}{x + 1}$. (i) Find the domain and range of $f(x)$. (ii) Determine whether $f(x)$ is onto. "
   "(iii) Prove that $f(x)$ is one-to-one.", [
    rows("i", "Domain and range of $f(x) = \\frac{2x - 3}{x + 1}$", [
        (r"x + 1 \ne 0 \Rightarrow \text{Dom}(f) = \mathbb{R} \setminus \{-1\}", "The denominator cannot be zero.", "نسب نما صفر نہیں ہو سکتا۔", []),
        (r"y = \frac{2x - 3}{x + 1} \Rightarrow xy + y = 2x - 3 \Rightarrow x(y - 2) = -(y + 3)", "Solve $y = f(x)$ for $x$.", "$y = f(x)$ سے $x$ معلوم کریں۔", []),
        (r"x = \frac{y + 3}{2 - y},\quad y \ne 2", "Divide by $2 - y$; this needs $y \\ne 2$.", "$2 - y$ سے تقسیم کریں؛ اس کے لیے $y \\ne 2$۔",
         ["simplify((2*((y + 3)/(2 - y)) - 3)/((y + 3)/(2 - y) + 1)) == y"]),
        (r"y = 2:\ 2x - 3 = 2x + 2 \Rightarrow -3 = 2 \ (\text{impossible});\quad \text{Range}(f) = \mathbb{R} \setminus \{2\}", "The value 2 is never reached.", "قیمت 2 کبھی حاصل نہیں ہوتی۔", [])],
        "Domain $\\mathbb{R} \\setminus \\{-1\\}$; range $\\mathbb{R} \\setminus \\{2\\}$"),
    rows("ii", "Is $f$ onto $\\mathbb{R}$?", [
        (r"\text{Range}(f) = \mathbb{R} \setminus \{2\} \ne \mathbb{R}", "The codomain is $\\mathbb{R}$, but $2$ is not the image of any $x$.", "کوڈومین $\\mathbb{R}$ ہے، مگر $2$ کسی $x$ کا عکس نہیں۔", []),
        (r"\text{So } f \text{ is not onto}", "Onto needs every element of the codomain to be an image.", "پوشا ہونے کے لیے کوڈومین کا ہر رکن عکس ہونا ضروری ہے۔", [])], "not onto"),
    rows("iii", "Prove $f$ is one-to-one", [
        (r"f(x_1) = f(x_2) \Rightarrow \frac{2x_1 - 3}{x_1 + 1} = \frac{2x_2 - 3}{x_2 + 1}", "Suppose two inputs (both $\\ne -1$) give the same output.", "فرض کریں دو داخلی قیمتیں ($-1$ کے سوا) ایک ہی نتیجہ دیتی ہیں۔", []),
        (r"(2x_1 - 3)(x_2 + 1) = (2x_2 - 3)(x_1 + 1)", "Cross-multiply (the denominators are not zero).", "طرفین کی ضرب کریں (نسب نما صفر نہیں)۔", []),
        (r"2x_1x_2 + 2x_1 - 3x_2 - 3 = 2x_1x_2 + 2x_2 - 3x_1 - 3 \Rightarrow 5x_1 = 5x_2", "Expand; $2x_1x_2$ and $-3$ cancel; collect.", "پھیلائیں؛ $2x_1x_2$ اور $-3$ کٹ جاتے ہیں؛ اکٹھا کریں۔",
         ["expand((2*a - 3)*(b + 1) - (2*b - 3)*(a + 1)) == 5*a - 5*b"]),
        (r"x_1 = x_2 \Rightarrow f \text{ is one-to-one}", "Divide by 5.", "5 سے تقسیم کریں۔", [])], "one-to-one")], "2.1")


Q9 = rows("", "", [
    (r"\text{One-to-one: } e^{-x_1} = e^{-x_2} \Rightarrow \ln e^{-x_1} = \ln e^{-x_2} \Rightarrow -x_1 = -x_2 \Rightarrow x_1 = x_2", "Suppose two inputs give the same output and take $\\ln$ of both sides.",
     "فرض کریں دو داخلی قیمتیں ایک ہی نتیجہ دیتی ہیں اور دونوں اطراف کا $\\ln$ لیں۔", ["log(exp(-R(3,2))) == -R(3,2)"]),
    (r"\text{So } f \text{ is one-to-one}", "Distinct elements have distinct images.", "مختلف ارکان کے عکس مختلف ہیں۔", []),
    (r"\text{Onto: } y = e^{-x} \Rightarrow \ln y = -x \Rightarrow x = -\ln y = \ln\frac{1}{y}", "For a value $y$, solve $y = e^{-x}$ for $x$.", "قیمت $y$ کے لیے $y = e^{-x}$ سے $x$ معلوم کریں۔",
     ["exp(-(-log(R(1,2)))) == R(1,2)"]),
    (r"x > 0 \Rightarrow -x < 0 \Rightarrow 0 < e^{-x} < e^0 = 1", "But the inputs are only positive numbers, so every output lies between 0 and 1.",
     "مگر داخلی قیمتیں صرف مثبت ہیں، اس لیے ہر نتیجہ 0 اور 1 کے درمیان ہے۔", ["exp(-R(1,10)) < 1", "exp(-10) > 0"]),
    (r"0 < y < 1 \Rightarrow x = \ln\frac{1}{y} > 0 \text{ and } f(x) = y;\qquad y \ge 1 \Rightarrow x = -\ln y \le 0 \notin \mathbb{R}^+",
     "Each $y$ in $(0, 1)$ has a positive pre-image; a value such as $y = 2$ would need $x = -\\ln 2 < 0$, which is not allowed.",
     "$(0, 1)$ کی ہر $y$ کا مثبت عکس معکوس ہے؛ مگر $y = 2$ کے لیے $x = -\\ln 2 < 0$ چاہیے جو اجازت نہیں۔", ["-log(R(1,2)) > 0", "-log(2) < 0"]),
    (r"\text{Range}(f) = (0, 1):\quad f: \mathbb{R}^+ \to (0, 1) \text{ is one-to-one and onto (bijective)}",
     "So $f$ is a bijection from $\\mathbb{R}^+$ onto $(0, 1)$; it is not onto the whole of $\\mathbb{R}^+$.",
     "اس لیے $f$، $\\mathbb{R}^+$ سے $(0, 1)$ پر دو طرفہ تناظر ہے؛ یہ پورے $\\mathbb{R}^+$ پر پوشا نہیں۔", [])],
    "One-to-one; range $(0, 1)$, so $f$ is a bijection from $\\mathbb{R}^+$ onto $(0, 1)$ (it is not onto the whole of $\\mathbb{R}^+$)")
note(Q9, "The textbook prints $f(x) = e^{-x}$ on $\\mathbb{R}^+ \\to \\mathbb{R}^+$, as quoted in two solution sets; both of them call it bijective by taking "
         "$x = -\\ln y$, but that $x$ is positive only when $y < 1$. For $x > 0$ the values of $e^{-x}$ fill $(0, 1)$ only, so $f$ is one-to-one and a bijection onto "
         "$(0, 1)$, not onto all of $\\mathbb{R}^+$. The third (typed) set reads the function as $e^{x}$ and likewise finds it one-to-one but not onto $\\mathbb{R}^+$ "
         "(its range would be $(1, \\infty)$).",
     "کتاب میں $f(x) = e^{-x}$ ہے۔ دو حل میں $x = -\\ln y$ لے کر اسے دو طرفہ کہا گیا ہے، مگر یہ $x$ صرف $y < 1$ پر مثبت ہے؛ اس لیے $f$ یک یک ہے اور $(0, 1)$ پر دو طرفہ تناظر ہے، "
     "پورے $\\mathbb{R}^+$ پر نہیں۔ تیسرے حل میں $e^{x}$ پڑھا گیا ہے اور وہ بھی اسے یک یک مگر $\\mathbb{R}^+$ پر غیر پوشا پاتا ہے۔")
ex("ex2.1", 9, "Consider the function $f: \\mathbb{R}^+ \\to \\mathbb{R}^+$ defined by $f(x) = e^{-x}$. Show that $f(x)$ is a bijective.", [Q9], "2.1")


ex("ex2.1", 10, "Let $g: \\mathbb{R} \\to \\mathbb{R}$ be given by $g(x) = x^3 - 3x$. Determine if $g(x)$ is injective and/or surjective.", [
    rows("", "", [
        (r"g(x) = x^3 - 3x = x(x^2 - 3) = x\left(x - \sqrt{3}\right)\left(x + \sqrt{3}\right)", "Factorize to find where $g(x) = 0$.", "تجزی کر کے دیکھیں کہ $g(x) = 0$ کہاں ہے۔",
         ["expand(x*(x - sqrt(3))*(x + sqrt(3))) == x**3 - 3*x"]),
        (r"g(0) = g\left(\sqrt{3}\right) = g\left(-\sqrt{3}\right) = 0", "Three different inputs give the same output 0.", "تین مختلف داخلی قیمتیں ایک ہی نتیجہ 0 دیتی ہیں۔",
         ["0**3 - 3*0 == 0", "sqrt(3)**3 - 3*sqrt(3) == 0", "(-sqrt(3))**3 - 3*(-sqrt(3)) == 0"]),
        (r"\text{So } g \text{ is not injective (not one-to-one)}", "Distinct elements with the same image.", "مختلف ارکان کا ایک ہی عکس۔", []),
        (r"\text{Take any } y \in \mathbb{R}:\ x^3 - 3x - y = 0 \text{ is a cubic with real coefficients}", "For surjectivity we need a real $x$ with $g(x) = y$.",
         "پوشا ہونے کے لیے ایسا حقیقی $x$ چاہیے کہ $g(x) = y$۔", []),
        (r"x \to -\infty \Rightarrow g(x) \to -\infty,\quad x \to \infty \Rightarrow g(x) \to \infty", "A cubic is a continuous curve that runs from $-\\infty$ to $\\infty$, so it crosses every horizontal line $y = $ constant: every real cubic has a real root.",
         "مکعب منحنی مسلسل ہے جو $-\\infty$ سے $\\infty$ تک جاتی ہے، اس لیے ہر افقی خط کو کاٹتی ہے: ہر حقیقی مکعب مساوات کا کم از کم ایک حقیقی جذر ہے۔",
         ["(-10)**3 - 3*(-10) < 0", "10**3 - 3*10 > 0"]),
        (r"\text{So } g \text{ is surjective (onto } \mathbb{R}\text{), but not injective}", "Every real number is an image.", "ہر حقیقی عدد کسی کا عکس ہے۔", [])],
        "surjective but not injective")], "2.1")


# ================================================================================================== Exercise 2.2

def axes_meet(label, m, c, prompt):
    """Where the line y = m x + c meets the axes, with its graph."""
    m, c = sp.nsimplify(m), sp.nsimplify(c)
    f = m * X + c
    x0 = -c / m
    lo, hi = float(min(x0, 0)) - 2, float(max(x0, 0)) + 2
    ys = [float(f.subs(X, t)) for t in (lo, hi)] + [0.0]
    g = Graph((lo, hi), (min(ys) - 1, max(ys) + 1), h=70)
    lab = lambda v: str(v) if v.is_Integer else f"{v.p}/{v.q}"            # noqa: E731
    steps = [
        S(rf"x = 0:\ y = {L(c)}", "On the $y$-axis $x = 0$: put $x = 0$.", "$y$-محور پر $x = 0$: $x = 0$ رکھیں۔",
          f"({sp.sstr(f)}).subs(x, 0) == {ps(c)}"),
        S(rf"y = 0:\ 0 = {L(f)} \Rightarrow x = {L(x0)}", "On the $x$-axis $y = 0$: put $y = 0$ and solve.", "$x$-محور پر $y = 0$: $y = 0$ رکھ کر حل کریں۔",
          f"({sp.sstr(f)}).subs(x, {ps(x0)}) == 0"),
        S(rf"\text{{Plot }} \left({L(x0)}, 0\right) \text{{ and }} \left(0, {L(c)}\right) \text{{ and draw the line}}", "Two points fix a line: plot them and join; the line cuts the axes at these points.",
          "دو نقاط سے خط بنتا ہے: انہیں لگا کر ملائیں؛ خط انہی نقاط پر محوروں کو کاٹتا ہے۔",
          draw=g.axes() + g.curve(sp.sstr(f)) + g.point(float(x0), 0, f"({lab(x0)}, 0)") + g.point(0, float(c), f"(0, {lab(c)})"))]
    return P(label, steps, rf"$\left({L(x0)}, 0\right)$ and $\left(0, {L(c)}\right)$", prompt=prompt)


ex("ex2.2", 1, "Find the point of intersection of the coordinate axes and the following linear functions graphically: (i) $y = -5x + 10$ (ii) $y = 2x - 1$ "
   "(iii) $y = \\frac{1}{2}x - 3$ (iv) $y = 3x + \\frac{3}{2}$", [
    axes_meet("i", -5, 10, "$y = -5x + 10$"), axes_meet("ii", 2, -1, "$y = 2x - 1$"), axes_meet("iii", R(1, 2), -3, "$y = \\frac{1}{2}x - 3$"),
    axes_meet("iv", 3, R(3, 2), "$y = 3x + \\frac{3}{2}$")], "2.2", figure_h=70)


def _lb(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Rational else f"{float(v):.2f}"


def meet(label, fpy, gpy, prompt):
    """Point(s) where y = f(x) and y = g(x) meet: algebra for exact values, tables and a graph."""
    f, g_ = sp.sympify(fpy, locals={"x": X}), sp.sympify(gpy, locals={"x": X})
    d = sp.expand(f - g_)
    flip = sp.Poly(d, X).LC() < 0
    if flip:
        d = -d
    roots = sorted(set(sp.solve(d, X)), key=float)
    deg = sp.degree(d, X)
    pts = [(r, f.subs(X, r)) for r in roots]
    tangent = deg == 2 and len(roots) == 1
    steps = [S(rf"f(x) = g(x):\quad {L(f)} = {L(g_)}", "Where the graphs meet, both functions have the same $y$-value: set them equal.",
               "جہاں گراف ملتے ہیں وہاں دونوں تفاعل کی $y$-قیمت برابر ہے: انہیں برابر رکھیں۔")]
    if deg == 1:
        steps.append(S(rf"{L(d)} = 0 \Rightarrow x = {L(roots[0])}", "Collect the terms on one side and solve.", "ارکان ایک طرف اکٹھے کر کے حل کریں۔",
                       f"({sp.sstr(d)}).subs(x, {ps(roots[0])}) == 0"))
    elif not all(r.is_Rational for r in roots):
        A, B, C = sp.Poly(d, X).all_coeffs()
        shown = ",\\ ".join(f"x = {L(r)} \\approx {float(r):.2f}" for r in roots)
        steps.append(S(rf"{L(d)} = 0 \Rightarrow x = \frac{{{L(-B)} \pm \sqrt{{{L(B * B - 4 * A * C)}}}}}{{{L(2 * A)}}} \Rightarrow {shown}",
                       "Bring every term to one side" + (" (and multiply by $-1$)" if flip else "") + " and use the quadratic formula.",
                       "تمام ارکان ایک طرف لا کر" + (" ($-1$ سے ضرب دے کر)" if flip else "") + " دو درجی کلیہ استعمال کریں۔",
                       *[f"({sp.sstr(d)}).subs(x, {ps(r)}) == 0" for r in roots]))
    else:
        fac = sp.factor(d)
        shown = ",\\ ".join(f"x = {L(r)}" for r in roots)
        steps.append(S(rf"{L(d)} = 0 \Rightarrow {L(fac)} = 0 \Rightarrow {shown}",
                       "Bring every term to one side" + (" (and multiply by $-1$)" if flip else "") + " and factorize." + (" A repeated root: the graphs touch at one point." if tangent else ""),
                       "تمام ارکان ایک طرف لا کر" + (" ($-1$ سے ضرب دے کر)" if flip else "") + " تجزی کریں۔" + (" دہرا جذر: گراف ایک نقطے پر چھوتے ہیں۔" if tangent else ""),
                       f"expand({sp.sstr(fac)}) == {sp.sstr(d)}", *[f"({sp.sstr(d)}).subs(x, {ps(r)}) == 0" for r in roots]))
    steps.append(S(",\\quad ".join(rf"x = {L(r)}:\ y = {L(f.subs(X, r))}" for r in roots), "Put each $x$ in either function to get $y$ (both give the same value).",
                   "ہر $x$ کو کسی بھی تفاعل میں رکھ کر $y$ معلوم کریں (دونوں ایک ہی قیمت دیتے ہیں)۔",
                   *[f"({fpy}).subs(x, {ps(r)}) == ({gpy}).subs(x, {ps(r)})" for r in roots]))
    lo, hi = min(int(sp.floor(min(roots))) - 2, -1), max(int(sp.ceiling(max(roots))) + 2, 1)      # keep x = 0 (the y-axis) in view
    xs = list(range(lo, hi + 1))
    if len(xs) > 8:
        xs = xs[:: max(1, len(xs) // 7)]
    t1, y1 = table_step(fpy, xs, name="f(x)")
    t2, y2 = table_step(gpy, xs, name="g(x)")
    yv = [float(v) for v in y1 + y2] + [float(y) for _, y in pts] + [0.0]
    ylo, yhi = max(min(yv), float(min(y for _, y in pts)) - 12) - 1, min(max(yv), float(max(y for _, y in pts)) + 12) + 1
    gr = Graph((lo - 0.5, hi + 0.5), (ylo, yhi), h=70)
    draw = gr.axes() + gr.curve(fpy) + gr.curve(gpy)
    for r, y in pts:
        draw += gr.point(float(r), float(y), f"({_lb(r)}, {_lb(y)})")
    steps += [t1, t2,
              S(r"\text{Draw both graphs and read where they meet}", "Plot both tables on the same axes; the meeting point(s) agree with the algebra.",
                "دونوں جدول ایک ہی محوروں پر بنائیں؛ ملنے کے نقاط الجبرا سے ملتے ہیں۔", draw=draw)]
    ans = " and ".join(rf"$\left({L(r)}, {L(y)}\right)$" for r, y in pts) + (" (the graphs touch there)" if tangent else "")
    return P(label, steps, ans, prompt=prompt)


ex("ex2.2", 2, "Find the point(s) of intersection of the following functions graphically: (i) $f(x) = 2x + 5,\\ g(x) = -x + 5$ (ii) $f(x) = 3x - 2,\\ g(x) = 10 - x$ "
   "(iii) $f(x) = 2x - 4,\\ g(x) = 3x - 1$ (iv) $f(x) = -3x - 4,\\ g(x) = \\frac{1}{2}x + 3$ (v) $f(x) = x - 1,\\ g(x) = x^2 - 4x + 3$ "
   "(vi) $f(x) = 3x + 4,\\ g(x) = x^2 + 2x - 8$ (vii) $f(x) = -2x - 1,\\ g(x) = x^2 - 4x$ (viii) $f(x) = -x^2 - 3x + 2,\\ g(x) = x + 6$", [
    meet("i", "2*x + 5", "-x + 5", "$f(x) = 2x + 5,\\ g(x) = -x + 5$"),
    meet("ii", "3*x - 2", "10 - x", "$f(x) = 3x - 2,\\ g(x) = 10 - x$"),
    meet("iii", "2*x - 4", "3*x - 1", "$f(x) = 2x - 4,\\ g(x) = 3x - 1$"),
    meet("iv", "-3*x - 4", "x/2 + 3", "$f(x) = -3x - 4,\\ g(x) = \\frac{1}{2}x + 3$"),
    meet("v", "x - 1", "x**2 - 4*x + 3", "$f(x) = x - 1,\\ g(x) = x^2 - 4x + 3$"),
    meet("vi", "3*x + 4", "x**2 + 2*x - 8", "$f(x) = 3x + 4,\\ g(x) = x^2 + 2x - 8$"),
    meet("vii", "-2*x - 1", "x**2 - 4*x", "$f(x) = -2x - 1,\\ g(x) = x^2 - 4x$"),
    meet("viii", "-x**2 - 3*x + 2", "x + 6", "$f(x) = -x^2 - 3x + 2,\\ g(x) = x + 6$")], "2.2", figure_h=70)


def rgraph(label, py, fn, xs, reason, dom, rng, prompt, xr, yr, start=None):
    """Graph of a square-root or cube-root function: domain and range reasoning, a table (2 d.p.), the curve."""
    e = sp.sympify(py, locals={"x": X})
    vals = [sp.nsimplify(e.subs(X, t)) for t in xs]
    shown = [L(v) if v.is_Rational else f"{float(v):.2f}" for v in vals]
    at = lambda t: py.replace("x", ps(t))                 # noqa: E731  (the checker's x is a positive symbol: put the number in directly)
    checks = [(f"{at(t)} == {ps(v)}" if v.is_Rational else near(at(t), shown[i], 2)) for i, (t, v) in enumerate(zip(xs, vals))]
    g = Graph(xr, yr, h=70)
    draw = g.axes() + pcurve(g, fn) + sum((g.point(float(t), fn(float(t))) for t in xs if g.y0 <= fn(float(t)) <= g.y1), [])
    if start:
        draw += g.point(start[0], start[1], f"({start[0]:g}, {round(start[1], 2):g})")
    steps = [S(m, en, ur, *c) for m, en, ur, c in reason]
    steps.append(S(rf"\begin{{array}}{{c|{'c' * len(xs)}}} x & {' & '.join(L(sp.nsimplify(t)) for t in xs)} \\ \hline y & {' & '.join(shown)} \end{{array}}",
                   "Make a table of values (decimals to 2 places).", "قیمتوں کا جدول بنائیں (اعشاریہ کے بعد 2 ہندسے)۔", *checks))
    steps.append(S(r"\text{Plot the points and join them with a smooth curve}", "Plot the points and join them smoothly.", "نقاط لگا کر ہموار خم سے ملائیں۔", draw=draw))
    steps.append(S(rf"\text{{Domain}} = {dom},\quad \text{{Range}} = {rng}", "Read the domain and range.", "ڈومین اور رینج پڑھیں۔"))
    head = f"Domain ${dom}$; " + (rf"minimum point $\left({L(sp.nsimplify(start[0]))}, -\sqrt[3]{{\frac{{9}}{{4}}}}\right)$, so " if label == "vii" else "")
    return P(label, steps, head + rf"range ${rng}$", prompt=prompt)


SQ = "A square root is real only when the number under it is not negative."
SQU = "جذر صرف تب حقیقی ہے جب اس کے نیچے عدد منفی نہ ہو۔"
CB = "A cube root is real for every real number (positive, negative or zero)."
CBU = "مکعب جذر ہر حقیقی عدد کا حقیقی ہوتا ہے (مثبت، منفی یا صفر)۔"
c94 = sp.cbrt(R(9, 4))
ex("ex2.2", 3, "Graph the following functions: (i) $y = \\sqrt{3x}$ (ii) $y = \\sqrt{x} + 5$ (iii) $y = -\\frac{1}{2}\\sqrt{x}$ (iv) $y = -\\sqrt{x + 1} + 2$ "
   "(v) $y = \\sqrt[3]{2x + 1}$ (vi) $y = 2\\sqrt[3]{x} - 3$ (vii) $y = \\sqrt[3]{x^2 + x - 2}$", [
    rgraph("i", "sqrt(3*x)", lambda t: math.sqrt(3 * t), [0, 1, 2, 3, 4, 5],
           [(r"3x \ge 0 \Rightarrow x \ge 0", SQ, SQU, []), (r"\sqrt{3x} \ge 0", "A square root is never negative; it grows without end.", "جذر کبھی منفی نہیں؛ یہ بڑھتا ہی جاتا ہے۔", [])],
           r"[0, \infty)", r"[0, \infty)", "$y = \\sqrt{3x}$", (-1, 6), (-1, 5)),
    rgraph("ii", "sqrt(x) + 5", lambda t: math.sqrt(t) + 5, [0, 1, 4, 9],
           [(r"x \ge 0", SQ, SQU, []), (r"\sqrt{x} \ge 0 \Rightarrow \sqrt{x} + 5 \ge 5", "The root is never negative, so $y$ is never below 5.", "جذر منفی نہیں، اس لیے $y$ کبھی 5 سے کم نہیں۔", [])],
           r"[0, \infty)", r"[5, \infty)", "$y = \\sqrt{x} + 5$", (-1, 10), (-1, 9)),
    rgraph("iii", "-sqrt(x)/2", lambda t: -math.sqrt(t) / 2, [0, 1, 4, 9],
           [(r"x \ge 0", SQ, SQU, []), (r"\sqrt{x} \ge 0 \Rightarrow -\tfrac{1}{2}\sqrt{x} \le 0", "Multiplying by a negative number turns the inequality round.", "منفی عدد سے ضرب دینے پر عدم مساوات الٹ جاتی ہے۔", [])],
           r"[0, \infty)", r"(-\infty, 0]", "$y = -\\frac{1}{2}\\sqrt{x}$", (-1, 10), (-2, 1)),
    rgraph("iv", "-sqrt(x + 1) + 2", lambda t: -math.sqrt(t + 1) + 2, [-1, 0, 3, 8],
           [(r"x + 1 \ge 0 \Rightarrow x \ge -1", SQ, SQU, []),
            (r"\sqrt{x + 1} \ge 0 \Rightarrow -\sqrt{x + 1} + 2 \le 2", "The root is never negative, so $y$ is never above 2.", "جذر منفی نہیں، اس لیے $y$ کبھی 2 سے زیادہ نہیں۔", [])],
           r"[-1, \infty)", r"(-\infty, 2]", "$y = -\\sqrt{x + 1} + 2$", (-2, 9), (-2, 3), start=(-1, 2)),
    rgraph("v", "real_root(2*x + 1, 3)", lambda t: cbrt(2 * t + 1), [-5, -1, 0, 1, 4],
           [(r"2x + 1 \in \mathbb{R} \text{ for every real } x", CB, CBU, []),
            (r"y = \sqrt[3]{2x + 1} \Rightarrow x = \frac{y^3 - 1}{2}", "Every real $y$ comes from a real $x$.", "ہر حقیقی $y$ کسی حقیقی $x$ سے آتا ہے۔", ["real_root(2*((y**3 - 1)/2) + 1, 3) == y"])],
           r"\mathbb{R}", r"\mathbb{R}", "$y = \\sqrt[3]{2x + 1}$", (-6, 5), (-3, 3)),
    rgraph("vi", "2*real_root(x, 3) - 3", lambda t: 2 * cbrt(t) - 3, [-8, -1, 0, 1, 8],
           [(r"x \in \mathbb{R}", CB, CBU, []),
            (r"y = 2\sqrt[3]{x} - 3 \Rightarrow x = \left(\frac{y + 3}{2}\right)^3", "Every real $y$ comes from a real $x$.", "ہر حقیقی $y$ کسی حقیقی $x$ سے آتا ہے۔", ["2*real_root(((y + 3)/2)**3, 3) - 3 == y"])],
           r"\mathbb{R}", r"\mathbb{R}", "$y = 2\\sqrt[3]{x} - 3$", (-9, 9), (-8, 2)),
    rgraph("vii", "real_root(x**2 + x - 2, 3)", lambda t: cbrt(t * t + t - 2), [-4, -3, -2, -1, R(-1, 2), 0, 1, 2, 3],
           [(r"x^2 + x - 2 \in \mathbb{R} \text{ for every real } x", CB, CBU, []),
            (r"x^2 + x - 2 = \left(x + \tfrac{1}{2}\right)^2 - \tfrac{9}{4} \ge -\tfrac{9}{4}", "Complete the square: the inside is smallest, $-\\frac{9}{4}$, at $x = -\\frac{1}{2}$.",
             "مربع مکمل کریں: اندر کی قیمت $x = -\\frac{1}{2}$ پر سب سے کم، $-\\frac{9}{4}$، ہے۔", ["expand((x + R(1,2))**2 - R(9,4)) == x**2 + x - 2"]),
            (r"y \ge \sqrt[3]{-\tfrac{9}{4}} = -\sqrt[3]{\tfrac{9}{4}} \approx -1.31;\quad y = 0 \text{ at } x = -2,\ 1", "The cube root keeps the order, so $y$ is smallest there; the zeros come from $(x + 2)(x - 1) = 0$.",
             "مکعب جذر ترتیب نہیں بدلتا، اس لیے $y$ وہیں سب سے کم ہے؛ صفر $(x + 2)(x - 1) = 0$ سے۔",
             [near("-cbrt(R(9,4))", -1.31, 2), "expand((x + 2)*(x - 1)) == x**2 + x - 2"])],
           r"\mathbb{R}", r"\left[-\sqrt[3]{\frac{9}{4}}, \infty\right)", "$y = \\sqrt[3]{x^2 + x - 2}$", (-5, 4), (-2, 3), start=(-0.5, -float(c94)))],
   "2.2", figure_h=70)


s3 = sp.sqrt(3)
tq = 5 + 5 * s3
gq = Graph((0, 20), (0, 500), h=70)
Q24 = [
    rows("i", "When are the heights equal? When does the tree overtake the building?", [
        (r"T(t) = H(t):\ 50 + 10t + t^2 = 100 + 20t", "Same height: set the two functions equal.", "ایک جیسی اونچائی: دونوں تفاعل برابر رکھیں۔", []),
        (r"t^2 - 10t - 50 = 0", "Bring every term to one side.", "تمام ارکان ایک طرف لائیں۔", ["expand(50 + 10*t + t**2 - (100 + 20*t)) == t**2 - 10*t - 50"]),
        (r"t = \frac{10 \pm \sqrt{100 + 200}}{2} = \frac{10 \pm 10\sqrt{3}}{2} = 5 \pm 5\sqrt{3}", "Quadratic formula.", "دو درجی کلیہ۔",
         ["(5 + 5*sqrt(3))**2 - 10*(5 + 5*sqrt(3)) - 50 == 0", "(5 - 5*sqrt(3))**2 - 10*(5 - 5*sqrt(3)) - 50 == 0"]),
        (r"t = 5 + 5\sqrt{3} \approx 13.66 \text{ months} \quad (5 - 5\sqrt{3} < 0 \text{ rejected})", "Time is not negative.", "وقت منفی نہیں۔",
         [near("5 + 5*sqrt(3)", 13.66, 2), "5 - 5*sqrt(3) < 0"]),
        (r"\text{Draw } H(t) = 100 + 20t \text{ and } T(t) = 50 + 10t + t^2", "Sketch both graphs: the straight line and the parabola cross once for $t \\ge 0$.",
         "دونوں گراف بنائیں: سیدھا خط اور قطع مکافی $t \\ge 0$ پر ایک بار کٹتے ہیں۔",
         ["100 + 20*20 == 500", "50 + 10*20 + 20**2 == 650"],
         relabel(gq.axes() + gq.curve("100 + 20*x") + gq.curve("50 + 10*x + x**2") + gq.point(float(tq), float(100 + 20 * tq), "(13.66, 373.21)"),
                 "t", "h", [(gq.X(17.6), gq.Y(395), "H(t)"), (gq.X(13.2), gq.Y(470), "T(t)")])),
        (r"t > 5 + 5\sqrt{3}:\ T(t) - H(t) = t^2 - 10t - 50 > 0", "After that time the parabola is above the line: the tree is taller.", "اس کے بعد قطع مکافی خط سے اوپر ہے: درخت اونچا ہے۔",
         ["14**2 - 10*14 - 50 > 0", "13**2 - 10*13 - 50 < 0"])],
        "$t = 5 + 5\\sqrt{3} \\approx 13.66$ months; after that the tree is taller than the building"),
    rows("ii", "What will that height be?", [
        (r"H\left(5 + 5\sqrt{3}\right) = 100 + 20\left(5 + 5\sqrt{3}\right) = 100 + 100 + 100\sqrt{3}", "Put the time in $H(t)$ (or $T(t)$).", "وقت کو $H(t)$ (یا $T(t)$) میں رکھیں۔", []),
        (r"= 200 + 100\sqrt{3} \approx 373.21 \text{ m}", "Simplify.", "سادہ کریں۔",
         ["100 + 20*(5 + 5*sqrt(3)) == 200 + 100*sqrt(3)", "50 + 10*(5 + 5*sqrt(3)) + (5 + 5*sqrt(3))**2 == 200 + 100*sqrt(3)", near("200 + 100*sqrt(3)", 373.21, 2)])],
        "$200 + 100\\sqrt{3} \\approx 373.21$ m")]
ex("ex2.2", 4, "A building's height over time is modeled by $H(t) = 100 + 20t$ which is in metres and $t$ is the time in months. The height of a growing tree nearby is given by "
   "$T(t) = 50 + 10t + t^2$. (i) At what time will the building and tree have the same height? (ii) What will that height be? Sketch the graphs of both functions and "
   "determine the time when the tree will overtake the height of the building.", Q24, "2.2", figure_h=70)


gd = Graph((0, 10), (0, 220), h=70)
ex("ex2.2", 5, "A radioactive substance has a half-life of 2 years. If the initial quantity is 200 grams and the exponential decay function is "
   "$Q(t) = Q_0\\left(\\frac{1}{2}\\right)^{t/h}$, then find the remaining quantity after 6 years graphically.", [
    rows("", "", [
        (r"Q_0 = 200,\ h = 2:\quad Q(t) = 200\left(\frac{1}{2}\right)^{t/2}", "Put the initial quantity and the half-life in the model.", "ابتدائی مقدار اور نصف عمر ماڈل میں رکھیں۔", []),
        (r"\begin{array}{c|ccccc} t & 0 & 2 & 4 & 6 & 8 \\ \hline Q & 200 & 100 & 50 & 25 & 12.5 \end{array}", "Every 2 years the quantity halves.", "ہر 2 سال بعد مقدار آدھی رہ جاتی ہے۔",
         ["200*R(1,2)**0 == 200", "200*R(1,2)**1 == 100", "200*R(1,2)**2 == 50", "200*R(1,2)**3 == 25", "200*R(1,2)**4 == R(25,2)"]),
        (r"\text{Plot the points and draw the decay curve}", "Join the points with a smooth curve; read the value at $t = 6$.", "نقاط کو ہموار خم سے ملائیں؛ $t = 6$ پر قیمت پڑھیں۔", [],
         relabel(gd.axes() + gd.curve("200*(1/2)**(x/2)") + sum((gd.point(t, 200 * 0.5 ** (t / 2)) for t in (0, 2, 4, 8)), []) + gd.point(6, 25, "(6, 25)"),
                 "t", "Q", [(gd.X(2.6), gd.Y(140), "Q(t)")])),
        (r"Q(6) = 200\left(\frac{1}{2}\right)^3 = \frac{200}{8} = 25 \text{ g}", "The graph and the formula agree.", "گراف اور فارمولا ایک جیسا جواب دیتے ہیں۔", ["200*R(1,2)**(6/2) == 25"])],
        "$25$ g")], "2.2", figure_h=70)


# ================================================================================================== templates for new questions
# (used by engine11 for questions of these kinds with new numbers; every step carries sympy checks)

A_, H_ = sp.Symbol("a"), sp.Symbol("h")


def _sub_py(e, arg):
    """The rule with x replaced by (arg), as a sympy string (not simplified)."""
    return sp.sstr(e).replace("x", f"({sp.sstr(arg)})")


def fvalue(label, e, arg, prompt, name="f"):
    """f(arg) for the rule f(x) = e; arg is a number or an expression in x."""
    raw = sp.sympify(_sub_py(e, arg), evaluate=False)
    val = sp.expand(e.subs(X, arg))
    if arg.is_number:
        val = sp.nsimplify(sp.radsimp(val)) if val.is_real else val
        if not val.is_real:
            steps = [S(rf"{name}({L(arg)}) = {L(raw)}", f"Put $x = {L(arg)}$ in the rule.", f"قاعدے میں $x = {L(arg)}$ رکھیں۔"),
                     S(r"\text{The number under the square root is negative}", f"The square root of a negative number is not a real number, so ${L(arg)}$ is not in the domain of ${name}$.",
                       f"منفی عدد کا جذر حقیقی نہیں، اس لیے ${L(arg)}$، ${name}$ کے ڈومین میں نہیں۔", f"Abs(im({_sub_py(e, arg)})) > 0")]
            return P(label, steps, rf"${name}({L(arg)})$ is undefined in $\mathbb{{R}}$", prompt=prompt)
        how, howu = f"Put $x = {L(arg)}$ in the rule and simplify.", f"قاعدے میں $x = {L(arg)}$ رکھ کر سادہ کریں۔"
    else:
        how, howu = f"Replace every $x$ in the rule by $\\left({L(arg)}\\right)$ and simplify.", f"قاعدے میں ہر $x$ کی جگہ $\\left({L(arg)}\\right)$ رکھ کر سادہ کریں۔"
    steps = [S(rf"{name}\left({L(arg)}\right) = {L(raw)} = {L(val)}", how, howu, f"expand({_sub_py(e, arg)}) == {sp.sstr(val)}")]
    return P(label, steps, rf"${name}\left({L(arg)}\right) = {L(val)}$", prompt=prompt)


def diff_quotient(label, e, prompt):
    """(f(a + h) - f(a)) / h for a polynomial rule f(x) = e."""
    fa, fah = e.subs(X, A_), sp.expand(e.subs(X, A_ + H_))
    d = sp.expand(fah - fa)
    q = sp.expand(sp.cancel(d / H_))
    steps = [
        S(rf"f(a + h) = {L(fah)},\quad f(a) = {L(fa)}","Put $x = a + h$ (expand) and $x = a$ in the rule.",
          "قاعدے میں $x = a + h$ (پھیلا کر) اور $x = a$ رکھیں۔", f"expand({sp.sstr(e.subs(X, A_ + H_))}) == {sp.sstr(fah)}"),
        S(rf"f(a + h) - f(a) = {L(d)}", "Subtract: the terms without $h$ cancel.", "تفریق کریں: $h$ کے بغیر ارکان کٹ جاتے ہیں۔", f"expand(({sp.sstr(fah)}) - ({sp.sstr(fa)})) == {sp.sstr(d)}"),
        S(rf"\frac{{f(a + h) - f(a)}}{{h}} = {L(q)},\quad h \ne 0", "Every term has a factor $h$: divide by $h$.", "ہر رکن میں $h$ جزو ہے: $h$ سے تقسیم کریں۔",
          f"({sp.sstr(d)})/h == {sp.sstr(q)}")]
    return P(label, steps, rf"${L(q)}$", prompt=prompt)


def _iv(lo=None, hi=None, lo_in=True, hi_in=True):
    a = r"(-\infty" if lo is None else ("[" if lo_in else "(") + L(lo)
    b = r"\infty)" if hi is None else L(hi) + ("]" if hi_in else ")")
    return rf"\left{a[0]}{a[1:]}, {b[:-1]}\right{b[-1]}"


def dom_range(label, e, prompt, name="f"):
    """Domain and range of m x + c, p sqrt(m x + c) + k, p |m x + c| + k, or (a x + b)/(c x + d); None for other rules."""
    e = sp.expand(e) if e.is_polynomial(X) else e
    y = sp.Symbol("y")
    if e.is_polynomial(X) and sp.degree(e, X) == 1:
        m, c = sp.Poly(e, X).all_coeffs()
        xs = sp.solve(sp.Eq(e, y), X)[0]
        steps = [S(rf"\text{{Dom}}({name}) = \mathbb{{R}}", f"${L(e)}$ is defined for every real $x$.", f"${L(e)}$ ہر حقیقی $x$ کے لیے معین ہے۔"),
                 S(rf"y = {L(e)} \Rightarrow x = {L(xs)}", "For the range, solve for $x$: it is real for every real $y$.", "رینج کے لیے $x$ معلوم کریں: یہ ہر حقیقی $y$ کے لیے حقیقی ہے۔",
                   f"({sp.sstr(e)}).subs(x, {sp.sstr(xs)}) == y"),
                 S(rf"\text{{Range}}({name}) = \mathbb{{R}}", "Every real number is a value.", "ہر حقیقی عدد ایک قیمت ہے۔")]
        return P(label, steps, r"Domain $\mathbb{R}$; range $\mathbb{R}$", prompt=prompt)
    for kind in ("sqrt", "abs"):
        inner = [a for a in e.atoms(sp.Pow, sp.Abs) if (kind == "sqrt" and isinstance(a, sp.Pow) and a.exp == R(1, 2)) or (kind == "abs" and isinstance(a, sp.Abs))]
        if len(inner) != 1:
            continue
        w = inner[0]
        u = w.base if kind == "sqrt" else w.args[0]
        k = sp.nsimplify(e.subs(w, 0))
        p = sp.nsimplify(sp.simplify((e - k) / w))
        if not (u.is_polynomial(X) and sp.degree(u, X) == 1 and p.is_number and k.is_number and p != 0 and sp.simplify(p * w + k - e) == 0):
            return None
        m, c = sp.Poly(u, X).all_coeffs()
        b = -c / m
        rng = _iv(lo=k) if p > 0 else _iv(hi=k)
        up = p > 0
        if kind == "sqrt":
            dom = _iv(lo=b) if m > 0 else _iv(hi=b)
            steps = [S(rf"{L(u)} \ge 0 \Rightarrow x {'\\ge' if m > 0 else '\\le'} {L(b)}", SQ, SQU, f"({sp.sstr(u)}).subs(x, {ps(b)}) == 0"),
                     S(rf"\text{{Dom}}({name}) = {dom}", "The domain.", "ڈومین۔"),
                     S(rf"\sqrt{{{L(u)}}} \ge 0 \Rightarrow {L(e)} {'\\ge' if up else '\\le'} {L(k)}",
                       "A square root is never negative" + ("" if up else ", and it is multiplied by a negative number") + f"; the value ${L(k)}$ is reached at $x = {L(b)}$ and the root grows without end.",
                       "جذر کبھی منفی نہیں" + ("" if up else "، اور اسے منفی عدد سے ضرب دی گئی ہے") + f"؛ قیمت ${L(k)}$، $x = {L(b)}$ پر ملتی ہے اور جذر بڑھتا جاتا ہے۔",
                       f"({sp.sstr(e)}).subs(x, {ps(b)}) == {ps(k)}")]
        else:
            dom = r"\mathbb{R}"
            steps = [S(rf"\text{{Dom}}({name}) = \mathbb{{R}}", f"${L(e)}$ is defined for every real $x$.", f"${L(e)}$ ہر حقیقی $x$ کے لیے معین ہے۔"),
                     S(rf"\left|{L(u)}\right| \ge 0 \Rightarrow {L(e)} {'\\ge' if up else '\\le'} {L(k)}",
                       "An absolute value is never negative" + ("" if up else ", and it is multiplied by a negative number") + f"; the value ${L(k)}$ is reached at $x = {L(b)}$ and the size grows without end.",
                       "مطلق قیمت کبھی منفی نہیں" + ("" if up else "، اور اسے منفی عدد سے ضرب دی گئی ہے") + f"؛ قیمت ${L(k)}$، $x = {L(b)}$ پر ملتی ہے۔",
                       f"({sp.sstr(e)}).subs(x, {ps(b)}) == {ps(k)}")]
        steps.append(S(rf"\text{{Range}}({name}) = {rng}", "The range.", "رینج۔"))
        return P(label, steps, rf"Domain ${dom}$; range ${rng}$", prompt=prompt)
    num, den = sp.fraction(sp.together(e))
    if not (num.is_polynomial(X) and den.is_polynomial(X) and sp.degree(den, X) == 1 and sp.degree(num, X) <= 1):
        return None
    a, b = sp.Poly(num, X).all_coeffs() if sp.degree(num, X) == 1 else (0, num)
    c, d = sp.Poly(den, X).all_coeffs()
    if sp.simplify(a * d - b * c) == 0:
        return None
    x0, y0 = -d / c, sp.nsimplify(a / c)
    xs = sp.simplify((b - d * y) / (c * y - a))
    steps = [S(rf"{L(den)} \ne 0 \Rightarrow x \ne {L(x0)};\quad \text{{Dom}}({name}) = \mathbb{{R}} \setminus \{{{L(x0)}\}}", "A fraction is undefined when its denominator is zero.",
               "نسب نما صفر ہو تو کسر معین نہیں۔", f"({sp.sstr(den)}).subs(x, {ps(x0)}) == 0"),
             S(rf"y = {L(e)} \Rightarrow x = {L(xs)},\quad y \ne {L(y0)}", "Solve $y = f(x)$ for $x$ (cross-multiply and collect the $x$ terms); dividing needs the denominator non-zero.",
               "$y = f(x)$ سے $x$ معلوم کریں (طرفین کی ضرب، $x$ والے ارکان اکٹھے)؛ تقسیم کے لیے نسب نما غیر صفر ہو۔", f"simplify(({sp.sstr(e)}).subs(x, {sp.sstr(xs)})) == y"),
             S(rf"y = {L(y0)}:\ {L(num)} = {L(y0)}\left({L(den)}\right) \text{{ has no solution}}", f"The $x$ terms cancel and a false statement is left, so ${L(y0)}$ is never reached.",
               f"$x$ والے ارکان کٹ جاتے ہیں اور غلط بیان بچتا ہے، اس لیے ${L(y0)}$ کبھی حاصل نہیں ہوتا۔", f"expand(({sp.sstr(num)}) - ({sp.sstr(y0)})*({sp.sstr(den)})) == {sp.sstr(sp.expand(num - y0 * den))}"),
             S(rf"\text{{Range}}({name}) = \mathbb{{R}} \setminus \{{{L(y0)}\}}", "The range.", "رینج۔")]
    return P(label, steps, rf"Domain $\mathbb{{R}} \setminus \{{{L(x0)}\}}$; range $\mathbb{{R}} \setminus \{{{L(y0)}\}}$", prompt=prompt)
