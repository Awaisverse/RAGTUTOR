# Class 11, Unit 1 - Exercise 1.5 (run inside unit01.py)
import math as _m

from _c11 import ctex2 as ctex                     # parts that are sums of surds are grouped (this file only runs last)


def ans(z):
    return "$" + ctex(z) + "$"


def _approx(fx, fy):
    """x + iy to 2 decimals; a real result has no imaginary part shown."""
    if abs(fy) < 5e-3:
        return f"{fx:.2f}"
    return f"{fx:.2f} {'+' if fy >= 0 else '-'} {abs(fy):.2f}i"


def near(expr, value, k):
    """The sympy expression equals value to k decimal places."""
    return f"Abs(({expr}) - ({value})) <= {0.5 * 10 ** (-k) + 1e-9}"


PI = sp.pi


def ang_tex(t):
    """An angle in radians as LaTeX: \\frac{5\\pi}{4}."""
    return sp.latex(sp.nsimplify(t))


def cis_tex(r, t):
    rr = "" if r == 1 else L(r)
    a = ang_tex(t)
    return rf"{rr}\left(\cos {a} + i\sin {a}\right)" if not a.startswith("-") else rf"{rr}\left(\cos\left({a}\right) + i\sin\left({a}\right)\right)"


# ------------------------------------------------------------------------------------------ Q1: polar points

def polar_fig(r, deg):
    """Polar axes centred at (50, 30), a circle of radius |r|, the ray at the given angle (dashed when r < 0) and the point."""
    R_ = 22.0
    cx, cy = 50.0, 30.0
    t = _m.radians(deg)
    ux, uy = _m.cos(t), -_m.sin(t)                    # page y grows downwards
    s = 1 if r > 0 else -1
    px, py_ = cx + s * R_ * ux, cy + s * R_ * uy
    out = [{"t": "line", "p": [cx - 28, cy, cx + 28, cy], "arrow": True}, {"t": "line", "p": [cx, cy + 27, cx, cy - 27], "arrow": True},
           {"t": "circle", "c": [cx, cy], "r": R_}, {"t": "dot", "p": [cx, cy]}, {"t": "text", "p": [cx + 1.5, cy + 4], "s": "O"},
           {"t": "line", "p": [cx, cy, round(cx + 26 * ux, 2), round(cy + 26 * uy, 2)], "dash": r < 0, "arrow": r > 0},
           {"t": "arc", "c": [cx, cy], "r": 6, "a": [round(-deg, 2), 0] if deg >= 0 else [0, round(-deg, 2)]}]
    if r < 0:                                          # the point is on the opposite ray
        out.append({"t": "line", "p": [cx, cy, round(cx - 26 * ux, 2), round(cy - 26 * uy, 2)], "arrow": True})
    out += [{"t": "dot", "p": [round(px, 2), round(py_, 2)]},
            {"t": "text", "p": [round(px + (2 if px >= cx else -16), 2), round(py_ - 2, 2)], "s": f"({_fmt_r(r)}, {_fmt_deg(deg)})"}]
    return out


def _fmt_r(r):
    r = sp.nsimplify(r)
    return str(r) if r.is_Integer else f"{r.p}/{r.q}"


def _fmt_deg(d):
    return f"{d:g}°"


def polar_point(label, r, theta, deg, prompt):
    r = sp.nsimplify(r)
    steps = [S(rf"(r, \theta) = \left({L(r)}, {theta}\right) \quad (\theta = {deg:g}^\circ)", "Read the distance $r$ from the pole and the angle $\\theta$ from the initial line.",
               "قطب سے فاصلہ $r$ اور ابتدائی خط سے زاویہ $\\theta$ پڑھیں۔")]
    if r > 0:
        steps.append(S(rf"\text{{Turn }} {deg:g}^\circ \text{{ {'anticlockwise' if deg >= 0 else 'clockwise'}, then go }} {L(r)} \text{{ units along the ray}}",
                       "A positive $r$ is measured along the ray of the angle.", "مثبت $r$ زاویے کی شعاع کے ساتھ ناپا جاتا ہے۔", draw=polar_fig(float(r), deg)))
    else:
        d2 = deg + 180
        steps.append(S(rf"\left({L(r)}, {deg:g}^\circ\right) = \left({L(-r)}, {deg:g}^\circ + 180^\circ\right) = \left({L(-r)}, {d2:g}^\circ\right)",
                       "A negative $r$ means: go $|r|$ units in the OPPOSITE direction of the ray, i.e. add $180^\\circ$ to the angle.",
                       "منفی $r$ کا مطلب ہے: شعاع کی مخالف سمت میں $|r|$ اکائیاں جائیں، یعنی زاویے میں $180^\\circ$ جمع کریں۔", f"{deg} + 180 == {d2}"))
        steps.append(S(rf"\text{{Turn }} {deg:g}^\circ\text{{, then go }} {L(-r)} \text{{ units backwards through the pole}}", "Plot the point on the opposite ray.",
                       "نقطہ مخالف شعاع پر لگائیں۔", draw=polar_fig(float(r), deg)))
    x, y = float(r) * _m.cos(_m.radians(deg)), float(r) * _m.sin(_m.radians(deg))
    steps.append(S(rf"x = r\cos\theta \approx {x:.2f},\quad y = r\sin\theta \approx {y:.2f}", "In Cartesian coordinates the point is $(r\\cos\\theta, r\\sin\\theta)$.",
                   "کارتیسی محددات میں نقطہ $(r\\cos\\theta, r\\sin\\theta)$ ہے۔",
                   near(f"({sp.sstr(r)})*cos(({deg})*pi/180)", round(x, 2), 2), near(f"({sp.sstr(r)})*sin(({deg})*pi/180)", round(y, 2), 2)))
    return P(label, steps, f"plotted at $\\left({L(r)}, {theta}\\right)$, i.e. $({x:.2f}, {y:.2f})$", prompt=prompt)


Q1P = [("i", 2, r"75^\circ", 75), ("ii", -3, r"120^\circ", 120), ("iii", 2, r"\frac{\pi}{6}", 30), ("iv", 5, r"\frac{5\pi}{6}", 150),
       ("v", R(-5, 2), r"\frac{\pi}{3}", 60), ("vi", -3, r"-\frac{2\pi}{3}", -120), ("vii", R(-9, 2), r"-\frac{19\pi}{12}", -285),
       ("viii", R(-5, 2), r"\frac{5\pi}{12}", 75)]
ex("ex1.5", 1, "Plot the following points: (i) $(2, 75^\\circ)$ (ii) $(-3, 120^\\circ)$ (iii) $\\left(2, \\frac{\\pi}{6}\\right)$ (iv) $\\left(5, \\frac{5\\pi}{6}\\right)$ "
   "(v) $\\left(-\\frac{5}{2}, \\frac{\\pi}{3}\\right)$ (vi) $\\left(-3, -\\frac{2\\pi}{3}\\right)$ (vii) $\\left(-\\frac{9}{2}, -\\frac{19\\pi}{12}\\right)$ "
   "(viii) $\\left(-\\frac{5}{2}, \\frac{5\\pi}{12}\\right)$", [
       polar_point(l, r, th, d, f"$\\left({L(sp.nsimplify(r))}, {th}\\right)$") for l, r, th, d in Q1P], "1.5", figure_h=60)


# ------------------------------------------------------------------------------------------ Q2: polar form

