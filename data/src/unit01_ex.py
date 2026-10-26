"""Unit 1 - Real Numbers: exercise questions (Mathematics 9, Punjab textbook 2026).

Each solution is checked two ways: every computed step has a sympy check, and the build compares the
final answer with the book's printed Answers section (data/answers/unit01.json).
"""
import math

import _figs as F
from _helpers import P, Q, S, T
from _steps import between_part

UNIT = {"unit": 1, "title": "Real Numbers", "title_ur": "حقیقی اعداد", "items": []}
ITEMS = UNIT["items"]


def between_squares(n):
    k = math.isqrt(n)
    return (f"{k * k} < {n} < {(k + 1) ** 2}, so {n} is not a perfect square and $\\sqrt{{{n}}}$ is irrational.",
            f"{k * k} < {n} < {(k + 1) ** 2}، اس لیے {n} مکمل مربع نہیں اور $\\sqrt{{{n}}}$ غیر ناطق ہے۔",
            [f"floor(sqrt({n}))**2 < {n}", f"(floor(sqrt({n}))+1)**2 > {n}"])


# =========================================================================================
# EXERCISE 1.1
# =========================================================================================

# ---- Q1: rational or irrational ----
sq7_en, sq7_ur, sq7_chk = between_squares(7)
sq11_en, sq11_ur, sq11_chk = between_squares(11)
sq39_en, sq39_ur, sq39_chk = between_squares(39)

q1_parts = [
    P("i", [T("2.353535 has a finite number of digits after the decimal point, so it is a terminating decimal and therefore rational.",
              "2.353535 میں اعشاریہ کے بعد ہندسے محدود ہیں، یہ محدود اعشاری عدد ہے، اس لیے ناطق ہے۔",
              "Rational('2.353535') == Rational(2353535, 1000000)")], "Rational", prompt="$2.353535$"),
    P("ii", [S(r"0.\bar{6} = 0.666\ldots = \frac{6}{9} = \frac{2}{3}",
               "The digit 6 repeats forever, so this is a non-terminating recurring decimal. It can be written as p/q, so it is rational.",
               "ہندسہ 6 بار بار آتا ہے، یہ غیر محدود دوری اعشاری عدد ہے۔ اسے p/q کی شکل میں لکھا جا سکتا ہے، اس لیے ناطق ہے۔",
               "9*Rational(2,3) == 6")], "Rational", prompt=r"$0.\bar{6}$"),
    P("iii", [T("2.236067... goes on without ending and no group of digits repeats, so it is a non-terminating, non-recurring decimal and therefore irrational.",
                "2.236067... ختم نہیں ہوتا اور ہندسوں کا کوئی گروہ دہرایا نہیں جاتا، اس لیے یہ غیر ناطق ہے۔")],
      "Irrational", prompt=r"$2.236067\ldots$"),
    P("iv", [S(r"\sqrt{7}", sq7_en, sq7_ur, *sq7_chk)], "Irrational", prompt=r"$\sqrt{7}$"),
    P("v", [T("$e = 2.71828\\ldots$ (Euler's number) is a non-terminating, non-recurring decimal, so it is irrational.",
              "$e = 2.71828\\ldots$ (یولر کا عدد) غیر محدود غیر دوری اعشاری عدد ہے، اس لیے غیر ناطق ہے۔")],
      "Irrational", prompt="$e$"),
    P("vi", [T("$\\pi = 3.14159\\ldots$ is a non-terminating, non-recurring decimal, so it is irrational.",
               "$\\pi = 3.14159\\ldots$ غیر محدود غیر دوری اعشاری عدد ہے، اس لیے غیر ناطق ہے۔")],
      "Irrational", prompt=r"$\pi$"),
    P("vii", [S(r"\sqrt{11}\ \text{is irrational}", sq11_en, sq11_ur, *sq11_chk),
              T("5 is rational and $\\sqrt{11}$ is irrational. A rational number plus an irrational number is irrational, so $5+\\sqrt{11}$ is irrational.",
                "5 ناطق ہے اور $\\sqrt{11}$ غیر ناطق ہے۔ ناطق اور غیر ناطق عدد کا مجموعہ غیر ناطق ہوتا ہے، اس لیے $5+\\sqrt{11}$ غیر ناطق ہے۔")],
      "Irrational", prompt=r"$5+\sqrt{11}$"),
    P("viii", [S(r"(\sqrt{3}+\sqrt{13})^2 = 3+13+2\sqrt{39} = 16+2\sqrt{39}",
                 "Square the number. If $\\sqrt{3}+\\sqrt{13}$ were rational, its square would be rational too.",
                 "عدد کا مربع لیں۔ اگر $\\sqrt{3}+\\sqrt{13}$ ناطق ہوتا تو اس کا مربع بھی ناطق ہوتا۔",
                 "(sqrt(3)+sqrt(13))**2 == 16 + 2*sqrt(39)"),
                S(r"\sqrt{39}\ \text{is irrational}", sq39_en, sq39_ur, *sq39_chk),
                T("So $16+2\\sqrt{39}$ is irrational, which means its square root $\\sqrt{3}+\\sqrt{13}$ cannot be rational. It is irrational.",
                  "اس لیے $16+2\\sqrt{39}$ غیر ناطق ہے، یعنی اس کا جذر $\\sqrt{3}+\\sqrt{13}$ ناطق نہیں ہو سکتا۔ یہ غیر ناطق ہے۔")],
      "Irrational", prompt=r"$\sqrt{3}+\sqrt{13}$"),
    P("ix", [S(r"\frac{15}{4} = 3.75", "15/4 is a quotient of two integers, so it is rational. Its decimal 3.75 terminates.",
               "15/4 دو صحیح اعداد کی نسبت ہے، اس لیے ناطق ہے۔ اس کا اعشاری روپ 3.75 محدود ہے۔",
               "Rational(15,4) == Rational('3.75')")], "Rational", prompt=r"$\frac{15}{4}$"),
    P("x", [S(r"(2-\sqrt{2})(2+\sqrt{2}) = 2^2-(\sqrt{2})^2 = 4-2 = 2",
              "Use $(a-b)(a+b) = a^2-b^2$. The product is 2, which is a rational number.",
              "$(a-b)(a+b) = a^2-b^2$ استعمال کریں۔ حاصل ضرب 2 ہے جو ناطق عدد ہے۔",
              "(2-sqrt(2))*(2+sqrt(2)) == 2", "2**2 - sqrt(2)**2 == 2")], "Rational", prompt=r"$(2-\sqrt{2})(2+\sqrt{2})$"),
]
q1_parts[-1]["key_note"] = ("The printed answer key lists (x) as Irrational, but (2-sqrt2)(2+sqrt2) = 2, which is rational. "
                            "The key has an error here; the sympy check above proves the product is 2.")
