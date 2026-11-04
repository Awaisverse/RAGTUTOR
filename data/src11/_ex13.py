# Class 11, Unit 1 - Exercise 1.3 (run inside unit01.py: uses its ex(), note(), S, P, T, C, I, L, ...)


def sq_sum(label, poly_tex, lines, prod_py, poly_py, answer):
    """A sum of two squares A^2 + B^2 = A^2 - (Bi)^2 = (A + Bi)(A - Bi)."""
    steps = [S(lines[0], "Write the sum as a difference of squares using $i^2 = -1$: $B^2 = -(Bi)^2$.",
               "$i^2 = -1$ کی مدد سے مجموعے کو مربعوں کے فرق کی صورت میں لکھیں: $B^2 = -(Bi)^2$۔")]
    steps += [S(t, "Use $A^2 - B^2 = (A + B)(A - B)$.", "$A^2 - B^2 = (A + B)(A - B)$ استعمال کریں۔", f"expand({prod_py}) == {poly_py}") for t in lines[1:]]
    return P(label, steps, answer, prompt=f"${poly_tex}$")


def _sgn(v):
    return "+" if v >= 0 else "-"


def complete_sq(label, a, b, c, mode="factor"):
    """a z^2 + b z + c with real coefficients and complex roots: complete the square, then factorize or solve."""
    a, b, c = sp.Integer(a), sp.Integer(b), sp.Integer(c)
    p, q = b / a, c / a                                     # z^2 + p z + q
    h = -p / 2                                              # (z - h)^2 = -k
    k = q - h ** 2                                          # > 0 here: the roots are h +- i sqrt(k)
    s = sp.sqrt(k)
    r1, r2 = exact(h + s * I), exact(h - s * I)
    poly = a * Z ** 2 + b * Z + c
    ptex = sp.latex(poly)
    zh = rf"\left(z {_minus(h)}\right)"
    half = abs(p) / 2
    steps = []
    if mode == "solve":
        first = rf"{ptex} = 0"
        if a != 1:
            steps.append(S(rf"{first} \Rightarrow z^2 {_sgn(p)} {L(abs(p))}z + {L(q)} = 0", f"Divide by ${L(a)}$ so that the coefficient of $z^2$ is 1.",
                           f"$z^2$ کا عددی سر 1 بنانے کے لیے ${L(a)}$ سے تقسیم کریں۔",
                           f"expand(({sp.sstr(poly)})/{a}) == expand(z**2 + ({sp.sstr(p)})*z + ({sp.sstr(q)}))"))
        steps.append(S(rf"z^2 {_sgn(p)} {L(abs(p))}z = {L(-q)}", "Move the constant term to the right side.", "مستقل رکن کو دائیں طرف لے جائیں۔"))
        steps.append(S(rf"z^2 {_sgn(p)} 2\left({L(half)}\right)z + \left({L(half)}\right)^2 = {L(-q)} + \left({L(half)}\right)^2",
                       "Add the square of half the coefficient of $z$ to both sides.", "دونوں طرف $z$ کے عددی سر کے نصف کا مربع جمع کریں۔",
                       f"{sp.sstr(-q)} + ({sp.sstr(half)})**2 == {sp.sstr(-k)}"))
        steps.append(S(rf"{zh}^2 = {L(-k)}", "The left side is a perfect square.", "بائیں جانب مکمل مربع ہے۔",
                       f"expand((z - ({sp.sstr(h)}))**2) == expand(z**2 + ({sp.sstr(p)})*z + ({sp.sstr(h ** 2)}))"))
        steps.append(S(rf"z {_minus(h)} = \pm\sqrt{{{L(-k)}}} = \pm {ctex(s * I)}", "Take the square root: $\\sqrt{-m} = i\\sqrt{m}$ for $m > 0$.",
                       "جذر لیں: $m > 0$ کے لیے $\\sqrt{-m} = i\\sqrt{m}$۔", f"({py(s * I)})**2 == {py(-k)}"))
        steps.append(S(rf"z = {L(h)} \pm {ctex(s * I)}", "Move the constant across; both values satisfy the equation.",
                       "مستقل کو دوسری طرف لے جائیں؛ دونوں قیمتیں مساوات کو پورا کرتی ہیں۔",
                       f"expand(({sp.sstr(poly)}).subs(z, {py(r1)})) == 0", f"expand(({sp.sstr(poly)}).subs(z, {py(r2)})) == 0"))
        return P(label, steps, rf"$z = {L(h)} \pm {ctex(s * I)}$", prompt=f"${ptex} = 0$")
    lead = "" if a == 1 else L(a)
    inner = rf"z^2 {_sgn(p)} {L(abs(p))}z + {L(q)}"
    if a != 1:
        steps.append(S(rf"{ptex} = {L(a)}\left({inner}\right)", f"Take ${L(a)}$ common.", f"${L(a)}$ مشترک لیں۔",
                       f"expand({a}*(z**2 + ({sp.sstr(p)})*z + ({sp.sstr(q)}))) == {sp.sstr(poly)}"))
    steps.append(S(rf"{inner} = z^2 {_sgn(p)} 2\left({L(half)}\right)z + \left({L(half)}\right)^2 + {L(q)} - \left({L(half)}\right)^2",
                   "Add and subtract the square of half the coefficient of $z$.", "$z$ کے عددی سر کے نصف کا مربع جمع اور تفریق کریں۔"))
    steps.append(S(rf"= {zh}^2 + {L(k)}", "Write the perfect square and simplify the constant.", "مکمل مربع لکھیں اور مستقل کو سادہ کریں۔",
                   f"expand((z - ({sp.sstr(h)}))**2 + ({sp.sstr(k)})) == expand(z**2 + ({sp.sstr(p)})*z + ({sp.sstr(q)}))"))
    steps.append(S(rf"= {zh}^2 - \left({ctex(s * I)}\right)^2", "Write $+m$ as $-(i\\sqrt{m})^2$ to get a difference of squares.",
                   "مربعوں کا فرق بنانے کے لیے $+m$ کو $-(i\\sqrt{m})^2$ لکھیں۔", f"({py(s * I)})**2 == {py(-k)}"))
    ftex = lead + rf"\left(z {_minus(r1)}\right)\left(z {_minus(r2)}\right)"
    steps.append(S(rf"{ptex} = {ftex}", "Use $A^2 - B^2 = (A + B)(A - B)$; multiplying out gives back the polynomial.",
                   "$A^2 - B^2 = (A + B)(A - B)$ استعمال کریں؛ ضرب دینے سے وہی کثیر رقمی آتی ہے۔", product_check([r1, r2], a, poly)))
    return P(label, steps, f"${ftex}$", prompt=f"${ptex}$")


