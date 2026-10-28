"""Class 10, Unit 3 - Matrices and Determinants: Exercises 3.1-3.6 and Review Exercise 3.

Questions transcribed from the reference notes (data/class10/pages/u03_*.png). Every matrix result is computed and checked with
sympy (Eq(Matrix, Matrix)); final answers are checked against data/answers10/unit03.json (transcribed from the notes).
Notes errors found and recorded with key_note: Ex 3.6 Q8 (the cyclists' determinants).
"""
import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T
from _mat import (M, R, add, adj, ans, chain, cramer, det, inv, inverse_solve, meq, mpy, mtex, mul, scal, strtex, sys_answer, tr,
                  verify, _e)

UNIT = {"unit": 3, "title": "Matrices and Determinants", "title_ur": "قالب اور مقطع", "class": 10, "items": []}
ex = maker(UNIT["items"])


def named(ms):
    return ", ".join(f"${n} = {mtex(m)}$" for n, m in ms)


def kinds(m):
    """Every name the unit gives this matrix."""
    out = []
    if all(v == 0 for v in m):
        out.append("null")
    if m.rows == 1:
        out.append("row")
    if m.cols == 1:
        out.append("column")
    if m.rows == m.cols:
        diag = all(m[i, j] == 0 for i in range(m.rows) for j in range(m.cols) if i != j)
        if m == sp.eye(m.rows):
            out.append("unit")
        elif diag and len(set(m[i, i] for i in range(m.rows))) == 1 and m[0, 0] != 0:
            out.append("scalar")
        elif diag and any(m[i, i] != 0 for i in range(m.rows)):
            out.append("diagonal")
        out.append("square")
    else:
        out.append("rectangular")
    return out


TYPE_UR = {"null": "صفری", "row": "قطاری", "column": "کالمی", "unit": "اکائی", "scalar": "سکیلر", "diagonal": "وتری", "square": "مربعی",
           "rectangular": "مستطیلی"}
WHY = {"null": "every entry is 0", "row": "it has only one row", "column": "it has only one column", "unit": "it is square with 1s on the diagonal and 0s elsewhere",
       "scalar": "it is diagonal with all diagonal entries equal", "diagonal": "all entries off the diagonal are 0",
       "square": "rows = columns", "rectangular": "rows and columns are not equal"}


def classify(label, ms, allowed, prompt=""):
    """One step per matrix: the first of `allowed` that fits."""
    steps, ans_ = [], []
    for n, m in ms:
        k = next(t for t in allowed if t in kinds(m))
        steps.append(S(rf"{n} = {mtex(m)}:\ \text{{{k} matrix}}", f"${n}$ is a {k} matrix because {WHY[k]}.",
                       f"${n}$ ایک {TYPE_UR[k]} قالب ہے ({m.rows}-by-{m.cols})۔", f"{mpy(m)}.rows == {m.rows}", f"{mpy(m)}.cols == {m.cols}"))
        ans_.append(f"{n}: {k}")
    return P(label, steps, ", ".join(ans_), prompt=prompt)


# ------------------------------------------------------------------------------------------ Exercise 3.1

A1, B1, C1, D1, E1 = M([[0, 0], [0, 0]]), M([[3], [4], [7]]), M([[8, -10, 11]]), M([[3, 2, 1], [1, 0, 3], [4, 5, 6]]), M([[5, 9, -2], [-3, 4, 5]])
L1 = [("A", A1), ("B", B1), ("C", C1), ("D", D1), ("E", E1)]
ex("ex3.1", 1, "Write the number of rows and number of columns in each matrix. " + named(L1), [P("", [
    S(rf"{n} = {mtex(m)}:\ \text{{rows}} = {m.rows},\ \text{{columns}} = {m.cols}", "Count the horizontal lines (rows) and the vertical lines (columns).",
      "افقی لکیریں (قطاریں) اور عمودی لکیریں (کالم) گنیں۔", f"{mpy(m)}.rows == {m.rows}", f"{mpy(m)}.cols == {m.cols}") for n, m in L1],
    "; ".join(f"{n}: {m.rows} rows, {m.cols} columns" for n, m in L1))], "3.1")

L2 = [("A", M([[1], [0]])), ("B", M([[3, 4]])), ("C", M([[3, 5], [5, 6]])), ("D", M([[0, 3, 4], [5, 0, 9]])), ("E", M([[0, 1], [3, 4], [5, 6]])), ("F", M([[5]]))]
ex("ex3.1", 2, "Write the order of each matrix. " + named(L2), [P("", [
    S(rf"{n} = {mtex(m)}:\ \text{{order }} {m.rows}\text{{-by-}}{m.cols}", "Order = (number of rows)-by-(number of columns).",
      "درجہ = (قطاروں کی تعداد)-by-(کالموں کی تعداد)۔", f"{mpy(m)}.rows == {m.rows}", f"{mpy(m)}.cols == {m.cols}") for n, m in L2],
    ", ".join(f"{n}: {m.rows}-by-{m.cols}" for n, m in L2))], "3.1")

L3 = [("A", M([[0, 3], [4, 1]])), ("B", M([[9], [-7]])), ("C", M([[2 * 3, 2 - 1], [2 * 2, 4 - 2], [4 + 4, 3 + 0]])),
      ("D", M([[5 + 4], [-8 + 1]])), ("E", M([[6, 1], [4, 2], [8, 3]])), ("F", M([[3 - 3, 3], [3 + 1, 1]]))]
ex("ex3.1", 3, r"Which of the following matrices are equal? $A=\begin{bmatrix}0&3\\4&1\end{bmatrix}$, $B=\begin{bmatrix}9\\-7\end{bmatrix}$, "
   r"$C=\begin{bmatrix}2\times3&2-1\\2\times2&4-2\\4+4&3+0\end{bmatrix}$, $D=\begin{bmatrix}5+4\\-8+1\end{bmatrix}$, $E=\begin{bmatrix}6&1\\4&2\\8&3\end{bmatrix}$, "
   r"$F=\begin{bmatrix}3-3&3\\3+1&1\end{bmatrix}$", [P("", [
       S(r"C = \begin{bmatrix} 2\times3 & 2-1 \\ 2\times2 & 4-2 \\ 4+4 & 3+0 \end{bmatrix} = " + mtex(L3[2][1]) + r",\quad D = " + mtex(L3[3][1])
         + r",\quad F = " + mtex(L3[5][1]), "Simplify the entries first.", "پہلے ارکان کو سادہ کریں۔",
         meq(L3[2][1], M([[6, 1], [4, 2], [8, 3]])), meq(L3[3][1], M([[9], [-7]])), meq(L3[5][1], M([[0, 3], [4, 1]]))),
       S(r"A = F,\quad B = D,\quad C = E", "Equal matrices have the same order and equal entries in the same positions.",
         "مساوی قالبوں کا درجہ ایک ہوتا ہے اور ایک ہی مقام کے ارکان برابر ہوتے ہیں۔",
         meq(L3[0][1], L3[5][1]), meq(L3[1][1], L3[3][1]), meq(L3[2][1], L3[4][1]))], "A = F, B = D, C = E")], "3.1")