q1_parts[-1]["note"] = {"en": "The book's printed answer key says \"Irrational\" for this part. That is a misprint: the product equals 2, a rational number.",
                        "ur": "کتاب کے آخر میں دیے گئے جوابات میں اس حصے کے لیے \"غیر ناطق\" لکھا ہے۔ یہ غلطی ہے: حاصل ضرب 2 ہے جو ناطق عدد ہے۔"}

ITEMS.append(Q("ex1.1-q1", "exercise", 1, 10,
               r"Identify each of the following as a rational or irrational number: (i) $2.353535$ (ii) $0.\bar{6}$ (iii) $2.236067\ldots$ (iv) $\sqrt{7}$ "
               r"(v) $e$ (vi) $\pi$ (vii) $5+\sqrt{11}$ (viii) $\sqrt{3}+\sqrt{13}$ (ix) $\frac{15}{4}$ (x) $(2-\sqrt{2})(2+\sqrt{2})$",
               q1_parts, exercise="1.1"))


# ---- Q2: represent on the number line ----
def sqrt_figure_steps(n_label, stage_two):
    """Number line 0..3. sqrt2 = hypotenuse of legs 1 and 1; sqrt3 = hypotenuse of legs sqrt2 and 1."""
    lo, hi = 0, 3
    tri1, by1 = F.triangle(lo, hi, 1, 1)
    arc1 = F.arc_to_axis(lo, hi, 1, 1, math.sqrt(2))
    x0, x1, xd = F.nx(0, lo, hi), F.nx(1, lo, hi), F.nx(math.sqrt(2), lo, hi)
    labels1 = [F.text(x0 - 2, F.Y + 12, "O"), F.text(x1, F.Y + 12, "A"), F.text(x1 + 3, by1, "B")]
    first = [
        S(r"\sqrt{2} = \sqrt{1^2+1^2}",
          "Write 2 as a sum of two squares: 2 = 1² + 1². So $\\sqrt{2}$ is the hypotenuse of a right triangle whose legs are 1 and 1.",
          "2 کو دو مربعات کے مجموعے کی شکل میں لکھیں: 2 = 1² + 1²۔ اس لیے $\\sqrt{2}$ اس قائمۃ الزاویہ مثلث کا وتر ہے جس کے دونوں ضلع 1 ہیں۔",
          "sqrt(2) == sqrt(1**2 + 1**2)", draw=[F.axis(lo, hi)]),
        S(r"m\overline{OA} = 1, \quad m\overline{AB} = 1",
          "Mark O at 0 and A at 1. At A draw AB = 1 unit perpendicular to the number line. This gives the right-angled triangle OAB.",
          "O کو 0 پر اور A کو 1 پر لگائیں۔ A پر نمبر لائن کے عمود 1 اکائی کا AB کھینچیں۔ یوں قائمۃ الزاویہ مثلث OAB بنتا ہے۔",
          draw=tri1 + labels1),
        S(r"(m\overline{OB})^2 = 1^2+1^2 = 2 \;\Rightarrow\; m\overline{OB} = \sqrt{2}",
          "By the Pythagoras theorem the hypotenuse OB is $\\sqrt{2}$.", "فیثاغورث کے قضیے سے وتر OB کی لمبائی $\\sqrt{2}$ ہے۔",
          "1**2 + 1**2 == 2"),
    ]
    if not stage_two:
        first.append(S(r"|\overline{OP}| = \sqrt{2}",
                       "With O as the centre and radius OB, draw an arc. It cuts the number line at P, so P represents $\\sqrt{2}$.",
                       "O کو مرکز اور OB کو رداس لے کر قوس کھینچیں۔ یہ نمبر لائن کو P پر کاٹتی ہے، اس لیے P نقطہ $\\sqrt{2}$ کو ظاہر کرتا ہے۔",
                       draw=arc1 + [F.text(xd, F.Y + 12, "P")]))
        return first
    # sqrt3: keep the sqrt2 construction (point D), then build a second right triangle on it
    first.insert(0, S(r"\sqrt{3} = \sqrt{(\sqrt{2})^2+1^2}",
                      "Since 3 = 2 + 1, $\\sqrt{3}$ is the hypotenuse of a right triangle with legs $\\sqrt{2}$ and 1. So first construct $\\sqrt{2}$, then use it as one leg.",
                      "چونکہ 3 = 2 + 1 ہے، اس لیے $\\sqrt{3}$ اس قائمۃ الزاویہ مثلث کا وتر ہے جس کے ضلع $\\sqrt{2}$ اور 1 ہیں۔ پہلے $\\sqrt{2}$ بنائیں، پھر اسے ایک ضلع کے طور پر استعمال کریں۔",
                      "sqrt(3) == sqrt(sqrt(2)**2 + 1**2)"))
    first.append(S(r"|\overline{OD}| = \sqrt{2}",
                   "With O as the centre and radius OB draw an arc. It cuts the number line at D, so OD = $\\sqrt{2}$.",
                   "O کو مرکز اور OB کو رداس لے کر قوس کھینچیں۔ یہ نمبر لائن کو D پر کاٹتی ہے، اس لیے OD = $\\sqrt{2}$ ہے۔",
                   draw=arc1 + [F.text(xd, F.Y + 12, "D")]))
    ey = round(F.Y - 88 / (hi - lo), 2)
    tri2 = [{"t": "line", "p": [xd, F.Y, xd, ey]}, {"t": "right", "p": [xd, F.Y], "d": [-1, 0, 0, -1]},
            {"t": "line", "p": [x0, F.Y, xd, ey]}, F.text(xd + 3, ey, "E")]
    first += [
        S(r"m\overline{OD} = \sqrt{2}, \quad m\overline{DE} = 1",
          "At D draw DE = 1 unit perpendicular to the number line and join O to E. The legs of the new right triangle ODE are $\\sqrt{2}$ and 1.",
          "D پر نمبر لائن کے عمود 1 اکائی کا DE کھینچیں اور O کو E سے ملائیں۔ نئے قائمۃ الزاویہ مثلث ODE کے ضلع $\\sqrt{2}$ اور 1 ہیں۔",
          draw=tri2),
        S(r"(m\overline{OE})^2 = (\sqrt{2})^2+1^2 = 3 \;\Rightarrow\; m\overline{OE} = \sqrt{3}",
          "By the Pythagoras theorem OE = $\\sqrt{3}$.", "فیثاغورث کے قضیے سے OE = $\\sqrt{3}$ ہے۔",
          "sqrt(2)**2 + 1**2 == 3"),
        S(r"|\overline{OF}| = \sqrt{3}",
          "With O as the centre and radius OE, draw an arc. It cuts the number line at F, so F represents $\\sqrt{3}$.",
          "O کو مرکز اور OE کو رداس لے کر قوس کھینچیں۔ یہ نمبر لائن کو F پر کاٹتی ہے، اس لیے F نقطہ $\\sqrt{3}$ کو ظاہر کرتا ہے۔",
          draw=F.arc_to_axis(lo, hi, math.sqrt(2), 1, math.sqrt(3)) + [F.text(F.nx(math.sqrt(3), lo, hi), F.Y + 12, "F")]),
    ]
    return first


