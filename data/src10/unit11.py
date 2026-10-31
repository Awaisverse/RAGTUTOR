"""Class 10, Unit 11 - Information Handling: Exercises 11.1-11.2 and Review Exercise 11.

Questions transcribed from the reference notes (data/class10/pages/u11_*.png). Every statistic is computed exactly from the data
(sympy Rationals) and each rounded value is checked to its stated decimal places; ogives, box plots and scatter diagrams are drawn
on the board. Answers are checked against data/answers10/unit11.json; notes errors recorded with key_note.
"""
import math

import sympy as sp

from _gen import Graph, maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 11, "title": "Information Handling", "title_ur": "معلومات کا استعمال", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational


def Q(v):
    """Exact rational from an int, float literal or string."""
    return sp.nsimplify(str(v)) if not isinstance(v, sp.Basic) else v


def near(expr, value, k):
    return f"Abs(({expr}) - {value}) <= {0.5 * 10 ** (-k) + 1e-9}"


def fmt(v, k):
    """Round half up (as taught: 56.5 -> 57), from the exact value."""
    from decimal import ROUND_HALF_UP, Decimal
    d = Decimal(str(sp.N(Q(v), 30)))
    return str(d.quantize(Decimal(1).scaleb(-k), rounding=ROUND_HALF_UP))


def py(v):
    return "(" + sp.sstr(Q(v)) + ")"


def rows(rs):
    return [S(t, en, ur, *c) for t, en, ur, c in rs]


def one(eid, n, question, rs, answer, exercise, note=None, h=None):
    p = P("", rows(rs), answer)
    if note:
        p["key_note"] = note
    ex(eid, n, question, [p], exercise, figure_h=h)


def tex_list(vs):
    return ", ".join(sp.latex(Q(v)) if Q(v).is_Integer else str(v) for v in vs)


# ------------------------------------------------------------------------------------------ grouped data: quantiles by formula


def cf_table(classes, f):
    cf, run = [], 0
    for x in f:
        run += x
        cf.append(run)
    head = " & ".join(f"{a}-{b}" for a, b in classes)
    return S(rf"\begin{{array}}{{c|{'c' * len(classes)}}} \text{{Class}} & {head} \\ \hline f & {' & '.join(map(str, f))} \\ c.f. & {' & '.join(map(str, cf))} \end{{array}}",
             "Add the frequencies one by one to get the cumulative frequencies.", "تعدد ایک ایک کر کے جمع کریں تاکہ مجموعی تعدد ملے۔",
             f"{' + '.join(map(str, f))} == {cf[-1]}"), cf


def boundaries(classes):
    """Class boundaries: (10 - 20) stays; (44 - 48, 49 - 53) uses 43.5 - 48.5."""
    gap = classes[1][0] - classes[0][1]
    half = R(gap, 2)
    return [(Q(a) - half, Q(b) + half) for a, b in classes], Q(classes[0][1] - classes[0][0]) + gap


def quantile(name, pos_tex, pos, classes, f, cf, k_round, note_en=""):
    bnd, h = boundaries(classes)
    i = next(j for j, c in enumerate(cf) if c >= pos)
    L, cfp, fi = bnd[i][0], (cf[i - 1] if i else 0), f[i]
    val = L + (Q(pos) - cfp) / fi * h
    return S(rf"{name}:\ {pos_tex} = {sp.latex(Q(pos))},\ \text{{class }} {classes[i][0]}-{classes[i][1]},\ L = {sp.latex(L)},\ c.f. = {cfp},\ f = {fi};\ "
             rf"{name} = {sp.latex(L)} + \frac{{{sp.latex(Q(pos))} - {cfp}}}{{{fi}}} \times {sp.latex(h)} \approx {fmt(val, 2)}",
             f"Find the class where the cumulative frequency first reaches {sp.latex(Q(pos))}, then use $L + \\frac{{\\text{{position}} - c.f.}}{{f}} \\times h$.{note_en}",
             f"وہ جماعت معلوم کریں جہاں مجموعی تعدد پہلی بار {sp.latex(Q(pos))} تک پہنچے، پھر کلیہ لگائیں۔",
             near(f"{py(L)} + ({py(pos)} - {cfp})/{fi}*{py(h)}", fmt(val, 2), 2)), val


def ogive(label, classes, f, asks, prompt, k_ans=0):
    """asks: list of (name, position tex, position value)."""
    st, cf = cf_table(classes, f)
    bnd, h = boundaries(classes)
    N = cf[-1]
    xs = [float(bnd[0][0])] + [float(b[1]) for b in bnd]
    ys = [0] + cf
    g = Graph((xs[0] - h, xs[-1] + h / 2), (0, N * 1.1), h=70, xstep=float(h), ystep=None)
    steps = [st, S(r"\text{Plot (upper boundary, c.f.) and join: the ogive}", "Plot each upper class boundary against its cumulative frequency, starting from (lower boundary, 0).",
                   "ہر اوپری جماعتی حد کو اس کے مجموعی تعدد کے ساتھ لگائیں اور ملا دیں۔",
                   draw=g.axes() + [{"t": "poly", "p": sum(([g.X(x), g.Y(y)] for x, y in zip(xs, ys)), [])}] + sum((g.point(x, y) for x, y in zip(xs, ys)), []))]
    vals = {}
    for name, pt, pos in asks:
        s, v = quantile(name, pt, pos, classes, f, cf, 2)
        y = float(pos)
        s["draw"] = [{"t": "line", "p": [g.X(xs[0]), g.Y(y), g.X(float(v)), g.Y(y)], "dash": True},
                     {"t": "line", "p": [g.X(float(v)), g.Y(y), g.X(float(v)), g.Y(0)], "dash": True}]
        steps.append(s)
        vals[name] = v
    iqr = vals["Q_3"] - vals["Q_1"]
    steps.append(S(rf"IQR = Q_3 - Q_1 = {fmt(vals['Q_3'], 2)} - {fmt(vals['Q_1'], 2)} \approx {fmt(iqr, 2)}", "Interquartile range.", "بین الربعی وسعت۔",
                   near(f"{py(vals['Q_3'])} - {py(vals['Q_1'])}", fmt(iqr, 2), 2)))
    out = [f"{n.replace('_', '').replace('{', '').replace('}', '')} = {fmt(v, k_ans)}" for n, v in vals.items()] + [f"IQR = {fmt(iqr, k_ans)}"]
    return P(label, steps, ", ".join(out).replace("Q2", "Median"), prompt=prompt)