Q31 = [
    sq_sum("i", "a^2 + 4b^2", [r"a^2 + 4b^2 = a^2 - (2bi)^2", r"= (a + 2bi)(a - 2bi)"], "(a + 2*b*I)*(a - 2*b*I)", "a**2 + 4*b**2", "$(a + 2bi)(a - 2bi)$"),
    sq_sum("ii", "9a^2 + 16b^2", [r"9a^2 + 16b^2 = (3a)^2 - (4bi)^2", r"= (3a + 4bi)(3a - 4bi)"], "(3*a + 4*b*I)*(3*a - 4*b*I)", "9*a**2 + 16*b**2",
           "$(3a + 4bi)(3a - 4bi)$"),
    sq_sum("iii", "3x^2 + 3y^2", [r"3x^2 + 3y^2 = 3\left(x^2 + y^2\right) = 3\left[x^2 - (iy)^2\right]", r"= 3(x + iy)(x - iy)"], "3*(x + I*y)*(x - I*y)",
           "3*x**2 + 3*y**2", "$3(x + iy)(x - iy)$"),
    sq_sum("iv", "144x^2 + 225y^2", [r"144x^2 + 225y^2 = 9\left(16x^2 + 25y^2\right) = 9\left[(4x)^2 - (5iy)^2\right]", r"= 9(4x + 5iy)(4x - 5iy)"],
           "9*(4*x + 5*I*y)*(4*x - 5*I*y)", "144*x**2 + 225*y**2", "$9(4x + 5iy)(4x - 5iy)$"),
    P("v", [S(r"z^2 - 2iz - 1 = z^2 - 2iz + i^2", "Write $-1$ as $i^2$.", "$-1$ کو $i^2$ لکھیں۔", "I**2 == -1"),
            S(r"= (z - i)^2 = (z - i)(z - i)", "This is $(a - b)^2 = a^2 - 2ab + b^2$ with $a = z$, $b = i$.", "یہ $(a - b)^2$ ہے جہاں $a = z$ اور $b = i$۔",
              "expand((z - I)**2) == z**2 - 2*I*z - 1")], "$(z - i)(z - i)$", prompt="$z^2 - 2iz - 1$"),
    complete_sq("vi", 1, 6, 13), complete_sq("vii", 1, 4, 5), complete_sq("viii", 2, -22, 65)]
