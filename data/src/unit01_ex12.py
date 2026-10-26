"""Unit 1 - Real Numbers: Exercise 1.2 (radical expressions and laws of indices), printed pages 13-14."""
from _helpers import P, Q, S, T

UNIT = {"unit": 1, "title": "Real Numbers", "title_ur": "حقیقی اعداد", "items": []}
ITEMS = UNIT["items"]

CONJ = ("Multiply the numerator and the denominator by the conjugate of the denominator.",
        "شمار کنندہ اور نسب نما کو نسب نما کے مزدوج سے ضرب دیں۔")
DIFF_SQ = ("Use $(a+b)(a-b) = a^2-b^2$ in the denominator.", "نسب نما میں $(a+b)(a-b) = a^2-b^2$ استعمال کریں۔")


# =========================================================================================
# Q1: rationalize the denominator
# =========================================================================================
q1 = [
    P("i", [
        S(r"\frac{13}{4+\sqrt{3}} \times \frac{4-\sqrt{3}}{4-\sqrt{3}}", *CONJ, "13/(4+sqrt(3)) == 13*(4-sqrt(3))/(4**2 - 3)"),
        S(r"= \frac{13(4-\sqrt{3})}{4^2-(\sqrt{3})^2} = \frac{13(4-\sqrt{3})}{13}", *DIFF_SQ, "4**2 - sqrt(3)**2 == 13"),
        S(r"= 4-\sqrt{3}", "Cancel 13 from the numerator and the denominator.", "شمار کنندہ اور نسب نما سے 13 کاٹ دیں۔", "13*(4-sqrt(3))/13 == 4 - sqrt(3)"),
    ], r"$4-\sqrt{3}$", prompt=r"$\frac{13}{4+\sqrt{3}}$"),
    P("ii", [
        S(r"\frac{\sqrt{2}+\sqrt{5}}{\sqrt{3}} \times \frac{\sqrt{3}}{\sqrt{3}}", "The denominator is a single root, so multiply the numerator and the denominator by $\\sqrt{3}$.",
          "نسب نما ایک ہی جذر ہے، اس لیے شمار کنندہ اور نسب نما کو $\\sqrt{3}$ سے ضرب دیں۔", "(sqrt(2)+sqrt(5))/sqrt(3) == (sqrt(2)+sqrt(5))*sqrt(3)/3"),
        S(r"= \frac{\sqrt{2}\sqrt{3}+\sqrt{5}\sqrt{3}}{3} = \frac{\sqrt{6}+\sqrt{15}}{3}", "Multiply the roots: $\\sqrt{a}\\sqrt{b} = \\sqrt{ab}$.",
          "جذروں کو ضرب دیں: $\\sqrt{a}\\sqrt{b} = \\sqrt{ab}$۔", "sqrt(2)*sqrt(3) == sqrt(6)", "sqrt(5)*sqrt(3) == sqrt(15)"),
    ], r"$\frac{\sqrt{6}+\sqrt{15}}{3}$", prompt=r"$\frac{\sqrt{2}+\sqrt{5}}{\sqrt{3}}$"),
    P("iii", [
        S(r"\frac{\sqrt{2}-1}{\sqrt{5}} \times \frac{\sqrt{5}}{\sqrt{5}}", "Multiply the numerator and the denominator by $\\sqrt{5}$.",
          "شمار کنندہ اور نسب نما کو $\\sqrt{5}$ سے ضرب دیں۔", "(sqrt(2)-1)/sqrt(5) == (sqrt(2)-1)*sqrt(5)/5"),
        S(r"= \frac{\sqrt{2}\sqrt{5}-\sqrt{5}}{5} = \frac{\sqrt{10}-\sqrt{5}}{5}", "Multiply the roots: $\\sqrt{2}\\sqrt{5} = \\sqrt{10}$.",
          "جذروں کو ضرب دیں: $\\sqrt{2}\\sqrt{5} = \\sqrt{10}$۔", "sqrt(2)*sqrt(5) == sqrt(10)"),
    ], r"$\frac{\sqrt{10}-\sqrt{5}}{5}$", prompt=r"$\frac{\sqrt{2}-1}{\sqrt{5}}$"),
    P("iv", [
        S(r"\frac{6-4\sqrt{2}}{6+4\sqrt{2}} \times \frac{6-4\sqrt{2}}{6-4\sqrt{2}} = \frac{(6-4\sqrt{2})^2}{6^2-(4\sqrt{2})^2}", *CONJ,
          "(6-4*sqrt(2))/(6+4*sqrt(2)) == (6-4*sqrt(2))**2/(6**2 - (4*sqrt(2))**2)"),
        S(r"(6-4\sqrt{2})^2 = 36-48\sqrt{2}+32 = 68-48\sqrt{2}, \qquad 6^2-(4\sqrt{2})^2 = 36-32 = 4",
          "Expand the numerator with $(a-b)^2 = a^2-2ab+b^2$ and simplify the denominator.",
          "شمار کنندہ کو $(a-b)^2 = a^2-2ab+b^2$ سے پھیلائیں اور نسب نما سادہ کریں۔",
          "(6-4*sqrt(2))**2 == 68 - 48*sqrt(2)", "6**2 - (4*sqrt(2))**2 == 4"),
        S(r"= \frac{68-48\sqrt{2}}{4} = 17-12\sqrt{2}", "Divide each term by 4.", "ہر رکن کو 4 سے تقسیم کریں۔", "(68-48*sqrt(2))/4 == 17 - 12*sqrt(2)"),
    ], r"$17-12\sqrt{2}$", prompt=r"$\frac{6-4\sqrt{2}}{6+4\sqrt{2}}$"),
    P("v", [
        S(r"\frac{\sqrt{3}-\sqrt{2}}{\sqrt{3}+\sqrt{2}} \times \frac{\sqrt{3}-\sqrt{2}}{\sqrt{3}-\sqrt{2}} = \frac{(\sqrt{3}-\sqrt{2})^2}{(\sqrt{3})^2-(\sqrt{2})^2}", *CONJ,
          "(sqrt(3)-sqrt(2))/(sqrt(3)+sqrt(2)) == (sqrt(3)-sqrt(2))**2/(3-2)"),
        S(r"(\sqrt{3}-\sqrt{2})^2 = 3-2\sqrt{6}+2 = 5-2\sqrt{6}, \qquad (\sqrt{3})^2-(\sqrt{2})^2 = 3-2 = 1",
          "Expand the numerator; the denominator becomes 1.", "شمار کنندہ کو پھیلائیں؛ نسب نما 1 ہو جاتا ہے۔",
          "(sqrt(3)-sqrt(2))**2 == 5 - 2*sqrt(6)", "sqrt(3)**2 - sqrt(2)**2 == 1"),
        S(r"= 5-2\sqrt{6}", "Dividing by 1 changes nothing.", "1 سے تقسیم کرنے سے کچھ نہیں بدلتا۔", "(5-2*sqrt(6))/1 == 5 - 2*sqrt(6)"),
    ], r"$5-2\sqrt{6}$", prompt=r"$\frac{\sqrt{3}-\sqrt{2}}{\sqrt{3}+\sqrt{2}}$"),
    P("vi", [
        S(r"\frac{4\sqrt{3}}{\sqrt{7}+\sqrt{5}} \times \frac{\sqrt{7}-\sqrt{5}}{\sqrt{7}-\sqrt{5}} = \frac{4\sqrt{3}(\sqrt{7}-\sqrt{5})}{(\sqrt{7})^2-(\sqrt{5})^2}", *CONJ,
          "4*sqrt(3)/(sqrt(7)+sqrt(5)) == 4*sqrt(3)*(sqrt(7)-sqrt(5))/(7-5)"),
        S(r"(\sqrt{7})^2-(\sqrt{5})^2 = 7-5 = 2", *DIFF_SQ, "sqrt(7)**2 - sqrt(5)**2 == 2"),
        S(r"= \frac{4\sqrt{3}(\sqrt{7}-\sqrt{5})}{2} = 2\sqrt{3}(\sqrt{7}-\sqrt{5})", "Divide 4 by 2.", "4 کو 2 سے تقسیم کریں۔",
          "4*sqrt(3)*(sqrt(7)-sqrt(5))/2 == 2*sqrt(3)*(sqrt(7)-sqrt(5))"),
    ], r"$2\sqrt{3}(\sqrt{7}-\sqrt{5})$", prompt=r"$\frac{4\sqrt{3}}{\sqrt{7}+\sqrt{5}}$"),
]
ITEMS.append(Q("ex1.2-q1", "exercise", 1, 13, "Rationalize the denominator of the following: (i) $\\frac{13}{4+\\sqrt{3}}$ (ii) $\\frac{\\sqrt{2}+\\sqrt{5}}{\\sqrt{3}}$ "
               "(iii) $\\frac{\\sqrt{2}-1}{\\sqrt{5}}$ (iv) $\\frac{6-4\\sqrt{2}}{6+4\\sqrt{2}}$ (v) $\\frac{\\sqrt{3}-\\sqrt{2}}{\\sqrt{3}+\\sqrt{2}}$ (vi) $\\frac{4\\sqrt{3}}{\\sqrt{7}+\\sqrt{5}}$",
               q1, exercise="1.2"))

