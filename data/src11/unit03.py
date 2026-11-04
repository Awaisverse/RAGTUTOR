"""Class 11, Unit 3 - Theory of Quadratic Functions (Punjab/PECTAA, 2025): Exercises 3.1 and 3.2.

Question statements: two typed/handwritten solution sets on MathCity (Mehreen Kanwal & Rana Ali Hasan; Ammar Mujahid, whose
pages quote the textbook's own question text). Every answer was also worked out independently with sympy; where the two
sets differ the textbook's printed text is followed and the difference is noted on the part. Every step is checked with sympy.
"""
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "src10"))
from _gen import Graph, table_step  # noqa: E402
from _helpers import P, Q, S, T  # noqa: E402

UNIT = {"unit": 3, "title": "Theory of Quadratic Functions", "title_ur": "دو درجی تفاعل کا نظریہ", "class": 11, "items": []}
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


def num(v):
    v = sp.nsimplify(v)
    return L(v)


def near(expr, value, k):
    return f"Abs(({expr}) - ({value})) <= {0.5 * 10 ** (-k) + 1e-9}"


def ps(v):
    return "(" + sp.sstr(sp.nsimplify(v)) + ")"


def poly_tex(a, b, c):
    return L(sp.nsimplify(a) * X ** 2 + sp.nsimplify(b) * X + sp.nsimplify(c))


# ================================================================================================== Exercise 3.1

def vertex_cs(label, a, b, c):
    """Maximum or minimum value of a x^2 + b x + c by completing the square."""
    a, b, c = sp.nsimplify(a), sp.nsimplify(b), sp.nsimplify(c)
    f = a * X ** 2 + b * X + c
    h = -b / (2 * a)
    k = f.subs(X, h)
    half = b / (2 * a)
    steps = []
    if a != 1:
        steps.append(S(rf"f(x) = {L(f)} = {L(a)}\left(x^2 {sgn(b / a)} {L(abs(b / a))}x\right) {sgn(c)} {L(abs(c))}",
                       f"Take ${L(a)}$ common from the two terms with $x$.", f"$x$ والے دونوں ارکان سے ${L(a)}$ مشترک لیں۔",
                       f"expand({L(a) if False else sp.sstr(a)}*(x**2 + ({sp.sstr(b / a)})*x) + ({sp.sstr(c)})) == {sp.sstr(f)}"))
    inner = rf"\left(x {sgn(half)} {L(abs(half))}\right)^2 - \left({L(abs(half))}\right)^2"
    steps.append(S(rf"f(x) = {'' if a == 1 else L(a)}\left[{inner}\right] {sgn(c)} {L(abs(c))}",
                   "Complete the square: add and subtract the square of half the coefficient of $x$.",
                   "مربع مکمل کریں: $x$ کے عددی سر کے نصف کا مربع جمع اور تفریق کریں۔",
                   f"expand(({sp.sstr(a)})*((x + ({sp.sstr(half)}))**2 - ({sp.sstr(half)})**2) + ({sp.sstr(c)})) == {sp.sstr(f)}"))
    vform = rf"{'' if a == 1 else ('-' if a == -1 else L(a))}\left(x {sgn(half)} {L(abs(half))}\right)^2 {sgn(k)} {L(abs(k))}"
    steps.append(S(rf"f(x) = {vform}", "Multiply out the bracket and collect the constants.", "قوسین کھول کر مستقل ارکان اکٹھے کریں۔",
                   f"expand(({sp.sstr(a)})*(x - ({sp.sstr(h)}))**2 + ({sp.sstr(k)})) == {sp.sstr(f)}"))
    kind = "minimum" if a > 0 else "maximum"
    steps.append(S(rf"\left(x {sgn(half)} {L(abs(half))}\right)^2 \ge 0 \Rightarrow f(x) {'\\ge' if a > 0 else '\\le'} {L(k)}",
                   f"A square is never negative{', and it is multiplied by a negative number' if a < 0 else ''}, so $f(x)$ is never {'below' if a > 0 else 'above'} ${L(k)}$.",
                   f"مربع کبھی منفی نہیں ہوتا{'، اور اسے منفی عدد سے ضرب دی گئی ہے' if a < 0 else ''}، اس لیے $f(x)$ کبھی ${L(k)}$ سے {'کم' if a > 0 else 'زیادہ'} نہیں ہوتا۔"))
    steps.append(S(rf"\text{{{kind.capitalize()} value}} = {L(k)} \text{{ at }} x = {L(h)}", f"The {kind} is reached when the square is zero, at $x = {L(h)}$.",
                   f"{'کم سے کم' if a > 0 else 'زیادہ سے زیادہ'} قیمت تب ملتی ہے جب مربع صفر ہو، یعنی $x = {L(h)}$ پر۔", f"({sp.sstr(f)}).subs(x, {ps(h)}) == {ps(k)}"))
    return P(label, steps, rf"{kind.capitalize()} value ${L(k)}$ at $x = {L(h)}$", prompt=f"$f(x) = {L(f)}$")


ex("ex3.1", 1, "Find the maximum or minimum value of the following quadratic functions by completing square: (i) $f(x) = x^2 + 6x + 13$ (ii) $f(x) = x^2 + 4x$ "
   "(iii) $f(x) = -x^2 + 8x + 13$ (iv) $f(x) = -x^2 - 3x - 5$ (v) $f(x) = 3x^2 + 6x - 13$ (vi) $f(x) = -2x^2 - x + 21$", [
       vertex_cs(l, a, b, c) for l, a, b, c in [("i", 1, 6, 13), ("ii", 1, 4, 0), ("iii", -1, 8, 13), ("iv", -1, -3, -5), ("v", 3, 6, -13), ("vi", -2, -1, 21)]], "3.1")