ex("ex1.3", 1, "Factorize the following: (i) $a^2 + 4b^2$ (ii) $9a^2 + 16b^2$ (iii) $3x^2 + 3y^2$ (iv) $144x^2 + 225y^2$ (v) $z^2 - 2iz - 1$ (vi) $z^2 + 6z + 13$ "
   "(vii) $z^2 + 4z + 5$ (viii) $2z^2 - 22z + 65$", Q31, "1.3")


def lin(label, poly_tex, rows, roots, lead, poly_py):
    """rows: (math, en, ur, check) working; the last line gives the linear factors, checked by multiplying out."""
    steps = [S(m, en, ur, *([c] if c else [])) for m, en, ur, c in rows]
    ftex = ("" if lead == 1 else L(lead)) + "".join(rf"\left(z {_minus(r)}\right)" for r in roots)
    steps.append(S(rf"{poly_tex} = {ftex}", "Write the product of linear factors; multiplying out gives back the polynomial.",
                   "خطی اجزائے ضربی کا حاصل ضرب لکھیں؛ ضرب دینے سے وہی کثیر رقمی واپس آتی ہے۔",
                   product_check(roots, lead, sp.sympify(poly_py, locals={"z": Z}))))
    return P(label, steps, f"${ftex}$", prompt=f"${poly_tex}$")