def entries_equal(label, lhs_rows, rhs, unknowns, prompt, eqs_tex, sol):
    """Equal matrices: equate entries and solve. lhs_rows uses sympy strings; sol maps names to values."""
    loc = {u: sp.Symbol(u) for u in unknowns}
    L = sp.Matrix([[sp.sympify(v, locals=loc) for v in row] for row in lhs_rows])
    sub = {loc[k]: v for k, v in sol.items()}
    steps = [S(eqs_tex[0], "Equal matrices have equal entries in the same positions.", "مساوی قالبوں کے ایک ہی مقام کے ارکان برابر ہوتے ہیں۔")]
    for t in eqs_tex[1:]:
        steps.append(S(t, "Solve each equation.", "ہر مساوات حل کریں۔"))
    steps.append(S(r",\quad ".join(f"{k} = {_e(v)}" for k, v in sol.items()), "Put the values back: the two matrices are equal.",
                   "قیمتیں واپس رکھیں: دونوں قالب برابر ہیں۔", f"Eq({mpy(L.subs(sub))}, {mpy(rhs)})"))
    return P(label, steps, "$" + r",\ ".join(f"{k} = {_e(v)}" for k, v in sol.items()) + "$", prompt=prompt)


ex("ex3.1", 4, r"If $\begin{bmatrix}a+2&c-3\\b-1&d+4\end{bmatrix}=\begin{bmatrix}5&8\\6&4\end{bmatrix}$, then find the values of $a$, $b$, $c$ and $d$.", [
    entries_equal("", [["a+2", "c-3"], ["b-1", "d+4"]], M([[5, 8], [6, 4]]), "abcd", "",
                  [r"a + 2 = 5,\quad b - 1 = 6,\quad c - 3 = 8,\quad d + 4 = 4", r"a = 5 - 2,\quad b = 6 + 1,\quad c = 8 + 3,\quad d = 4 - 4"],
                  {"a": 3, "b": 7, "c": 11, "d": 0})], "3.1")
ex("ex3.1", 5, r"If $\begin{bmatrix}2x+1&4\\7&5\end{bmatrix}=\begin{bmatrix}9&4\\7&y\end{bmatrix}$, then find the values of $x$ and $y$.", [
    entries_equal("", [["2*x+1", "4"], ["7", "5"]], M([[9, 4], [7, 5]]), "xy", "",
                  [r"2x + 1 = 9,\quad y = 5", r"2x = 9 - 1 = 8 \Rightarrow x = 4"], {"x": 4, "y": 5})], "3.1")
ex("ex3.1", 6, r"If $\begin{bmatrix}a+b&2d-1\\3b+2&4\end{bmatrix}=\begin{bmatrix}10&5\\11&c\end{bmatrix}$, then find the values of $a$, $b$, $c$ and $d$.", [
    entries_equal("", [["a+b", "2*d-1"], ["3*b+2", "4"]], M([[10, 5], [11, 4]]), "abcd", "",
                  [r"a + b = 10,\quad 2d - 1 = 5,\quad 3b + 2 = 11,\quad c = 4", r"3b = 9 \Rightarrow b = 3,\quad a = 10 - 3 = 7,\quad 2d = 6 \Rightarrow d = 3"],
                  {"a": 7, "b": 3, "c": 4, "d": 3})], "3.1")
ex("ex3.1", 7, r"If $\begin{bmatrix}p+q&5\\11&p-2q\end{bmatrix}=\begin{bmatrix}6&5\\11&0\end{bmatrix}$, then find the values of $p$ and $q$.", [
    entries_equal("", [["p+q", "5"], ["11", "p-2*q"]], M([[6, 5], [11, 0]]), "pq", "",
                  [r"p + q = 6 \quad (i),\qquad p - 2q = 0 \quad (ii)", r"2(i) + (ii):\ 2p + 2q + p - 2q = 12 \Rightarrow 3p = 12 \Rightarrow p = 4",
                   r"4 + q = 6 \Rightarrow q = 2"], {"p": 4, "q": 2})], "3.1")

# ------------------------------------------------------------------------------------------ Exercise 3.2

T1 = [("A", M([[5, 7, 8]])), ("B", M([[0]])), ("C", M([[1, 0], [0, 1]])), ("D", M([[0, 0], [0, 0]])), ("E", M([[6], [0], [8]])), ("F", M([[7], [1], [9]]))]
ex("ex3.2", 1, "From the following matrices identify unit matrices, row matrices, column matrices and null matrices. " + named(T1),
   [classify("", T1, ["null", "unit", "row", "column"])], "3.2")
T2 = [("A", M([[5], [3], [4]])), ("B", M([[1, 6], [4, 1]])), ("C", M([[3, 5, 8], [0, 4, -2]])), ("D", M([[5, -5], [2, 7]])),
      ("E", M([[3, 2], [4, 1], [5, 0]])), ("F", M([[5, -3, 7]])), ("G", M([[3, 0, 1], [1, 3, 4], [5, 2, -3]])), ("H", M([[3, 5], [4, 4], [5, 2]]))]
ex("ex3.2", 2, "Identify type of the given matrices as row, column, square and rectangular matrices. " + named(T2),
   [classify("", T2, ["row", "column", "square", "rectangular"])], "3.2")
T3 = [("A", M([[1, 0], [0, 1]])), ("B", M([[5, 0], [0, 5]])), ("C", M([[3, 0], [0, 0]])), ("D", M([[7, 0], [0, 6]])), ("E", M([[2, 0], [0, 2]]))]
ex("ex3.2", 3, "Identify diagonal, scalar and unit matrices. " + named(T3), [classify("", T3, ["unit", "scalar", "diagonal"])], "3.2")

T4 = [("A", M([[2, 3], [4, 5]])), ("B", M([[3], [7], [6]])), ("C", M([[5, -2, 4]])), ("D", M([[2, 5], [3, 6], [4, 7]]))]
ex("ex3.2", 4, "Find transpose of each of the following matrices: " + named(T4), [P("", sum((tr(m, n)[0] for n, m in T4), []),
   "; ".join(f"${n}^t = {mtex(m.T)}$" for n, m in T4))], "3.2")
T5 = [("A", M([[-3, 0], [5, 6]])), ("B", M([[-3, 3], [-2, 2]])), ("C", M([[-9, 1], [1, -7]]))]
ex("ex3.2", 5, "Find negative of the following matrices: " + named(T5), [P("", [
    S(rf"-{n} = -{mtex(m)} = {mtex(-m)}", "Change the sign of every entry.", "ہر رکن کی علامت بدلیں۔", meq(m + (-m), sp.zeros(*m.shape))) for n, m in T5],
    "; ".join(f"$-{n} = {mtex(-m)}$" for n, m in T5))], "3.2")
A6, B6 = M([[2, 3], [4, 5]]), M([[7, 6], [5, 8]])
ex("ex3.2", 6, rf"If $A = {mtex(A6)}$ and $B = {mtex(B6)}$, then verify that (i) $(A^t)^t = A$ (ii) $(B^t)^t = B$", [
    verify("i", "$(A^t)^t = A$", "(A^t)^t", chain(lambda _: tr(A6, "A"), lambda v: tr(v, "(A^t)")), "A", ([], A6)),
    verify("ii", "$(B^t)^t = B$", "(B^t)^t", chain(lambda _: tr(B6, "B"), lambda v: tr(v, "(B^t)")), "B", ([], B6))], "3.2")