# ------------------------------------------------------------------------------------------ ungrouped data: five-number summary and box plots


def item(sorted_d, pos):
    """Value at a (possibly fractional) position, 1-based."""
    lo = int(math.floor(pos))
    frac = Q(pos) - lo
    v = Q(sorted_d[lo - 1])
    if frac:
        v = v + frac * (Q(sorted_d[lo]) - Q(sorted_d[lo - 1]))
    return v


def box_draw(mn, q1, md, q3, mx, lo, hi):
    def X(v):
        return round(6 + (float(v) - lo) / (hi - lo) * 88, 2)
    y = 22
    return [{"t": "numberline", "from": lo, "to": hi, "y": 45, "marks": []},
            {"t": "line", "p": [X(mn), y, X(q1), y]}, {"t": "line", "p": [X(q3), y, X(mx), y]},
            {"t": "line", "p": [X(mn), y - 3, X(mn), y + 3]}, {"t": "line", "p": [X(mx), y - 3, X(mx), y + 3]},
            {"t": "poly", "p": [X(q1), y - 6, X(q3), y - 6, X(q3), y + 6, X(q1), y + 6], "close": True},
            {"t": "line", "p": [X(md), y - 6, X(md), y + 6]},
            {"t": "text", "p": [X(q1) - 2, y - 9], "s": "Q1"}, {"t": "text", "p": [X(md) - 3, y - 9], "s": "Med"}, {"t": "text", "p": [X(q3) - 2, y - 9], "s": "Q3"}]


def five_number(label, data, prompt, extra=True):
    d = sorted(data, key=lambda v: Q(v))
    n = len(d)
    md, q1, q3 = item(d, R(n + 1, 2)), item(d, R(n + 1, 4)), item(d, R(3 * (n + 1), 4))
    mn, mx = Q(d[0]), Q(d[-1])
    lo = int(math.floor(float(mn) / 2) * 2) - 2
    hi = int(math.ceil(float(mx) / 2) * 2) + 2
    steps = [S(r"\text{Ordered data: } " + tex_list(d) + rf",\quad n = {n}", "Arrange the data in increasing order.", "مواد کو صعودی ترتیب میں لکھیں۔", f"{n} == {len(data)}"),
             S(rf"\text{{Median}} = \left(\frac{{n + 1}}{{2}}\right)^{{th}} = {sp.latex(R(n + 1, 2))}^{{th}} \text{{ item}} = {sp.latex(md)}", "Middle item.", "درمیانی رقم۔",
               f"{py(md)} == {py(item(d, R(n + 1, 2)))}"),
             S(rf"Q_1 = \left(\frac{{n + 1}}{{4}}\right)^{{th}} = {sp.latex(R(n + 1, 4))}^{{th}} \text{{ item}} = {sp.latex(q1)},\quad "
               rf"Q_3 = \left(\frac{{3(n + 1)}}{{4}}\right)^{{th}} = {sp.latex(R(3 * (n + 1), 4))}^{{th}} \text{{ item}} = {sp.latex(q3)}", "Quartiles by position.", "ربعیے مقام سے۔")]
    if extra:
        steps.append(S(rf"\text{{Range}} = {sp.latex(mx)} - {sp.latex(mn)} = {sp.latex(mx - mn)},\quad IQR = {sp.latex(q3)} - {sp.latex(q1)} = {sp.latex(q3 - q1)}",
                       "Range = max - min; IQR = $Q_3 - Q_1$.", "وسعت = بڑی - چھوٹی؛ IQR = $Q_3 - Q_1$۔", f"{py(mx)} - {py(mn)} == {py(mx - mn)}", f"{py(q3)} - {py(q1)} == {py(q3 - q1)}"))
    steps.append(S(rf"\text{{Five-number summary: }} ({sp.latex(mn)}, {sp.latex(q1)}, {sp.latex(md)}, {sp.latex(q3)}, {sp.latex(mx)})", "Draw the box from $Q_1$ to $Q_3$ with the median inside, "
                   "and whiskers to the minimum and maximum.", "باکس $Q_1$ سے $Q_3$ تک بنائیں، اندر وسطانیہ، اور کم سے کم و زیادہ سے زیادہ تک لکیریں۔",
                   draw=box_draw(mn, q1, md, q3, mx, lo, hi)))
    ans = f"Median = {sp.latex(md)}, Q1 = {sp.latex(q1)}, Q3 = {sp.latex(q3)}"
    if extra:
        ans += f", Range = {sp.latex(mx - mn)}, IQR = {sp.latex(q3 - q1)}"
    return P(label, steps, ans, prompt=prompt)


# ------------------------------------------------------------------------------------------ dispersion


def dispersion(data, k=2, name="x", show_table=True):
    d = [Q(v) for v in data]
    n = len(d)
    m = sum(d) / n
    var = sum((v - m) ** 2 for v in d) / n
    sd = sp.sqrt(var)
    steps = [S(rf"\bar{{{name}}} = \frac{{{' + '.join(str(v) for v in data)}}}{{{n}}} = \frac{{{sp.latex(sum(d))}}}{{{n}}} \approx {fmt(m, k)}", "Mean = sum $\\div$ number of values.",
               "اوسط = مجموعہ $\\div$ تعداد۔", f"{' + '.join(py(v) for v in data)} == {py(sum(d))}")]
    if show_table:
        steps.append(S(rf"\sigma^2 = \frac{{\sum({name} - \bar{{{name}}})^2}}{{n}} = \frac{{{fmt(sum((v - m) ** 2 for v in d), 4).rstrip('0').rstrip('.')}}}{{{n}}} \approx {fmt(var, 4 if var < 1 else 2)}",
                       "Variance = mean of the squared deviations from the mean.", "تغیر = اوسط سے انحرافات کے مربعوں کا اوسط۔",
                       near(f"({' + '.join(f'({py(v)} - {py(m)})**2' for v in data)})/{n}", fmt(var, 4 if var < 1 else 2), 4 if var < 1 else 2)))
    steps.append(S(rf"\sigma = \sqrt{{\sigma^2}} \approx {fmt(sd, k)}", "Standard deviation = square root of the variance.", "معیاری انحراف = تغیر کا جذر۔",
                   near(f"sqrt({py(var)})", fmt(sd, k), k)))
    return steps, m, var, sd


