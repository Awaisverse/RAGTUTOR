"""Class 11 matrix and determinant templates (Unit 4): 3-by-3 expansion, minors and cofactors, the adjoint inverse,
elementary row operations (inverse by [A | I], rank by echelon form, systems by echelon form and RREF), Cramer's rule,
the inversion method, homogeneous systems and determinant properties (row/column operations with a factor kept outside).
Every step is checked with sympy; the step text says what is done and why, as the typed solutions do.

The Class 10 templates (data/src10/_mat.py) are 2-by-2 only for determinants and adjoints; these work for any order."""
import sympy as sp

from _helpers import P, S, T

R = sp.Rational
L = sp.latex


# ------------------------------------------------------------------------------------------ writing

def e(v):
    return L(sp.nsimplify(v) if isinstance(v, float) else v)


def _t(v):
    """An entry or factor: sums with the positive term first (b - a, not -a + b)."""
    return nice(v, True) if getattr(v, "is_Add", False) else e(v)


def p(v):
    """(v) as a factor in the working: (3), (-2), (a + b), (b - a)."""
    return f"({_t(v)})"


def mtex(m, bars=False):
    env = "vmatrix" if bars else "bmatrix"
    rows = [" & ".join(_t(v) for v in m.row(i)) for i in range(m.rows)]
    return rf"\begin{{{env}}} " + r" \\ ".join(rows) + rf" \end{{{env}}}"


def strtex(rows, bars=False):
    env = "vmatrix" if bars else "bmatrix"
    return rf"\begin{{{env}}} " + r" \\ ".join(" & ".join(r) for r in rows) + rf" \end{{{env}}}"


def augtex(m, split):
    """[A | B] with a bar after column `split`."""
    cols = "c" * split + "|" + "c" * (m.cols - split)
    rows = [" & ".join(e(v) for v in m.row(i)) for i in range(m.rows)]
    return rf"\left[\begin{{array}}{{{cols}}} " + r" \\ ".join(rows) + r" \end{array}\right]"


def py(v):
    return sp.sstr(v)


def mpy(m):
    return "Matrix([" + ", ".join("[" + ", ".join(py(v) for v in m.row(i)) + "]" for i in range(m.rows)) + "])"


def meq(a, b):
    """Entry-by-entry equality (the checker simplifies each entry, so unexpanded complex products compare correctly)."""
    return f"{mpy(a)} == {mpy(b)}"


def ans(m):
    return "$" + mtex(m) + "$"


def _plus(terms):
    """'a + b - c' from already-signed pieces [('+', 'a'), ('-', 'b'), ...]."""
    out = ""
    for sgn, t in terms:
        out += (f" {sgn} " if out else ("" if sgn == "+" else "-")) + t
    return out


def simp(v):
    v = sp.factor(sp.expand(v))
    return v


# ------------------------------------------------------------------------------------------ products, sums, transposes

def madd(A, B, na="A", nb="B", sign=1):
    op = "+" if sign > 0 else "-"
    Rm = (A + B if sign > 0 else A - B).applyfunc(sp.expand)
    work = [[f"{p(A[i, j]) if not A[i, j].is_number or A[i, j].is_real is False or A[i, j] < 0 else e(A[i, j])} {op} {p(B[i, j])}"
             for j in range(A.cols)] for i in range(A.rows)]
    return [S(rf"{na} {op} {nb} = {mtex(A)} {op} {mtex(B)} = {strtex(work)} = {mtex(Rm)}",
              "The matrices have the same order, so " + ("add" if sign > 0 else "subtract") + " the entries in the same positions.",
              "دونوں قالب ایک ہی درجے کے ہیں، اس لیے ایک ہی مقام کے ارکان " + ("جمع" if sign > 0 else "تفریق") + " کریں۔",
              meq(A + B if sign > 0 else A - B, Rm))], Rm


def mmul(A, B, na="A", nb="B"):
    Rm = (A * B).applyfunc(sp.expand)
    prods = [[" + ".join(f"{p(A[i, k])}{p(B[k, j])}" for k in range(A.cols)) for j in range(B.cols)] for i in range(A.rows)]
    return [S(rf"{na}{nb} = {mtex(A)}{mtex(B)} = {strtex(prods)}",
              f"${na}$ has {A.cols} columns and ${nb}$ has {B.rows} rows, so the product exists. Multiply each row of the first matrix by "
              "each column of the second, entry by entry, and add.",
              f"${na}$ کے {A.cols} کالم اور ${nb}$ کی {B.rows} قطاریں ہیں، اس لیے حاصل ضرب ممکن ہے۔ پہلے قالب کی ہر قطار کو دوسرے کے ہر کالم سے "
              "رکن بہ رکن ضرب دے کر جمع کریں۔"),
            S(rf"{na}{nb} = {mtex(Rm)}", "Work out every entry.", "ہر رکن کا حساب کریں۔", meq(A * B, Rm))], Rm


def mtr(A, na="A"):
    return [S(rf"{na}^t = {mtex(A.T)}", f"The transpose: row 1 of ${na}$ becomes column 1, row 2 becomes column 2, and so on.",
              f"پلٹ (transpose): ${na}$ کی پہلی قطار پہلا کالم بنتی ہے، دوسری قطار دوسرا کالم، وغیرہ۔", f"Eq({mpy(A)}.T, {mpy(A.T)})")], A.T


def mscal(k, A, na="A"):
    Rm = (k * A).applyfunc(sp.expand)
    return [S(rf"{e(k)}{na} = {e(k)}{mtex(A)} = {mtex(Rm)}", f"Multiply every entry of ${na}$ by ${e(k)}$.",
              f"${na}$ کے ہر رکن کو ${e(k)}$ سے ضرب دیں۔", meq(k * A, Rm))], Rm


