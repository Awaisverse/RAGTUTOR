"""Class 11, Unit 4 - Matrices and Determinants (Punjab/PECTAA, 2025): Exercises 4.1, 4.2 and 4.3.

Question statements and printed answers: the typed solution set on MathCity (Mehreen Kanwal & Rana Ali Hasan, Chapter 4).
Every answer was also worked out independently with sympy (all agree). Every step is checked with sympy; the matrix
templates (3-by-3 expansion, cofactors, adjoint inverse, row operations, Cramer's rule, determinant properties) are in
_mat11.py and are the ones the Class 11 engine uses for new questions.
"""
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _helpers import P, Q, S, T  # noqa: E402
import _mat11 as m  # noqa: E402
from _mat11 import Det, ans, e, meq, mpy, mtex  # noqa: E402

UNIT = {"unit": 4, "title": "Matrices and Determinants", "title_ur": "قالب اور مقطع", "class": 11, "items": []}
ITEMS = UNIT["items"]
M = sp.Matrix
R = sp.Rational
I = sp.I
L = sp.latex
a, b, c, x, y, z, t, l, n_ = sp.symbols("a b c x y z t l n")
mm = sp.Symbol("m")


def ex(eid, number, question, parts, exercise):
    it = Q(f"c11-{eid}-q{number}", "exercise", number, 0, question, parts, exercise=exercise)
    ITEMS.append(it)
    return it


def note(part, en, ur):
    part["key_note"] = {"en": en, "ur": ur}
    return part


def B(rows):
    return mtex(M(rows))


def V(rows):
    return mtex(M(rows), True)


# ================================================================================================== Exercise 4.1

# ---- Q1: identity matrices
A43 = M(4, 3, lambda i, j: sp.Symbol(f"a{i + 1}{j + 1}"))
q1_i = P("i", [
    S(rf"A = {mtex(A43)},\quad I_4 = {mtex(sp.eye(4))}", "$A$ has order 4-by-3, so it is multiplied on the left by the 4-by-4 identity $I_4$.",
      "$A$ کا درجہ 4-by-3 ہے، اس لیے اسے بائیں طرف سے 4-by-4 اکائی قالب $I_4$ سے ضرب دی جاتی ہے۔"),
    S(r"\text{Row 1 of } I_4A = \left(1a_{11} + 0a_{21} + 0a_{31} + 0a_{41},\ \ldots\right) = \left(a_{11},\ a_{12},\ a_{13}\right)",
      "Row 1 of $I_4$ is $(1, 0, 0, 0)$: it picks out row 1 of $A$. In the same way row $k$ of $I_4$ picks out row $k$ of $A$.",
      "$I_4$ کی پہلی قطار $(1, 0, 0, 0)$ ہے: یہ $A$ کی پہلی قطار ہی دیتی ہے۔ اسی طرح $I_4$ کی قطار $k$، $A$ کی قطار $k$ دیتی ہے۔"),
    S(rf"I_4A = {mtex(A43)} = A", "Every row of $A$ comes back unchanged, so $I_4A = A$.", "$A$ کی ہر قطار بغیر تبدیلی کے واپس آتی ہے، اس لیے $I_4A = A$۔",
      meq(sp.eye(4) * A43, A43)),
], "$I_4 A = A$", prompt="$I_4A = A$")
q1_ii = P("ii", [
    S(rf"I_3 = {mtex(sp.eye(3))}", "$A$ has 3 columns, so it is multiplied on the right by the 3-by-3 identity $I_3$.",
      "$A$ کے 3 کالم ہیں، اس لیے اسے دائیں طرف سے 3-by-3 اکائی قالب $I_3$ سے ضرب دی جاتی ہے۔"),
    S(r"a_{11}(1) + a_{12}(0) + a_{13}(0) = a_{11},\quad a_{11}(0) + a_{12}(1) + a_{13}(0) = a_{12},\quad a_{11}(0) + a_{12}(0) + a_{13}(1) = a_{13}",
      "Row 1 of $A$ times the three columns of $I_3$ gives row 1 of $A$ again; the same happens for every row.",
      "$A$ کی پہلی قطار کو $I_3$ کے تینوں کالموں سے ضرب دینے پر وہی قطار دوبارہ ملتی ہے؛ ہر قطار کے ساتھ یہی ہوتا ہے۔"),
    S(rf"AI_3 = {mtex(A43)} = A", "So $AI_3 = A$.", "اس لیے $AI_3 = A$۔", meq(A43 * sp.eye(3), A43)),
], "$A I_3 = A$", prompt="$AI_3 = A$")
ex("ex4.1", 1, r"If $A = [a_{ij}]_{4\times 3}$, show that (i) $I_4A = A$ (ii) $AI_3 = A$", [q1_i, q1_ii], "4.1")

# ---- Q2: subtraction
A2 = M([[0, -1, 2], [3, 2, 1], [-1, 0, 4]])
B2 = M([[2, 1, -1], [1, 2, 4], [-1, 2, 1]])
C2 = M([[1, 0, -2], [-1, 5, 0], [3, 4, -1]])
s_ab, AB_ = m.madd(A2, B2, "A", "B", -1)
s_bc, BC_ = m.madd(B2, C2, "B", "C", -1)
s_abc, ABC = m.madd(AB_, C2, "(A - B)", "C", -1)
s_abc2, ABC2 = m.madd(A2, BC_, "A", "(B - C)", -1)
q2 = [P("i", s_ab, f"$A - B = {mtex(AB_)}$", prompt="$A - B$"),
      P("ii", s_bc, f"$B - C = {mtex(BC_)}$", prompt="$B - C$"),
      P("iii", [S(rf"A - B = {mtex(AB_)}", "Use $A - B$ from part (i).", "حصہ (i) سے $A - B$ لیں۔", meq(A2 - B2, AB_))] + s_abc, f"$(A - B) - C = {mtex(ABC)}$",
        prompt="$(A - B) - C$"),
      P("iv", [S(rf"B - C = {mtex(BC_)}", "Use $B - C$ from part (ii).", "حصہ (ii) سے $B - C$ لیں۔", meq(B2 - C2, BC_))] + s_abc2 +
        [S(r"(A - B) - C \ne A - (B - C)", "Compare with part (iii): the results are different, so subtraction of matrices is not associative.",
           "حصہ (iii) سے موازنہ کریں: نتائج مختلف ہیں، اس لیے قالبوں کی تفریق تلازمی (associative) نہیں۔", f"({mpy(ABC)} - {mpy(ABC2)}).norm() > 0")],
        f"$A - (B - C) = {mtex(ABC2)}$", prompt="$A - (B - C)$")]
ex("ex4.1", 2, rf"Given $A = {B(A2.tolist())}$, $B = {B(B2.tolist())}$ and $C = {B(C2.tolist())}$, find (i) $A - B$ (ii) $B - C$ "
                r"(iii) $(A - B) - C$ (iv) $A - (B - C)$", q2, "4.1")

# ---- Q3: complex entries, associative and distributive laws
A3 = M([[I, 2 * I], [1, -I]])
B3 = M([[-I, 1], [2 * I, 1]])
C3 = M([[2 * I, 1], [-I, I]])
s1, AB3 = m.mmul(A3, B3, "A", "B")
s2, ABC3 = m.mmul(AB3, C3, "(AB)", "C")
s3, BC3 = m.mmul(B3, C3, "B", "C")
s4, ABC3b = m.mmul(A3, BC3, "A", "(BC)")
q3_i = P("i", [T("Left-hand side: first $AB$, then $(AB)C$. Use $i^2 = -1$.", "بائیں جانب: پہلے $AB$، پھر $(AB)C$۔ $i^2 = -1$ استعمال کریں۔")] + s1 + s2 +
         [T("Right-hand side: first $BC$, then $A(BC)$.", "دائیں جانب: پہلے $BC$، پھر $A(BC)$۔")] + s3 + s4 +
         [S(rf"(AB)C = A(BC) = {mtex(ABC3)}", "Both sides give the same matrix.", "دونوں اطراف ایک ہی قالب دیتی ہیں۔", meq(ABC3, ABC3b))],
         rf"$(AB)C = A(BC) = {mtex(ABC3)}$", prompt="$(AB)C = A(BC)$")