# =========================================================================================
# Q2: simplify with the laws of indices
# =========================================================================================
NEG = ("A negative exponent means the reciprocal: $a^{-m} = \\frac{1}{a^m}$.", "منفی طاقت کا مطلب معکوس ہے: $a^{-m} = \\frac{1}{a^m}$۔")
POW = ("Write the numbers as powers and use $(a^m)^n = a^{mn}$.", "اعداد کو طاقت کی شکل میں لکھیں اور $(a^m)^n = a^{mn}$ استعمال کریں۔")
BASE = ("Write every base as a power of the same number so the laws of indices can be used.",
        "ہر اساس کو ایک ہی عدد کی طاقت کی شکل میں لکھیں تاکہ قوانین قوت استعمال ہو سکیں۔")

q2 = [
    P("i", [
        S(r"\left(\frac{81}{16}\right)^{-\frac{3}{4}} = \left(\frac{16}{81}\right)^{\frac{3}{4}}", *NEG,
          "Rational(81,16)**Rational(-3,4) == Rational(16,81)**Rational(3,4)"),
        S(r"= \left(\frac{2^4}{3^4}\right)^{\frac{3}{4}} = \left(\frac{2}{3}\right)^{4 \times \frac{3}{4}} = \left(\frac{2}{3}\right)^3", *POW,
          "Rational(16,81) == Rational(2,3)**4", "(Rational(2,3)**4)**Rational(3,4) == Rational(2,3)**3"),
        S(r"= \frac{8}{27}", "Cube the fraction: $\\frac{2^3}{3^3}$.", "کسر کا مکعب لیں: $\\frac{2^3}{3^3}$۔", "Rational(2,3)**3 == Rational(8,27)"),
    ], r"$\frac{8}{27}$", prompt=r"$\left(\frac{81}{16}\right)^{-\frac{3}{4}}$"),
    P("ii", [
        S(r"\left(\frac{3}{4}\right)^{-2} = \left(\frac{4}{3}\right)^{2} = \frac{16}{9}", *NEG, "Rational(3,4)**(-2) == Rational(16,9)"),
        S(r"\left(\frac{4}{9}\right)^{3} = \frac{64}{729}", "Cube the numerator and the denominator.", "شمار کنندہ اور نسب نما کا مکعب لیں۔", "Rational(4,9)**3 == Rational(64,729)"),
        S(r"\frac{16}{9} \div \frac{64}{729} \times \frac{16}{27} = \frac{16}{9} \times \frac{729}{64} \times \frac{16}{27} = 12",
          "Division by a fraction is multiplication by its reciprocal. Then multiply and cancel.",
          "کسر سے تقسیم کا مطلب اس کے معکوس سے ضرب ہے۔ پھر ضرب دیں اور کاٹیں۔",
          "Rational(16,9)/Rational(64,729)*Rational(16,27) == 12"),
    ], "$12$", prompt=r"$\left(\frac{3}{4}\right)^{-2} \div \left(\frac{4}{9}\right)^{3} \times \frac{16}{27}$"),
    P("iii", [
        S(r"(0.027)^{-\frac{1}{3}} = \left(\frac{27}{1000}\right)^{-\frac{1}{3}} = \left(\frac{3^3}{10^3}\right)^{-\frac{1}{3}}", "Write 0.027 as a fraction and then as cubes.",
          "0.027 کو کسر اور پھر مکعبوں کی شکل میں لکھیں۔", "Rational('0.027') == Rational(27,1000)", "Rational(27,1000) == Rational(3,10)**3"),
        S(r"= \left(\frac{3}{10}\right)^{3 \times \left(-\frac{1}{3}\right)} = \left(\frac{3}{10}\right)^{-1}", "Multiply the exponents: $(a^m)^n = a^{mn}$.",
          "قوتوں کو ضرب دیں: $(a^m)^n = a^{mn}$۔", "(Rational(3,10)**3)**Rational(-1,3) == Rational(3,10)**(-1)"),
        S(r"= \frac{10}{3}", "A power of $-1$ gives the reciprocal.", "طاقت $-1$ معکوس دیتی ہے۔", "Rational(3,10)**(-1) == Rational(10,3)"),
    ], r"$\frac{10}{3}$", prompt=r"$(0.027)^{-\frac{1}{3}}$"),
    P("iv", [
        S(r"\frac{x^{14} y^{21} z^{35}}{y^{14} z^{7}} = x^{14} y^{21-14} z^{35-7} = x^{14} y^{7} z^{28}", "Inside the root, divide powers of the same base by subtracting the exponents: $\\frac{a^m}{a^n} = a^{m-n}$.",
          "جذر کے اندر ایک ہی اساس کی طاقتوں کی تقسیم میں قوتیں منفی کریں: $\\frac{a^m}{a^n} = a^{m-n}$۔",
          "x**14*y**21*z**35/(y**14*z**7) == x**14*y**7*z**28"),
        S(r"\sqrt[7]{x^{14} y^{7} z^{28}} = \left(x^{14} y^{7} z^{28}\right)^{\frac{1}{7}} = x^{2} y\, z^{4}", "Write the 7th root as the power $\\frac{1}{7}$ and multiply each exponent by $\\frac{1}{7}$.",
          "ساتویں جذر کو طاقت $\\frac{1}{7}$ کی شکل میں لکھیں اور ہر قوت کو $\\frac{1}{7}$ سے ضرب دیں۔",
          "(x**14*y**7*z**28)**Rational(1,7) == x**2*y*z**4"),
    ], r"$x^2 y z^4$", prompt=r"$\sqrt[7]{\frac{x^{14} \times y^{21} \times z^{35}}{y^{14} z^{7}}}$"),
    P("v", [
        S(r"5 \cdot 25^{n+1} = 5 \cdot 5^{2n+2} = 5^{2n+3}, \qquad 25 \cdot 5^{2n} = 5^{2n+2}", *BASE,
          "5*25**(n+1) == 5**(2*n+3)", "25*5**(2*n) == 5**(2*n+2)"),
        S(r"5 \cdot 5^{2n+3} = 5^{2n+4}, \qquad 25^{n+1} = 5^{2n+2}", "Do the same for the denominator.", "نسب نما کے ساتھ بھی یہی کریں۔",
          "5*5**(2*n+3) == 5**(2*n+4)", "25**(n+1) == 5**(2*n+2)"),
        S(r"\frac{5^{2n+3}-5^{2n+2}}{5^{2n+4}-5^{2n+2}} = \frac{5^{2n+2}(5-1)}{5^{2n+2}(5^2-1)} = \frac{4}{24}",
          "Take out the common factor $5^{2n+2}$ from the numerator and the denominator.", "شمار کنندہ اور نسب نما سے مشترک جزو $5^{2n+2}$ نکالیں۔",
          "5**(2*n+3) - 5**(2*n+2) == 5**(2*n+2)*(5-1)", "5**(2*n+4) - 5**(2*n+2) == 5**(2*n+2)*(5**2-1)"),
        S(r"= \frac{1}{6}", "Cancel the common factor 4.", "مشترک جزو 4 کاٹ دیں۔", "Rational(4,24) == Rational(1,6)"),
    ], r"$\frac{1}{6}$", prompt=r"$\frac{5\cdot(25)^{n+1} - 25\cdot(5)^{2n}}{5\cdot(5)^{2n+3} - (25)^{n+1}}$"),
    P("vi", [
        S(r"16^{x+1} = 2^{4x+4}, \qquad 4^{2x} = 2^{4x}", *BASE, "16**(x+1) == 2**(4*x+4)", "4**(2*x) == 2**(4*x)"),
        S(r"2^{x-3} \times 8^{x+2} = 2^{x-3} \times 2^{3x+6} = 2^{4x+3}", "Write 8 as $2^3$ and add the exponents when multiplying: $a^m \\cdot a^n = a^{m+n}$.",
          "8 کو $2^3$ لکھیں اور ضرب میں قوتیں جمع کریں: $a^m \\cdot a^n = a^{m+n}$۔", "8**(x+2) == 2**(3*x+6)", "2**(x-3)*2**(3*x+6) == 2**(4*x+3)"),
        S(r"\frac{2^{4x+4}+20 \cdot 2^{4x}}{2^{4x+3}} = \frac{2^{4x}(16+20)}{2^{4x} \cdot 8} = \frac{36}{8}",
          "Take out the common factor $2^{4x}$.", "مشترک جزو $2^{4x}$ نکالیں۔",
          "2**(4*x+4) + 20*2**(4*x) == 2**(4*x)*(16+20)", "2**(4*x+3) == 2**(4*x)*8"),
        S(r"= \frac{9}{2}", "Cancel the common factor 4.", "مشترک جزو 4 کاٹ دیں۔", "Rational(36,8) == Rational(9,2)"),
    ], r"$\frac{9}{2}$", prompt=r"$\frac{(16)^{x+1} + 20(4^{2x})}{2^{x-3} \times 8^{x+2}}$"),
    P("vii", [
        S(r"64^{-\frac{2}{3}} = (4^3)^{-\frac{2}{3}} = 4^{-2} = \frac{1}{16}", *POW, "64**Rational(-2,3) == Rational(1,16)"),
        S(r"9^{-\frac{3}{2}} = (3^2)^{-\frac{3}{2}} = 3^{-3} = \frac{1}{27}", *POW, "9**Rational(-3,2) == Rational(1,27)"),
        S(r"\frac{1}{16} \div \frac{1}{27} = \frac{1}{16} \times 27 = \frac{27}{16}", "Divide by a fraction by multiplying with its reciprocal.",
          "کسر سے تقسیم اس کے معکوس سے ضرب کے برابر ہے۔", "Rational(1,16)/Rational(1,27) == Rational(27,16)"),
    ], r"$\frac{27}{16}$", prompt=r"$(64)^{-\frac{2}{3}} \div (9)^{-\frac{3}{2}}$"),
    P("viii", [
        S(r"9^{n+1} = 3^{2n+2}, \qquad 9^{n-1} = 3^{2n-2}", *BASE, "9**(n+1) == 3**(2*n+2)", "9**(n-1) == 3**(2*n-2)"),
        S(r"\frac{3^n \cdot 3^{2n+2}}{3^{n-1} \cdot 3^{2n-2}} = \frac{3^{3n+2}}{3^{3n-3}}", "Add the exponents in the numerator and in the denominator.",
          "شمار کنندہ اور نسب نما میں قوتیں جمع کریں۔", "3**n*3**(2*n+2) == 3**(3*n+2)", "3**(n-1)*3**(2*n-2) == 3**(3*n-3)"),
        S(r"= 3^{(3n+2)-(3n-3)} = 3^5 = 243", "Divide powers of the same base by subtracting the exponents.",
          "ایک ہی اساس کی طاقتوں کی تقسیم میں قوتیں منفی کریں۔", "3**(3*n+2)/3**(3*n-3) == 3**5", "3**5 == 243"),
    ], "$243$", prompt=r"$\frac{3^n \times 9^{n+1}}{3^{n-1} \times 9^{n-1}}$"),
    P("ix", [
        S(r"5^{n+3} - 6 \cdot 5^{n+1} = 5^n(5^3 - 6 \cdot 5) = 5^n(125-30) = 95 \cdot 5^n", "Take out the common factor $5^n$ from the numerator.",
          "شمار کنندہ سے مشترک جزو $5^n$ نکالیں۔", "5**(n+3) - 6*5**(n+1) == 5**n*(125-30)", "125-30 == 95"),
        S(r"9 \cdot 5^n - 4 \cdot 5^n = 5^n(9-4) = 5 \cdot 5^n", "Do the same in the denominator.", "نسب نما میں بھی یہی کریں۔", "9*5**n - 4*5**n == 5**n*(9-4)"),
        S(r"\frac{95 \cdot 5^n}{5 \cdot 5^n} = 19", "Cancel $5^n$ and divide 95 by 5.", "$5^n$ کاٹیں اور 95 کو 5 سے تقسیم کریں۔", "Rational(95,5) == 19"),
    ], "$19$", prompt=r"$\frac{5^{n+3} - 6 \cdot 5^{n+1}}{9 \times 5^n - 4 \times 5^n}$"),
]
ITEMS.append(Q("ex1.2-q2", "exercise", 2, 14, "Simplify the following: (i) $\\left(\\frac{81}{16}\\right)^{-\\frac{3}{4}}$ (ii) $\\left(\\frac{3}{4}\\right)^{-2} \\div \\left(\\frac{4}{9}\\right)^{3} \\times \\frac{16}{27}$ "
               "(iii) $(0.027)^{-\\frac{1}{3}}$ (iv) $\\sqrt[7]{\\frac{x^{14} \\times y^{21} \\times z^{35}}{y^{14} z^{7}}}$ (v) $\\frac{5\\cdot(25)^{n+1} - 25\\cdot(5)^{2n}}{5\\cdot(5)^{2n+3} - (25)^{n+1}}$ "
               "(vi) $\\frac{(16)^{x+1} + 20(4^{2x})}{2^{x-3} \\times 8^{x+2}}$ (vii) $(64)^{-\\frac{2}{3}} \\div (9)^{-\\frac{3}{2}}$ (viii) $\\frac{3^n \\times 9^{n+1}}{3^{n-1} \\times 9^{n-1}}$ "
               "(ix) $\\frac{5^{n+3} - 6 \\cdot 5^{n+1}}{9 \\times 5^n - 4 \\times 5^n}$", q2, exercise="1.2"))