# ------------------------------------------------------------------------------------------ determinants

def minor(A, i, j):
    return A.minor_submatrix(i, j)


def det2_work(m):
    a, b, c, d = m[0, 0], m[0, 1], m[1, 0], m[1, 1]
    return f"{p(a)}{p(d)} - {p(b)}{p(c)}"


def det_expand(A, lhs="|A|", row=0, simplify=simp, factor=None):
    """|A| of a 3-by-3 (or 2-by-2) matrix by expansion along `row`: the minors, their values, the total.
    `factor` (an expression) is kept in front of the determinant. -> (steps, value including the factor)."""
    v = A.det()
    fpre = "" if factor is None or factor == 1 else (nice(factor) if factor != -1 else "-")
    fval = 1 if factor is None else factor
    if A.rows == 2:
        val = simplify(fval * v)
        return [S(rf"{lhs} = {fpre}{mtex(A, True)} = {fpre}\left[{det2_work(A)}\right] = {e(val)}",
                  "For a 2-by-2 determinant, multiply along the leading diagonal and subtract the product along the other diagonal.",
                  "2-by-2 مقطع میں مرکزی وتر کے ارکان کا حاصل ضرب لیں اور دوسرے وتر کے حاصل ضرب کو منفی کریں۔",
                  f"expand(({py(fval)})*{mpy(A)}.det()) == expand({py(val)})")], val
    terms1, terms2, terms3, checks = [], [], [], []
    for j in range(3):
        a = A[row, j]
        sgn = "+" if (row + j) % 2 == 0 else "-"
        if a == 0:
            continue
        M = minor(A, row, j)
        mv = sp.expand(M.det())
        terms1.append((sgn, rf"{p(a)}{mtex(M, True)}"))
        terms2.append((sgn, rf"{p(a)}\left[{det2_work(M)}\right]"))
        terms3.append((sgn, rf"{p(a)}{p(sp.expand(mv) if mv.free_symbols else simplify(mv))}"))
        checks.append(f"expand({mpy(M)}.det()) == expand({py(mv)})")
    val = simplify(fval * v)
    where = f"row {row + 1}"
    zeros = sum(1 for j in range(3) if A[row, j] == 0)
    steps = [S(rf"{lhs} = {fpre}{mtex(A, True)} = {fpre}\left[{_plus(terms1)}\right]" if fpre else rf"{lhs} = {mtex(A, True)} = {_plus(terms1)}",
               f"Expand along {where}" + (f" (it has {zeros} zero{'s' if zeros > 1 else ''}, so fewer terms)" if zeros else "") +
               ": each entry times its minor (delete that entry's row and column), with the signs $+\\ -\\ +$"
               + (" for the middle row: $-\\ +\\ -$" if row == 1 else "") + ".",
               f"قطار {row + 1} کے ساتھ پھیلائیں" + ("، اس میں صفر ہیں اس لیے کم ارکان بنتے ہیں" if zeros else "") +
               ": ہر رکن کو اس کے مائنر (اس رکن کی قطار اور کالم ہٹا کر بننے والا مقطع) سے ضرب دیں، علامتیں $+\\ -\\ +$" +
               (" اور درمیانی قطار کے لیے $-\\ +\\ -$" if row == 1 else "") + "۔"),
             S(rf"= {fpre}\left[{_plus(terms2)}\right]" if fpre else rf"= {_plus(terms2)}", "Open each 2-by-2 minor: $ad - bc$.",
               "ہر 2-by-2 مائنر کھولیں: $ad - bc$۔", *checks),
             S(rf"= {fpre}\left[{_plus(terms3)}\right] = {e(val)}" if fpre else rf"= {_plus(terms3)} = {e(val)}",
               "Multiply out and simplify.", "ضرب دے کر سادہ کریں۔", f"expand(({py(fval)})*{mpy(A)}.det()) == expand({py(val)})")]
    inner = sp.expand(v)
    one = len(terms3) == 1 and sum(1 for j in range(3) if A[row, j] == 1) == 1 and all(A[row, j] in (0, 1) for j in range(3))
    if inner.free_symbols and e(inner) != e(simplify(v)) and not one:   # letters: the expanded form before factorizing
        mid = rf"{fpre}\left[{e(inner)}\right]" if fpre else e(inner)
        steps[-1]["math"] = (rf"= {fpre}\left[{_plus(terms3)}\right] = {mid} = {e(val)}" if fpre else rf"= {_plus(terms3)} = {mid} = {e(val)}")
        steps[-1]["en"] = "Multiply out, cancel the like terms, then factorize."
        steps[-1]["ur"] = "ضرب دے کر یکساں ارکان کاٹیں، پھر تجزی کریں۔"
        steps[-1]["check"].append(f"expand({mpy(A)}.det()) == expand({py(inner)})")
    return steps, val


def det_line(A, lhs):
    """One-line |A| for Cramer's rule and the inversion method: lhs = |A| = a(..) - b(..) + c(..) = value."""
    v = A.det()
    if A.rows == 2:
        return S(rf"{lhs} = {mtex(A, True)} = {det2_work(A)} = {e(v)}", "", "", f"{mpy(A)}.det() == {py(v)}"), v
    parts = []
    for j in range(3):
        if A[0, j] == 0:
            continue
        parts.append(("+" if j % 2 == 0 else "-", rf"{p(A[0, j])}\left[{det2_work(minor(A, 0, j))}\right]"))
    return S(rf"{lhs} = {mtex(A, True)} = {_plus(parts)} = {e(v)}", "", "", f"{mpy(A)}.det() == {py(v)}"), v