L7 = M([[2, 3, 4], [3, -2, 5], [4, 5, 0]])
ex("ex3.2", 7, rf"Show that $L = {mtex(L7)}$ is a symmetric matrix.", [P("", tr(L7, "L")[0] + [
    S(r"L^t = L", "A matrix equal to its own transpose is symmetric.", "جو قالب اپنے پلٹ کے برابر ہو وہ متشاکل ہے۔", meq(L7.T, L7))],
    "$L^t = L$, so $L$ is symmetric")], "3.2")

# ------------------------------------------------------------------------------------------ Exercise 3.3

C1L = [("A", M([[3, 4], [-2, 1]])), ("B", M([[3], [4]])), ("C", M([[5, 2]])), ("D", M([[1, 7], [2, 5]])), ("E", M([[2]])), ("F", M([[7, 11]])),
       ("G", sp.Matrix([[sp.Symbol("a")], [sp.Symbol("b")]])), ("H", M([[3]])), ("M", sp.Matrix([[sp.Symbol("l")], [sp.Symbol("m")]]))]
groups = {}
for n, m in C1L:
    groups.setdefault(m.shape, []).append(n)
ex("ex3.3", 1, "Which of the following matrices are conformable for addition and subtraction? " + named(C1L), [P("", [
    S(r",\quad ".join(f"{n}: {m.rows}\\text{{-by-}}{m.cols}" for n, m in C1L), "Write the order of each matrix.", "ہر قالب کا درجہ لکھیں۔",
      *[c for n, m in C1L for c in (f"{mpy(m)}.rows == {m.rows}", f"{mpy(m)}.cols == {m.cols}")]),
    S(r"\text{Same order: } " + r";\ ".join(", ".join(v) for v in groups.values() if len(v) > 1),
      "Only matrices of the same order can be added or subtracted.", "صرف ایک ہی درجہ کے قالب جمع یا تفریق ہو سکتے ہیں۔")],
    "; ".join(" and ".join(v) for v in groups.values() if len(v) > 1))], "3.3")

X, Y, Z = M([[1, -1], [-2, 2]]), M([[1, 2], [3, 4]]), M([[3, 0], [0, -2]])
q2 = [P("i", add(X, Y, "X", "Y")[0], ans(X + Y), prompt="$X+Y$"),
      P("ii", chain(lambda _: scal(7, Z, "Z"), lambda v: add(Y, v, "Y", "7Z"))[0], ans(Y + 7 * Z), prompt="$Y+7Z$"),
      P("iii", chain(lambda _: scal(4, X, "X"), lambda v: add(v, Z, "4X", "Z", -1))[0], ans(4 * X - Z), prompt="$4X-Z$"),
      P("iv", chain(lambda _: scal(2, Y, "Y"), lambda _: scal(3, Z, "Z"), lambda _: add(X, 2 * Y, "X", "2Y"),
                    lambda v: add(v, 3 * Z, "X + 2Y", "3Z"))[0], ans(X + 2 * Y + 3 * Z), prompt="$X+2Y+3Z$"),
      P("v", chain(lambda _: scal(4, Y, "Y"), lambda _: add(X, 4 * Y, "X", "4Y", -1), lambda v: add(v, Z, "X - 4Y", "Z"))[0],
        ans(X - 4 * Y + Z), prompt="$X-4Y+Z$"),
      P("vi", add(Z, Z, "Z", "Z", -1)[0], ans(Z - Z), prompt="$Z-Z$")]
ex("ex3.3", 2, rf"If $X={mtex(X)}$, $Y={mtex(Y)}$ and $Z={mtex(Z)}$, then find the following: (i) $X+Y$ (ii) $Y+7Z$ (iii) $4X-Z$ (iv) $X+2Y+3Z$ "
   r"(v) $X-4Y+Z$ (vi) $Z-Z$", q2, "3.3")

I3 = [("i", "P", M([[5], [-7]])), ("ii", "Q", M([[9, -3]])), ("iii", "R", M([[2, -1], [-2, 3]])), ("iv", "S", M([[1, 0], [0, 1]]))]
ex("ex3.3", 3, "Find the additive inverse of the following matrices: " + " ".join(f"({l}) ${n}={mtex(m)}$" for l, n, m in I3), [
    P(l, [S(rf"-{n} = -{mtex(m)} = {mtex(-m)}", "The additive inverse changes the sign of every entry.", "جمعی معکوس میں ہر رکن کی علامت بدل جاتی ہے۔",
            meq(m + (-m), sp.zeros(*m.shape)))], ans(-m), prompt=f"${n}={mtex(m)}$") for l, n, m in I3], "3.3")

A4, B4, C4 = M([[2, 3], [-3, 2]]), M([[3, 4], [5, 6]]), M([[1, -2], [0, 5]])
ex("ex3.3", 4, rf"If $A={mtex(A4)}$, $B={mtex(B4)}$ and $C={mtex(C4)}$, then verify the following: (i) $A+B=B+A$ (ii) $(A+B)+C=A+(B+C)$ "
   r"(iii) $(2A+B)+C=2A+(B+C)$ (iv) $3(A+B)=3A+3B$", [
       verify("i", "$A+B=B+A$", "A+B", add(A4, B4), "B+A", add(B4, A4, "B", "A")),
       verify("ii", "$(A+B)+C=A+(B+C)$", "(A+B)+C", chain(lambda _: add(A4, B4), lambda v: add(v, C4, "(A+B)", "C")),
              "A+(B+C)", chain(lambda _: add(B4, C4, "B", "C"), lambda v: add(A4, v, "A", "(B+C)"))),
       verify("iii", "$(2A+B)+C=2A+(B+C)$", "(2A+B)+C", chain(lambda _: scal(2, A4), lambda v: add(v, B4, "2A", "B"), lambda v: add(v, C4, "(2A+B)", "C")),
              "2A+(B+C)", chain(lambda _: add(B4, C4, "B", "C"), lambda v: add(2 * A4, v, "2A", "(B+C)"))),
       verify("iv", "$3(A+B)=3A+3B$", "3(A+B)", chain(lambda _: add(A4, B4), lambda v: scal(3, v, "(A+B)")),
              "3A+3B", chain(lambda _: scal(3, A4), lambda _: scal(3, B4, "B"), lambda _: add(3 * A4, 3 * B4, "3A", "3B")))], "3.3")

A5, B5 = M([[5, 6], [7, -2]]), M([[-5, -6], [-7, 2]])
ex("ex3.3", 5, rf"If $A={mtex(A5)}$ and $B={mtex(B5)}$, then show that $B$ is additive inverse of $A$ and $A$ is additive inverse of $B$.", [P("",
    add(A5, B5)[0] + add(B5, A5, "B", "A")[0] + [S(r"A + B = B + A = O \Rightarrow B = -A,\ A = -B", "Their sum is the null matrix, so each is the additive inverse of the other.",
                                                  "ان کا مجموعہ صفری قالب ہے، اس لیے ہر ایک دوسرے کا جمعی معکوس ہے۔", meq(B5, -A5))],
    "$A + B = B + A = O$, so $B = -A$ and $A = -B$")], "3.3")