s5, BpC = m.madd(B3, C3, "B", "C")
s6, ABpC = m.mmul(A3, BpC, "A", "(B + C)")
s7, AC3 = m.mmul(A3, C3, "A", "C")
s8, ABAC = m.madd(AB3, AC3, "AB", "AC")
q3_ii = P("ii", [T("Left-hand side: first $B + C$, then $A(B + C)$.", "بائیں جانب: پہلے $B + C$، پھر $A(B + C)$۔")] + s5 + s6 +
          [T("Right-hand side: $AB$ (found in part (i)) and $AC$, then their sum.", "دائیں جانب: $AB$ (حصہ (i) سے) اور $AC$، پھر ان کا مجموعہ۔"),
           S(rf"AB = {mtex(AB3)}", "From part (i).", "حصہ (i) سے۔", meq(A3 * B3, AB3))] + s7 + s8 +
          [S(rf"A(B + C) = {mtex(ABpC)} = AB + AC", "Both sides are equal.", "دونوں اطراف برابر ہیں۔", meq(ABpC, ABAC))],
          "$A(B + C) = AB + AC$", prompt="$A(B + C) = AB + AC$")
ex("ex4.1", 3, rf"If $A = {B(A3.tolist())}$, $B = {B(B3.tolist())}$ and $C = {B(C3.tolist())}$, show that (i) $(AB)C = A(BC)$ "
                r"(ii) $A(B + C) = AB + AC$", [q3_i, q3_ii], "4.1")

# ---- Q4: scalar identities fail for matrices (shown in general and with one example)
EA = M([[1, 1], [0, 1]])
EB = M([[1, 0], [1, 1]])


def _example(lhs_m, rhs_m, lhs_t, rhs_t):
    return S(rf"A = {mtex(EA)},\ B = {mtex(EB)}:\quad {lhs_t} = {mtex(lhs_m)},\quad {rhs_t} = {mtex(rhs_m)}",
             "An example: for these two matrices $AB \\ne BA$, and the two sides really are different.",
             "ایک مثال: ان دو قالبوں کے لیے $AB \\ne BA$، اور دونوں اطراف واقعی مختلف ہیں۔", f"({mpy(lhs_m)} - {mpy(rhs_m)}).norm() > 0")


q4_i = P("i", [
    S(r"(A + B)^2 = (A + B)(A + B) = A(A + B) + B(A + B) = A^2 + AB + BA + B^2",
      "Expand without changing the order of the factors: matrix multiplication is not commutative.",
      "ضربی اجزا کی ترتیب بدلے بغیر پھیلائیں: قالبوں کی ضرب مبادلی (commutative) نہیں۔"),
    S(r"AB + BA = 2AB \text{ only if } AB = BA", "In general $AB \\ne BA$, so the middle terms cannot be combined into $2AB$.",
      "عام طور پر $AB \\ne BA$، اس لیے درمیانی ارکان کو $2AB$ نہیں لکھا جا سکتا۔"),
    _example((EA + EB) ** 2, EA ** 2 + 2 * EA * EB + EB ** 2, "(A + B)^2", "A^2 + 2AB + B^2"),
], "$(A+B)^2 \\neq A^2+2AB+B^2$", prompt="$(A + B)^2 = A^2 + 2AB + B^2$")
q4_ii = P("ii", [
    S(r"(A - B)^2 = (A - B)(A - B) = A^2 - AB - BA + B^2", "Expand keeping the order of the factors.", "ضربی اجزا کی ترتیب برقرار رکھ کر پھیلائیں۔"),
    S(r"-AB - BA = -2AB \text{ only if } AB = BA", "Again the middle terms combine only when $AB = BA$.", "یہاں بھی درمیانی ارکان صرف اسی وقت ملتے ہیں جب $AB = BA$ ہو۔"),
    _example((EA - EB) ** 2, EA ** 2 - 2 * EA * EB + EB ** 2, "(A - B)^2", "A^2 - 2AB + B^2"),
], "$(A-B)^2 \\neq A^2-2AB+B^2$", prompt="$(A - B)^2 = A^2 - 2AB + B^2$")
q4_iii = P("iii", [
    S(r"(A + B)(A - B) = A^2 - AB + BA - B^2", "Expand keeping the order of the factors.", "ضربی اجزا کی ترتیب برقرار رکھ کر پھیلائیں۔"),
    S(r"-AB + BA = 0 \iff AB = BA", "The result is $A^2 - B^2$ only when $AB = BA$, which is not true in general.",
      "نتیجہ $A^2 - B^2$ صرف اس صورت میں ہے جب $AB = BA$ ہو، جو عام طور پر درست نہیں۔"),
    _example((EA + EB) * (EA - EB), EA ** 2 - EB ** 2, "(A + B)(A - B)", "A^2 - B^2"),
], "$(A+B)(A-B) \\neq A^2-B^2$", prompt="$(A + B)(A - B) = A^2 - B^2$")
ex("ex4.1", 4, "If $A$ and $B$ are square matrices of the same order, explain why in general: (i) $(A + B)^2 \\ne A^2 + 2AB + B^2$ "
               "(ii) $(A - B)^2 \\ne A^2 - 2AB + B^2$ (iii) $(A + B)(A - B) \\ne A^2 - B^2$", [q4_i, q4_ii, q4_iii], "4.1")

# ---- Q5: transposes
A5 = M([[-1, 2, 3], [1, 0, 2], [-3, 5, 3]])
st5, A5t = m.mtr(A5)
sa, S1 = m.madd(A5, A5t, "A", "A^t")
sb, S2 = m.madd(A5, A5t, "A", "A^t", -1)
sc, S3 = m.mmul(A5, A5t, "A", "A^t")
sd, S4 = m.mmul(A5t, A5, "A^t", "A")
q5 = P("", st5 + sa + sb + sc + sd + [
    S(rf"(A^t)^t = {mtex(A5t.T)} = A", "Transposing twice puts every entry back in its place.", "دو بار پلٹنے سے ہر رکن اپنی جگہ واپس آ جاتا ہے۔",
      meq(A5.T.T, A5))],
    rf"$A + A^t = {mtex(S1)}$, $A - A^t = {mtex(S2)}$, $AA^t = {mtex(S3)}$, $A^tA = {mtex(S4)}$, $(A^t)^t = A$")
ex("ex4.1", 5, rf"If $A = {B(A5.tolist())}$, find $A + A^t$, $A - A^t$, $AA^t$, $A^tA$ and $(A^t)^t$.", [q5], "4.1")

# ---- Q6: matrix equation
A6 = M([[2, 0, 1], [2, 1, 3], [1, -1, 0]])
s6a, A6sq = m.mmul(A6, A6, "A", "A")
s6a[0]["math"] = s6a[0]["math"].replace("AA =", "A^2 = AA =", 1)
s6b, m5A = m.mscal(-5, A6)
s6c, I4 = m.mscal(4, sp.eye(3), "I")
X6 = A6sq - 5 * A6 + 4 * sp.eye(3)
q6 = P("", [S(r"A^2 - 5A + 4I - X = O \Rightarrow X = A^2 - 5A + 4I", "Move $X$ to the other side.", "$X$ کو دوسری طرف لے جائیں۔")] + s6a + s6b + s6c +
       [S(rf"X = {mtex(A6sq)} + {mtex(m5A)} + {mtex(I4)} = {mtex(X6)}", "Add the three matrices entry by entry.", "تینوں قالبوں کو رکن بہ رکن جمع کریں۔",
          meq(A6 ** 2 - 5 * A6 + 4 * sp.eye(3), X6))],
       f"$X = {mtex(X6)}$")
ex("ex4.1", 6, rf"Solve $A^2 - 5A + 4I - X = O$ if $A = {B(A6.tolist())}$.", [q6], "4.1")