def cofactor_step(A, i, j, name="A"):
    M = minor(A, i, j)
    mv = M.det()
    c = (-1) ** (i + j) * mv
    sgn = "" if (i + j) % 2 == 0 else "-"
    return S(rf"{name}_{{{i + 1}{j + 1}}} = (-1)^{{{i + 1}+{j + 1}}}{mtex(M, True)} = {sgn}\left[{det2_work(M)}\right] = {e(c)}",
             f"Delete row {i + 1} and column {j + 1} to get the minor $M_{{{i + 1}{j + 1}}}$; the cofactor is $(-1)^{{i+j}}M_{{ij}}$.",
             f"قطار {i + 1} اور کالم {j + 1} ہٹا کر مائنر $M_{{{i + 1}{j + 1}}}$ ملتا ہے؛ ہم عامل (cofactor) $(-1)^{{i+j}}M_{{ij}}$ ہے۔",
             f"{mpy(A)}.cofactor({i}, {j}) == {py(c)}"), c


def adjoint_inverse(A, name="A"):
    """|A|, the matrix of cofactors, adj A and A^-1 = adj A / |A|. -> (steps, inverse or None)."""
    steps, d = det_expand(A, f"|{name}|")
    if d == 0:
        steps.append(S(rf"|{name}| = 0 \Rightarrow {name} \text{{ is singular, so }} {name}^{{-1}} \text{{ does not exist}}",
                       "A matrix with determinant 0 has no inverse.", "جس قالب کا مقطع 0 ہو اس کا معکوس نہیں ہوتا۔"))
        return steps, None
    steps.append(S(rf"|{name}| = {e(d)} \ne 0", f"So ${name}$ is non-singular and ${name}^{{-1}}$ exists.",
                   f"اس لیے ${name}$ غیر نادر ہے اور ${name}^{{-1}}$ موجود ہے۔"))
    C = A.cofactor_matrix()
    for i in range(A.rows):
        line = r",\quad ".join(rf"{name}_{{{i + 1}{j + 1}}} = {'' if (i + j) % 2 == 0 else '-'}{mtex(minor(A, i, j), True)} = {e(C[i, j])}"
                               for j in range(A.cols))
        steps.append(S(line, f"Cofactors of row {i + 1}: delete the entry's row and column, find the 2-by-2 determinant, and use the sign "
                             "pattern $\\begin{smallmatrix} + & - & + \\\\ - & + & - \\\\ + & - & + \\end{smallmatrix}$.",
                       f"قطار {i + 1} کے ہم عامل: رکن کی قطار اور کالم ہٹا کر 2-by-2 مقطع نکالیں اور علامتوں کا نمونہ "
                       "$\\begin{smallmatrix} + & - & + \\\\ - & + & - \\\\ + & - & + \\end{smallmatrix}$ استعمال کریں۔",
                       *[f"{mpy(A)}.cofactor({i}, {j}) == {py(C[i, j])}" for j in range(A.cols)]))
    Ad = C.T
    Iv = A.inv()
    steps.append(S(rf"\operatorname{{adj}}{name} = \left[{name}_{{ij}}\right]^t = {mtex(Ad)}",
                   "The adjoint is the transpose of the matrix of cofactors.", "ملحقہ (adjoint) قالب ہم عاملوں کے قالب کا پلٹ ہے۔",
                   f"Eq({mpy(A)}.adjugate(), {mpy(Ad)})"))
    steps.append(S(rf"{name}^{{-1}} = \frac{{1}}{{|{name}|}}\operatorname{{adj}}{name} = \frac{{1}}{{{e(d)}}}{mtex(Ad)} = {mtex(Iv)}",
                   "Divide every entry of the adjoint by the determinant.", "ملحقہ قالب کے ہر رکن کو مقطع سے تقسیم کریں۔",
                   f"Eq({mpy(A)}.inv(), {mpy(Iv)})"))
    return steps, Iv


# ------------------------------------------------------------------------------------------ elementary row operations

def _rname(i):
    return f"R_{i + 1}"


def _coef(k):
    """'3', '-', '' or '\\frac{1}{2}' in front of a row name."""
    if k == 1:
        return ""
    if k == -1:
        return "-"
    return e(k)


def _comb(i, terms):
    """'R_2 - 3R_1' for R_i + sum k R_j."""
    s = _rname(i)
    for j, k in terms:
        s += f" {'-' if k < 0 else '+'} {_coef(abs(k))}{_rname(j)}"
    return s