def polar_form(label, prompt, pre, z, exact_angle=True):
    z = exact(z)
    x, y = sp.re(z), sp.im(z)
    r = sp.sqrt(x ** 2 + y ** 2)
    r = sp.nsimplify(r)
    t = sp.arg(z)                                      # principal argument
    q = quadrant_name(z)
    steps = list(pre)
    steps.append(S(rf"x = {L(x)},\ y = {L(y)}:\quad r = \sqrt{{x^2 + y^2}} = \sqrt{{{L(x ** 2 + y ** 2)}}} = {L(r)}", "Find the modulus $r$.", "مقیاس $r$ معلوم کریں۔",
                   f"sqrt(({py(x)})**2 + ({py(y)})**2) == {sp.sstr(r)}"))
    if exact_angle and sp.nsimplify(t / PI).is_Rational:
        t = sp.nsimplify(t)
        tt = t if t > -PI else t + 2 * PI
        ref = sp.atan(abs(y / x)) if x != 0 else PI / 2
        if x == 0:
            reason = rf"\text{{The point lies on the {'positive' if y > 0 else 'negative'} imaginary axis}} \Rightarrow \theta = {ang_tex(t)}"
        else:
            reason = rf"\text{{Quadrant {q}}},\ \tan^{{-1}}\left|\frac{{y}}{{x}}\right| = {ang_tex(ref)} \Rightarrow \theta = {ang_tex(t)}"
        steps.append(S(reason, (f"Find the angle from the quadrant of $(x, y)$ (here quadrant {q}) and the reference angle $\\tan^{{-1}}\\left|\\frac{{y}}{{x}}\\right|$."
                                if x != 0 else f"Here $x = 0$, so $\\frac{{y}}{{x}}$ is not defined: the point is on the imaginary axis, {'above' if y > 0 else 'below'} the origin, at an angle of ${ang_tex(t)}$."),
                       (f"زاویہ $(x, y)$ کے ربع (یہاں ربع {q}) اور حوالہ زاویہ $\\tan^{{-1}}\\left|\\frac{{y}}{{x}}\\right|$ سے معلوم کریں۔"
                        if x != 0 else f"یہاں $x = 0$ ہے، اس لیے $\\frac{{y}}{{x}}$ معین نہیں؛ نقطہ خیالی محور پر مبدا سے {'اوپر' if y > 0 else 'نیچے'} ہے، زاویہ ${ang_tex(t)}$۔"),
                       f"cos({sp.sstr(t)})*({sp.sstr(r)}) == {py(x)}", f"sin({sp.sstr(t)})*({sp.sstr(r)}) == {py(y)}"))
        ans_tex = cis_tex(r, t)
        extra = ""
        if t < 0:
            extra = rf" \quad \left(\text{{or }} {cis_tex(r, t + 2 * PI)}\right)"
        steps.append(S(rf"{ctex(z)} = {ans_tex}{extra}", "Write $r(\\cos\\theta + i\\sin\\theta)$.", "$r(\\cos\\theta + i\\sin\\theta)$ لکھیں۔"))
        return P(label, steps, f"${ans_tex}$", prompt=prompt)
    deg = float(sp.N(t * 180 / PI))
    ratio = sp.nsimplify(y / x)
    steps.append(S(rf"\theta = \tan^{{-1}}\left(\frac{{{L(y)}}}{{{L(x)}}}\right) = \tan^{{-1}}\left({L(ratio)}\right) \approx {deg:.2f}^\circ",
                   "The point is in quadrant I, so $\\theta = \\tan^{-1}\\frac{y}{x}$.", "نقطہ ربع I میں ہے، اس لیے $\\theta = \\tan^{-1}\\frac{y}{x}$۔",
                   near(f"atan({sp.sstr(ratio)})*180/pi", round(deg, 2), 2)))
    a = rf"\tan^{{-1}}{L(ratio)}"
    rr = "" if r == 1 else L(r)
    steps.append(S(rf"{ctex(z)} = {rr}\left(\cos\theta + i\sin\theta\right),\quad \theta = {a} \approx {deg:.2f}^\circ",
                   "Write the polar form.", "قطبی صورت لکھیں۔", f"({sp.sstr(r)})*cos(atan({sp.sstr(ratio)})) == {py(x)}"))
    return P(label, steps, rf"${rr}(\cos\theta + i\sin\theta),\ \theta = {a} \approx {deg:.2f}^\circ$", prompt=prompt)


def quadrant_name(z):
    x, y = sp.re(z), sp.im(z)
    if x > 0 and y >= 0:
        return "I"
    if x <= 0 and y > 0:
        return "II"
    if x < 0 and y <= 0:
        return "III"
    return "IV"


_d25, _v25 = div(C(1, -1), C(1, 1))
_d26, _v26 = div(C(s3, 1), C(1, s3))
_d27, _v27 = div(C(3, 4), C(4, 3))
p2iv = polar_form("iv", "$-\\frac{5}{2} - \\frac{5\\sqrt{3}}{2}i$", [], C(R(-5, 2), -5 * s3 / 2))
ex("ex1.5", 2, "Express the following complex numbers in polar form: (i) $4+3i$ (ii) $1+i$ (iii) $\\frac{1}{2} + \\frac{\\sqrt{3}}{2}i$ (iv) $-\\frac{5}{2} - \\frac{5\\sqrt{3}}{2}i$ "
   "(v) $\\frac{1-i}{1+i}$ (vi) $\\frac{\\sqrt{3}+i}{1+\\sqrt{3}i}$ (vii) $\\frac{3+4i}{4+3i}$", [
       polar_form("i", "$4+3i$", [], C(4, 3), exact_angle=False),
       polar_form("ii", "$1+i$", [], C(1, 1)),
       polar_form("iii", "$\\frac{1}{2} + \\frac{\\sqrt{3}}{2}i$", [], C(R(1, 2), s3 / 2)),
       note(p2iv, "The angle can be given as the principal argument $-\\frac{2\\pi}{3}$ or as $\\frac{4\\pi}{3}$ (the notes and a typed solution use $\\frac{4\\pi}{3}$); both describe the same number.",
            "زاویہ اصل دلیل $-\\frac{2\\pi}{3}$ یا $\\frac{4\\pi}{3}$ لکھا جا سکتا ہے؛ دونوں ایک ہی عدد بتاتے ہیں۔"),
       polar_form("v", "$\\frac{1-i}{1+i}$", [S(r"z = \frac{1 - i}{1 + i}", "First simplify the fraction.", "پہلے کسر کو سادہ کریں۔")] + _d25, _v25),
       polar_form("vi", "$\\frac{\\sqrt{3}+i}{1+\\sqrt{3}i}$", [S(r"z = \frac{\sqrt{3} + i}{1 + \sqrt{3}i}", "First simplify the fraction.", "پہلے کسر کو سادہ کریں۔")] + _d26, _v26),
       polar_form("vii", "$\\frac{3+4i}{4+3i}$", [S(r"z = \frac{3 + 4i}{4 + 3i}", "First simplify the fraction.", "پہلے کسر کو سادہ کریں۔")] + _d27, _v27, exact_angle=False)], "1.5")


# ------------------------------------------------------------------------------------------ Q3: rectangular form