def sketch(label, a, b, c, prompt=None):
    a, b, c = sp.nsimplify(a), sp.nsimplify(b), sp.nsimplify(c)
    f = a * X ** 2 + b * X + c
    h = -b / (2 * a)
    k = f.subs(X, h)
    D = b * b - 4 * a * c
    roots = sorted(set(sp.solve(f, X)), key=float) if D >= 0 else []
    h0 = int(sp.floor(h))
    xs = [h0 + d for d in (-3, -2, -1, 0, 1, 2, 3)] + ([h0 + 4] if h != h0 else [])   # whole numbers around the vertex
    if roots:
        lo, hi = min([float(r) for r in roots] + [float(h) - 3]) - 1, max([float(r) for r in roots] + [float(h) + 3]) + 1
    else:
        lo, hi = float(h) - 4, float(h) + 4
    ys = [float(f.subs(X, t)) for t in (lo, hi, float(h))]
    g = Graph((lo, hi), (min(ys + [0]) - 1, max(ys + [0]) + 1), h=70)
    kind = "minimum" if a > 0 else "maximum"
    rng = rf"\left[{L(k)}, \infty\right)" if a > 0 else rf"\left(-\infty, {L(k)}\right]"
    tab, tys = table_step(sp.sstr(f), xs)
    steps = [
        S(rf"f(x) = {L(f)}:\ a = {L(a)},\ b = {L(b)},\ c = {L(c)}", f"Read off the coefficients; $a {'>' if a > 0 else '<'} 0$, so the parabola opens {'upwards' if a > 0 else 'downwards'} and has a {kind} point.",
          f"عددی سر پڑھیں؛ $a {'>' if a > 0 else '<'} 0$ ہے، اس لیے قطع مکافی {'اوپر' if a > 0 else 'نیچے'} کھلتا ہے اور اس کا {'کم سے کم' if a > 0 else 'زیادہ سے زیادہ'} نقطہ ہے۔"),
        S(rf"h = -\frac{{b}}{{2a}} = -\frac{{{L(b)}}}{{2({L(a)})}} = {L(h)},\quad k = f({L(h)}) = {L(k)}", "Find the vertex $(h, k)$: $h = -\\frac{b}{2a}$ and $k = f(h)$.",
          "راس $(h, k)$ معلوم کریں: $h = -\\frac{b}{2a}$ اور $k = f(h)$۔", f"-({sp.sstr(b)})/(2*({sp.sstr(a)})) == {ps(h)}", f"({sp.sstr(f)}).subs(x, {ps(h)}) == {ps(k)}"),
        {**tab, "draw": g.axes() + sum((g.point(float(t), float(v)) for t, v in zip(xs, tys) if g.y0 <= float(v) <= g.y1 and lo <= float(t) <= hi), [])},
        S(r"\text{Join the points with a smooth curve}", f"Plot the points and join them with a smooth curve symmetric about the axis $x = {L(h)}$.",
          f"نقاط لگا کر محور $x = {L(h)}$ کے گرد متناظر ہموار خم سے ملائیں۔",
          draw=g.curve(sp.sstr(f)) + g.point(float(h), float(k), f"({sp.nsimplify(h)}, {sp.nsimplify(k)})") + [{"t": "line", "p": [g.X(float(h)), 5, g.X(float(h)), 65], "dash": True}]),
        S(rf"\text{{{kind.capitalize()} point}} = \left({L(h)}, {L(k)}\right),\quad \text{{axis}}: x = {L(h)}", f"The vertex is the {kind} point of the graph.",
          f"راس گراف کا {'کم سے کم' if a > 0 else 'زیادہ سے زیادہ'} نقطہ ہے۔"),
        S(rf"\text{{Domain}} = \mathbb{{R}} = (-\infty, \infty),\quad \text{{Range}} = {rng}", f"Any real $x$ can be put in, so the domain is all real numbers; the values go {'up from' if a > 0 else 'down from'} ${L(k)}$.",
          f"ہر حقیقی $x$ رکھا جا سکتا ہے، اس لیے ڈومین تمام حقیقی اعداد ہیں؛ قیمتیں ${L(k)}$ سے {'اوپر' if a > 0 else 'نیچے'} جاتی ہیں۔",
          f"({sp.sstr(f)}).subs(x, {ps(h + 1)}) {'>' if a > 0 else '<'} {ps(k)}")]
    if roots:
        nice = all(r.is_Rational for r in roots)
        how = (rf"{L(sp.factor(f))} = 0" if nice else
               rf"x = \frac{{{L(-b)} \pm \sqrt{{{L(D)}}}}}{{{L(2 * a)}}}")
        shown = ",\\ ".join(f"x = {L(r)}" + ("" if r.is_Rational else rf" \approx {float(r):.2f}") for r in roots)
        steps.insert(2, S(rf"{how} \;\Rightarrow\; {shown}",
                          "The $x$-intercepts are where $f(x) = 0$: " + ("factorize." if nice else "use the quadratic formula (decimals help to plot)."),
                          "$x$-مقطع وہاں ہیں جہاں $f(x) = 0$: " + ("تجزی کریں۔" if nice else "دو درجی کلیہ استعمال کریں (اعشاریہ قیمتیں گراف بنانے میں مدد دیتی ہیں)۔"),
                          *[f"({sp.sstr(f)}).subs(x, {ps(r)}) == 0" for r in roots]))
    return P(label, steps, rf"{kind.capitalize()} point $\left({L(h)}, {L(k)}\right)$; domain $\mathbb{{R}}$; range ${rng}$", prompt=prompt or f"$f(x) = {L(f)}$")


ex("ex3.1", 2, "Find the maximum or minimum point by sketching the following quadratic functions. Also find their domain and range: (i) $f(x) = x^2 - 4x$ "
   "(ii) $f(x) = x^2 - 5x + 6$ (iii) $f(x) = -x^2 + 2x - 8$ (iv) $f(x) = x^2 - 4x + 4$ (v) $f(x) = x^2 + 2x - 8.3$ (vi) $f(x) = 6 - x - x^2$", [
       sketch("i", 1, -4, 0), sketch("ii", 1, -5, 6), sketch("iii", -1, 2, -8), sketch("iv", 1, -4, 4), sketch("v", 1, 2, R(-83, 10), "$f(x) = x^2 + 2x - 8.3$"),
       sketch("vi", -1, -1, 6, "$f(x) = 6 - x - x^2$")], "3.1", figure_h=70)


def inverse(label, a, b, c, p, rel, prompt, neat=None, given_vertex=False):
    """Inverse of a x^2 + b x + c on the side x rel p of the vertex (rel in '<=', '<', '>=', '>')."""
    a, b, c, p = sp.nsimplify(a), sp.nsimplify(b), sp.nsimplify(c), sp.nsimplify(p)
    f = a * X ** 2 + b * X + c
    h = -b / (2 * a)
    k = f.subs(X, h)
    left = rel in ("<=", "<")
    strict = rel in ("<", ">")
    s = -1 if left else 1
    finv = h + s * sp.sqrt((X - k) / a)
    fp = f.subs(X, p)
    if a > 0:
        rng = (rf"\left({L(fp)}, \infty\right)" if strict else rf"\left[{L(fp)}, \infty\right)")
    else:
        rng = (rf"\left(-\infty, {L(fp)}\right)" if strict else rf"\left(-\infty, {L(fp)}\right]")
    dom = (rf"\left(-\infty, {L(p)}\right{')' if strict else ']'}" if left else rf"\left{'(' if strict else '['}{L(p)}, \infty\right)")
    reltex = {"<=": r"\le", "<": "<", ">=": r"\ge", ">": ">"}[rel]
    if a == 1:
        root = rf"\sqrt{{y {sgn(-k)} {L(abs(k))}}}"
    elif a > 0:
        root = rf"\sqrt{{\frac{{y {sgn(-k)} {L(abs(k))}}}{{{L(a)}}}}}"
    else:                                              # a < 0: keep the denominator positive
        root = rf"\sqrt{{-\frac{{y {sgn(-k)} {L(abs(k))}}}{{{L(-a)}}}}}"
    rootx = root.replace("y", "x")
    hx = "" if h == 0 else f"{L(h)} "
    vertex = rf"{L(a) if a not in (1, -1) else ('-' if a == -1 else '')}\left(x {sgn(-h)} {L(abs(h))}\right)^2 {sgn(k)} {L(abs(k))}"
    steps = [
        (S(rf"y = {vertex}", "Write $y = f(x)$; it is already in completed-square form, so $x$ appears only once.",
           "$y = f(x)$ لکھیں؛ یہ پہلے ہی مکمل مربع کی صورت میں ہے، اس لیے $x$ صرف ایک بار آتا ہے۔",
           f"expand(({sp.sstr(a)})*(x - ({sp.sstr(h)}))**2 + ({sp.sstr(k)})) == {sp.sstr(f)}") if given_vertex else
         S(rf"y = {L(f)} = {vertex}" if h != 0 else rf"y = {L(f)}",
          "Write $y = f(x)$ and complete the square, so that $x$ appears only once." if h != 0 else "Write $y = f(x)$.",
          "$y = f(x)$ لکھیں اور مربع مکمل کریں تاکہ $x$ صرف ایک بار آئے۔" if h != 0 else "$y = f(x)$ لکھیں۔",
          f"expand(({sp.sstr(a)})*(x - ({sp.sstr(h)}))**2 + ({sp.sstr(k)})) == {sp.sstr(f)}")),
        S(rf"\left(x {sgn(-h)} {L(abs(h))}\right)^2 = \frac{{y {sgn(-k)} {L(abs(k))}}}{{{L(a)}}}" if h != 0 else rf"x^2 = \frac{{y {sgn(-k)} {L(abs(k))}}}{{{L(a)}}}",
          "Make the square the subject.", "مربع کو موضوع بنائیں۔"),
        S(rf"x {sgn(-h) if h != 0 else ''} {L(abs(h)) if h != 0 else ''} = {'-' if left else '+'}{root} \;\Rightarrow\; x = {hx}{'-' if left else '+'} {root}",
          f"Take the square root. The domain is $x {reltex} {L(p)}$, on the {'left' if left else 'right'} of the vertex $x = {L(h)}$, so $x - ({L(h)})$ is {'negative' if left else 'positive'}: take the {'negative' if left else 'positive'} root.",
          f"جذر لیں۔ ڈومین $x {reltex} {L(p)}$ راس $x = {L(h)}$ کی {'بائیں' if left else 'دائیں'} طرف ہے، اس لیے {'منفی' if left else 'مثبت'} جذر لیں۔"),
        S(rf"f^{{-1}}(x) = {hx}{'-' if left else '+'} {rootx}", "Interchange $x$ and $y$.", "$x$ اور $y$ کا تبادلہ کریں۔",
          f"simplify(({sp.sstr(f)}).subs(x, {ps(finv) if False else '(' + sp.sstr(finv) + ')'})) == x"),
        S(rf"\text{{Dom}}(f) = {dom},\quad \text{{Range}}(f) = {rng}",
          (f"On its domain the values of $f$ come as close as we like to $f({L(p)}) = {L(fp)}$ without reaching it (${L(p)}$ itself is excluded), and go {'up' if a > 0 else 'down'} without end."
           if strict else f"On its domain $f$ starts at $f({L(p)}) = {L(fp)}$ and goes {'up' if a > 0 else 'down'} without end."),
          (f"اپنے ڈومین پر $f$ کی قیمتیں $f({L(p)}) = {L(fp)}$ کے قریب آتی ہیں مگر اس تک نہیں پہنچتیں (${L(p)}$ خارج ہے)، اور {'اوپر' if a > 0 else 'نیچے'} جاتی ہیں۔"
           if strict else f"اپنے ڈومین پر $f$ کی قیمت $f({L(p)}) = {L(fp)}$ سے شروع ہو کر {'اوپر' if a > 0 else 'نیچے'} جاتی ہے۔"),
          f"({sp.sstr(f)}).subs(x, {ps(p)}) == {ps(fp)}"),
        S(rf"\text{{Dom}}(f^{{-1}}) = \text{{Range}}(f) = {rng},\quad \text{{Range}}(f^{{-1}}) = \text{{Dom}}(f) = {dom}", "The domain and range swap for the inverse.",
          "معکوس کے لیے ڈومین اور رینج آپس میں بدل جاتے ہیں۔")]
    shown = rf"{hx}{'-' if left else '+'} {rootx}"
    if neat:                                           # a tidier equal form, e.g. \frac{1 + \sqrt{3x - 17}}{3}
        tex, py_ = neat
        steps.insert(4, S(rf"f^{{-1}}(x) = {tex}", "Simplify: take the fractions together under one root.", "سادہ کریں: کسروں کو ایک جذر کے نیچے اکٹھا کریں۔",
                          f"simplify(({py_}) - ({sp.sstr(finv)})) == 0"))
        shown = tex
    return P(label, steps, rf"$f^{{-1}}(x) = {shown}$; Dom$(f^{{-1}}) = {rng}$, Range$(f^{{-1}}) = {dom}$", prompt=prompt)


