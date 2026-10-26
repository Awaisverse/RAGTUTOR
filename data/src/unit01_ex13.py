"""Unit 1 - Real Numbers: Exercise 1.3 (word problems) and Review Exercise 1. Printed pages 18-20."""
from sympy import Rational as _R

import _figs as F
from _helpers import P, Q, S, T, one
from _steps import associative_parts, between_part, distributive_parts

UNIT = {"unit": 1, "title": "Real Numbers", "title_ur": "حقیقی اعداد", "items": []}
ITEMS = UNIT["items"]

# =========================================================================================
# EXERCISE 1.3
# =========================================================================================
ITEMS.append(Q("ex1.3-q1", "exercise", 1, 18, "The sum of three consecutive integers is forty-two, find the three integers.", one([
    S(r"\text{Let the integers be } x,\; x+1,\; x+2", "Consecutive integers differ by 1, so call them x, x+1 and x+2.",
      "متواتر صحیح اعداد میں 1 کا فرق ہوتا ہے، انہیں x، x+1 اور x+2 فرض کریں۔"),
    S(r"x + (x+1) + (x+2) = 42 \;\Rightarrow\; 3x+3 = 42", "Their sum is 42. Collect the terms.", "ان کا مجموعہ 42 ہے۔ ارکان کو جمع کریں۔", "x + (x+1) + (x+2) == 3*x + 3"),
    S(r"3x = 39 \;\Rightarrow\; x = 13", "Subtract 3 from both sides, then divide by 3.", "دونوں طرف سے 3 منفی کریں، پھر 3 سے تقسیم کریں۔", "42 - 3 == 39", "Rational(39,3) == 13"),
    S(r"x = 13,\quad x+1 = 14,\quad x+2 = 15", "Put x = 13 back to get the three integers.", "تینوں اعداد معلوم کرنے کے لیے x = 13 رکھیں۔", "13 + 14 + 15 == 42"),
], "$13,\\ 14,\\ 15$"), exercise="1.3"))

# Q2: right triangle with a given area
tri_a, tri_c, tri_b = (30, 50), (85, 50), (30, 12)
q2_fig = [{"t": "poly", "p": [tri_a[0], tri_a[1], tri_c[0], tri_c[1], tri_b[0], tri_b[1]], "close": True},
          {"t": "right", "p": [tri_a[0], tri_a[1]], "d": [1, 0, 0, -1]},
          F.text(tri_b[0] - 3, tri_b[1] - 3, "B"), F.text(tri_a[0] - 3, tri_a[1] + 5, "A"), F.text(tri_c[0] + 2, tri_c[1] + 5, "C"),
          F.text(57, 56, "(sqrt3+sqrt5) cm")]