# =========================================================================================
# Q3: x = 3 + sqrt(8)
# =========================================================================================
INV = S(r"\frac{1}{x} = \frac{1}{3+\sqrt{8}} \times \frac{3-\sqrt{8}}{3-\sqrt{8}} = \frac{3-\sqrt{8}}{9-8} = 3-\sqrt{8}",
        "First find $\\frac{1}{x}$ by rationalizing: multiply by the conjugate $3-\\sqrt{8}$.",
        "پہلے $\\frac{1}{x}$ نکالیں: مزدوج $3-\\sqrt{8}$ سے ضرب دے کر نسب نما کو ناطق بنائیں۔",
        "1/(3+sqrt(8)) == 3 - sqrt(8)", "3**2 - sqrt(8)**2 == 1")


def inv_step():
    return {**INV}


q3 = [
    P("i", [inv_step(),
            S(r"x+\frac{1}{x} = (3+\sqrt{8}) + (3-\sqrt{8}) = 6", "Add. The $\\sqrt{8}$ terms cancel.", "جمع کریں۔ $\\sqrt{8}$ والے رکن ختم ہو جاتے ہیں۔",
              "(3+sqrt(8)) + (3-sqrt(8)) == 6")], "$6$", prompt=r"$x+\frac{1}{x}$"),
    P("ii", [inv_step(),
             S(r"x-\frac{1}{x} = (3+\sqrt{8}) - (3-\sqrt{8}) = 2\sqrt{8}", "Subtract. The 3s cancel.", "منفی کریں۔ 3 ختم ہو جاتے ہیں۔",
               "(3+sqrt(8)) - (3-sqrt(8)) == 2*sqrt(8)")], r"$2\sqrt{8}$", prompt=r"$x-\frac{1}{x}$"),
    P("iii", [inv_step(),
              S(r"x+\frac{1}{x} = 6", "From part (i).", "حصہ (i) سے۔", "(3+sqrt(8)) + (3-sqrt(8)) == 6"),
              S(r"\left(x+\frac{1}{x}\right)^2 = x^2+2+\frac{1}{x^2} \;\Rightarrow\; x^2+\frac{1}{x^2} = 6^2-2 = 34",
                "Square both sides and use $(a+b)^2 = a^2+2ab+b^2$.", "دونوں طرف مربع لیں اور $(a+b)^2 = a^2+2ab+b^2$ استعمال کریں۔",
                "(3+sqrt(8))**2 + (3-sqrt(8))**2 == 6**2 - 2", "6**2 - 2 == 34")], "$34$", prompt=r"$x^2+\frac{1}{x^2}$"),
    P("iv", [inv_step(),
             S(r"x+\frac{1}{x} = 6, \qquad x-\frac{1}{x} = 2\sqrt{8}", "Use the results of parts (i) and (ii).", "حصہ (i) اور (ii) کے نتائج استعمال کریں۔",
               "(3+sqrt(8)) + (3-sqrt(8)) == 6", "(3+sqrt(8)) - (3-sqrt(8)) == 2*sqrt(8)"),
             S(r"x^2-\frac{1}{x^2} = \left(x+\frac{1}{x}\right)\left(x-\frac{1}{x}\right) = 6 \times 2\sqrt{8} = 12\sqrt{8}",
               "Use $a^2-b^2 = (a+b)(a-b)$.", "$a^2-b^2 = (a+b)(a-b)$ استعمال کریں۔",
               "(3+sqrt(8))**2 - (3-sqrt(8))**2 == 6*2*sqrt(8)", "6*2*sqrt(8) == 12*sqrt(8)")], r"$12\sqrt{8}$", prompt=r"$x^2-\frac{1}{x^2}$"),
    P("v", [inv_step(),
            S(r"x^2+\frac{1}{x^2} = 34", "From part (iii).", "حصہ (iii) سے۔", "(3+sqrt(8))**2 + (3-sqrt(8))**2 == 34"),
            S(r"\left(x^2+\frac{1}{x^2}\right)^2 = x^4+2+\frac{1}{x^4} \;\Rightarrow\; x^4+\frac{1}{x^4} = 34^2-2 = 1154",
              "Square both sides again.", "دونوں طرف دوبارہ مربع لیں۔", "(3+sqrt(8))**4 + (3-sqrt(8))**4 == 34**2 - 2", "34**2 - 2 == 1154")],
      "$1154$", prompt=r"$x^4+\frac{1}{x^4}$"),
    P("vi", [inv_step(),
             S(r"x-\frac{1}{x} = 2\sqrt{8}", "From part (ii).", "حصہ (ii) سے۔", "(3+sqrt(8)) - (3-sqrt(8)) == 2*sqrt(8)"),
             S(r"\left(x-\frac{1}{x}\right)^2 = (2\sqrt{8})^2 = 4 \times 8 = 32", "Square $2\\sqrt{8}$: $(\\sqrt{8})^2 = 8$.", "$2\\sqrt{8}$ کا مربع لیں: $(\\sqrt{8})^2 = 8$۔",
               "((3+sqrt(8)) - (3-sqrt(8)))**2 == 32", "(2*sqrt(8))**2 == 32")], "$32$", prompt=r"$\left(x-\frac{1}{x}\right)^2$"),
]
ITEMS.append(Q("ex1.2-q3", "exercise", 3, 14, "If $x = 3+\\sqrt{8}$ then find the value of: (i) $x+\\frac{1}{x}$ (ii) $x-\\frac{1}{x}$ (iii) $x^2+\\frac{1}{x^2}$ "
               "(iv) $x^2-\\frac{1}{x^2}$ (v) $x^4+\\frac{1}{x^4}$ (vi) $\\left(x-\\frac{1}{x}\\right)^2$", q3, exercise="1.2"))