def fraction_figure_steps(from_, to_, lo, hi, n, value, plain, tex, rule_en, rule_ur, math_line, *checks):
    """Mark `value` by dividing the interval [lo, hi] into n equal parts."""
    return [
        S(tex + rf" \text{{ lies between }} {lo} \text{{ and }} {hi}",
          f"Draw a number line. {plain} lies between {lo} and {hi}.", f"نمبر لائن بنائیں۔ {plain} عدد {lo} اور {hi} کے درمیان ہے۔",
          f"Rational({value.p},{value.q}) > {lo}", f"Rational({value.p},{value.q}) < {hi}", draw=[F.axis(from_, to_)]),
        S(rf"\text{{Divide }} [{lo},{hi}] \text{{ into }} {n} \text{{ equal parts}}",
          f"Divide the distance between {lo} and {hi} into {n} equal parts. Each part is 1/{n}.",
          f"{lo} اور {hi} کے درمیان فاصلے کو {n} برابر حصوں میں تقسیم کریں۔ ہر حصہ 1/{n} ہے۔", draw=[F.subdivide(lo, hi, from_, to_, n)]),
        S(math_line, rule_en, rule_ur, *checks,
          draw=[F.axis(from_, to_, marks=[{"v": float(value), "s": plain}])]),
    ]