A6, B6 = M([[6, -2], [0, 3]]), M([[8, -1], [3, 0]])
ex("ex3.3", 6, rf"If $A={mtex(A6)}$ and $B={mtex(B6)}$, then verify that (i) $(A+B)^t=A^t+B^t$ (ii) $(A-B)^t=A^t-B^t$", [
    verify("i", "$(A+B)^t=A^t+B^t$", "(A+B)^t", chain(lambda _: add(A6, B6), lambda v: tr(v, "(A+B)")),
           "A^t+B^t", chain(lambda _: tr(A6), lambda _: tr(B6, "B"), lambda _: add(A6.T, B6.T, "A^t", "B^t"))),
    verify("ii", "$(A-B)^t=A^t-B^t$", "(A-B)^t", chain(lambda _: add(A6, B6, sign=-1), lambda v: tr(v, "(A-B)")),
           "A^t-B^t", chain(lambda _: tr(A6), lambda _: tr(B6, "B"), lambda _: add(A6.T, B6.T, "A^t", "B^t", -1)))], "3.3")

# ------------------------------------------------------------------------------------------ Exercise 3.4

PAIRS = [("i", M([[1, 2], [-1, 0]]), M([[3, 2], [1, -1]])), ("ii", M([[1, -2]]), M([[3], [-4]])), ("iii", M([[4], [4]]), M([[2, 5]])),
         ("iv", M([[1, 2], [-1, 1], [3, 0]]), M([[-1, 4, 1], [2, 3, 1]])), ("v", M([[1, 2, 2], [3, 1, 1]]), M([[1, 5], [2, 4], [1, 6]]))]


def ab_ba(label, A, B):
    s1, ab = mul(A, B)
    s2, ba = mul(B, A, "B", "A")
    parts = [f"$AB = {mtex(ab)}$" if ab is not None else "$AB$ not possible", f"$BA = {mtex(ba)}$" if ba is not None else "$BA$ not possible"]
    return P(label, s1 + s2, ", ".join(parts), prompt=f"$A={mtex(A)},\\ B={mtex(B)}$")


ex("ex3.4", 1, "Find $AB$ and $BA$, if possible. " + " ".join(f"({l}) $A={mtex(a)}$, $B={mtex(b)}$" for l, a, b in PAIRS),
   [ab_ba(l, a, b) for l, a, b in PAIRS], "3.4")

A2, B2, C2 = M([[5, 1], [-1, 4]]), M([[2, -1], [0, 3]]), M([[5, 1], [1, 4]])
s_ab, ab2 = mul(A2, B2)
s_ba, ba2 = mul(B2, A2, "B", "A")
q2 = [P("i", s_ab + s_ba + [S(rf"AB = {mtex(ab2)} \ne {mtex(ba2)} = BA", "The two products are different, so $AB \\ne BA$.",
                              "دونوں حاصل ضرب مختلف ہیں، اس لیے $AB \\ne BA$۔", f"Ne({mpy(ab2)}, {mpy(ba2)})")],
        f"verified: $AB = {mtex(ab2)} \\ne BA = {mtex(ba2)}$", prompt=r"$AB \ne BA$"),
      verify("ii", "$A(B-C)=AB-AC$", "A(B-C)", chain(lambda _: add(B2, C2, "B", "C", -1), lambda v: mul(A2, v, "A", "(B-C)")),
             "AB-AC", chain(lambda _: mul(A2, B2), lambda _: mul(A2, C2, "A", "C"), lambda _: add(A2 * B2, A2 * C2, "AB", "AC", -1))),
      verify("iii", "$A(BC)=(AB)C$", "A(BC)", chain(lambda _: mul(B2, C2, "B", "C"), lambda v: mul(A2, v, "A", "(BC)")),
             "(AB)C", chain(lambda _: mul(A2, B2), lambda v: mul(v, C2, "(AB)", "C"))),
      verify("iv", "$(BC)^t=C^tB^t$", "(BC)^t", chain(lambda _: mul(B2, C2, "B", "C"), lambda v: tr(v, "(BC)")),
             "C^tB^t", chain(lambda _: tr(C2, "C"), lambda _: tr(B2, "B"), lambda _: mul(C2.T, B2.T, "C^t", "B^t"))),
      verify("v", "$(B+C)A=BA+CA$", "(B+C)A", chain(lambda _: add(B2, C2, "B", "C"), lambda v: mul(v, A2, "(B+C)", "A")),
             "BA+CA", chain(lambda _: mul(B2, A2, "B", "A"), lambda _: mul(C2, A2, "C", "A"), lambda _: add(B2 * A2, C2 * A2, "BA", "CA")))]
ex("ex3.4", 2, rf"Verify each statement, using $A={mtex(A2)}$, $B={mtex(B2)}$ and $C={mtex(C2)}$: (i) $AB\ne BA$ (ii) $A(B-C)=AB-AC$ "
   r"(iii) $A(BC)=(AB)C$ (iv) $(BC)^t=C^tB^t$ (v) $(B+C)A=BA+CA$", q2, "3.4")

ex("ex3.4", 3, r"If $\begin{bmatrix}4&a\\b&3\end{bmatrix}\begin{bmatrix}6\\6\end{bmatrix}=\begin{bmatrix}6\\3\end{bmatrix}$, then find the values of $a$ and $b$.", [P("", [
    S(r"\begin{bmatrix} (4)(6) + (a)(6) \\ (b)(6) + (3)(6) \end{bmatrix} = \begin{bmatrix} 24 + 6a \\ 6b + 18 \end{bmatrix} = \begin{bmatrix} 6 \\ 3 \end{bmatrix}",
      "Multiply the matrices (row by column).", "قالبوں کو ضرب دیں (قطار ضرب کالم)۔", "Eq(Matrix([[4, a], [b, 3]])*Matrix([[6], [6]]), Matrix([[24 + 6*a], [6*b + 18]]))"),
    S(r"24 + 6a = 6 \Rightarrow 6a = -18 \Rightarrow a = -3", "Equate the first entries.", "پہلے ارکان برابر کریں۔", "24 + 6*(-3) == 6"),
    S(r"6b + 18 = 3 \Rightarrow 6b = -15 \Rightarrow b = -\frac{5}{2}", "Equate the second entries.", "دوسرے ارکان برابر کریں۔",
      "Eq(Matrix([[4, -3], [R(-5,2), 3]])*Matrix([[6], [6]]), Matrix([[6], [3]]))")], r"$a = -3,\ b = -\frac{5}{2}$")], "3.4")