def row_reduce(M, split, mode="rref", integer=False):
    """Elementary row operations on M (an augmented [A | B] when split < M.cols).

    mode 'rref': pivots made 1 and every other entry of a pivot column made 0 (Gauss-Jordan);
    mode 'echelon': zeros below each pivot only; with integer=True rows are combined as p R_j - q R_i (no fractions).
    -> (steps, final matrix, pivot columns)."""
    M = M.copy()
    steps = []
    show = (lambda m: augtex(m, split)) if split < M.cols else mtex
    r = 0
    pivots = []
    ncol = split
    for c in range(ncol):
        if r >= M.rows:
            break
        rows = [i for i in range(r, M.rows) if M[i, c] != 0]
        if not rows:
            continue
        best = next((i for i in rows if M[i, c] in (1, -1)), rows[0])
        if best != r:
            prev = M.copy()
            M.row_swap(r, best)
            steps.append(S(rf"{_rname(r)} \leftrightarrow {_rname(best)}:\ {show(M)}",
                           f"Interchange rows {r + 1} and {best + 1} so that the pivot is a convenient number.",
                           f"قطار {r + 1} اور {best + 1} کی جگہ بدلیں تاکہ محور (pivot) ایک آسان عدد ہو۔",
                           f"Eq({mpy(M)}.row({r}), {mpy(prev)}.row({best}))", f"Eq({mpy(M)}.row({best}), {mpy(prev)}.row({r}))"))
        piv = M[r, c]
        if mode in ("rref", "unit") and piv != 1:
            prev = M.copy()
            M[r, :] = (M[r, :] / piv).applyfunc(sp.nsimplify)
            k = 1 / piv
            steps.append(S(rf"{_rname(r)} \to {_coef(k)}{_rname(r)}:\ {show(M)}",
                           f"Divide row {r + 1} by ${e(piv)}$ to make the pivot $1$.", f"محور کو $1$ بنانے کے لیے قطار {r + 1} کو ${e(piv)}$ سے تقسیم کریں۔",
                           f"Eq({mpy(M)}.row({r}), ({py(k)})*{mpy(prev)}.row({r}))"))
            piv = 1
        targets = [i for i in range(M.rows) if i != r and M[i, c] != 0 and (mode == "rref" or i > r)]
        if targets:
            prev = M.copy()
            ops, checks = [], []
            for i in targets:
                q = prev[i, c]
                if integer and mode == "echelon" and (piv not in (1, -1) or not q.is_integer):
                    g = sp.gcd(piv, q)
                    a, b = piv / g, q / g
                    if a < 0:
                        a, b = -a, -b
                    M[i, :] = (a * prev[i, :] - b * prev[r, :]).applyfunc(sp.expand)
                    ops.append(rf"{_rname(i)} \to {_coef(a)}{_rname(i)} {'-' if b > 0 else '+'} {_coef(abs(b))}{_rname(r)}")
                    checks.append(f"Eq({mpy(M)}.row({i}), ({py(a)})*{mpy(prev)}.row({i}) - ({py(b)})*{mpy(prev)}.row({r}))")
                else:
                    k = -q / piv
                    M[i, :] = (prev[i, :] + k * prev[r, :]).applyfunc(sp.expand)
                    ops.append(rf"{_comb(i, [(r, k)])}".replace(f"{_rname(i)} ", rf"{_rname(i)} \to {_rname(i)} ", 1))
                    checks.append(f"Eq({mpy(M)}.row({i}), {mpy(prev)}.row({i}) + ({py(k)})*{mpy(prev)}.row({r}))")
            steps.append(S(r",\ ".join(ops) + rf":\ {show(M)}",
                           f"Use row {r + 1} to make every other entry of column {c + 1} zero" if mode == "rref" else
                           f"Use row {r + 1} to make the entries below the pivot in column {c + 1} zero.",
                           f"قطار {r + 1} کی مدد سے کالم {c + 1} کے باقی تمام ارکان صفر کریں۔" if mode == "rref" else
                           f"قطار {r + 1} کی مدد سے کالم {c + 1} میں محور کے نیچے والے ارکان صفر کریں۔", *checks))
        pivots.append(c)
        r += 1
    return steps, M, pivots


def back_reduce(M, split, pivots):
    """From an echelon form with pivots 1: clear the entries above each pivot, last pivot first (-> reduced echelon form)."""
    M = M.copy()
    steps = []
    show = (lambda m_: augtex(m_, split)) if split < M.cols else mtex
    for r in range(len(pivots) - 1, 0, -1):
        c = pivots[r]
        targets = [i for i in range(r) if M[i, c] != 0]
        if not targets:
            continue
        prev = M.copy()
        ops, checks = [], []
        for i in targets:
            k = -prev[i, c]
            M[i, :] = (prev[i, :] + k * prev[r, :]).applyfunc(sp.expand)
            ops.append(rf"{_comb(i, [(r, k)])}".replace(f"{_rname(i)} ", rf"{_rname(i)} \to {_rname(i)} ", 1))
            checks.append(f"Eq({mpy(M)}.row({i}), {mpy(prev)}.row({i}) + ({py(k)})*{mpy(prev)}.row({r}))")
        steps.append(S(r",\ ".join(ops) + rf":\ {show(M)}", f"Use row {r + 1} to make the entries above its pivot in column {c + 1} zero.",
                       f"قطار {r + 1} کی مدد سے کالم {c + 1} میں محور کے اوپر والے ارکان صفر کریں۔", *checks))
    return steps, M


def inverse_rowops(A, name="A"):
    n = A.rows
    aug = A.row_join(sp.eye(n))
    steps = [S(rf"\left[{name} \mid I_{n}\right] = {augtex(aug, n)}", f"Write ${name}$ and the identity matrix side by side.",
               f"${name}$ اور اکائی قالب کو ساتھ ساتھ لکھیں۔")]
    if A.det() == 0:
        return steps + [S(rf"|{name}| = 0", "The matrix is singular, so it has no inverse.", "قالب نادر ہے، اس لیے اس کا معکوس نہیں۔",
                          f"{mpy(A)}.det() == 0")], None
    s, M, _ = row_reduce(aug, n, "rref")
    steps += s
    Iv = M[:, n:]
    steps.append(S(rf"\left[I_{n} \mid {name}^{{-1}}\right] \Rightarrow {name}^{{-1}} = {mtex(Iv)}",
                   f"The left half is now $I_{n}$, so the right half is ${name}^{{-1}}$.", f"بایاں حصہ اب $I_{n}$ ہے، اس لیے دایاں حصہ ${name}^{{-1}}$ ہے۔",
                   f"Eq({mpy(A)}*{mpy(Iv)}, eye({n}))"))
    return steps, Iv