def rect(label, prompt, r, t, ref_tex=None):
    """r cis t in x + iy form; t a rational multiple of pi."""
    r, t = sp.nsimplify(r), sp.nsimplify(t)
    c, s = sp.nsimplify(sp.cos(t)), sp.nsimplify(sp.sin(t))
    c, s = sp.radsimp(sp.cos(t).rewrite(sp.sqrt)), sp.radsimp(sp.sin(t).rewrite(sp.sqrt))
    z = exact(sp.expand(r * c + r * s * I))
    steps = [S(rf"z = {cis_tex(r, t)} = {L(r)}\cos {_w(t)} + i\,{L(r)}\sin {_w(t)}", "Expand: $x = r\\cos\\theta$, $y = r\\sin\\theta$.",
               "پھیلائیں: $x = r\\cos\\theta$، $y = r\\sin\\theta$۔")]
    if ref_tex:
        steps.append(S(ref_tex[0], ref_tex[1], ref_tex[2]))
    steps += [S(rf"\cos {_w(t)} = {L(c)},\quad \sin {_w(t)} = {L(s)}", "Find the exact values (use the reference angle and the signs in its quadrant).",
                "درست قیمتیں معلوم کریں (حوالہ زاویہ اور اس کے ربع کی علامتیں)۔", f"cos({sp.sstr(t)}) == {sp.sstr(c)}", f"sin({sp.sstr(t)}) == {sp.sstr(s)}"),
              S(rf"z = {L(r)}\left({L(c)}\right) + i\,{L(r)}\left({L(s)}\right) = {ctex(z)}", "Multiply by $r$.", "$r$ سے ضرب دیں۔",
                f"({sp.sstr(r)})*(cos({sp.sstr(t)}) + I*sin({sp.sstr(t)})) == {py(z)}")]
    return P(label, steps, ans(z), prompt=prompt), z


def _w(t):
    a = ang_tex(t)
    return rf"\left({a}\right)" if a.startswith("-") else a


q3 = [rect("i", "$4\\left(\\cos\\frac{5\\pi}{3} + i\\sin\\frac{5\\pi}{3}\\right)$", 4, 5 * PI / 3)[0],
      rect("ii", "$\\frac{3}{2}\\left(\\cos\\frac{7\\pi}{6} + i\\sin\\frac{7\\pi}{6}\\right)$", R(3, 2), 7 * PI / 6)[0],
      rect("iii", "$|z| = 7,\\ \\arg z = \\frac{23\\pi}{12}$", 7, 23 * PI / 12,
           (r"\frac{23\pi}{12} = 2\pi - \frac{\pi}{12},\quad \cos\frac{\pi}{12} = \frac{\sqrt{6} + \sqrt{2}}{4},\ \sin\frac{\pi}{12} = \frac{\sqrt{6} - \sqrt{2}}{4}",
            "$\\frac{23\\pi}{12}$ is in quadrant IV with reference angle $\\frac{\\pi}{12} = 15^\\circ$ ($\\cos 15^\\circ = \\cos(45^\\circ - 30^\\circ)$).",
            "$\\frac{23\\pi}{12}$ ربع IV میں ہے، حوالہ زاویہ $\\frac{\\pi}{12} = 15^\\circ$ ہے۔"))[0],
      rect("iv", "$|z| = 11,\\ \\arg z = -\\frac{11\\pi}{12}$", 11, -11 * PI / 12,
           (r"-\frac{11\pi}{12} = -\left(\pi - \frac{\pi}{12}\right):\ \text{quadrant III, reference angle } \frac{\pi}{12}",
            "Going $\\frac{11\\pi}{12}$ clockwise lands in quadrant III, $\\frac{\\pi}{12}$ from the negative real axis.",
            "گھڑی کی سمت $\\frac{11\\pi}{12}$ جانے سے ربع III آتا ہے۔"))[0],
      rect("v", "$|z| = \\frac{10}{3},\\ \\arg z = -\\frac{17\\pi}{12}$", R(10, 3), -17 * PI / 12,
           (r"-\frac{17\pi}{12} + 2\pi = \frac{7\pi}{12}:\ \text{quadrant II, reference angle } \frac{5\pi}{12}",
            "Add $2\\pi$ to get a positive angle in quadrant II.", "مثبت زاویہ لینے کے لیے $2\\pi$ جمع کریں؛ یہ ربع II میں ہے۔"))[0]]
p3vi = P("vi", [
    S(r"z = 2\cos(-33^\circ) + i\,2\sin(-33^\circ) = 2\cos 33^\circ - 2i\sin 33^\circ", "$\\cos(-\\theta) = \\cos\\theta$ and $\\sin(-\\theta) = -\\sin\\theta$.",
      "$\\cos(-\\theta) = \\cos\\theta$ اور $\\sin(-\\theta) = -\\sin\\theta$۔"),
    S(r"\cos 33^\circ \approx 0.8387,\quad \sin 33^\circ \approx 0.5446", "Use a calculator (degree mode).", "کیلکولیٹر استعمال کریں (ڈگری موڈ)۔",
      near("cos(33*pi/180)", 0.8387, 4), near("sin(33*pi/180)", 0.5446, 4)),
    S(r"z \approx 1.6773 - 1.0893i", "Multiply by 2.", "2 سے ضرب دیں۔", near("2*cos(33*pi/180)", 1.6773, 4), near("2*sin(33*pi/180)", 1.0893, 4))],
    "$2\\cos 33^\\circ - 2i\\sin 33^\\circ \\approx 1.6773 - 1.0893i$", prompt="$2\\cos(-33^\\circ) + i\\,2\\sin(-33^\\circ)$")
note(p3vi, "The notes write the angle as $-33$; it is $-33^\\circ$ (degrees), as in the typed solutions.", "نوٹس میں زاویہ $-33$ لکھا ہے؛ یہ $-33^\\circ$ (ڈگری) ہے۔")
ex("ex1.5", 3, "Express the following complex numbers in rectangular form: (i) $4\\left(\\cos\\frac{5\\pi}{3} + i\\sin\\frac{5\\pi}{3}\\right)$ "
   "(ii) $\\frac{3}{2}\\left(\\cos\\frac{7\\pi}{6} + i\\sin\\frac{7\\pi}{6}\\right)$ (iii) $|z| = 7$, $\\arg z = \\frac{23\\pi}{12}$ (iv) $|z| = 11$, $\\arg z = -\\frac{11\\pi}{12}$ "
   "(v) $|z| = \\frac{10}{3}$, $\\arg z = -\\frac{17\\pi}{12}$ (vi) $2\\cos(-33^\\circ) + i\\,2\\sin(-33^\\circ)$", q3 + [p3vi], "1.5")


# ------------------------------------------------------------------------------------------ Q4, Q5: operations in polar form

