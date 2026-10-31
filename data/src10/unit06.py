"""Class 10, Unit 6 - Vectors in Plane: Exercises 6.1-6.3 and Review Exercise 6.

Questions transcribed from the reference notes (data/class10/pages/u06_*.png); every component, magnitude and unit vector is
checked with sympy; final answers are checked against data/answers10/unit06.json.
(Ex 6.2 Q6: the notes write -7n for -3n in one line of working; their answer n = 47/37, m = -3/37 is correct.)
"""
import sympy as sp

from _gen import Graph, maker, mcq, ps
from _helpers import P, S, T

UNIT = {"unit": 6, "title": "Vectors in Plane", "title_ur": "مستوی میں سمتیے", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational
I_, J_ = r"\underline{i}", r"\underline{j}"


def num(v):
    return sp.latex(sp.nsimplify(v))


def comp(c):
    """A component as the notes write it: 3/5, -4/sqrt(41), 1/sqrt(2)."""
    c = sp.nsimplify(c)
    if c.is_Rational:
        return sp.latex(c)
    q = sp.nsimplify(c ** 2)
    a, b = sp.fraction(q)
    if sp.sqrt(a).is_Integer:
        sign = "-" if c < 0 else ""
        return rf"{sign}\frac{{{sp.sqrt(a)}}}{{\sqrt{{{b}}}}}"
    return sp.latex(c)


def vt(v):
    """x i + y j."""
    x, y = [sp.nsimplify(t) for t in v]
    def term(c, u, first):
        if c == 0:
            return ""
        ct = comp(c)
        if ct == "1":
            ct = ""
        elif ct == "-1":
            ct = "-"
        s = ct + u
        if first:
            return s
        return (" - " + s[1:]) if s.startswith("-") else (" + " + s)
    out = term(x, I_, True) + term(y, J_, x == 0)
    return out or "0"


def vpy(v):
    return f"({sp.sstr(v[0])}, {sp.sstr(v[1])})"


def mag(v):
    return sp.sqrt(sp.nsimplify(v[0]) ** 2 + sp.nsimplify(v[1]) ** 2)


def mag_steps(v, name="a"):
    x, y = [sp.nsimplify(t) for t in v]
    m = mag(v)
    return [S(rf"|{name}| = \sqrt{{({num(x)})^2 + ({num(y)})^2}} = \sqrt{{{num(x ** 2)} + {num(y ** 2)}}} = {num(m)}",
              "Magnitude $= \\sqrt{x^2 + y^2}$.", "مقدار $= \\sqrt{x^2 + y^2}$۔", f"sqrt(({sp.sstr(x)})**2 + ({sp.sstr(y)})**2) == {ps(m)}")], m


def unit_steps(v, name="a"):
    st, m = mag_steps(v, name)
    u = (sp.nsimplify(v[0]) / m, sp.nsimplify(v[1]) / m)
    st.append(S(rf"\hat{{{name}}} = \frac{{{name}}}{{|{name}|}} = \frac{{{vt(v)}}}{{{num(m)}}} = {vt(u)}", "Divide the vector by its magnitude.",
                "سمتیہ کو اس کی مقدار سے تقسیم کریں۔", f"({sp.sstr(u[0])})**2 + ({sp.sstr(u[1])})**2 == 1",
                f"({sp.sstr(u[0])})*{ps(m)} == {ps(v[0])}", f"({sp.sstr(u[1])})*{ps(m)} == {ps(v[1])}"))
    return st, u


def combo(coefs, vecs, names):
    """sum k_i v_i, shown term by term."""
    res = (sum(k * v[0] for k, v in zip(coefs, vecs)), sum(k * v[1] for k, v in zip(coefs, vecs)))
    expr = ""
    for k, n in zip(coefs, names):
        kt = "" if k == 1 else "-" if k == -1 else num(k)
        expr += ("" if not expr else (" - " if k < 0 else " + ")) + (kt.lstrip("-") if expr else kt) + rf"\underline{{{n}}}"
    sub = ""
    for k, v in zip(coefs, vecs):
        kt = "" if abs(k) == 1 else num(abs(k))
        piece = rf"{kt}\left({vt(v)}\right)"
        sub += ((" - " if k < 0 else "") if not sub else (" - " if k < 0 else " + ")) + piece
    open_ = ""
    for k, v in zip(coefs, vecs):
        w = (k * v[0], k * v[1])
        t = vt(w)
        open_ += t if not open_ else ((" - " + t[1:]) if t.startswith("-") else (" + " + t))
    steps = [S(rf"{expr} = {sub}", "Put in the vectors.", "سمتیے رکھیں۔"),
             S(rf"= {open_}", "Multiply each vector by its number.", "ہر سمتیے کو اس کے عدد سے ضرب دیں۔"),
             S(rf"= {vt(res)}", "Add the $\\underline{i}$ parts and the $\\underline{j}$ parts.", "$\\underline{i}$ والے اور $\\underline{j}$ والے حصے الگ الگ جمع کریں۔",
               f"{' + '.join(f'({sp.sstr(k)})*({sp.sstr(v[0])})' for k, v in zip(coefs, vecs))} == {ps(res[0])}",
               f"{' + '.join(f'({sp.sstr(k)})*({sp.sstr(v[1])})' for k, v in zip(coefs, vecs))} == {ps(res[1])}")]
    return steps, res, expr


def ab_vector(A, B, an="A", bn="B"):
    v = (B[0] - A[0], B[1] - A[1])
    return S(rf"\overrightarrow{{{an}{bn}}} = (x_2 - x_1){I_} + (y_2 - y_1){J_} = ({num(B[0])} - ({num(A[0])})){I_} + ({num(B[1])} - ({num(A[1])})){J_} = {vt(v)}",
             "Tip minus tail: subtract the coordinates of the first point from the second.", "دوسرے نقطے کے محدد سے پہلے نقطے کے محدد تفریق کریں۔",
             f"{ps(B[0])} - {ps(A[0])} == {ps(v[0])}", f"{ps(B[1])} - {ps(A[1])} == {ps(v[1])}"), v


def quadrant(p):
    x, y = p
    return {(1, 1): "I", (-1, 1): "II", (-1, -1): "III", (1, -1): "IV"}[(sp.sign(x), sp.sign(y))]


# ------------------------------------------------------------------------------------------ Exercise 6.1

PTS = [("i", (4, 3)), ("ii", (5, -4)), ("iii", (-6, 2)), ("iv", (-4, -4))]
ex("ex6.1", 1, "Name the quadrant in which each point lies. " + " ".join(f"({l}) $({p[0]}, {p[1]})$" for l, p in PTS), [
    P(l, [S(rf"x = {p[0]} {'> 0' if p[0] > 0 else '< 0'},\ y = {p[1]} {'> 0' if p[1] > 0 else '< 0'} \Rightarrow \text{{Quadrant {quadrant(p)}}}",
            "Quadrant I: $(+, +)$, II: $(-, +)$, III: $(-, -)$, IV: $(+, -)$.", "ربع I: $(+, +)$، II: $(-, +)$، III: $(-, -)$، IV: $(+, -)$۔",
            f"{p[0]} {'>' if p[0] > 0 else '<'} 0", f"{p[1]} {'>' if p[1] > 0 else '<'} 0")], f"Quadrant {quadrant(p)}", prompt=f"$({p[0]}, {p[1]})$")
    for l, p in PTS], "6.1")

PL = [("i", "A", (3, -3)), ("ii", "B", (-3, 3)), ("iii", "C", (5, 7)), ("iv", "D", (-2, -4))]
g = Graph((-6, 8), (-6, 8))
ex("ex6.1", 2, "Plot the following points on the coordinate plane: " + " ".join(f"({l}) ${n}({p[0]}, {p[1]})$" for l, n, p in PL), [P("", [
    S(r"\text{Draw the } x\text{-axis and } y\text{-axis}", "Draw the two axes and mark equal units.", "دونوں محور کھینچ کر برابر اکائیاں لگائیں۔", draw=g.axes())] + [
    S(rf"{n}({p[0]}, {p[1]})", f"Move {abs(p[0])} units {'right' if p[0] > 0 else 'left'} and {abs(p[1])} units {'up' if p[1] > 0 else 'down'}; mark ${n}$ (quadrant {quadrant(p)}).",
      f"{abs(p[0])} اکائی {'دائیں' if p[0] > 0 else 'بائیں'} اور {abs(p[1])} اکائی {'اوپر' if p[1] > 0 else 'نیچے'} جائیں؛ ${n}$ لگائیں۔",
      f"{p[0]}*{p[1]} == {p[0] * p[1]}", draw=g.point(p[0], p[1], f"{n}({p[0]}, {p[1]})")) for l, n, p in PL],
    "plotted: " + ", ".join(f"{n}({p[0]}, {p[1]}) in quadrant {quadrant(p)}" for _, n, p in PL))], "6.1", figure_h=70)

TT = [("i", "B", "A"), ("ii", "P", "Q"), ("iii", "S", "R"), ("iv", "M", "N"), ("v", "A", "B"), ("vi", "D", "C")]
ex("ex6.1", 3, "Name the tail and tip of the following vectors (as drawn in the book: (i) from $B$ to $A$, (ii) from $P$ to $Q$, (iii) from $S$ to $R$, "
   "(iv) from $M$ to $N$, (v) from $A$ to $B$, (vi) from $D$ to $C$).", [
       P(l, [S(rf"\text{{Tail}} = {t},\quad \text{{Tip}} = {h}", "The tail is the starting point; the tip is where the arrowhead is.",
               "دم ابتدائی نقطہ ہے؛ سرا وہ ہے جہاں تیر کا نشان ہے۔", draw=[{"t": "line", "p": [30, 45, 70, 15], "arrow": True},
                                                                         {"t": "text", "p": [24, 50], "s": t}, {"t": "text", "p": [72, 12], "s": h}])],
         f"Tail = {t}, Tip = {h}", prompt=f"vector from ${t}$ to ${h}$") for l, t, h in TT], "6.1")

AB4 = [("i", (1, -7), (-2, 4)), ("ii", (8, 9), (12, 3))]
ex("ex6.1", 4, r"Write the vector $\overrightarrow{AB}$ in the form of $x\underline{i}+y\underline{j}$: (i) $A(1,-7), B(-2,4)$ (ii) $A(8,9), B(12,3)$", [
    P(l, [ab_vector(A, B)[0]], f"${vt((B[0] - A[0], B[1] - A[1]))}$", prompt=f"$A({A[0]},{A[1]}), B({B[0]},{B[1]})$") for l, A, B in AB4], "6.1")

M5 = [("i", (-3, 2)), ("ii", (4, -3)), ("iii", (R(1, 2), R(3, 2)))]
ex("ex6.1", 5, r"Find the magnitude of the $\underline{a}$: " + " ".join(f"({l}) $\\underline{{a}} = {vt(v)}$" for l, v in M5), [
    P(l, mag_steps(v)[0], f"${num(mag(v))}$", prompt=f"$\\underline{{a}} = {vt(v)}$") for l, v in M5], "6.1")

U6 = [("i", (-4, 5)), ("ii", (6, 8)), ("iii", (1 / sp.sqrt(6), 1 / sp.sqrt(6))), ("iv", (R(1, 2), R(-3, 4)))]
ex("ex6.1", 6, "Find a unit vector in the direction of the vector given below: " + " ".join(f"({l}) $\\underline{{a}} = {vt(v)}$" for l, v in U6), [
    P(l, unit_steps(v)[0], f"${vt(unit_steps(v)[1])}$", prompt=f"$\\underline{{a}} = {vt(v)}$") for l, v in U6], "6.1")


def unit_of_combo(eid, n, question, coefs, vecs, names, exercise):
    st, v, expr = combo(coefs, vecs, names)
    us, u = unit_steps(v, "v")
    st.append(S(rf"\text{{Let }} \underline{{v}} = {expr} = {vt(v)}", "Call the result $\\underline{v}$.", "نتیجہ کو $\\underline{v}$ کہیں۔"))
    st += us
    st.append(T("A vector divided by its magnitude keeps its direction and has length 1, so it is parallel to the original vector.",
                "سمتیہ کو اس کی مقدار سے تقسیم کرنے پر سمت وہی رہتی ہے اور لمبائی 1 ہو جاتی ہے، اس لیے یہ اصل سمتیے کے متوازی ہے۔"))
    ex(eid, n, question, [P("", st, f"${vt(u)}$")], exercise)


a7, b7, c7 = (5, -7), (-1, -1), (2, 3)
unit_of_combo("ex6.1", 7, rf"If $\underline{{a}}={vt(a7)}$, $\underline{{b}}={vt(b7)}$ and $\underline{{c}}={vt(c7)}$, then find unit vector parallel to "
              r"$\underline{a}+\underline{b}-3\underline{c}$.", [1, 1, -3], [a7, b7, c7], "abc", "6.1")
a8, b8, c8 = (3, -1), (-2, 4), (1, 2)
unit_of_combo("ex6.1", 8, rf"If $\underline{{a}}={vt(a8)}$, $\underline{{b}}={vt(b8)}$ and $\underline{{c}}={vt(c8)}$, then find unit vector parallel to "
              r"$3\underline{a}-2\underline{c}+4\underline{b}$.", [3, -2, 4], [a8, c8, b8], "acb", "6.1")

PAR = [("i", (6, 1), (12, 2)), ("ii", (-2, 3), (6, -9)), ("iii", (5, -4), (6, -3)), ("iv", (3, -7), (6, -14))]


def parallel(label, a, b):
    k0, k1 = sp.Rational(b[0], a[0]), sp.Rational(b[1], a[1])
    if k0 == k1:
        st = [S(rf"\underline{{b}} = {vt(b)} = {num(k0)}\left({vt(a)}\right) = {num(k0)}\underline{{a}}", "One vector is a number times the other.",
                "ایک سمتیہ دوسرے کا عددی مضرب ہے۔", f"{k0}*{a[0]} == {b[0]}", f"{k0}*{a[1]} == {b[1]}"),
              S(r"\text{parallel}", "Vectors that are multiples of each other are parallel.", "ایک دوسرے کے مضرب سمتیے متوازی ہوتے ہیں۔")]
        return P(label, st, f"parallel ($\\underline{{b}} = {num(k0)}\\underline{{a}}$)", prompt=f"$\\underline{{a}}={vt(a)},\\ \\underline{{b}}={vt(b)}$")
    st = [S(rf"\frac{{{b[0]}}}{{{a[0]}}} = {num(k0)},\quad \frac{{{b[1]}}}{{{a[1]}}} = {num(k1)}", "Compare the ratios of the components.", "اجزاء کی نسبتوں کا موازنہ کریں۔",
            f"Ne({k0}, {k1})"),
          S(r"\text{not parallel}", "The ratios are different, so $\\underline{b}$ is not a multiple of $\\underline{a}$.", "نسبتیں مختلف ہیں، اس لیے متوازی نہیں۔")]
    return P(label, st, "not parallel", prompt=f"$\\underline{{a}}={vt(a)},\\ \\underline{{b}}={vt(b)}$")


ex("ex6.1", 9, "Which of the following vectors are parallel? " + " ".join(f"({l}) $\\underline{{a}}={vt(a)},\\ \\underline{{b}}={vt(b)}$" for l, a, b in PAR),
   [parallel(l, a, b) for l, a, b in PAR], "6.1")
ex("ex6.1", 10, r"Find a vector thrice in length of $3\underline{i}-2\underline{j}$, but opposite in direction.", [P("", [
    S(rf"3\left({vt((3, -2))}\right) = {vt((9, -6))}", "Three times the length: multiply by 3.", "تین گنا لمبائی: 3 سے ضرب دیں۔", "3*3 == 9", "3*(-2) == -6"),
    S(rf"-3\left({vt((3, -2))}\right) = {vt((-9, 6))}", "Opposite direction: change the sign.", "مخالف سمت: علامت بدلیں۔", "-3*3 == -9", "-3*(-2) == 6")],
    f"${vt((-9, 6))}$")], "6.1")
ex("ex6.1", 11, r"Find two vectors that are double in magnitude of $3\underline{i}-5\underline{j}$, one in the same direction of it and other in its opposite direction.", [P("", [
    S(rf"2\left({vt((3, -5))}\right) = {vt((6, -10))}", "Same direction, double magnitude.", "اسی سمت، دگنی مقدار۔", "2*3 == 6", "2*(-5) == -10"),
    S(rf"-2\left({vt((3, -5))}\right) = {vt((-6, 10))}", "Opposite direction, double magnitude.", "مخالف سمت، دگنی مقدار۔", "-2*3 == -6", "-2*(-5) == 10")],
    f"${vt((6, -10))}$ and ${vt((-6, 10))}$")], "6.1")

# ------------------------------------------------------------------------------------------ Exercise 6.2

a1, b1 = (7, -3), (1, 5)
Q1 = [("i", [1, 1]), ("ii", [1, 3]), ("iii", [3, R(1, 2)]), ("iv", [-1, 1]), ("v", [-5, 4]), ("vi", [R(3, 2), -1])]


def labelled(coefs):
    a, b = coefs
    t = ""
    for k, n in ((a, "a"), (b, "b")):
        if k == 0:
            continue
        kt = "" if abs(k) == 1 else num(abs(k))
        t += ("-" if k < 0 else "") if not t else (" - " if k < 0 else " + ")
        t += kt + rf"\underline{{{n}}}"
    return t


q1 = []
for l, cf in Q1:
    order = [(cf[1], b1, "b"), (cf[0], a1, "a")] if l in ("iv", "v") else [(cf[0], a1, "a"), (cf[1], b1, "b")]
    st, v, _ = combo([o[0] for o in order], [o[1] for o in order], [o[2] for o in order])
    book = {"iv": r"\underline{b}-\underline{a}", "v": r"4\underline{b}-5\underline{a}"}   # as printed, b first
    q1.append(P(l, st, f"${vt(v)}$", prompt=f"${book[l]}$" if l in book else f"${labelled(cf)}$"))
ex("ex6.2", 1, rf"If $\underline{{a}}={vt(a1)}$ and $\underline{{b}}={vt(b1)}$, then find the following vectors: (i) $\underline{{a}}+\underline{{b}}$ "
   r"(ii) $\underline{a}+3\underline{b}$ (iii) $3\underline{a}+\frac{1}{2}\underline{b}$ (iv) $\underline{b}-\underline{a}$ (v) $4\underline{b}-5\underline{a}$ "
   r"(vi) $\frac{3}{2}\underline{a}-\underline{b}$", q1, "6.2")

a2, b2, c2 = (6, -1), (1, 5), (3, 5)
Q2 = [("i", [1, -1], [b2, c2], "bc", r"\underline{b}-\underline{c}"), ("ii", [1, -2, 1], [a2, b2, c2], "abc", r"\underline{a}-2\underline{b}+\underline{c}"),
      ("iii", [1, -1, -1], [c2, b2, a2], "cba", r"\underline{c}-\underline{b}-\underline{a}")]
q2 = []
for l, cf, vs, ns, t in Q2:
    st, v, _ = combo(cf, vs, ns)
    ms, m = mag_steps(v, "v")
    q2.append(P(l, st + ms, f"${num(m)}$", prompt=f"${t}$"))
ex("ex6.2", 2, rf"If $\underline{{a}}={vt(a2)}$, $\underline{{b}}={vt(b2)}$ and $\underline{{c}}={vt(c2)}$, then find the magnitudes of the following vectors: "
   r"(i) $\underline{b}-\underline{c}$ (ii) $\underline{a}-2\underline{b}+\underline{c}$ (iii) $\underline{c}-\underline{b}-\underline{a}$", q2, "6.2")


def compare(label, lhs_tex, lhs_parts, rhs, unknowns, prompt):
    """(p x + q) i + (r y + s) j = rhs: compare coefficients and solve."""
    syms = {u: sp.Symbol(u) for u in unknowns}
    ci, cj = [sp.sympify(t, locals=syms) for t in lhs_parts]
    sol = sp.solve([ci - rhs[0], cj - rhs[1]], list(syms.values()), dict=True)[0]
    vals = {u: sol[s] for u, s in syms.items()}
    st = [S(rf"{lhs_tex} = ({sp.latex(ci)}){I_} + ({sp.latex(cj)}){J_} = {vt(rhs)}", "Collect the $\\underline{i}$ terms and the $\\underline{j}$ terms.",
            "$\\underline{i}$ والے اور $\\underline{j}$ والے ارکان اکٹھے کریں۔"),
          S(rf"{sp.latex(ci)} = {num(rhs[0])},\quad {sp.latex(cj)} = {num(rhs[1])}", "Equal vectors have equal components: compare the coefficients.",
            "مساوی سمتیوں کے اجزاء برابر ہوتے ہیں: عددی سروں کا موازنہ کریں۔"),
          S(r",\quad ".join(f"{u} = {num(v)}" for u, v in vals.items()), "Solve.", "حل کریں۔",
            f"({sp.sstr(ci)}).subs({{{', '.join(f'{u}: {ps(v)}' for u, v in vals.items())}}}) == {ps(rhs[0])}",
            f"({sp.sstr(cj)}).subs({{{', '.join(f'{u}: {ps(v)}' for u, v in vals.items())}}}) == {ps(rhs[1])}")]
    return P(label, st, "$" + r",\ ".join(f"{u} = {num(v)}" for u, v in vals.items()) + "$", prompt=prompt)


ex("ex6.2", 3, r"Find the values of $x$ and $y$ in each of the following equations: (i) $(x\underline{i}+y\underline{j})+(2\underline{i}+3\underline{j})=7\underline{i}+6\underline{j}$ "
   r"(ii) $(x\underline{i}-5\underline{j})+(3\underline{i}+5\underline{j})=-8\underline{i}+y\underline{j}$ (iii) $(y\underline{i}+3\underline{j})+(-5\underline{i}+2x\underline{j})=9\underline{i}+7\underline{j}$", [
       compare("i", r"(x\underline{i} + y\underline{j}) + (2\underline{i} + 3\underline{j})", ["x+2", "y+3"], (7, 6), "xy",
               r"$(x\underline{i}+y\underline{j})+(2\underline{i}+3\underline{j})=7\underline{i}+6\underline{j}$"),
       P("ii", [S(r"(x\underline{i} - 5\underline{j}) + (3\underline{i} + 5\underline{j}) = (x + 3)\underline{i} + 0\underline{j} = -8\underline{i} + y\underline{j}",
                  "Collect the components.", "اجزاء اکٹھے کریں۔"),
                S(r"x + 3 = -8,\quad y = 0", "Compare the coefficients.", "عددی سروں کا موازنہ کریں۔"),
                S(r"x = -11,\quad y = 0", "Solve.", "حل کریں۔", "-11 + 3 == -8", "-5 + 5 == 0")], r"$x = -11,\ y = 0$",
         prompt=r"$(x\underline{i}-5\underline{j})+(3\underline{i}+5\underline{j})=-8\underline{i}+y\underline{j}$"),
       compare("iii", r"(y\underline{i} + 3\underline{j}) + (-5\underline{i} + 2x\underline{j})", ["y-5", "3+2*x"], (9, 7), "xy",
               r"$(y\underline{i}+3\underline{j})+(-5\underline{i}+2x\underline{j})=9\underline{i}+7\underline{j}$")], "6.2")

ex("ex6.2", 4, r"If $\underline{a}=\underline{i}+3\underline{j}$, $\underline{c}=2\underline{i}+\underline{j}$ and $\underline{a}+2\underline{b}=\underline{c}$, then find $|\underline{b}|$.", [P("", [
    S(r"2\underline{b} = \underline{c} - \underline{a} = (2\underline{i} + \underline{j}) - (\underline{i} + 3\underline{j}) = \underline{i} - 2\underline{j}",
      "Make $\\underline{b}$ the subject.", "$\\underline{b}$ کو موضوع بنائیں۔", "2 - 1 == 1", "1 - 3 == -2"),
    S(rf"\underline{{b}} = {vt((R(1, 2), -1))}", "Divide by 2.", "2 سے تقسیم کریں۔")] + mag_steps((R(1, 2), -1), "b")[0], r"$\frac{\sqrt{5}}{2}$")], "6.2")
st5, v5, _ = combo([1, 5], [(-2, 7), (3, -5)], "ab")
ex("ex6.2", 5, r"If $\underline{a}=-2\underline{i}+7\underline{j}$ and $\underline{b}=3\underline{i}-5\underline{j}$, then find the vector components of $\underline{a}+5\underline{b}$.",
   [P("", st5 + [S(rf"\text{{components: }} {num(v5[0])}\ \text{{along }} \underline{{i}},\ {num(v5[1])}\ \text{{along }} \underline{{j}}", "Read off the components.",
                   "اجزاء پڑھیں۔")], f"${vt(v5)}$")], "6.2")
p6 = P("", [S(r"5\underline{i} - 3\underline{j} = m\underline{i} - 10m\underline{j} + 4n\underline{i} - 3n\underline{j} = (m + 4n)\underline{i} - (10m + 3n)\underline{j}",
              "Multiply out and collect the components.", "ضرب دے کر اجزاء اکٹھے کریں۔"),
            S(r"m + 4n = 5 \quad (1),\qquad 10m + 3n = 3 \quad (2)", "Compare the coefficients.", "عددی سروں کا موازنہ کریں۔"),
            S(r"10(1) - (2):\ 40n - 3n = 50 - 3 \Rightarrow 37n = 47 \Rightarrow n = \frac{47}{37}", "Eliminate $m$.", "$m$ ختم کریں۔", "40 - 3 == 37", "50 - 3 == 47"),
            S(r"m = 5 - 4\left(\frac{47}{37}\right) = \frac{185 - 188}{37} = -\frac{3}{37}", "Put $n$ in (1).", "$n$ کی قیمت (1) میں رکھیں۔",
              "R(-3,37) + 4*R(47,37) == 5", "10*R(-3,37) + 3*R(47,37) == 3")], r"$m = -\frac{3}{37},\ n = \frac{47}{37}$")
ex("ex6.2", 6, r"If $5\underline{i}-3\underline{j}=m(\underline{i}-10\underline{j})+n(4\underline{i}-3\underline{j})$, then find the values of $m$ and $n$.", [p6], "6.2")


def translate(eid, n, question, names, pts, tv, exercise, h=70):
    new = [(p[0] + tv[0], p[1] + tv[1]) for p in pts]
    xs = [p[0] for p in pts + new]
    ys = [p[1] for p in pts + new]
    g = Graph((min(xs + [0]) - 2, max(xs + [0]) + 2), (min(ys + [0]) - 2, max(ys + [0]) + 2))
    poly = sum(([g.X(p[0]), g.Y(p[1])] for p in pts), [])
    poly2 = sum(([g.X(p[0]), g.Y(p[1])] for p in new), [])
    steps = [S(r"\text{Plot } " + ", ".join(f"{a}({p[0]}, {p[1]})" for a, p in zip(names, pts)), "Plot the given points and join them.", "دیے گئے نقاط لگا کر ملائیں۔",
               draw=g.axes() + [{"t": "poly", "p": poly, "close": True}] + sum((g.point(p[0], p[1], a) for a, p in zip(names, pts)), []))]
    for a, p, q in zip(names, pts, new):
        steps.append(S(rf"{a}({p[0]}, {p[1]}) \to {a}'({p[0]} + ({tv[0]}), {p[1]} + ({tv[1]})) = {a}'({q[0]}, {q[1]})",
                       f"Add the translation vector ${vt(tv)}$: $x$ changes by {tv[0]}, $y$ by {tv[1]}.", f"انتقالی سمتیہ ${vt(tv)}$ جمع کریں۔",
                       f"{p[0]} + ({tv[0]}) == {q[0]}", f"{p[1]} + ({tv[1]}) == {q[1]}",
                       draw=[{"t": "line", "p": [g.X(p[0]), g.Y(p[1]), g.X(q[0]), g.Y(q[1])], "dash": True}] + g.point(q[0], q[1], a + "'")))
    steps.append(S(r"\text{Join the image points}", "The image has the same shape and size; it has only moved.", "عکس کی شکل اور سائز وہی ہے؛ صرف جگہ بدلی ہے۔",
                   draw=[{"t": "poly", "p": poly2, "close": True}]))
    ex(eid, n, question, [P("", steps, ", ".join(f"${a}'({q[0]}, {q[1]})$" for a, q in zip(names, new)))], exercise, figure_h=h)


# ------------------------------------------------------------------------------------------ Exercise 6.3

translate("ex6.3", 1, r"Plot $A(-5,4)$, $B(-6,1)$ and $C(-3,1)$ to form a $\triangle ABC$. Also translate $\triangle ABC$ to $\triangle A'B'C'$ by translation vector "
          r"$8\underline{i}-6\underline{j}$.", "ABC", [(-5, 4), (-6, 1), (-3, 1)], (8, -6), "6.3")
translate("ex6.3", 2, r"Plot $A(-6,-2)$, $B(-6,-5)$, $C(-3,-5)$ and $D(-3,-2)$ to form a square $ABCD$. Also translate square $ABCD$ to square $A'B'C'D'$ by "
          r"translation vector $9\underline{i}+7\underline{j}$.", "ABCD", [(-6, -2), (-6, -5), (-3, -5), (-3, -2)], (9, 7), "6.3")
translate("ex6.3", 3, r"Plot $A(-6,3)$, $B(-4,0)$, $C(-2,3)$ and $D(-4,4)$ to form a kite $ABCD$. Also translate kite $ABCD$ to kite $A'B'C'D'$ by translation "
          r"vector $6\underline{i}-6\underline{j}$.", "ABCD", [(-6, 3), (-4, 0), (-2, 3), (-4, 4)], (6, -6), "6.3")

ex("ex6.3", 4, "The coordinates of $A$, $B$ and $D$ are $(1,2)$, $(6,3)$ and $(2,8)$ respectively. Find the coordinates of $C$ by using vector method if $ABCD$ is a parallelogram.", [P("", [
    S(r"\overrightarrow{AB} = \overrightarrow{DC}", "In a parallelogram opposite sides are equal and parallel.", "متوازی الاضلاع میں مخالف اضلاع برابر اور متوازی ہوتے ہیں۔"),
    S(r"\overrightarrow{AB} = (6 - 1, 3 - 2) = (5, 1),\quad \overrightarrow{DC} = (x_C - 2,\ y_C - 8)", "Write both vectors.", "دونوں سمتیے لکھیں۔"),
    S(r"x_C - 2 = 5 \Rightarrow x_C = 7,\quad y_C - 8 = 1 \Rightarrow y_C = 9", "Equate the components.", "اجزاء برابر کریں۔", "7 - 2 == 6 - 1", "9 - 8 == 3 - 2")],
    "$C(7, 9)$")], "6.3")
ex("ex6.3", 5, r"In parallelogram $ABCD$, the vectors representing two opposite sides are $\overrightarrow{AB}=6\underline{i}+2\underline{j}$, $\overrightarrow{DC}=-6\underline{i}-2\underline{j}$. "
   "Show that the opposite sides are equal in magnitude and parallel.", [P("", [
       S(r"|\overrightarrow{AB}| = \sqrt{6^2 + 2^2} = \sqrt{40},\quad |\overrightarrow{DC}| = \sqrt{(-6)^2 + (-2)^2} = \sqrt{40}", "Equal magnitudes.", "مقداریں برابر ہیں۔",
         "sqrt(6**2 + 2**2) == sqrt(40)", "sqrt((-6)**2 + (-2)**2) == sqrt(40)"),
       S(r"\overrightarrow{AB} = -\overrightarrow{DC}", "One is $-1$ times the other, so they are parallel.", "ایک دوسرے کا $-1$ گنا ہے، اس لیے متوازی ہیں۔", "-(-6) == 6", "-(-2) == 2")],
       r"$|\overrightarrow{AB}| = |\overrightarrow{DC}| = \sqrt{40}$ and $\overrightarrow{AB} = -\overrightarrow{DC}$ (parallel)")], "6.3")


def isosceles(eid, n, question, names, pts, exercise):
    (a, A), (b, B), (c, C) = zip(names, pts)
    st, vs = [], {}
    for (p, P1), (q, Q1) in (((a, A), (b, B)), ((a, A), (c, C)), ((b, B), (c, C))):
        s, v = ab_vector(P1, Q1, p, q)
        st.append(s)
        vs[p + q] = v
    for k, v in vs.items():
        st.append(S(rf"|\overrightarrow{{{k}}}| = \sqrt{{({num(v[0])})^2 + ({num(v[1])})^2}} = {num(mag(v))}", "Magnitude of each side.", "ہر ضلع کی مقدار۔",
                    f"sqrt(({v[0]})**2 + ({v[1]})**2) == {ps(mag(v))}"))
    mags = {k: mag(v) for k, v in vs.items()}
    eq = [(k1, k2) for k1 in mags for k2 in mags if k1 < k2 and mags[k1] == mags[k2]][0]
    st.append(S(rf"|\overrightarrow{{{eq[0]}}}| = |\overrightarrow{{{eq[1]}}}| \Rightarrow \text{{isosceles}}", "Two sides are equal, so the triangle is isosceles.",
                "دو اضلاع برابر ہیں، اس لیے مثلث متساوی الساقین ہے۔"))
    ex(eid, n, question, [P("", st, f"isosceles: $|\\overrightarrow{{{eq[0]}}}| = |\\overrightarrow{{{eq[1]}}}| = {num(mags[eq[0]])}$")], exercise)


isosceles("ex6.3", 6, "Points $A(1,2)$, $B(4,6)$ and $C(7,2)$ form a triangle. Check whether triangle $ABC$ is an isosceles by using vector magnitude.",
          "ABC", [(1, 2), (4, 6), (7, 2)], "6.3")


def parallelogram(eid, n, question, names, pts, exercise):
    P_, Q_, R_, S_ = pts
    a, b, c, d = names
    s1, v1 = ab_vector(P_, Q_, a, b)
    s2, v2 = ab_vector(S_, R_, d, c)
    s3, v3 = ab_vector(P_, S_, a, d)
    s4, v4 = ab_vector(Q_, R_, b, c)
    st = [s1, s2, s3, s4, S(rf"\overrightarrow{{{a}{b}}} = \overrightarrow{{{d}{c}}},\quad \overrightarrow{{{a}{d}}} = \overrightarrow{{{b}{c}}}",
                             "Both pairs of opposite sides are equal and parallel, so it is a parallelogram.", "مخالف اضلاع کے دونوں جوڑے برابر اور متوازی ہیں، اس لیے یہ متوازی الاضلاع ہے۔",
                             f"{v1[0]} == {v2[0]}", f"{v1[1]} == {v2[1]}", f"{v3[0]} == {v4[0]}", f"{v3[1]} == {v4[1]}")]
    ex(eid, n, question, [P("", st, f"${a}{b}{c}{d}$ is a parallelogram")], exercise)


parallelogram("ex6.3", 7, "Use vectors to show that $PQRS$ is a parallelogram, where the points $P$, $Q$, $R$ and $S$ have coordinates $(1,2)$, $(5,2)$, $(7,6)$ and $(3,6)$ respectively.",
              "PQRS", [(1, 2), (5, 2), (7, 6), (3, 6)], "6.3")
isosceles("ex6.3", 8, "Use vectors to show that triangle $XYZ$ is an isosceles, where the points $X$, $Y$, $Z$ have the coordinates $(0,0)$, $(2,0)$ and $(1,3)$ respectively.",
          "XYZ", [(0, 0), (2, 0), (1, 3)], "6.3")
ex("ex6.3", 9, r"A ball is projected with an initial velocity vector $\underline{v}_0=10\underline{i}+20\underline{j}$. The horizontal component is in the $x$-direction and "
   r"gravity is $\underline{g}=0\underline{i}-10\underline{j}$. Find the maximum height and horizontal range.", [P("", [
       S(r"v_{0x} = 10,\quad v_{0y} = 20,\quad g = 10", "Read the components.", "اجزاء پڑھیں۔"),
       S(r"H = \frac{v_{0y}^2}{2g} = \frac{20^2}{2 \cdot 10} = 20", "Maximum height.", "زیادہ سے زیادہ بلندی۔", "20**2/(2*10) == 20"),
       S(r"R = \frac{2 v_{0x} v_{0y}}{g} = \frac{2 \cdot 10 \cdot 20}{10} = 40", "Horizontal range.", "افقی فاصلہ۔", "2*10*20/10 == 40")],
       "$H = 20$ m, $R = 40$ m")], "6.3")
ex("ex6.3", 10, r"A car enters a loop with velocity vector $\underline{v}=30\underline{j}$ and exits with velocity $\underline{v}'=30\underline{i}$. What is the change in velocity vector?", [P("", [
    S(r"\Delta\underline{v} = \underline{v}' - \underline{v} = 30\underline{i} - 30\underline{j}", "Change = final $-$ initial.", "تبدیلی = آخری $-$ ابتدائی۔"),
    S(r"|\Delta\underline{v}| = \sqrt{30^2 + (-30)^2} = 30\sqrt{2}", "Its magnitude.", "اس کی مقدار۔", "sqrt(30**2 + (-30)**2) == 30*sqrt(2)")],
    r"$30\underline{i} - 30\underline{j}$, magnitude $30\sqrt{2}$")], "6.3")
ex("ex6.3", 11, r"An aeroplane has airspeed $\underline{v}_p=20\underline{i}$ and there is a crosswind $\underline{v}_w=50\underline{j}$. Find the resultant velocity and its magnitude.", [P("", [
    S(r"\underline{v}_r = \underline{v}_p + \underline{v}_w = 20\underline{i} + 50\underline{j}", "Add the two velocities.", "دونوں رفتاریں جمع کریں۔"),
    S(r"|\underline{v}_r| = \sqrt{20^2 + 50^2} = \sqrt{2900} \approx 53.85", "Its magnitude.", "اس کی مقدار۔", "20**2 + 50**2 == 2900", "Abs(sqrt(2900) - 53.85) < 0.01")],
    r"$20\underline{i} + 50\underline{j}$, magnitude $\approx 53.85$")], "6.3")

# ------------------------------------------------------------------------------------------ Review Exercise 6

q1 = [mcq("i", "$x$-axis and $y$-axis divide a coordinate plane into ______ parts.", [r"\text{one}", r"\text{two}", r"\text{three}", r"\text{four}"], 3,
          [T("The two axes make four quadrants.", "دونوں محور چار ربع بناتے ہیں۔")]),
      mcq("ii", "$P(4,-4)$ lies in ______ quadrant.", [r"\text{first}", r"\text{second}", r"\text{third}", r"\text{fourth}"], 3,
          [S(r"x > 0,\ y < 0 \Rightarrow \text{fourth}", "$(+, -)$ is the fourth quadrant.", "$(+, -)$ چوتھا ربع ہے۔", "4 > 0", "-4 < 0")]),
      mcq("iii", "A vector having magnitude 1, is called:", [r"\text{equal vector}", r"\text{parallel vector}", r"\text{unit vector}", r"\text{zero vector}"], 2,
          [T("A unit vector has length 1.", "اکائی سمتیے کی لمبائی 1 ہوتی ہے۔")]),
      mcq("iv", r"What is the value of $|3\underline{i}+4\underline{j}|$?", ["3", "4", "5", "7"], 2,
          [S(r"\sqrt{3^2 + 4^2} = 5", "Magnitude.", "مقدار۔", "sqrt(3**2 + 4**2) == 5")]),
      mcq("v", r"If $\underline{a}=\lambda\underline{b}$, then $\underline{a}$ and $\underline{b}$ are:", [r"\text{equal}", r"\text{parallel}", r"\text{perpendicular}", r"\text{non-parallel}"], 1,
          [T("A number times a vector is parallel to it.", "سمتیے کا عددی مضرب اس کے متوازی ہوتا ہے۔")]),
      mcq("vi", r"If $\overrightarrow{OA}=\underline{a}$, $\overrightarrow{OB}=\underline{b}$, then $\overrightarrow{AB}$ is:", [r"\underline{b}-\underline{a}", r"\underline{a}-\underline{b}",
                                                                                                                         r"\underline{a}+\underline{b}", r"\underline{b}+\underline{a}"], 0,
          [T("$\\overrightarrow{AB} = \\overrightarrow{OB} - \\overrightarrow{OA}$ (tip minus tail).", "$\\overrightarrow{AB} = \\overrightarrow{OB} - \\overrightarrow{OA}$۔")]),
      mcq("vii", "Translation vector shows:", [r"\text{deformation}", r"\text{rotation}", r"\text{movement}", r"\text{enlargement}"], 2,
          [T("A translation moves every point by the same vector.", "انتقال ہر نقطے کو ایک ہی سمتیے سے منتقل کرتا ہے۔")]),
      mcq("viii", "Sum of two vectors is:", [r"\text{a triangle}", r"\text{a vector}", r"\text{a scalar}", r"\text{a length}"], 1,
          [T("Adding vectors gives a vector.", "سمتیوں کا مجموعہ سمتیہ ہوتا ہے۔")]),
      mcq("ix", "The position vector of point $P(3,-2)$ with respect to $O$ is:", [r"3\underline{i}+2\underline{j}", r"3\underline{i}-2\underline{j}",
                                                                               r"-3\underline{i}+2\underline{j}", r"2\underline{i}-3\underline{j}"], 1,
          [T("Position vector $= x\\underline{i} + y\\underline{j}$.", "مقامی سمتیہ $= x\\underline{i} + y\\underline{j}$۔")]),
      mcq("x", "Vector from point $P(3,4)$ to origin is:", [r"3\underline{i}+4\underline{j}", r"-3\underline{i}+4\underline{j}", r"-3\underline{i}-4\underline{j}",
                                                           r"3\underline{i}-4\underline{j}"], 2,
          [S(r"\overrightarrow{PO} = (0 - 3)\underline{i} + (0 - 4)\underline{j}", "Tip minus tail.", "سرا منفی دم۔", "0 - 3 == -3", "0 - 4 == -4")])]
ex("rev6", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 6")


def mag_ab(label, A, B):
    s, v = ab_vector(A, B)
    ms, m = mag_steps(v, r"\overrightarrow{AB}")
    return P(label, [s] + ms, f"${num(m)}$", prompt=f"$A({A[0]},{A[1]}),\\ B({B[0]},{B[1]})$")


ex("rev6", 2, r"Find magnitude of the $\overrightarrow{AB}$: (i) $A(7,7), B(-12,0)$ (ii) $A(9,3), B(2,11)$", [mag_ab("i", (7, 7), (-12, 0)), mag_ab("ii", (9, 3), (2, 11))], "Review 6")
ua = (R(5, 3), R(1, 3))
ex("rev6", 3, r"Find a unit vector in the direction of $\underline{a}=\frac{5}{3}\underline{i}+\frac{1}{3}\underline{j}$.", [P("", unit_steps(ua)[0], f"${vt(unit_steps(ua)[1])}$")],
   "Review 6")
a4, b4, c4 = (2, -1), (3, 1), (4, 1)
R4 = [("i", [5, -1, 1], [b4, a4, c4], "bac", r"5\underline{b}-\underline{a}+\underline{c}"), ("ii", [8, 1, 5], [a4, b4, c4], "abc", r"8\underline{a}+\underline{b}+5\underline{c}"),
      ("iii", [1, 1, -4], [c4, b4, a4], "cba", r"\underline{c}+\underline{b}-4\underline{a}")]
ex("rev6", 4, rf"If $\underline{{a}}={vt(a4)}$, $\underline{{b}}={vt(b4)}$ and $\underline{{c}}={vt(c4)}$, then find the following vectors: "
   r"(i) $5\underline{b}-\underline{a}+\underline{c}$ (ii) $8\underline{a}+\underline{b}+5\underline{c}$ (iii) $\underline{c}+\underline{b}-4\underline{a}$",
   [P(l, combo(cf, vs, ns)[0], f"${vt(combo(cf, vs, ns)[1])}$", prompt=f"${t}$") for l, cf, vs, ns, t in R4], "Review 6")
ex("rev6", 5, r"Find the values of $x$ and $y$ in the following equation. $(2x\underline{i}+y\underline{j})+(-\underline{i}+5\underline{j})=\frac{1}{4}\underline{i}-8\underline{j}$",
   [compare("", r"(2x\underline{i} + y\underline{j}) + (-\underline{i} + 5\underline{j})", ["2*x-1", "y+5"], (R(1, 4), -8), "xy", "")], "Review 6")
translate("rev6", 6, r"Plot $A(-5,3)$, $B(-2,3)$ and $C(-4,5)$ to form a triangle $ABC$. Also, translate $\triangle ABC$ to $\triangle A'B'C'$ by translation vector "
          r"$5\underline{i}-2\underline{j}$.", "ABC", [(-5, 3), (-2, 3), (-4, 5)], (5, -2), "Review 6")
parallelogram("rev6", 7, "Use vectors to show that $ABCD$ is a parallelogram, where the points are $A(2,3)$, $B(6,3)$, $C(7,6)$ and $D(3,6)$.",
              "ABCD", [(2, 3), (6, 3), (7, 6), (3, 6)], "Review 6")
isosceles("rev6", 8, "Use vectors to show that triangle $ABC$ is an isosceles triangle, where the points $A$, $B$ and $C$ have coordinates $(1,2)$, $(4,6)$ and $(7,2)$ respectively.",
          "ABC", [(1, 2), (4, 6), (7, 2)], "Review 6")
ex("rev6", 9, r"A ball is projected with velocity vector $\underline{v}=6\underline{i}+8\underline{j}$. What is the magnitude of velocity?",
   [P("", mag_steps((6, 8), r"\underline{v}")[0], "$10$")], "Review 6")
ex("rev6", 10, "An aircraft is flying due east with an airspeed of 200 km/h. There is a wind blowing due north at 60 km/h. Find the resultant velocity and its magnitude.", [P("", [
    S(r"\underline{v} = 200\underline{i} + 60\underline{j}", "East is $\\underline{i}$, north is $\\underline{j}$; add the velocities.", "مشرق $\\underline{i}$ اور شمال $\\underline{j}$ ہے؛ رفتاریں جمع کریں۔"),
    S(r"|\underline{v}| = \sqrt{200^2 + 60^2} = \sqrt{43600} \approx 208.8 \text{ km/h}", "Its magnitude.", "اس کی مقدار۔", "200**2 + 60**2 == 43600",
      "Abs(sqrt(43600) - 208.8) < 0.01")], r"$200\underline{i} + 60\underline{j}$, magnitude $\approx 208.8$ km/h")], "Review 6")
