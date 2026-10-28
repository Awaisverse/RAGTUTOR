"""Templates for Unit 3 (matrices and determinants). Each operation returns (steps, value) and shows the entry-by-entry
working the notes show; every result is checked as a sympy matrix equation (Eq(Matrix, Matrix))."""
import sympy as sp

from _helpers import P, S, T

Mx = sp.Matrix
R = sp.Rational


def M(rows):
    return sp.Matrix(rows)


def _e(v):
    return sp.latex(sp.nsimplify(v) if isinstance(v, float) else v)


def mtex(m, bars=False):
    env = "vmatrix" if bars else "bmatrix"
    rows = [" & ".join(_e(v) for v in m.row(i)) for i in range(m.rows)]
    return rf"\begin{{{env}}} " + r" \\ ".join(rows) + rf" \end{{{env}}}"


def strtex(rows, bars=False):
    """A matrix of already-written LaTeX strings (for the entry-by-entry working)."""
    env = "vmatrix" if bars else "bmatrix"
    return rf"\begin{{{env}}} " + r" \\ ".join(" & ".join(r) for r in rows) + rf" \end{{{env}}}"


def mpy(m):
    return "Matrix([" + ", ".join("[" + ", ".join(sp.sstr(v) for v in m.row(i)) + "]" for i in range(m.rows)) + "])"


def meq(a, b):
    return f"Eq({mpy(a)}, {mpy(b)})"


def ans(m):
    return "$" + mtex(m) + "$"


def _p(v):
    """(v) as the notes write a factor: (3), (-2)."""
    return f"({_e(v)})"


def _signed(a, b, op):
    """'a + b' / 'a - b' written as a student would: 2 - 1, -2 - (-1)."""
    if op == "+":
        return f"{_e(a)} {'-' if b < 0 else '+'} {_e(abs(b))}"
    return f"{_e(a)} - {_e(b) if b >= 0 else '(' + _e(b) + ')'}"


def order(m):
    return f"{m.rows}\\text{{-by-}}{m.cols}"


# ------------------------------------------------------------------------------------------ operations


def add(A, B, na="A", nb="B", sign=1):
    op = "+" if sign > 0 else "-"
    if A.shape != B.shape:
        raise ValueError("not conformable")
    Rm = A + B if sign > 0 else A - B
    work = [[_signed(A[i, j], B[i, j], op) for j in range(A.cols)] for i in range(A.rows)]
    steps = [S(rf"{na} {op} {nb} = {mtex(A)} {op} {mtex(B)} = {strtex(work)} = {mtex(Rm)}",
               "Matrices of the same order: " + ("add" if sign > 0 else "subtract") + " the entries in the same positions.",
               "ایک ہی درجہ کے قالب: ایک ہی مقام کے ارکان " + ("جمع" if sign > 0 else "تفریق") + " کریں۔",
               meq(A + B if sign > 0 else A - B, Rm))]
    return steps, Rm


def scal(k, A, na="A"):
    Rm = k * A
    return [S(rf"{_e(k)}{na} = {_e(k)}{mtex(A)} = {mtex(Rm)}", f"Multiply every entry by {_e(k)}.", f"ہر رکن کو {_e(k)} سے ضرب دیں۔",
              meq(k * A, Rm))], Rm


def mul(A, B, na="A", nb="B"):
    if A.cols != B.rows:
        return [S(rf"{na}\ ({order(A)}),\ {nb}\ ({order(B)}): \text{{not conformable}}",
                  f"The number of columns of ${na}$ ({A.cols}) is not equal to the number of rows of ${nb}$ ({B.rows}), so ${na}{nb}$ is not possible.",
                  f"${na}$ کے کالموں کی تعداد ({A.cols}) ${nb}$ کی قطاروں کی تعداد ({B.rows}) کے برابر نہیں، اس لیے ${na}{nb}$ ممکن نہیں۔")], None
    Rm = A * B
    prods = [[" + ".join(f"{_p(A[i, k])}{_p(B[k, j])}" for k in range(A.cols)) for j in range(B.cols)] for i in range(A.rows)]
    sums = [[" + ".join(_e(A[i, k] * B[k, j]) for k in range(A.cols)).replace("+ -", "- ") for j in range(B.cols)] for i in range(A.rows)]
    steps = [S(rf"{na}{nb} = {mtex(A)}{mtex(B)} = {strtex(prods)}",
               "Multiply each row of the first matrix by each column of the second, entry by entry, and add.",
               "پہلے قالب کی ہر قطار کو دوسرے کے ہر کالم سے رکن بہ رکن ضرب دے کر جمع کریں۔"),
             S(rf"= {strtex(sums)} = {mtex(Rm)}", "Work out the products and add them.", "حاصل ضرب نکال کر جمع کریں۔", meq(A * B, Rm))]
    return steps, Rm