# =========================================================================================
# Q4 and Q5
# =========================================================================================
ITEMS.append(Q("ex1.2-q4", "exercise", 4, 14, "Find the rational numbers $p$ and $q$ such that $\\frac{8-3\\sqrt{2}}{4+3\\sqrt{2}} = p+q\\sqrt{2}$.", [
    P("", [
        S(r"\frac{8-3\sqrt{2}}{4+3\sqrt{2}} \times \frac{4-3\sqrt{2}}{4-3\sqrt{2}} = \frac{(8-3\sqrt{2})(4-3\sqrt{2})}{4^2-(3\sqrt{2})^2}", *CONJ,
          "(8-3*sqrt(2))/(4+3*sqrt(2)) == (8-3*sqrt(2))*(4-3*sqrt(2))/(4**2 - (3*sqrt(2))**2)"),
        S(r"(8-3\sqrt{2})(4-3\sqrt{2}) = 32-24\sqrt{2}-12\sqrt{2}+18 = 50-36\sqrt{2}, \qquad 4^2-(3\sqrt{2})^2 = 16-18 = -2",
          "Multiply out the numerator and simplify the denominator.", "شمار کنندہ کو ضرب دیں اور نسب نما سادہ کریں۔",
          "(8-3*sqrt(2))*(4-3*sqrt(2)) == 50 - 36*sqrt(2)", "4**2 - (3*sqrt(2))**2 == -2"),
        S(r"= \frac{50-36\sqrt{2}}{-2} = -25+18\sqrt{2}", "Divide each term by $-2$.", "ہر رکن کو $-2$ سے تقسیم کریں۔", "(50-36*sqrt(2))/(-2) == -25 + 18*sqrt(2)"),
        S(r"-25+18\sqrt{2} = p+q\sqrt{2} \;\Rightarrow\; p = -25, \; q = 18", "Compare the rational parts and the coefficients of $\\sqrt{2}$.",
          "ناطق حصوں اور $\\sqrt{2}$ کے عددی سروں کا موازنہ کریں۔", "-25 + 18*sqrt(2) == (-25) + 18*sqrt(2)"),
    ], r"$p=-25,\ q=18$")], exercise="1.2"))