ITEMS.append(Q("ex1.3-q2", "exercise", 2, 18, "The diagram shows right angled $\\Delta ABC$ in which the length of $\\overline{AC}$ is $(\\sqrt{3}+\\sqrt{5})$ cm. "
               "The area of $\\Delta ABC$ is $(1+\\sqrt{15})$ cm$^2$. Find the length $\\overline{AB}$ in the form $(a\\sqrt{3}+b\\sqrt{5})$ cm, where $a$ and $b$ are integers.", one([
    S(r"\text{Area} = \frac{1}{2} \times m\overline{AB} \times m\overline{AC}", "The right angle is at A, so AB and AC are the base and the height of the triangle.",
      "قائمہ زاویہ A پر ہے، اس لیے AB اور AC مثلث کی قاعدہ اور اونچائی ہیں۔", draw=q2_fig),
    S(r"1+\sqrt{15} = \frac{1}{2} \times m\overline{AB} \times (\sqrt{3}+\sqrt{5}) \;\Rightarrow\; m\overline{AB} = \frac{2(1+\sqrt{15})}{\sqrt{3}+\sqrt{5}}",
      "Put in the area and AC, then solve for AB.", "رقبہ اور AC رکھیں، پھر AB کے لیے حل کریں۔",
      "Rational(1,2)*(2*(1+sqrt(15))/(sqrt(3)+sqrt(5)))*(sqrt(3)+sqrt(5)) == 1 + sqrt(15)"),
    S(r"m\overline{AB} = \frac{2(1+\sqrt{15})}{\sqrt{3}+\sqrt{5}} \times \frac{\sqrt{5}-\sqrt{3}}{\sqrt{5}-\sqrt{3}} = \frac{2(1+\sqrt{15})(\sqrt{5}-\sqrt{3})}{5-3} = (1+\sqrt{15})(\sqrt{5}-\sqrt{3})",
      "Rationalize the denominator with the conjugate $\\sqrt{5}-\\sqrt{3}$; the denominator becomes $5-3 = 2$.",
      "مزدوج $\\sqrt{5}-\\sqrt{3}$ سے نسب نما کو ناطق بنائیں؛ نسب نما $5-3 = 2$ ہو جاتا ہے۔",
      "2*(1+sqrt(15))/(sqrt(3)+sqrt(5)) == (1+sqrt(15))*(sqrt(5)-sqrt(3))"),
    S(r"(1+\sqrt{15})(\sqrt{5}-\sqrt{3}) = \sqrt{5}-\sqrt{3}+\sqrt{75}-\sqrt{45} = \sqrt{5}-\sqrt{3}+5\sqrt{3}-3\sqrt{5} = 4\sqrt{3}-2\sqrt{5}",
      "Multiply out, then use $\\sqrt{75} = 5\\sqrt{3}$ and $\\sqrt{45} = 3\\sqrt{5}$.", "ضرب دیں، پھر $\\sqrt{75} = 5\\sqrt{3}$ اور $\\sqrt{45} = 3\\sqrt{5}$ استعمال کریں۔",
      "(1+sqrt(15))*(sqrt(5)-sqrt(3)) == 4*sqrt(3) - 2*sqrt(5)", "sqrt(75) == 5*sqrt(3)", "sqrt(45) == 3*sqrt(5)"),
], r"$m\overline{AB} = 4\sqrt{3}-2\sqrt{5}$ cm"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q3", "exercise", 3, 18, "A rectangle has sides of length $2+\\sqrt{18}$ m and $\\left(5-\\frac{4}{\\sqrt{2}}\\right)$ m. Express the area of the rectangle in the form $a+b\\sqrt{2}$, where $a$ and $b$ are integers.", one([
    S(r"\sqrt{18} = 3\sqrt{2}, \qquad \frac{4}{\sqrt{2}} = \frac{4\sqrt{2}}{2} = 2\sqrt{2}", "Simplify the sides: $\\sqrt{18} = \\sqrt{9 \\times 2}$ and rationalize $\\frac{4}{\\sqrt{2}}$.",
      "اضلاع کو سادہ کریں: $\\sqrt{18} = \\sqrt{9 \\times 2}$ اور $\\frac{4}{\\sqrt{2}}$ کو ناطق بنائیں۔", "sqrt(18) == 3*sqrt(2)", "4/sqrt(2) == 2*sqrt(2)"),
    S(r"\text{Sides: } 2+3\sqrt{2} \text{ and } 5-2\sqrt{2}", "Put the simplified values into the sides.", "سادہ قیمتیں اضلاع میں رکھیں۔",
      "2 + sqrt(18) == 2 + 3*sqrt(2)", "5 - 4/sqrt(2) == 5 - 2*sqrt(2)"),
    S(r"\text{Area} = (2+3\sqrt{2})(5-2\sqrt{2}) = 10-4\sqrt{2}+15\sqrt{2}-6(\sqrt{2})^2", "Area = length × width. Multiply each term of the first bracket by each term of the second.",
      "رقبہ = لمبائی × چوڑائی۔ پہلے قوسین کے ہر رکن کو دوسرے کے ہر رکن سے ضرب دیں۔", "(2+3*sqrt(2))*(5-2*sqrt(2)) == 10 - 4*sqrt(2) + 15*sqrt(2) - 6*sqrt(2)**2"),
    S(r"= 10-12+11\sqrt{2} = -2+11\sqrt{2}", "Use $(\\sqrt{2})^2 = 2$ and add the like terms.", "$(\\sqrt{2})^2 = 2$ استعمال کریں اور ملتے جلتے ارکان جمع کریں۔",
      "(2+3*sqrt(2))*(5-2*sqrt(2)) == -2 + 11*sqrt(2)"),
], r"$(11\sqrt{2}-2)\ m^2$"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q4", "exercise", 4, 18, "Find two numbers whose sum is 68 and difference is 22.", one([
    S(r"a+b = 68 \quad \text{(i)}, \qquad a-b = 22 \quad \text{(ii)}", "Let the numbers be a and b and write both conditions.", "اعداد کو a اور b فرض کریں اور دونوں شرطیں لکھیں۔"),
    S(r"2a = 90 \;\Rightarrow\; a = 45", "Add (i) and (ii). The b terms cancel.", "(i) اور (ii) کو جمع کریں، b والے رکن ختم ہو جاتے ہیں۔", "68 + 22 == 90", "Rational(90,2) == 45"),
    S(r"45 + b = 68 \;\Rightarrow\; b = 23", "Put a = 45 in (i).", "a = 45 کو (i) میں رکھیں۔", "68 - 45 == 23", "45 - 23 == 22"),
], "$45,\\ 23$"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q5", "exercise", 5, 18, "The weather in Lahore was unusually warm during the summer of 2024. The TV news reported temperature as high as $48^\\circ C$. "
               "By using the formula $\\left({}^\\circ F = \\frac{9}{5}\\,{}^\\circ C + 32\\right)$ find the temperature as Fahrenheit scale.", one([
    S(r"{}^\circ F = \frac{9}{5}\,{}^\circ C + 32", "Use the Celsius-to-Fahrenheit formula.", "سیلسیس سے فارن ہائیٹ کا فارمولا استعمال کریں۔"),
    S(r"^\circ F = \frac{9}{5} \times 48 + 32 = 86.4 + 32 = 118.4", "Put $^\\circ C = 48$ and calculate.", "$^\\circ C = 48$ رکھیں اور حساب کریں۔",
      "Rational(9,5)*48 == Rational('86.4')", "Rational('86.4') + 32 == Rational('118.4')"),
], r"$118.4^{\circ}F$"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q6", "exercise", 6, 19, "The sum of the ages of the father and son is 72 years. Six years ago, the father's age was 2 times the age of the son. What was son's age six years ago?", one([
    S(r"\text{Son's age six years ago} = x, \quad \text{father's age six years ago} = 2x", "Use the age six years ago as the unknown, because the problem gives the relation for that time.",
      "نامعلوم مقدار کے لیے چھ سال پہلے کی عمر لیں، کیونکہ مسئلے میں تعلق اسی وقت کا دیا گیا ہے۔"),
    S(r"\text{Present ages: son } x+6, \quad \text{father } 2x+6", "Add 6 years to each age to get the present ages.", "موجودہ عمریں معلوم کرنے کے لیے ہر عمر میں 6 سال جمع کریں۔"),
    S(r"(x+6) + (2x+6) = 72 \;\Rightarrow\; 3x+12 = 72", "The sum of the present ages is 72.", "موجودہ عمروں کا مجموعہ 72 ہے۔", "(x+6) + (2*x+6) == 3*x + 12"),
    S(r"3x = 60 \;\Rightarrow\; x = 20", "Subtract 12 and divide by 3.", "12 منفی کریں اور 3 سے تقسیم کریں۔", "72 - 12 == 60", "Rational(60,3) == 20",
      "(20+6) + (2*20+6) == 72"),
], r"$20$ years"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q7", "exercise", 7, 19, "Mirha bought a toy for Rs. 1500 and sold for Rs. 1520. What was her profit percentage?", one([
    S(r"\text{Profit} = SP - CP = 1520 - 1500 = 20", "Profit is selling price minus cost price.", "منافع = فروخت قیمت − خرید قیمت۔", "1520 - 1500 == 20"),
    S(r"\text{Profit\%} = \frac{20}{1500} \times 100 = 1.33\%", "Profit % = profit / CP × 100.", "منافع فیصد = منافع / خرید قیمت × 100۔",
      "abs(Rational(20*100,1500) - Rational('1.33')) < Rational(1,100)"),
], r"$1.33\%$"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q8", "exercise", 8, 19, "The annual income of Tayyab is Rs. 9,60,000, while the exempted amount is Rs. 1,30,000. How much tax would he have to pay at the rate of 0.75%?", one([
    S(r"\text{Taxable income} = 960000 - 130000 = 830000", "Tax is paid only on the income above the exempted amount.", "ٹیکس صرف مستثنیٰ رقم سے زائد آمدنی پر دیا جاتا ہے۔", "960000 - 130000 == 830000"),
    S(r"\text{Tax} = 830000 \times \frac{0.75}{100} = 6225", "Find 0.75% of the taxable income.", "قابل ٹیکس آمدنی کا 0.75 فیصد نکالیں۔", "830000*Rational(75,10000) == 6225"),
], "Rs. 6225"), exercise="1.3"))