def grouped_dispersion(mids, f, k=2):
    N = sum(f)
    mids = [Q(v) for v in mids]
    m = sum(a * b for a, b in zip(mids, f)) / N
    var = sum(b * (a - m) ** 2 for a, b in zip(mids, f)) / N
    sd = sp.sqrt(var)
    head = " & ".join(sp.latex(v) for v in mids)
    steps = [S(rf"\begin{{array}}{{c|{'c' * len(f)}}} x\ (\text{{midpoint}}) & {head} \\ \hline f & {' & '.join(map(str, f))} \\ fx & {' & '.join(sp.latex(a * b) for a, b in zip(mids, f))} \end{{array}}",
               "Use the class midpoints as $x$.", "جماعت کے درمیانی نقاط کو $x$ لیں۔", f"{' + '.join(map(str, f))} == {N}"),
             S(rf"\bar{{x}} = \frac{{\sum fx}}{{\sum f}} = \frac{{{sp.latex(sum(a * b for a, b in zip(mids, f)))}}}{{{N}}} \approx {fmt(m, 2)}", "Mean of grouped data.", "گروہی مواد کا اوسط۔",
               near(f"{py(sum(a * b for a, b in zip(mids, f)))}/{N}", fmt(m, 2), 2)),
             S(rf"\sigma^2 = \frac{{\sum f(x - \bar{{x}})^2}}{{\sum f}} \approx {fmt(var, 2)}", "Variance of grouped data.", "گروہی مواد کا تغیر۔",
               near(f"({' + '.join(f'{b}*({py(a)} - {py(m)})**2' for a, b in zip(mids, f))})/{N}", fmt(var, 2), 2)),
             S(rf"\sigma = \sqrt{{{fmt(var, 2)}}} \approx {fmt(sd, k)}", "Standard deviation.", "معیاری انحراف۔", near(f"sqrt({py(var)})", fmt(sd, k), k))]
    return steps, m, var, sd


# ------------------------------------------------------------------------------------------ scatter and regression


def regression(xs, ys, x_name="x", y_name="y", k=4):
    n = len(xs)
    X, Y = [Q(v) for v in xs], [Q(v) for v in ys]
    sx, sy = sum(X), sum(Y)
    sxy = sum(a * b for a, b in zip(X, Y))
    sx2 = sum(a * a for a in X)
    sy2 = sum(b * b for b in Y)
    b = (n * sxy - sx * sy) / (n * sx2 - sx ** 2)
    a = (sy - b * sx) / n
    r = (n * sxy - sx * sy) / sp.sqrt((n * sx2 - sx ** 2) * (n * sy2 - sy ** 2))
    steps = [S(rf"n = {n},\ \sum {x_name} = {sp.latex(sx)},\ \sum {y_name} = {sp.latex(sy)},\ \sum {x_name}{y_name} = {sp.latex(sxy)},\ \sum {x_name}^2 = {sp.latex(sx2)}",
               "Work out the sums from the table.", "جدول سے مجموعے نکالیں۔",
               f"{' + '.join(py(v) for v in xs)} == {py(sx)}", f"{' + '.join(py(v) for v in ys)} == {py(sy)}",
               f"{' + '.join(f'{py(p)}*{py(q)}' for p, q in zip(xs, ys))} == {py(sxy)}", f"{' + '.join(f'{py(p)}**2' for p in xs)} == {py(sx2)}"),
             S(rf"b = \frac{{n\sum {x_name}{y_name} - \sum {x_name}\sum {y_name}}}{{n\sum {x_name}^2 - (\sum {x_name})^2}} \approx {fmt(b, k)},\quad a = \frac{{\sum {y_name} - b\sum {x_name}}}{{n}} \approx {fmt(a, k)}",
               "Least-squares line $\\hat{y} = a + bx$.", "کم سے کم مربعوں کا خط $\\hat{y} = a + bx$۔",
               near(f"({n}*{py(sxy)} - {py(sx)}*{py(sy)})/({n}*{py(sx2)} - {py(sx)}**2)", fmt(b, k), k), near(f"({py(sy)} - ({py(b)})*{py(sx)})/{n}", fmt(a, k), k)),
             S(rf"r = \frac{{n\sum {x_name}{y_name} - \sum {x_name}\sum {y_name}}}{{\sqrt{{[n\sum {x_name}^2 - (\sum {x_name})^2][n\sum {y_name}^2 - (\sum {y_name})^2]}}}} \approx {fmt(r, 3)}",
               "Correlation coefficient: close to $+1$ strong positive, close to $-1$ strong negative.", "ارتباطی سر: $+1$ کے قریب مضبوط مثبت، $-1$ کے قریب مضبوط منفی۔",
               near(f"({n}*{py(sxy)} - {py(sx)}*{py(sy)})/sqrt(({n}*{py(sx2)} - {py(sx)}**2)*({n}*{py(sy2)} - {py(sy)}**2))", fmt(r, 3), 3))]
    return steps, a, b, r


def scatter_draw(xs, ys, a, b, pad=0.1):
    fx = [float(v) for v in xs]
    fy = [float(v) for v in ys]
    x0, x1 = min(fx + [0]), max(fx)
    y0, y1 = min(fy + [0]), max(fy)
    g = Graph((x0, x1 + (x1 - x0) * pad), (y0, y1 + (y1 - y0) * pad), h=70)
    line = sp.sstr(sp.Float(a, 6) + sp.Float(b, 6) * sp.Symbol("x"))
    return g.axes() + sum((g.point(p, q) for p, q in zip(fx, fy)), []) + g.curve(line)


def kind(r):
    s = "strong" if abs(r) >= 0.8 else ("moderate" if abs(r) >= 0.5 else "weak")
    return f"{s} {'positive' if r > 0 else 'negative'} correlation"


# ------------------------------------------------------------------------------------------ Exercise 11.1