ex("ex3.1", 3, "Find the inverse of the following quadratic functions. Also find their domain and range: (i) $f(x) = x^2 - 3,\\ x \\le 0$ "
   "(ii) $f(x) = x^2 + 6x + 4,\\ x < -3$ (iii) $f(x) = 2x^2 - 8x + 11,\\ x \\ge 2$ (iv) $f(x) = 3x^2 - 2x + 6,\\ x \\ge 5$ "
   "(v) $f(x) = 2(x - 3)^2 + 1,\\ x \\ge 3$ (vi) $f(x) = -3(x + 4)^2 - 5,\\ x < -4$", [
       inverse("i", 1, 0, -3, 0, "<=", "$f(x) = x^2 - 3,\\ x \\le 0$"),
       inverse("ii", 1, 6, 4, -3, "<", "$f(x) = x^2 + 6x + 4,\\ x < -3$"),
       inverse("iii", 2, -8, 11, 2, ">=", "$f(x) = 2x^2 - 8x + 11,\\ x \\ge 2$"),
       inverse("iv", 3, -2, 6, 5, ">=", "$f(x) = 3x^2 - 2x + 6,\\ x \\ge 5$", neat=(r"\frac{1 + \sqrt{3x - 17}}{3}", "(1 + sqrt(3*x - 17))/3")),
       inverse("v", 2, -12, 19, 3, ">=", "$f(x) = 2(x - 3)^2 + 1,\\ x \\ge 3$", given_vertex=True),
       inverse("vi", -3, -24, -53, -4, "<", "$f(x) = -3(x + 4)^2 - 5,\\ x < -4$", given_vertex=True)], "3.1")


def rows(label, prompt, rs, answer):
    return P(label, [S(m, en, ur, *c) for m, en, ur, c in rs], answer, prompt=prompt)