ITEMS.append(Q("ex1.3-q9", "exercise", 9, 19, "Find the compound markup on Rs. 3,75,000 for one year at the rate of 14% compounded annually.", one([
    S(r"A = P\left(1+\frac{r}{100}\right)^t = 375000 \times \left(1+\frac{14}{100}\right)^1 = 375000 \times 1.14 = 427500", "Find the amount after 1 year with the compound formula.",
      "مرکب فارمولے سے ایک سال بعد کی کل رقم معلوم کریں۔", "375000*Rational(114,100) == 427500"),
    S(r"\text{Compound markup} = A - P = 427500 - 375000 = 52500", "The markup is the amount minus the principal.", "منافع = کل رقم − اصل رقم۔", "427500 - 375000 == 52500"),
], "Rs. 52500"), exercise="1.3"))

# =========================================================================================
# REVIEW EXERCISE 1
# =========================================================================================


def mcq(label, prompt, options, correct, steps, key_note=None):
    text = prompt + "  " + "  ".join(f"({k}) {v}" for k, v in options.items())
    part = P(label, steps, correct, prompt=text)
    if key_note:
        part["key_note"] = key_note["log"]
        part["note"] = {"en": key_note["en"], "ur": key_note["ur"]}
    return part


def letter_step(correct, options, why_en, why_ur):
    return T(f"The correct option is ({correct}) {options[correct]}. {why_en}", f"درست جواب ({correct}) {options[correct]} ہے۔ {why_ur}")


