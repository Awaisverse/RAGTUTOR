# Class 11, Unit 1 - Exercise 1.4 (run inside unit01.py)
W = OMEGA            # omega written out for the checks: (-1 + sqrt(3)*I)/2
W2 = OMEGA2          # omega squared


def cube_roots(label, a):
    c = sp.Integer(a) ** sp.Rational(1, 3) if a > 0 else -sp.Integer(-a) ** sp.Rational(1, 3)
    c = sp.nsimplify(c)
    w = (-1 + s3 * I) / 2
    roots = [C(c), exact(c * w), exact(c * w ** 2)]
    sign = "-" if a > 0 else "+"
    cab = abs(c)
    steps = [
        S(rf"x^3 = {a} \Rightarrow x^3 {sign} {abs(a)} = 0 \Rightarrow x^3 {sign} {L(cab)}^3 = 0", f"Let $x$ be a cube root of ${a}$.",
          f"فرض کریں $x$، ${a}$ کا جذر المکعب ہے۔", f"({py(c)})**3 == {a}"),
        S(rf"(x {_minus(c)})\left(x^2 {'+' if c > 0 else '-'} {L(cab)}x + {L(c ** 2)}\right) = 0",
          "Use $a^3 - b^3 = (a - b)(a^2 + ab + b^2)$ (or the sum of cubes).", "$a^3 - b^3 = (a - b)(a^2 + ab + b^2)$ (یا مکعبوں کا مجموعہ) استعمال کریں۔",
          f"expand((z - ({sp.sstr(c)}))*(z**2 + ({sp.sstr(c)})*z + ({sp.sstr(c ** 2)}))) == z**3 - ({a})"),
        S(rf"x = {L(c)} \quad\text{{or}}\quad x = \frac{{{L(-c)} \pm \sqrt{{{L(c ** 2)} - {L(4 * c ** 2)}}}}}{{2}} = \frac{{{L(-c)} \pm \sqrt{{{L(-3 * c ** 2)}}}}}{{2}}",
          "The first factor gives the real root; solve the quadratic factor with the quadratic formula.",
          "پہلا جزو حقیقی جذر دیتا ہے؛ دو درجی جزو کو دو درجی کلیے سے حل کریں۔"),
        S(rf"x = {ctex(roots[1])},\quad {ctex(roots[2])}", "$\\sqrt{" + L(-3 * c ** 2) + "} = " + ctex(sp.sqrt(3 * c ** 2) * I) + "$; these are $" + L(c) + "\\omega$ and $" + L(c) + "\\omega^2$.",
          "یہ $" + L(c) + "\\omega$ اور $" + L(c) + "\\omega^2$ ہیں۔", *[f"expand(({py(r)})**3) == {a}" for r in roots[1:]]),
        S(r"\text{Cube roots: } " + ",\\ ".join(ctex(r) for r in roots), "So the three cube roots are $c$, $c\\omega$, $c\\omega^2$.",
          "اس طرح تین جذر المکعب $c$، $c\\omega$، $c\\omega^2$ ہیں۔")]
    return P(label, steps, "$" + ",\\ ".join(ctex(r) for r in roots) + "$", prompt=f"${a}$")


ex("ex1.4", 1, "Find the three cube roots of: (i) $8$ (ii) $-8$ (iii) $-27$ (iv) $64$ (v) $-125$", [
    cube_roots(l, a) for l, a in [("i", 8), ("ii", -8), ("iii", -27), ("iv", 64), ("v", -125)]], "1.4")


def fourth_roots(label, a):
    c = sp.Integer(a) ** sp.Rational(1, 4)
    c = sp.nsimplify(c)
    roots = [C(c), C(-c), C(0, c), C(0, -c)]
    steps = [
        S(rf"x^4 = {a} \Rightarrow x^4 - {a} = 0", f"Let $x$ be a fourth root of ${a}$.", f"فرض کریں $x$، ${a}$ کا چوتھا جذر ہے۔"),
        S(rf"(x^2 - {L(c ** 2)})(x^2 + {L(c ** 2)}) = 0", "Difference of squares.", "مربعوں کا فرق۔",
          f"expand((z**2 - {sp.sstr(c ** 2)})*(z**2 + {sp.sstr(c ** 2)})) == z**4 - {a}"),
        S(rf"x^2 = {L(c ** 2)} \Rightarrow x = \pm {L(c)};\qquad x^2 = -{L(c ** 2)} \Rightarrow x = \pm {L(c)}i", "Solve each factor.", "ہر جزو حل کریں۔",
          *[f"expand(({py(r)})**4) == {a}" for r in roots]),
        S(rf"{L(c)} + (-{L(c)}) + {L(c)}i + (-{L(c)}i) = 0", "Add the four roots: they cancel in pairs, so the sum is zero.",
          "چاروں جذر جمع کریں: جوڑوں میں کٹ جاتے ہیں، اس لیے مجموعہ صفر ہے۔", " + ".join(py(r) for r in roots) + " == 0")]
    return P(label, steps, rf"$\pm {L(c)},\ \pm {L(c)}i$; sum $= 0$", prompt=f"${a}$")