s5, s7, s17 = sp.sqrt(5), sp.sqrt(7), sp.sqrt(17)
Q4 = [
    rows("i", "$|x^2 + 1| = 5$", [
        (r"x^2 + 1 = 5 \quad\text{or}\quad x^2 + 1 = -5", "$|A| = 5$ means $A = 5$ or $A = -5$.", "$|A| = 5$ کا مطلب $A = 5$ یا $A = -5$۔", []),
        (r"x^2 = 4 \Rightarrow x = \pm 2;\qquad x^2 = -6 \ (\text{no real } x)", "Solve each; a square cannot be negative.", "ہر ایک حل کریں؛ مربع منفی نہیں ہو سکتا۔", ["Abs(2**2 + 1) == 5", "Abs((-2)**2 + 1) == 5"]),
        (r"\text{S.S.} = \{-2, 2\}", "The solution set.", "حل سیٹ۔", [])], "$\\{-2, 2\\}$"),
    rows("ii", "$|x^2 + 5x + 4| = 0$", [
        (r"x^2 + 5x + 4 = 0", "$|A| = 0$ only when $A = 0$.", "$|A| = 0$ صرف تب ہوتا ہے جب $A = 0$۔", []),
        (r"(x + 1)(x + 4) = 0 \Rightarrow x = -1,\ -4", "Factorize: $1 \\times 4 = 4$, $1 + 4 = 5$.", "تجزی کریں: $1 \\times 4 = 4$، $1 + 4 = 5$۔",
         ["expand((x + 1)*(x + 4)) == x**2 + 5*x + 4", "(-4)**2 + 5*(-4) + 4 == 0"]),
        (r"\text{S.S.} = \{-4, -1\}", "The solution set.", "حل سیٹ۔", [])], "$\\{-4, -1\\}$"),
    rows("iii", "$|x^2 - 6x + 8| = 4$", [
        (r"x^2 - 6x + 8 = 4 \quad\text{or}\quad x^2 - 6x + 8 = -4", "$|A| = 4$ means $A = 4$ or $A = -4$.", "$|A| = 4$ کا مطلب $A = 4$ یا $A = -4$۔", []),
        (r"x^2 - 6x + 4 = 0 \Rightarrow x = \frac{6 \pm \sqrt{36 - 16}}{2} = 3 \pm \sqrt{5}", "First equation by the quadratic formula.", "پہلی مساوات دو درجی کلیے سے۔",
         [f"Abs((3 + sqrt(5))**2 - 6*(3 + sqrt(5)) + 8) == 4", f"Abs((3 - sqrt(5))**2 - 6*(3 - sqrt(5)) + 8) == 4"]),
        (r"x^2 - 6x + 12 = 0:\ \Delta = 36 - 48 = -12 < 0 \ (\text{no real roots})", "Second equation: negative discriminant.", "دوسری مساوات: امتیازی منفی ہے۔", ["36 - 48 == -12"]),
        (r"\text{S.S.} = \{3 - \sqrt{5},\ 3 + \sqrt{5}\}", "The solution set.", "حل سیٹ۔", [])], "$\\{3 - \\sqrt{5},\\ 3 + \\sqrt{5}\\}$"),
    rows("iv", "$|3x^2 - 7x + 2| = x^2 - x + 1$", [
        (r"x^2 - x + 1 = \left(x - \tfrac{1}{2}\right)^2 + \tfrac{3}{4} > 0", "The right side is always positive, so both signs of the inside are possible.", "دائیں جانب ہمیشہ مثبت ہے، اس لیے اندر کی دونوں علامتیں ممکن ہیں۔",
         ["expand((x - R(1,2))**2 + R(3,4)) == x**2 - x + 1"]),
        (r"3x^2 - 7x + 2 = x^2 - x + 1 \Rightarrow 2x^2 - 6x + 1 = 0 \Rightarrow x = \frac{6 \pm \sqrt{28}}{4} = \frac{3 \pm \sqrt{7}}{2}", "Case 1: the inside equals the right side.",
         "حالت 1: اندر کی عبارت دائیں جانب کے برابر۔", ["Abs(3*((3+sqrt(7))/2)**2 - 7*((3+sqrt(7))/2) + 2) == ((3+sqrt(7))/2)**2 - (3+sqrt(7))/2 + 1",
                                                     "Abs(3*((3-sqrt(7))/2)**2 - 7*((3-sqrt(7))/2) + 2) == ((3-sqrt(7))/2)**2 - (3-sqrt(7))/2 + 1"]),
        (r"3x^2 - 7x + 2 = -(x^2 - x + 1) \Rightarrow 4x^2 - 8x + 3 = 0 \Rightarrow (2x - 1)(2x - 3) = 0 \Rightarrow x = \tfrac{1}{2},\ \tfrac{3}{2}",
         "Case 2: the inside equals minus the right side.", "حالت 2: اندر کی عبارت دائیں جانب کے منفی کے برابر۔",
         ["expand((2*x - 1)*(2*x - 3)) == 4*x**2 - 8*x + 3", "Abs(3*R(1,4) - 7*R(1,2) + 2) == R(1,4) - R(1,2) + 1", "Abs(3*R(9,4) - 7*R(3,2) + 2) == R(9,4) - R(3,2) + 1"]),
        (r"\text{S.S.} = \left\{\frac{3 - \sqrt{7}}{2},\ \frac{1}{2},\ \frac{3}{2},\ \frac{3 + \sqrt{7}}{2}\right\}", "All four values check in the original equation.", "چاروں قیمتیں اصل مساوات کو پورا کرتی ہیں۔", [])],
        "$\\left\\{\\frac{3 - \\sqrt{7}}{2},\\ \\frac{1}{2},\\ \\frac{3}{2},\\ \\frac{3 + \\sqrt{7}}{2}\\right\\}$"),
    rows("v", "$|x^2 - 4| < 5$", [
        (r"-5 < x^2 - 4 < 5", "$|A| < 5$ means $-5 < A < 5$.", "$|A| < 5$ کا مطلب $-5 < A < 5$۔", []),
        (r"-1 < x^2 < 9", "Add 4 throughout.", "سب میں 4 جمع کریں۔", []),
        (r"x^2 > -1 \text{ always};\quad x^2 < 9 \Rightarrow -3 < x < 3", "The left part holds for every real $x$; the right part gives $-3 < x < 3$.", "بائیں حصہ ہر $x$ کے لیے درست ہے؛ دائیں حصہ $-3 < x < 3$ دیتا ہے۔",
         ["Abs(0**2 - 4) < 5", "Abs(3**2 - 4) == 5"]),
        (r"\text{S.S.} = (-3, 3)", "The solution set.", "حل سیٹ۔", [])], "$(-3, 3)$"),
    rows("vi", "$|x^2 - 3x + 2| > 4$", [
        (r"x^2 - 3x + 2 > 4 \quad\text{or}\quad x^2 - 3x + 2 < -4", "$|A| > 4$ means $A > 4$ or $A < -4$.", "$|A| > 4$ کا مطلب $A > 4$ یا $A < -4$۔", []),
        (r"x^2 - 3x - 2 > 0:\ x = \frac{3 \pm \sqrt{17}}{2} \Rightarrow x < \frac{3 - \sqrt{17}}{2} \ \text{or}\ x > \frac{3 + \sqrt{17}}{2}", "First inequality: the parabola opens upwards, so it is positive outside its roots.",
         "پہلی عدم مساوات: قطع مکافی اوپر کھلتا ہے، اس لیے جذروں کے باہر مثبت ہے۔", ["((3 + sqrt(17))/2)**2 - 3*((3 + sqrt(17))/2) - 2 == 0", "Abs(5**2 - 3*5 + 2) > 4"]),
        (r"x^2 - 3x + 6 < 0:\ \Delta = 9 - 24 < 0 \ (\text{never})", "Second inequality: always positive, so it has no solution.", "دوسری عدم مساوات: ہمیشہ مثبت، اس لیے کوئی حل نہیں۔", ["9 - 24 == -15"]),
        (r"\text{S.S.} = \left(-\infty, \frac{3 - \sqrt{17}}{2}\right) \cup \left(\frac{3 + \sqrt{17}}{2}, \infty\right)", "The solution set.", "حل سیٹ۔", [])],
        "$\\left(-\\infty, \\frac{3 - \\sqrt{17}}{2}\\right) \\cup \\left(\\frac{3 + \\sqrt{17}}{2}, \\infty\\right)$"),
    rows("vii", "$|x^2 - 5x + 6| \\le x + 2$", [
        (r"x + 2 \ge 0 \Rightarrow x \ge -2;\qquad -(x + 2) \le x^2 - 5x + 6 \le x + 2", "$|A| \\le B$ needs $B \\ge 0$, then $-B \\le A \\le B$.", "$|A| \\le B$ کے لیے $B \\ge 0$، پھر $-B \\le A \\le B$۔", []),
        (r"x^2 - 5x + 6 \le x + 2 \Rightarrow x^2 - 6x + 4 \le 0 \Rightarrow 3 - \sqrt{5} \le x \le 3 + \sqrt{5}", "Right part: between the roots $3 \\pm \\sqrt{5}$.",
         "دائیں حصہ: جذروں $3 \\pm \\sqrt{5}$ کے درمیان۔", ["(3 + sqrt(5))**2 - 6*(3 + sqrt(5)) + 4 == 0"]),
        (r"x^2 - 5x + 6 \ge -x - 2 \Rightarrow x^2 - 4x + 8 = (x - 2)^2 + 4 > 0 \ (\text{always})", "Left part: always true.", "بائیں حصہ: ہمیشہ درست۔", ["expand((x - 2)**2 + 4) == x**2 - 4*x + 8"]),
        (r"\text{S.S.} = \left[3 - \sqrt{5},\ 3 + \sqrt{5}\right]", "These values also satisfy $x \\ge -2$.", "یہ قیمتیں $x \\ge -2$ کو بھی پورا کرتی ہیں۔",
         ["Abs(3**2 - 5*3 + 6) <= 3 + 2", "3 - sqrt(5) >= -2"])], "$\\left[3 - \\sqrt{5},\\ 3 + \\sqrt{5}\\right]$"),
    rows("viii", "$|2x^2 - 3x - 5| < 4$", [
        (r"-4 < 2x^2 - 3x - 5 < 4", "$|A| < 4$ means $-4 < A < 4$.", "$|A| < 4$ کا مطلب $-4 < A < 4$۔", []),
        (r"2x^2 - 3x - 1 > 0 \Rightarrow x < \frac{3 - \sqrt{17}}{4} \ \text{or}\ x > \frac{3 + \sqrt{17}}{4}", "Left part: roots $\\frac{3 \\pm \\sqrt{17}}{4}$; positive outside them.",
         "بائیں حصہ: جذر $\\frac{3 \\pm \\sqrt{17}}{4}$؛ ان کے باہر مثبت۔", ["2*((3 + sqrt(17))/4)**2 - 3*((3 + sqrt(17))/4) - 1 == 0"]),
        (r"2x^2 - 3x - 9 < 0 \Rightarrow (2x + 3)(x - 3) < 0 \Rightarrow -\tfrac{3}{2} < x < 3", "Right part: negative between its roots.", "دائیں حصہ: جذروں کے درمیان منفی۔",
         ["expand((2*x + 3)*(x - 3)) == 2*x**2 - 3*x - 9"]),
        (r"\text{S.S.} = \left(-\tfrac{3}{2}, \frac{3 - \sqrt{17}}{4}\right) \cup \left(\frac{3 + \sqrt{17}}{4}, 3\right)", "Both parts must hold: intersect the two solutions.",
         "دونوں حصے درست ہوں: دونوں حل کا مشترک حصہ لیں۔", ["Abs(2*(-1)**2 - 3*(-1) - 5) < 4", "Abs(2*2**2 - 3*2 - 5) < 4", "Abs(2*0**2 - 3*0 - 5) >= 4"])],
        "$\\left(-\\frac{3}{2}, \\frac{3 - \\sqrt{17}}{4}\\right) \\cup \\left(\\frac{3 + \\sqrt{17}}{4}, 3\\right)$")]