o1 = {"a": "integer", "b": "rational number", "c": "irrational number", "d": "natural number"}
o2 = {"a": "natural numbers", "b": "integers", "c": "rational numbers", "d": "irrational numbers"}
o3 = {"a": "rational number", "b": "natural number", "c": "integer", "d": "irrational number"}
o4 = {"a": "whole number", "b": "integer", "c": "rational number", "d": "irrational number"}
o5 = {"a": "reflexive property", "b": "transitive number", "c": "symmetric property", "d": "trichotomy property"}
o6 = {"a": "trichotomy", "b": "transitive", "c": "additive", "d": "multiplicative"}
o7 = {"a": "$\\frac{3}{2}$", "b": "$\\frac{3}{4}$", "c": "$\\frac{5}{6}$", "d": "$\\frac{2}{3}$"}
o8 = {"a": "reflexive", "b": "symmetric", "c": "transitive", "d": "additive"}
o9 = {"a": "$\\sqrt{102}$", "b": "$9\\sqrt{3}$", "c": "$5\\sqrt{3}$", "d": "$8\\sqrt{3}$"}
o10 = {"a": "prime number", "b": "odd number", "c": "irrational number", "d": "rational number"}

rev1 = [
    mcq("i", r"$\sqrt{7}$ is:", o1, "c", [
        S(r"4 < 7 < 9", "7 lies between the consecutive squares 4 and 9, so it is not a perfect square and $\\sqrt{7}$ is irrational.",
          "7 دو متواتر مربعات 4 اور 9 کے درمیان ہے، یہ مکمل مربع نہیں، اس لیے $\\sqrt{7}$ غیر ناطق ہے۔", "floor(sqrt(7))**2 < 7", "(floor(sqrt(7))+1)**2 > 7"),
        letter_step("c", o1, "It is not an integer, not rational and not natural.", "یہ نہ صحیح عدد ہے، نہ ناطق اور نہ قدرتی۔")]),
    mcq("ii", r"$\pi$ and $e$ are:", o2, "d", [
        letter_step("d", o2, "Both $\\pi = 3.14159\\ldots$ and $e = 2.71828\\ldots$ are non-terminating, non-recurring decimals.",
                    "$\\pi = 3.14159\\ldots$ اور $e = 2.71828\\ldots$ دونوں غیر محدود غیر دوری اعشاری اعداد ہیں۔")]),
    mcq("iii", r"If $n$ is not a perfect square, then $\sqrt{n}$ is:", o3, "d", [
        letter_step("d", o3, "A square root that is not a whole number is a non-terminating, non-recurring decimal. For example $\\sqrt{7}$ with 7 between 4 and 9.",
                    "جو جذر مکمل عدد نہ ہو وہ غیر محدود غیر دوری اعشاری عدد ہوتا ہے۔ مثلاً $\\sqrt{7}$ جبکہ 7، 4 اور 9 کے درمیان ہے۔")]),
    mcq("iv", r"$\sqrt{3}+\sqrt{5}$ is:", o4, "d", [
        S(r"(\sqrt{3}+\sqrt{5})^2 = 8+2\sqrt{15}", "Square the number. $\\sqrt{15}$ is irrational because 15 lies between 9 and 16.",
          "عدد کا مربع لیں۔ $\\sqrt{15}$ غیر ناطق ہے کیونکہ 15، 9 اور 16 کے درمیان ہے۔", "(sqrt(3)+sqrt(5))**2 == 8 + 2*sqrt(15)",
          "floor(sqrt(15))**2 < 15", "(floor(sqrt(15))+1)**2 > 15"),
        letter_step("d", o4, "The square is irrational, so $\\sqrt{3}+\\sqrt{5}$ cannot be rational.", "مربع غیر ناطق ہے، اس لیے $\\sqrt{3}+\\sqrt{5}$ ناطق نہیں ہو سکتا۔")]),
    mcq("v", r"For all $x \in R$, $x = x$ is called:", o5, "a", [
        letter_step("a", o5, "Every number is equal to itself: the reflexive property.", "ہر عدد اپنے برابر ہوتا ہے: خاصیت انعکاس۔")]),
    mcq("vi", r"Let $a, b, c \in R$, then $a > b$ and $b > c \Rightarrow a > c$ is called ______ property.", o6, "b", [
        letter_step("b", o6, "If a is greater than b and b is greater than c, then a is greater than c: the transitive property.",
                    "اگر a بڑا ہے b سے اور b بڑا ہے c سے تو a بڑا ہے c سے: خاصیت تعدی۔")]),
    mcq("vii", r"$2^x \times 8^x = 64$ then $x =$", o7, "a", [
        S(r"2^x \times 8^x = 2^x \times 2^{3x} = 2^{4x}", "Write 8 as $2^3$ and add the exponents.", "8 کو $2^3$ لکھیں اور قوتیں جمع کریں۔", "8**x == 2**(3*x)", "2**x*2**(3*x) == 2**(4*x)"),
        S(r"2^{4x} = 64 = 2^6 \;\Rightarrow\; 4x = 6 \;\Rightarrow\; x = \frac{3}{2}", "Equal bases have equal exponents.", "برابر اساس کی صورت میں قوتیں برابر ہوتی ہیں۔",
          "64 == 2**6", "Rational(6,4) == Rational(3,2)", "2**Rational(3,2) * 8**Rational(3,2) == 64"),
        letter_step("a", o7, "Check: $2^{3/2} \\times 8^{3/2} = 16^{3/2} = 64$.", "تصدیق: $2^{3/2} \\times 8^{3/2} = 16^{3/2} = 64$۔")],
        {"log": "The printed key lists (vii) as b, but x = 3/2 is option (a). The key has (vii) and (viii) swapped.",
         "en": "The book's printed answer key says (b) for this part. That is a misprint: x = 3/2, which is option (a). The key appears to have parts (vii) and (viii) swapped.",
         "ur": "کتاب کے آخر میں دیے گئے جوابات میں اس حصے کے لیے (b) لکھا ہے۔ یہ غلطی ہے: x = 3/2 ہے جو (a) ہے۔ ایسا لگتا ہے کہ جوابات میں حصہ (vii) اور (viii) آپس میں بدل گئے ہیں۔"}),
    mcq("viii", r"Let $a, b \in R$, then $a = b$ and $b = a$ is called ______ property.", o8, "b", [
        letter_step("b", o8, "If a = b then b = a: the symmetric property.", "اگر a = b ہو تو b = a: خاصیت تشاکل۔")],
        {"log": "The printed key lists (viii) as a, but a=b => b=a is the symmetric property, option (b). The key has (vii) and (viii) swapped.",
         "en": "The book's printed answer key says (a) for this part. That is a misprint: a = b and b = a is the symmetric property, which is option (b).",
         "ur": "کتاب کے آخر میں دیے گئے جوابات میں اس حصے کے لیے (a) لکھا ہے۔ یہ غلطی ہے: a = b اور b = a خاصیت تشاکل ہے جو (b) ہے۔"}),
    mcq("ix", r"$\sqrt{75}+\sqrt{27} =$", o9, "d", [
        S(r"\sqrt{75} = \sqrt{25 \times 3} = 5\sqrt{3}, \qquad \sqrt{27} = \sqrt{9 \times 3} = 3\sqrt{3}", "Take out the perfect squares from under the roots.",
          "جذروں کے نیچے سے مکمل مربع باہر نکالیں۔", "sqrt(75) == 5*sqrt(3)", "sqrt(27) == 3*sqrt(3)"),
        S(r"5\sqrt{3}+3\sqrt{3} = 8\sqrt{3}", "Add the like terms.", "ملتے جلتے ارکان جمع کریں۔", "5*sqrt(3) + 3*sqrt(3) == 8*sqrt(3)", "sqrt(75) + sqrt(27) == 8*sqrt(3)"),
        letter_step("d", o9, "", "")]),
    mcq("x", r"The product of $(3+\sqrt{5})(3-\sqrt{5})$ is:", o10, "d", [
        S(r"(3+\sqrt{5})(3-\sqrt{5}) = 3^2-(\sqrt{5})^2 = 9-5 = 4", "Use $(a+b)(a-b) = a^2-b^2$.", "$(a+b)(a-b) = a^2-b^2$ استعمال کریں۔", "(3+sqrt(5))*(3-sqrt(5)) == 4"),
        letter_step("d", o10, "4 is a rational number (it is also not prime and not odd).", "4 ناطق عدد ہے (یہ مفرد اور طاق بھی نہیں)۔")]),
]
ITEMS.append(Q("rev1-q1", "review", 1, 19, "Four options are given against each statement. Encircle the correct option.", rev1, exercise="Review 1"))