C1, F1 = [(44, 48), (49, 53), (54, 58), (59, 63), (64, 68), (69, 73), (74, 78)], [3, 12, 15, 23, 12, 8, 7]
ex("ex11.1", 1, "The following frequency distribution represents the achievement of a student's group upon a memory test: Scores 44-48, 49-53, 54-58, 59-63, 64-68, 69-73, 74-78 "
   "with No. of Students 3, 12, 15, 23, 12, 8, 7. (i) Plot cumulative frequency graph of group scores. (ii) Determine median, lower and upper quartiles, $D_3$, $P_{90}$ and "
   "interquartile range graphically. Note: Write your answers in whole numbers.", [
       ogive("", C1, F1, [("Q_2", r"\frac{N}{2}", 40), ("Q_1", r"\frac{N}{4}", 20), ("Q_3", r"\frac{3N}{4}", 60), ("D_3", r"\frac{3N}{10}", 24), ("P_{90}", r"\frac{90N}{100}", 72)], "")],
   "11.1", figure_h=70)
C2, F2 = [(69, 79), (79, 89), (89, 99), (99, 109), (109, 119)], [4, 10, 13, 8, 5]
ex("ex11.1", 2, "Construct an ogive for the following distribution of scores: 69-79, 79-89, 89-99, 99-109, 109-119 with $f$ = 4, 10, 13, 8, 5. Determine median, lower and upper "
   "quartiles, $D_6$, $P_{80}$ and interquartile range graphically.", [
       ogive("", C2, F2, [("Q_2", r"\frac{N}{2}", 20), ("Q_1", r"\frac{N}{4}", 10), ("Q_3", r"\frac{3N}{4}", 30), ("D_6", r"\frac{6N}{10}", 24), ("P_{80}", r"\frac{80N}{100}", 32)], "")],
   "11.1", figure_h=70)
ex("ex11.1", 3, r"Find $Q_1$, $Q_3$, median, range and $IQR$ for the dataset given below: 3, 6, 8, 4, 7, 5, 10, 11, 13, 9, 14, 12, 15, 16, 17. Also draw a box-and-whisker plot.",
   [five_number("", [3, 6, 8, 4, 7, 5, 10, 11, 13, 9, 14, 12, 15, 16, 17], "")], "11.1", figure_h=55)
ex("ex11.1", 4, r"Find $Q_1$, $Q_3$, median, range, $IQR$ and extreme values plot for the following data: 102, 98, 95, 100, 93, 110, 108, 104, 97, 96, 92, 101, 99, 105, 107. "
   "Also draw a box-and-whisker plot.", [five_number("", [102, 98, 95, 100, 93, 110, 108, 104, 97, 96, 92, 101, 99, 105, 107], "")], "11.1", figure_h=55)
one("ex11.1", 5, r"Find $Q_1$, $Q_3$, median, minimum and maximum values for the following box-and-whisker plot (as drawn in the book).", [
    (r"\text{Minimum} = 10,\ Q_1 = 22,\ \text{Median} = 25,\ Q_3 = 35,\ \text{Maximum} = 46", "Read the ends of the whiskers, the edges of the box and the line inside the box.",
     "لکیروں کے سرے، باکس کے کنارے اور باکس کے اندر کی لکیر پڑھیں۔", [], )], "Min = 10, Q1 = 22, Median = 25, Q3 = 35, Max = 46", "11.1")
UNIT["items"][-1]["parts"][0]["steps"][0]["draw"] = box_draw(10, 22, 25, 35, 46, 8, 50)
UNIT["items"][-1]["figure_h"] = 55
one("ex11.1", 6, r"Draw the box-and-whisker plot, if min. value = 12, max. value = 26, median = 19, $Q_1$ = 14 and $Q_3$ = 24.", [
    (r"(12, 14, 19, 24, 26)", "Box from $Q_1 = 14$ to $Q_3 = 24$, median line at 19, whiskers to 12 and 26.", "باکس 14 سے 24 تک، وسطانیہ 19 پر، لکیریں 12 اور 26 تک۔", ["12 < 14", "14 < 19", "19 < 24", "24 < 26"])],
    "box from 14 to 24, median 19, whiskers to 12 and 26", "11.1", h=55)
UNIT["items"][-1]["parts"][0]["steps"][0]["draw"] = box_draw(12, 14, 19, 24, 26, 10, 30)

X7, Y7 = [14, 28, 34, 36, 43, 45, 46, 49], [16, 20, 33, 35, 38, 39, 42, 43]
st7, a7, b7, r7 = regression(X7, Y7)
st7[0]["draw"] = scatter_draw(X7, Y7, a7, b7)
ex("ex11.1", 7, "Construct a scatter diagram and draw a line of best fit for the following quiz scores for 8 students in a class: 1st quiz 14, 28, 34, 36, 43, 45, 46, 49; "
   "2nd quiz 16, 20, 33, 35, 38, 39, 42, 43. Describe correlation between 1st and 2nd quiz scores also.",
   [P("", st7 + [S(r"\text{" + kind(r7) + "}", "As the first score increases the second score also increases; the points lie close to a rising line.",
                   "پہلے نمبر بڑھنے سے دوسرے نمبر بھی بڑھتے ہیں؛ نقاط ایک چڑھتی لکیر کے قریب ہیں۔")], "strong positive correlation")], "11.1", figure_h=70)

X8, Y8 = [20, 38, 70, 40, 100, 110, 50, 136, 150, 80], [160, 142, 130, 120, 70, 50, 140, 44, 36, 100]
st8, a8, b8, r8 = regression(Y8, X8, "y", "x")
st8[0]["draw"] = scatter_draw(X8, Y8, -a8 / b8, 1 / b8)
est8 = a8 + b8 * 60
ex("ex11.1", 8, "The following table shows the test scores (one measuring speed and the other measuring strength) of football players out of 200: 1st Test 20, 38, 70, 40, 100, 110, 50, "
   "136, 150, 80; 2nd Test 160, 142, 130, 120, 70, 50, 140, 44, 36, 100. (i) Construct a scatter diagram and draw a line of best fit. (ii) Describe correlation between the 1st and 2nd "
   "tests. (iii) Abdullah scores 60 in the 2nd test. Estimate his score in the 1st test.", [
       P("i", [T("Plot (1st test, 2nd test) for each player and draw the line of best fit (here the regression of the 1st test on the 2nd).",
                 "ہر کھلاڑی کے لیے نقطہ لگائیں اور بہترین خط کھینچیں۔")] + st8[:2], "scatter diagram with a falling line of best fit", prompt="scatter diagram and line of best fit"),
       P("ii", [st8[2], S(r"\text{" + kind(r8) + "}", "One score rises as the other falls.", "ایک نمبر بڑھتا ہے تو دوسرا گھٹتا ہے۔")], "strong negative correlation", prompt="correlation"),
       P("iii", [S(rf"x = a + by = {fmt(a8, 2)} + ({fmt(b8, 4)})(60) \approx {fmt(est8, 1)}", "Put $y = 60$ in the line of the 1st test on the 2nd test.",
                   "خط میں $y = 60$ رکھیں۔", near(f"{py(a8)} + ({py(b8)})*60", fmt(est8, 1), 1))], f"{fmt(est8, 1)}", prompt="estimate for 60 in the 2nd test")],
   "11.1", figure_h=70)