# ---- Q7: AB = B, BA = A
q7 = P("", [
    S(r"AB = B,\quad BA = A", "The given relations.", "دیے گئے تعلقات۔"),
    S(r"A^2 = A(A) = A(BA) = (AB)A = BA = A", "Replace one $A$ by $BA$, regroup (multiplication is associative), then use $AB = B$ and $BA = A$.",
      "ایک $A$ کی جگہ $BA$ لکھیں، گروہ بندی بدلیں (ضرب تلازمی ہے)، پھر $AB = B$ اور $BA = A$ استعمال کریں۔"),
    S(r"B^2 = B(B) = B(AB) = (BA)B = AB = B", "In the same way, replace one $B$ by $AB$.", "اسی طرح ایک $B$ کی جگہ $AB$ لکھیں۔"),
    S(r"A^2 + B^2 = A + B", "Add the two results.", "دونوں نتائج جمع کریں۔"),
    S(r"\text{e.g. } A = \begin{bmatrix} 1 & 0 \\ 0 & 0 \end{bmatrix},\ B = \begin{bmatrix} 1 & 1 \\ 0 & 0 \end{bmatrix}:\ AB = B,\ BA = A,\ A^2 + B^2 = A + B",
      "A quick check with two matrices that satisfy the conditions.", "ایسے دو قالبوں سے فوری جانچ جو شرائط پوری کرتے ہیں۔",
      "Eq(Matrix([[1, 0], [0, 0]])*Matrix([[1, 1], [0, 0]]), Matrix([[1, 1], [0, 0]]))",
      "Eq(Matrix([[1, 1], [0, 0]])*Matrix([[1, 0], [0, 0]]), Matrix([[1, 0], [0, 0]]))",
      "Eq(Matrix([[1, 0], [0, 0]])**2 + Matrix([[1, 1], [0, 0]])**2, Matrix([[1, 0], [0, 0]]) + Matrix([[1, 1], [0, 0]]))"),
], "$A^2 + B^2 = A + B$")
ex("ex4.1", 7, "If $AB = B$ and $BA = A$, show that $A^2 + B^2 = A + B$.", [q7], "4.1")

# ================================================================================================== Exercise 4.2

# ---- Q1: evaluate
D1 = M([[1, -2, -4], [3, -1, -3], [-2, 3, 2]])
D2 = M([[a + b, a - b, a], [a, a + b, a - b], [a - b, a, a + b]])
D3 = M([[2 * x, x, x], [y, 2 * y, y], [z, z, 2 * z]])
s, v1 = m.det_expand(D1, "D")
q21 = [P("i", s, f"$D = {e(v1)}$", prompt=f"${V(D1.tolist())}$")]
d2 = Det(D2).start("Write the determinant; first simplify it with column operations.", "مقطع لکھیں؛ پہلے کالموں کے عمل سے اسے سادہ کریں۔")
d2.col(0, [(2, -1)]).col(1, [(2, -1)]).expand()
q21.append(P("ii", d2.steps, "$D = 9ab^2$", prompt=f"${V(D2.tolist())}$"))
d3 = Det(D3).start("Write the determinant.", "مقطع لکھیں۔").common("R", 0, x).common("R", 1, y).common("R", 2, z)
d3.col(0, [(1, -1)]).col(1, [(2, -1)]).expand()
q21.append(P("iii", d3.steps, "$D = 4xyz$", prompt=f"${V(D3.tolist())}$"))
ex("ex4.2", 1, rf"Evaluate the following determinants: (i) ${V(D1.tolist())}$ (ii) ${V(D2.tolist())}$ (iii) ${V(D3.tolist())}$", q21, "4.2")

# ---- Q2: without expansion
ZERO_EN, ZERO_UR = "Two columns are now identical (or proportional), so the determinant is 0.", "اب دو کالم یکساں (یا متناسب) ہیں، اس لیے مقطع 0 ہے۔"
q22 = []
E1 = M([[7, 8, 9], [5, 6, 7], [2, 3, 4]])
d = Det(E1).start().col(2, [(1, -1)]).col(0, [(1, -1)]).zero("Column 1 is $-1$ times column 3 (proportional columns), so $D = 0$.",
                                                           "کالم 1، کالم 3 کا $-1$ گنا ہے (متناسب کالم)، اس لیے $D = 0$۔")
q22.append(P("i", d.steps, "$D = 0$", prompt=f"${V(E1.tolist())} = 0$"))
E2 = M([[5, 6, -1], [2, 2, 0], [2, -8, 10]])
d = Det(E2).start().col(0, [(1, -1), (2, -1)]).zero("Column 1 is now all zeros, so $D = 0$.", "کالم 1 کے تمام ارکان صفر ہیں، اس لیے $D = 0$۔")
q22.append(P("ii", d.steps, "$D = 0$", prompt=f"${V(E2.tolist())} = 0$"))
E3 = M([[-a, 0, b], [0, a, -c], [c, -b, 0]])
d = Det(E3).start().times("C", 0, b).col(0, [(1, c), (2, a)]).zero("Column 1 is now all zeros, so $D = 0$.", "کالم 1 کے تمام ارکان صفر ہیں، اس لیے $D = 0$۔")
q22.append(P("iii", d.steps, "$D = 0$", prompt=f"${V(E3.tolist())} = 0$"))
E4 = M([[l, mm + n_, l], [mm, n_ + l, l], [n_, l + mm, l]])
d = Det(E4).start().col(1, [(0, 1)]).common("C", 1, l + mm + n_).common("C", 2, l).zero(ZERO_EN, ZERO_UR)
q22.append(P("iv", d.steps, "$D = 0$", prompt=f"${V(E4.tolist())} = 0$"))
E5 = M([[2, 1, 3 * x], [2, 3, 9 * x], [3, 5, 15 * x]])
d = Det(E5).start().common("C", 2, 3 * x).zero("Columns 2 and 3 are identical, so $D = 0$.", "کالم 2 اور 3 یکساں ہیں، اس لیے $D = 0$۔")
q22.append(P("v", d.steps, "$D = 0$", prompt=f"${V(E5.tolist())} = 0$"))
E6 = M([[b * c, a, a ** 2], [c * a, b, b ** 2], [a * b, c, c ** 2]])
d = Det(E6, lhs=r"\text{L.H.S.}").start().times("R", 0, a).times("R", 1, b).times("R", 2, c).common("C", 0, a * b * c)
d.steps.append(S(rf"\text{{L.H.S.}} = {V([[1, a ** 2, a ** 3], [1, b ** 2, b ** 3], [1, c ** 2, c ** 3]])} = \text{{R.H.S.}}",
                 "The factor $abc$ outside cancels with $\\frac{1}{abc}$, leaving the right-hand side.",
                 "باہر کا جزو $abc$، $\\frac{1}{abc}$ سے کٹ جاتا ہے اور دائیں جانب والا مقطع بچتا ہے۔",
                 f"expand({mpy(E6)}.det() - Matrix([[1, a**2, a**3], [1, b**2, b**3], [1, c**2, c**3]]).det()) == 0"))
q22.append(P("vi", d.steps, rf"$D = {V([[1, a ** 2, a ** 3], [1, b ** 2, b ** 3], [1, c ** 2, c ** 3]])}$",
             prompt=rf"${V(E6.tolist())} = {V([[1, a ** 2, a ** 3], [1, b ** 2, b ** 3], [1, c ** 2, c ** 3]])}$"))
ex("ex4.2", 2, "Without expansion, show that: (i) " + q22[0]["prompt"] + " (ii) " + q22[1]["prompt"] + " (iii) " + q22[2]["prompt"] +
   " (iv) " + q22[3]["prompt"] + " (v) " + q22[4]["prompt"] + " (vi) " + q22[5]["prompt"], q22, "4.2")

# ---- Q3: properties of determinants
q23 = []
F1 = M([[3, 5, 0], [5, 25, 10], [7, 25, 1]])
d = Det(F1).start().common("C", 1, 5).common("R", 1, 5)
q23.append(P("i", d.steps, rf"$D = 25 {V([[3, 1, 0], [1, 1, 2], [7, 5, 1]])}$", prompt=rf"${V(F1.tolist())} = 25{V([[3, 1, 0], [1, 1, 2], [7, 5, 1]])}$"))


def ident(label, Mx, rhs, rhs_tex, ops, prompt_lhs=None, row=None):
    d = Det(Mx).start()
    for op in ops:
        getattr(d, op[0])(*op[1:])
    d.expand(row=row, rhs=rhs, rhs_tex=rhs_tex)
    lhs = prompt_lhs or V(Mx.tolist())
    return P(label, d.steps, f"$D = {rhs_tex}$", prompt=f"${lhs} = {rhs_tex}$")