ITEMS.append(Q("rev1-q2", "review", 2, 20, "If $a = \\frac{3}{2}$, $b = \\frac{5}{3}$ and $c = \\frac{7}{5}$, then verify that (i) $a(b+c) = ab+ac$ (ii) $(a+b)c = ac+bc$",
               distributive_parts(_R(3, 2), _R(5, 3), _R(7, 5)), exercise="Review 1"))
ITEMS.append(Q("rev1-q3", "review", 3, 20, "If $a = \\frac{4}{3}$, $b = \\frac{5}{2}$ and $c = \\frac{7}{4}$, then verify the associative property of real numbers w.r.t. addition and multiplication.",
               associative_parts(_R(4, 3), _R(5, 2), _R(7, 4)), exercise="Review 1"))
ITEMS.append(Q("rev1-q4", "review", 4, 20, "Is 0 a rational number? Explain.", one([
    S(r"0 = \frac{0}{1}", "A rational number is a number that can be written as $\\frac{p}{q}$ with p and q integers and $q \\neq 0$. Here p = 0 and q = 1.",
      "ناطق عدد وہ ہے جسے $\\frac{p}{q}$ کی شکل میں لکھا جا سکے جہاں p اور q صحیح اعداد ہوں اور $q \\neq 0$ ہو۔ یہاں p = 0 اور q = 1 ہے۔", "Rational(0,1) == 0"),
    T("So 0 can be written in the form $\\frac{p}{q}$ and it is a rational number.", "اس لیے 0 کو $\\frac{p}{q}$ کی شکل میں لکھا جا سکتا ہے اور یہ ناطق عدد ہے۔")],
    "Yes, 0 is a rational number because $0 = \\frac{0}{1}$."), exercise="Review 1"))