ex("ex1.4", 2, "Find the four fourth roots of $16, 81, 625$. Also show that their sum is zero in each case.", [
    fourth_roots("i", 16), fourth_roots("ii", 81), fourth_roots("iii", 625)], "1.4")

OM = (r"\omega = \frac{-1 + \sqrt{3}i}{2},\quad \omega^3 = 1,\quad 1 + \omega + \omega^2 = 0",
      "The imaginary cube roots of unity satisfy $\\omega^3 = 1$ and $1 + \\omega + \\omega^2 = 0$.",
      "اکائی کے خیالی جذر المکعب $\\omega^3 = 1$ اور $1 + \\omega + \\omega^2 = 0$ کو پورا کرتے ہیں۔",
      f"expand({W}**3) == 1", f"expand(1 + {W} + {W}**2) == 0")

ex("ex1.4", 3, "If $1, \\omega, \\omega^2$ are the cube roots of unity, show that $1 + \\omega^n + \\omega^{2n} = 3$, where $n$ is a multiple of $3$.", [P("", [
    S(*OM),
    S(r"n = 3k,\ k \in \mathbb{Z} \Rightarrow \omega^n = \omega^{3k} = (\omega^3)^k = 1^k = 1", "A multiple of 3 is $3k$; use $\\omega^3 = 1$.",
      "3 کا مضرب $3k$ ہوتا ہے؛ $\\omega^3 = 1$ استعمال کریں۔", f"expand({W}**6) == 1"),
    S(r"\omega^{2n} = (\omega^{n})^2 = 1^2 = 1", "Square the result.", "نتیجے کا مربع لیں۔", f"expand({W}**12) == 1"),
    S(r"1 + \omega^n + \omega^{2n} = 1 + 1 + 1 = 3", "Add.", "جمع کریں۔", f"expand(1 + {W}**3 + {W}**6) == 3", f"expand(1 + {W}**9 + {W}**18) == 3")],
    "proved: $1 + \\omega^n + \\omega^{2n} = 1 + 1 + 1 = 3$")], "1.4")

ex("ex1.4", 4, "Evaluate: (i) $\\left(\\frac{-1+\\sqrt{-3}}{2}\\right)^7 + \\left(\\frac{-1-\\sqrt{-3}}{2}\\right)^7$ (ii) $(-1+\\sqrt{-3})^5 + (-1-\\sqrt{-3})^5$", [
    P("i", [S(r"\frac{-1 + \sqrt{-3}}{2} = \frac{-1 + \sqrt{3}i}{2} = \omega,\quad \frac{-1 - \sqrt{-3}}{2} = \omega^2", "Write $\\sqrt{-3} = \\sqrt{3}i$: these are $\\omega$ and $\\omega^2$.",
              "$\\sqrt{-3} = \\sqrt{3}i$ لکھیں: یہ $\\omega$ اور $\\omega^2$ ہیں۔", f"expand({W}**2) == expand({W2})"),
            S(r"\omega^7 + (\omega^2)^7 = \omega^7 + \omega^{14} = \omega^{6}\omega + \omega^{12}\omega^2", "Split off powers of $\\omega^3 = 1$.",
              "$\\omega^3 = 1$ کی طاقتیں الگ کریں۔"),
            S(r"= \omega + \omega^2 = -1", "Use $1 + \\omega + \\omega^2 = 0$.", "$1 + \\omega + \\omega^2 = 0$ استعمال کریں۔",
              f"expand({W}**7 + {W2}**7) == -1")], "$-1$", prompt="$\\left(\\frac{-1+\\sqrt{-3}}{2}\\right)^7 + \\left(\\frac{-1-\\sqrt{-3}}{2}\\right)^7$"),
    P("ii", [S(r"-1 + \sqrt{-3} = 2\omega,\quad -1 - \sqrt{-3} = 2\omega^2", "Each is twice a cube root of unity.", "ہر ایک اکائی کے جذر المکعب کا دگنا ہے۔"),
             S(r"(2\omega)^5 + (2\omega^2)^5 = 32\left(\omega^5 + \omega^{10}\right) = 32\left(\omega^2 + \omega\right)", "Take $2^5 = 32$ out; $\\omega^5 = \\omega^2$, $\\omega^{10} = \\omega$.",
               "$2^5 = 32$ باہر نکالیں؛ $\\omega^5 = \\omega^2$، $\\omega^{10} = \\omega$۔", f"expand({W}**5) == expand({W}**2)"),
             S(r"= 32(-1) = -32", "Use $\\omega + \\omega^2 = -1$.", "$\\omega + \\omega^2 = -1$ استعمال کریں۔",
               "expand((-1 + sqrt(3)*I)**5 + (-1 - sqrt(3)*I)**5) == -32")], "$-32$", prompt="$(-1+\\sqrt{-3})^5 + (-1-\\sqrt{-3})^5$")], "1.4")