from sympy import Rational as _R  # noqa: E402

q2_parts = [
    P("i", sqrt_figure_steps("2", False), r"P represents $\sqrt{2}$ on the number line.", prompt=r"$\sqrt{2}$"),
    P("ii", sqrt_figure_steps("3", True), r"F represents $\sqrt{3}$ on the number line.", prompt=r"$\sqrt{3}$"),
    P("iii", fraction_figure_steps(3, 6, 4, 5, 3, _R(13, 3), "4 1/3", r"4\frac{1}{3}",
                                   "The point is 1 part to the right of 4.", "نقطہ 4 سے ایک حصہ دائیں طرف ہے۔",
                                   r"4\frac{1}{3} = 4 + \frac{1}{3}", "4 + Rational(1,3) == Rational(13,3)"),
      r"$4\frac{1}{3}$ is the first division to the right of 4.", prompt=r"$4\frac{1}{3}$"),
    P("iv", fraction_figure_steps(-4, 0, -3, -2, 7, _R(-15, 7), "-2 1/7", r"-2\frac{1}{7}",
                                  "The point is 1 part to the left of -2, because the number is negative.",
                                  "عدد منفی ہے، اس لیے نقطہ -2 سے ایک حصہ بائیں طرف ہے۔",
                                  r"-2\frac{1}{7} = -2 - \frac{1}{7}", "-2 - Rational(1,7) == Rational(-15,7)"),
      r"$-2\frac{1}{7}$ is the first division to the left of $-2$.", prompt=r"$-2\frac{1}{7}$"),
    P("v", fraction_figure_steps(-1, 2, 0, 1, 8, _R(5, 8), "5/8", r"\frac{5}{8}",
                                 "The point is 5 parts to the right of 0.", "نقطہ 0 سے پانچ حصے دائیں طرف ہے۔",
                                 r"\frac{5}{8} = 5 \times \frac{1}{8}", "5*Rational(1,8) == Rational(5,8)"),
      r"$\frac{5}{8}$ is the fifth division to the right of 0.", prompt=r"$\frac{5}{8}$"),
    P("vi", fraction_figure_steps(1, 4, 2, 3, 4, _R(11, 4), "2 3/4", r"2\frac{3}{4}",
                                  "The point is 3 parts to the right of 2.", "نقطہ 2 سے تین حصے دائیں طرف ہے۔",
                                  r"2\frac{3}{4} = 2 + 3 \times \frac{1}{4}", "2 + 3*Rational(1,4) == Rational(11,4)"),
      r"$2\frac{3}{4}$ is the third division to the right of 2.", prompt=r"$2\frac{3}{4}$"),
]
ITEMS.append(Q("ex1.1-q2", "exercise", 2, 10, r"Represent the following numbers on the number line: (i) $\sqrt{2}$ (ii) $\sqrt{3}$ (iii) $4\frac{1}{3}$ "
               r"(iv) $-2\frac{1}{7}$ (v) $\frac{5}{8}$ (vi) $2\frac{3}{4}$", q2_parts, exercise="1.1"))