ITEMS.append(Q("rev1-q5", "review", 5, 20, "State trichotomy property of real numbers.", one([
    T("The trichotomy property says: for any two real numbers a and b, exactly one of the three relations is true: a = b, a > b or a < b.",
      "خاصیت سہ شقی کہتی ہے: کسی بھی دو حقیقی اعداد a اور b کے لیے تین رشتوں میں سے ایک اور صرف ایک درست ہوتا ہے: a = b، a > b یا a < b۔")],
    "For all $a, b \\in R$, either $a = b$ or $a > b$ or $a < b$."), exercise="Review 1"))
ITEMS.append(Q("rev1-q6", "review", 6, 20, "Find two rational numbers between 4 and 5.", [
    between_part("", "4", "5", _R(4), _R(5), _R(9, 2), _R(19, 4))], exercise="Review 1"))

q7 = [
    P("i", [
        S(r"\frac{x^{15} y^{35}}{z^{20}} \text{ under a fifth root} \;\Rightarrow\; \left(\frac{x^{15} y^{35}}{z^{20}}\right)^{\frac{1}{5}}", "Write the 5th root as the power $\\frac{1}{5}$.",
          "پانچویں جذر کو طاقت $\\frac{1}{5}$ کی شکل میں لکھیں۔"),
        S(r"= \frac{x^{15 \times \frac{1}{5}} \, y^{35 \times \frac{1}{5}}}{z^{20 \times \frac{1}{5}}} = \frac{x^3 y^7}{z^4}", "Multiply each exponent by $\\frac{1}{5}$.", "ہر قوت کو $\\frac{1}{5}$ سے ضرب دیں۔",
          "(x**15*y**35/z**20)**Rational(1,5) == x**3*y**7/z**4", "Rational(15,5) == 3", "Rational(35,5) == 7", "Rational(20,5) == 4"),
    ], r"$\frac{x^3 y^7}{z^4}$", prompt=r"$\sqrt[5]{\frac{x^{15} y^{35}}{z^{20}}}$"),
    P("ii", [
        S(r"\sqrt[3]{(27)^{2x}} = \left((3^3)^{2x}\right)^{\frac{1}{3}} = 3^{3 \times 2x \times \frac{1}{3}} = 3^{2x}", "Write 27 as $3^3$ and multiply the exponents.",
          "27 کو $3^3$ لکھیں اور قوتیں ضرب دیں۔", "cbrt(27**(2*x)) == 3**(2*x)"),
    ], r"$3^{2x}$", prompt=r"$\sqrt[3]{(27)^{2x}}$"),
    P("iii", [
        S(r"6(3)^{n+2} = 6 \cdot 3^n \cdot 3^2 = 54 \cdot 3^n", "Split the power: $3^{n+2} = 3^n \\cdot 3^2$.", "طاقت کو توڑیں: $3^{n+2} = 3^n \\cdot 3^2$۔", "6*3**(n+2) == 54*3**n"),
        S(r"3^{n+1} - 3^n = 3^n(3-1) = 2 \cdot 3^n", "Take out the common factor $3^n$ in the denominator.", "نسب نما میں مشترک جزو $3^n$ نکالیں۔", "3**(n+1) - 3**n == 2*3**n"),
        S(r"\frac{54 \cdot 3^n}{2 \cdot 3^n} = 27", "Cancel $3^n$ and divide 54 by 2.", "$3^n$ کاٹیں اور 54 کو 2 سے تقسیم کریں۔", "Rational(54,2) == 27"),
    ], "$27$", prompt=r"$\frac{6(3)^{n+2}}{3^{n+1} - 3^n}$"),
]
ITEMS.append(Q("rev1-q7", "review", 7, 20, "Simplify the following: (i) $\\sqrt[5]{\\frac{x^{15} y^{35}}{z^{20}}}$ (ii) $\\sqrt[3]{(27)^{2x}}$ (iii) $\\frac{6(3)^{n+2}}{3^{n+1} - 3^n}$", q7, exercise="Review 1"))