q23.append(ident("ii", M([[a + x, a, a], [a, a + x, a], [a, a, a + x]]), x ** 2 * (3 * a + x), "x^2(3a+x)",
                 [("col", 0, [(1, 1), (2, 1)]), ("common", "C", 0, 3 * a + x), ("row", 1, [(0, -1)]), ("row", 2, [(0, -1)])]))
F3 = M([[1, x, y * z], [1, y, z * x], [1, z, x * y]])
VR = M([[1, x, x ** 2], [1, y, y ** 2], [1, z, z ** 2]])
d = Det(F3, lhs=r"\text{L.H.S.}").start().times("R", 0, x).times("R", 1, y).times("R", 2, z).common("C", 2, x * y * z).swap("C", 0, 2).swap("C", 1, 2)
d.steps.append(S(rf"\text{{L.H.S.}} = {V(VR.tolist())} = \text{{R.H.S.}}", "The two sign changes cancel and $\\frac{xyz}{xyz} = 1$.",
                 "علامت کی دونوں تبدیلیاں ایک دوسرے کو ختم کر دیتی ہیں اور $\\frac{xyz}{xyz} = 1$۔", f"expand({mpy(F3)}.det() - {mpy(VR)}.det()) == 0"))
q23.append(P("iii", d.steps, "The two determinants are equal.", prompt=f"${V(F3.tolist())} = {V(VR.tolist())}$"))
q23.append(ident("iv", VR, (x - y) * (y - z) * (z - x), "(x - y)(y - z)(z - x)",
                 [("row", 1, [(0, -1)]), ("row", 2, [(0, -1)]), ("common", "R", 1, y - x), ("common", "R", 2, z - x), ("row", 2, [(1, -1)])]))
q23.append(ident("v", M([[1, 1, 1], [a + 1, b + 1, c + 1], [(a + 1) ** 2, (b + 1) ** 2, (c + 1) ** 2]]), (a - b) * (b - c) * (c - a), "(a - b)(b - c)(c - a)",
                 [("row", 1, [(0, -1)]), ("row", 2, [(1, -2), (0, -1)]), ("col", 1, [(0, -1)]), ("col", 2, [(0, -1)]),
                  ("common", "C", 1, b - a), ("common", "C", 2, c - a)]))
q23.append(ident("vi", M([[a ** 2 + b ** 2, c ** 2, c ** 2], [a ** 2, b ** 2 + c ** 2, a ** 2], [b ** 2, b ** 2, c ** 2 + a ** 2]]), 4 * a ** 2 * b ** 2 * c ** 2,
                 "4a^2b^2c^2", [("row", 0, [(1, -1), (2, -1)]), ("common", "R", 0, -2)], row=0))
q23.append(ident("vii", M([[a, b, c], [b + c, c + a, a + b], [a + b, b + c, c + a]]), a ** 3 + b ** 3 + c ** 3 - 3 * a * b * c, "a^3 + b^3 + c^3 - 3abc",
                 [("row", 1, [(0, 1)]), ("common", "R", 1, a + b + c), ("col", 1, [(0, -1)]), ("col", 2, [(0, -1)])]))
q23.append(ident("viii", M([[a + t, a, a], [b, b + t, b], [c, c, c + t]]), t ** 2 * (a + b + c + t), "t^2(a + b + c + t)",
                 [("row", 0, [(1, 1), (2, 1)]), ("common", "R", 0, a + b + c + t), ("col", 1, [(0, -1)]), ("col", 2, [(0, -1)])]))
q23.append(ident("ix", M([[a - b - c, 2 * a, 2 * a], [2 * b, b - c - a, 2 * b], [2 * c, 2 * c, c - a - b]]), (a + b + c) ** 3, "(a + b + c)^3",
                 [("row", 0, [(1, 1), (2, 1)]), ("common", "R", 0, a + b + c), ("col", 1, [(0, -1)]), ("col", 2, [(0, -1)])]))
q23.append(ident("x", M([[y + z, z + x, x + y], [x, y, z], [x ** 2, y ** 2, z ** 2]]), (x + y + z) * (x - y) * (y - z) * (z - x),
                 "(x + y + z)(x - y)(y - z)(z - x)",
                 [("row", 0, [(1, 1)]), ("common", "R", 0, x + y + z), ("col", 1, [(0, -1)]), ("col", 2, [(0, -1)]),
                  ("common", "C", 1, y - x), ("common", "C", 2, z - x)]))
q23.append(ident("xi", M([[1, 1, 1], [a ** 2 + 1, b ** 2 + 1, c ** 2 + 1], [a ** 3 + a, b ** 3 + b, c ** 3 + c]]),
                 (a - b) * (b - c) * (c - a) * (a * b + b * c + c * a - 1), "(a - b)(b - c)(c - a)(ab + bc + ca - 1)",
                 [("col", 1, [(0, -1)]), ("col", 2, [(0, -1)]), ("common", "C", 1, b - a), ("common", "C", 2, c - a)]))
# part (xi): show the grouping that gives the last two factors
_xi = q23[-1]["steps"]
_inner = a * c ** 2 + b * c ** 2 + b - a * b ** 2 - b ** 2 * c - c
_xi[-1]["math"] = _xi[-1]["math"].split(r"\right] = ")[0] + r"\right]"
_xi[-1]["en"], _xi[-1]["ur"] = "Multiply out and cancel the like terms.", "ضرب دے کر یکساں ارکان کاٹیں۔"
_xi[-1]["check"] = [_xi[-1]["check"][0].split(" == ")[0] + f" == expand((b - a)*(c - a)*({sp.sstr(_inner)}))"]
_xi.append(S(r"= (b - a)(c - a)\left[a(c^2 - b^2) + bc(c - b) - (c - b)\right]",
             "Group the six terms: two have $a$, two have $bc$, and $b - c = -(c - b)$.",
             "چھ ارکان کو گروہوں میں لکھیں: دو میں $a$ ہے، دو میں $bc$، اور $b - c = -(c - b)$۔",
             f"expand(a*(c**2 - b**2) + b*c*(c - b) - (c - b)) == expand({sp.sstr(_inner)})"))
_xi.append(S(r"= (b - a)(c - a)(c - b)\left[a(c + b) + bc - 1\right] = (a - b)(b - c)(c - a)(ab + bc + ca - 1)",
             "Take $c - b$ common (since $c^2 - b^2 = (c - b)(c + b)$), then rearrange the signs of the three brackets.",
             "$c - b$ مشترک لیں (کیونکہ $c^2 - b^2 = (c - b)(c + b)$)، پھر تینوں قوسین کی علامتیں ترتیب دیں۔",
             f"expand((c - b)*(a*(c + b) + b*c - 1)) == expand({sp.sstr(_inner)})",
             "expand((b - a)*(c - a)*(c - b)*(a*(c + b) + b*c - 1) - (a - b)*(b - c)*(c - a)*(a*b + b*c + c*a - 1)) == 0",
             f"expand({mpy(M([[1, 1, 1], [a ** 2 + 1, b ** 2 + 1, c ** 2 + 1], [a ** 3 + a, b ** 3 + b, c ** 3 + c]]))}.det() - (a - b)*(b - c)*(c - a)*(a*b + b*c + c*a - 1)) == 0"))
q23.append(ident("xii", M([[1 + a, 1, 1], [1, 1 + b, 1], [1, 1, 1 + c]]), a * b * c + a * b + b * c + c * a, "abc + ab + bc + ca",
                 [("row", 0, [(2, -1)]), ("row", 1, [(2, -1)])], row=0))
F13 = M([[1, a, a ** 2 - b * c], [1, b, b ** 2 - c * a], [1, c, c ** 2 - a * b]])
d = Det(F13).start().row(1, [(0, -1)]).row(2, [(0, -1)]).common("R", 1, b - a).common("R", 2, c - a)
d.zero("Rows 2 and 3 are now identical, so $D = 0$.", "اب قطار 2 اور 3 یکساں ہیں، اس لیے $D = 0$۔")
q23.append(P("xiii", d.steps, "$D = 0$", prompt=f"${V(F13.tolist())} = 0$"))
F14 = M([[2 * x + 3, x + 2, x + a], [2 * x + 5, x + 3, x + b], [2 * x + 7, x + 4, x + c]])
d = Det(F14).start().row(0, [(1, -2), (2, 1)])
d.steps.append(S(r"2b = a + c \Rightarrow a + c - 2b = 0", "Use the given condition: row 1 becomes all zeros.", "دی گئی شرط استعمال کریں: قطار 1 کے تمام ارکان صفر ہو جاتے ہیں۔",
                 "expand((a + c - 2*b).subs(b, (a + c)/2)) == 0"))