# ---- Q3: recurring decimals as p/q ----
def recurring_part(label, digits, expr, note_reduce=None):
    k = len(digits)
    num, den = int(digits), 10 ** k - 1
    mult = 10 ** k
    steps = [
        S(rf"x = 0.{digits * 3}\ldots", "Let x be the recurring decimal.", "فرض کریں x یہ دوری اعشاری عدد ہے۔"),
        S(rf"{mult}x = {digits}.{digits * 3}\ldots",
          f"{'One digit repeats' if k == 1 else 'Two digits repeat'}, so multiply both sides by {mult}.",
          f"{'ایک ہندسہ' if k == 1 else 'دو ہندسے'} دہرائے جاتے ہیں، اس لیے دونوں طرف {mult} سے ضرب دیں۔",
          f"{mult}*Rational({num},{den}) == {num} + Rational({num},{den})"),
        S(rf"{mult}x - x = {digits}.{digits * 3}\ldots - 0.{digits * 3}\ldots \;\Rightarrow\; {den}x = {num}",
          "Subtract the first line from the second so the repeating part cancels.",
          "پہلی لکیر کو دوسری میں سے منہا کریں، دہرایا جانے والا حصہ ختم ہو جاتا ہے۔",
          f"{mult}*Rational({num},{den}) - Rational({num},{den}) == {num}"),
        S(rf"x = \frac{{{num}}}{{{den}}}", f"Divide both sides by {den}." + (f" {note_reduce[0]}" if note_reduce else ""),
          f"دونوں طرف {den} سے تقسیم کریں۔" + (f" {note_reduce[1]}" if note_reduce else ""),
          f"Rational({num},{den})*{den} == {num}"),
    ]
    return P(label, steps, rf"$\frac{{{num}}}{{{den}}}$", prompt=expr)


ITEMS.append(Q("ex1.1-q3", "exercise", 3, 10, r"Express the following as a rational number $\frac{p}{q}$ where $p$ and $q$ are integers and $q \neq 0$: "
               r"(i) $0.\bar{4}$ (ii) $0.\overline{37}$ (iii) $0.\overline{21}$",
               [recurring_part("i", "4", r"$0.\bar{4}$"), recurring_part("ii", "37", r"$0.\overline{37}$"),
                recurring_part("iii", "21", r"$0.\overline{21}$",
                               ("In lowest terms this is 7/33.", "سب سے چھوٹی صورت میں یہ 7/33 ہے۔"))], exercise="1.1"))