X9, Y9 = ["0.5", 1, 2, 3, 4, 5, 6, 7, 8, 9], ["4.0", "3.9", "3.7", "3.5", "3.3", "3.1", "2.9", "2.8", "2.6", "2.5"]
st9, a9, b9, r9 = regression(X9, Y9)
st9[0]["draw"] = scatter_draw(X9, Y9, a9, b9)
est9 = a9 + b9 * Q("6.5")
p9iii = P("iii", [S(rf"\hat{{y}} = {fmt(a9, 4)} + ({fmt(b9, 4)})(6.5) \approx {fmt(est9, 2)} \approx 2.9", "Put $x = 6.5$ in the line of best fit.", "بہترین خط میں $x = 6.5$ رکھیں۔",
                    near(f"{py(a9)} + ({py(b9)})*R(13,2)", fmt(est9, 2), 2))], r"$\approx 2.9$", prompt="GPA for 6.5 hours")
p9iii["key_note"] = {"en": "The reference notes use $\\sum xy = 135.55$ (the correct sum is 132.8) and get 2.98 by calculation, while reading 2.9 from their graph; "
                           "the least-squares value is 2.88.", "ur": "حوالہ نوٹس میں $\\sum xy$ غلط ہے؛ درست تخمینہ 2.88 (تقریباً 2.9) ہے۔"}
ex("ex11.1", 9, "The following table shows the number of daily social media hours and GPA of university students: Hours 0.5, 1, 2, 3, 4, 5, 6, 7, 8, 9; GPA 4.0, 3.9, 3.7, 3.5, 3.3, "
   "3.1, 2.9, 2.8, 2.6, 2.5. (i) Construct a scatter diagram and draw a line of best fit. (ii) Identify the nature of correlation between social media use and GPA. (iii) Estimate the "
   "GPA for a student who spends 6.5 hours on social media.", [
       P("i", st9[:2], "scatter diagram with a falling line of best fit", prompt="scatter diagram and line of best fit"),
       P("ii", [st9[2], S(r"\text{" + kind(r9) + "}", "More hours, lower GPA.", "زیادہ گھنٹے، کم GPA۔")], "strong negative correlation", prompt="nature of correlation"), p9iii],
   "11.1", figure_h=70)

# ------------------------------------------------------------------------------------------ Exercise 11.2

ex("ex11.2", 1, "Find the range of the following data sets: (i) 63, 89, 98, 125, 79, 108, 117, 60 (ii) 43.5, 13.6, 18.9, 38.4, 61.4, 29.4", [
    P("i", rows([(r"\text{Range} = 125 - 60 = 65", "Highest minus lowest.", "سب سے بڑی منفی سب سے چھوٹی۔", ["Max(63, 89, 98, 125, 79, 108, 117, 60) - Min(63, 89, 98, 125, 79, 108, 117, 60) == 65"])]),
      "65", prompt="63, 89, 98, 125, 79, 108, 117, 60"),
    P("ii", rows([(r"\text{Range} = 61.4 - 13.6 = 47.8", "Highest minus lowest.", "سب سے بڑی منفی سب سے چھوٹی۔", ["R(614,10) - R(136,10) == R(478,10)"])]), "47.8",
      prompt="43.5, 13.6, 18.9, 38.4, 61.4, 29.4")], "11.2")
one("ex11.2", 2, "If the range and the lowest value of a set of data are 46.7 and 13.4 respectively, then find the highest value.", [
    (r"46.7 = \text{Highest} - 13.4 \Rightarrow \text{Highest} = 46.7 + 13.4 = 60.1", "Range = highest - lowest.", "وسعت = بڑی - چھوٹی۔", ["R(467,10) + R(134,10) == R(601,10)"])], "60.1", "11.2")
one("ex11.2", 3, "Calculate the range of the following data: Income (in Rs.) 4000-4500, 4500-5000, 5000-5500, 5500-6000, 6000-6500 with No. of workers 8, 12, 30, 21, 6.", [
    (r"\text{Range} = 6500 - 4000 = 2500", "Upper limit of the last class minus lower limit of the first class.", "آخری جماعت کی اوپری حد منفی پہلی جماعت کی نچلی حد۔", ["6500 - 4000 == 2500"])],
    "Rs. 2500", "11.2")
st, m, v, s = dispersion([52, 55, 50, 53, 54, 56, 52])
ex("ex11.2", 4, "A group of 7 workers reported the number of items they assembled in a day as: 52, 55, 50, 53, 54, 56, 52. Find the standard deviation and variance of the items assembled.",
   [P("", st, f"Variance = {fmt(v, 2)}, SD = {fmt(s, 2)}")], "11.2")
st, m, v, s = dispersion([120, 135, 130, 125, 140])
ex("ex11.2", 5, "A librarian recorded the number of visitors during 5 days of a week: 120, 135, 130, 125, 140. Calculate the variance and standard deviation of visitors.",
   [P("", st, f"Variance = {fmt(v, 0)}, SD = {fmt(s, 2)}")], "11.2")