def ops(r1, t1, r2, t2, n1, n2):
    z1 = exact(sp.expand(r1 * sp.radsimp(sp.cos(t1).rewrite(sp.sqrt)) + r1 * sp.radsimp(sp.sin(t1).rewrite(sp.sqrt)) * I))
    z2 = exact(sp.expand(r2 * sp.radsimp(sp.cos(t2).rewrite(sp.sqrt)) + r2 * sp.radsimp(sp.sin(t2).rewrite(sp.sqrt)) * I))
    pre = S(rf"z_1 = {ctex(z1)},\quad z_2 = {ctex(z2)}", "Write both numbers in $x + iy$ form ($x = r\\cos\\theta$, $y = r\\sin\\theta$).",
            "دونوں اعداد کو $x + iy$ صورت میں لکھیں۔", f"{py(z1)} == {r1}*(cos({sp.sstr(t1)}) + I*sin({sp.sstr(t1)}))",
            f"{py(z2)} == {r2}*(cos({sp.sstr(t2)}) + I*sin({sp.sstr(t2)}))")
    out = []
    for lab, op in (("i", "+"), ("ii", "-")):
        v = exact(z1 + z2) if op == "+" else exact(z1 - z2)
        fx, fy = float(sp.re(v)), float(sp.im(v))
        out.append(P(lab, [pre, S(rf"z_1 {op} z_2 = {ctex(v)} \approx {_approx(fx, fy)}",
                                  "Add (subtract) the real parts and the imaginary parts.", "حقیقی اور خیالی حصوں کو جمع (تفریق) کریں۔",
                                  f"{py(z1)} {op} {py(z2)} == {py(v)}")], f"${ctex(v)} \\approx {_approx(fx, fy)}$",
                     prompt=f"$z_1 {op} z_2$"))
    for lab, op in (("iii", "*"), ("iv", "/")):
        rr = r1 * r2 if op == "*" else sp.Rational(r1, r2)
        tt = t1 + t2 if op == "*" else t1 - t2
        tt2 = tt - 2 * PI * sp.floor((tt + PI) / (2 * PI))       # reduce into (-pi, pi]
        if tt2 <= -PI:
            tt2 += 2 * PI
        v = exact(z1 * z2) if op == "*" else exact(sp.radsimp(z1 / z2))
        v = exact(sp.expand(rr * sp.radsimp(sp.cos(tt2).rewrite(sp.sqrt)) + rr * sp.radsimp(sp.sin(tt2).rewrite(sp.sqrt)) * I))
        fx, fy = float(sp.re(v)), float(sp.im(v))
        sym = r"z_1 z_2" if op == "*" else r"\frac{z_1}{z_2}"
        rule = ("Multiply the moduli and add the arguments." if op == "*" else "Divide the moduli and subtract the arguments.")
        out.append(P(lab, [
            S(rf"{sym} = {L(rr)}\left(\cos\left({ang_tex(t1)} {'+' if op == '*' else '-'} {ang_tex(t2)}\right) + i\sin\left({ang_tex(t1)} {'+' if op == '*' else '-'} {ang_tex(t2)}\right)\right) = {cis_tex(rr, tt)}",
              rule, "مقیاسوں کو ضرب دیں اور دلائل جمع کریں۔" if op == "*" else "مقیاسوں کو تقسیم کریں اور دلائل تفریق کریں۔"),
            S(rf"= {cis_tex(rr, tt2)}" if tt2 != tt else rf"= {cis_tex(rr, tt)}",
              "Take the angle into $(-\\pi, \\pi]$ by adding or subtracting $2\\pi$ (this does not change the number)." if tt2 != tt else "The angle is already in $(-\\pi, \\pi]$.",
              "$2\\pi$ جمع یا تفریق کر کے زاویہ $(-\\pi, \\pi]$ میں لائیں۔" if tt2 != tt else "زاویہ پہلے ہی $(-\\pi, \\pi]$ میں ہے۔",
              f"cos({sp.sstr(tt)}) == cos({sp.sstr(tt2)})"),
            S(rf"= {ctex(v)} \approx {_approx(fx, fy)}", "Use the exact values of $\\cos$ and $\\sin$ and multiply out.",
              "$\\cos$ اور $\\sin$ کی درست قیمتیں رکھ کر ضرب دیں۔", f"{py(z1)} {op} {py(z2)} == {py(v)}")],
            f"${ctex(v)} \\approx {_approx(fx, fy)}$", prompt=f"${sym}$"))
    return out


ex("ex1.5", 4, "If $z_1 = 9\\left(\\cos\\frac{5\\pi}{4} + i\\sin\\frac{5\\pi}{4}\\right)$ and $z_2 = 5\\left(\\cos\\frac{\\pi}{3} + i\\sin\\frac{\\pi}{3}\\right)$ then find "
   "(i) $z_1 + z_2$ (ii) $z_1 - z_2$ (iii) $z_1 z_2$ (iv) $\\frac{z_1}{z_2}$", ops(9, 5 * PI / 4, 5, PI / 3, 9, 5), "1.5")
ex("ex1.5", 5, "If $z_1 = 7\\left(\\cos\\frac{23\\pi}{12} + i\\sin\\frac{23\\pi}{12}\\right)$ and $z_2 = 11\\left(\\cos\\frac{11\\pi}{12} + i\\sin\\frac{11\\pi}{12}\\right)$, "
   "find the following and express in $x + iy$ form: (i) $z_1 + z_2$ (ii) $z_1 - z_2$ (iii) $z_1 z_2$ (iv) $\\frac{z_1}{z_2}$", ops(7, 23 * PI / 12, 11, 11 * PI / 12, 7, 11), "1.5")
ex("ex1.5", 6, "If $z_1$ and $z_2$ are two complex numbers, show that (i) $\\operatorname{Arg}(z_1 z_2) = \\operatorname{Arg} z_1 + \\operatorname{Arg} z_2$ "
   "(ii) $\\operatorname{Arg}\\left(\\frac{z_1}{z_2}\\right) = \\operatorname{Arg} z_1 - \\operatorname{Arg} z_2$", [
       P("i", [S(r"z_1 = r_1(\cos\theta_1 + i\sin\theta_1),\quad z_2 = r_2(\cos\theta_2 + i\sin\theta_2)", "Write both numbers in polar form; $\\theta_1 = \\operatorname{Arg} z_1$, $\\theta_2 = \\operatorname{Arg} z_2$.",
                 "دونوں اعداد قطبی صورت میں لکھیں؛ $\\theta_1 = \\operatorname{Arg} z_1$، $\\theta_2 = \\operatorname{Arg} z_2$۔"),
               S(r"z_1 z_2 = r_1 r_2\left[(\cos\theta_1\cos\theta_2 - \sin\theta_1\sin\theta_2) + i(\sin\theta_1\cos\theta_2 + \cos\theta_1\sin\theta_2)\right]",
                 "Multiply out with $i^2 = -1$.", "$i^2 = -1$ کے ساتھ ضرب دیں۔",
                 "expand((cos(p) + I*sin(p))*(cos(q) + I*sin(q))) == expand((cos(p)*cos(q) - sin(p)*sin(q)) + I*(sin(p)*cos(q) + cos(p)*sin(q)))"),
               S(r"= r_1 r_2\left[\cos(\theta_1 + \theta_2) + i\sin(\theta_1 + \theta_2)\right]", "Use the addition formulas for $\\cos$ and $\\sin$.",
                 "$\\cos$ اور $\\sin$ کے جمع کے کلیے استعمال کریں۔", "cos(p)*cos(q) - sin(p)*sin(q) == cos(p + q)", "sin(p)*cos(q) + cos(p)*sin(q) == sin(p + q)"),
               S(r"\therefore\ \operatorname{Arg}(z_1 z_2) = \theta_1 + \theta_2 = \operatorname{Arg} z_1 + \operatorname{Arg} z_2", "The argument of the product is the sum of the arguments (up to a multiple of $2\\pi$).",
                 "حاصل ضرب کی دلیل دلائل کا مجموعہ ہے ($2\\pi$ کے مضرب تک)۔")], "proved: $z_1 z_2 = r_1 r_2 \\operatorname{cis}(\\theta_1 + \\theta_2)$",
         prompt="$\\operatorname{Arg}(z_1 z_2) = \\operatorname{Arg} z_1 + \\operatorname{Arg} z_2$"),
       P("ii", [S(r"\frac{z_1}{z_2} = \frac{r_1(\cos\theta_1 + i\sin\theta_1)}{r_2(\cos\theta_2 + i\sin\theta_2)} \times \frac{\cos\theta_2 - i\sin\theta_2}{\cos\theta_2 - i\sin\theta_2}",
                  "Multiply by the conjugate of the denominator.", "نسب نما کے مزدوج سے ضرب دیں۔"),
                S(r"= \frac{r_1}{r_2}\cdot\frac{(\cos\theta_1\cos\theta_2 + \sin\theta_1\sin\theta_2) + i(\sin\theta_1\cos\theta_2 - \cos\theta_1\sin\theta_2)}{\cos^2\theta_2 + \sin^2\theta_2}",
                  "Multiply out; the denominator is $\\cos^2\\theta_2 + \\sin^2\\theta_2 = 1$.", "ضرب دیں؛ نسب نما $\\cos^2\\theta_2 + \\sin^2\\theta_2 = 1$ ہے۔",
                  "expand((cos(p) + I*sin(p))*(cos(q) - I*sin(q))) == expand((cos(p)*cos(q) + sin(p)*sin(q)) + I*(sin(p)*cos(q) - cos(p)*sin(q)))"),
                S(r"= \frac{r_1}{r_2}\left[\cos(\theta_1 - \theta_2) + i\sin(\theta_1 - \theta_2)\right]", "Use the subtraction formulas.", "تفریق کے کلیے استعمال کریں۔",
                  "cos(p)*cos(q) + sin(p)*sin(q) == cos(p - q)", "sin(p)*cos(q) - cos(p)*sin(q) == sin(p - q)"),
                S(r"\therefore\ \operatorname{Arg}\left(\frac{z_1}{z_2}\right) = \theta_1 - \theta_2 = \operatorname{Arg} z_1 - \operatorname{Arg} z_2", "The argument of a quotient is the difference of the arguments (up to $2\\pi$).",
                  "حاصل قسمت کی دلیل دلائل کا فرق ہے ($2\\pi$ تک)۔")], "proved: $\\frac{z_1}{z_2} = \\frac{r_1}{r_2}\\operatorname{cis}(\\theta_1 - \\theta_2)$",
         prompt="$\\operatorname{Arg}\\left(\\frac{z_1}{z_2}\\right) = \\operatorname{Arg} z_1 - \\operatorname{Arg} z_2$")], "1.5")