ex("ex3.1", 4, "Solve the following absolute value quadratic equations and inequalities: (i) $|x^2 + 1| = 5$ (ii) $|x^2 + 5x + 4| = 0$ (iii) $|x^2 - 6x + 8| = 4$ "
   "(iv) $|3x^2 - 7x + 2| = x^2 - x + 1$ (v) $|x^2 - 4| < 5$ (vi) $|x^2 - 3x + 2| > 4$ (vii) $|x^2 - 5x + 6| \\le x + 2$ (viii) $|2x^2 - 3x - 5| < 4$", Q4, "3.1")


# ================================================================================================== Exercise 3.2

Q21 = [
    rows("i", "$\\frac{1}{3x} + \\frac{4x}{6} = 1,\\ x \\ne 0$", [
        (r"\frac{1}{3x} + \frac{4x}{6} = 1 \quad (\times 6x)", "Multiply both sides by the L.C.M. $6x$ (allowed because $x \\ne 0$).", "دونوں اطراف کو ذو اضعاف اقل $6x$ سے ضرب دیں ($x \\ne 0$)۔", []),
        (r"2 + 4x^2 = 6x \Rightarrow 4x^2 - 6x + 2 = 0 \Rightarrow 2x^2 - 3x + 1 = 0", "Collect the terms and divide by 2.", "ارکان اکٹھے کر کے 2 سے تقسیم کریں۔", []),
        (r"(2x - 1)(x - 1) = 0 \Rightarrow x = \tfrac{1}{2},\ 1", "Factorize.", "تجزی کریں۔", ["expand((2*x - 1)*(x - 1)) == 2*x**2 - 3*x + 1"]),
        (r"\text{Check: both make the original equation true}", "Neither value makes a denominator zero, and both satisfy the equation.", "کوئی قیمت نسب نما کو صفر نہیں کرتی اور دونوں مساوات کو پورا کرتی ہیں۔",
         ["1/(3*R(1,2)) + 4*R(1,2)/6 == 1", "1/(3*1) + 4*1/6 == 1"])], "$\\left\\{\\frac{1}{2}, 1\\right\\}$"),
    rows("ii", "$\\frac{x}{x+1} + \\frac{x+1}{x} = \\frac{5}{2},\\ x \\ne -1, 0$", [
        (r"\text{Let } y = \frac{x}{x + 1}:\quad y + \frac{1}{y} = \frac{5}{2}", "The two fractions are reciprocals: substitute $y$.", "دونوں کسریں ایک دوسرے کی معکوس ہیں: $y$ رکھیں۔", []),
        (r"2y^2 - 5y + 2 = 0 \Rightarrow (2y - 1)(y - 2) = 0 \Rightarrow y = \tfrac{1}{2},\ 2", "Multiply by $2y$ and factorize.", "$2y$ سے ضرب دے کر تجزی کریں۔", ["expand((2*y - 1)*(y - 2)) == 2*y**2 - 5*y + 2"]),
        (r"\frac{x}{x + 1} = \frac{1}{2} \Rightarrow x = 1;\qquad \frac{x}{x + 1} = 2 \Rightarrow x = -2", "Go back to $x$.", "واپس $x$ پر جائیں۔", ["1/(1 + 1) == R(1,2)", "(-2)/(-2 + 1) == 2"]),
        (r"\text{S.S.} = \{-2, 1\}", "Both values satisfy the original equation.", "دونوں قیمتیں اصل مساوات کو پورا کرتی ہیں۔", ["1/2 + 2/1 == R(5,2)", "(-2)/(-1) + (-1)/(-2) == R(5,2)"])], "$\\{-2, 1\\}$"),
    rows("iii", "$\\frac{1}{x+1} + \\frac{2}{x+2} = \\frac{7}{x+5},\\ x \\ne -1, -2, -5$", [
        (r"(x + 2)(x + 5) + 2(x + 1)(x + 5) = 7(x + 1)(x + 2)", "Multiply by $(x + 1)(x + 2)(x + 5)$.", "$(x + 1)(x + 2)(x + 5)$ سے ضرب دیں۔", []),
        (r"x^2 + 7x + 10 + 2x^2 + 12x + 10 = 7x^2 + 21x + 14", "Multiply out each product.", "ہر حاصل ضرب کھولیں۔",
         ["expand((x + 2)*(x + 5) + 2*(x + 1)*(x + 5)) == 3*x**2 + 19*x + 20", "expand(7*(x + 1)*(x + 2)) == 7*x**2 + 21*x + 14"]),
        (r"4x^2 + 2x - 6 = 0 \Rightarrow 2x^2 + x - 3 = 0 \Rightarrow (2x + 3)(x - 1) = 0", "Collect the terms and factorize.", "ارکان اکٹھے کر کے تجزی کریں۔",
         ["expand((2*x + 3)*(x - 1)) == 2*x**2 + x - 3"]),
        (r"x = -\tfrac{3}{2},\ 1", "Neither value is excluded; both check.", "کوئی قیمت خارج نہیں؛ دونوں پوری ہوتی ہیں۔",
         ["1/(R(-3,2) + 1) + 2/(R(-3,2) + 2) == 7/(R(-3,2) + 5)", "1/(1 + 1) + 2/(1 + 2) == 7/(1 + 5)"])], "$\\left\\{-\\frac{3}{2}, 1\\right\\}$"),
    rows("iv", "$\\frac{a}{ax-1} + \\frac{b}{bx-1} = a + b,\\ x \\ne \\frac{1}{a}, \\frac{1}{b}$", [
        (r"\left(\frac{a}{ax - 1} - b\right) + \left(\frac{b}{bx - 1} - a\right) = 0", "Split the right side: take $b$ to the first fraction and $a$ to the second.",
         "دائیں جانب کو تقسیم کریں: $b$ پہلی کسر کے ساتھ اور $a$ دوسری کے ساتھ۔", []),
        (r"\frac{a + b - abx}{ax - 1} + \frac{a + b - abx}{bx - 1} = 0", "Simplify each bracket: the numerators are the same.", "ہر قوسین سادہ کریں: شمار کنندہ ایک ہی ہیں۔",
         ["simplify(a/(a*x - 1) - b - (a + b - a*b*x)/(a*x - 1)) == 0", "simplify(b/(b*x - 1) - a - (a + b - a*b*x)/(b*x - 1)) == 0"]),
        (r"(a + b - abx)\left[\frac{1}{ax - 1} + \frac{1}{bx - 1}\right] = 0", "Take the common factor out.", "مشترک جزو باہر نکالیں۔", []),
        (r"a + b - abx = 0 \Rightarrow x = \frac{a + b}{ab};\qquad \frac{(a + b)x - 2}{(ax - 1)(bx - 1)} = 0 \Rightarrow x = \frac{2}{a + b}", "Set each factor to zero.",
         "ہر جزو کو صفر کے برابر رکھیں۔", ["simplify(a/(a*(a + b)/(a*b) - 1) + b/(b*(a + b)/(a*b) - 1)) == a + b",
                                          "simplify(a/(a*2/(a + b) - 1) + b/(b*2/(a + b) - 1)) == a + b"]),
        (r"\text{S.S.} = \left\{\frac{a + b}{ab},\ \frac{2}{a + b}\right\}", "Both values satisfy the equation (when they do not make a denominator zero).",
         "دونوں قیمتیں مساوات کو پورا کرتی ہیں (جب نسب نما صفر نہ ہو)۔", [])], "$\\left\\{\\frac{a + b}{ab},\\ \\frac{2}{a + b}\\right\\}$"),
    rows("v", "$\\frac{x+1}{x-1} + \\frac{x-1}{x+1} = 2,\\ x \\ne 1, -1$", [
        (r"(x + 1)^2 + (x - 1)^2 = 2(x^2 - 1)", "Multiply by $(x - 1)(x + 1) = x^2 - 1$.", "$(x - 1)(x + 1) = x^2 - 1$ سے ضرب دیں۔", []),
        (r"2x^2 + 2 = 2x^2 - 2", "Multiply out.", "کھولیں۔", ["expand((x + 1)**2 + (x - 1)**2) == 2*x**2 + 2"]),
        (r"2 = -2 \quad (\text{impossible})", "The $x^2$ terms cancel and a false statement is left.", "$x^2$ کٹ جاتے ہیں اور غلط بیان بچتا ہے۔", []),
        (r"\text{S.S.} = \varnothing \ (\text{no solution})", "No value of $x$ satisfies the equation.", "کوئی قیمت مساوات کو پورا نہیں کرتی۔", [])], "no solution, $\\varnothing$"),
    rows("vi", "$3x^2 + 15x - 2\\sqrt{x^2 + 5x + 1} = 2$", [
        (r"3(x^2 + 5x + 1) - 3 - 2\sqrt{x^2 + 5x + 1} = 2", "Write $3x^2 + 15x$ as $3(x^2 + 5x + 1) - 3$.", "$3x^2 + 15x$ کو $3(x^2 + 5x + 1) - 3$ لکھیں۔",
         ["expand(3*(x**2 + 5*x + 1) - 3) == 3*x**2 + 15*x"]),
        (r"\text{Let } t = \sqrt{x^2 + 5x + 1} \ge 0:\quad 3t^2 - 2t - 5 = 0", "Substitute $t$ for the square root.", "جذر کی جگہ $t$ رکھیں۔", []),
        (r"(3t - 5)(t + 1) = 0 \Rightarrow t = \tfrac{5}{3}\ \ (t = -1 \text{ is rejected: } t \ge 0)", "Factorize; a square root is not negative.", "تجزی کریں؛ جذر منفی نہیں ہوتا۔",
         ["expand((3*t - 5)*(t + 1)) == 3*t**2 - 2*t - 5"]),
        (r"x^2 + 5x + 1 = \tfrac{25}{9} \Rightarrow 9x^2 + 45x - 16 = 0 \Rightarrow (3x - 1)(3x + 16) = 0", "Square and solve for $x$.", "مربع لے کر $x$ معلوم کریں۔",
         ["expand((3*x - 1)*(3*x + 16)) == 9*x**2 + 45*x - 16"]),
        (r"x = \tfrac{1}{3},\ -\tfrac{16}{3}", "Both values check in the original equation.", "دونوں قیمتیں اصل مساوات کو پورا کرتی ہیں۔",
         ["3*R(1,9) + 15*R(1,3) - 2*sqrt(R(1,9) + 5*R(1,3) + 1) == 2", "3*R(256,9) + 15*R(-16,3) - 2*sqrt(R(256,9) + 5*R(-16,3) + 1) == 2"])],
        "$\\left\\{\\frac{1}{3},\\ -\\frac{16}{3}\\right\\}$"),
    rows("vii", "$\\sqrt{2x+8} + \\sqrt{x+5} = 7$", [
        (r"\sqrt{2x + 8} = 7 - \sqrt{x + 5}", "Isolate one root.", "ایک جذر کو الگ کریں۔", []),
        (r"2x + 8 = 49 - 14\sqrt{x + 5} + x + 5 \Rightarrow 14\sqrt{x + 5} = 46 - x", "Square both sides and simplify.", "دونوں اطراف کا مربع لے کر سادہ کریں۔", []),
        (r"196(x + 5) = (46 - x)^2 \Rightarrow x^2 - 288x + 1136 = 0 \Rightarrow (x - 4)(x - 284) = 0", "Square again and factorize.", "دوبارہ مربع لے کر تجزی کریں۔",
         ["expand((46 - x)**2 - 196*(x + 5)) == x**2 - 288*x + 1136", "expand((x - 4)*(x - 284)) == x**2 - 288*x + 1136"]),
        (r"x = 4:\ \sqrt{16} + \sqrt{9} = 7 \ \checkmark;\qquad x = 284:\ \sqrt{576} + \sqrt{289} = 41 \ne 7", "Check both in the original equation: squaring brought in an extraneous root.",
         "دونوں کو اصل مساوات میں جانچیں: مربع لینے سے ایک فالتو جذر آ گیا۔", ["sqrt(2*4 + 8) + sqrt(4 + 5) == 7", "sqrt(2*284 + 8) + sqrt(284 + 5) == 41"]),
        (r"\text{S.S.} = \{4\}", "Only $x = 4$ is a solution.", "صرف $x = 4$ حل ہے۔", [])], "$\\{4\\}$"),
    rows("viii", "$\\sqrt{3x+4} = 2 + \\sqrt{2x-4}$", [
        (r"3x + 4 = 4 + 4\sqrt{2x - 4} + 2x - 4 \Rightarrow x + 4 = 4\sqrt{2x - 4}", "Square both sides and simplify.", "دونوں اطراف کا مربع لے کر سادہ کریں۔", []),
        (r"(x + 4)^2 = 16(2x - 4) \Rightarrow x^2 - 24x + 80 = 0 \Rightarrow (x - 4)(x - 20) = 0", "Square again and factorize.", "دوبارہ مربع لے کر تجزی کریں۔",
         ["expand((x + 4)**2 - 16*(2*x - 4)) == x**2 - 24*x + 80", "expand((x - 4)*(x - 20)) == x**2 - 24*x + 80"]),
        (r"x = 4:\ \sqrt{16} = 2 + \sqrt{4} \ \checkmark;\qquad x = 20:\ \sqrt{64} = 2 + \sqrt{36} \ \checkmark", "Check both in the original equation.", "دونوں کو اصل مساوات میں جانچیں۔",
         ["sqrt(3*4 + 4) == 2 + sqrt(2*4 - 4)", "sqrt(3*20 + 4) == 2 + sqrt(2*20 - 4)"]),
        (r"\text{S.S.} = \{4, 20\}", "Both values are solutions.", "دونوں قیمتیں حل ہیں۔", [])], "$\\{4, 20\\}$"),
    rows("ix", "$\\sqrt{x+7} + \\sqrt{x+2} = \\sqrt{6x+13}$", [
        (r"x + 7 + x + 2 + 2\sqrt{(x + 7)(x + 2)} = 6x + 13 \Rightarrow \sqrt{(x + 7)(x + 2)} = 2x + 2", "Square both sides and simplify.", "دونوں اطراف کا مربع لے کر سادہ کریں۔", []),
        (r"x^2 + 9x + 14 = 4x^2 + 8x + 4 \Rightarrow 3x^2 - x - 10 = 0 \Rightarrow (x - 2)(3x + 5) = 0", "Square again and factorize.", "دوبارہ مربع لے کر تجزی کریں۔",
         ["expand(4*x**2 + 8*x + 4 - (x**2 + 9*x + 14)) == 3*x**2 - x - 10", "expand((x - 2)*(3*x + 5)) == 3*x**2 - x - 10"]),
        (r"x = 2:\ 3 + 2 = 5 = \sqrt{25}\ \checkmark;\qquad x = -\tfrac{5}{3}:\ 2x + 2 = -\tfrac{4}{3} < 0 \ (\text{rejected})", "Check: at $x = -\\frac{5}{3}$ the root would equal a negative number.",
         "جانچ: $x = -\\frac{5}{3}$ پر جذر منفی عدد کے برابر ہو جاتا، اس لیے رد۔", ["sqrt(2 + 7) + sqrt(2 + 2) == sqrt(6*2 + 13)",
                                                                            "sqrt(R(-5,3) + 7) + sqrt(R(-5,3) + 2) - sqrt(6*R(-5,3) + 13) > 0"]),
        (r"\text{S.S.} = \{2\}", "Only $x = 2$ is a solution.", "صرف $x = 2$ حل ہے۔", [])], "$\\{2\\}$"),
    rows("x", "$\\sqrt{x+5} - \\sqrt{x-3} = 2$", [
        (r"\sqrt{x + 5} = 2 + \sqrt{x - 3}", "Isolate one root.", "ایک جذر کو الگ کریں۔", []),
        (r"x + 5 = 4 + 4\sqrt{x - 3} + x - 3 \Rightarrow 4\sqrt{x - 3} = 4 \Rightarrow \sqrt{x - 3} = 1", "Square both sides; the $x$ terms cancel.", "دونوں اطراف کا مربع لیں؛ $x$ کٹ جاتے ہیں۔", []),
        (r"x - 3 = 1 \Rightarrow x = 4", "Square again.", "دوبارہ مربع لیں۔", []),
        (r"\text{Check: } \sqrt{9} - \sqrt{1} = 3 - 1 = 2\ \checkmark;\quad \text{S.S.} = \{4\}", "The value checks in the original equation.", "قیمت اصل مساوات کو پورا کرتی ہے۔",
         ["sqrt(4 + 5) - sqrt(4 - 3) == 2"])], "$\\{4\\}$")]