s3 = sp.sqrt(3)
Q32 = [
    lin("i", "z^3 + 8", [(r"z^3 + 8 = z^3 + 2^3 = (z + 2)(z^2 - 2z + 4)", "Sum of cubes: $a^3 + b^3 = (a + b)(a^2 - ab + b^2)$.",
                          "مکعبوں کا مجموعہ: $a^3 + b^3 = (a + b)(a^2 - ab + b^2)$۔", "expand((z + 2)*(z**2 - 2*z + 4)) == z**3 + 8"),
                         (r"z^2 - 2z + 4 = (z - 1)^2 + 3 = (z - 1)^2 - (\sqrt{3}i)^2", "Complete the square in the quadratic factor.",
                          "دو درجی جزو میں مربع مکمل کریں۔", "expand((z - 1)**2 - (sqrt(3)*I)**2) == z**2 - 2*z + 4")],
        [C(-2), C(1, s3), C(1, -s3)], 1, "z**3 + 8"),
    lin("ii", "z^3 + 27", [(r"z^3 + 27 = (z + 3)(z^2 - 3z + 9)", "Sum of cubes with $b = 3$.", "مکعبوں کا مجموعہ، $b = 3$۔",
                            "expand((z + 3)*(z**2 - 3*z + 9)) == z**3 + 27"),
                           (r"z^2 - 3z + 9 = \left(z - \tfrac{3}{2}\right)^2 + \tfrac{27}{4} = \left(z - \tfrac{3}{2}\right)^2 - \left(\tfrac{3\sqrt{3}}{2}i\right)^2",
                            "Complete the square: $9 - \\frac{9}{4} = \\frac{27}{4}$ and $\\sqrt{\\frac{27}{4}} = \\frac{3\\sqrt{3}}{2}$.",
                            "مربع مکمل کریں: $9 - \\frac{9}{4} = \\frac{27}{4}$۔", "expand((z - R(3,2))**2 - (3*sqrt(3)/2*I)**2) == z**2 - 3*z + 9")],
        [C(-3), C(R(3, 2), 3 * s3 / 2), C(R(3, 2), -3 * s3 / 2)], 1, "z**3 + 27"),
    lin("iii", "z^3 - 2z^2 + 16z - 32", [(r"= z^2(z - 2) + 16(z - 2) = (z - 2)(z^2 + 16)", "Group the terms in pairs and take out the common factor $z - 2$.",
                                          "ارکان کو جوڑوں میں گروہ بنا کر مشترک جزو $z - 2$ باہر نکالیں۔", "expand((z - 2)*(z**2 + 16)) == z**3 - 2*z**2 + 16*z - 32"),
                                         (r"z^2 + 16 = z^2 - (4i)^2 = (z - 4i)(z + 4i)", "Difference of squares with $16 = -(4i)^2$.",
                                          "مربعوں کا فرق، $16 = -(4i)^2$۔", "expand((z - 4*I)*(z + 4*I)) == z**2 + 16")],
        [C(2), C(0, 4), C(0, -4)], 1, "z**3 - 2*z**2 + 16*z - 32"),
    lin("iv", "z^4 + 21z^2 - 100", [(r"= z^4 + 25z^2 - 4z^2 - 100 = (z^2 + 25)(z^2 - 4)", "Treat it as a quadratic in $z^2$: $25 \\times (-4) = -100$ and $25 - 4 = 21$.",
                                     "اسے $z^2$ میں دو درجی سمجھیں: $25 \\times (-4) = -100$ اور $25 - 4 = 21$۔", "expand((z**2 + 25)*(z**2 - 4)) == z**4 + 21*z**2 - 100"),
                                    (r"z^2 - 4 = (z - 2)(z + 2),\quad z^2 + 25 = (z - 5i)(z + 5i)", "Factor each square difference.", "مربعوں کے ہر فرق کی تجزی کریں۔",
                                     "expand((z - 5*I)*(z + 5*I)) == z**2 + 25")],
        [C(2), C(-2), C(0, 5), C(0, -5)], 1, "z**4 + 21*z**2 - 100"),
    lin("v", "z^4 - 16", [(r"z^4 - 16 = (z^2 - 4)(z^2 + 4)", "Difference of squares: $(z^2)^2 - 4^2$.", "مربعوں کا فرق: $(z^2)^2 - 4^2$۔",
                           "expand((z**2 - 4)*(z**2 + 4)) == z**4 - 16"),
                          (r"z^2 - 4 = (z - 2)(z + 2),\quad z^2 + 4 = (z - 2i)(z + 2i)", "Again: $z^2 + 4 = z^2 - (2i)^2$.", "دوبارہ: $z^2 + 4 = z^2 - (2i)^2$۔",
                           "expand((z - 2*I)*(z + 2*I)) == z**2 + 4")],
        [C(2), C(-2), C(0, 2), C(0, -2)], 1, "z**4 - 16"),
    lin("vi", "z^4 + 3z^2 - 4", [(r"= z^4 + 4z^2 - z^2 - 4 = (z^2 + 4)(z^2 - 1)", "Split the middle term: $4 \\times (-1) = -4$, $4 - 1 = 3$.",
                                  "درمیانی رکن تقسیم کریں: $4 \\times (-1) = -4$، $4 - 1 = 3$۔", "expand((z**2 + 4)*(z**2 - 1)) == z**4 + 3*z**2 - 4"),
                                 (r"z^2 - 1 = (z - 1)(z + 1),\quad z^2 + 4 = (z - 2i)(z + 2i)", "Factor each bracket.", "ہر قوسین کی تجزی کریں۔",
                                  "expand((z - 1)*(z + 1)) == z**2 - 1")],
        [C(1), C(-1), C(0, 2), C(0, -2)], 1, "z**4 + 3*z**2 - 4"),
    lin("vii", "z^4 + 5z^2 + 6", [(r"= z^4 + 2z^2 + 3z^2 + 6 = (z^2 + 2)(z^2 + 3)", "Split the middle term: $2 \\times 3 = 6$, $2 + 3 = 5$.",
                                   "درمیانی رکن تقسیم کریں: $2 \\times 3 = 6$، $2 + 3 = 5$۔", "expand((z**2 + 2)*(z**2 + 3)) == z**4 + 5*z**2 + 6"),
                                  (r"z^2 + 2 = (z - \sqrt{2}i)(z + \sqrt{2}i),\quad z^2 + 3 = (z - \sqrt{3}i)(z + \sqrt{3}i)", "Write each as a difference of squares.",
                                   "ہر ایک کو مربعوں کے فرق کی صورت میں لکھیں۔", "expand((z - sqrt(2)*I)*(z + sqrt(2)*I)) == z**2 + 2")],
        [C(0, sp.sqrt(2)), C(0, -sp.sqrt(2)), C(0, s3), C(0, -s3)], 1, "z**4 + 5*z**2 + 6"),
    lin("viii", "z^4 - 32z^2 - 3969", [(r"= z^4 - 81z^2 + 49z^2 - 3969 = (z^2 - 81)(z^2 + 49)", "Split the middle term: $(-81) \\times 49 = -3969$, $-81 + 49 = -32$.",
                                        "درمیانی رکن تقسیم کریں: $(-81) \\times 49 = -3969$، $-81 + 49 = -32$۔",
                                        "expand((z**2 - 81)*(z**2 + 49)) == z**4 - 32*z**2 - 3969"),
                                       (r"z^2 - 81 = (z - 9)(z + 9),\quad z^2 + 49 = (z - 7i)(z + 7i)", "Factor each bracket.", "ہر قوسین کی تجزی کریں۔",
                                        "expand((z - 7*I)*(z + 7*I)) == z**2 + 49")],
        [C(9), C(-9), C(0, 7), C(0, -7)], 1, "z**4 - 32*z**2 - 3969")]
