"""Unit 1 - Real Numbers (Mathematics 9, Punjab textbook 2026). Worked examples 1-14."""
from _helpers import S, T, P, Q, one

UNIT = {
    "unit": 1,
    "title": "Real Numbers",
    "title_ur": "حقیقی اعداد",
    "items": [
        Q("u1-example1", "example", 1, 4,
          "Identify the following decimal numbers as rational or irrational: (i) 0.35 (ii) 0.444... (iii) 3.$\\bar{5}$ (iv) 3.36788542... (v) 1.709975947...",
          [
              P("i", [T("0.35 is a terminating decimal, so it is rational.",
                        "0.35 ایک محدود اعشاری عدد ہے، اس لیے یہ ناطق (rational) ہے۔")],
                "Rational"),
              P("ii", [T("0.444... repeats the digit 4 forever, so it is non-terminating recurring, hence rational.",
                         "0.444... میں ہندسہ 4 بار بار آتا ہے، یعنی غیر محدود دوری اعشاری، اس لیے ناطق ہے۔")],
                "Rational"),
              P("iii", [S("3.\\bar{5} = 3.5555\\ldots", "3.$\\bar{5}$ کا مطلب ہے 3.5555... (5 بار بار آتا ہے)۔", "5 بار بار آتا ہے، اس لیے یہ ناطق ہے۔")],
                "Rational"),
              P("iv", [T("3.36788542... does not repeat and does not end, so it is irrational.",
                         "یہ نہ ختم ہوتا ہے نہ دہرایا جاتا ہے، اس لیے غیر ناطق (irrational) ہے۔")],
                "Irrational"),
              P("v", [T("1.709975947... does not repeat and does not end, so it is irrational.",
                        "یہ بھی نہ ختم ہوتا ہے نہ دہرایا جاتا ہے، اس لیے غیر ناطق ہے۔")],
                "Irrational"),
          ]),

        Q("u1-example2", "example", 2, 5,
          "Represent $\\sqrt{5}$ on a number line.",
          one([
              S("\\sqrt{5} = \\sqrt{2^2+1^2}", "Build a right triangle with legs 2 and 1. Its hypotenuse is $\\sqrt{5}$.",
                "قائمۃ الزاویہ مثلث بنائیں جس کے دو ضلع 2 اور 1 ہوں۔ وتر $\\sqrt{5}$ ہوگا۔",
                "sqrt(5) == sqrt(2**2 + 1**2)",
                draw=[{"t": "numberline", "from": -4, "to": 4, "y": 40}]),
              S("(OB)^2 = (OA)^2 + (AB)^2 = 2^2 + 1^2 = 5", "By Pythagoras, OB = $\\sqrt{5}$.",
                "فیثاغورث کے قضیے سے OB = $\\sqrt{5}$ ہے۔",
                "2**2 + 1**2 == 5",
                draw=[{"t": "poly", "p": [20, 40, 40, 40, 40, 30], "close": True}]),
              S("\\text{Draw arc of radius } OB \\text{ centred at } O", "With O as centre and radius OB, draw an arc. It cuts the number line at P.",
                "O کو مرکز اور OB کو رداس لے کر قوس کھینچیں۔ یہ نمبر لائن کو نقطہ P پر کاٹے گی۔",
                draw=[{"t": "arc", "c": [20, 40], "r": 22, "a": [-10, 10]}]),
          ], "P represents $\\sqrt{5}$ on the number line, since OP = $\\sqrt{5}$.")),

        Q("u1-example3", "example", 3, 5,
          "Express the recurring decimals as $\\frac{p}{q}$: (i) $0.\\bar{5}$  (ii) $0.\\overline{93}$",
          [
              P("i", [
                  S("x = 0.555\\ldots", "Let x be the number.", "فرض کریں x وہ عدد ہے۔"),
                  S("10x = 5.555\\ldots", "Multiply by 10, because one digit repeats.", "ایک ہندسہ دہرانے کی وجہ سے 10 سے ضرب دیں۔", "10*Rational(5,9) == Rational(50,9)"),
                  S("9x = 5", "Subtract (i) from (ii).", "(ii) میں سے (i) منہا کریں۔", "10*Rational(5,9) - Rational(5,9) == 5"),
                  S("x = \\frac{5}{9}", "Divide by 9.", "9 سے تقسیم کریں۔", "Rational(5,9)*9 == 5"),
              ], "$\\frac{5}{9}$"),
              P("ii", [
                  S("x = 0.939393\\ldots", "Let x = 0.$\\overline{93}$.", "فرض کریں x = 0.$\\overline{93}$۔"),
                  S("100x = 93.939393\\ldots", "Two digits repeat, so multiply by 100.", "دو ہندسے دہرتے ہیں، اس لیے 100 سے ضرب دیں۔", "100*Rational(93,99) == Rational(9300,99)"),
                  S("99x = 93", "Subtract (i) from (ii).", "(ii) میں سے (i) منہا کریں۔", "100*Rational(93,99) - Rational(93,99) == 93"),
                  S("x = \\frac{93}{99} = \\frac{31}{33}", "Divide by 99 and cancel the common factor 3.", "99 سے تقسیم کریں اور 3 سے کم کریں۔", "Rational(93,99) == Rational(31,33)"),
              ], "$\\frac{93}{99} = \\frac{31}{33}$"),
          ]),

        Q("u1-example4", "example", 4, 6,
          "Find two rational numbers between 2 and 3.",
          one([
              S("\\frac{2+3}{2} = \\frac{5}{2}", "Average of 2 and 3 is a rational number between them.",
                "2 اور 3 کا اوسط ان کے درمیان ایک ناطق عدد ہے۔", "(2+3)/2 == Rational(5,2)"),
              S("\\frac{\\frac{5}{2}+3}{2} = \\frac{11}{4}", "Average of $\\frac{5}{2}$ and 3 is another one.",
                "$\\frac{5}{2}$ اور 3 کا اوسط ایک اور عدد ہے۔", "(Rational(5,2)+3)/2 == Rational(11,4)"),
          ], "$\\frac{5}{2}$ and $\\frac{11}{4}$")),

        Q("u1-example5", "example", 5, 9,
          "If $a=\\frac{2}{3}$, $b=\\frac{3}{2}$, $c=\\frac{5}{3}$, verify the distributive property over addition.",
          [
              P("i", [
                  S("LHS = a(b+c) = \\frac{2}{3}\\left(\\frac{3}{2}+\\frac{5}{3}\\right) = \\frac{2}{3}\\cdot\\frac{19}{6} = \\frac{19}{9}",
                    "Compute the left side first.", "پہلے بائیں طرف کی قیمت نکالیں۔",
                    "Rational(2,3)*(Rational(3,2)+Rational(5,3)) == Rational(19,9)"),
                  S("RHS = ab+ac = 1 + \\frac{10}{9} = \\frac{19}{9}", "Now compute ab + ac.", "اب ab + ac نکالیں۔",
                    "Rational(2,3)*Rational(3,2) + Rational(2,3)*Rational(5,3) == Rational(19,9)"),
                  T("LHS = RHS, so a(b+c) = ab+ac is verified.", "LHS = RHS ہے، لہذا a(b+c) = ab+ac کی تصدیق ہوگئی۔"),
              ], "Verified: $\\frac{19}{9} = \\frac{19}{9}$"),
              P("ii", [
                  S("LHS = (a+b)c = \\left(\\frac{4+9}{6}\\right)\\frac{5}{3} = \\frac{65}{18}", "Compute the left side.", "بائیں طرف کی قیمت نکالیں۔",
                    "(Rational(2,3)+Rational(3,2))*Rational(5,3) == Rational(65,18)"),
                  S("RHS = ac+bc = \\frac{10}{9}+\\frac{15}{6} = \\frac{65}{18}", "Compute the right side.", "دائیں طرف کی قیمت نکالیں۔",
                    "Rational(2,3)*Rational(5,3) + Rational(3,2)*Rational(5,3) == Rational(65,18)"),
              ], "Verified: $\\frac{65}{18} = \\frac{65}{18}$"),
          ]),

        Q("u1-example6", "example", 6, 9,
          "Identify the property that justifies each statement: (i) a > 13 then a+2 > 15  (ii) 3<9 and 6<12 then 9<21  (iii) 7>4 and 5>3 then 35>12  (iv) -5 < -4 then 20 > 16",
          [
              P("i", [S("a > 13 \\Rightarrow a+2 > 13+2 = 15", "Add 2 to both sides. This is the order property with respect to addition.",
                        "دونوں طرف 2 جمع کریں۔ یہ ترتیب کی خاصیت (جمع کے لحاظ سے) ہے۔", "13+2 == 15")], "Order property w.r.t. addition"),
              P("ii", [S("3+6 < 9+12 \\Rightarrow 9 < 21", "Add the two inequalities. Order property w.r.t. addition.",
                         "دونوں عدم مساوات کو جمع کریں۔ جمع کے لحاظ سے ترتیب کی خاصیت۔", "3+6 == 9", "9+12 == 21")], "Order property w.r.t. addition"),
              P("iii", [S("7\\times 5 > 4\\times 3 \\Rightarrow 35 > 12", "Multiply the two inequalities. Order property w.r.t. multiplication.",
                          "دونوں عدم مساوات کو ضرب دیں۔ ضرب کے لحاظ سے ترتیب کی خاصیت۔", "7*5 == 35", "4*3 == 12")], "Order property w.r.t. multiplication"),
              P("iv", [S("(-5)(-4) > (-4)(-4) \\Rightarrow 20 > 16", "Multiply both sides by -4. Multiplying by a negative number reverses the inequality sign, so -5 < -4 becomes 20 > 16.",
                         "دونوں طرف -4 سے ضرب دیں۔ منفی عدد سے ضرب کرنے پر عدم مساوات کی علامت الٹ جاتی ہے، یعنی 20 > 16۔", "(-5)*(-4) == 20", "(-4)*(-4) == 16")], "Order property w.r.t. multiplication"),
          ]),

        Q("u1-example7", "example", 7, 11,
          "Simplify: (i) $\\sqrt[4]{16x^4y^8}$  (ii) $\\sqrt[3]{27x^6y^9z^3}$  (iii) $(64)^{-4/3}$",
          [
              P("i", [
                  S("\\sqrt[4]{16x^4y^8} = (16)^{1/4}(x^4)^{1/4}(y^8)^{1/4}", "Write the radical as a power 1/4 and use $(ab)^m = a^m b^m$.",
                    "جذر کو 1/4 کی طاقت میں لکھیں اور $(ab)^m = a^m b^m$ استعمال کریں۔", "(16)**Rational(1,4) == 2"),
                  S("= 2\\cdot x \\cdot y^2", "Use $(a^m)^n = a^{mn}$: $4\\cdot\\frac14 = 1$, $8\\cdot\\frac14 = 2$.",
                    "$(a^m)^n = a^{mn}$ استعمال کریں: $4\\cdot\\frac14 = 1$ اور $8\\cdot\\frac14 = 2$۔", "Rational(4,4)==1", "Rational(8,4)==2"),
              ], "$2xy^2$"),
              P("ii", [
                  S("\\sqrt[3]{27x^6y^9z^3} = 3\\,x^{6/3}\\,y^{9/3}\\,z^{3/3}", "27 = 3^3, so its cube root is 3. Divide each exponent by 3.",
                    "27 = 3^3 ہے، اس کا مکعب جذر 3 ہے۔ ہر قوت کو 3 سے تقسیم کریں۔", "3**3 == 27"),
                  S("= 3x^2y^3z", "Simplify the exponents.", "قوتیں سادہ کریں۔", "Rational(6,3)==2", "Rational(9,3)==3"),
              ], "$3x^2y^3z$"),
              P("iii", [
                  S("(64)^{-4/3} = \\frac{1}{(64)^{4/3}}", "A negative exponent gives the reciprocal.", "منفی قوت کا مطلب معکوس ہے۔", "64**Rational(-4,3) == 1/64**Rational(4,3)"),
                  S("64 = 4^3 \\Rightarrow (64)^{4/3} = 4^4 = 256", "Write 64 = 4^3, then (4^3)^{4/3} = 4^4.", "64 = 4^3 لکھیں، پھر $(4^3)^{4/3} = 4^4$۔", "4**4 == 256", "64**Rational(4,3) == 256"),
              ], "$\\frac{1}{256}$"),
          ]),

        Q("u1-example8", "example", 8, 13,
          "Rationalize the denominator: (i) $\\frac{3}{\\sqrt5+\\sqrt2}$  (ii) $\\frac{3}{\\sqrt5-\\sqrt3}$",
          [
              P("i", [
                  S("\\frac{3}{\\sqrt5+\\sqrt2}\\times\\frac{\\sqrt5-\\sqrt2}{\\sqrt5-\\sqrt2}", "Multiply by the conjugate $\\sqrt5-\\sqrt2$.",
                    "مزدوج $\\sqrt5-\\sqrt2$ سے ضرب دیں۔", "3/(sqrt(5)+sqrt(2)) == sqrt(5)-sqrt(2)"),
                  S("= \\frac{3(\\sqrt5-\\sqrt2)}{5-2} = \\sqrt5-\\sqrt2", "Denominator is $(\\sqrt5)^2-(\\sqrt2)^2 = 3$.",
                    "مخرج $(\\sqrt5)^2-(\\sqrt2)^2 = 3$ ہے۔", "(sqrt(5))**2 - (sqrt(2))**2 == 3"),
              ], "$\\sqrt5-\\sqrt2$"),
              P("ii", [
                  S("\\frac{3}{\\sqrt5-\\sqrt3}\\times\\frac{\\sqrt5+\\sqrt3}{\\sqrt5+\\sqrt3}", "Multiply by the conjugate $\\sqrt5+\\sqrt3$.",
                    "مزدوج $\\sqrt5+\\sqrt3$ سے ضرب دیں۔", "3/(sqrt(5)-sqrt(3)) == 3*(sqrt(5)+sqrt(3))/2"),
                  S("= \\frac{3(\\sqrt5+\\sqrt3)}{5-3} = \\frac{3(\\sqrt5+\\sqrt3)}{2}", "Denominator is $5-3 = 2$.", "مخرج $5-3 = 2$ ہے۔", "(sqrt(5))**2 - (sqrt(3))**2 == 2"),
              ], "$\\frac{3(\\sqrt5+\\sqrt3)}{2}$"),
          ]),

        Q("u1-example9", "example", 9, 14,
          "The sum of two real numbers is 8 and their difference is 2. Find the numbers.",
          one([
              S("a+b = 8 \\quad (i),\\qquad a-b = 2 \\quad (ii)", "Write both equations.", "دونوں مساواتیں لکھیں۔"),
              S("2a = 10 \\Rightarrow a = 5", "Add (i) and (ii).", "(i) اور (ii) کو جمع کریں۔", "Rational(8+2,2)==5"),
              S("5 + b = 8 \\Rightarrow b = 3", "Put a = 5 in (i).", "a = 5 کو (i) میں رکھیں۔", "8-5 == 3"),
          ], "5 and 3")),

        Q("u1-example10", "example", 10, 16,
          "Normal human body temperature is 98.6 °F. Convert it to Celsius and Kelvin.",
          one([
              S("^\\circ C = \\frac{5}{9}(F-32)", "Use the Fahrenheit-to-Celsius formula.", "فارن ہائیٹ سے سیلسیس کا فارمولا استعمال کریں۔",
                "Rational(5,9)*(Rational(986,10)-32) == 37"),
              S("K = C + 273 = 37 + 273 = 310", "Convert Celsius to Kelvin.", "سیلسیس کو کیلون میں بدلیں۔", "37+273 == 310"),
          ], "37 °C and 310 K")),

        Q("u1-example11", "example", 11, 16,
          "Hamail bought a bicycle for Rs. 6590 and sold it for Rs. 6850. Find the profit percentage.",
          one([
              S("P = SP - CP = 6850 - 6590 = 260", "Profit is selling price minus cost price.", "منافع = فروخت قیمت − خرید قیمت۔", "6850-6590 == 260"),
              S("\\text{Profit\\%} = \\frac{260}{6590}\\times 100 \\approx 3.94\\%", "Profit % = profit / CP x 100.",
                "منافع فیصد = منافع / خرید قیمت × 100۔", "abs(260*100/6590 - 3.94) < 0.01"),
          ], "About 3.94% (≈ 4%)")),

        Q("u1-example12", "example", 12, 17,
          "Umair bought a book for Rs. 850 and sold it for Rs. 720. What was his loss percentage?",
          one([
              S("\\text{Loss} = CP - SP = 850 - 720 = 130", "Loss is cost price minus selling price.", "نقصان = خرید قیمت − فروخت قیمت۔", "850-720 == 130"),
              S("\\text{Loss\\%} = \\frac{130}{850}\\times 100 = 15.29\\%", "Loss % = loss / CP x 100.", "نقصان فیصد = نقصان / خرید قیمت × 100۔", "abs(130*100/850 - 15.29) < 0.01"),
          ], "15.29%")),

        Q("u1-example13", "example", 13, 17,
          "Saleem, Nadeem and Tanveer earned a profit of Rs. 4,50,000. Their investments are in the ratio 4 : 7 : 14. Find each person's profit.",
          one([
              S("\\text{Sum of ratios} = 4+7+14 = 25", "Add the parts of the ratio.", "تناسب کے حصے جمع کریں۔", "4+7+14 == 25"),
              S("\\text{Saleem} = \\frac{4}{25}\\times 450000 = 72000", "Each person gets (own ratio / 25) of the profit.",
                "ہر شخص کو اپنے حصے / 25 کا منافع ملے گا۔", "Rational(4,25)*450000 == 72000"),
              S("\\text{Nadeem} = \\frac{7}{25}\\times 450000 = 126000", "Same method for Nadeem.", "ندیم کے لیے بھی یہی طریقہ۔", "Rational(7,25)*450000 == 126000"),
              S("\\text{Tanveer} = \\frac{14}{25}\\times 450000 = 252000", "Same method for Tanveer.", "تنویر کے لیے بھی یہی طریقہ۔", "Rational(14,25)*450000 == 252000"),
          ], "Saleem Rs. 72,000; Nadeem Rs. 1,26,000; Tanveer Rs. 2,52,000")),

        Q("u1-example14", "example", 14, 18,
          "If the simple profit on Rs. 6400 for 12 years is Rs. 3840, find the rate of profit.",
          one([
              S("\\text{Rate} = \\frac{\\text{profit}\\times 100}{\\text{time}\\times\\text{principal}}", "Use the simple-profit rate formula.", "سادہ منافع کی شرح کا فارمولا۔"),
              S("= \\frac{3840\\times 100}{12\\times 6400} = 5\\%", "Substitute the values.", "قیمتیں رکھیں۔", "Rational(3840*100, 12*6400) == 5"),
          ], "5%")),
    ],
}