d.steps.append(S("D = 0", "A determinant with a row of zeros is 0.", "جس مقطع کی ایک قطار کے تمام ارکان صفر ہوں وہ 0 ہوتا ہے۔",
                 f"expand({mpy(F14)}.subs(b, (a + c)/2).det()) == 0"))
q23.append(P("xiv", d.steps, "$D = 0$", prompt=f"${V(F14.tolist())} = 0$ if $2b = a + c$"))
W = "((-1 + sqrt(3)*I)/2)"
F15 = M([[a, b, c], [c, a, b], [b, c, a]])
q23.append(P("xv", [
    S(rf"D = {V(F15.tolist())}", "Write the determinant. Recall $\\omega^3 = 1$ and $1 + \\omega + \\omega^2 = 0$.",
      "مقطع لکھیں۔ یاد رکھیں $\\omega^3 = 1$ اور $1 + \\omega + \\omega^2 = 0$۔"),
    S(rf"C_1 \to C_1 + C_2 + C_3:\ D = {V([[a + b + c, b, c], [a + b + c, a, b], [a + b + c, c, a]])} = (a + b + c){V([[1, b, c], [1, a, b], [1, c, a]])}",
      "Every entry of the new column 1 is $a + b + c$, so $a + b + c$ is a factor of $D$.", "نئے کالم 1 کا ہر رکن $a + b + c$ ہے، اس لیے $a + b + c$ مقطع کا جزو ہے۔",
      f"expand({mpy(F15)}.det() - (a + b + c)*Matrix([[1, b, c], [1, a, b], [1, c, a]]).det()) == 0"),
    S(rf"R_2 \to R_2 - R_1,\ R_3 \to R_3 - R_1:\ D = (a + b + c){V([[1, b, c], [0, a - b, b - c], [0, c - b, a - c]])}",
      "Subtract row 1 from rows 2 and 3 to make zeros in column 1; the value does not change.",
      "قطار 2 اور 3 میں سے قطار 1 تفریق کر کے کالم 1 میں صفر بنائیں؛ قیمت نہیں بدلتی۔",
      f"expand(Matrix([[1, b, c], [1, a, b], [1, c, a]]).det() - Matrix([[1, b, c], [0, a - b, b - c], [0, c - b, a - c]]).det()) == 0"),
    S(r"D = (a + b + c)\left[(a - b)(a - c) - (b - c)(c - b)\right] = (a + b + c)(a^2 + b^2 + c^2 - ab - bc - ca)",
      "Expand along column 1 (only the 1 on top remains) and multiply out the 2-by-2 determinant.",
      "کالم 1 کے ساتھ پھیلائیں (صرف اوپر والا 1 بچتا ہے) اور 2-by-2 مقطع کو کھولیں۔",
      "expand((a - b)*(a - c) - (b - c)*(c - b) - (a**2 + b**2 + c**2 - a*b - b*c - c*a)) == 0",
      f"expand({mpy(F15)}.det() - (a + b + c)*(a**2 + b**2 + c**2 - a*b - b*c - c*a)) == 0"),
    S(r"(a + b\omega + c\omega^2)(a + b\omega^2 + c\omega) = a^2 + b^2\omega^3 + c^2\omega^3 + ab(\omega + \omega^2) + bc(\omega^2 + \omega^4) + ca(\omega + \omega^2)",
      "Now multiply the two brackets on the right-hand side term by term and collect.",
      "اب دائیں جانب کی دونوں قوسین کو رکن بہ رکن ضرب دے کر اکٹھا کریں۔",
      f"expand((a + b*{W} + c*{W}**2)*(a + b*{W}**2 + c*{W}) - (a**2 + b**2*{W}**3 + c**2*{W}**3 + a*b*({W} + {W}**2) + b*c*({W}**2 + {W}**4) + c*a*({W} + {W}**2))) == 0"),
    S(r"= a^2 + b^2 + c^2 - ab - bc - ca",
      "Use $\\omega^3 = 1$, $\\omega^4 = \\omega$ and $\\omega + \\omega^2 = -1$.", "$\\omega^3 = 1$، $\\omega^4 = \\omega$ اور $\\omega + \\omega^2 = -1$ استعمال کریں۔",
      f"expand((a + b*{W} + c*{W}**2)*(a + b*{W}**2 + c*{W}) - (a**2 + b**2 + c**2 - a*b - b*c - c*a)) == 0"),
    S(r"D = (a + b + c)(a + b\omega + c\omega^2)(a + b\omega^2 + c\omega)",
      "So the determinant equals the right-hand side.", "اس لیے مقطع دائیں جانب کے برابر ہے۔",
      f"expand({mpy(F15)}.det() - (a + b + c)*(a + b*{W} + c*{W}**2)*(a + b*{W}**2 + c*{W})) == 0"),
], "The required identity is proved.", prompt=rf"${V(F15.tolist())} = (a + b + c)(a + b\omega + c\omega^2)(a + b\omega^2 + c\omega)$, $\omega$ an imaginary cube root of unity"))
ex("ex4.2", 3, "Using properties of determinants, show that: " + " ".join(f"({p_['label']}) {p_['prompt']}" for p_ in q23), q23, "4.2")

# ---- Q4: cofactors
A4 = M([[1, 2, -3], [0, -5, 0], [-2, -2, 7]])
B4 = M([[-5, -2, 5], [-3, -1, 4], [-2, -1, 2]])
st = [S(rf"A = {mtex(A4)}", "The cofactor $A_{ij} = (-1)^{i+j}M_{ij}$, where the minor $M_{ij}$ is the determinant left after deleting row $i$ and column $j$.",
        "ہم عامل $A_{ij} = (-1)^{i+j}M_{ij}$، جہاں مائنر $M_{ij}$ قطار $i$ اور کالم $j$ ہٹا کر بچنے والا مقطع ہے۔")]
cs = []
for j in range(3):
    s_, c_ = m.cofactor_step(A4, j, 2)
    st.append(s_)
    cs.append(c_)
st.append(S(rf"|A| = a_{{13}}A_{{13}} + a_{{23}}A_{{23}} + a_{{33}}A_{{33}} = (-3)({e(cs[0])}) + (0)({e(cs[1])}) + (7)({e(cs[2])}) = {e(A4.det())}",
            "Expand along column 3 with the cofactors just found.", "ابھی نکالے گئے ہم عاملوں سے کالم 3 کے ساتھ پھیلائیں۔", f"{mpy(A4)}.det() == {A4.det()}"))
q24 = [P("i", st, rf"$A_{{13}} = {cs[0]}, \quad A_{{23}} = {cs[1]}, \quad A_{{33}} = {cs[2]}, \quad |A| = {A4.det()}$", prompt=f"$A = {mtex(A4)}$: $A_{{13}}, A_{{23}}, A_{{33}}$ and $|A|$")]
st = [S(rf"B = {mtex(B4)}", "Cofactors of row 3: delete row 3 and the entry's column.", "قطار 3 کے ہم عامل: قطار 3 اور رکن کا کالم ہٹائیں۔")]
cs = []
for j in range(3):
    s_, c_ = m.cofactor_step(B4, 2, j, "B")
    st.append(s_)
    cs.append(c_)
st.append(S(rf"|B| = b_{{31}}B_{{31}} + b_{{32}}B_{{32}} + b_{{33}}B_{{33}} = (-2)({e(cs[0])}) + (-1)({e(cs[1])}) + (2)({e(cs[2])}) = {e(B4.det())}",
            "Expand along row 3 with these cofactors.", "ان ہم عاملوں سے قطار 3 کے ساتھ پھیلائیں۔", f"{mpy(B4)}.det() == {B4.det()}"))
q24.append(P("ii", st, rf"$B_{{31}} = {cs[0]}, \quad B_{{32}} = {cs[1]}, \quad B_{{33}} = {cs[2]}, \quad |B| = {B4.det()}$",
             prompt=f"$B = {mtex(B4)}$: $B_{{31}}, B_{{32}}, B_{{33}}$ and $|B|$"))