ex("ex1.3", 2, "Factorize the following polynomial into its linear factors: (i) $z^3 + 8$ (ii) $z^3 + 27$ (iii) $z^3 - 2z^2 + 16z - 32$ (iv) $z^4 + 21z^2 - 100$ "
   "(v) $z^4 - 16$ (vi) $z^4 + 3z^2 - 4$ (vii) $z^4 + 5z^2 + 6$ (viii) $z^4 - 32z^2 - 3969$", Q32, "1.3")

ex("ex1.3", 3, "Find the roots of $z^4 + 7z^2 - 144 = 0$ and hence express it as product of linear factors.", [P("", [
    S(r"z^4 + 16z^2 - 9z^2 - 144 = 0 \Rightarrow (z^2 + 16)(z^2 - 9) = 0", "Split the middle term: $16 \\times (-9) = -144$, $16 - 9 = 7$.",
      "درمیانی رکن تقسیم کریں: $16 \\times (-9) = -144$، $16 - 9 = 7$۔", "expand((z**2 + 16)*(z**2 - 9)) == z**4 + 7*z**2 - 144"),
    S(r"z^2 = -16 \Rightarrow z = \pm 4i;\qquad z^2 = 9 \Rightarrow z = \pm 3", "Set each factor to zero.", "ہر جزو کو صفر کے برابر رکھیں۔",
      "(4*I)**4 + 7*(4*I)**2 - 144 == 0", "3**4 + 7*3**2 - 144 == 0"),
    S(r"z^4 + 7z^2 - 144 = (z - 3)(z + 3)(z - 4i)(z + 4i)", "Each root $r$ gives a linear factor $z - r$.", "ہر جذر $r$ سے خطی جزو $z - r$ بنتا ہے۔",
      "expand((z - 3)*(z + 3)*(z - 4*I)*(z + 4*I)) == z**4 + 7*z**2 - 144")],
    "roots $3, -3, 4i, -4i$; $(z - 3)(z + 3)(z - 4i)(z + 4i)$")], "1.3")

ex("ex1.3", 4, "Solve the following complex quadratic equation by completing square method: (i) $2z^2 - 3z + 4 = 0$ (ii) $z^2 - 6z + 30 = 0$ (iii) $3z^2 - 18z + 50 = 0$ "
   "(iv) $z^2 + 4z + 13 = 0$ (v) $2z^2 + 6z + 9 = 0$ (vi) $3z^2 - 5z + 7 = 0$", [
       complete_sq(l, a, b, c, "solve") for l, a, b, c in
       [("i", 2, -3, 4), ("ii", 1, -6, 30), ("iii", 3, -18, 50), ("iv", 1, 4, 13), ("v", 2, 6, 9), ("vi", 3, -5, 7)]], "1.3")


def solve_by_factors(label, poly_tex, rows, roots, poly_py):
    steps = [S(m, en, ur, *([c] if c else [])) for m, en, ur, c in rows]
    steps.append(S(r"z = " + ",\\ ".join(ctex(r) for r in roots), "Each factor equal to zero gives a root; every root satisfies the equation.",
                   "ہر جزو کو صفر رکھنے سے ایک جذر ملتا ہے؛ ہر جذر مساوات کو پورا کرتا ہے۔",
                   *[f"expand(({poly_py}).subs(z, {py(r)})) == 0" for r in roots]))
    return P(label, steps, roots_answer(roots), prompt=f"${poly_tex} = 0$")