def tr(A, na="A"):
    return [S(rf"{na}^t = {mtex(A)}^t = {mtex(A.T)}", "The transpose turns rows into columns.", "پلٹ (ٹرانسپوز) میں قطاریں کالم بن جاتی ہیں۔",
              f"Eq({mpy(A)}.T, {mpy(A.T)})")], A.T


def det(A, na="A"):
    a, b, c, d = A[0, 0], A[0, 1], A[1, 0], A[1, 1]
    v = A.det()
    return [S(rf"|{na}| = {mtex(A, True)} = {_p(a)}{_p(d)} - {_p(b)}{_p(c)} = {_e(a * d)} {'-' if b * c >= 0 else '+'} {_e(abs(b * c))} = {_e(v)}",
              "For a 2-by-2 matrix, $|A| = ad - bc$.", "2-by-2 قالب کے لیے $|A| = ad - bc$۔", f"{mpy(A)}.det() == {sp.sstr(v)}")], v


def adj(A, na="A"):
    Ad = A.adjugate()
    return [S(rf"\operatorname{{Adj}}{na} = {mtex(Ad)}", "Swap the entries on the leading diagonal and change the signs of the other two.",
              "مرکزی وتر کے ارکان کی جگہ بدلیں اور باقی دو کی علامت بدلیں۔", f"Eq({mpy(A)}.adjugate(), {mpy(Ad)})")], Ad


def inv(A, na="A"):
    st, d = det(A, na)
    if d == 0:
        return st + [S(rf"|{na}| = 0 \Rightarrow {na}^{{-1}} \text{{ does not exist}}", "A singular matrix has no inverse.", "نادر قالب کا معکوس نہیں ہوتا۔")], None
    s2, Ad = adj(A, na)
    Iv = A.inv()
    st += s2
    st.append(S(rf"{na}^{{-1}} = \frac{{1}}{{|{na}|}}\operatorname{{Adj}}{na} = \frac{{1}}{{{_e(d)}}}{mtex(Ad)} = {mtex(Iv)}",
                "Divide the adjoint by the determinant.", "ملحقہ قالب کو مقطع سے تقسیم کریں۔",
                f"Eq({mpy(A)}.inv(), {mpy(Iv)})", meq(A * Iv, sp.eye(A.rows))))
    return st, Iv


def chain(*ops):
    steps, v = [], None
    for op in ops:
        s, v = op(v)
        steps += s
    return steps, v


def verify(label, prompt, lhs_name, lhs, rhs_name, rhs, law_en="Both sides are equal.", law_ur="دونوں اطراف برابر ہیں۔"):
    (ls, lv), (rs, rv) = lhs, rhs
    steps = ([T(f"Left-hand side: ${lhs_name}$", f"بائیں جانب: ${lhs_name}$")] + ls + [T(f"Right-hand side: ${rhs_name}$", f"دائیں جانب: ${rhs_name}$")] + rs +
             [S(rf"{lhs_name} = {mtex(lv)} = {rhs_name}", law_en, law_ur, meq(lv, rv))])
    return P(label, steps, f"verified: both sides $= {mtex(lv)}$", prompt=prompt)


# ------------------------------------------------------------------------------------------ systems of two equations


def _eq_tex(a, b, c, names):
    x, y = names
    t = (f"{'' if a == 1 else '-' if a == -1 else _e(a)}{x}" if a != 0 else "")
    if b != 0:
        coef = "" if abs(b) == 1 else _e(abs(b))
        t += f" {'-' if b < 0 else '+'} {coef}{y}" if t else f"{'-' if b < 0 else ''}{coef}{y}"
    return f"{t} = {_e(c)}"