ex("ex3.2", 1, "Solve the following equations: (i) $\\frac{1}{3x} + \\frac{4x}{6} = 1,\\ x \\ne 0$ (ii) $\\frac{x}{x+1} + \\frac{x+1}{x} = \\frac{5}{2},\\ x \\ne -1, 0$ "
   "(iii) $\\frac{1}{x+1} + \\frac{2}{x+2} = \\frac{7}{x+5},\\ x \\ne -1, -2, -5$ (iv) $\\frac{a}{ax-1} + \\frac{b}{bx-1} = a + b,\\ x \\ne \\frac{1}{a}, \\frac{1}{b}$ "
   "(v) $\\frac{x+1}{x-1} + \\frac{x-1}{x+1} = 2,\\ x \\ne 1, -1$ (vi) $3x^2 + 15x - 2\\sqrt{x^2 + 5x + 1} = 2$ (vii) $\\sqrt{2x+8} + \\sqrt{x+5} = 7$ "
   "(viii) $\\sqrt{3x+4} = 2 + \\sqrt{2x-4}$ (ix) $\\sqrt{x+7} + \\sqrt{x+2} = \\sqrt{6x+13}$ (x) $\\sqrt{x+5} - \\sqrt{x-3} = 2$", Q21, "3.2")


def word(eid, n, question, rs, answer, note_=None):
    p = P("", [S(m, en, ur, *c) for m, en, ur, c in rs], answer)
    if note_:
        note(p, *note_)
    ex(eid, n, question, [p], "3.2")