ex("ex1.5", 7, "Divide $z_1 = 6(\\cos 150^\\circ + i\\sin 150^\\circ)$ by $z_2 = 3(\\cos 30^\\circ + i\\sin 30^\\circ)$ and express the result in $x + iy$ form.", [P("", [
    S(r"\frac{z_1}{z_2} = \frac{6}{3}\left[\cos(150^\circ - 30^\circ) + i\sin(150^\circ - 30^\circ)\right] = 2(\cos 120^\circ + i\sin 120^\circ)",
      "Divide the moduli and subtract the arguments.", "مقیاسوں کو تقسیم کریں اور دلائل تفریق کریں۔"),
    S(r"\cos 120^\circ = -\frac{1}{2},\quad \sin 120^\circ = \frac{\sqrt{3}}{2}", "Exact values in quadrant II.", "ربع II میں درست قیمتیں۔",
      "cos(120*pi/180) == -R(1,2)", "sin(120*pi/180) == sqrt(3)/2"),
    S(r"\frac{z_1}{z_2} = 2\left(-\frac{1}{2} + \frac{\sqrt{3}}{2}i\right) = -1 + \sqrt{3}i", "Multiply by 2.", "2 سے ضرب دیں۔",
      "6*(cos(150*pi/180) + I*sin(150*pi/180))/(3*(cos(30*pi/180) + I*sin(30*pi/180))) == -1 + sqrt(3)*I")], "$-1 + \\sqrt{3}i$")], "1.5")

ex("ex1.5", 8, "Multiply $z_1 = 2(\\cos 60^\\circ + i\\sin 60^\\circ)$ and $z_2 = 5(\\cos 90^\\circ + i\\sin 90^\\circ)$ and express the result in $x + iy$ form.", [P("", [
    S(r"z_1 z_2 = (2)(5)\left[\cos(60^\circ + 90^\circ) + i\sin(60^\circ + 90^\circ)\right] = 10(\cos 150^\circ + i\sin 150^\circ)",
      "Multiply the moduli and add the arguments.", "مقیاسوں کو ضرب دیں اور دلائل جمع کریں۔"),
    S(r"\cos 150^\circ = -\frac{\sqrt{3}}{2},\quad \sin 150^\circ = \frac{1}{2}", "Exact values in quadrant II.", "ربع II میں درست قیمتیں۔",
      "cos(150*pi/180) == -sqrt(3)/2", "sin(150*pi/180) == R(1,2)"),
    S(r"z_1 z_2 = 10\left(-\frac{\sqrt{3}}{2} + \frac{1}{2}i\right) = -5\sqrt{3} + 5i", "Multiply by 10.", "10 سے ضرب دیں۔",
      "2*(cos(60*pi/180) + I*sin(60*pi/180))*5*(cos(90*pi/180) + I*sin(90*pi/180)) == -5*sqrt(3) + 5*I")], "$-5\\sqrt{3} + 5i$")], "1.5")

ex("ex1.5", 9, "Find the modulus and argument of $z = -2 - 2i$.", [P("", [
    S(r"|z| = \sqrt{(-2)^2 + (-2)^2} = \sqrt{8} = 2\sqrt{2}", "Modulus.", "مقیاس۔", "Abs(-2 - 2*I) == 2*sqrt(2)"),
    S(r"\text{Quadrant III},\ \tan^{-1}\left|\frac{-2}{-2}\right| = \frac{\pi}{4}", "Both parts are negative: the point is in quadrant III; the reference angle is $\\frac{\\pi}{4}$.",
      "دونوں حصے منفی ہیں: نقطہ ربع III میں ہے؛ حوالہ زاویہ $\\frac{\\pi}{4}$ ہے۔"),
    S(r"\arg z = -\pi + \frac{\pi}{4} = -\frac{3\pi}{4} \quad (\text{or } \pi + \tfrac{\pi}{4} = \tfrac{5\pi}{4})", "In quadrant III the principal argument is $-\\pi + $ (reference angle).",
      "ربع III میں اصل دلیل $-\\pi +$ (حوالہ زاویہ) ہے۔", "arg(-2 - 2*I) == -3*pi/4")], "$|z| = 2\\sqrt{2},\\ \\arg z = -\\frac{3\\pi}{4}$ (or $\\frac{5\\pi}{4}$)")], "1.5")


# ------------------------------------------------------------------------------------------ Q10-Q17: arguments and loci