def system_steps(A, Bv, names=("x", "y")):
    x, y = names
    return S(rf"{mtex(A)}{strtex([[x], [y]])} = {mtex(Bv)}", "Write the equations in matrix form $AX = B$.", "مساوات کو قالبی شکل $AX = B$ میں لکھیں۔")


def inverse_solve(A, Bv, names=("x", "y")):
    """X = A^-1 B, with the working; returns (steps, (x, y))."""
    steps = [system_steps(A, Bv, names)]
    s, Iv = inv(A)
    steps += s
    if Iv is None:
        return steps, None
    d = A.det()
    Ad = A.adjugate()
    raw = Ad * Bv
    X = A.inv() * Bv
    work = [[" + ".join(f"{_p(Ad[i, k])}{_p(Bv[k, 0])}" for k in range(2))] for i in range(2)]
    steps.append(S(rf"X = A^{{-1}}B = \frac{{1}}{{{_e(d)}}}{mtex(Ad)}{mtex(Bv)} = \frac{{1}}{{{_e(d)}}}{strtex(work)} = \frac{{1}}{{{_e(d)}}}{mtex(raw)} = {mtex(X)}",
                   "Multiply $A^{-1}$ by $B$.", "$A^{-1}$ کو $B$ سے ضرب دیں۔", meq(A.inv() * Bv, X)))
    steps.append(S(rf"{names[0]} = {_e(X[0])},\quad {names[1]} = {_e(X[1])}", "Read off the unknowns, and check them in both equations.",
                   "نامعلوم قیمتیں پڑھیں اور دونوں مساوات میں جانچیں۔", meq(A * X, Bv)))
    return steps, (X[0], X[1])


def cramer(A, Bv, names=("x", "y")):
    x, y = names
    Ax = A.copy()
    Ax[:, 0] = Bv
    Ay = A.copy()
    Ay[:, 1] = Bv
    d, dx, dy = A.det(), Ax.det(), Ay.det()
    steps = [system_steps(A, Bv, names)]
    if d == 0:
        steps.append(S(rf"|A| = {mtex(A, True)} = 0", "The determinant is 0, so Cramer's rule cannot be used.",
                       "مقطع 0 ہے، اس لیے کریمر کا اصول استعمال نہیں ہو سکتا۔", f"{mpy(A)}.det() == 0"))
        return steps, None

    def dline(name, m, v):
        a, b, c, e = m[0, 0], m[0, 1], m[1, 0], m[1, 1]
        return rf"{name} = {mtex(m, True)} = {_p(a)}{_p(e)} - {_p(b)}{_p(c)} = {_e(v)}"
    steps += [S(dline("|A|", A, d), "Find $|A|$ from the coefficients.", "عددی سروں سے $|A|$ معلوم کریں۔", f"{mpy(A)}.det() == {sp.sstr(d)}"),
              S(dline(f"|A_{x}|", Ax, dx), f"Replace the ${x}$-column by the constants and find the determinant.",
                f"${x}$ کے کالم کی جگہ مستقل اعداد رکھ کر مقطع معلوم کریں۔", f"{mpy(Ax)}.det() == {sp.sstr(dx)}"),
              S(dline(f"|A_{y}|", Ay, dy), f"Replace the ${y}$-column by the constants.", f"${y}$ کے کالم کی جگہ مستقل اعداد رکھیں۔",
                f"{mpy(Ay)}.det() == {sp.sstr(dy)}"),
              S(rf"{x} = \frac{{|A_{x}|}}{{|A|}} = \frac{{{_e(dx)}}}{{{_e(d)}}} = {_e(dx / d)},\quad {y} = \frac{{|A_{y}|}}{{|A|}} = \frac{{{_e(dy)}}}{{{_e(d)}}} = {_e(dy / d)}",
                "Cramer's rule.", "کریمر کا اصول۔", meq(A * Mx([dx / d, dy / d]), Bv))]
    return steps, (dx / d, dy / d)


def sys_answer(vals, names=("x", "y")):
    return "$" + r",\ ".join(f"{n} = {_e(v)}" for n, v in zip(names, vals)) + "$"