# ---- Q4: name the property ----
ITEMS.append(Q("ex1.1-q4", "exercise", 4, 11, r"Name the property used in the following: (i) $(a+4)+b = a+(4+b)$ (ii) $\sqrt{2}+\sqrt{3} = \sqrt{3}+\sqrt{2}$ "
               r"(iii) $x-x = 0$ (iv) $a(b+c) = ab+ac$ (v) $16+0 = 16$ (vi) $100\times 1 = 100$ (vii) $4\times(5\times 8) = (4\times 5)\times 8$ (viii) $ab = ba$",
               [P("i", [S(r"(a+4)+b = a+(4+b)", "The grouping of the numbers changes but the sum stays the same.", "اعداد کی گروہ بندی بدلی مگر مجموعہ وہی رہا۔",
                          "(a+4)+b == a+(4+b)")], "Associative property over addition", prompt=r"$(a+4)+b = a+(4+b)$"),
                P("ii", [S(r"\sqrt{2}+\sqrt{3} = \sqrt{3}+\sqrt{2}", "The order of the numbers changes but the sum stays the same.", "اعداد کی ترتیب بدلی مگر مجموعہ وہی رہا۔",
                           "sqrt(2)+sqrt(3) == sqrt(3)+sqrt(2)")], "Commutative property over addition", prompt=r"$\sqrt{2}+\sqrt{3} = \sqrt{3}+\sqrt{2}$"),
                P("iii", [S(r"x-x = x+(-x) = 0", "A number plus its negative is 0, so -x is the additive inverse of x.", "عدد اور اس کے منفی کا مجموعہ 0 ہوتا ہے، اس لیے -x عدد x کا جمعی معکوس ہے۔",
                            "x - x == 0")], "Additive inverse", prompt="$x-x = 0$"),
                P("iv", [S(r"a(b+c) = ab+ac", "Multiplication is spread over addition from the left.", "ضرب بائیں طرف سے جمع پر تقسیم ہو رہی ہے۔",
                           "a*(b+c) == a*b + a*c")], "Left distributive property", prompt="$a(b+c) = ab+ac$"),
                P("v", [S(r"16+0 = 16", "Adding 0 does not change the number, so 0 is the additive identity.", "0 جمع کرنے سے عدد نہیں بدلتا، اس لیے 0 جمعی محائدہ ہے۔",
                          "16 + 0 == 16")], "Additive identity", prompt="$16+0 = 16$"),
                P("vi", [S(r"100 \times 1 = 100", "Multiplying by 1 does not change the number, so 1 is the multiplicative identity.", "1 سے ضرب دینے سے عدد نہیں بدلتا، اس لیے 1 ضربی محائدہ ہے۔",
                           "100*1 == 100")], "Multiplicative identity", prompt=r"$100\times 1 = 100$"),
                P("vii", [S(r"4\times(5\times 8) = (4\times 5)\times 8", "The grouping of the numbers changes but the product stays the same.", "اعداد کی گروہ بندی بدلی مگر حاصل ضرب وہی رہا۔",
                            "4*(5*8) == (4*5)*8")], "Associative property under multiplication", prompt=r"$4\times(5\times 8) = (4\times 5)\times 8$"),
                P("viii", [S(r"ab = ba", "The order of the numbers changes but the product stays the same.", "اعداد کی ترتیب بدلی مگر حاصل ضرب وہی رہا۔",
                             "a*b == b*a")], "Commutative property under multiplication", prompt="$ab = ba$")], exercise="1.1"))