one("ex11.2", 6, "Find the range, variance and standard deviation of first 23 odd numbers.", [
    (r"1, 3, 5, \ldots, 45:\quad \text{Range} = 45 - 1 = 44", "The 23rd odd number is $2(23) - 1 = 45$.", "23واں طاق عدد $2(23) - 1 = 45$ ہے۔", ["2*23 - 1 == 45"]),
    (r"\bar{x} = \frac{1 + 45}{2} = 23,\quad \sigma^2 = \frac{n^2 - 1}{3} = \frac{23^2 - 1}{3} = 176", "For the first $n$ odd numbers the variance is $\\frac{n^2 - 1}{3}$.",
     "پہلے $n$ طاق اعداد کا تغیر $\\frac{n^2 - 1}{3}$ ہے۔", ["(" + " + ".join(f"({2 * k - 1} - 23)**2" for k in range(1, 24)) + ")/23 == 176"]),
    (r"\sigma = \sqrt{176} \approx 13.27", "Square root.", "جذر۔", [near("sqrt(176)", "13.27", 2)])], "Range = 44, Variance = 176, SD = 13.27", "11.2")
st, m, v, s = grouped_dispersion([42, 51, 54, 61, 63, 71], [5, 13, 4, 9, 5, 4])
ex("ex11.2", 7, "The rainfall recorded in various places of five districts in a week is given below. Find its variance and standard deviation. Rainfall (in mm) 42, 51, 54, 61, 63, 71 with "
   "Number of places 5, 13, 4, 9, 5, 4.", [P("", st, f"Variance = {fmt(v, 2)}, SD = {fmt(s, 2)}")], "11.2")
UNIT["items"][-1]["parts"][0]["key_note"] = {"en": "The reference notes give 67.282 from rounded squares; the exact variance is 67.27 (SD 8.20 either way).",
                                             "ur": "حوالہ نوٹس میں 67.282 ہے؛ درست تغیر 67.27 ہے۔"}
sa, ma, va, sda = dispersion([98, 100, 102, 101, 99], name="x_A")
sb, mb, vb, sdb = dispersion([95, 100, 105, 90, 110], name="x_B")
ex("ex11.2", 8, "Machine A Output (units): 98, 100, 102, 101, 99. Machine B Output (units): 95, 100, 105, 90, 110. (i) Which machine has better performance? (ii) Which machine is more consistent?", [
    P("i", sa[:1] + sb[:1] + [S(r"\bar{x}_A = \bar{x}_B = 100", "Equal means: equal performance.", "اوسط برابر: کارکردگی برابر۔", "R(500,5) == 100")], "equal performance (both means 100)",
      prompt="better performance"),
    P("ii", sa[1:] + sb[1:] + [S(rf"\sigma_A \approx {fmt(sda, 2)} < \sigma_B \approx {fmt(sdb, 2)}", "The smaller standard deviation is more consistent.", "کم معیاری انحراف زیادہ مستقل ہے۔",
                                 f"sqrt(2) < sqrt(50)")], "Machine A is more consistent", prompt="more consistent")], "11.2")
sa, ma, va, sda = dispersion(["5.5", "5.7", "5.4", "5.6", "5.8", "5.6"], name="x_A")
sb, mb, vb, sdb = dispersion(["5.5", "6.5", "4.5", "6.0", "5.0", "6.0"], name="x_B")
p9 = P("", sa + sb + [S(rf"\bar{{x}}_A = {fmt(ma, 2)} > \bar{{x}}_B = {fmt(mb, 2)},\quad \sigma_A = {fmt(sda, 2)} < \sigma_B = {fmt(sdb, 2)}",
                        "A has the higher mean (better performance) and the smaller standard deviation (more consistent).", "A کا اوسط زیادہ اور معیاری انحراف کم ہے۔")],
       f"A: mean {fmt(ma, 2)}, SD {fmt(sda, 2)}; B: mean {fmt(mb, 2)}, SD {fmt(sdb, 2)}; A performs better and is more consistent")
p9["key_note"] = {"en": "The reference notes give $\\sigma_A = 0.14$ and $\\sigma_B = 0.72$; computed from the data they are 0.13 and 0.67 (the conclusion is the same).",
                  "ur": "حوالہ نوٹس میں 0.14 اور 0.72 ہیں؛ درست 0.13 اور 0.67 ہیں (نتیجہ وہی ہے)۔"}
ex("ex11.2", 9, "The monthly sales (rupees in lacs) for two salespersons over 6 months are: Person A: 5.5, 5.7, 5.4, 5.6, 5.8, 5.6; Person B: 5.5, 6.5, 4.5, 6.0, 5.0, 6.0. "
   "Compare their performance and consistency.", [p9], "11.2")
st, m, v, s = grouped_dispersion([900, 1100, 1300, 1500, 1700, 1900], [2, 4, 6, 8, 2, 1])
ex("ex11.2", 10, "The table given below shows the daily wages of workers in a textile mill, grouped into six income brackets (Daily Wage in Rs): 800-1000, 1000-1200, 1200-1400, 1400-1600, 1600-1800, "
   "1800-2000 with frequency 2, 4, 6, 8, 2, 1. Calculate the mean, variance and standard deviation of the wages.", [P("", st, f"Mean = {fmt(m, 2)}, Variance = {fmt(v, 2)}, SD = {fmt(s, 2)}")],
   "11.2")
st, m, v, s = dispersion([15, 18, 14, 20, 13])
ex("ex11.2", 11, "A company forecasts monthly sales (rupees in millions): 15, 18, 14, 20, 13. Find variability in sales predictions.", [P("", st, f"Variance = {fmt(v, 1)}, SD = {fmt(s, 2)}")], "11.2")
st, m, v, s = dispersion(["5.2", "6.0", "4.8", "5.5", "6.2"])
ex("ex11.2", 12, "Unemployment rates (%) in five provinces are 5.2, 6.0, 4.8, 5.5, 6.2. Calculate standard deviation and describe is there balanced unemployment rate?",
   [P("", st + [S(r"\text{fairly balanced}", "The standard deviation is small compared with the mean, so the rates are close together.", "معیاری انحراف اوسط کے مقابلے میں کم ہے۔")],
      f"SD = {fmt(s, 2)}; fairly balanced")], "11.2")


def short(label, rs, ans, prompt):
    return P(label, rows(rs), ans, prompt=prompt)