ITEMS.append(Q("rev1-q8", "review", 8, 20, "The sum of three consecutive odd integers is 51. Find the three integers.", one([
    S(r"\text{Let the odd integers be } x,\; x+2,\; x+4", "Consecutive odd integers differ by 2.", "متواتر طاق اعداد میں 2 کا فرق ہوتا ہے۔"),
    S(r"x + (x+2) + (x+4) = 51 \;\Rightarrow\; 3x+6 = 51", "Their sum is 51.", "ان کا مجموعہ 51 ہے۔", "x + (x+2) + (x+4) == 3*x + 6"),
    S(r"3x = 45 \;\Rightarrow\; x = 15", "Subtract 6, then divide by 3.", "6 منفی کریں، پھر 3 سے تقسیم کریں۔", "51 - 6 == 45", "Rational(45,3) == 15"),
    S(r"x = 15,\quad x+2 = 17,\quad x+4 = 19", "Put x = 15 back.", "x = 15 واپس رکھیں۔", "15 + 17 + 19 == 51"),
], "$15,\\ 17,\\ 19$"), exercise="Review 1"))

ITEMS.append(Q("rev1-q9", "review", 9, 20, "Abdullah picked up 96 balls and placed them into two buckets. One bucket has twenty-eight more balls than the other bucket. How many balls were in each bucket?", one([
    S(r"\text{Smaller bucket} = x, \quad \text{larger bucket} = x+28", "Let the smaller bucket hold x balls; the other holds 28 more.", "چھوٹی بالٹی میں x گیندیں فرض کریں؛ دوسری میں 28 زیادہ ہیں۔"),
    S(r"x + (x+28) = 96 \;\Rightarrow\; 2x = 68 \;\Rightarrow\; x = 34", "The two buckets hold 96 balls together.", "دونوں بالٹیوں میں کل 96 گیندیں ہیں۔", "x + (x+28) == 2*x + 28", "96 - 28 == 68", "Rational(68,2) == 34"),
    S(r"34 \quad \text{and} \quad 34+28 = 62", "The larger bucket has 28 more balls.", "بڑی بالٹی میں 28 گیندیں زیادہ ہیں۔", "34 + 62 == 96", "62 - 34 == 28"),
], "$34,\\ 62$"), exercise="Review 1"))