ex("ex3.4", 4, r"If $\begin{bmatrix}x&1\\y&2\end{bmatrix}\begin{bmatrix}1&0\\3&-1\end{bmatrix}=\begin{bmatrix}7&-1\\4&-2\end{bmatrix}$, then find the values of $x$ and $y$.", [P("", [
    S(r"\begin{bmatrix} x + 3 & 0 - 1 \\ y + 6 & 0 - 2 \end{bmatrix} = \begin{bmatrix} 7 & -1 \\ 4 & -2 \end{bmatrix}", "Multiply the matrices (row by column).",
      "قالبوں کو ضرب دیں (قطار ضرب کالم)۔", "Eq(Matrix([[x, 1], [y, 2]])*Matrix([[1, 0], [3, -1]]), Matrix([[x + 3, -1], [y + 6, -2]]))"),
    S(r"x + 3 = 7 \Rightarrow x = 4,\quad y + 6 = 4 \Rightarrow y = -2", "Equate the matching entries.", "متعلقہ ارکان برابر کریں۔",
      "Eq(Matrix([[4, 1], [-2, 2]])*Matrix([[1, 0], [3, -1]]), Matrix([[7, -1], [4, -2]]))")], "$x = 4,\\ y = -2$")], "3.4")

# ------------------------------------------------------------------------------------------ Exercise 3.5

D1 = [("i", M([[10, 5], [4, 6]])), ("ii", M([[-5, 8], [-3, -7]])), ("iii", M([[3, 8], [0, 2]]))]
ex("ex3.5", 1, "Find the values of each of the determinant. " + " ".join(f"({l}) ${mtex(m, True)}$" for l, m in D1), [
    P(l, det(m, "A")[0], f"${_e(m.det())}$", prompt=f"${mtex(m, True)}$") for l, m in D1], "3.5")

S2 = [("A", M([[5, 3], [3, 2]])), ("B", M([[7, 21], [2, 6]])), ("C", M([[13, 5], [7, 3]])), ("D", M([[2, 0], [0, 0]]))]
ex("ex3.5", 2, "Find whether the following matrices are singular or non-singular. " + named(S2), [P("", sum(
    ([*det(m, n)[0], S(rf"|{n}| {'= 0' if m.det() == 0 else r'\ne 0'} \Rightarrow \text{{{'singular' if m.det() == 0 else 'non-singular'}}}",
                       "A matrix is singular when its determinant is 0." if m.det() == 0 else "The determinant is not 0, so the matrix is non-singular.",
                       "جب مقطع 0 ہو تو قالب نادر (singular) ہوتا ہے۔" if m.det() == 0 else "مقطع 0 نہیں، اس لیے قالب غیر نادر ہے۔")] for n, m in S2), []),
    ", ".join(f"{n}: {'singular' if m.det() == 0 else 'non-singular'}" for n, m in S2))], "3.5")

ex("ex3.5", 3, r"Find the value of $x$ when $A=\begin{bmatrix}x&6\\5&15\end{bmatrix}$ is a singular matrix.", [P("", [
    S(r"|A| = (x)(15) - (6)(5) = 15x - 30", "Find the determinant.", "مقطع معلوم کریں۔", "Matrix([[x, 6], [5, 15]]).det() == 15*x - 30"),
    S(r"15x - 30 = 0 \Rightarrow x = 2", "A singular matrix has determinant 0.", "نادر قالب کا مقطع 0 ہوتا ہے۔", "Matrix([[2, 6], [5, 15]]).det() == 0")], "$x = 2$")], "3.5")

AD = [("A", sp.Matrix([[sp.Symbol("a"), sp.Symbol("b")], [sp.Symbol("c"), sp.Symbol("d")]])), ("B", M([[5, -2], [3, 7]])), ("C", M([[-3, 5], [-3, 2]]))]
ex("ex3.5", 4, "Find the adjoint of the following matrices: " + named(AD), [P("", sum((adj(m, n)[0] for n, m in AD), []),
   "; ".join(rf"$\operatorname{{Adj}}{n} = {mtex(m.adjugate())}$" for n, m in AD))], "3.5")

INV = [("i", M([[5, 0], [0, 5]])), ("ii", M([[-4, 8], [7, 2]])), ("iii", M([[40, 8], [5, 2]])), ("iv", M([[3, 5], [5, -3]])), ("v", M([[10, 8], [3, 3]])),
       ("vi", M([[-2, -3], [4, 5]]))]
ex("ex3.5", 5, "Find multiplicative inverse of the following matrices: " + " ".join(f"({l}) ${mtex(m)}$" for l, m in INV), [
    P(l, inv(m)[0], ans(m.inv()), prompt=f"${mtex(m)}$") for l, m in INV], "3.5")

A6 = M([[5, -3], [2, -1]])
ex("ex3.5", 6, rf"If $A={mtex(A6)}$, then find $A^{{-1}}$ and prove that $AA^{{-1}}=A^{{-1}}A=I$.", [P("", inv(A6)[0] + mul(A6, A6.inv(), "A", "A^{-1}")[0]
   + mul(A6.inv(), A6, "A^{-1}", "A")[0] + [S(r"AA^{-1} = A^{-1}A = I", "Both products are the identity matrix.", "دونوں حاصل ضرب اکائی قالب ہیں۔",
                                             meq(A6 * A6.inv(), sp.eye(2)), meq(A6.inv() * A6, sp.eye(2)))],
   f"$A^{{-1}} = {mtex(A6.inv())}$; $AA^{{-1}} = A^{{-1}}A = I$")], "3.5")

MI = [("i", M([[2, -1], [-3, 2]]), M([[2, 1], [3, 2]])), ("ii", M([[4, 15], [2, 8]]), M([[4, R(-15, 2)], [-1, 2]]))]
ex("ex3.5", 7, "Show that the following matrices are multiplicative inverse of each other. " + " ".join(f"({l}) ${mtex(a)}, {mtex(b)}$" for l, a, b in MI), [
    P(l, mul(a, b)[0] + [S(r"AB = I", "Two matrices are multiplicative inverses of each other when their product is the identity matrix.",
                           "دو قالب ایک دوسرے کے ضربی معکوس ہیں جب ان کا حاصل ضرب اکائی قالب ہو۔", meq(a * b, sp.eye(2)), meq(b * a, sp.eye(2)))],
      "$AB = I$, so they are inverses", prompt=f"${mtex(a)}, {mtex(b)}$") for l, a, b in MI], "3.5")

PI = [("i", M([[-3, -2], [5, 6]]), M([[2, -1], [-3, 2]])), ("ii", M([[1, 2], [8, 0]]), M([[0, -1], [5, 2]]))]
ex("ex3.5", 8, r"Prove that $(AB)^{-1}=B^{-1}A^{-1}$, if " + " ".join(f"({l}) $A={mtex(a)}$, $B={mtex(b)}$" for l, a, b in PI), [
    verify(l, f"$A={mtex(a)},\\ B={mtex(b)}$", "(AB)^{-1}", chain(lambda _, a=a, b=b: mul(a, b), lambda v: inv(v, "(AB)")),
           "B^{-1}A^{-1}", chain(lambda _, a=a: inv(a), lambda _, b=b: inv(b, "B"), lambda _, a=a, b=b: mul(b.inv(), a.inv(), "B^{-1}", "A^{-1}")))
    for l, a, b in PI], "3.5")

# ------------------------------------------------------------------------------------------ Exercise 3.6