ex("ex11.2", 13, r"Find variance and standard deviation: (i) $\sum x = 45$, $\sum x^2 = 421$, $n = 5$ (ii) $\sum fx = 210$, $\sum fx^2 = 7560$, $\sum f = 6$ "
   r"(iii) $\bar{x} = 18$, $\sum fx^2 = 1670$, $\sum f = 5$", [
       short("i", [(r"\sigma^2 = \frac{421}{5} - \left(\frac{45}{5}\right)^2 = 84.2 - 81 = 3.2,\quad \sigma = \sqrt{3.2} \approx 1.79", "$\\sigma^2 = \\frac{\\sum x^2}{n} - \\bar{x}^2$.",
                    "$\\sigma^2 = \\frac{\\sum x^2}{n} - \\bar{x}^2$۔", ["R(421,5) - 9**2 == R(16,5)", near("sqrt(R(16,5))", "1.79", 2)])], "Variance = 3.2, SD = 1.79", r"$\sum x = 45$, $\sum x^2 = 421$, $n = 5$"),
       short("ii", [(r"\sigma^2 = \frac{7560}{6} - \left(\frac{210}{6}\right)^2 = 1260 - 1225 = 35,\quad \sigma = \sqrt{35} \approx 5.92", "$\\sigma^2 = \\frac{\\sum fx^2}{\\sum f} - \\bar{x}^2$.",
                     "$\\sigma^2 = \\frac{\\sum fx^2}{\\sum f} - \\bar{x}^2$۔", ["7560/6 - 35**2 == 35", near("sqrt(35)", "5.92", 2)])], "Variance = 35, SD = 5.92", r"$\sum fx = 210$, $\sum fx^2 = 7560$, $\sum f = 6$"),
       short("iii", [(r"\sigma^2 = \frac{1670}{5} - 18^2 = 334 - 324 = 10,\quad \sigma = \sqrt{10} \approx 3.16", "Same formula with the given mean.", "دیے گئے اوسط کے ساتھ وہی کلیہ۔",
                      ["1670/5 - 18**2 == 10", near("sqrt(10)", "3.16", 2)])], "Variance = 10, SD = 3.16", r"$\bar{x} = 18$, $\sum fx^2 = 1670$, $\sum f = 5$")], "11.2")

# ------------------------------------------------------------------------------------------ Review Exercise 11

q1 = [mcq("i", "______ is used to get the cumulative frequencies.", [r"\text{Addition}", r"\text{square root}", r"\text{multiplication}", r"\text{division}"], 0,
          [T("Cumulative frequencies are running totals.", "مجموعی تعدد جمع کر کے بنتے ہیں۔")]),
      mcq("ii", "Second quartile represents:", [r"\text{mean}", r"\text{mode}", r"\text{median}", r"\text{variance}"], 2, [T("$Q_2$ is the median.", "$Q_2$ وسطانیہ ہے۔")]),
      mcq("iii", "First quartile divides the data into ______ equal parts.", [r"\text{Two}", r"\text{Three}", r"\text{four}", r"\text{ten}"], 2,
          [T("Quartiles split the data into four equal parts.", "ربعیے مواد کو چار برابر حصوں میں تقسیم کرتے ہیں۔")]),
      mcq("iv", "Difference between the highest and the lowest values is called:", [r"\text{mean}", r"\text{variance}", r"\text{range}", r"\text{standard deviation}"], 2, [T("That is the range.", "یہ وسعت ہے۔")]),
      mcq("v", "Scatter diagram represents a relationship between ______ variables.", [r"\text{five}", r"\text{two}", r"\text{three}", r"\text{four}"], 1, [T("Two variables.", "دو متغیر۔")]),
      mcq("vi", "______ is measure of dispersion:", [r"\text{mean}", r"\text{median}", r"\text{mode}", r"\text{variance}"], 3, [T("Variance measures spread.", "تغیر پھیلاؤ ناپتا ہے۔")]),
      mcq("vii", "Positive square root of variance is called:", [r"\text{mean}", r"\text{median}", r"\text{standard deviation}", r"\text{range}"], 2, [T("$\\sigma = \\sqrt{\\sigma^2}$.", "$\\sigma = \\sqrt{\\sigma^2}$۔")]),
      mcq("viii", "______ is not measure of dispersion.", [r"\text{range}", r"\text{arithmetic mean}", r"\text{variance}", r"\text{standard deviation}"], 1,
          [T("The mean is an average, not a spread.", "اوسط پھیلاؤ نہیں ناپتا۔")]),
      mcq("ix", "Variance of the data 8, 8, 8, 8, 8, 8 is:", ["0", "16", "8", "48"], 0, [S(r"\sigma^2 = 0", "All values equal the mean.", "سب قیمتیں اوسط کے برابر ہیں۔", "6*(8 - 8)**2/6 == 0")]),
      mcq("x", "Range of first 20 natural numbers is:", ["20", "10", "19", "30"], 2, [S(r"20 - 1 = 19", "Highest minus lowest.", "بڑی منفی چھوٹی۔", "20 - 1 == 19")])]