ex("ex1.5", 10, "Write the equation $\\arg(\\bar{z} - 2 + i) = \\frac{2\\pi}{3}$ in Cartesian form, if $z = x + iy$.", [P("", [
    S(r"\bar{z} - 2 + i = (x - iy) - 2 + i = (x - 2) + i(1 - y)", "Put $\\bar z = x - iy$ and collect real and imaginary parts.",
      "$\\bar z = x - iy$ رکھیں اور حقیقی اور خیالی حصے اکٹھے کریں۔", "expand((x - I*y) - 2 + I) == (x - 2) + I*(1 - y)"),
    S(r"\tan\frac{2\pi}{3} = \frac{1 - y}{x - 2} \Rightarrow -\sqrt{3} = \frac{1 - y}{x - 2}", "The argument $\\theta$ of $X + iY$ satisfies $\\tan\\theta = \\frac{Y}{X}$; $\\tan\\frac{2\\pi}{3} = -\\sqrt{3}$.",
      "$X + iY$ کی دلیل $\\theta$ کے لیے $\\tan\\theta = \\frac{Y}{X}$؛ $\\tan\\frac{2\\pi}{3} = -\\sqrt{3}$۔", "tan(2*pi/3) == -sqrt(3)"),
    S(r"1 - y = -\sqrt{3}(x - 2) \Rightarrow y = \sqrt{3}x + 1 - 2\sqrt{3}", "Cross-multiply and make $y$ the subject.", "طرفین ضرب کر کے $y$ کو موضوع بنائیں۔",
      "expand(1 - (sqrt(3)*x + 1 - 2*sqrt(3))) == expand(-sqrt(3)*(x - 2))"),
    S(r"\text{with } x - 2 < 0,\ 1 - y > 0 \ (\text{the angle } \tfrac{2\pi}{3} \text{ is in quadrant II})", "Only the part of the line where the real part is negative and the imaginary part positive (a ray) has argument $\\frac{2\\pi}{3}$.",
      "صرف وہ حصہ جہاں حقیقی حصہ منفی اور خیالی حصہ مثبت ہو (ایک شعاع) کی دلیل $\\frac{2\\pi}{3}$ ہے۔", "arg((0 - 2) + I*(1 - (sqrt(3)*0 + 1 - 2*sqrt(3)))) == 2*pi/3")],
    "$y = \\sqrt{3}x + 1 - 2\\sqrt{3}$ (with $x < 2$)")], "1.5")

ex("ex1.5", 11, "If $z = x + iy$ and $\\arg\\left(\\frac{\\bar{z} - 1 + 2i}{\\bar{z} + 1 - 2i}\\right) = \\frac{9\\pi}{4}$, show that $x^2 + y^2 - 4x + 2y - 5 = 0$.", [P("", [
    S(r"\bar{z} - 1 + 2i = (x - 1) + i(2 - y),\quad \bar{z} + 1 - 2i = (x + 1) - i(y + 2)", "Put $\\bar z = x - iy$.", "$\\bar z = x - iy$ رکھیں۔"),
    S(r"\frac{(x - 1) + i(2 - y)}{(x + 1) - i(y + 2)} \times \frac{(x + 1) + i(y + 2)}{(x + 1) + i(y + 2)}", "Multiply by the conjugate of the denominator.", "نسب نما کے مزدوج سے ضرب دیں۔"),
    S(r"= \frac{(x^2 + y^2 - 5) + i(4x - 2y)}{(x + 1)^2 + (y + 2)^2}", "Multiply out the numerator: real part $(x-1)(x+1) - (2-y)(y+2)$, imaginary part $(x-1)(y+2) + (2-y)(x+1)$.",
      "شمار کنندہ ضرب دیں۔", "expand(((x - 1) + I*(2 - y))*((x + 1) + I*(y + 2))) == expand((x**2 + y**2 - 5) + I*(4*x - 2*y))"),
    S(r"\frac{9\pi}{4} = 2\pi + \frac{\pi}{4} \Rightarrow \tan\frac{\pi}{4} = 1 = \frac{4x - 2y}{x^2 + y^2 - 5}", "An argument of $\\frac{9\\pi}{4}$ is the same direction as $\\frac{\\pi}{4}$, where imaginary part = real part.",
      "$\\frac{9\\pi}{4}$ کی دلیل $\\frac{\\pi}{4}$ والی سمت ہے، جہاں خیالی حصہ = حقیقی حصہ۔", "tan(9*pi/4) == 1"),
    S(r"x^2 + y^2 - 5 = 4x - 2y \Rightarrow x^2 + y^2 - 4x + 2y - 5 = 0", "Rearrange.", "ترتیب دیں۔")], "proved: $x^2 + y^2 - 4x + 2y - 5 = 0$")], "1.5")

ex("ex1.5", 12, "If $z = x + iy$ and $\\arg(z - 2 - 3i) - \\arg(z + 2 + 3i) = 2\\pi$, show that $2y = 3x$.", [P("", [
    S(r"z - 2 - 3i = (x - 2) + i(y - 3),\quad z + 2 + 3i = (x + 2) + i(y + 3)", "Write both numbers in $x + iy$ form.", "دونوں اعداد $x + iy$ صورت میں لکھیں۔"),
    S(r"\arg(z - 2 - 3i) = \arg(z + 2 + 3i) + 2\pi \Rightarrow \tan\left[\arg(z - 2 - 3i)\right] = \tan\left[\arg(z + 2 + 3i)\right]", "Angles that differ by $2\\pi$ have the same tangent.",
      "جن زاویوں میں $2\\pi$ کا فرق ہو ان کا $\\tan$ برابر ہوتا ہے۔"),
    S(r"\frac{y - 3}{x - 2} = \frac{y + 3}{x + 2}", "$\\tan(\\arg(X + iY)) = \\frac{Y}{X}$.", "$\\tan(\\arg(X + iY)) = \\frac{Y}{X}$۔"),
    S(r"(y - 3)(x + 2) = (y + 3)(x - 2) \Rightarrow xy + 2y - 3x - 6 = xy - 2y + 3x - 6", "Cross-multiply and expand.", "طرفین ضرب کر کے پھیلائیں۔",
      "expand((y - 3)*(x + 2)) == x*y + 2*y - 3*x - 6", "expand((y + 3)*(x - 2)) == x*y - 2*y + 3*x - 6"),
    S(r"4y = 6x \Rightarrow 2y = 3x", "Cancel $xy$ and $-6$ and simplify.", "$xy$ اور $-6$ کاٹ کر سادہ کریں۔")], "proved: $2y = 3x$")], "1.5")


def locus(eid, n, question, rows, answer):
    ex(eid, n, question, [P("", [S(m, en, ur, *c) for m, en, ur, c in rows], answer)], "1.5")


locus("ex1.5", 13, "Solve $|z - 2i| = |\\bar{z} + 2|$ for $z = x + iy$ (find the set of points).", [
    (r"|x + i(y - 2)| = |(x + 2) - iy|", "Put $z = x + iy$ and $\\bar z = x - iy$.", "$z = x + iy$ اور $\\bar z = x - iy$ رکھیں۔", []),
    (r"x^2 + (y - 2)^2 = (x + 2)^2 + y^2", "Square both moduli: $|X + iY|^2 = X^2 + Y^2$.", "دونوں مقیاسوں کا مربع لیں۔", []),
    (r"x^2 + y^2 - 4y + 4 = x^2 + 4x + 4 + y^2 \Rightarrow -4y = 4x", "Expand and cancel $x^2$, $y^2$ and $4$.", "پھیلائیں اور $x^2$، $y^2$ اور $4$ کاٹیں۔",
     ["expand(x**2 + (y - 2)**2 - ((x + 2)**2 + y**2)) == -4*y - 4*x"]),
    (r"y = -x", "The set of points is the straight line $y = -x$ (check: $z = 1 - i$ satisfies it).", "نقاط کا سیٹ خط مستقیم $y = -x$ ہے۔",
     ["Abs((1 - I) - 2*I) == Abs(conjugate(1 - I) + 2)"])], "$y = -x$")