SYS1 = [("i", M([[2, 5], [4, -3]]), M([19, -1]), r"2x+5y=19,\ 4x-3y=-1"), ("ii", M([[3, 2], [5, -1]]), M([7, 16]), r"3x+2y=7,\ 5x-y=16"),
        ("iii", M([[1, -2], [2, 7]]), M([9, -4]), r"x-2y=9,\ 2x+7y=-4"), ("iv", M([[3, 2], [1, -2]]), M([2, -2]), r"3x+2y=2,\ x-2y=-2")]
ex("ex3.6", 1, "Solve by matrix inversion method, if possible. " + " ".join(f"({l}) ${t}$" for l, _, _, t in SYS1), [
    P(l, inverse_solve(a, b)[0], sys_answer(list(a.inv() * b)), prompt=f"${t}$") for l, a, b, t in SYS1], "3.6")

SYS2 = [("i", M([[1, 4], [2, -1]]), M([4, 5]), r"x+4y=4,\ 2x-y=5"), ("ii", M([[1, 2], [3, -2]]), M([7, -3]), r"x+2y=7,\ 3x-2y=-3"),
        ("iii", M([[2, -5], [4, -3]]), M([-6, -12]), r"2x-5y=-6,\ 4x-3y=-12"), ("iv", M([[3, 2], [5, 6]]), M([-1, 5]), r"3x+2y=-1,\ 5x+6y=5")]
ex("ex3.6", 2, "Use Cramer's rule to solve the following pair of linear equations, if possible. " + " ".join(f"({l}) ${t}$" for l, _, _, t in SYS2), [
    P(l, cramer(a, b)[0], sys_answer(list(a.inv() * b)), prompt=f"${t}$") for l, a, b, t in SYS2], "3.6")


def word(eid, number, question, intro, A, B, names, answer_fmt, method="cramer", exercise="3.6", note=None):
    s, vals = (cramer if method == "cramer" else inverse_solve)(A, B, names)
    part = P("", [T(*intro)] + s, answer_fmt(vals))
    if note:
        part["key_note"] = note
    ex(eid, number, question, [part], exercise)


word("ex3.6", 3, r"An electrical engineer wants to determine the current in two branches A and B of a simple electrical circuit. The system of the equations is: "
     r"$x+y=7$, $2x-y=2$ where $x$ is the current in branch A and $y$ is the current in branch B. Find $x$ and $y$ by using matrices.",
     ("The two equations are given; solve them with Cramer's rule.", "دونوں مساوات دی گئی ہیں؛ کریمر کے اصول سے حل کریں۔"),
     M([[1, 1], [2, -1]]), M([7, 2]), ("x", "y"), lambda v: f"$x = {_e(v[0])},\\ y = {_e(v[1])}$")

ex("ex3.6", 4, r"Three forces act on a particle and must be in equilibrium i.e. $F_1+F_2+F_3=0$, where $F_1=\begin{bmatrix}8\\x\end{bmatrix}$, "
   r"$F_2=\begin{bmatrix}-2\\-7\end{bmatrix}$, $F_3=\begin{bmatrix}y\\-1\end{bmatrix}$. Find the value of $x$ and $y$.", [P("", [
       S(r"\begin{bmatrix} 8 \\ x \end{bmatrix} + \begin{bmatrix} -2 \\ -7 \end{bmatrix} + \begin{bmatrix} y \\ -1 \end{bmatrix} = \begin{bmatrix} 0 \\ 0 \end{bmatrix}",
         "Equilibrium: the forces add to the zero matrix.", "توازن: قوتوں کا مجموعہ صفری قالب ہے۔"),
       S(r"8 - 2 + y = 0,\quad x - 7 - 1 = 0", "Add the entries row by row.", "قطار بہ قطار ارکان جمع کریں۔"),
       S(r"y = -6,\quad x = 8", "Solve each equation.", "ہر مساوات حل کریں۔",
         "Eq(Matrix([[8], [8]]) + Matrix([[-2], [-7]]) + Matrix([[-6], [-1]]), Matrix([[0], [0]]))")], "$x = 8,\\ y = -6$")], "3.6")

word("ex3.6", 5, "Two support beams, A and B are holding up a combined load of 100 kN. Twice the load on beam A and three times the load on beam B equals 240 kN. "
     "Find the load of beam A and beam B by using matrices.",
     ("Let $a$ and $b$ be the loads (kN): $a + b = 100$, $2a + 3b = 240$.", "فرض کریں بوجھ $a$ اور $b$ ہیں (kN): $a + b = 100$، $2a + 3b = 240$۔"),
     M([[1, 1], [2, 3]]), M([100, 240]), ("a", "b"), lambda v: f"A = {_e(v[0])} kN, B = {_e(v[1])} kN")
word("ex3.6", 6, "In a 2D game world, two characters are moving along straight paths. One character moves along a line where the total of twice their horizontal "
     "position and vertical position is 5, while the other moves along a line where their horizontal position is one more than their vertical position. "
     "Find their point of intersection by using matrices.",
     ("$2x + y = 5$ and $x = y + 1$, i.e. $x - y = 1$.", "$2x + y = 5$ اور $x = y + 1$ یعنی $x - y = 1$۔"),
     M([[2, 1], [1, -1]]), M([5, 1]), ("x", "y"), lambda v: f"$({_e(v[0])}, {_e(v[1])})$")
word("ex3.6", 7, "Two years ago a man was 5 times as old as his son was. After 6 years he will be 3 times as old as his son. Find their present ages by using matrices.",
     ("Let the man be $x$ and the son $y$ years old now: $x - 2 = 5(y - 2) \\Rightarrow x - 5y = -8$ and $x + 6 = 3(y + 6) \\Rightarrow x - 3y = 12$.",
      "فرض کریں آدمی کی عمر $x$ اور بیٹے کی $y$ سال ہے: $x - 5y = -8$ اور $x - 3y = 12$۔"),
     M([[1, -5], [1, -3]]), M([-8, 12]), ("x", "y"), lambda v: f"man {_e(v[0])} years, son {_e(v[1])} years")
word("ex3.6", 8, r"Two cyclists are 44 km apart and start out at the same time. If they go towards one another they meet in 2 hours, but if they go in the same "
     r"direction the faster overtakes the slower in $7\frac{1}{2}$ hours. Find their speeds by using matrices.",
     ("Let the speeds be $u$ and $v$ km/h ($u > v$). Towards each other: $2(u + v) = 44 \\Rightarrow u + v = 22$. Same direction: "
      "$7.5(u - v) = 44 \\Rightarrow u - v = \\frac{88}{15}$.", "فرض کریں رفتاریں $u$ اور $v$ کلومیٹر فی گھنٹہ ہیں: $u + v = 22$ اور $u - v = \\frac{88}{15}$۔"),
     M([[1, 1], [1, -1]]), M([22, R(88, 15)]), ("u", "v"),
     lambda v: f"$u = {_e(v[0])} \\approx {float(v[0]):.2f}$ km/h, $v = {_e(v[1])} \\approx {float(v[1]):.2f}$ km/h",
     note={"en": "The reference notes compute the determinants as -26.867 and -15.467 (correct: -418/15 = -27.867 and -242/15 = -16.133), so their speeds "
                 "13.433 and 7.733 km/h are wrong; the correct speeds 13.93 and 8.07 km/h add to 22 and differ by 88/15.",
           "ur": "حوالہ نوٹس میں مقطع غلط نکالے گئے ہیں، اس لیے ان کی رفتاریں غلط ہیں؛ درست رفتاریں 13.93 اور 8.07 کلومیٹر فی گھنٹہ ہیں۔"})