ex("rev11", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 11")
CR, FR = [(170, 180), (180, 190), (190, 200), (200, 210), (210, 220), (220, 230)], [2, 6, 9, 12, 8, 3]
ex("rev11", 2, "The following results for the long jump were recorded: Distance (in cm) 170-180, 180-190, 190-200, 200-210, 210-220, 220-230 with $f$ = 2, 6, 9, 12, 8, 3. Construct the "
   "cumulative frequency polygon and locate median, $Q_1$, $Q_3$, $D_7$, $P_{90}$ and interquartile range on it.", [
       ogive("", CR, FR, [("Q_2", r"\frac{N}{2}", 20), ("Q_1", r"\frac{N}{4}", 10), ("Q_3", r"\frac{3N}{4}", 30), ("D_7", r"\frac{7N}{10}", 28), ("P_{90}", r"\frac{90N}{100}", 36)], "", k_ans=1)],
   "Review 11", figure_h=70)
UNIT["items"][-1]["parts"][0]["key_note"] = {"en": "The reference notes give IQR = 19.1 from the rounded quartiles 211.3 - 192.2; from the exact quartiles "
                                                    "211.25 - 192.22 = 19.03, i.e. 19.0.", "ur": "حوالہ نوٹس میں IQR = 19.1 ہے؛ درست ربعیوں سے 19.0 آتا ہے۔"}
one("rev11", 3, r"The summary statistics for a data set is given below. Show it with a box-and-whisker plot. Min. Value 5, Max. Value 70, $Q_1$ 12.6, Median 43, $Q_3$ 55.6.", [
    (r"(5, 12.6, 43, 55.6, 70)", "Box from 12.6 to 55.6 with the median line at 43; whiskers to 5 and 70.", "باکس 12.6 سے 55.6 تک، وسطانیہ 43 پر، لکیریں 5 اور 70 تک۔",
     ["5 < R(126,10)", "R(126,10) < 43", "43 < R(556,10)", "R(556,10) < 70"])], "box from 12.6 to 55.6, median 43, whiskers to 5 and 70", "Review 11", h=55)
UNIT["items"][-1]["parts"][0]["steps"][0]["draw"] = box_draw(5, 12.6, 43, 55.6, 70, 0, 80)
XR, YR = list(range(10)), [90, 85, 83, 80, 76, 74, 72, 70, 68, 65]
str_, ar, br, rr = regression(XR, YR)
str_[0]["draw"] = scatter_draw(XR, YR, ar, br)
estr = ar + br * Q("6.5")
ex("rev11", 4, "The following table shows the weekly hours spent exercising and resting heart rate (beats per minute) for ten individuals: Exercise Hours 0-9; Heart Rate 90, 85, 83, 80, 76, "
   "74, 72, 70, 68, 65. (i) Plot the data on a scatter diagram and draw a line of best fit. (ii) State the type of correlation observed. (iii) Predict the heart rate of Sakeena who "
   "exercises for 6.5 hours per week.", [
       P("i", str_[:2], rf"$\hat{{y}} = {fmt(ar, 2)} - {fmt(-br, 2)}x$", prompt="scatter diagram and line of best fit"),
       P("ii", [str_[2], S(r"\text{" + kind(rr) + "}", "More exercise, lower resting heart rate.", "زیادہ ورزش، کم دل کی دھڑکن۔")], "strong negative correlation", prompt="type of correlation"),
       P("iii", [S(rf"\hat{{y}} = {fmt(ar, 2)} - {fmt(-br, 2)}(6.5) \approx {fmt(estr, 2)}", "Put $x = 6.5$.", "$x = 6.5$ رکھیں۔", near(f"{py(ar)} + ({py(br)})*R(13,2)", fmt(estr, 2), 2))],
         f"{fmt(estr, 2)}", prompt="heart rate for 6.5 hours")], "Review 11", figure_h=70)
one("rev11", 5, "Find the range for the given data, 25, 30, 35, 40, 50, 60, 65, 75", [(r"\text{Range} = 75 - 25 = 50", "Highest minus lowest.", "بڑی منفی چھوٹی۔", ["75 - 25 == 50"])], "50", "Review 11")
st, m, v, s = grouped_dispersion([R(5, 2), R(15, 2), R(25, 2), R(35, 2), R(45, 2), R(55, 2)], [4, 12, 20, 24, 16, 4])
ex("rev11", 6, "Calculate range, variance and standard deviation for the following data set: Class Interval 0-5, 5-10, 10-15, 15-20, 20-25, 25-30 with $f$ = 4, 12, 20, 24, 16, 4.",
   [P("", [S(r"\text{Range} = 30 - 0 = 30", "Upper limit of the last class minus lower limit of the first.", "آخری جماعت کی اوپری حد منفی پہلی کی نچلی حد۔", "30 - 0 == 30")] + st,
      f"Range = 30, Variance = {fmt(v, 1)}, SD = {fmt(s, 1)}")], "Review 11")
one("rev11", 7, "The sum of 5 numbers is 45 and the sum of their squares is 421. Find the mean and standard deviation of the data.", [
    (r"\bar{x} = \frac{45}{5} = 9,\quad \sigma^2 = \frac{421}{5} - 9^2 = 3.2,\quad \sigma = \sqrt{3.2} \approx 1.789", "Use $\\sigma^2 = \\frac{\\sum x^2}{n} - \\bar{x}^2$.",
     "$\\sigma^2 = \\frac{\\sum x^2}{n} - \\bar{x}^2$ استعمال کریں۔", ["45/5 == 9", "R(421,5) - 81 == R(16,5)", near("sqrt(R(16,5))", "1.789", 3)])], "Mean = 9, SD = 1.789", "Review 11")
sa, ma, va, sda = dispersion([45, 47, 46, 48, 46, 47], name="x_A")
sb, mb, vb, sdb = dispersion([38, 52, 40, 50, 42, 49], name="x_B")
p8 = P("", sa + sb + [S(rf"\bar{{x}}_A = {fmt(ma, 2)} > \bar{{x}}_B = {fmt(mb, 2)},\quad \sigma_A = {fmt(sda, 2)} < \sigma_B = {fmt(sdb, 2)}",
                        "Family A spends more on average and its expenses are more stable.", "خاندان A اوسطاً زیادہ خرچ کرتا ہے اور اس کے اخراجات زیادہ مستحکم ہیں۔")],
       f"A: mean {fmt(ma, 2)}, SD {fmt(sda, 2)}; B: mean {fmt(mb, 2)}, SD {fmt(sdb, 2)}; Family A spends more and is more stable")
p8["key_note"] = {"en": "The reference notes use $\\sum x_B^2 = 12521$ (the correct sum is 12413), so their $s_B = 5.73$; computed from the data $s_B = 5.37$ (the conclusion is the same).",
                  "ur": "حوالہ نوٹس میں $\\sum x_B^2$ غلط ہے؛ درست $s_B = 5.37$ ہے۔"}
ex("rev11", 8, "The monthly household expenses (rupees in thousands) of two families for 6 months were: Family A: 45, 47, 46, 48, 46, 47; Family B: 38, 52, 40, 50, 42, 49. Calculate the "
   "mean and standard deviation of the monthly expenses. Which family spends more on average? Which family has more stable expenses?", [p8], "Review 11")
st, m, v, s = grouped_dispersion([1100, 1300, 1500, 1700, 1900], [6, 10, 12, 8, 4])
ex("rev11", 9, "The daily wages of 40 workers in a factory are grouped as follows (Daily Wages in Rs.): 1000-1200, 1200-1400, 1400-1600, 1600-1800, 1800-2000 with No. of Workers 6, 10, 12, 8, 4. Find the mean, "
   "variance and standard deviation of the daily wages.", [P("", st, f"Mean = {fmt(m, 0)}, Variance = {fmt(v, 0)}, SD = {fmt(s, 2)}")], "Review 11")