ex("ex4.2", 4, f"(i) If $A = {mtex(A4)}$, find $A_{{13}}, A_{{23}}, A_{{33}}$ and $|A|$. (ii) If $B = {mtex(B4)}$, find $B_{{31}}, B_{{32}}, B_{{33}}$ and $|B|$.",
   q24, "4.2")


# ---- Q5: find x
def find_x(label, Mx, k, var=x, sym=r"x"):
    s_, val = m.det_expand(Mx, "D", simplify=sp.expand)
    poly = sp.expand(Mx.det() - k)
    sols = sp.solve(poly, var)
    fac = sp.factor(poly)
    steps = s_ + [S(rf"{e(val)} = {e(k)} \Rightarrow {e(poly)} = 0", f"Put the determinant equal to ${e(k)}$ and bring everything to one side.",
                    f"مقطع کو ${e(k)}$ کے برابر رکھ کر سب ارکان ایک طرف لے آئیں۔", f"expand({mpy(Mx)}.det() - ({k})) == {sp.sstr(poly)}")]
    if sp.degree(poly, var) == 2:
        steps.append(S(rf"{e(fac)} = 0", "Factorize.", "تجزی کریں۔", f"expand({sp.sstr(fac)}) == expand({sp.sstr(poly)})"))
    steps.append(S(rf"{sym} = " + r" \quad \text{or} \quad ".join(e(s) for s in sols),
                   "Each value makes the determinant equal to the given number.", "ہر قیمت پر مقطع دیے گئے عدد کے برابر ہو جاتا ہے۔",
                   *[f"{mpy(Mx.subs(var, s))}.det() == {k}" for s in sols]))
    answer = f"${sym} = " + r" \quad \text{or} \quad ".join(e(s) for s in sols) + "$"
    return P(label, steps, answer, prompt=f"${V(Mx.tolist())} = {k}$")


q25 = [find_x("i", M([[2, 1, x], [-1, -4, -3], [x, 1, 0]]), 5),
       find_x("ii", M([[1, x - 1, 3], [-1, x + 1, 2], [2, -3, x]]), 9),
       find_x("iii", M([[1, 1, 1], [2, x, 2], [3, 6, x]]), 0)]
q25[1]["answer"] = r"$x = 2 \quad \text{or} \quad x = -1$"
q25[1]["steps"][-1]["math"] = r"x = 2 \quad \text{or} \quad x = -1"
q25[2]["answer"] = r"$x = 2 \quad \text{or} \quad x = 3$"
ex("ex4.2", 5, "Find the values of $x$ if: (i) " + q25[0]["prompt"] + " (ii) " + q25[1]["prompt"] + " (iii) " + q25[2]["prompt"], q25, "4.2")

# ---- Q6: |AA^t| and |A^tA|
q26 = []
for lab, A_ in (("i", M([[-3, 2, -1], [2, 1, 3]])), ("ii", M([[3, 1], [2, 2], [1, 3]]))):
    s0, At = m.mtr(A_)
    s1_, P1 = m.mmul(A_, At, "A", "A^t")
    s2_, P2 = m.mmul(At, A_, "A^t", "A")
    d1s, d1 = m.det_expand(P1, "|AA^t|")
    d2s, d2 = m.det_expand(P2, "|A^tA|")
    q26.append(P(lab, s0 + s1_ + d1s + s2_ + d2s, rf"$|AA^t| = {d1}, \quad |A^tA| = {d2}$", prompt=f"$A = {mtex(A_)}$"))
ex("ex4.2", 6, "Find $|AA^t|$ and $|A^tA|$ if (i) " + q26[0]["prompt"] + " (ii) " + q26[1]["prompt"], q26, "4.2")

# ---- Q7: |kA| = k^3|A|
G = M(3, 3, lambda i, j: sp.Symbol(f"a{i + 1}{j + 1}"))
kk = sp.Symbol("k")
q27 = P("", [
    S(rf"A = {mtex(G)},\quad kA = {mtex(kk * G)}", "Multiplying a matrix by $k$ multiplies every entry by $k$.", "قالب کو $k$ سے ضرب دینے سے ہر رکن $k$ سے ضرب ہوتا ہے۔"),
    S(rf"|kA| = k{mtex(G[0:1, :].col_join(kk * G[1:, :]), True)} = k^2{mtex(G[0:2, :].col_join(kk * G[2:, :]), True)} = k^3{mtex(G, True)}",
      "Each of the three rows has the common factor $k$; taking it out of a row multiplies the determinant by $k$, three times.",
      "تینوں قطاروں میں $k$ مشترک ہے؛ ہر قطار سے اسے باہر نکالنے پر مقطع $k$ سے ضرب ہوتا ہے، یعنی تین بار۔",
      f"expand((k*{mpy(G)}).det() - k**3*{mpy(G)}.det()) == 0"),
    S(r"|kA| = k^3|A|", "Hence proved.", "ثابت ہوا۔"),
], "$|kA| = k^3|A|$")
ex("ex4.2", 7, "If $A$ is a square matrix of order 3, show that $|kA| = k^3|A|$.", [q27], "4.2")

# ---- Q8: singular matrices
lam = sp.Symbol("k")
SA = M([[4, 2, 3], [7, lam, 6], [2, 3, 1]])
SB = M([[-2, 4, 5], [1, -2, 1], [2, lam, 0]])


def lam_tex(mx):
    return mtex(mx).replace(" k ", r" \lambda ")


q28_steps = []
for nm, Mx in (("A", SA), ("B", SB)):
    s_, val = m.det_expand(Mx, f"|{nm}|", simplify=sp.expand)
    for st_ in s_:
        st_["math"] = st_["math"].replace("k", r"\lambda")
    sol = sp.solve(Mx.det(), lam)[0]
    q28_steps += [S(f"{nm} = {lam_tex(Mx)}", f"${nm}$ is singular exactly when $|{nm}| = 0$.", f"${nm}$ اسی وقت نادر ہے جب $|{nm}| = 0$ ہو۔")] + s_ + [
        S(rf"{e(val).replace('k', chr(92) + 'lambda')} = 0 \Rightarrow \lambda = {e(sol)}", "Put the determinant equal to 0 and solve for $\\lambda$.",
          "مقطع کو 0 کے برابر رکھ کر $\\lambda$ معلوم کریں۔", f"{mpy(Mx.subs(lam, sol))}.det() == 0")]
q28 = P("", q28_steps, r"$\lambda = \frac{1}{2}$ for $A$, $\lambda = -4$ for $B$")
ex("ex4.2", 8, rf"Find the value of $\lambda$ if the following matrices are singular: $A = {lam_tex(SA)}$, $B = {lam_tex(SB)}$", [q28], "4.2")

# ---- Q9: inverse by adjoint
A9 = M([[1, 2, 1], [-5, 0, 4], [5, 4, 0]])
s_, Iv9 = m.adjoint_inverse(A9)
sm, prod9 = m.mmul(Iv9, A9, "A^{-1}", "A")
sm[0]["en"] = "To show $A^{-1}A = I_3$, multiply each row of $A^{-1}$ by each column of $A$, entry by entry, and add."
sm[0]["ur"] = "$A^{-1}A = I_3$ دکھانے کے لیے $A^{-1}$ کی ہر قطار کو $A$ کے ہر کالم سے رکن بہ رکن ضرب دے کر جمع کریں۔"
sm[1]["math"] += " = I_3"
sm[1]["en"] = "The fractions cancel: every entry on the leading diagonal is 1 and every other entry is 0."
sm[1]["ur"] = "کسور کٹ جاتی ہیں: مرکزی وتر کا ہر رکن 1 اور باقی ہر رکن 0 ہے۔"
sm[1]["check"].append(meq(Iv9 * A9, sp.eye(3)))
s_ += sm
ex("ex4.2", 9, rf"Find the inverse of $A = {mtex(A9)}$ and show that $A^{{-1}}A = I_3$.", [P("", s_, f"$A^{{-1}} = {mtex(Iv9)}$")], "4.2")