# ------------------------------------------------------------------------------------------ Review Exercise 3

q1 = [mcq("i", r"If $\begin{bmatrix}a+2\\3\end{bmatrix}=\begin{bmatrix}7\\3\end{bmatrix}$, then $a=$", ["3", "5", "6", "7"], 1,
          [S(r"a + 2 = 7 \Rightarrow a = 5", "Equate the matching entries.", "متعلقہ ارکان برابر کریں۔", "5 + 2 == 7")]),
      mcq("ii", r"$A=\begin{bmatrix}3&5&0\end{bmatrix}$ is a ______ matrix.", [r"\text{row}", r"\text{square}", r"\text{column}", r"\text{null}"], 0,
          [T("It has only one row.", "اس کی صرف ایک قطار ہے۔")]),
      mcq("iii", r"$B=\begin{bmatrix}2\\3\end{bmatrix}$ is a ______ matrix.", [r"\text{identity}", r"\text{square}", r"\text{row}", r"\text{column}"], 3,
          [T("It has only one column.", "اس کا صرف ایک کالم ہے۔")]),
      mcq("iv", r"$M=\begin{bmatrix}1&0&0\\0&1&0\\0&0&1\end{bmatrix}$ is a/an ______ matrix.", [r"\text{rectangular}", r"\text{identity}", r"\text{column}", r"\text{row}"], 1,
          [T("1s on the leading diagonal and 0s elsewhere.", "مرکزی وتر پر 1 اور باقی جگہ 0۔")]),
      mcq("v", r"If $A^t=-A$, then $A$ is ______ matrix.", [r"\text{symmetric}", r"\text{row}", r"\text{rectangular}", r"\text{skew-symmetric}"], 3,
          [T("A matrix equal to the negative of its transpose is skew-symmetric.", "جو قالب اپنے پلٹ کے منفی کے برابر ہو وہ skew-symmetric ہے۔")]),
      mcq("vi", r"If $A=[3\ \ 4]$, $B=[7\ \ 8]$, then $A+B=$", [r"[21\ \ 32]", r"[24\ \ 28]", r"[10\ \ 12]", r"[11\ \ 11]"], 2,
          [S(r"[3 + 7\ \ 4 + 8] = [10\ \ 12]", "Add the entries.", "ارکان جمع کریں۔", "Eq(Matrix([[3, 4]]) + Matrix([[7, 8]]), Matrix([[10, 12]]))")]),
      mcq("vii", r"If $A=[3\ \ 4]$, $B=[7\ \ 8]$, then $B-A=$", [r"[10\ \ 12]", r"[11\ \ 11]", r"[4\ \ 4]", r"[-4\ \ -4]"], 2,
          [S(r"[7 - 3\ \ 8 - 4] = [4\ \ 4]", "Subtract the entries.", "ارکان تفریق کریں۔", "Eq(Matrix([[7, 8]]) - Matrix([[3, 4]]), Matrix([[4, 4]]))")]),
      mcq("viii", r"What is the additive inverse of $\begin{bmatrix}3\\4\end{bmatrix}$?", [r"\begin{bmatrix}-3\\4\end{bmatrix}", r"\begin{bmatrix}-3\\-4\end{bmatrix}",
                                                                                       r"\begin{bmatrix}3\\4\end{bmatrix}", r"\begin{bmatrix}-1\\1\end{bmatrix}"], 1,
          [S(r"-\begin{bmatrix} 3 \\ 4 \end{bmatrix} = \begin{bmatrix} -3 \\ -4 \end{bmatrix}", "Change the sign of each entry.", "ہر رکن کی علامت بدلیں۔",
             "Eq(Matrix([[3], [4]]) + Matrix([[-3], [-4]]), Matrix([[0], [0]]))")]),
      mcq("ix", r"If $A=\begin{bmatrix}3&1&3\\2&0&2\end{bmatrix}$, then order of $A^t$ is:", [r"3\text{-by-}2", r"2\text{-by-}3", r"3\text{-by-}3", r"2\text{-by-}2"], 0,
          [S(r"A: 2\text{-by-}3 \Rightarrow A^t: 3\text{-by-}2", "Transposing swaps rows and columns.", "پلٹنے سے قطاریں اور کالم بدل جاتے ہیں۔",
             "Matrix([[3, 1, 3], [2, 0, 2]]).T.rows == 3", "Matrix([[3, 1, 3], [2, 0, 2]]).T.cols == 2")]),
      mcq("x", r"$\begin{vmatrix}3&1\\0&4\end{vmatrix}=$", ["11", "12", "13", "-11"], 1,
          [S(r"(3)(4) - (1)(0) = 12", "$ad - bc$.", "$ad - bc$۔", "Matrix([[3, 1], [0, 4]]).det() == 12")])]