locus("ex1.5", 14, "For $z = x + iy$, solve $|5z + 4 + i| = |5\\bar{z} - 3 + 2i|$ (find the set of points).", [
    (r"|(5x + 4) + i(5y + 1)| = |(5x - 3) + i(2 - 5y)|", "Put $z = x + iy$, $\\bar z = x - iy$ and collect parts.", "$z$ اور $\\bar z$ رکھ کر حصے اکٹھے کریں۔", []),
    (r"(5x + 4)^2 + (5y + 1)^2 = (5x - 3)^2 + (2 - 5y)^2", "Square both moduli.", "دونوں مقیاسوں کا مربع لیں۔", []),
    (r"40x + 10y + 17 = -30x - 20y + 13", "Expand; $25x^2$ and $25y^2$ cancel.", "پھیلائیں؛ $25x^2$ اور $25y^2$ کٹ جاتے ہیں۔",
     ["expand((5*x + 4)**2 + (5*y + 1)**2 - (5*x - 3)**2 - (2 - 5*y)**2) == 70*x + 30*y + 4"]),
    (r"70x + 30y + 4 = 0 \Rightarrow 35x + 15y + 2 = 0 \Rightarrow y = -\frac{7}{3}x - \frac{2}{15}", "Collect terms and simplify: a straight line.",
     "ارکان اکٹھے کر کے سادہ کریں: ایک خط مستقیم۔", ["expand(35*x + 15*(-R(7,3)*x - R(2,15)) + 2) == 0"])], "$35x + 15y + 2 = 0$, i.e. $y = -\\frac{7}{3}x - \\frac{2}{15}$")

locus("ex1.5", 15, "Determine the set of points $z = x + iy$ that satisfy the equation $|3\\bar{z} - 2 + i| = |3z + i|$.", [
    (r"|(3x - 2) + i(1 - 3y)| = |3x + i(3y + 1)|", "Put $\\bar z = x - iy$ and $z = x + iy$.", "$\\bar z$ اور $z$ رکھیں۔", []),
    (r"(3x - 2)^2 + (1 - 3y)^2 = 9x^2 + (3y + 1)^2", "Square both moduli.", "دونوں مقیاسوں کا مربع لیں۔", []),
    (r"-12x + 4 - 6y = 6y \Rightarrow -12x - 12y + 4 = 0", "Expand and cancel $9x^2$, $9y^2$ and $1$.", "پھیلائیں اور برابر ارکان کاٹیں۔",
     ["expand((3*x - 2)**2 + (1 - 3*y)**2 - 9*x**2 - (3*y + 1)**2) == -12*x - 12*y + 4"]),
    (r"x + y = \frac{1}{3} \Rightarrow y = -x + \frac{1}{3}", "Divide by $-12$: the set is a straight line.", "$-12$ سے تقسیم کریں: سیٹ ایک خط مستقیم ہے۔", [])],
    "$3x + 3y - 1 = 0$, i.e. $y = -x + \\frac{1}{3}$")

locus("ex1.5", 16, "If $z = x + iy$ and $w = \\frac{1 - iz}{z - i}$, show that $|w| = 1 \\Rightarrow z$ is real.", [
    (r"|w| = 1 \Rightarrow |1 - iz| = |z - i|", "The modulus of a quotient is the quotient of the moduli.", "حاصل قسمت کا مقیاس، مقیاسوں کا حاصل قسمت ہے۔", []),
    (r"1 - iz = 1 - i(x + iy) = (1 + y) - ix,\quad z - i = x + i(y - 1)", "Put $z = x + iy$.", "$z = x + iy$ رکھیں۔",
     ["expand(1 - I*(x + I*y)) == (1 + y) - I*x"]),
    (r"(1 + y)^2 + x^2 = x^2 + (y - 1)^2", "Square both moduli.", "دونوں مقیاسوں کا مربع لیں۔", []),
    (r"1 + 2y + y^2 = y^2 - 2y + 1 \Rightarrow 4y = 0 \Rightarrow y = 0", "Expand and cancel.", "پھیلائیں اور کاٹیں۔",
     ["expand((1 + y)**2 + x**2 - x**2 - (y - 1)**2) == 4*y"]),
    (r"z = x + 0i = x \text{ is real}", "The imaginary part is zero.", "خیالی حصہ صفر ہے۔", [])], "proved: $y = 0$, so $z$ is real")

locus("ex1.5", 17, "If $z_1 \\ne z_2$ and $|z_2| = 1$, find $\\left|\\frac{z_2 - z_1}{1 - \\bar{z}_1 z_2}\\right|$.", [
    (r"|z_2| = 1 \Rightarrow z_2 \bar{z}_2 = |z_2|^2 = 1", "Use $z\\bar z = |z|^2$.", "$z\\bar z = |z|^2$ استعمال کریں۔", []),
    (r"1 - \bar{z}_1 z_2 = z_2\bar{z}_2 - \bar{z}_1 z_2 = z_2\left(\bar{z}_2 - \bar{z}_1\right)", "Replace 1 by $z_2\\bar z_2$ and take $z_2$ common.",
     "1 کی جگہ $z_2\\bar z_2$ رکھیں اور $z_2$ مشترک لیں۔", []),
    (r"|1 - \bar{z}_1 z_2| = |z_2|\,\left|\overline{z_2 - z_1}\right| = 1 \cdot |z_2 - z_1|", "$|z_2| = 1$ and a number and its conjugate have the same modulus.",
     "$|z_2| = 1$ اور عدد اور اس کے مزدوج کا مقیاس برابر ہوتا ہے۔", []),
    (r"\left|\frac{z_2 - z_1}{1 - \bar{z}_1 z_2}\right| = \frac{|z_2 - z_1|}{|z_2 - z_1|} = 1", "Divide ($z_1 \\ne z_2$, so the denominator is not zero). Check with $z_2 = i$, $z_1 = 2$.",
     "تقسیم کریں ($z_1 \\ne z_2$)۔ جانچ: $z_2 = i$، $z_1 = 2$۔", ["Abs((I - 2)/(1 - conjugate(2)*I)) == 1", "Abs((I - (3 + 4*I))/(1 - (3 - 4*I)*I)) == 1"])], "$1$")


# ------------------------------------------------------------------------------------------ Q18-Q22: applications

ex("ex1.5", 18, "An AC source supplies a voltage of $V = 120\\left(\\cos\\frac{\\pi}{4} + i\\sin\\frac{\\pi}{4}\\right)$ volts to a circuit with impedance "
   "$Z = \\frac{1 + i\\sqrt{3}}{2}$ ohms. Calculate the current in polar form.", [P("", [
    S(r"V = IZ \Rightarrow I = \frac{V}{Z}", "Ohm's law for AC circuits: the impedance $Z$ plays the part of the resistance.", "AC سرکٹ میں اوہم کا قانون: رکاوٹ $Z$ مزاحمت کا کام کرتی ہے۔"),
    S(r"Z = \frac{1}{2} + \frac{\sqrt{3}}{2}i:\quad |Z| = \sqrt{\tfrac{1}{4} + \tfrac{3}{4}} = 1,\quad \theta = \tan^{-1}\sqrt{3} = \frac{\pi}{3}", "Write $Z$ in polar form.",
      "$Z$ کو قطبی صورت میں لکھیں۔", "Abs(R(1,2) + sqrt(3)/2*I) == 1", "arg(R(1,2) + sqrt(3)/2*I) == pi/3"),
    S(r"I = \frac{120\left(\cos\frac{\pi}{4} + i\sin\frac{\pi}{4}\right)}{1\left(\cos\frac{\pi}{3} + i\sin\frac{\pi}{3}\right)} = 120\left[\cos\left(\frac{\pi}{4} - \frac{\pi}{3}\right) + i\sin\left(\frac{\pi}{4} - \frac{\pi}{3}\right)\right]",
      "Divide the moduli and subtract the arguments.", "مقیاسوں کو تقسیم کریں اور دلائل تفریق کریں۔"),
    S(r"I = 120\left[\cos\left(-\frac{\pi}{12}\right) + i\sin\left(-\frac{\pi}{12}\right)\right] \approx 115.91 - 31.06i \ \text{A}", "$\\frac{\\pi}{4} - \\frac{\\pi}{3} = -\\frac{\\pi}{12}$.",
      "$\\frac{\\pi}{4} - \\frac{\\pi}{3} = -\\frac{\\pi}{12}$۔", "120*(cos(pi/4) + I*sin(pi/4))/(R(1,2) + sqrt(3)/2*I) == 120*(cos(-pi/12) + I*sin(-pi/12))",
      near("120*cos(pi/12)", 115.91, 2))], "$I = 120\\left[\\cos\\left(-\\frac{\\pi}{12}\\right) + i\\sin\\left(-\\frac{\\pi}{12}\\right)\\right]$ A")], "1.5")