def rank_steps(A, name="A"):
    steps = [S(rf"{name} = {mtex(A)}", "Reduce the matrix to echelon form; the rank is the number of non-zero rows.",
               "قالب کو زینہ دار (echelon) شکل میں لائیں؛ رینک غیر صفر قطاروں کی تعداد ہے۔")]
    s, M, piv = row_reduce(A, A.cols, "echelon", integer=True)
    steps += s
    r = len(piv)
    steps.append(S(rf"\text{{rank}}({name}) = {r}", f"The echelon form has {r} non-zero row{'s' if r != 1 else ''}.",
                   f"زینہ دار شکل میں {r} غیر صفر قطاریں ہیں۔", f"{mpy(A)}.rank() == {r}"))
    return steps, r


# ------------------------------------------------------------------------------------------ systems of equations

def _lin(row, names):
    t = ""
    for a, n in zip(row, names):
        if a == 0:
            continue
        c = "" if abs(a) == 1 else e(abs(a))
        t += (f" {'-' if a < 0 else '+'} {c}{n}" if t else f"{'-' if a < 0 else ''}{c}{n}")
    return t or "0"


def system_tex(A, Bv, names):
    return r"\begin{cases} " + r" \\ ".join(f"{_lin(A.row(i), names)} = {e(Bv[i])}" for i in range(A.rows)) + r" \end{cases}"


def matrix_form(A, Bv, names):
    return S(rf"AX = B:\quad {mtex(A)}{strtex([[n] for n in names])} = {mtex(Bv)}",
             "Write the system in matrix form: $A$ holds the coefficients, $X$ the unknowns and $B$ the constants.",
             "نظام کو قالبی شکل میں لکھیں: $A$ میں عددی سر، $X$ میں نامعلوم اور $B$ میں مستقل اعداد۔")


def sys_answer(vals, names):
    if len(names) == 3 and all(n.startswith("x_") for n in names):
        return "$(" + ", ".join(names) + r") = \left(" + ", ".join(e(v) for v in vals) + r"\right)$"
    return "$" + r",\ ".join(f"{n} = {e(v)}" for n, v in zip(names, vals)) + "$"


def cramer(A, Bv, names):
    n = A.rows
    st, d = det_line(A, r"\Delta")
    st["en"], st["ur"] = "Find the determinant of the coefficients first.", "پہلے عددی سروں کا مقطع معلوم کریں۔"
    steps = [matrix_form(A, Bv, names), st]
    if d == 0:
        steps.append(S(r"\Delta = 0", "Cramer's rule needs $\\Delta \\ne 0$.", "کریمر کے اصول کے لیے $\\Delta \\ne 0$ ضروری ہے۔"))
        return steps, None
    vals = []
    for k in range(n):
        Ak = A.copy()
        Ak[:, k] = Bv
        s, dk = det_line(Ak, rf"\Delta_{{{k + 1}}}")
        s["en"] = f"Replace column {k + 1} (the ${names[k]}$-column) by the constants and find the determinant."
        s["ur"] = f"کالم {k + 1} (${names[k]}$ کا کالم) کی جگہ مستقل اعداد رکھ کر مقطع معلوم کریں۔"
        steps.append(s)
        vals.append(dk / d)
    steps.append(S(r",\quad ".join(rf"{nm} = \frac{{\Delta_{{{k + 1}}}}}{{\Delta}} = {e(vals[k])}" for k, nm in enumerate(names)),
                   "Cramer's rule: each unknown is its replaced determinant divided by $\\Delta$.",
                   "کریمر کا اصول: ہر نامعلوم اپنے بدلے ہوئے مقطع کو $\\Delta$ سے تقسیم کرنے سے ملتا ہے۔",
                   meq(A * sp.Matrix(vals), Bv)))
    return steps, vals


def inversion(A, Bv, names):
    steps = [matrix_form(A, Bv, names)]
    s, Iv = adjoint_inverse(A)
    steps += s
    if Iv is None:
        return steps, None
    X = Iv * Bv
    d = A.det()
    raw = A.adjugate() * Bv
    steps.append(S(rf"X = A^{{-1}}B = \frac{{1}}{{{e(d)}}}{mtex(A.adjugate())}{mtex(Bv)} = \frac{{1}}{{{e(d)}}}{mtex(raw)} = {mtex(X)}",
                   "Multiply $A^{-1}$ by $B$.", "$A^{-1}$ کو $B$ سے ضرب دیں۔", meq(Iv * Bv, X)))
    steps.append(S(r",\quad ".join(f"{n} = {e(v)}" for n, v in zip(names, X)), "Read off the unknowns; they satisfy all the equations.",
                   "نامعلوم قیمتیں پڑھیں؛ یہ تمام مساوات کو پورا کرتی ہیں۔", meq(A * X, Bv)))
    return steps, list(X)