# ---- Q10: (AB)^t = B^tA^t
q210 = []
for lab, A_, B_ in (("i", M([[1, -1, 2], [0, -3, 1]]), M([[1, 1], [-3, -2], [0, 1]])), ("ii", M([[1, 2], [1, 4], [2, 1]]), M([[1, -3], [-2, 1]]))):
    s1_, AB = m.mmul(A_, B_)
    s2_, ABt = m.mtr(AB, "(AB)")
    s3_, Bt = m.mtr(B_, "B")
    s4_, At = m.mtr(A_, "A")
    s5_, BtAt = m.mmul(Bt, At, "B^t", "A^t")
    q210.append(P(lab, [T("Left-hand side: $AB$, then its transpose.", "بائیں جانب: $AB$، پھر اس کا پلٹ۔")] + s1_ + s2_ +
                  [T("Right-hand side: $B^t$ and $A^t$, then $B^tA^t$.", "دائیں جانب: $B^t$ اور $A^t$، پھر $B^tA^t$۔")] + s3_ + s4_ + s5_ +
                  [S(rf"(AB)^t = {mtex(ABt)} = B^tA^t", "Both sides are equal.", "دونوں اطراف برابر ہیں۔", meq(ABt, BtAt))],
                  "$(AB)^t = B^t A^t$", prompt=f"$A = {mtex(A_)}$, $B = {mtex(B_)}$"))
ex("ex4.2", 10, "Verify $(AB)^t = B^tA^t$ if (i) " + q210[0]["prompt"] + " (ii) " + q210[1]["prompt"], q210, "4.2")

# ================================================================================================== Exercise 4.3

# ---- Q1: inverse by row operations
q31 = []
for lab, A_ in (("i", M([[2, 6, -3], [0, -2, 0], [-2, 5, 6]])), ("ii", M([[1, 2, -1], [0, -2, 8], [1, 0, 2]])), ("iii", M([[1, 6, 2], [2, 13, 0], [0, -1, 1]]))):
    s_, Iv = m.inverse_rowops(A_)
    q31.append(P(lab, s_, f"$A^{{-1}} = {mtex(Iv)}$", prompt=f"${mtex(A_)}$"))
ex("ex4.3", 1, "Find the inverse of each matrix by using elementary row operations: (i) " + q31[0]["prompt"] + " (ii) " + q31[1]["prompt"] +
   " (iii) " + q31[2]["prompt"], q31, "4.3")

# ---- Q2: rank
q32 = []
for lab, A_ in (("i", M([[1, -1, 3, 1], [-2, -6, 1, -1], [3, 1, 4, -2]])), ("ii", M([[1, -2, 3], [2, -4, 6], [-1, 0, 2], [0, 1, -1]])),
                ("iii", M([[3, -1, 3, 0, 1], [1, 2, -1, -3, -2], [2, 3, 4, 2, 1], [2, 5, -2, -3, 3]]))):
    s_, r_ = m.rank_steps(A_)
    q32.append(P(lab, s_, rf"$\text{{rank}}(A) = {r_}$", prompt=f"${mtex(A_)}$"))
ex("ex4.3", 2, "Find the rank of each matrix: (i) " + q32[0]["prompt"] + " (ii) " + q32[1]["prompt"] + " (iii) " + q32[2]["prompt"], q32, "4.3")

SYS = {
    "3i": (M([[2, 1, -1], [1, -1, 2], [3, 2, 1]]), M([1, 3, 4]), ["x", "y", "z"]),
    "3ii": (M([[1, 2, -3], [4, -1, 1], [-2, 3, 2]]), M([0, 5, 3]), ["x_1", "x_2", "x_3"]),
    "3iii": (M([[2, -1, 1], [1, 2, 2], [1, -2, -1]]), M([1, 2, 1]), ["x_1", "x_2", "x_3"]),
    "4i": (M([[1, -2, 1], [3, 1, -2], [0, 1, -1]]), M([-1, 4, 1]), ["x", "y", "z"]),
    "4ii": (M([[2, 1, 3], [1, 3, -2], [-3, -1, 2]]), M([3, 0, 4]), ["x_1", "x_2", "x_3"]),
    "4iii": (M([[1, 1, 0], [2, 0, -1], [0, 2, -3]]), M([2, 1, -1]), ["x", "y", "z"]),
    "5i": (M([[1, 2, -2], [2, 3, 1], [5, 4, -3]]), M([-1, 1, 1]), ["x_1", "x_2", "x_3"]),
    "5ii": (M([[1, 2, 1], [2, 1, 2], [2, 3, -1]]), M([2, 3, 7]), ["x", "y", "z"]),
    "5iii": (M([[1, 4, 1], [2, 1, -2], [3, 1, -1]]), M([2, 9, 12]), ["x_1", "x_2", "x_3"]),
}


def sys_part(key, method):
    A_, B_, nm = SYS[key]
    s_, vals = method(A_, B_, nm)
    return P(key[1:], s_, m.sys_answer(vals, nm), prompt="$" + m.system_tex(A_, B_, nm) + "$")


for qn, method, text in ((3, m.cramer, "Solve the following systems by Cramer's rule:"),
                         (4, m.inversion, "Solve the following systems by the matrix inversion method:"),
                         (5, m.gauss_jordan, "Solve the following systems by reducing their augmented matrices to echelon form and reduced echelon form:")):
    ps = [sys_part(f"{qn}{lab}", method) for lab in ("i", "ii", "iii")]
    ex("ex4.3", qn, text + " " + " ".join(f"({p_['label']}) {p_['prompt']}" for p_ in ps), ps, "4.3")

# answers written as the printed key writes them
for it in ITEMS:
    if it["id"] == "c11-ex4.3-q4":
        it["parts"][0]["answer"] = "$x = 1, y = 1, z = 0$"
        it["parts"][1]["answer"] = r"$x_1 = -\frac{8}{9}, \quad x_2 = \frac{10}{9}, \quad x_3 = \frac{11}{9}$"
        it["parts"][2]["answer"] = r"$x = 1, \; y = 1, \; z = 1$"
    if it["id"] == "c11-ex4.3-q5":
        it["parts"][1]["answer"] = r"$(x, y, z) = \left( \frac{22}{9}, \frac{1}{3}, -\frac{10}{9} \right)$"
    if it["id"] == "c11-ex4.3-q3":
        it["parts"][0]["answer"] = "$(x, y, z) = (1, 0, 1)$"

# ---- Q6: homogeneous systems
q36 = []
for lab, A_, nm in (("i", M([[1, 4, -2], [2, 1, 5], [5, 2, 8]]), ["x", "y", "z"]), ("ii", M([[1, 4, 2], [2, 1, -3], [3, 2, -4]]), ["x_1", "x_2", "x_3"]),
                    ("iii", M([[1, 2, -1], [1, -1, 5], [2, 1, 4]]), ["x_1", "x_2", "x_3"])):
    s_, base, free = m.homogeneous(A_, nm)
    if free is None:
        answer = f"$({','.join(nm)}) = (0,0,0)$"
    else:
        answer = f"$({', '.join(nm)}) = t({', '.join(e(v) for v in base)}), \\quad t \\in \\mathbb{{R}}$"
    q36.append(P(lab, s_, answer, prompt="$" + m.system_tex(A_, sp.zeros(3, 1), nm) + "$"))
ex("ex4.3", 6, "Solve the following homogeneous systems by Gaussian elimination: " + " ".join(f"({p_['label']}) {p_['prompt']}" for p_ in q36), q36, "4.3")

# ---- Q7: reflection in the y-axis
Ry = M([[-1, 0], [0, 1]])
pts = {"A": (4, 1), "B": (-2, 5), "C": (0, -3)}
Pm = M([[4, -2, 0], [1, 5, -3]])
img = Ry * Pm
q37 = P("", [
    S(rf"P = {mtex(Ry)}", "Reflection in the $y$-axis sends $(x, y)$ to $(-x, y)$; its matrix is $P$.",
      "$y$-محور میں انعکاس $(x, y)$ کو $(-x, y)$ پر لے جاتا ہے؛ اس کا قالب $P$ ہے۔"),
    S(rf"P{mtex(Pm)} = {mtex(Ry)}{mtex(Pm)} = {mtex(img)}", "Write the three vertices as the columns of one matrix and multiply by $P$.",
      "تینوں راسوں کو ایک قالب کے کالموں کے طور پر لکھ کر $P$ سے ضرب دیں۔", meq(Ry * Pm, img)),
    S(r"A'(-4, 1),\quad B'(2, 5),\quad C'(0, -3)", "Each column of the product is an image vertex.", "حاصل ضرب کا ہر کالم ایک عکس راس ہے۔"),
], r"$A'(-4,1), \quad B'(2,5), \quad C'(0,-3)$")
ex("ex4.3", 7, "A triangle has vertices $A(4, 1)$, $B(-2, 5)$ and $C(0, -3)$. Find its image under reflection in the $y$-axis by using a transformation matrix.",
   [q37], "4.3")