word("ex3.2", 2, "A farmer bought some sheep for Rs. 9000. If he had paid Rs. 100 less for each, he would have got 3 sheep more for the same money. How many sheep did he buy, when the rate in each case is uniform?", [
    (r"\text{Let the number of sheep} = x \Rightarrow \text{price of one} = \frac{9000}{x}", "Choose the unknown.", "نامعلوم چنیں۔", []),
    (r"(x + 3)\left(\frac{9000}{x} - 100\right) = 9000", "With Rs. 100 less each, $x + 3$ sheep cost the same Rs. 9000.", "ہر ایک پر 100 روپے کم سے $x + 3$ بھیڑیں اسی 9000 میں۔", []),
    (r"9000 - 100x + \frac{27000}{x} - 300 = 9000 \Rightarrow x^2 + 3x - 270 = 0", "Multiply out, multiply by $x$ and divide by $-100$.", "کھولیں، $x$ سے ضرب دیں اور $-100$ سے تقسیم کریں۔",
     ["expand(-x*((x + 3)*(9000/x - 100) - 9000)/100) == x**2 + 3*x - 270"]),
    (r"(x + 18)(x - 15) = 0 \Rightarrow x = 15 \ (x = -18 \text{ rejected})", "Factorize; the number of sheep cannot be negative.", "تجزی کریں؛ بھیڑوں کی تعداد منفی نہیں ہو سکتی۔",
     ["expand((x + 18)*(x - 15)) == x**2 + 3*x - 270", "(15 + 3)*(9000/15 - 100) == 9000"]),
    (r"\text{He bought 15 sheep (Rs. 600 each)}", "Check: 18 sheep at Rs. 500 also cost Rs. 9000.", "جانچ: 18 بھیڑیں 500 روپے فی کس بھی 9000 روپے۔", ["18*500 == 9000"])], "15 sheep")

word("ex3.2", 3, "A man sold his stock of eggs for Rs. 240. If he had 2 dozen more, he would have got the same money by selling the whole for Rs. 0.50 per dozen cheaper. How many dozen eggs did he sell?", [
    (r"\text{Let the number of dozens} = x \Rightarrow \text{price per dozen} = \frac{240}{x}", "Choose the unknown.", "نامعلوم چنیں۔", []),
    (r"(x + 2)\left(\frac{240}{x} - 0.5\right) = 240", "With 2 dozen more at Rs. 0.50 less per dozen, the money is the same.", "2 درجن زیادہ اور فی درجن 0.50 روپے کم سے رقم وہی۔", []),
    (r"240 - 0.5x + \frac{480}{x} - 1 = 240 \Rightarrow x^2 + 2x - 960 = 0", "Multiply out, multiply by $-2x$ and rearrange.", "کھولیں، $-2x$ سے ضرب دے کر ترتیب دیں۔",
     ["expand(-2*x*((x + 2)*(240/x - R(1,2)) - 240)) == x**2 + 2*x - 960"]),
    (r"(x + 32)(x - 30) = 0 \Rightarrow x = 30 \ (x = -32 \text{ rejected})", "Factorize: $32 \\times 30 = 960$ and $32 - 30 = 2$; the number of dozens is positive.",
     "تجزی کریں: $32 \\times 30 = 960$ اور $32 - 30 = 2$؛ درجنوں کی تعداد مثبت ہے۔", ["expand((x + 32)*(x - 30)) == x**2 + 2*x - 960"]),
    (r"\text{He sold 30 dozen (Rs. 8 a dozen)}", "Check: 32 dozen at Rs. 7.50 also bring Rs. 240.", "جانچ: 32 درجن 7.50 روپے فی درجن سے بھی 240 روپے۔",
     ["30*8 == 240", "32*R(15,2) == 240"])],
    "30 dozen",
    ("One solution set quotes the price as Rs. 2400; that gives $x^2 + 2x - 9600 = 0$ with no whole-number answer (about 97 dozen). The question is taken with "
     "Rs. 240, as in the other solution set and the long-standing textbook problem, which gives exactly 30 dozen.",
     "ایک حل میں قیمت 2400 روپے لکھی ہے جس سے پورا جواب نہیں آتا (تقریباً 97 درجن)؛ یہاں 240 روپے لیا گیا ہے جس سے ٹھیک 30 درجن آتا ہے۔"))