def gauss_jordan(A, Bv, names):
    """Echelon form, then reduced echelon form, of [A | B]."""
    n = A.cols
    aug = A.row_join(Bv)
    steps = [S(rf"\left[A \mid B\right] = {augtex(aug, n)}", "Write the augmented matrix of the system.", "نظام کا بڑھایا ہوا (augmented) قالب لکھیں۔")]
    s, M, piv = row_reduce(aug, n, "unit")
    steps += s
    if piv != list(range(n)):
        return steps, None
    steps.append(S(rf"\text{{Echelon form: }} {augtex(M, n)}",
                   "Each pivot is 1 and every entry below a pivot is 0: this is the echelon form.",
                   "ہر محور 1 ہے اور ہر محور کے نیچے والے ارکان 0 ہیں: یہ زینہ دار (echelon) شکل ہے۔"))
    s, M = back_reduce(M, n, piv)
    steps += s
    vals = list(M[:, n])
    steps.append(S(rf"\text{{Reduced echelon form: }} {augtex(M, n)} \Rightarrow " + r",\quad ".join(f"{nm} = {e(v)}" for nm, v in zip(names, vals)),
                   "Now every pivot column has 0 everywhere except its pivot: this is the reduced echelon form, and each row reads one unknown.",
                   "اب ہر محوری کالم میں محور کے سوا باقی ارکان 0 ہیں: یہ تحویل شدہ زینہ دار شکل ہے، اور ہر قطار سے ایک نامعلوم ملتا ہے۔",
                   meq(A * sp.Matrix(vals), Bv)))
    return steps, vals


def homogeneous(A, names):
    """AX = 0: |A| != 0 gives only the trivial solution; |A| = 0 gives a family with a parameter t."""
    n = A.cols
    st, d = det_line(A, "|A|")
    st["en"] = "For a homogeneous system, first find $|A|$: it decides whether non-trivial solutions exist."
    st["ur"] = "متجانس نظام میں پہلے $|A|$ معلوم کریں: اسی سے پتا چلتا ہے کہ غیر صفری حل ہیں یا نہیں۔"
    steps = [S(rf"AX = O:\quad {mtex(A)}{strtex([[x] for x in names])} = {mtex(sp.zeros(n, 1))}",
               "Write the system in matrix form; the constants are all zero.", "نظام کو قالبی شکل میں لکھیں؛ تمام مستقل صفر ہیں۔"), st]
    s, M, piv = row_reduce(A, n, "unit")                  # Gaussian elimination: echelon form, then back-substitution
    steps += s
    if d != 0:
        steps.append(S(rf"\text{{Echelon form: }} {mtex(M)}", "Each pivot is 1 and every entry below a pivot is 0.",
                       "ہر محور 1 ہے اور ہر محور کے نیچے والے ارکان 0 ہیں۔"))
        last = names[-1]
        steps.append(S(rf"{last} = 0 \Rightarrow " + r" \Rightarrow ".join(f"{x} = 0" for x in reversed(names[:-1])) + r"\ \text{(trivial solution only)}",
                       "Back-substitution: the last row gives the last unknown as 0, and then each row above gives 0 too. "
                       "Since $|A| \\ne 0$ the only solution is the trivial one.",
                       "پچھلی طرف سے قیمتیں رکھیں: آخری قطار سے آخری نامعلوم 0 ملتا ہے، پھر اوپر والی ہر قطار سے بھی 0۔ "
                       "چونکہ $|A| \\ne 0$، اس لیے صرف صفری (trivial) حل ہے۔", f"Abs({mpy(A)}.det()) > 0"))
        return steps, [0] * n, None
    free = [c for c in range(n) if c not in piv]
    tt = sp.Symbol("t")
    steps.append(S(rf"\text{{Echelon form: }} {mtex(M)}",
                   f"$|A| = 0$, so a row of zeros appears: there are infinitely many solutions, and ${names[free[0]]}$ is a free unknown.",
                   f"$|A| = 0$، اس لیے صفروں کی ایک قطار بن جاتی ہے: لامحدود حل ہیں اور ${names[free[0]]}$ آزاد نامعلوم ہے۔"))
    sol = [None] * n
    for f in free:
        sol[f] = tt
    back = []
    for r_ in range(len(piv) - 1, -1, -1):
        c = piv[r_]
        sol[c] = sp.expand(-sum(M[r_, j] * sol[j] for j in range(c + 1, n)))
        back.append(rf"{_lin(M.row(r_), names)} = 0 \Rightarrow {names[c]} = {e(sol[c])}")
    steps.append(S(rf"{names[free[0]]} = t:\quad " + r",\quad ".join(back),
                   f"Back-substitution: put ${names[free[0]]} = t$ and work upwards, one row at a time.",
                   f"پچھلی طرف سے قیمتیں رکھیں: ${names[free[0]]} = t$ لے کر اوپر کی طرف ایک ایک قطار حل کریں۔",
                   meq(A * sp.Matrix(sol), sp.zeros(n, 1))))
    g = sp.lcm([sp.fraction(sp.nsimplify(v / tt))[1] for v in sol if v != 0])
    base = [sp.expand(v / tt * g) for v in sol]
    vec = sp.Matrix(base)
    steps.append(S(rf"({', '.join(names)}) = t({', '.join(e(v) for v in base)}),\quad t \in \mathbb{{R}}",
                   f"Put ${names[free[0]]}$ = ${e(g)}t$" + " (to avoid fractions)" * (g != 1) + " and write every unknown in terms of $t$.",
                   f"${names[free[0]]} = {e(g)}t$ رکھیں" + (" (کسور سے بچنے کے لیے)" if g != 1 else "") + " اور ہر نامعلوم کو $t$ کی صورت میں لکھیں۔",
                   meq(A * vec, sp.zeros(n, 1))))
    return steps, base, free


