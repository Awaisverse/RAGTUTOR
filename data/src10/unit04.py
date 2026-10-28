"""Class 10, Unit 4 - Functions and Graphs: Exercises 4.1-4.3 and Review Exercise 4.

Questions transcribed from the reference notes (data/class10/pages/u04_*.png); working checked with sympy; final answers checked
against data/answers10/unit04.json. Notes errors recorded with key_note: Ex 4.2 Q3(iv) and Review 4 Q2(iii).
"""
import sympy as sp

from _func import X, abs_equation, abs_graph, abs_inequality, combine, compose, fx, inverse, lt
from _gen import maker, mcq, ps
from _helpers import P, S, T

UNIT = {"unit": 4, "title": "Functions and Graphs", "title_ur": "تفاعل اور گراف", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational

# ------------------------------------------------------------------------------------------ Exercise 4.1

ex("ex4.1", 1, r"If $f(x)=2x+5$, $g(x)=3x-2$, then find (i) $f(x)+g(x)$ (ii) $f(x)-g(x)$", [
    combine("i", "f", "2*x+5", "g", "3*x-2", "+", "$f(x)+g(x)$"), combine("ii", "f", "2*x+5", "g", "3*x-2", "-", "$f(x)-g(x)$")], "4.1")
ex("ex4.1", 2, r"If $f(x)=x+2$, $g(x)=2x+4$, then find (i) $f(x)\cdot g(x)$ (ii) $g(x)\cdot f(x)$ (iii) $\frac{f(x)}{g(x)}$ (iv) $\frac{g(x)}{f(x)}$", [
    combine("i", "f", "x+2", "g", "2*x+4", "*", r"$f(x)\cdot g(x)$"), combine("ii", "g", "2*x+4", "f", "x+2", "*", r"$g(x)\cdot f(x)$"),
    combine("iii", "f", "x+2", "g", "2*x+4", "/", r"$\frac{f(x)}{g(x)}$"), combine("iv", "g", "2*x+4", "f", "x+2", "/", r"$\frac{g(x)}{f(x)}$")], "4.1")

FG = [("i", "2*x+3", "x**3", r"f(x)=2x+3;\ g(x)=x^3"), ("ii", "2/x", "2*x**2-1", r"f(x)=\frac{2}{x},\ x\ne 0;\ g(x)=2x^2-1"),
      ("iii", "2*x-1", "(x+1)/2", r"f(x)=2x-1;\ g(x)=\frac{x+1}{2}")]
q3 = []
for l, f, g, t in FG:
    for k, (on, o, inn, i_) in zip("abcd", [("f", f, "g", g), ("g", g, "f", f), ("f", f, "f", f), ("g", g, "g", g)]):
        p, _ = compose(f"{l}{k}", on, o, inn, i_, prompt=rf"${t}$: $({on}\circ {inn})(x)$")
        q3.append(p)
ex("ex4.1", 3, r"For the functions $f$ and $g$, find (a) $(f\circ g)(x)$ (b) $(g\circ f)(x)$ (c) $(f\circ f)(x)$ (d) $(g\circ g)(x)$ where, "
   r"(i) $f(x)=2x+3$; $g(x)=x^3$ (ii) $f(x)=\frac{2}{x},\ x\ne0$; $g(x)=2x^2-1$ (iii) $f(x)=2x-1$; $g(x)=\frac{x+1}{2}$", q3, "4.1")

ex("ex4.1", 4, r"Find the value of $k$, such that $(f\circ g)(x)=(g\circ f)(x)$, where $f(x)=3x+2$, $g(x)=6x-k$.", [P("", [
    S(r"(f\circ g)(x) = f(6x - k) = 3(6x - k) + 2 = 18x - 3k + 2", "Put $g(x)$ in $f$.", "$g(x)$ کو $f$ میں رکھیں۔", "3*(6*x - k) + 2 == 18*x - 3*k + 2"),
    S(r"(g\circ f)(x) = g(3x + 2) = 6(3x + 2) - k = 18x + 12 - k", "Put $f(x)$ in $g$.", "$f(x)$ کو $g$ میں رکھیں۔", "6*(3*x + 2) - k == 18*x + 12 - k"),
    S(r"18x - 3k + 2 = 18x + 12 - k \Rightarrow -2k = 10", "Equate the two and cancel $18x$.", "دونوں کو برابر کر کے $18x$ کاٹ دیں۔"),
    S(r"k = -5", "Divide by $-2$.", "$-2$ سے تقسیم کریں۔", "(3*(6*x - k) + 2 - (6*(3*x + 2) - k)).subs(k, -5) == 0")], "$k = -5$")], "4.1")


def value_of(label, chain_, prompt, ans):
    steps = [S(t, en, ur, *c) for t, en, ur, c in chain_]
    return P(label, steps, ans, prompt=prompt)


ex("ex4.1", 5, r"Given that $f(x)=3x+2$ and $g(x)=2x+3$. Find (i) $g(f(4))$ (ii) $f(f(3))$ (iii) $f(g(-2))$", [
    value_of("i", [(r"f(4) = 3(4) + 2 = 14", "Work out the inside function first.", "پہلے اندر والا تفاعل نکالیں۔", ["3*4 + 2 == 14"]),
                   (r"g(f(4)) = g(14) = 2(14) + 3 = 31", "Then put the result in $g$.", "پھر نتیجہ $g$ میں رکھیں۔", ["2*14 + 3 == 31"])], "$g(f(4))$", "$31$"),
    value_of("ii", [(r"f(3) = 3(3) + 2 = 11", "Inside first.", "پہلے اندر والا۔", ["3*3 + 2 == 11"]),
                    (r"f(f(3)) = f(11) = 3(11) + 2 = 35", "Then $f$ again.", "پھر دوبارہ $f$۔", ["3*11 + 2 == 35"])], "$f(f(3))$", "$35$"),
    value_of("iii", [(r"g(-2) = 2(-2) + 3 = -1", "Inside first.", "پہلے اندر والا۔", ["2*(-2) + 3 == -1"]),
                     (r"f(g(-2)) = f(-1) = 3(-1) + 2 = -1", "Then $f$.", "پھر $f$۔", ["3*(-1) + 2 == -1"])], "$f(g(-2))$", "$-1$")], "4.1")

ex("ex4.1", 6, r"Find $f^{-1}(x)$ in each of the following: (i) $f(x)=2x-3$ (ii) $f(x)=4x^3-1$ (iii) $f(x)=\sqrt{x-1},\ x\ge1$ (iv) $f(x)=\frac{x+1}{3x-2},\ x\ne\frac{2}{3}$", [
    inverse("i", "2*x-3", [r"2x = y + 3", r"x = \frac{y + 3}{2}"], "(x+3)/2", "$f(x)=2x-3$"),
    inverse("ii", "4*x**3-1", [r"4x^3 = y + 1", r"x^3 = \frac{y + 1}{4}", r"x = \sqrt[3]{\frac{y + 1}{4}}"], "((x+1)/4)**R(1,3)", "$f(x)=4x^3-1$"),
    inverse("iii", "sqrt(x-1)", [r"y^2 = x - 1", r"x = y^2 + 1"], "x**2+1", r"$f(x)=\sqrt{x-1},\ x\ge1$", r"x \ge 0"),
    inverse("iv", "(x+1)/(3*x-2)", [r"y(3x - 2) = x + 1", r"3xy - 2y = x + 1", r"3xy - x = 2y + 1", r"x(3y - 1) = 2y + 1", r"x = \frac{2y + 1}{3y - 1}"],
            "(2*x+1)/(3*x-1)", r"$f(x)=\frac{x+1}{3x-2},\ x\ne\frac{2}{3}$", r"x \ne \frac{1}{3}")], "4.1")

ex("ex4.1", 7, r"The functions $f$ and $g$ are defined such that $f(x)=4x+2$ and $g(x)=6x-18$. (i) Find $f^{-1}(x)$ and $g^{-1}(x)$. (ii) Find $x$ if $f^{-1}(x)=g^{-1}(x)$.", [
    P("i", inverse("", "4*x+2", [r"4x = y - 2", r"x = \frac{y - 2}{4}"], "(x-2)/4", "")["steps"] +
      [S(r"\text{and for } g:\ y = 6x - 18 \Rightarrow 6x = y + 18 \Rightarrow g^{-1}(x) = \frac{x + 18}{6}", "Do the same for $g$.", "$g$ کے لیے بھی یہی کریں۔",
         "simplify((6*x - 18).subs(x, (x + 18)/6)) == x")], r"$f^{-1}(x) = \frac{x - 2}{4},\ g^{-1}(x) = \frac{x + 18}{6}$",
      prompt=r"Find $f^{-1}(x)$ and $g^{-1}(x)$."),
    P("ii", [S(r"\frac{x - 2}{4} = \frac{x + 18}{6}", "Equate the two inverses.", "دونوں معکوس برابر کریں۔"),
             S(r"6(x - 2) = 4(x + 18) \Rightarrow 6x - 12 = 4x + 72", "Cross-multiply.", "کراس ضرب دیں۔", "6*(x - 2) - 4*(x + 18) == 2*x - 84"),
             S(r"2x = 84 \Rightarrow x = 42", "Solve.", "حل کریں۔", "(42 - 2)/4 == (42 + 18)/6")], "$x = 42$", prompt=r"Find $x$ if $f^{-1}(x)=g^{-1}(x)$.")], "4.1")


def verify_inverse(label, f, finv, prompt):
    F, Fi = fx(f), fx(finv)
    return P(label, [S(rf"f^{{-1}}(x) = {lt(Fi)}", "First find the inverse function.", "پہلے معکوس تفاعل معلوم کریں۔"),
                     S(rf"f(f^{{-1}}(x)) = f\left({lt(Fi)}\right) = {lt(F.subs(X, Fi))} = x", "Put $f^{-1}(x)$ in $f$ and simplify.", "$f^{-1}(x)$ کو $f$ میں رکھ کر سادہ کریں۔",
                       f"simplify(({sp.sstr(F)}).subs(x, {ps(Fi)})) == x"),
                     S(rf"f^{{-1}}(f(x)) = f^{{-1}}\left({lt(F)}\right) = {lt(Fi.subs(X, F))} = x", "Put $f(x)$ in $f^{-1}$ and simplify.", "$f(x)$ کو $f^{-1}$ میں رکھ کر سادہ کریں۔",
                       f"simplify(({sp.sstr(Fi)}).subs(x, {ps(F)})) == x")], "verified: $f(f^{-1}(x)) = f^{-1}(f(x)) = x$", prompt=prompt)


ex("ex4.1", 8, r"Verify that $f(f^{-1}(x))=f^{-1}(f(x))=x$: (i) $f(x)=x-6$ (ii) $f(x)=7x-4$ (iii) $f(x)=\frac{x-3}{4}$ (iv) $f(x)=\frac{x-4}{x+2},\ x\ne-2$", [
    verify_inverse("i", "x-6", "x+6", "$f(x)=x-6$"), verify_inverse("ii", "7*x-4", "(x+4)/7", "$f(x)=7x-4$"),
    verify_inverse("iii", "(x-3)/4", "4*x+3", r"$f(x)=\frac{x-3}{4}$"), verify_inverse("iv", "(x-4)/(x+2)", "(2*x+4)/(1-x)", r"$f(x)=\frac{x-4}{x+2},\ x\ne-2$")], "4.1")

DR = [("i", "12x-3", r"(-\infty, \infty)", r"(-\infty, \infty)", "a straight line takes every real value"),
      ("ii", r"\frac{1}{2}x+8", r"(-\infty, \infty)", r"(-\infty, \infty)", "a straight line takes every real value"),
      ("iii", r"\frac{x}{1+x},\ x\ne-1", r"(-\infty, 1) \cup (1, \infty)", r"(-\infty, -1) \cup (-1, \infty)", "$f$ never equals 1 and $x \\ne -1$"),
      ("iv", r"\sqrt{x-2},\ x\ge2", r"[0, \infty)", r"[2, \infty)", "a square root is never negative and $x \\ge 2$")]
DRC = {"i": [], "ii": [], "iii": ["x/(1 + x) - 1 == -1/(1 + x)"], "iv": ["sqrt(2 - 2) == 0"]}
ex("ex4.1", 9, r"Without finding $f^{-1}(x)$, find domain and range of $f^{-1}(x)$: (i) $f(x)=12x-3$ (ii) $f(x)=\frac{1}{2}x+8$ (iii) $f(x)=\frac{x}{1+x},\ x\ne-1$ "
   r"(iv) $f(x)=\sqrt{x-2},\ x\ge2$", [
       P(l, [S(r"\text{Domain of } f^{-1} = \text{Range of } f,\quad \text{Range of } f^{-1} = \text{Domain of } f",
               "The inverse swaps the roles of input and output.", "معکوس تفاعل ان پٹ اور آؤٹ پٹ کا کردار بدل دیتا ہے۔"),
             S(rf"\text{{Domain}} = {d},\quad \text{{Range}} = {r}", f"Here {why}.", "یہاں " + why + "۔", *DRC[l])],
         rf"Domain $= {d}$; Range $= {r}$", prompt=f"$f(x)={t}$") for l, t, d, r, why in DR], "4.1")

ex("ex4.1", 10, r"Given that $f(x)=x^2+9$ and $g(x)=x+21$. Find the values of $a$ such that: $f(a)=g(a)$", [P("", [
    S(r"a^2 + 9 = a + 21", "Put $a$ in both functions and equate.", "دونوں تفاعل میں $a$ رکھ کر برابر کریں۔"),
    S(r"a^2 - a - 12 = 0", "Move all terms to one side.", "تمام ارکان ایک طرف لے جائیں۔", "(a**2 + 9) - (a + 21) == a**2 - a - 12"),
    S(r"(a - 4)(a + 3) = 0", "Factorize.", "تجزی کریں۔", "expand((a - 4)*(a + 3)) == a**2 - a - 12"),
    S(r"a = 4 \quad\text{or}\quad a = -3", "Each factor equal to 0.", "ہر جزو صفر کے برابر۔", "4**2 + 9 == 4 + 21", "(-3)**2 + 9 == -3 + 21")], "$a = -3,\\ a = 4$")], "4.1")

# ------------------------------------------------------------------------------------------ Exercise 4.2

AG = [("i", "Abs(x-2)", "|x-2|"), ("ii", "3*Abs(x+3)-4", "3|x+3|-4"), ("iii", "5*Abs(x)", "5|x|"), ("iv", "Abs(x+2)+3", "|x+2|+3"),
      ("v", "2*Abs(x+4)-3", "2|x+4|-3"), ("vi", "2*Abs(x+1)-6", "2|x+1|-6")]
ex("ex4.2", 1, "Plot graph for the following absolute valued functions: " + " ".join(f"({l}) $f(x)={t}$" for l, _, t in AG),
   [abs_graph(l, f, f"$f(x)={t}$") for l, f, t in AG], "4.2", figure_h=70)

AE = [("i", "x-2", 6, "|x-2|=6"), ("ii", "2*x+1", 7, "|2x+1|=7"), ("iii", "4*x-9", 3, "|4x-9|=3"), ("iv", "7-2*x", 1, "|7-2x|=1")]
ex("ex4.2", 2, "Solve and express the solution on number line: " + " ".join(f"({l}) ${t}$" for l, _, _, t in AE),
   [abs_equation(l, e, r, f"${t}$") for l, e, r, t in AE], "4.2", figure_h=45)

E_ = ("Remove the absolute value: $|A| \\le k$ means $-k \\le A \\le k$.", "مطلق قیمت ہٹائیں: $|A| \\le k$ کا مطلب $-k \\le A \\le k$۔")
G_ = ("$|A| > k$ means $A < -k$ or $A > k$.", "$|A| > k$ کا مطلب $A < -k$ یا $A > k$۔")
SOLVE = ("Solve for $x$.", "$x$ معلوم کریں۔")
q3 = [abs_inequality("i", "Abs(5*x+8)", "<=", "3", [(r"-3 \le 5x + 8 \le 3", *E_), (r"-11 \le 5x \le -5", "Subtract 8.", "8 تفریق کریں۔"),
                                                   (r"-\frac{11}{5} \le x \le -1", "Divide by 5.", "5 سے تقسیم کریں۔")], r"$|5x+8|\le 3$")[0],
      abs_inequality("ii", "Abs(4*x-12)", "<=", "0", [(r"|4x - 12| \le 0 \Rightarrow 4x - 12 = 0", "An absolute value is never negative, so it can only be 0.",
                                                       "مطلق قیمت کبھی منفی نہیں ہوتی، اس لیے یہ صرف 0 ہو سکتی ہے۔"), (r"x = 3", *SOLVE)], r"$|4x-12|\le 0$")[0],
      abs_inequality("iii", "Abs(3-4*x)", ">", "0", [(r"|3 - 4x| > 0 \Rightarrow 3 - 4x \ne 0", "An absolute value is positive except where it is 0.",
                                                      "مطلق قیمت مثبت ہے سوائے جہاں یہ 0 ہو۔"), (r"x \ne \frac{3}{4}", *SOLVE)], r"$|3-4x|>0$")[0],
      abs_inequality("iv", "1-2*Abs(R(3,2)*x-5)", ">", "-3", [(r"-2\left|\frac{3}{2}x - 5\right| > -4", "Subtract 1 from both sides.", "دونوں اطراف سے 1 تفریق کریں۔"),
                                                              (r"\left|\frac{3}{2}x - 5\right| < 2", "Divide by $-2$: the sign turns round.", "$-2$ سے تقسیم کریں: علامت الٹ جاتی ہے۔"),
                                                              (r"-2 < \frac{3}{2}x - 5 < 2 \Rightarrow 3 < \frac{3}{2}x < 7", "Remove the absolute value and add 5.", "مطلق قیمت ہٹائیں اور 5 جمع کریں۔"),
                                                              (r"2 < x < \frac{14}{3}", "Multiply by $\\frac{2}{3}$.", "$\\frac{2}{3}$ سے ضرب دیں۔")],
                     r"$1-2\left|\frac{3}{2}x-5\right|>-3$")[0],
      abs_inequality("v", "Abs(3*x-2)", "<=", "12", [(r"-12 \le 3x - 2 \le 12", *E_), (r"-10 \le 3x \le 14", "Add 2.", "2 جمع کریں۔"),
                                                     (r"-\frac{10}{3} \le x \le \frac{14}{3}", "Divide by 3.", "3 سے تقسیم کریں۔")], r"$|3x-2|\le 12$")[0],
      abs_inequality("vi", "Abs(1-2*x)", ">", "5", [(r"1 - 2x < -5 \quad\text{or}\quad 1 - 2x > 5", *G_), (r"-2x < -6 \quad\text{or}\quad -2x > 4", "Subtract 1.", "1 تفریق کریں۔"),
                                                    (r"x > 3 \quad\text{or}\quad x < -2", "Divide by $-2$: the signs turn round.", "$-2$ سے تقسیم کریں: علامات الٹ جاتی ہیں۔")],
                     r"$|1-2x|>5$")[0]]
q3[3]["key_note"] = {"en": "The reference notes write $-2|3x-10| > -4$ (the factor $\\frac{1}{2}$ is lost) and get $\\frac{8}{3} < x < 4$; the correct solution is "
                           "$2 < x < \\frac{14}{3}$ (for example $x = 2.5$ gives $1 - 2(1.25) = -1.5 > -3$).",
                     "ur": "حوالہ نوٹس میں $\\frac{1}{2}$ کا جزو چھوٹ گیا ہے؛ درست حل $2 < x < \\frac{14}{3}$ ہے۔"}
ex("ex4.2", 3, r"Solve and express the solution on number line: (i) $|5x+8|\le3$ (ii) $|4x-12|\le0$ (iii) $|3-4x|>0$ (iv) $1-2\left|\frac{3}{2}x-5\right|>-3$ "
   r"(v) $|3x-2|\le12$ (vi) $|1-2x|>5$", q3, "4.2", figure_h=45)

# ------------------------------------------------------------------------------------------ Exercise 4.3


def evaluate(eid, n, question, fname, f, var, value, unit, ex_no="4.3"):
    v = sp.Symbol(var)
    F = sp.sympify(f, locals={var: v, "R": sp.Rational})
    val = F.subs(v, value)
    ex(eid, n, question, [P("", [S(rf"{fname}({var}) = {sp.latex(F)}", "Write the model.", "ماڈل لکھیں۔"),
                                 S(rf"{fname}({sp.latex(value)}) = {sp.latex(F).replace(var, '(' + sp.latex(value) + ')')} = {sp.latex(val)}",
                                   f"Put ${var} = {sp.latex(value)}$.", f"${var} = {sp.latex(value)}$ رکھیں۔", f"({f}).subs({var}, {ps(value)}) == {ps(val)}")],
                            f"{sp.latex(val) if not isinstance(val, sp.Float) else val} {unit}")], ex_no)


evaluate("ex4.3", 1, "A function $B(t)=5{,}000+200t$ represents the total balance (in rupees) after $t$ months. What will be the balance after 6 months?",
         "B", "5000 + 200*t", "t", 6, "rupees")
evaluate("ex4.3", 2, "A function $f(k)=150+20k$ represents the total fare (in rupees) for $k$ kilometres. How much will the fare be for a 12 kilometres ride?",
         "f", "150 + 20*k", "k", 12, "rupees")
evaluate("ex4.3", 3, "The cost of manufacturing fancy sofa set would be fixed charges Rs. 5500 which is modeled as $f(n)=5500n$, where $n$ is the number of sofa sets. "
         "Find the cost of 50 sofa sets.", "f", "5500*n", "n", 50, "rupees")
evaluate("ex4.3", 4, r"A function $T(d)=\frac{d}{60}$ represents the time $T$ in hours to travel a distance $d$ kilometres. How long will it take to travel 180 km?",
         "T", "d/60", "d", 180, "hours")
evaluate("ex4.3", 5, "A company charges Rs. 100 for an encoding work. In addition, the company charges Rs. 5 per page of printed output. The model of function "
         "$f(x)=100+5x$, where $x$ represents the number of pages printed out. How much will company charge for 55 page encoding and printing work?",
         "f", "100 + 5*x", "x", 55, "rupees")

ex("ex4.3", 6, r"A chemical reaction is stable at $37^\circ C$. The process must be stopped if the temperature deviates by more than $2.5^\circ C$. "
   r"The condition is modeled as: $|T-37^\circ|>2.5^\circ$, $T$ be the temperature. For what temperature values must the process be stopped?", [P("", [
       S(r"T - 37 < -2.5 \quad\text{or}\quad T - 37 > 2.5", *G_), S(r"T < 34.5 \quad\text{or}\quad T > 39.5", "Add 37.", "37 جمع کریں۔",
                                                                "Abs(34.4 - 37) > 2.5", "Abs(39.6 - 37) > 2.5", "Abs(37 - 37) <= 2.5")],
       r"$T < 34.5^\circ$ or $T > 39.5^\circ$")], "4.3")
ex("ex4.3", 7, r"A factory produces metal rods that must be 2.5 metres long, with a tolerance of $\pm0.04$ metres. An absolute value inequality models this: "
   r"$|x-2.5|\le0.04$. What is the range of acceptable lengths?", [P("", [
       S(r"-0.04 \le x - 2.5 \le 0.04", *E_), S(r"2.46 \le x \le 2.54", "Add 2.5.", "2.5 جمع کریں۔", "Abs(R(246,100) - R(5,2)) <= R(4,100)", "Abs(R(254,100) - R(5,2)) <= R(4,100)")],
       r"$2.46 \le x \le 2.54$")], "4.3")
ex("ex4.3", 8, r"A machine part must be aligned so that its centre is exactly at 0. If it shifts more than 0.1 mm, the part is rejected. The model is given by "
   r"$|x|>0.1$. What positions of the centre cause rejection?", [P("", [
       S(r"|x| > 0.1 \Rightarrow x < -0.1 \quad\text{or}\quad x > 0.1", *G_, "Abs(-0.2) > 0.1", "Abs(0.05) <= 0.1")],
       r"$x < -0.1$ or $x > 0.1$")], "4.3")

# ------------------------------------------------------------------------------------------ Review Exercise 4

q1 = [mcq("i", r"If $f(x)=\frac{5x-6}{3}$, then what is the value of $f(3)$?", ["-1", "3", "9", "15"], 1,
          [S(r"f(3) = \frac{5(3) - 6}{3} = \frac{9}{3} = 3", "Put $x = 3$.", "$x = 3$ رکھیں۔", "(5*3 - 6)/3 == 3")]),
      mcq("ii", r"A function $f$ from $X$ to $Y$ is represented by:", ["f: XY", r"f: Y\to X", r"f: X\to Y", r"f: \frac{X}{Y}"], 2,
          [T("A function from $X$ to $Y$ is written $f: X \\to Y$.", "$X$ سے $Y$ کا تفاعل $f: X \\to Y$ لکھا جاتا ہے۔")]),
      mcq("iii", r"$(f\circ g)(x)=$", ["(f+g)(x)", "(f-g)(x)", "f(g(x))", r"f(x)\div g(x)"], 2, [T("Composition: $g$ first, then $f$.", "ترکیب: پہلے $g$ پھر $f$۔")]),
      mcq("iv", r"If $f(x)=2x+3$, $g(x)=x+1$, then $f(x)+g(x)=$", ["3x", "3x+4", "4", "2x^2+3"], 1,
          [S(r"(2x + 3) + (x + 1) = 3x + 4", "Add like terms.", "متشابہ ارکان جمع کریں۔", "(2*x + 3) + (x + 1) == 3*x + 4")]),
      mcq("v", r"If $f(x)=5x+2$, $h(x)=2x-2$, then $f(x)-h(x)=$", ["3x", "5x^2-4", "3x+4", "-3x-4"], 2,
          [S(r"(5x + 2) - (2x - 2) = 3x + 4", "Subtract.", "تفریق کریں۔", "(5*x + 2) - (2*x - 2) == 3*x + 4")]),
      mcq("vi", r"If $f(x)=3x+1$, $g(x)=2x$, then $g(x)\times f(x)=$", ["6x+2x", "5x^2+1", "x+1", "6x^2+2x"], 3,
          [S(r"2x(3x + 1) = 6x^2 + 2x", "Multiply.", "ضرب دیں۔", "2*x*(3*x + 1) == 6*x**2 + 2*x")]),
      mcq("vii", r"If $f(x)=x^2-4$, $g(x)=x+2,\ x\ne-2$, then $\frac{f(x)}{g(x)}=$", [r"\frac{1}{x-2}", r"\frac{1}{x+2}", "x+2", "x-2"], 3,
          [S(r"\frac{(x - 2)(x + 2)}{x + 2} = x - 2", "Factorize and cancel.", "تجزی کر کے کاٹ دیں۔", "(x**2 - 4)/(x + 2) == x - 2")]),
      mcq("viii", "What is the shape of the graph of an absolute value function?", [r"\text{U-shaped}", r"\text{V-shaped}", r"\text{L-shaped}", r"\text{M-shaped}"], 1,
          [T("Two straight lines meeting at a corner make a V.", "دو خطوط مستقیم ایک کونے پر مل کر V بناتے ہیں۔")]),
      mcq("ix", "If a graph represents a function, then every vertical line must intersect it at:", [r"\text{4 points}", r"\text{3 points}", r"\text{2 points}", r"\text{1 point}"], 3,
          [T("Vertical line test: each $x$ has exactly one $y$.", "عمودی خط کی جانچ: ہر $x$ کا صرف ایک $y$ ہوتا ہے۔")]),
      mcq("x", r"If $f(x)=x^3$, then $f(-2)=$", ["-8", "8", "4", "-6"], 0, [S(r"(-2)^3 = -8", "Cube $-2$.", "$-2$ کا مکعب۔", "(-2)**3 == -8")])]
ex("rev4", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 4")

q2 = [combine("i", "f", "25-x**2", "g", "5+x", "+", "$f(x)+g(x)$"), combine("ii", "f", "25-x**2", "g", "5+x", "-", "$f(x)-g(x)$"),
      combine("iii", "f", "25-x**2", "g", "5+x", "*", r"$f(x)\cdot g(x)$"), combine("iv", "f", "25-x**2", "g", "5+x", "/", r"$\frac{f(x)}{g(x)}$"),
      value_of("v", [(r"f(7) = 25 - 7^2 = 25 - 49 = -24", "Put $x = 7$.", "$x = 7$ رکھیں۔", ["25 - 7**2 == -24"])], "$f(7)$", "$-24$"),
      value_of("vi", [(r"g(-8) = 5 + (-8) = -3", "Put $x = -8$.", "$x = -8$ رکھیں۔", ["5 + (-8) == -3"])], "$g(-8)$", "$-3$")]
q2[2]["key_note"] = {"en": "The reference notes drop the $-x^3$ term: $(25 - x^2)(5 + x) = 125 + 25x - 5x^2 - x^3$.",
                     "ur": "حوالہ نوٹس میں $-x^3$ کا رکن چھوٹ گیا ہے۔"}
ex("rev4", 2, r"If $f(x)=25-x^2$ and $g(x)=5+x$, then find (i) $f(x)+g(x)$ (ii) $f(x)-g(x)$ (iii) $f(x)\cdot g(x)$ (iv) $\frac{f(x)}{g(x)}$ (v) $f(7)$ (vi) $g(-8)$",
   q2, "Review 4")
ex("rev4", 3, r"If $f(x)=x^3$ and $g(x)=14+2x$, then find (i) $(f\circ g)(x)$ (ii) $(g\circ f)(x)$ (iii) $(f\circ f)(x)$ (iv) $(g\circ g)(x)$", [
    compose(l, o, of, i_, if_, rf"$({o}\circ {i_})(x)$")[0] if l != "i" else
    P("i", [S(r"(f\circ g)(x) = f(14 + 2x) = (14 + 2x)^3", "Put $g(x)$ in place of $x$ in $f$.", "$f$ میں $x$ کی جگہ $g(x)$ رکھیں۔",
              "(x**3).subs(x, 14 + 2*x) == (14 + 2*x)**3")], "$(14 + 2x)^3$", prompt=r"$(f\circ g)(x)$")
    for l, o, of, i_, if_ in [("i", "f", "x**3", "g", "14+2*x"), ("ii", "g", "14+2*x", "f", "x**3"), ("iii", "f", "x**3", "f", "x**3"), ("iv", "g", "14+2*x", "g", "14+2*x")]],
   "Review 4")
ex("rev4", 4, r"Find $f^{-1}(x)$, if (i) $f(x)=9x-1$ (ii) $f(x)=\frac{5}{x-1},\ x\ne1$ (iii) $f(x)=\sqrt{x-5},\ x\ge5$ (iv) $f(x)=\frac{3-x}{2}$", [
    inverse("i", "9*x-1", [r"9x = y + 1", r"x = \frac{y + 1}{9}"], "(x+1)/9", "$f(x)=9x-1$"),
    inverse("ii", "5/(x-1)", [r"y(x - 1) = 5 \Rightarrow yx - y = 5", r"yx = 5 + y", r"x = \frac{5 + y}{y}"], "(5+x)/x", r"$f(x)=\frac{5}{x-1},\ x\ne1$"),
    inverse("iii", "sqrt(x-5)", [r"y^2 = x - 5", r"x = y^2 + 5"], "x**2+5", r"$f(x)=\sqrt{x-5},\ x\ge5$", r"x \ge 0"),
    inverse("iv", "(3-x)/2", [r"2y = 3 - x", r"x = 3 - 2y"], "3-2*x", r"$f(x)=\frac{3-x}{2}$")], "Review 4")
ex("rev4", 5, r"Plot graph for the following absolute valued functions: (i) $f(x)=7|x|$ (ii) $f(x)=|x+6|-2$", [
    abs_graph("i", "7*Abs(x)", "$f(x)=7|x|$"), abs_graph("ii", "Abs(x+6)-2", "$f(x)=|x+6|-2$")], "Review 4", figure_h=70)
ex("rev4", 6, r"Solve and express the solution on number line: (i) $|3x-2|=1$ (ii) $|6x+1|=9$", [
    abs_equation("i", "3*x-2", 1, "$|3x-2|=1$"), abs_equation("ii", "6*x+1", 9, "$|6x+1|=9$")], "Review 4", figure_h=45)
ex("rev4", 7, r"Solve and express the solution on number line: (i) $|7-2x|\le1$ (ii) $|6x+18|\le24$", [
    abs_inequality("i", "Abs(7-2*x)", "<=", "1", [(r"-1 \le 7 - 2x \le 1", *E_), (r"-8 \le -2x \le -6", "Subtract 7.", "7 تفریق کریں۔"),
                                                 (r"3 \le x \le 4", "Divide by $-2$ (the signs turn round).", "$-2$ سے تقسیم کریں (علامات الٹ جاتی ہیں)۔")], r"$|7-2x|\le 1$")[0],
    abs_inequality("ii", "Abs(6*x+18)", "<=", "24", [(r"-24 \le 6x + 18 \le 24", *E_), (r"-42 \le 6x \le 6", "Subtract 18.", "18 تفریق کریں۔"),
                                                    (r"-7 \le x \le 1", "Divide by 6.", "6 سے تقسیم کریں۔")], r"$|6x+18|\le 24$")[0]], "Review 4", figure_h=45)
ex("rev4", 8, r"Given that $f(x)=3x+7$, find (i) $f^{-1}(x)$ (ii) the value of $x$ for which $f(x)=f^{-1}(x)$", [
    inverse("i", "3*x+7", [r"3x = y - 7", r"x = \frac{y - 7}{3}"], "(x-7)/3", "$f^{-1}(x)$"),
    P("ii", [S(r"3x + 7 = \frac{x - 7}{3}", "Equate $f(x)$ and $f^{-1}(x)$.", "$f(x)$ اور $f^{-1}(x)$ برابر کریں۔"),
             S(r"9x + 21 = x - 7 \Rightarrow 8x = -28", "Multiply by 3 and collect terms.", "3 سے ضرب دے کر ارکان اکٹھے کریں۔", "3*(3*x + 7) - (x - 7) == 8*x + 28"),
             S(r"x = -\frac{7}{2}", "Divide by 8.", "8 سے تقسیم کریں۔", "3*R(-7,2) + 7 == (R(-7,2) - 7)/3")], r"$x = -\frac{7}{2}$",
      prompt=r"the value of $x$ for which $f(x)=f^{-1}(x)$")], "Review 4")
ex("rev4", 9, r"A company earns a profit of Rs. 100 for each item sold after a fixed monthly expense of Rs. 10,000. A function $P(x)=100x-10{,}000$ represents the "
   r"profit after selling $x$ items. How many items must be sold to break even (profit = 0)?", [P("", [
       S(r"100x - 10000 = 0", "Break even: profit is 0.", "نہ نفع نہ نقصان: منافع 0 ہے۔"),
       S(r"x = \frac{10000}{100} = 100", "Solve for $x$.", "$x$ معلوم کریں۔", "100*100 - 10000 == 0")], "100 items")], "Review 4")
evaluate("rev4", 10, r"A store offers a 15% discount on a product. A function $D(p)=0.85p$ gives the selling price after the discount on an original price $p$. "
         r"What is the selling price of an item that originally costs Rs. 2,000?", "D", "R(85,100)*p", "p", 2000, "rupees", "Review 4")
ex("rev4", 11, r"A GPS system is considered accurate if the actual position differs from the reported position by no more than 6 metres. If the actual location is "
   r"at point $x=100$, the allowed range is defined as: $|x-r|\le6$, where $r$ is the reported location. What is the range of acceptable reported locations?", [P("", [
       S(r"|r - 100| \le 6 \Rightarrow -6 \le r - 100 \le 6", *E_), S(r"94 \le r \le 106", "Add 100.", "100 جمع کریں۔", "Abs(94 - 100) <= 6", "Abs(106 - 100) <= 6", "Abs(107 - 100) > 6")],
       "$94 \\le r \\le 106$")], "Review 4")