q5 = [
    P("i", [
        S(r"25^{\frac{3}{2}} = (5^2)^{\frac{3}{2}} = 5^3 = 125, \qquad 243^{\frac{3}{5}} = (3^5)^{\frac{3}{5}} = 3^3 = 27", *POW, "25**Rational(3,2) == 125", "243**Rational(3,5) == 27"),
        S(r"16^{\frac{5}{4}} = (2^4)^{\frac{5}{4}} = 2^5 = 32, \qquad 8^{\frac{4}{3}} = (2^3)^{\frac{4}{3}} = 2^4 = 16", *POW, "16**Rational(5,4) == 32", "8**Rational(4,3) == 16"),
        S(r"\frac{125 \times 27}{32 \times 16} = \frac{3375}{512}", "Multiply the numerator and the denominator.", "شمار کنندہ اور نسب نما کو ضرب دیں۔",
          "Rational(125*27, 32*16) == Rational(3375,512)"),
    ], r"$\frac{3375}{512}$", prompt=r"$\frac{(25)^{\frac{3}{2}} \times (243)^{\frac{3}{5}}}{(16)^{\frac{5}{4}} \times (8)^{\frac{4}{3}}}$"),
    P("ii", [
        S(r"\sqrt[3]{(27)^{2x}} = \left((3^3)^{2x}\right)^{\frac{1}{3}} = 3^{2x}", "Write 27 as $3^3$ and multiply the exponents: $3 \\cdot 2x \\cdot \\frac{1}{3} = 2x$.",
          "27 کو $3^3$ لکھیں اور قوتیں ضرب دیں: $3 \\cdot 2x \\cdot \\frac{1}{3} = 2x$۔", "cbrt(27**(2*x)) == 3**(2*x)"),
        S(r"9^{x+1} = 3^{2x+2} = 9 \cdot 3^{2x}, \qquad 216 \cdot 3^{2x-1} = 72 \cdot 3^{2x}", "Write the denominator in terms of $3^{2x}$: $\\frac{216}{3} = 72$.",
          "نسب نما کو $3^{2x}$ کی صورت میں لکھیں: $\\frac{216}{3} = 72$۔", "9**(x+1) == 9*3**(2*x)", "216*3**(2*x-1) == 72*3**(2*x)"),
        S(r"\frac{54 \cdot 3^{2x}}{9 \cdot 3^{2x} + 72 \cdot 3^{2x}} = \frac{54 \cdot 3^{2x}}{81 \cdot 3^{2x}} = \frac{54}{81} = \frac{2}{3}",
          "Take out the common factor $3^{2x}$, cancel it and reduce the fraction.", "مشترک جزو $3^{2x}$ نکال کر کاٹیں اور کسر کو مختصر کریں۔",
          "54*cbrt(27**(2*x))/(9**(x+1) + 216*3**(2*x-1)) == Rational(2,3)"),
    ], r"$\frac{2}{3}$", prompt=r"$\frac{54 \times \sqrt[3]{(27)^{2x}}}{9^{x+1} + 216(3^{2x-1})}$"),
    P("iii", [
        S(r"(216)^{\frac{2}{3}} = (6^3)^{\frac{2}{3}} = 6^2 = 36, \qquad (25)^{\frac{1}{2}} = 5", *POW, "216**Rational(2,3) == 36", "25**Rational(1,2) == 5"),
        S(r"(0.04)^{-\frac{3}{2}} = \left(\frac{4}{100}\right)^{-\frac{3}{2}} = \left(\frac{1}{5}\right)^{2 \times \left(-\frac{3}{2}\right)} = 5^3 = 125",
          "Write 0.04 as $\\left(\\frac{1}{5}\\right)^2$ and multiply the exponents.", "0.04 کو $\\left(\\frac{1}{5}\\right)^2$ لکھیں اور قوتیں ضرب دیں۔",
          "Rational('0.04') == Rational(1,5)**2", "Rational('0.04')**Rational(-3,2) == 125"),
        S(r"\sqrt{\frac{36 \times 5}{125}} = \sqrt{\frac{180}{125}} = \sqrt{\frac{36}{25}} = \frac{6}{5}", "Simplify the fraction under the root, then take the square root.",
          "جذر کے نیچے کسر سادہ کریں، پھر جذر لیں۔", "Rational(36*5,125) == Rational(36,25)", "sqrt(Rational(36,25)) == Rational(6,5)"),
    ], r"$\frac{6}{5}$", prompt=r"$\sqrt{\frac{(216)^{\frac{2}{3}} \times (25)^{\frac{1}{2}}}{(0.04)^{-\frac{3}{2}}}}$"),
    P("iv", [
        S(r"\text{Let } u = a^{\frac{1}{3}}, \; v = b^{\frac{2}{3}}", "Give the two terms short names so the pattern is visible.", "دونوں اجزا کو مختصر نام دیں تاکہ نمونہ نظر آئے۔"),
        S(r"a^{\frac{2}{3}} = u^2, \quad a^{\frac{1}{3}}b^{\frac{2}{3}} = uv, \quad b^{\frac{4}{3}} = v^2 \;\Rightarrow\; (u+v)(u^2-uv+v^2)",
          "The second bracket is $u^2-uv+v^2$.", "دوسرا قوسین $u^2-uv+v^2$ ہے۔",
          "a**Rational(2,3) == (a**Rational(1,3))**2", "b**Rational(4,3) == (b**Rational(2,3))**2"),
        S(r"(u+v)(u^2-uv+v^2) = u^3+v^3 = a + b^2", "Use $(u+v)(u^2-uv+v^2) = u^3+v^3$ with $u^3 = a$ and $v^3 = b^2$.",
          "$(u+v)(u^2-uv+v^2) = u^3+v^3$ استعمال کریں جہاں $u^3 = a$ اور $v^3 = b^2$ ہے۔",
          "(a**Rational(1,3)+b**Rational(2,3))*(a**Rational(2,3) - a**Rational(1,3)*b**Rational(2,3) + b**Rational(4,3)) == a + b**2"),
    ], "$a+b^2$", prompt=r"$\left(a^{\frac{1}{3}}+b^{\frac{2}{3}}\right) \times \left(a^{\frac{2}{3}} - a^{\frac{1}{3}}b^{\frac{2}{3}} + b^{\frac{4}{3}}\right)$"),
]
ITEMS.append(Q("ex1.2-q5", "exercise", 5, 14, "Simplify the following: (i) $\\frac{(25)^{\\frac{3}{2}} \\times (243)^{\\frac{3}{5}}}{(16)^{\\frac{5}{4}} \\times (8)^{\\frac{4}{3}}}$ "
               "(ii) $\\frac{54 \\times \\sqrt[3]{(27)^{2x}}}{9^{x+1} + 216(3^{2x-1})}$ (iii) $\\sqrt{\\frac{(216)^{\\frac{2}{3}} \\times (25)^{\\frac{1}{2}}}{(0.04)^{-\\frac{3}{2}}}}$ "
               "(iv) $\\left(a^{\\frac{1}{3}}+b^{\\frac{2}{3}}\\right) \\times \\left(a^{\\frac{2}{3}} - a^{\\frac{1}{3}}b^{\\frac{2}{3}} + b^{\\frac{4}{3}}\\right)$", q5, exercise="1.2"))