def det_equation(Mx, k, var, sym=None):
    """Find var so that |Mx| = k (k = 0: the matrix is singular). -> (steps, solutions). The unknown is shown as `sym`."""
    sym = sym or L(var)
    show = (lambda s_: s_.replace(L(var), sym)) if sym != L(var) else (lambda s_: s_)
    s_, val = det_expand(Mx, "D", simplify=sp.expand)
    for st in s_:
        st["math"] = show(st["math"])
    poly = sp.expand(Mx.det() - k)
    if not poly.free_symbols or sp.degree(poly, var) < 1:
        return None, None
    sols = [v for v in sp.solve(poly, var) if v.is_real]
    if not sols:
        return None, None
    fac = sp.factor(poly)
    steps = s_ + [S(show(rf"{e(val)} = {e(k)} \Rightarrow {e(poly)} = 0"),
                    "The matrix is singular exactly when its determinant is 0." if k == 0 else
                    f"Put the determinant equal to ${e(k)}$ and bring everything to one side.",
                    "قالب اسی وقت نادر ہے جب اس کا مقطع 0 ہو۔" if k == 0 else f"مقطع کو ${e(k)}$ کے برابر رکھ کر سب ارکان ایک طرف لے آئیں۔",
                    f"expand({mpy(Mx)}.det() - ({py(k)})) == expand({py(poly)})")]
    if sp.degree(poly, var) == 2 and fac != poly:
        steps.append(S(show(rf"{e(fac)} = 0"), "Factorize.", "تجزی کریں۔", f"expand({py(fac)}) == expand({py(poly)})"))
    steps.append(S(f"{sym} = " + r" \quad \text{or} \quad ".join(e(s) for s in sols),
                   "Each value makes the determinant equal to the given number.", "ہر قیمت پر مقطع دیے گئے عدد کے برابر ہو جاتا ہے۔",
                   *[f"{mpy(Mx.subs(var, s))}.det() == {py(k)}" for s in sols]))
    return steps, sols


def matrix_poly(terms, A, name="A"):
    """c1 A^k1 + ... + c I for one square matrix A. terms: [(coefficient, power)] with power 0 for I. -> (steps, value)."""
    n = A.rows
    steps, pieces, total = [], [], sp.zeros(n, n)
    powers = {}
    for k in sorted({k for _, k in terms if k >= 2}):
        prev = powers.get(k - 1, A)
        s_, v = mmul(prev, A, name if k == 2 else f"{name}^{{{k - 1}}}", name)
        s_[-1]["math"] = s_[-1]["math"].replace(f"{name}{name} =", f"{name}^2 =", 1) if k == 2 else s_[-1]["math"]
        steps += s_
        powers[k] = v
    for coef, k in terms:
        base = sp.eye(n) if k == 0 else (A if k == 1 else powers[k])
        bname = "I" if k == 0 else (name if k == 1 else f"{name}^{{{k}}}")
        val = (coef * base).applyfunc(sp.expand)
        if coef not in (1,):
            steps.append(S(rf"{e(coef)}{bname} = {mtex(val)}", f"Multiply every entry of ${bname}$ by ${e(coef)}$.", f"${bname}$ کے ہر رکن کو ${e(coef)}$ سے ضرب دیں۔",
                           meq(coef * base, val)))
        pieces.append(mtex(val))
        total += val
    expr_tex = ""
    for coef, k in terms:
        bname = "I" if k == 0 else (name if k == 1 else f"{name}^{{{k}}}")
        c_ = "" if abs(coef) == 1 else e(abs(coef))
        expr_tex += (f" {'-' if coef < 0 else '+'} " if expr_tex else ("-" if coef < 0 else "")) + f"{c_}{bname}"
    chk_terms = " + ".join(f"({py(c_)})*{mpy(A)}**{k}" if k else f"({py(c_)})*eye({n})" for c_, k in terms)
    steps.append(S(rf"{expr_tex} = " + " + ".join(pieces) + rf" = {mtex(total)}", "Add the matrices entry by entry.", "قالبوں کو رکن بہ رکن جمع کریں۔",
                   f"{chk_terms} == {mpy(total)}"))
    return steps, total, expr_tex


# ------------------------------------------------------------------------------------------ determinant properties

def nice(v, bare=False):
    """A factor as a student writes it: c - a (not -a + c); products of brackets (b - a)(c - a); bare=True: no outer
    brackets around a single sum."""
    v = sp.sympify(v)
    if v.is_Add:
        terms = sorted(v.as_ordered_terms(), key=lambda t_: t_.could_extract_minus_sign())   # positive terms first
        s = e(terms[0])
        for t_ in terms[1:]:
            s += f" - {e(-t_)}" if t_.could_extract_minus_sign() else f" + {e(t_)}"
        return s if bare else f"({s})"
    if v.is_Mul:
        num, den = sp.fraction(v)
        if den != 1:
            return e(v)
        coef, rest = v.as_coeff_Mul()
        out = "" if coef == 1 else "-" if coef == -1 else e(coef)
        for f_ in rest.as_ordered_factors():
            out += nice(f_) if f_.is_Add else (f"({nice(f_.base, True)})^{{{e(f_.exp)}}}" if f_.is_Pow and f_.base.is_Add else e(f_))
        return out
    if v.is_Pow and v.base.is_Add:
        return f"({nice(v.base, True)})^{{{e(v.exp)}}}"
    return e(v)