# ---- Q8: scaling
Ps = M([[5, 0, 0], [0, -5, 0], [0, 0, -5]])
Xp = M([30, 20, -5])
Xa = Ps.inv() * Xp
q38 = P("", [
    S(rf"PX = X':\quad {mtex(Ps)}{m.strtex([['x'], ['y'], ['z']])} = {mtex(Xp)}", "The point $A = (x, y, z)$ is mapped to $X' = PX$.",
      "نقطہ $A = (x, y, z)$، $X' = PX$ پر جاتا ہے۔"),
    S(rf"X = P^{{-1}}X' = {mtex(Ps.inv())}{mtex(Xp)} = {mtex(Xa)}", "$P$ is diagonal, so $P^{-1}$ has the reciprocals on the diagonal.",
      "$P$ وتری قالب ہے، اس لیے $P^{-1}$ کے وتر پر مقلوب اعداد ہیں۔", meq(Ps.inv() * Xp, Xa), meq(Ps * Xa, Xp)),
], "$A = (6, -4, 1)$")
ex("ex4.3", 8, rf"A point $A$ is mapped to $(30, 20, -5)$ by the scaling matrix $P = {mtex(Ps)}$. Find the coordinates of $A$.", [q38], "4.3")

# ---- Q9: image of y = x^2
XX, YY = sp.symbols("X Y")
Pc = M([[1, 2], [3, 4]])
inv_c = Pc.inv()
q39 = P("", [
    S(rf"{m.strtex([['X'], ['Y']])} = {mtex(Pc)}{m.strtex([['x'], ['y']])} \Rightarrow X = x + 2y,\ Y = 3x + 4y",
      "A point $(x, y)$ of the curve goes to $(X, Y)$.", "منحنی کا نقطہ $(x, y)$، $(X, Y)$ پر جاتا ہے۔"),
    S(rf"{m.strtex([['x'], ['y']])} = P^{{-1}}{m.strtex([['X'], ['Y']])} = {mtex(inv_c)}{m.strtex([['X'], ['Y']])} \Rightarrow x = -2X + Y,\ y = \frac{{3X - Y}}{{2}}",
      "$|P| = 4 - 6 = -2$, so $P^{-1} = -\\frac{1}{2}\\begin{bmatrix} 4 & -2 \\\\ -3 & 1 \\end{bmatrix}$; express $x, y$ in terms of $X, Y$.",
      "$|P| = 4 - 6 = -2$، اس لیے $P^{-1} = -\\frac{1}{2}\\begin{bmatrix} 4 & -2 \\\\ -3 & 1 \\end{bmatrix}$؛ $x, y$ کو $X, Y$ کی صورت میں لکھیں۔",
      meq(Pc.inv(), inv_c), "Eq(Matrix([[-2, 1], [R(3, 2), R(-1, 2)]])*Matrix([[1, 2], [3, 4]]), eye(2))"),
    S(r"\frac{3X - Y}{2} = (Y - 2X)^2 \Rightarrow 3X - Y = 2(Y - 2X)^2", "Substitute in $y = x^2$.", "$y = x^2$ میں قیمتیں رکھیں۔"),
    S(r"8X^2 - 8XY + 2Y^2 - 3X + Y = 0", "Expand and collect all terms on one side.", "پھیلا کر تمام ارکان ایک طرف جمع کریں۔",
      "expand(2*(Y - 2*X)**2 - (3*X - Y)) == expand(8*X**2 - 8*X*Y + 2*Y**2 - 3*X + Y)"),
], "The image curve is $3X - Y = 2(Y - 2X)^2$ or equivalently $8X^2 - 8XY + 2Y^2 - 3X + Y = 0$.")
ex("ex4.3", 9, rf"Find the equation of the image of the curve $y = x^2$ under the transformation with matrix $P = {mtex(Pc)}$.", [q39], "4.3")

# ---- Q10: encode
Ae = M([[1, 0, 1], [2, -1, 1], [0, 1, 2]])
blocks = [M([11, 5, 5]), M([16, 9, 20]), M([21, 16, 0])]
enc = [Ae * u for u in blocks]
q310 = P("", [
    S(r"K\,E\,E\,P\,I\,T\,U\,P \to 11,\ 5,\ 5,\ 16,\ 9,\ 20,\ 21,\ 16", "Write each letter as its number ($A = 1, \\ldots, Z = 26$); the spaces are left out.",
      "ہر حرف کو اس کے عدد میں لکھیں ($A = 1, \\ldots, Z = 26$)؛ خالی جگہیں چھوڑ دی جاتی ہیں۔"),
    S(rf"u_1 = {mtex(blocks[0])},\ u_2 = {mtex(blocks[1])},\ u_3 = {mtex(blocks[2])}",
      "Group the numbers in threes (the matrix is 3-by-3); the last group is completed with 0.", "اعداد کو تین تین کے گروہوں میں لکھیں (قالب 3-by-3 ہے)؛ آخری گروہ کو 0 سے مکمل کریں۔"),
] + [S(rf"Au_{k + 1} = {mtex(Ae)}{mtex(blocks[k])} = {mtex(enc[k])}", "Multiply by $A$ to encode the block.", "گروہ کو رمز میں بدلنے کے لیے $A$ سے ضرب دیں۔",
       meq(Ae * blocks[k], enc[k])) for k in range(3)],
    rf"The encoded message is represented by ${mtex(enc[0])}, \quad {mtex(enc[1])}, \quad {mtex(enc[2])}$")
note(q310, "The solution set leaves out the spaces and completes the last block with 0; with 27 for a space the blocks would change.",
     "حل میں خالی جگہیں چھوڑ دی گئی ہیں اور آخری گروہ 0 سے مکمل کیا گیا ہے؛ اگر خالی جگہ کے لیے 27 لیا جائے تو گروہ بدل جائیں گے۔")
ex("ex4.3", 10, rf"Use the matrix $A = {mtex(Ae)}$ to encode the message KEEP IT UP, where $A$ to $Z$ correspond to $1$ to $26$.", [q310], "4.3")

# ---- Q11: decode
Ad = M([[1, 1, -1], [1, 0, 1], [2, 1, 1]])
codes = [M([11, 20, 43]), M([25, 10, 41]), M([22, 14, 41])]
s_, Ivd = m.adjoint_inverse(Ad)
dec = [Ivd * v for v in codes]
letters = ["".join(" " if int(n) == 27 else chr(64 + int(n)) for n in d_) for d_ in dec]
q311 = P("", [S("v = Au \\Rightarrow u = A^{-1}v", "To decode, multiply each code block by $A^{-1}$.", "رمز کھولنے کے لیے ہر رمزی گروہ کو $A^{-1}$ سے ضرب دیں۔")] + s_ +
         [S(rf"A^{{-1}}{mtex(codes[k])} = {mtex(dec[k])} \to \text{{{letters[k].replace(' ', '(space)')}}}",
            "Multiply, then turn the numbers into letters ($27$ is a space).", "ضرب دیں، پھر اعداد کو حروف میں بدلیں ($27$ خالی جگہ ہے)۔", meq(Ivd * codes[k], dec[k]))
          for k in range(3)] +
         [S(r"\text{HOLD FIRE}", "Read the blocks in order.", "گروہوں کو ترتیب سے پڑھیں۔")], "HOLD FIRE")
ex("ex4.3", 11, rf"Decode the message ${mtex(codes[0])}, {mtex(codes[1])}, {mtex(codes[2])}$ encoded with the matrix $A = {mtex(Ad)}$, where $1$ to $26$ "
                "represent $A$ to $Z$ and $27$ represents a space.", [q311], "4.3")