_d19, _v19 = div(C(90, 30), C(3, -6))
ex("ex1.5", 19, "An AC circuit has an impedance of $Z = 3 - 6i$ ohms and is connected to a voltage source of $V = 90 + 30i$ volts. Find the current in both "
   "rectangular and polar form.", [P("", [S(r"I = \frac{V}{Z} = \frac{90 + 30i}{3 - 6i}", "Ohm's law: $I = \\frac{V}{Z}$.", "اوہم کا قانون: $I = \\frac{V}{Z}$۔")] + _d19 + [
    S(r"|I| = \sqrt{2^2 + 14^2} = \sqrt{200} = 10\sqrt{2},\quad \theta = \tan^{-1}\frac{14}{2} = \tan^{-1}7 \approx 81.87^\circ", "Polar form: modulus and argument (quadrant I).",
      "قطبی صورت: مقیاس اور دلیل (ربع I)۔", "Abs(2 + 14*I) == 10*sqrt(2)", near("atan(7)*180/pi", 81.87, 2)),
    S(r"I = 2 + 14i = 10\sqrt{2}\left(\cos\theta + i\sin\theta\right),\ \theta = \tan^{-1}7 \approx 81.87^\circ \ \text{A}", "Both forms of the current.", "کرنٹ کی دونوں صورتیں۔")],
    "$I = 2 + 14i$ A $= 10\\sqrt{2}(\\cos\\theta + i\\sin\\theta)$, $\\theta = \\tan^{-1}7 \\approx 81.87^\\circ$")], "1.5")

LETTERS = {ch: k + 1 for k, ch in enumerate("ABCDEFGHIJKLMNOPQRSTUVWXYZ")}


def cipher(word, key, mode):
    k = exact(key)
    rows = []
    enc = []
    for ch in word:
        n = LETTERS[ch]
        e = exact(n * k) if mode == "*" else exact(n + k)
        enc.append(e)
        rows.append(rf"{ch} = {n}: & {ctex(e)}")
    steps = [S(r"A = 1,\ B = 2,\ \dots,\ Z = 26", "Change each letter to its position in the alphabet.", "ہر حرف کو حروفِ تہجی میں اس کے نمبر سے بدلیں۔"),
             S(r"\begin{array}{ll}" + r" \\ ".join(rows) + r"\end{array}",
               f"Encrypt: {'multiply' if mode == '*' else 'add'} each number {'by' if mode == '*' else 'to'} the key $k = {ctex(k)}$.",
               f"خفیہ بنائیں: ہر عدد کو کلید $k = {ctex(k)}$ سے {'ضرب دیں' if mode == '*' else 'جمع کریں'}۔",
               *[f"{LETTERS[ch]}*{py(k)} == {py(e)}" if mode == "*" else f"{LETTERS[ch]} + {py(k)} == {py(e)}" for ch, e in zip(word, enc)])]
    if mode == "*":
        inv = exact(1 / k)
        steps.append(S(rf"k^{{-1}} = \frac{{1}}{{{ctex(k)}}} = \frac{{{ctex(sp.conjugate(k))}}}{{{L(sp.re(k) ** 2 + sp.im(k) ** 2)}}} = {ctex(inv)}",
                       "To decrypt, multiply by the inverse of the key.", "کھولنے کے لیے کلید کے معکوس سے ضرب دیں۔", f"{py(k)}*{py(inv)} == 1"))
        e0, n0 = enc[0], LETTERS[word[0]]
        prod = sp.expand(e0 * sp.conjugate(k))
        steps.append(S(rf"\left({ctex(e0)}\right) \times \frac{{{ctex(sp.conjugate(k))}}}{{{L(sp.re(k) ** 2 + sp.im(k) ** 2)}}} = \frac{{{ctex(prod)}}}{{{L(sp.re(k) ** 2 + sp.im(k) ** 2)}}} = {n0} \to {word[0]}",
                       f"Work out the first one in full: multiply out the brackets with $i^2 = -1$; the imaginary parts cancel and {n0} is {word[0]}.",
                       f"پہلا مکمل حل کریں: قوسین ضرب دیں ($i^2 = -1$)؛ خیالی حصے کٹ جاتے ہیں اور {n0} حرف {word[0]} ہے۔",
                       f"expand({py(e0)}*{py(sp.conjugate(k))}) == {py(prod)}"))
        steps.append(S(r"\begin{array}{ll}" + r" \\ ".join(rf"\left({ctex(e)}\right) \times k^{{-1}} = {LETTERS[ch]} & \to {ch}" for ch, e in zip(word, enc)) + r"\end{array}",
                       "The same for every letter: each product gives back the letter's number.", "ہر حرف کے لیے یہی: ہر حاصل ضرب حرف کا نمبر واپس دیتا ہے۔",
                       *[f"{py(e)}*{py(inv)} == {LETTERS[ch]}" for ch, e in zip(word, enc)]))
    else:
        steps.append(S(r"\begin{array}{ll}" + r" \\ ".join(rf"{ctex(e)} - ({ctex(k)}) = {LETTERS[ch]} & \to {ch}" for ch, e in zip(word, enc)) + r"\end{array}",
                       "To decrypt, subtract the key from each number.", "کھولنے کے لیے ہر عدد سے کلید تفریق کریں۔",
                       *[f"{py(e)} - {py(k)} == {LETTERS[ch]}" for ch, e in zip(word, enc)]))
    return P("", steps, "encrypted: $" + ",\\ ".join(ctex(e) for e in enc) + f"$; decrypted: {word}")


ex("ex1.5", 20, "Encrypt the word \"CODE\" by multiplying by the complex encryption key $k = 2 - i$. Then decrypt it back to the original word.", [cipher("CODE", C(2, -1), "*")], "1.5")
ex("ex1.5", 21, "With the complex encryption key $k = 3 - 3i$, encrypt the word \"QUIZ\" and recover the original word using the inverse of the key.", [cipher("QUIZ", C(3, -3), "*")], "1.5")
p22 = cipher("CLASS", C(-3, 4), "+")
note(p22, "The question says to ADD the key; the handwritten notes multiply by it instead (their decryption still returns CLASS). Adding gives $4i,\\ 9 + 4i,\\ -2 + 4i,\\ 16 + 4i,\\ 16 + 4i$.",
     "سوال میں کلید جمع کرنے کا کہا گیا ہے؛ ہاتھ کے نوٹس میں ضرب دی گئی ہے۔ جمع کرنے سے $4i,\\ 9 + 4i,\\ -2 + 4i,\\ 16 + 4i,\\ 16 + 4i$ ملتا ہے۔")
ex("ex1.5", 22, "Encrypt the word \"CLASS\" by adding the complex encryption key $k = -3 + 4i$. Then decrypt it back to the original word.", [p22], "1.5")