ex("rev3", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 3")

A2r, B2r = M([[4, 2], [7, 6]]), M([[5, 5], [8, 8]])
ex("rev3", 2, rf"If $A={mtex(A2r)}$, $B={mtex(B2r)}$, then find (i) $(A-B)^t$ (ii) $B^t-A^t$ (iii) $2A+3B$", [
    P("i", chain(lambda _: add(A2r, B2r, sign=-1), lambda v: tr(v, "(A-B)"))[0], ans((A2r - B2r).T), prompt="$(A-B)^t$"),
    P("ii", chain(lambda _: tr(B2r, "B"), lambda _: tr(A2r, "A"), lambda _: add(B2r.T, A2r.T, "B^t", "A^t", -1))[0], ans(B2r.T - A2r.T), prompt="$B^t-A^t$"),
    P("iii", chain(lambda _: scal(2, A2r), lambda _: scal(3, B2r, "B"), lambda _: add(2 * A2r, 3 * B2r, "2A", "3B"))[0], ans(2 * A2r + 3 * B2r), prompt="$2A+3B$")],
   "Review 3")

A3, B3, C3 = M([[2, 3], [4, 5]]), M([[5, 6], [2, 1]]), M([[3, 2], [1, 7]])
q3 = [verify("i", "$2(A+B)=2A+2B$", "2(A+B)", chain(lambda _: add(A3, B3), lambda v: scal(2, v, "(A+B)")),
             "2A+2B", chain(lambda _: scal(2, A3), lambda _: scal(2, B3, "B"), lambda _: add(2 * A3, 2 * B3, "2A", "2B"))),
      verify("ii", "$(A+B)+C=A+(B+C)$", "(A+B)+C", chain(lambda _: add(A3, B3), lambda v: add(v, C3, "(A+B)", "C")),
             "A+(B+C)", chain(lambda _: add(B3, C3, "B", "C"), lambda v: add(A3, v, "A", "(B+C)"))),
      verify("iii", "$(A+B)C=AC+BC$", "(A+B)C", chain(lambda _: add(A3, B3), lambda v: mul(v, C3, "(A+B)", "C")),
             "AC+BC", chain(lambda _: mul(A3, C3, "A", "C"), lambda _: mul(B3, C3, "B", "C"), lambda _: add(A3 * C3, B3 * C3, "AC", "BC"))),
      verify("iv", "$C(A-B)=CA-CB$", "C(A-B)", chain(lambda _: add(A3, B3, sign=-1), lambda v: mul(C3, v, "C", "(A-B)")),
             "CA-CB", chain(lambda _: mul(C3, A3, "C", "A"), lambda _: mul(C3, B3, "C", "B"), lambda _: add(C3 * A3, C3 * B3, "CA", "CB", -1))),
      verify("v", "$(AB)^{-1}=B^{-1}A^{-1}$", "(AB)^{-1}", chain(lambda _: mul(A3, B3), lambda v: inv(v, "(AB)")),
             "B^{-1}A^{-1}", chain(lambda _: inv(A3), lambda _: inv(B3, "B"), lambda _: mul(B3.inv(), A3.inv(), "B^{-1}", "A^{-1}"))),
      verify("vi", "$AA^{-1}=A^{-1}A=I$", "AA^{-1}", chain(lambda _: inv(A3), lambda v: mul(A3, v, "A", "A^{-1}")),
             "A^{-1}A", chain(lambda _: mul(A3.inv(), A3, "A^{-1}", "A")), "Both products are the identity matrix $I$.", "دونوں حاصل ضرب اکائی قالب $I$ ہیں۔"),
      verify("vii", "$(AB)^t=B^tA^t$", "(AB)^t", chain(lambda _: mul(A3, B3), lambda v: tr(v, "(AB)")),
             "B^tA^t", chain(lambda _: tr(B3, "B"), lambda _: tr(A3), lambda _: mul(B3.T, A3.T, "B^t", "A^t"))),
      verify("viii", "$(AB)C=A(BC)$", "(AB)C", chain(lambda _: mul(A3, B3), lambda v: mul(v, C3, "(AB)", "C")),
             "A(BC)", chain(lambda _: mul(B3, C3, "B", "C"), lambda v: mul(A3, v, "A", "(BC)")))]
ex("rev3", 3, rf"If $A={mtex(A3)}$, $B={mtex(B3)}$, $C={mtex(C3)}$, then verify that (i) $2(A+B)=2A+2B$ (ii) $(A+B)+C=A+(B+C)$ (iii) $(A+B)C=AC+BC$ "
   r"(iv) $C(A-B)=CA-CB$ (v) $(AB)^{-1}=B^{-1}A^{-1}$ (vi) $AA^{-1}=A^{-1}A=I$ (vii) $(AB)^t=B^tA^t$ (viii) $(AB)C=A(BC)$", q3, "Review 3")

A4r, B4r = M([[7, 3], [2, 1]]), M([[5, 3], [2, 4]])
ex("rev3", 4, rf"If $A={mtex(A4r)}$, $B={mtex(B4r)}$, then find (i) $|B|$ (ii) $\operatorname{{Adj}}B$ (iii) $A^{{-1}}$ (iv) $A^{{-1}}A$ (v) $(AB)^t$ (vi) $(B^t)^t$", [
    P("i", det(B4r, "B")[0], f"${B4r.det()}$", prompt="$|B|$"),
    P("ii", adj(B4r, "B")[0], ans(B4r.adjugate()), prompt=r"$\operatorname{Adj}B$"),
    P("iii", inv(A4r)[0], ans(A4r.inv()), prompt="$A^{-1}$"),
    P("iv", chain(lambda _: inv(A4r), lambda v: mul(v, A4r, "A^{-1}", "A"))[0], ans(A4r.inv() * A4r), prompt="$A^{-1}A$"),
    P("v", chain(lambda _: mul(A4r, B4r), lambda v: tr(v, "(AB)"))[0], ans((A4r * B4r).T), prompt="$(AB)^t$"),
    P("vi", chain(lambda _: tr(B4r, "B"), lambda v: tr(v, "(B^t)"))[0], ans(B4r), prompt="$(B^t)^t$")], "Review 3")

R5 = [("i", M([[3, 4], [5, -1]]), M([7, 2]), r"3x+4y=7,\ 5x-y=2"), ("ii", M([[1, -6], [2, 6]]), M([-15, -3]), r"x-6y=-15,\ 2x+6y=-3"),
      ("iii", M([[2, 1], [1, 3]]), M([5, 3]), r"2x+y=5,\ x+3y=3")]
ex("rev3", 5, "Use matrix inversion method and Cramer's rule to solve the following pair of linear equations, if possible: "
   + " ".join(f"({l}) ${t}$" for l, _, _, t in R5), [
       P(l, [T("Matrix inversion method.", "قالبی معکوس کا طریقہ۔")] + inverse_solve(a, b)[0] + [T("Cramer's rule.", "کریمر کا اصول۔")] + cramer(a, b)[0],
         sys_answer(list(a.inv() * b)), prompt=f"${t}$") for l, a, b, t in R5], "Review 3")

word("rev3", 6, "Find two numbers by using matrices such that twice the first added to the second makes 21 and twice the second added to the first makes 27.",
     ("Let the numbers be $x$ and $y$: $2x + y = 21$ and $x + 2y = 27$.", "فرض کریں اعداد $x$ اور $y$ ہیں: $2x + y = 21$ اور $x + 2y = 27$۔"),
     M([[2, 1], [1, 2]]), M([21, 27]), ("x", "y"), lambda v: f"the numbers are {_e(v[0])} and {_e(v[1])}", exercise="Review 3")
word("rev3", 7, "4 knives and 6 forks cost Rs. 136, whereas 6 knives and 5 forks cost Rs. 164. Find the cost of a knife and a fork by using matrices.",
     ("Let a knife cost $x$ and a fork $y$ rupees: $4x + 6y = 136$, $6x + 5y = 164$.", "فرض کریں چھری کی قیمت $x$ اور کانٹے کی $y$ روپے ہے: $4x + 6y = 136$، $6x + 5y = 164$۔"),
     M([[4, 6], [6, 5]]), M([136, 164]), ("x", "y"), lambda v: f"knife Rs. {_e(v[0])}, fork Rs. {_e(v[1])}", exercise="Review 3")
word("rev3", 8, "A shop employs, 5 men and 3 women, pays total daily wages Rs. 3500. If the number of men is reduced to 2 and 3 extra women are taken on, the daily "
     "wages amount to Rs. 5000. Find daily wages of a man and a woman by using matrices.",
     ("Let a man earn $m$ and a woman $w$ rupees a day: $5m + 3w = 3500$, $2m + 6w = 5000$.", "فرض کریں مرد کی اجرت $m$ اور عورت کی $w$ روپے ہے: $5m + 3w = 3500$، $2m + 6w = 5000$۔"),
     M([[5, 3], [2, 6]]), M([3500, 5000]), ("m", "w"), lambda v: f"man Rs. {_e(v[0])}, woman Rs. {_e(v[1])}", exercise="Review 3")