ex("ex1.4", 5, "Show that $(1 - \\omega + \\omega^2)(1 - \\omega^2 + \\omega^4)(1 - \\omega^4 + \\omega^8) \\dots$ to $2n$ factors $= 2^{2n}$.", [P("", [
    S(*OM),
    S(r"1 - \omega + \omega^2 = (1 + \omega^2) - \omega = -\omega - \omega = -2\omega", "Replace $1 + \\omega^2$ by $-\\omega$.", "$1 + \\omega^2$ کی جگہ $-\\omega$ رکھیں۔",
      f"expand(1 - {W} + {W}**2) == expand(-2*{W})"),
    S(r"1 - \omega^2 + \omega^4 = 1 - \omega^2 + \omega = -2\omega^2", "$\\omega^4 = \\omega$; replace $1 + \\omega$ by $-\\omega^2$.",
      "$\\omega^4 = \\omega$؛ $1 + \\omega$ کی جگہ $-\\omega^2$ رکھیں۔", f"expand(1 - {W}**2 + {W}**4) == expand(-2*{W}**2)"),
    S(r"1 - \omega^4 + \omega^8 = 1 - \omega + \omega^2 = -2\omega", "$\\omega^4 = \\omega$, $\\omega^8 = \\omega^2$: the factors repeat $-2\\omega, -2\\omega^2, -2\\omega, \\dots$",
      "$\\omega^4 = \\omega$، $\\omega^8 = \\omega^2$: اجزاء $-2\\omega, -2\\omega^2, \\dots$ دہراتے ہیں۔", f"expand(1 - {W}**4 + {W}**8) == expand(-2*{W})"),
    S(r"(-2\omega)(-2\omega^2) = 4\omega^3 = 4", "Each consecutive pair of factors multiplies to 4.", "ہر دو لگاتار اجزاء کا حاصل ضرب 4 ہے۔",
      f"expand((-2*{W})*(-2*{W}**2)) == 4"),
    S(r"2n \text{ factors} = n \text{ pairs} \Rightarrow 4^n = (2^2)^n = 2^{2n}", "There are $n$ such pairs.", "ایسے $n$ جوڑے ہیں۔",
      f"expand((1 - {W} + {W}**2)*(1 - {W}**2 + {W}**4)*(1 - {W}**4 + {W}**8)*(1 - {W}**8 + {W}**16)) == 2**4")],
    "proved: the product is $4^n = 2^{2n}$")], "1.4")

ex("ex1.4", 6, "Prove that $\\left(\\frac{i+\\sqrt{3}}{2}\\right)^8 + \\left(\\frac{i-\\sqrt{3}}{2}\\right)^8 = -1$.", [P("", [
    S(r"\frac{i + \sqrt{3}}{2} = -i\left(\frac{-1 + \sqrt{3}i}{2}\right) = -i\omega,\quad \frac{i - \sqrt{3}}{2} = -i\left(\frac{-1 - \sqrt{3}i}{2}\right) = -i\omega^2",
      "Take $-i$ out of each bracket (since $-i \\cdot \\sqrt{3}i = \\sqrt{3}$).", "ہر قوسین سے $-i$ باہر نکالیں (کیونکہ $-i \\cdot \\sqrt{3}i = \\sqrt{3}$)۔",
      f"expand(-I*{W}) == (I + sqrt(3))/2", f"expand(-I*{W2}) == (I - sqrt(3))/2"),
    S(r"(-i\omega)^8 + (-i\omega^2)^8 = (-i)^8\left(\omega^8 + \omega^{16}\right)", "Take $(-i)^8$ common.", "$(-i)^8$ مشترک لیں۔"),
    S(r"(-i)^8 = 1,\quad \omega^8 = \omega^2,\quad \omega^{16} = \omega", "Use $i^4 = 1$ and $\\omega^3 = 1$.", "$i^4 = 1$ اور $\\omega^3 = 1$ استعمال کریں۔",
      "(-I)**8 == 1", f"expand({W}**8) == expand({W}**2)"),
    S(r"= \omega^2 + \omega = -1", "Use $1 + \\omega + \\omega^2 = 0$.", "$1 + \\omega + \\omega^2 = 0$ استعمال کریں۔",
      "expand(((I + sqrt(3))/2)**8 + ((I - sqrt(3))/2)**8) == -1")], "proved: the sum is $\\omega^2 + \\omega = -1$")], "1.4")