ex("ex1.3", 5, "Solve the following equations: (i) $2z^4 - 32 = 0$ (ii) $3z^5 - 243z = 0$ (iii) $5z^5 - 5z = 0$ (iv) $z^3 - 5z^2 + z - 5 = 0$ "
   "(v) $4z^4 - 25z^2 - 21 = 0$ (vi) $z^3 + z^2 + z + 1 = 0$", [
       solve_by_factors("i", "2z^4 - 32", [(r"2(z^4 - 16) = 0 \Rightarrow 2(z^2 - 4)(z^2 + 4) = 0", "Take 2 common; difference of squares.", "2 مشترک لیں؛ مربعوں کا فرق۔",
                                             "expand(2*(z**2 - 4)*(z**2 + 4)) == 2*z**4 - 32"),
                                            (r"2(z - 2)(z + 2)(z - 2i)(z + 2i) = 0", "Factor again; $z^2 + 4 = z^2 - (2i)^2$.", "دوبارہ تجزی؛ $z^2 + 4 = z^2 - (2i)^2$۔",
                                             "expand(2*(z - 2)*(z + 2)*(z - 2*I)*(z + 2*I)) == 2*z**4 - 32")],
                        [C(2), C(-2), C(0, 2), C(0, -2)], "2*z**4 - 32"),
       solve_by_factors("ii", "3z^5 - 243z", [(r"3z(z^4 - 81) = 0 \Rightarrow 3z(z^2 - 9)(z^2 + 9) = 0", "Take $3z$ common; difference of squares.",
                                               "$3z$ مشترک لیں؛ مربعوں کا فرق۔", "expand(3*z*(z**2 - 9)*(z**2 + 9)) == 3*z**5 - 243*z"),
                                              (r"3z(z - 3)(z + 3)(z - 3i)(z + 3i) = 0", "Factor each bracket.", "ہر قوسین کی تجزی کریں۔",
                                               "expand(3*z*(z - 3)*(z + 3)*(z - 3*I)*(z + 3*I)) == 3*z**5 - 243*z")],
                        [C(0), C(3), C(-3), C(0, 3), C(0, -3)], "3*z**5 - 243*z"),
       solve_by_factors("iii", "5z^5 - 5z", [(r"5z(z^4 - 1) = 0 \Rightarrow 5z(z^2 - 1)(z^2 + 1) = 0", "Take $5z$ common; difference of squares.",
                                              "$5z$ مشترک لیں؛ مربعوں کا فرق۔", "expand(5*z*(z**2 - 1)*(z**2 + 1)) == 5*z**5 - 5*z"),
                                             (r"5z(z - 1)(z + 1)(z - i)(z + i) = 0", "Factor each bracket.", "ہر قوسین کی تجزی کریں۔",
                                              "expand(5*z*(z - 1)*(z + 1)*(z - I)*(z + I)) == 5*z**5 - 5*z")],
                        [C(0), C(1), C(-1), C(0, 1), C(0, -1)], "5*z**5 - 5*z"),
       solve_by_factors("iv", "z^3 - 5z^2 + z - 5", [(r"z^2(z - 5) + 1(z - 5) = 0 \Rightarrow (z - 5)(z^2 + 1) = 0", "Group in pairs and take out $z - 5$.",
                                                      "جوڑوں میں گروہ بنا کر $z - 5$ باہر نکالیں۔", "expand((z - 5)*(z**2 + 1)) == z**3 - 5*z**2 + z - 5"),
                                                     (r"(z - 5)(z - i)(z + i) = 0", "$z^2 + 1 = (z - i)(z + i)$.", "$z^2 + 1 = (z - i)(z + i)$۔",
                                                      "expand((z - I)*(z + I)) == z**2 + 1")],
                        [C(5), C(0, 1), C(0, -1)], "z**3 - 5*z**2 + z - 5"),
       solve_by_factors("v", "4z^4 - 25z^2 - 21", [(r"4z^4 - 28z^2 + 3z^2 - 21 = 0 \Rightarrow (z^2 - 7)(4z^2 + 3) = 0",
                                                    "Split the middle term: $4 \\times (-21) = -84 = (-28)(3)$ and $-28 + 3 = -25$.",
                                                    "درمیانی رکن تقسیم کریں: $4 \\times (-21) = -84 = (-28)(3)$ اور $-28 + 3 = -25$۔",
                                                    "expand((z**2 - 7)*(4*z**2 + 3)) == 4*z**4 - 25*z**2 - 21"),
                                                   (r"z^2 = 7 \Rightarrow z = \pm\sqrt{7};\quad z^2 = -\tfrac{3}{4} \Rightarrow z = \pm\tfrac{\sqrt{3}}{2}i",
                                                    "Solve each factor: $\\sqrt{-\\frac{3}{4}} = \\frac{\\sqrt{3}}{2}i$.", "ہر جزو حل کریں۔", "(sqrt(3)/2*I)**2 == -R(3,4)")],
                        [C(sp.sqrt(7)), C(-sp.sqrt(7)), C(0, s3 / 2), C(0, -s3 / 2)], "4*z**4 - 25*z**2 - 21"),
       solve_by_factors("vi", "z^3 + z^2 + z + 1", [(r"z^2(z + 1) + 1(z + 1) = 0 \Rightarrow (z + 1)(z^2 + 1) = 0", "Group in pairs and take out $z + 1$.",
                                                     "جوڑوں میں گروہ بنا کر $z + 1$ باہر نکالیں۔", "expand((z + 1)*(z**2 + 1)) == z**3 + z**2 + z + 1"),
                                                    (r"(z + 1)(z - i)(z + i) = 0", "$z^2 + 1 = (z - i)(z + i)$.", "$z^2 + 1 = (z - i)(z + i)$۔",
                                                     "expand((z - I)*(z + I)) == z**2 + 1")],
                        [C(-1), C(0, 1), C(0, -1)], "z**3 + z**2 + z + 1")], "1.3")