# ---- Q5: name the order / equality property ----
ITEMS.append(Q("ex1.1-q5", "exercise", 5, 11, r"Name the property used in the following: (i) $-3 < -1 \Rightarrow 0 < 2$ (ii) If $a < b$ then $\frac{1}{a} > \frac{1}{b}$ "
               r"(iii) If $a < b$ then $a+c < b+c$ (iv) If $ac < bc$ and $c > 0$ then $a < b$ (v) If $ac < bc$ and $c < 0$ then $a > b$ (vi) Either $a > b$ or $a = b$ or $a < b$",
               [P("i", [S(r"-3 < -1 \;\Rightarrow\; -3+3 < -1+3 \;\Rightarrow\; 0 < 2", "The same number (3) is added to both sides and the direction of the inequality stays the same.",
                          "دونوں طرف ایک ہی عدد (3) جمع کیا گیا اور عدم مساوات کی سمت وہی رہی۔", "-3+3 == 0", "-1+3 == 2")], "Additive property", prompt=r"$-3 < -1 \Rightarrow 0 < 2$"),
                P("ii", [S(r"a < b \;\Rightarrow\; \frac{1}{a} > \frac{1}{b}", "Taking reciprocals of two numbers with the same sign reverses the inequality. For example 2 < 3 but 1/2 > 1/3.",
                           "ایک ہی علامت والے دو اعداد کے مقلوب لینے سے عدم مساوات الٹ جاتی ہے۔ مثلاً 2 < 3 مگر 1/2 > 1/3۔", "Rational(1,2) > Rational(1,3)")],
                  "Reciprocal property", prompt=r"If $a < b$ then $\frac{1}{a} > \frac{1}{b}$"),
                P("iii", [S(r"a < b \;\Rightarrow\; a+c < b+c", "The same number c is added to both sides, so the inequality keeps its direction. For example 1 < 2 gives 1+5 < 2+5.",
                            "دونوں طرف ایک ہی عدد c جمع کیا گیا، اس لیے عدم مساوات کی سمت وہی رہتی ہے۔ مثلاً 1 < 2 سے 1+5 < 2+5۔", "1+5 < 2+5")],
                  "Additive property", prompt="If $a < b$ then $a+c < b+c$"),
                P("iv", [S(r"ac < bc,\ c > 0 \;\Rightarrow\; a < b", "Both sides are multiplied by 1/c, which is positive, so the direction does not change. For example 2·3 < 5·3 gives 2 < 5.",
                           "دونوں طرف 1/c سے ضرب دی گئی جو مثبت ہے، اس لیے سمت نہیں بدلتی۔ مثلاً 2·3 < 5·3 سے 2 < 5۔", "2*3 < 5*3", "2 < 5")],
                  "Multiplicative property", prompt="If $ac < bc$ and $c > 0$ then $a < b$"),
                P("v", [S(r"ac < bc,\ c < 0 \;\Rightarrow\; a > b", "Both sides are multiplied by 1/c, which is negative, so the inequality is reversed. For example 5(-2) < 2(-2) gives 5 > 2.",
                          "دونوں طرف 1/c سے ضرب دی گئی جو منفی ہے، اس لیے عدم مساوات الٹ جاتی ہے۔ مثلاً 5(-2) < 2(-2) سے 5 > 2۔", "5*(-2) < 2*(-2)", "5 > 2")],
                  "Multiplicative property", prompt="If $ac < bc$ and $c < 0$ then $a > b$"),
                P("vi", [S(r"a > b \ \text{or} \ a = b \ \text{or} \ a < b", "For any two real numbers exactly one of the three relations is true. For example, for 1/3 and 1/2 it is 1/3 < 1/2.",
                           "کسی بھی دو حقیقی اعداد کے لیے تین رشتوں میں سے ایک اور صرف ایک درست ہوتا ہے۔ مثلاً 1/3 اور 1/2 کے لیے 1/3 < 1/2۔", "Rational(1,3) < Rational(1,2)")],
                  "Trichotomy property", prompt=r"Either $a > b$ or $a = b$ or $a < b$")], exercise="1.1"))


# ---- Q6: two rational numbers between ----
ITEMS.append(Q("ex1.1-q6", "exercise", 6, 11, r"Find two rational numbers between: (i) $\frac{1}{3}$ and $\frac{1}{4}$ (ii) $3$ and $4$ (iii) $\frac{3}{5}$ and $\frac{4}{5}$",
               [between_part("i", r"\frac{1}{4}", r"\frac{1}{3}", _R(1, 4), _R(1, 3), _R(7, 24), _R(5, 16)),
                between_part("ii", "3", "4", _R(3), _R(4), _R(7, 2), _R(15, 4)),
                between_part("iii", r"\frac{3}{5}", r"\frac{4}{5}", _R(3, 5), _R(4, 5), _R(7, 10), _R(3, 4))], exercise="1.1"))