class Det:
    """A determinant written as coef * |M|, changed by row/column operations. Each step is checked:
    coef_before * |M_before| == coef_after * |M_after|."""

    def __init__(self, M, coef=1, lhs="D"):
        self.M = sp.Matrix(M)
        self.coef = sp.sympify(coef)
        self.lhs = lhs
        self.steps = []

    def tex(self):
        c = self.coef
        pre = "" if c == 1 else "-" if c == -1 else nice(c)
        return f"{pre}{mtex(self.M, True)}"

    def _record(self, prev_coef, prev, op_tex, en, ur):
        chk = f"expand(({py(prev_coef)})*{mpy(prev)}.det()) == expand(({py(self.coef)})*{mpy(self.M)}.det())"
        first = not self.steps
        self.steps.append(S((f"{self.lhs} = " if first else "= ") + (rf"{self.tex()}\quad ({op_tex})" if op_tex else self.tex()), en, ur, chk))

    def start(self, en="Write the determinant.", ur="مقطع لکھیں۔"):
        self.steps.append(S(f"{self.lhs} = {self.tex()}", en, ur))
        return self

    def _op(self, kind, i, terms, en, ur):
        prev, pc = self.M.copy(), self.coef
        name = "R" if kind == "R" else "C"
        if kind == "R":
            self.M[i, :] = (prev[i, :] + sum((k * prev[j, :] for j, k in terms), sp.zeros(1, prev.cols))).applyfunc(sp.expand)
        else:
            self.M[:, i] = (prev[:, i] + sum((k * prev[:, j] for j, k in terms), sp.zeros(prev.rows, 1))).applyfunc(sp.expand)
        s = f"{name}_{i + 1}"
        for j, k in terms:
            kk = sp.sympify(k)
            neg = kk.could_extract_minus_sign()
            ak = -kk if neg else kk
            s += f" {'-' if neg else '+'} {'' if ak == 1 else (e(ak) if (ak.is_number or ak.is_Symbol) else p(ak))}{name}_{j + 1}"
        op = rf"{name}_{i + 1} \to {s}"
        self._record(pc, prev, op, en or f"${op}$ does not change the value of the determinant.",
                     ur or f"${op}$ سے مقطع کی قیمت نہیں بدلتی۔")
        return self

    def row(self, i, terms, en=None, ur=None):
        return self._op("R", i, terms, en, ur)

    def col(self, i, terms, en=None, ur=None):
        return self._op("C", i, terms, en, ur)

    def common(self, kind, i, f, en=None, ur=None):
        """Take the factor f out of row/column i."""
        prev, pc = self.M.copy(), self.coef
        f = sp.sympify(f)
        if kind == "R":
            self.M[i, :] = (prev[i, :] / f).applyfunc(sp.cancel)
        else:
            self.M[:, i] = (prev[:, i] / f).applyfunc(sp.cancel)
        self.coef = pc * f
        nm = ("R" if kind == "R" else "C") + f"_{i + 1}"
        word = "row" if kind == "R" else "column"
        ft = nice(f, bare=True)
        self._record(pc, prev, rf"\text{{taking }} {ft} \text{{ common from }} {nm}",
                     en or f"Every entry of {word} {i + 1} has the factor ${ft}$; take it outside the determinant.",
                     ur or f"{'قطار' if kind == 'R' else 'کالم'} {i + 1} کے ہر رکن میں ${ft}$ مشترک ہے؛ اسے مقطع سے باہر لے آئیں۔")
        return self

    def times(self, kind, i, f, en=None, ur=None):
        """Multiply row/column i by f and divide outside by f."""
        prev, pc = self.M.copy(), self.coef
        f = sp.sympify(f)
        if kind == "R":
            self.M[i, :] = (prev[i, :] * f).applyfunc(sp.expand)
        else:
            self.M[:, i] = (prev[:, i] * f).applyfunc(sp.expand)
        self.coef = pc / f
        nm = ("R" if kind == "R" else "C") + f"_{i + 1}"
        self._record(pc, prev, rf"{nm} \to {e(f)}{nm}",
                     en or f"Multiply {'row' if kind == 'R' else 'column'} {i + 1} by ${e(f)}$ and divide the determinant by ${e(f)}$ to keep its value.",
                     ur or f"{'قطار' if kind == 'R' else 'کالم'} {i + 1} کو ${e(f)}$ سے ضرب دیں اور قیمت برقرار رکھنے کے لیے مقطع کو ${e(f)}$ سے تقسیم کریں۔")
        return self

    def swap(self, kind, i, j, en=None, ur=None):
        prev, pc = self.M.copy(), self.coef
        if kind == "R":
            self.M.row_swap(i, j)
        else:
            self.M.col_swap(i, j)
        self.coef = -pc
        nm = "R" if kind == "R" else "C"
        self._record(pc, prev, rf"{nm}_{{{i + 1}}} \leftrightarrow {nm}_{{{j + 1}}}",
                     en or "Interchanging two lines changes the sign of the determinant.",
                     ur or "دو قطاروں (یا کالموں) کی جگہ بدلنے سے مقطع کی علامت بدل جاتی ہے۔")
        return self

    def zero(self, reason_en, reason_ur):
        self.steps.append(S(rf"{self.lhs} = 0", reason_en, reason_ur, f"expand({mpy(self.M)}.det()) == 0"))
        return self

    def expand(self, row=None, rhs=None, rhs_tex=None):
        if row is None:                                   # the row with the most zeros
            row = max(range(self.M.rows), key=lambda i: (sum(1 for v in self.M.row(i) if v == 0), -i))
        s, v = det_expand(self.M, self.lhs, row=row, factor=self.coef)
        if rhs is not None:
            tgt = rhs_tex or e(rhs)
            if not s[-1]["math"].endswith(f"= {tgt}"):
                s[-1]["math"] += rf" = {tgt}"
            s[-1]["check"].append(f"expand(({py(self.coef)})*{mpy(self.M)}.det() - ({py(rhs)})) == 0")
        self.steps += s
        return self