ITEMS.append(Q("rev1-q10", "review", 10, 20, "Salma invested Rs. 3,50,000 in a bank, which paid simple profit at the rate of $7\\frac{1}{4}\\%$ per annum. After 2 years, the rate was increased to 8% per annum. "
               "Find the amount she had at the end of 7 years.", one([
    S(r"\text{Profit for the first 2 years} = 350000 \times \frac{7.25}{100} \times 2 = 50750", "Simple profit = principal × rate × time. The rate is $7\\frac{1}{4}\\% = 7.25\\%$.",
      "سادہ منافع = اصل × شرح × وقت۔ شرح $7\\frac{1}{4}\\% = 7.25\\%$ ہے۔", "350000*Rational(725,10000)*2 == 50750"),
    S(r"\text{Profit for the next 5 years} = 350000 \times \frac{8}{100} \times 5 = 140000", "After 2 years the rate is 8% for the remaining 7 − 2 = 5 years.",
      "2 سال بعد باقی 7 − 2 = 5 سالوں کے لیے شرح 8 فیصد ہے۔", "350000*Rational(8,100)*5 == 140000", "7 - 2 == 5"),
    S(r"\text{Amount} = 350000 + 50750 + 140000 = 540750", "Add the principal and both profits.", "اصل رقم اور دونوں منافع جمع کریں۔", "350000 + 50750 + 140000 == 540750"),
], "Rs. 540750"), exercise="Review 1"))