word("ex3.2", 4, "A cyclist travelled 48 km at a uniform speed. If he had travelled 2 km/hour slower, he would have taken 2 hours more to perform the journey. How long did he take to cover 48 km?", [
    (r"\text{Let the speed} = v \text{ km/h} \Rightarrow \text{time} = \frac{48}{v}", "Time = distance ÷ speed.", "وقت = فاصلہ ÷ رفتار۔", []),
    (r"\frac{48}{v - 2} - \frac{48}{v} = 2", "At 2 km/h slower he takes 2 hours more.", "2 کلومیٹر فی گھنٹہ کم رفتار سے 2 گھنٹے زیادہ۔", []),
    (r"48v - 48(v - 2) = 2v(v - 2) \Rightarrow v^2 - 2v - 48 = 0", "Multiply by $v(v - 2)$ and simplify.", "$v(v - 2)$ سے ضرب دے کر سادہ کریں۔",
     ["expand((2*v*(v - 2) - (48*v - 48*(v - 2)))/2) == v**2 - 2*v - 48"]),
    (r"(v - 8)(v + 6) = 0 \Rightarrow v = 8 \text{ km/h} \ (v = -6 \text{ rejected})", "Factorize; speed is positive.", "تجزی کریں؛ رفتار مثبت ہے۔", ["expand((v - 8)*(v + 6)) == v**2 - 2*v - 48"]),
    (r"\text{Time} = \frac{48}{8} = 6 \text{ hours}", "Check: at 6 km/h it takes 8 hours, 2 hours more.", "جانچ: 6 کلومیٹر فی گھنٹہ پر 8 گھنٹے، یعنی 2 گھنٹے زیادہ۔", ["48/8 == 6", "48/6 - 48/8 == 2"])], "6 hours")

word("ex3.2", 5, "To do a piece of work, Abdullah takes 10 days more than Abdul Hadi. Together they finish the work in 12 days. How long would Abdul Hadi take to finish it alone?", [
    (r"\text{Abdul Hadi: } x \text{ days},\quad \text{Abdullah: } x + 10 \text{ days}", "Choose the unknown.", "نامعلوم چنیں۔", []),
    (r"\frac{1}{x} + \frac{1}{x + 10} = \frac{1}{12}", "Work done in one day: together they do $\\frac{1}{12}$ of the job.", "ایک دن کا کام: دونوں مل کر $\\frac{1}{12}$ حصہ کرتے ہیں۔", []),
    (r"12(x + 10) + 12x = x(x + 10) \Rightarrow x^2 - 14x - 120 = 0", "Multiply by $12x(x + 10)$ and rearrange.", "$12x(x + 10)$ سے ضرب دے کر ترتیب دیں۔",
     ["expand(x*(x + 10) - 12*(x + 10) - 12*x) == x**2 - 14*x - 120"]),
    (r"(x - 20)(x + 6) = 0 \Rightarrow x = 20 \ (x = -6 \text{ rejected})", "Factorize; days are positive.", "تجزی کریں؛ دن مثبت ہیں۔", ["expand((x - 20)*(x + 6)) == x**2 - 14*x - 120"]),
    (r"\text{Abdul Hadi alone: 20 days}", "Check: $\\frac{1}{20} + \\frac{1}{30} = \\frac{1}{12}$.", "جانچ: $\\frac{1}{20} + \\frac{1}{30} = \\frac{1}{12}$۔", ["R(1,20) + R(1,30) == R(1,12)"])], "20 days")

word("ex3.2", 6, "The braking distance (in metres) of a car is modeled by $d(s) = 0.02s^2 + 0.1s$, where $s$ is the speed of car in km/h. If the maximum safe braking distance is 50 metres, find the range of speed where braking is safe.", [
    (r"0.02s^2 + 0.1s \le 50", "Safe means the braking distance is at most 50 m.", "محفوظ کا مطلب ہے بریک کا فاصلہ زیادہ سے زیادہ 50 میٹر۔", []),
    (r"s^2 + 5s - 2500 \le 0", "Multiply by 50.", "50 سے ضرب دیں۔", ["expand(50*(R(1,50)*s**2 + R(1,10)*s - 50)) == s**2 + 5*s - 2500"]),
    (r"s = \frac{-5 \pm \sqrt{25 + 10000}}{2} = \frac{-5 \pm \sqrt{10025}}{2}", "Roots of the boundary equation.", "حدی مساوات کے جذر۔", ["((-5 + sqrt(10025))/2)**2 + 5*((-5 + sqrt(10025))/2) - 2500 == 0"]),
    (r"0 \le s \le \frac{-5 + \sqrt{10025}}{2} \approx 47.56 \text{ km/h}", "Between the roots, and a speed is not negative.", "جذروں کے درمیان، اور رفتار منفی نہیں۔",
     [near("(-5 + sqrt(10025))/2", 47.56, 2), "R(1,50)*47**2 + R(1,10)*47 <= 50"])], "$0 \\le s \\le \\frac{-5 + \\sqrt{10025}}{2} \\approx 47.56$ km/h")

word("ex3.2", 7, "A rocket follows the height function $h(t) = -5t^2 + 20t + 30$, where $h(t)$ is the height in metres and $t$ is the time in seconds. Find the time interval during which the rocket is at least 40 metres above the ground.", [
    (r"-5t^2 + 20t + 30 \ge 40", "At least 40 m above the ground.", "زمین سے کم از کم 40 میٹر اوپر۔", []),
    (r"t^2 - 4t + 2 \le 0", "Subtract 40 and divide by $-5$ (the sign turns round).", "40 تفریق کریں اور $-5$ سے تقسیم کریں (علامت الٹ جاتی ہے)۔",
     ["expand((-5*t**2 + 20*t + 30 - 40)/(-5)) == t**2 - 4*t + 2"]),
    (r"t = \frac{4 \pm \sqrt{16 - 8}}{2} = 2 \pm \sqrt{2}", "Roots of the boundary equation.", "حدی مساوات کے جذر۔", ["(2 + sqrt(2))**2 - 4*(2 + sqrt(2)) + 2 == 0"]),
    (r"2 - \sqrt{2} \le t \le 2 + \sqrt{2} \quad (\approx 0.59 \le t \le 3.41 \text{ s})", "The parabola $t^2 - 4t + 2$ is negative between its roots.", "قطع مکافی جذروں کے درمیان منفی ہے۔",
     ["-5*2**2 + 20*2 + 30 >= 40", near("2 - sqrt(2)", 0.59, 2)])], "$2 - \\sqrt{2} \\le t \\le 2 + \\sqrt{2}$ s ($\\approx 0.59$ to $3.41$ s)")