ex("ex1.4", 7, "Evaluate $\\sum_{k=0}^{5} \\omega^{2k}$, where $\\omega$ is a cube root of unity.", [P("", [
    S(r"\sum_{k=0}^{5}\omega^{2k} = 1 + \omega^2 + \omega^4 + \omega^6 + \omega^8 + \omega^{10}", "Write out the six terms ($k = 0$ to $5$).",
      "چھ ارکان لکھیں ($k = 0$ سے $5$ تک)۔"),
    S(r"= 1 + \omega^2 + \omega + 1 + \omega^2 + \omega", "Reduce the powers with $\\omega^3 = 1$.", "$\\omega^3 = 1$ سے طاقتیں کم کریں۔",
      f"expand({W}**4) == expand({W})", f"expand({W}**10) == expand({W})"),
    S(r"= 2\left(1 + \omega + \omega^2\right) = 2(0) = 0", "Group into $1 + \\omega + \\omega^2 = 0$.", "$1 + \\omega + \\omega^2 = 0$ کی صورت میں گروہ بنائیں۔",
      f"expand(sum({W}**(2*k) for k in range(6))) == 0" if False else f"expand(1 + {W}**2 + {W}**4 + {W}**6 + {W}**8 + {W}**10) == 0")], "$0$")], "1.4")

ex("ex1.4", 8, "If $\\omega$ is an imaginary cube root of unity, prove that $\\frac{a + b\\omega^2 + c\\omega}{a\\omega^2 + b\\omega + c} = \\omega$.", [P("", [
    S(r"\omega\left(a\omega^2 + b\omega + c\right) = a\omega^3 + b\omega^2 + c\omega", "Multiply the denominator by $\\omega$.", "نسب نما کو $\\omega$ سے ضرب دیں۔"),
    S(r"= a + b\omega^2 + c\omega", "Use $\\omega^3 = 1$: this is exactly the numerator.", "$\\omega^3 = 1$ استعمال کریں: یہ بالکل شمار کنندہ ہے۔",
      f"expand({W}*(a*{W}**2 + b*{W} + c)) == expand(a + b*{W}**2 + c*{W})"),
    S(r"\therefore\ \frac{a + b\omega^2 + c\omega}{a\omega^2 + b\omega + c} = \frac{\omega\left(a\omega^2 + b\omega + c\right)}{a\omega^2 + b\omega + c} = \omega",
      "Cancel the common factor (the denominator is not zero).", "مشترک جزو کاٹ دیں (نسب نما صفر نہیں)۔",
      f"(a + b*{W}**2 + c*{W})/(a*{W}**2 + b*{W} + c) == {W}")], "proved: the fraction equals $\\omega$")], "1.4")

ex("ex1.4", 9, "If $\\omega$ is a cube root of unity, prove that $\\frac{a\\omega^{12} + b\\omega^{17} + c\\omega^{19}}{a\\omega^{14} + b\\omega^{22} + c\\omega^{30}} = \\omega$.", [P("", [
    S(r"\omega^{12} = 1,\ \omega^{17} = \omega^2,\ \omega^{19} = \omega;\quad \omega^{14} = \omega^2,\ \omega^{22} = \omega,\ \omega^{30} = 1",
      "Reduce each power with $\\omega^3 = 1$ (divide the power by 3 and keep the remainder).", "ہر طاقت کو $\\omega^3 = 1$ سے کم کریں (3 سے تقسیم کر کے باقی رکھیں)۔",
      f"expand({W}**17) == expand({W}**2)", f"expand({W}**19) == expand({W})", f"expand({W}**22) == expand({W})", f"expand({W}**14) == expand({W}**2)"),
    S(r"\frac{a + b\omega^2 + c\omega}{a\omega^2 + b\omega + c}", "The fraction becomes the one in Question 8.", "کسر سوال 8 والی بن جاتی ہے۔"),
    S(r"= \frac{\omega\left(a\omega^2 + b\omega + c\right)}{a\omega^2 + b\omega + c} = \omega", "As there, the numerator is $\\omega$ times the denominator.",
      "وہاں کی طرح شمار کنندہ، نسب نما کا $\\omega$ گنا ہے۔",
      f"(a*{W}**12 + b*{W}**17 + c*{W}**19)/(a*{W}**14 + b*{W}**22 + c*{W}**30) == {W}")], "proved: the fraction equals $\\omega$")], "1.4")