def poly_from_zeros(n, base_tex, base_py, at, value, k):
    base = sp.sympify(base_py, locals={"z": Z})
    bval = base.subs(Z, at)
    poly = sp.expand(k * base)
    return P("", [
        S(rf"P(z) = k\,{base_tex}", f"A polynomial of degree {n} with these zeros has a factor $z - r$ for each zero $r$; $k$ is a constant to find.",
          f"ان صفروں والی درجہ {n} کی کثیر رقمی میں ہر صفر $r$ کے لیے جزو $z - r$ ہوتا ہے؛ $k$ ایک مستقل ہے۔"),
        S(rf"P(z) = k\left({sp.latex(sp.expand(base))}\right)", "Multiply out the factors.", "اجزاء کو ضرب دیں۔", f"expand({base_py}) == {sp.sstr(sp.expand(base))}"),
        S(rf"P({at}) = k\left({L(bval)}\right) = {value} \Rightarrow k = {L(k)}", f"Use the given value $P({at}) = {value}$.",
          f"دی گئی قیمت $P({at}) = {value}$ استعمال کریں۔", f"({sp.sstr(base)}).subs(z, {at})*({sp.sstr(k)}) == {value}"),
        S(rf"P(z) = {L(k)}\left({sp.latex(sp.expand(base))}\right) = {sp.latex(poly)}", "Put $k$ back and multiply out.", "$k$ واپس رکھ کر ضرب دیں۔",
          f"expand(({sp.sstr(k)})*({base_py})) == {sp.sstr(poly)}", f"({sp.sstr(poly)}).subs(z, {at}) == {value}")],
        f"$P(z) = {sp.latex(poly)}$")


ex("ex1.3", 6, "Find a polynomial $P(z)$ of degree 3 with zeros $3, -2i, 2i$ and satisfying $P(1) = 20$.", [
    poly_from_zeros(3, r"(z - 3)(z + 2i)(z - 2i) = k(z - 3)(z^2 + 4)", "(z - 3)*(z**2 + 4)", 1, 20, -2)], "1.3")
ex("ex1.3", 7, "Find a polynomial $P(z)$ of degree 4 with zeros $2i, -2i, 1, -1$ and satisfying $P(2) = 240$.", [
    poly_from_zeros(4, r"(z - 2i)(z + 2i)(z - 1)(z + 1) = k(z^2 + 4)(z^2 - 1)", "(z**2 + 4)*(z**2 - 1)", 2, 240, 10)], "1.3")
ex("ex1.3", 8, "Find a polynomial $P(z)$ of degree 4 with zeros $4, -4, 1+i, 1-i$ and satisfying $P(2) = 72$.", [
    poly_from_zeros(4, r"(z - 4)(z + 4)\left(z - (1 + i)\right)\left(z - (1 - i)\right) = k(z^2 - 16)(z^2 - 2z + 2)",
                    "(z**2 - 16)*(z**2 - 2*z + 2)", 2, 72, -3)], "1.3")
