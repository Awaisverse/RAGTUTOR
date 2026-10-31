"""Class 10, Unit 7 - Trigonometry: Exercises 7.1-7.4 and Review Exercise 7.

Questions transcribed from the reference notes (data/class10/pages/u07_*.png). Exact values are checked symbolically; decimal answers
are checked numerically (the rounded value must be within half a unit of the last decimal place of the exact value).
Final answers are checked against data/answers10/unit07.json; notes errors are recorded with key_note.
"""
import math

import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 7, "title": "Trigonometry", "title_ur": "مثلثیات", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational


def d2r(d):
    return d * math.pi / 180


def sin(d):
    return math.sin(d2r(d))


def cos(d):
    return math.cos(d2r(d))


def tan(d):
    return math.tan(d2r(d))


def asin(v):
    return math.degrees(math.asin(v))


def atan(v):
    return math.degrees(math.atan(v))


def acos(v):
    return math.degrees(math.acos(v))


def r(v, k):
    """round half up to k decimals, as a string."""
    s = f"{v:.{k}f}"
    return s


def near(expr, value, k):
    """A check that the sympy expression equals value to k decimal places."""
    return f"Abs(({expr}) - {value}) <= {0.5 * 10 ** (-k) + 1e-9}"


def dg(x):
    """Degrees inside a check: sin(42*pi/180)."""
    return f"({x})*pi/180"


# ------------------------------------------------------------------------------------------ Exercise 7.1

SIGNS = [("i", "sin", 55), ("ii", "cos", 145), ("iii", "tan", 111), ("iv", "sec", 179), ("v", "cosec", 88), ("vi", "cot", 14)]
POS = {1: {"sin", "cos", "tan", "cosec", "sec", "cot"}, 2: {"sin", "cosec"}, 3: {"tan", "cot"}, 4: {"cos", "sec"}}
FN = {"sin": "sin", "cos": "cos", "tan": "tan", "sec": "sec", "cosec": "csc", "cot": "cot"}


def sign_part(label, f, d):
    q = 1 + int(d // 90) if d % 90 else int(d // 90)
    pos = f in POS[q]
    return P(label, [S(rf"{d}^\circ \text{{ lies in quadrant {['I', 'II', 'III', 'IV'][q - 1]}}}", f"${d}^\\circ$ is between ${90 * (q - 1)}^\\circ$ and ${90 * q}^\\circ$.",
                       f"${d}^\\circ$، ${90 * (q - 1)}^\\circ$ اور ${90 * q}^\\circ$ کے درمیان ہے۔"),
                     S(rf"\{f}\ {d}^\circ \text{{ is {'positive' if pos else 'negative'}}}" if f != "cosec" else rf"\operatorname{{cosec}}\ {d}^\circ \text{{ is {'positive' if pos else 'negative'}}}",
                       "All are positive in I; sin and cosec in II; tan and cot in III; cos and sec in IV.",
                       "ربع I میں سب مثبت؛ II میں sin اور cosec؛ III میں tan اور cot؛ IV میں cos اور sec۔",
                       f"{FN[f]}({dg(d)}) {'>' if pos else '<'} 0")], "Positive" if pos else "Negative", prompt=f"$\\{f}\\ {d}^\\circ$" if f != "cosec" else f"$\\operatorname{{cosec}}\\ {d}^\\circ$")


ex("ex7.1", 1, "Find the signs of the following: (i) $\\sin 55^\\circ$ (ii) $\\cos 145^\\circ$ (iii) $\\tan 111^\\circ$ (iv) $\\sec 179^\\circ$ "
   "(v) $\\operatorname{cosec} 88^\\circ$ (vi) $\\cot 14^\\circ$", [sign_part(l, f, d) for l, f, d in SIGNS], "7.1")

BL = [("i", r"\tan(180^\circ - \theta) = -\tan\theta", "tan(pi - t) == -tan(t)", r"-\tan\theta", "II: tan is negative; $180^\\circ$ keeps the same ratio"),
      ("ii", r"\sin(180^\circ - \theta) = +\sin\theta", "sin(pi - t) == sin(t)", r"+\sin\theta", "II: sin is positive; $180^\\circ$ keeps the same ratio"),
      ("iii", r"\tan(90^\circ + \theta) = -\cot\theta", "tan(pi/2 + t) == -cot(t)", r"-\cot\theta", "II: tan is negative; $90^\\circ$ changes tan to cot"),
      ("iv", r"\cos(90^\circ + \theta) = -\sin\theta", "cos(pi/2 + t) == -sin(t)", r"-\sin\theta", "II: cos is negative; $90^\\circ$ changes cos to sin"),
      ("v", r"\operatorname{cosec}(180^\circ - \theta) = +\operatorname{cosec}\theta", "csc(pi - t) == csc(t)", r"+\operatorname{cosec}\theta", "II: cosec is positive"),
      ("vi", r"\sec(90^\circ - \theta) = +\operatorname{cosec}\theta", "sec(pi/2 - t) == csc(t)", r"+\operatorname{cosec}\theta", "I: all positive; $90^\\circ$ changes sec to cosec")]
ex("ex7.1", 2, r"Fill in the blanks: (i) $\tan(180^\circ-\theta)=\ldots\tan\theta$ (ii) $\sin(180^\circ-\theta)=\ldots\sin\theta$ (iii) $\tan(90^\circ+\theta)=\ldots\cot\theta$ "
   r"(iv) $\cos(90^\circ+\theta)=\ldots\sin\theta$ (v) $\operatorname{cosec}(180^\circ-\theta)=\ldots\operatorname{cosec}\theta$ (vi) $\sec(90^\circ-\theta)=\ldots\operatorname{cosec}\theta$", [
       P(l, [S(t, f"For acute $\\theta$ the angle is in quadrant {why}.", "زاویے کا ربع اور ریشو کی تبدیلی دیکھیں۔", chk)], f"${a}$", prompt=f"${t.split('=')[0]}= \\ldots {a.lstrip('+-')}$")   # the blank as printed
       for l, t, chk, a, why in BL], "7.1")

EX = [("i", "sin", 150, r"\sin(1\times 90^\circ + 60^\circ) = \cos 60^\circ", R(1, 2)),
      ("ii", "tan", 150, r"\tan(1\times 90^\circ + 60^\circ) = -\cot 60^\circ", -1 / sp.sqrt(3)),
      ("iii", "sec", 150, r"\sec(1\times 90^\circ + 60^\circ) = -\operatorname{cosec} 60^\circ", -2 / sp.sqrt(3)),
      ("iv", "cosec", 120, r"\operatorname{cosec}(1\times 90^\circ + 30^\circ) = \sec 30^\circ", 2 / sp.sqrt(3)),
      ("v", "cos", 120, r"\cos(1\times 90^\circ + 30^\circ) = -\sin 30^\circ", R(-1, 2)),
      ("vi", "cot", 120, r"\cot(1\times 90^\circ + 30^\circ) = -\tan 30^\circ", -1 / sp.sqrt(3)),
      ("vii", "sin", 135, r"\sin(1\times 90^\circ + 45^\circ) = \cos 45^\circ", 1 / sp.sqrt(2)),
      ("viii", "sec", 135, r"\sec(1\times 90^\circ + 45^\circ) = -\operatorname{cosec} 45^\circ", -sp.sqrt(2)),
      ("ix", "cot", 135, r"\cot(1\times 90^\circ + 45^\circ) = -\tan 45^\circ", -1)]


def rtex(v):
    """1/sqrt(3) style, as the notes write exact trig values."""
    v = sp.nsimplify(v)
    if v.is_Rational:
        return sp.latex(v)
    q = v ** 2
    a, b = sp.fraction(sp.nsimplify(q))
    sg = "-" if v < 0 else ""
    if sp.sqrt(a).is_Integer and b != 1:
        return rf"{sg}\frac{{{sp.sqrt(a)}}}{{\sqrt{{{b}}}}}"
    return sp.latex(v)


def fname(f):
    return r"\operatorname{cosec}" if f == "cosec" else "\\" + f


ex("ex7.1", 3, r"Without using calculator, find the exact values of the following trigonometric functions: (i) $\sin 150^\circ$ (ii) $\tan 150^\circ$ (iii) $\sec 150^\circ$ "
   r"(iv) $\operatorname{cosec} 120^\circ$ (v) $\cos 120^\circ$ (vi) $\cot 120^\circ$ (vii) $\sin 135^\circ$ (viii) $\sec 135^\circ$ (ix) $\cot 135^\circ$", [
       P(l, [S(rf"{fname(f)}\ {d}^\circ = {t} = {rtex(v)}", "Write the angle as $90^\\circ + \\theta$: an odd multiple of $90^\\circ$ changes the ratio to its co-ratio; "
               "the sign is the sign of the ratio in quadrant II.", "زاویہ $90^\\circ + \\theta$ لکھیں: $90^\\circ$ کا طاق مضرب ریشو کو اس کی ہم ریشو میں بدل دیتا ہے؛ علامت ربع II والی ہے۔",
               f"{FN[f]}({dg(d)}) == {sp.sstr(v)}")], f"${rtex(v)}$", prompt=f"${fname(f)}\\ {d}^\\circ$") for l, f, d, t, v in EX], "7.1")

# ------------------------------------------------------------------------------------------ Exercise 7.2 (law of sines, area)


def solve_ssa(label, given, a_name, a, b_name, b, A_name, A, prompt, prec=(1, 2)):
    """Two sides and the angle opposite the first: law of sines for the other angle (acute value), then the rest."""
    ka, ks = prec
    sB = b * sin(A) / a
    B = asin(sB)
    other = [n for n in ("alpha", "beta", "gamma") if n not in (A_name, {"a": "alpha", "b": "beta", "c": "gamma"}[b_name])][0]
    C = 180 - A - B
    side = {"alpha": "a", "beta": "b", "gamma": "c"}[other]
    c = a * sin(C) / sin(A)
    Bn = {"a": "alpha", "b": "beta", "c": "gamma"}[b_name]
    steps = [S(rf"\frac{{{a_name}}}{{\sin\{A_name}}} = \frac{{{b_name}}}{{\sin\{Bn}}}", "Law of sines.", "قانون جیب (Law of sines)۔"),
             S(rf"\sin\{Bn} = \frac{{{b_name}\sin\{A_name}}}{{{a_name}}} = \frac{{{b}\sin {A}^\circ}}{{{a}}} = {r(sB, 3)}", f"Make $\\sin\\{Bn}$ the subject.",
               f"$\\sin\\{Bn}$ کو موضوع بنائیں۔", near(f"{b}*sin({dg(A)})/{a}", r(sB, 3), 3)),
             S(rf"\{Bn} = \sin^{{-1}}({r(sB, 3)}) = {r(B, ka)}^\circ", "Take the inverse sine (the acute angle).", "معکوس جیب لیں (حادہ زاویہ)۔",
               near(f"asin({b}*sin({dg(A)})/{a})*180/pi", r(B, ka), ka)),
             S(rf"\{other} = 180^\circ - {A}^\circ - {r(B, ka)}^\circ = {r(C, ka)}^\circ", "The angles of a triangle add to $180^\\circ$.", "مثلث کے زاویوں کا مجموعہ $180^\\circ$ ہے۔",
               near(f"180 - {A} - asin({b}*sin({dg(A)})/{a})*180/pi", r(C, ka), ka)),
             S(rf"{side} = \frac{{{a_name}\sin\{other}}}{{\sin\{A_name}}} = \frac{{{a}\sin {r(C, ka)}^\circ}}{{\sin {A}^\circ}} = {r(c, ks)}", "Law of sines again for the third side.",
               "تیسرے ضلع کے لیے دوبارہ قانون جیب۔", near(f"{a}*sin((180 - {A} - asin({b}*sin({dg(A)})/{a})*180/pi)*pi/180)/sin({dg(A)})", r(c, ks), ks))]
    ans = rf"$\{Bn} = {r(B, ka)}^\circ,\ \{other} = {r(C, ka)}^\circ,\ {side} = {r(c, ks)}$ cm"
    return P(label, steps, ans, prompt=prompt)


def solve_aas(label, known_side, s_val, s_angle, angles, prompt, prec=(1, 2)):
    """One side and two angles: third angle, then law of sines for the other two sides. angles: {name: value} for two angles."""
    names = ["alpha", "beta", "gamma"]
    third = [n for n in names if n not in angles][0]
    third_val = 180 - sum(angles.values())
    allang = {**angles, third: third_val}
    side_of = {"alpha": "a", "beta": "b", "gamma": "c"}
    steps = [S(rf"\{third} = 180^\circ - " + " - ".join(f"{v}^\\circ" for v in angles.values()) + rf" = {third_val}^\circ", "The angles of a triangle add to $180^\\circ$.",
               "مثلث کے زاویوں کا مجموعہ $180^\\circ$ ہے۔", f"180 - {sum(angles.values())} == {third_val}")]
    out = []
    for n in names:
        if side_of[n] == known_side:
            continue
        v = s_val * sin(allang[n]) / sin(allang[s_angle])
        steps.append(S(rf"{side_of[n]} = \frac{{{known_side}\sin\{n}}}{{\sin\{s_angle}}} = \frac{{{s_val}\sin {allang[n]}^\circ}}{{\sin {allang[s_angle]}^\circ}} = {r(v, prec[1])}",
                       "Law of sines.", "قانون جیب۔", near(f"{s_val}*sin({dg(allang[n])})/sin({dg(allang[s_angle])})", r(v, prec[1]), prec[1])))
        out.append(f"{side_of[n]} = {r(v, prec[1])}")
    return P(label, steps, rf"$\{third} = {third_val}^\circ,\ " + r",\ ".join(out) + "$ cm", prompt=prompt)


Q1 = [solve_ssa("i", "", "a", 6.1, "b", 8.4, "alpha", 42, r"$a=6.1$ cm, $b=8.4$ cm, $\alpha=42^\circ$", prec=(1, 1)),
      solve_ssa("ii", "", "c", 15.8, "a", 12.2, "gamma", 50, r"$a=12.2$ cm, $c=15.8$ cm, $\gamma=50^\circ$", prec=(1, 1)),
      solve_ssa("iii", "", "c", 5, "b", 5.2, "gamma", 48, r"$b=5.2$ cm, $c=5$ cm, $\gamma=48^\circ$"),
      solve_ssa("iv", "", "b", 4.8, "a", 4, "beta", 71, r"$b=4.8$ cm, $a=4$ cm, $\beta=71^\circ$"),
      solve_aas("v", "b", 8, "beta", {"beta": 70, "alpha": 100}, r"$\beta=70^\circ$, $b=8$ cm, $\alpha=100^\circ$"),
      solve_aas("vi", "a", 6, "alpha", {"alpha": 55, "gamma": 60}, r"$a=6$ cm, $\alpha=55^\circ$, $\gamma=60^\circ$"),
      solve_aas("vii", "c", 7, "gamma", {"beta": 34, "gamma": 64}, r"$c=7$ cm, $\beta=34^\circ$, $\gamma=64^\circ$"),
      solve_aas("viii", "b", 12, "beta", {"alpha": 92, "beta": 77}, r"$b=12$ cm, $\alpha=92^\circ$, $\beta=77^\circ$")]
ex("ex7.2", 1, r"Solve the triangle $ABC$, in which (i) $a=6.1$ cm, $b=8.4$ cm, $\alpha=42^\circ$ (ii) $a=12.2$ cm, $c=15.8$ cm, $\gamma=50^\circ$ "
   r"(iii) $b=5.2$ cm, $c=5$ cm, $\gamma=48^\circ$ (iv) $b=4.8$ cm, $a=4$ cm, $\beta=71^\circ$ (v) $\beta=70^\circ$, $b=8$ cm, $\alpha=100^\circ$ "
   r"(vi) $a=6$ cm, $\alpha=55^\circ$, $\gamma=60^\circ$ (vii) $c=7$ cm, $\beta=34^\circ$, $\gamma=64^\circ$ (viii) $b=12$ cm, $\alpha=92^\circ$, $\beta=77^\circ$", Q1, "7.2")


def area_sas(label, s1n, s1, s2n, s2, an, ang, prompt):
    A = 0.5 * s1 * s2 * sin(ang)
    return P(label, [S(rf"\text{{Area}} = \frac{{1}}{{2}}{s1n}{s2n}\sin\{an}", "Area = half the product of two sides and the sine of the angle between them.",
                       "رقبہ = دو اضلاع کے حاصل ضرب کا آدھا ضرب ان کے درمیانی زاویے کا جیب۔"),
                     S(rf"= \frac{{1}}{{2}}({s1})({s2})\sin {ang}^\circ = {r(A, 2)}\ \text{{cm}}^2", "Substitute.", "قیمتیں رکھیں۔",
                       near(f"R(1,2)*{s1}*{s2}*sin({dg(ang)})", r(A, 2), 2))], f"${r(A, 2)}$ cm$^2$", prompt=prompt)


def area_asa(label, sn, s, angles, opp, prompt):
    """One side and two angles: third angle, then Area = s^2 sin X sin Y / (2 sin Z) with Z opposite s."""
    names = ["alpha", "beta", "gamma"]
    third = [n for n in names if n not in angles][0]
    tv = 180 - sum(angles.values())
    allang = {**angles, third: tv}
    others = [n for n in names if n != opp]
    A = s * s * sin(allang[others[0]]) * sin(allang[others[1]]) / (2 * sin(allang[opp]))
    return P(label, [S(rf"\{third} = 180^\circ - " + " - ".join(f"{v}^\\circ" for v in angles.values()) + rf" = {tv}^\circ", "The angles add to $180^\\circ$.",
                       "زاویوں کا مجموعہ $180^\\circ$ ہے۔", f"180 - {sum(angles.values())} == {tv}"),
                     S(rf"\text{{Area}} = \frac{{{sn}^2\sin\{others[0]}\sin\{others[1]}}}{{2\sin\{opp}}} = \frac{{{s}^2\sin {allang[others[0]]}^\circ\sin {allang[others[1]]}^\circ}}{{2\sin {allang[opp]}^\circ}} = {r(A, 2)}\ \text{{cm}}^2",
                       "Area from one side and the angles.", "ایک ضلع اور زاویوں سے رقبہ۔",
                       near(f"{s}**2*sin({dg(allang[others[0]])})*sin({dg(allang[others[1]])})/(2*sin({dg(allang[opp])}))", r(A, 2), 2))],
             f"${r(A, 2)}$ cm$^2$", prompt=prompt)


def heron(label, a, b, c, prompt, k=2):
    s = (a + b + c) / 2
    A = math.sqrt(s * (s - a) * (s - b) * (s - c))
    return P(label, [S(rf"s = \frac{{a + b + c}}{{2}} = \frac{{{a} + {b} + {c}}}{{2}} = {s:g}", "Half the perimeter.", "نصف احاطہ۔", f"({a} + {b} + {c})/2 == {s}"),
                     S(rf"\Delta = \sqrt{{s(s - a)(s - b)(s - c)}} = \sqrt{{{s:g}({s - a:g})({s - b:g})({s - c:g})}} = {r(A, k)}\ \text{{cm}}^2", "Hero's formula.", "ہیرو کا کلیہ۔",
                       near(f"sqrt({s}*({s} - {a})*({s} - {b})*({s} - {c}))", r(A, k), k))], f"${r(A, k)}$ cm$^2$", prompt=prompt)


Q2 = [area_sas("i", "a", 7, "b", 8, "gamma", 38, r"$a=7$ cm, $b=8$ cm, $\gamma=38^\circ$"),
      area_sas("ii", "a", 11, "c", 14, "beta", 51, r"$a=11$ cm, $c=14$ cm, $\beta=51^\circ$"),
      area_sas("iii", "b", 3, "c", 9, "alpha", 78, r"$b=3$ cm, $c=9$ cm, $\alpha=78^\circ$"),
      area_asa("iv", "a", 10, {"alpha": 62, "beta": 69}, "alpha", r"$a=10$ cm, $\alpha=62^\circ$, $\beta=69^\circ$"),
      area_asa("v", "c", 4, {"beta": 36, "gamma": 80}, "gamma", r"$c=4$ cm, $\beta=36^\circ$, $\gamma=80^\circ$"),
      area_asa("vi", "c", 6.6, {"alpha": 23, "gamma": 89}, "gamma", r"$c=6.6$ cm, $\alpha=23^\circ$, $\gamma=89^\circ$"),
      heron("vii", 5.3, 4.7, 8.2, r"$a=5.3$ cm, $b=4.7$ cm, $c=8.2$ cm"),
      heron("viii", 6.12, 8.34, 7.12, r"$a=6.12$ cm, $b=8.34$ cm, $c=7.12$ cm")]
ex("ex7.2", 2, r"Calculate area of each triangle $ABC$. (i) $a=7$ cm, $b=8$ cm, $\gamma=38^\circ$ (ii) $a=11$ cm, $c=14$ cm, $\beta=51^\circ$ "
   r"(iii) $b=3$ cm, $c=9$ cm, $\alpha=78^\circ$ (iv) $a=10$ cm, $\alpha=62^\circ$, $\beta=69^\circ$ (v) $c=4$ cm, $\beta=36^\circ$, $\gamma=80^\circ$ "
   r"(vi) $c=6.6$ cm, $\alpha=23^\circ$, $\gamma=89^\circ$ (vii) $a=5.3$ cm, $b=4.7$ cm, $c=8.2$ cm (viii) $a=6.12$ cm, $b=8.34$ cm, $c=7.12$ cm", Q2, "7.2")

# ------------------------------------------------------------------------------------------ Exercise 7.3 (3D and applications)


def steps_of(rows):
    return [S(t, en, ur, *c) for t, en, ur, c in rows]


ex("ex7.3", 1, "In the triangular prism, find (i) the length $\\overline{CF}$. (ii) the length $\\overline{BF}$. (iii) the angle $BFC$, correct to one decimal place. "
   "(In the figure $FE = 5$ cm, $EC = 4$ cm, $BC = 3$ cm, with right angles at $E$ and $C$.)", [
       P("i", steps_of([(r"CF^2 = FE^2 + EC^2 = 5^2 + 4^2 = 41 \Rightarrow CF = \sqrt{41} \approx 6.4\ \text{cm}", "Pythagoras in the right triangle $FEC$.",
                         "قائمہ مثلث $FEC$ میں فیثا غورث۔", ["5**2 + 4**2 == 41", near("sqrt(41)", "6.4", 1)])]), "$6.4$ cm", prompt="the length $CF$"),
       P("ii", steps_of([(r"BF^2 = BC^2 + CF^2 = 3^2 + 41 = 50 \Rightarrow BF = \sqrt{50} = 5\sqrt{2} \approx 7.1\ \text{cm}", "Pythagoras in the right triangle $BCF$.",
                          "قائمہ مثلث $BCF$ میں فیثا غورث۔", ["3**2 + 41 == 50", "sqrt(50) == 5*sqrt(2)", near("sqrt(50)", "7.1", 1)])]), "$7.1$ cm", prompt="the length $BF$"),
       P("iii", steps_of([(r"\tan\angle BFC = \frac{BC}{CF} = \frac{3}{\sqrt{41}} \approx 0.4685", "Opposite over adjacent in the right triangle $BCF$.",
                           "قائمہ مثلث $BCF$ میں مقابل تقسیم متصل۔", [near("3/sqrt(41)", "0.4685", 4)]),
                          (r"\angle BFC = \tan^{-1}(0.4685) \approx 25.1^\circ", "Inverse tangent.", "معکوس ٹینجنٹ۔", [near("atan(3/sqrt(41))*180/pi", "25.1", 1)])]),
         r"$25.1^\circ$", prompt="the angle $BFC$")], "7.3")


def single(eid, n, question, rows, answer, exercise="7.3", note=None):
    p = P("", steps_of(rows), answer)
    if note:
        p["key_note"] = note
    ex(eid, n, question, [p], exercise)


single("ex7.3", 2, "The diagram shows a triangular pyramid with a horizontal rectangular base $PQRS$, in which $m\\overline{PQ} = 16$ cm, $m\\overline{QR} = 10$ cm. $M$ is the "
       "midpoint of the line $PR$. The vertex, $T$, is vertically above $M$ and $m\\overline{MT} = 15$ cm. Calculate the size of the angle between $TP$ and the base $PQRS$. "
       "Give your answer correct to 1 decimal place.", [
           (r"PR = \sqrt{16^2 + 10^2} = \sqrt{356} \approx 18.87\ \text{cm},\quad PM = \frac{PR}{2} \approx 9.43\ \text{cm}", "Diagonal of the base; $M$ is its midpoint.",
            "قاعدے کا وتر؛ $M$ اس کا وسطی نقطہ ہے۔", ["16**2 + 10**2 == 356", near("sqrt(356)/2", "9.43", 2)]),
           (r"\tan\theta = \frac{MT}{PM} = \frac{15}{9.43} \Rightarrow \theta = \tan^{-1}(1.590) \approx 57.8^\circ", "In the right triangle $TPM$.", "قائمہ مثلث $TPM$ میں۔",
            [near("atan(15/(sqrt(356)/2))*180/pi", "57.8", 1)])], r"$57.8^\circ$")
single("ex7.3", 3, "The diagram shows a pyramid. The base, $PQRS$, is a horizontal square of side 10 cm. The vertex, $V$, is vertically above the midpoint, $M$ and "
       "$m\\overline{VM} = 12$ cm. Calculate the size of angle $VPM$.", [
           (r"PR = \sqrt{10^2 + 10^2} = \sqrt{200} \approx 14.14,\quad PM = 7.07\ \text{cm}", "Half the diagonal of the square.", "مربع کے وتر کا آدھا۔",
            [near("sqrt(200)/2", "7.07", 2)]),
           (r"\tan\theta = \frac{12}{7.07} \approx 1.697 \Rightarrow \theta \approx 59.5^\circ", "Right triangle $VPM$.", "قائمہ مثلث $VPM$۔",
            [near("atan(12/(sqrt(200)/2))*180/pi", "59.5", 1)])], r"$59.5^\circ$")
single("ex7.3", 4, "$ABCDE$ is a square based pyramid, in which $m\\overline{AE} = m\\overline{BE} = m\\overline{CE} = m\\overline{DE} = 12$ cm and $m\\overline{AB} = 15$ cm. "
       "Calculate the size of angle $DEB$. Give your answer in degree (whole numbers).", [
           (r"BD = \sqrt{15^2 + 15^2} = \sqrt{450} = 15\sqrt{2} \approx 21.21\ \text{cm}", "Diagonal of the square base.", "مربع قاعدے کا وتر۔", ["sqrt(450) == 15*sqrt(2)"]),
           (r"BD^2 = DE^2 + BE^2 - 2(DE)(BE)\cos\angle DEB \Rightarrow 450 = 288 - 288\cos\angle DEB", "Law of cosines in triangle $DEB$.", "مثلث $DEB$ میں قانون جیب التمام۔",
            ["12**2 + 12**2 == 288"]),
           (r"\cos\angle DEB = -\frac{162}{288} = -0.5625 \Rightarrow \angle DEB \approx 124^\circ", "Solve for the angle.", "زاویہ معلوم کریں۔",
            ["(288 - 450)/R(288) == -R(9,16)", near("acos(-R(9,16))*180/pi", "124", 0)])], r"$124^\circ$")
single("ex7.3", 5, "The diagram shows a triangular prism with a horizontal rectangular base $ABCD$. $m\\overline{AB} = 10$ cm, $m\\overline{BC} = 7$ cm, $M$ is the midpoint of $AD$. "
       "The vertex $T$ is vertically above $M$ and $m\\overline{MT} = 6$ cm. Calculate the size of the angle between $\\overline{TB}$ and the base.", [
           (r"MB = \sqrt{AM^2 + AB^2} = \sqrt{3.5^2 + 10^2} \approx 10.59\ \text{cm}", "$AM = 3.5$ cm (half of $AD = 7$); right angle at $A$.", "$AM = 3.5$ سینٹی میٹر؛ $A$ پر قائمہ۔",
            [near("sqrt(R(7,2)**2 + 10**2)", "10.59", 2)]),
           (r"\tan\theta = \frac{MT}{MB} = \frac{6}{10.59} \approx 0.5663 \Rightarrow \theta \approx 29.5^\circ", "Right triangle $TMB$.", "قائمہ مثلث $TMB$۔",
            [near("atan(6/sqrt(R(7,2)**2 + 10**2))*180/pi", "29.5", 1)])], r"$29.5^\circ$")
single("ex7.3", 6, "In an isometric game, the camera is placed at a $45^\\circ$ angle from the ground. If the player is 10 units in front and 10 units above, what is the direct line of sight distance?", [
    (r"d = \sqrt{10^2 + 10^2} = \sqrt{200} = 10\sqrt{2} \approx 14.14\ \text{units}", "Pythagoras.", "فیثا غورث۔", ["sqrt(200) == 10*sqrt(2)", near("10*sqrt(2)", "14.14", 2)])],
    r"$10\sqrt{2} \approx 14.14$ units")
single("ex7.3", 7, "A surveyor spots the top of a tower at an elevation angle of $28^\\circ$. He is standing 60 metres from the base. Find the height of the tower.", [
    (r"\tan 28^\circ = \frac{h}{60} \Rightarrow h = 60\tan 28^\circ \approx 60 \times 0.5317 \approx 31.90\ \text{m}", "Opposite = adjacent $\\times$ tan.", "مقابل = متصل $\\times$ tan۔",
     [near(f"60*tan({dg(28)})", "31.90", 2)])], r"$31.90$ m")
single("ex7.3", 8, "A boat crosses a river 80 m wide, at a $60^\\circ$ angle to the current. What distance does the boat actually travel?", [
    (r"\cos 60^\circ = \frac{80}{x} \Rightarrow x = \frac{80}{\cos 60^\circ} = \frac{80}{1/2} = 160\ \text{m}", "As drawn in the notes, the width is the side next to the $60^\\circ$ angle.",
     "نوٹس کی شکل کے مطابق چوڑائی $60^\\circ$ کے متصل ضلع ہے۔", [f"80/cos({dg(60)}) == 160"])], "$160$ m")
single("ex7.3", 9, "A listener hears a sound from two speakers. One is 6 m directly ahead and the other is at $30^\\circ$ to the side, 6 m away. Find the distance between the speakers.", [
    (r"d^2 = 6^2 + 6^2 - 2(6)(6)\cos 30^\circ = 72 - 72\left(\frac{\sqrt{3}}{2}\right) \approx 9.65", "Law of cosines.", "قانون جیب التمام۔",
     [f"6**2 + 6**2 - 2*6*6*cos({dg(30)}) == 72 - 36*sqrt(3)", near("72 - 36*sqrt(3)", "9.65", 2)]),
    (r"d = \sqrt{9.65} \approx 3.1\ \text{m}", "Square root.", "جذر۔", [near("sqrt(72 - 36*sqrt(3))", "3.1", 1)])], "$3.1$ m")
single("ex7.3", 10, "A 10 m ladder leans against a wall making an angle of $75^\\circ$ with the ground. How high does it reach up the wall?", [
    (r"h = 10\sin 75^\circ \approx 10 \times 0.9659 \approx 9.66\ \text{m}", "Opposite = hypotenuse $\\times$ sin.", "مقابل = وتر $\\times$ sin۔", [near(f"10*sin({dg(75)})", "9.66", 2)])],
    "$9.66$ m")
single("ex7.3", 11, "A lighthouse is located on a cliff 80 m above sea level. A ship is spotted at an angle of depression of $12^\\circ$. How far is the ship from the base of the cliff?", [
    (r"\tan 12^\circ = \frac{80}{d} \Rightarrow d = \frac{80}{\tan 12^\circ} \approx \frac{80}{0.2126} \approx 376.4\ \text{m}",
     "The angle of depression equals the angle of elevation from the ship (alternate angles).", "زاویہ نشیب، جہاز سے زاویہ ارتفاع کے برابر ہے (متبادل زاویے)۔",
     [near(f"80/tan({dg(12)})", "376.4", 1)])], "$376.4$ m",
    note={"en": "The reference notes round $80/0.2126$ to 376.5; the exact value is 376.37... m, i.e. 376.4 m to one decimal place.",
          "ur": "حوالہ نوٹس میں 376.5 لکھا ہے؛ درست قیمت ایک اعشاریہ تک 376.4 میٹر ہے۔"})

# ------------------------------------------------------------------------------------------ Exercise 7.4 (bearings)

BR = [("i", r"180^\circ - 40^\circ = 140^\circ", "180 - 40 == 140", "140", "$P$ is $40^\\circ$ east of South: measure clockwise from North."),
      ("ii", r"270^\circ + 20^\circ = 290^\circ", "270 + 20 == 290", "290", "$P$ is $20^\\circ$ north of West."),
      ("iii", r"270^\circ - 50^\circ = 220^\circ", "270 - 50 == 220", "220", r"$P$ is $50^\circ$ south of West."),
      ("iv", r"90^\circ - 75^\circ = 015^\circ", "90 - 75 == 15", "015", "$P$ is $75^\\circ$ north of East.")]
ex("ex7.4", 1, "Find bearing of point $P$ in each of the following (as drawn in the book): (i) $40^\\circ$ east of South (ii) $20^\\circ$ north of West "
   "(iii) $50^\\circ$ south of West (iv) $75^\\circ$ north of East", [
       P(l, [S(rf"\text{{Bearing of }} \overrightarrow{{OP}} = {t}", why + " A bearing is measured clockwise from North and written with 3 figures.",
               "سمت (bearing) شمال سے گھڑی کی سوئی کی سمت میں ناپی جاتی ہے اور 3 ہندسوں میں لکھی جاتی ہے۔", c)], f"${a}^\\circ$") for l, t, c, a, why in BR], "7.4")
ex("ex7.4", 2, "The diagram shows the positions of two ships $P$ and $Q$ (the angle at $Q$ between North and $QP$ is $60^\\circ$, $P$ to the north-west). "
   "(i) What is the bearing of ship $P$ from ship $Q$? (ii) What is bearing of ship $Q$ from ship $P$?", [
       P("i", [S(r"360^\circ - 60^\circ = 300^\circ", "$P$ is $60^\\circ$ west of North as seen from $Q$.", "$Q$ سے دیکھیں تو $P$ شمال سے $60^\\circ$ مغرب کی طرف ہے۔", "360 - 60 == 300")],
         r"$300^\circ$", prompt="bearing of $P$ from $Q$"),
       P("ii", [S(r"300^\circ - 180^\circ = 120^\circ", "A back bearing differs by $180^\\circ$.", "الٹی سمت میں $180^\\circ$ کا فرق ہوتا ہے۔", "300 - 180 == 120")],
         r"$120^\circ$", prompt="bearing of $Q$ from $P$")], "7.4")
B3 = [("i", "A from C", r"360^\circ - 50^\circ = 310^\circ", "360 - 50 == 310", "310"), ("ii", "C from A", r"310^\circ - 180^\circ = 130^\circ", "310 - 180 == 130", "130"),
      ("iii", "C from B", r"180^\circ + 40^\circ = 220^\circ", "180 + 40 == 220", "220"), ("iv", "B from C", r"040^\circ", "40 == 40", "040")]
ex("ex7.4", 3, "The diagram shows 3 places $A$, $B$ and $C$ ($A$ is $50^\\circ$ west of North from $C$, $B$ is $40^\\circ$ east of North from $C$). Find the bearing of: "
   "(i) $A$ from $C$ (ii) $C$ from $A$ (iii) $C$ from $B$ (iv) $B$ from $C$", [
       P(l, [S(t, "Measure clockwise from North; a back bearing differs by $180^\\circ$.", "شمال سے گھڑی کی سمت ناپیں؛ الٹی سمت میں $180^\\circ$ کا فرق۔", c)], f"${a}^\\circ$", prompt=w)
       for l, w, t, c, a in B3], "7.4")
ex("ex7.4", 4, "Abdul Hadi walks 100 m North and then 300 m East. (i) How far is he from his starting position? (ii) On what bearing should he walk to get back to his starting position?", [
    P("i", [S(r"\sqrt{100^2 + 300^2} = \sqrt{100000} \approx 316.2\ \text{m}", "Pythagoras.", "فیثا غورث۔", "100**2 + 300**2 == 100000", near("sqrt(100000)", "316.2", 1))],
      "$316.2$ m", prompt="distance from the start"),
    P("ii", [S(r"\tan\theta = \frac{300}{100} = 3 \Rightarrow \theta \approx 71.57^\circ", "Angle at the start between North and the path.", "ابتدائی نقطے پر شمال اور راستے کے درمیان زاویہ۔",
               near("atan(3)*180/pi", "71.57", 2)),
             S(r"\text{Bearing back} = 180^\circ + 71.57^\circ = 251.57^\circ \approx 252^\circ", "To go back he walks S $71.57^\\circ$ W.", "واپسی کے لیے جنوب سے $71.57^\\circ$ مغرب۔",
               near("180 + atan(3)*180/pi", "252", 0))], r"$252^\circ$ (S $71.57^\circ$ W)", prompt="bearing back to the start")], "7.4")
single("ex7.4", 5, "Three ships $L$, $M$, $N$ are in the position shown in the diagram (from the diagram: $L$ is due West of $M$, $LM = 12$ km, $LN = 14$ km, $MN = 15$ km). Ship $M$ is North East of ship $N$. Find the bearing of $L$ from $M$.", [
    (r"\text{Bearing of } L \text{ from } M = 270^\circ", "$L$ is due West of $M$ (the line $LM$ is horizontal in the diagram).", "$L$، $M$ کے بالکل مغرب میں ہے۔", ["360 - 90 == 270"])],
    r"$270^\circ$", exercise="7.4")
single("ex7.4", 6, "A ship sails 20 km on a bearing of $120^\\circ$. How far to the South has the ship moved from its original position?", [
    (r"\text{southward} = 20\cos(180^\circ - 120^\circ) = 20\cos 60^\circ = 20 \times \frac{1}{2} = 10\ \text{km}", "Angle between the path and South is $60^\\circ$.",
     "راستے اور جنوب کے درمیان زاویہ $60^\\circ$ ہے۔", [f"20*cos({dg(60)}) == 10"])], "$10$ km", exercise="7.4")
single("ex7.4", 7, "Fatima walked South for 5.5 km and then turned West for 1.3 km. Calculate Huria's [i.e. Fatima's, as printed] bearing from her starting point.", [
    (r"\tan\alpha = \frac{1.3}{5.5} \approx 0.236 \Rightarrow \alpha \approx 13.30^\circ", "Angle west of South.", "جنوب سے مغرب کی طرف زاویہ۔", [near("atan(R(13,55))*180/pi", "13.30", 2)]),
    (r"\text{Bearing} = 180^\circ + 13.30^\circ \approx 193.3^\circ", "South is $180^\\circ$; add the angle towards West.", "جنوب $180^\\circ$ ہے؛ مغرب کی طرف کا زاویہ جمع کریں۔",
     [near("180 + atan(R(13,55))*180/pi", "193.3", 1)])], r"$193.3^\circ$", exercise="7.4",
    note={"en": "The reference notes give 193.2 after $180^\\circ + 13.29^\\circ$; $\\tan^{-1}(1.3/5.5) = 13.30^\\circ$, so the bearing is $193.3^\\circ$ to one decimal place.",
          "ur": "حوالہ نوٹس میں 193.2 لکھا ہے؛ درست قیمت $193.3^\\circ$ ہے۔"})
single("ex7.4", 8, "An aircraft flies 150 km east, then 100 km northeast ($45^\\circ$ from East). What is the total displacement?", [
    (r"\text{East} = 150 + 100\cos 45^\circ \approx 220.71,\quad \text{North} = 100\sin 45^\circ \approx 70.71", "Add the components.", "اجزاء جمع کریں۔",
     [near(f"150 + 100*cos({dg(45)})", "220.71", 2), near(f"100*sin({dg(45)})", "70.71", 2)]),
    (r"\text{Displacement} = \sqrt{220.71^2 + 70.71^2} \approx 231.76\ \text{km}", "Pythagoras.", "فیثا غورث۔",
     [near(f"sqrt((150 + 100*cos({dg(45)}))**2 + (100*sin({dg(45)}))**2)", "231.76", 2)])], "$231.76$ km", exercise="7.4",
    note={"en": "The reference notes give 231.91 km; $\\sqrt{220.71^2 + 70.71^2} = 231.76$ km.", "ur": "حوالہ نوٹس میں 231.91 لکھا ہے؛ درست 231.76 کلومیٹر ہے۔"})
single("ex7.4", 9, "A ship sails 100 km on a bearing of $045^\\circ$, then changes course and sails 120 km on a bearing of $135^\\circ$. Find the distance between the starting point and the final position.", [
    (r"\text{Angle between the courses} = 135^\circ - 45^\circ = 90^\circ", "The two legs are at right angles.", "دونوں راستوں کے درمیان قائمہ زاویہ ہے۔", ["135 - 45 == 90"]),
    (r"d^2 = 100^2 + 120^2 - 2(100)(120)\cos 90^\circ = 24400 \Rightarrow d \approx 156.2\ \text{km}", "Law of cosines ($\\cos 90^\\circ = 0$).", "قانون جیب التمام۔",
     [f"100**2 + 120**2 - 2*100*120*cos({dg(90)}) == 24400", near("sqrt(24400)", "156.2", 1)])], "$156.2$ km", exercise="7.4")

# ------------------------------------------------------------------------------------------ Review Exercise 7

q1 = [mcq("i", r"What is the value of $\cot 60^\circ$?", ["0", "1", r"\sqrt{3}", r"\frac{1}{\sqrt{3}}"], 3,
          [S(r"\cot 60^\circ = \frac{1}{\tan 60^\circ} = \frac{1}{\sqrt{3}}", "Reciprocal of tan.", "tan کا معکوس۔", f"cot({dg(60)}) == 1/sqrt(3)")]),
      mcq("ii", "All trigonometric ratios are positive in:", [r"\text{I-quadrant}", r"\text{II-quadrant}", r"\text{III-quadrant}", r"\text{IV-quadrant}"], 0,
          [T("In quadrant I both $x$ and $y$ are positive.", "ربع I میں $x$ اور $y$ دونوں مثبت ہیں۔")]),
      mcq("iii", r"$\operatorname{cosec}\theta$ is positive in:", [r"\text{I \& III-quadrants}", r"\text{II \& IV-quadrants}", r"\text{I \& II-quadrants}", r"\text{I \& IV-quadrants}"], 2,
          [T("cosec has the sign of sin: positive in I and II.", "cosec کی علامت sin والی ہے: I اور II میں مثبت۔")]),
      mcq("iv", r"$\sin(90^\circ+\theta)=$", [r"\sin\theta", r"-\sin\theta", r"\cos\theta", r"-\cos\theta"], 2,
          [S(r"\sin(90^\circ + \theta) = \cos\theta", "Quadrant II, sin positive; $90^\\circ$ changes sin to cos.", "ربع II، sin مثبت۔", "sin(pi/2 + t) == cos(t)")]),
      mcq("v", r"$\tan(180^\circ-\theta)=$", [r"\tan\theta", r"\cot\theta", r"-\cot\theta", r"-\tan\theta"], 3,
          [S(r"\tan(180^\circ - \theta) = -\tan\theta", "Quadrant II, tan negative.", "ربع II، tan منفی۔", "tan(pi - t) == -tan(t)")]),
      mcq("vi", "The law of sines is:", [r"\frac{b}{\sin\alpha}=\frac{a}{\sin\beta}=\frac{c}{\sin\gamma}", r"\frac{a}{\sin\alpha}=\frac{c}{\sin\beta}=\frac{b}{\sin\gamma}",
                                         r"\frac{a}{\sin\alpha}=\frac{b}{\sin\beta}=\frac{c}{\sin\gamma}", r"\frac{a}{\sin\alpha}=\frac{a}{\sin\beta}=\frac{a}{\sin\gamma}"], 2,
          [T("Each side over the sine of the opposite angle.", "ہر ضلع تقسیم مقابل زاویے کا جیب۔")]),
      mcq("vii", "The law of cosines is:", [r"\cos\alpha=\frac{b^2+a^2-c^2}{2ab}", r"\cos\beta=\frac{c^2+b^2-a^2}{2cb}", r"\cos\gamma=\frac{a^2+b^2-c^2}{2ab}",
                                            r"\cos\gamma=\frac{ca^2+b^2-c^2}{2ab}"], 2,
          [T("The angle's own side is the one subtracted.", "زاویے کے مقابل ضلع کا مربع تفریق ہوتا ہے۔")]),
      mcq("viii", r"Area of $\triangle ABC=$", [r"\frac{1}{2}ab\sin\alpha", r"\frac{1}{2}bc\sin\beta", r"\frac{1}{2}\sin\gamma", r"\frac{1}{2}ac\sin\beta"], 3,
          [T("Two sides and the angle between them ($\\beta$ is between $a$ and $c$).", "دو اضلاع اور ان کا درمیانی زاویہ۔")]),
      mcq("ix", "Bearing is measured from:", [r"\text{East}", r"\text{West}", r"\text{North}", r"\text{South}"], 2, [T("Bearings start at North.", "سمت شمال سے شروع ہوتی ہے۔")]),
      mcq("x", "Bearing is written as a:", [r"\text{1 figure}", r"\text{2 figures}", r"\text{3 figures}", r"\text{4 figures}"], 2, [T("For example $045^\\circ$.", "مثلاً $045^\\circ$۔")])]
ex("rev7", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 7")

b3, c3 = 3.1 * sin(36) / sin(44), 3.1 * sin(100) / sin(44)
ex("rev7", 2, r"Calculate the area of $\triangle ABC$, in which (i) $a=4$ cm, $b=6$ cm, $c=8$ cm (ii) $b=2.1$ cm, $c=5$ cm, $\gamma=45^\circ$ (iii) $c=3.1$ cm, $\gamma=44^\circ$, $\alpha=36^\circ$", [
    heron("i", 4, 6, 8, r"$a=4$ cm, $b=6$ cm, $c=8$ cm"),
    P("ii", steps_of([(r"\text{Area} = \frac{1}{2} \times 2.1 \times 5 \times \sin 45^\circ \approx 3.71\ \text{cm}^2",
                       "As in the reference notes, the given angle is used between the two sides.", "حوالہ نوٹس کی طرح دیا گیا زاویہ دونوں اضلاع کے درمیان لیا گیا ہے۔",
                       [near(f"R(1,2)*R(21,10)*5*sin({dg(45)})", "3.71", 2)])]), "$3.71$ cm$^2$", prompt=r"$b=2.1$ cm, $c=5$ cm, $\gamma=45^\circ$"),
    P("iii", steps_of([(r"\beta = 180^\circ - 44^\circ - 36^\circ = 100^\circ", "Angles add to $180^\\circ$.", "زاویوں کا مجموعہ $180^\\circ$۔", ["180 - 44 - 36 == 100"]),
                       (rf"a = \frac{{3.1\sin 36^\circ}}{{\sin 44^\circ}} \approx {r(b3, 3)},\quad b = \frac{{3.1\sin 100^\circ}}{{\sin 44^\circ}} \approx {r(c3, 3)}", "Law of sines.", "قانون جیب۔",
                        [near(f"R(31,10)*sin({dg(36)})/sin({dg(44)})", r(b3, 3), 3), near(f"R(31,10)*sin({dg(100)})/sin({dg(44)})", r(c3, 3), 3)]),
                       (rf"\text{{Area}} = \frac{{1}}{{2}}ab\sin\gamma = \frac{{1}}{{2}}({r(b3, 3)})({r(c3, 3)})\sin 44^\circ \approx 4.00\ \text{{cm}}^2", "Two sides and the included angle.",
                        "دو اضلاع اور درمیانی زاویہ۔", [near(f"R(1,2)*(R(31,10)*sin({dg(36)})/sin({dg(44)}))*(R(31,10)*sin({dg(100)})/sin({dg(44)}))*sin({dg(44)})", "4.00", 2)])]),
      "$4.00$ cm$^2$", prompt=r"$c=3.1$ cm, $\gamma=44^\circ$, $\alpha=36^\circ$")], "Review 7")
UNIT["items"][-1]["parts"][2]["key_note"] = {"en": "The reference notes give 4.01 cm$^2$; with $a = 2.623$, $b = 4.395$ the area is $4.00$ cm$^2$.", "ur": "حوالہ نوٹس میں 4.01 لکھا ہے؛ درست 4.00 ہے۔"}
r3 = solve_ssa("i", "", "a", 5.4, "b", 3.4, "alpha", 49, r"$a=5.4$ cm, $b=3.4$ cm, $\alpha=49^\circ$", prec=(2, 2))
r3["key_note"] = {"en": "The reference notes give $c = 6.48$ cm; with $\\gamma = 102.6^\\circ$, $c = \\frac{5.4\\sin 102.6^\\circ}{\\sin 49^\\circ} = 6.98$ cm.",
                  "ur": "حوالہ نوٹس میں $c = 6.48$ لکھا ہے؛ درست $c = 6.98$ سینٹی میٹر ہے۔"}
ex("rev7", 3, r"Solve the triangle $ABC$, in which (i) $a=5.4$ cm, $b=3.4$ cm, $\alpha=49^\circ$ (ii) $\alpha=32^\circ$, $\gamma=48^\circ$, $c=81$ cm", [
    r3, solve_aas("ii", "c", 81, "gamma", {"alpha": 32, "gamma": 48}, r"$\alpha=32^\circ$, $\gamma=48^\circ$, $c=81$ cm", prec=(1, 1))], "Review 7")
ex("rev7", 4, "The diagram shows a cuboid $ABCDEFGH$ in which $m\\overline{AB} = 5$ cm, $m\\overline{BC} = 7$ cm and $m\\overline{AE} = 3$ cm. (i) Calculate the length of "
   "$\\overline{AG}$. Give your answer correct to 3 significant figures. (ii) Calculate the size of the angle between $\\overline{AG}$ and the plane $ABCD$. Give your answer correct to 1 decimal place.", [
       P("i", steps_of([(r"AG = \sqrt{AB^2 + BC^2 + AE^2} = \sqrt{5^2 + 7^2 + 3^2} = \sqrt{83} \approx 9.11\ \text{cm}", "The space diagonal of a cuboid.", "مکعب نما کا فضائی وتر۔",
                         ["5**2 + 7**2 + 3**2 == 83", near("sqrt(83)", "9.11", 2)])]), "$9.11$ cm", prompt="the length $AG$"),
       P("ii", steps_of([(r"\tan\theta = \frac{3}{\sqrt{5^2 + 7^2}} = \frac{3}{\sqrt{74}} \Rightarrow \theta \approx 19.2^\circ", "The vertical edge over the base diagonal.",
                          "عمودی کنارہ تقسیم قاعدے کا وتر۔", [near("atan(3/sqrt(74))*180/pi", "19.2", 1)])]), r"$19.2^\circ$", prompt="the angle between $AG$ and $ABCD$")],
   "Review 7")
UNIT["items"][-1]["parts"][1]["key_note"] = {"en": "The reference notes give $20.9^\\circ$; $\\tan^{-1}(3/\\sqrt{74}) = 19.2^\\circ$.", "ur": "حوالہ نوٹس میں $20.9^\\circ$ لکھا ہے؛ درست $19.2^\\circ$ ہے۔"}
ex("rev7", 5, "The diagram shows a triangular prism $ABCDEF$ in which $m\\overline{AB} = 8$ cm, $m\\overline{BF} = 14$ cm and $m\\overline{EF} = 19$ cm. (i) Calculate the distance "
   "between $A$ and $F$. (ii) Calculate the angle between $\\overline{AF}$ and the plane $BCEF$.", [
       P("i", steps_of([(r"AF = \sqrt{AB^2 + BF^2} = \sqrt{8^2 + 14^2} = \sqrt{260} \approx 16.1\ \text{cm}", "Right triangle $ABF$ (right angle at $B$).", "قائمہ مثلث $ABF$۔",
                         ["8**2 + 14**2 == 260", near("sqrt(260)", "16.1", 1)])]), "$16.1$ cm", prompt="the distance $AF$"),
       P("ii", steps_of([(r"\sin\theta = \frac{AB}{AF} = \frac{8}{\sqrt{260}} \Rightarrow \theta \approx 29.7^\circ", "$AB$ is perpendicular to the plane $BCEF$.", "$AB$ مستوی $BCEF$ پر عمود ہے۔",
                          [near("asin(8/sqrt(260))*180/pi", "29.7", 1)])]), r"$29.7^\circ$", prompt="the angle between $AF$ and $BCEF$")], "Review 7")
single("rev7", 6, "Hashim walks 4 km due North, then turns and walks 3 km due East. What is the bearing from the starting point to his final position?", [
    (r"OP = \sqrt{4^2 + 3^2} = 5\ \text{km},\quad \tan\theta = \frac{3}{4} \Rightarrow \theta \approx 36.9^\circ", "Angle east of North.", "شمال سے مشرق کی طرف زاویہ۔",
     ["sqrt(4**2 + 3**2) == 5", near("atan(R(3,4))*180/pi", "36.9", 1)]),
    (r"\text{Bearing} \approx 037^\circ", "Measured clockwise from North, to the nearest degree.", "شمال سے گھڑی کی سمت، قریب ترین درجہ تک۔", [near("atan(R(3,4))*180/pi", "37", 0)])],
    r"$037^\circ$", exercise="Review 7")
single("rev7", 7, "A pilot flies 200 km on a bearing of $045^\\circ$, then turns and flies 150 km on a bearing of $135^\\circ$. How far is the plane from its original position?", [
    (r"\text{Angle} = 135^\circ - 45^\circ = 90^\circ", "The legs are at right angles.", "دونوں راستے قائمہ زاویے پر ہیں۔", ["135 - 45 == 90"]),
    (r"d^2 = 200^2 + 150^2 - 2(200)(150)\cos 90^\circ = 62500 \Rightarrow d = 250\ \text{km}", "Law of cosines.", "قانون جیب التمام۔",
     [f"200**2 + 150**2 - 2*200*150*cos({dg(90)}) == 62500", "sqrt(62500) == 250"])], "$250$ km", exercise="Review 7")


# ------------------------------------------------------------------------------------------ differences from the reference notes

ROUND = ("The reference notes round an intermediate value or the last digit differently; the value here is computed from the exact "
         "expression and rounded once.", "حوالہ نوٹس میں درمیانی قیمت یا آخری ہندسہ مختلف طریقے سے گول کیا گیا ہے؛ یہاں قیمت درست عبارت سے نکال کر ایک بار گول کی گئی ہے۔")
NOTES = {
    ("c10-ex7.2-q1", "i"): ("The reference notes give $c = 8.8$; $c = \\frac{6.1\\sin 70.9^\\circ}{\\sin 42^\\circ} = 8.6$ cm.",
                            "حوالہ نوٹس میں $c = 8.8$ ہے؛ درست $c = 8.6$ سینٹی میٹر ہے۔"),
    ("c10-ex7.2-q1", "ii"): ROUND,
    ("c10-ex7.2-q1", "iii"): ("The reference notes give $a = 6.61$; $a = \\frac{5.2\\sin 81.4^\\circ}{\\sin 50.6^\\circ} = 6.65$ cm.",
                              "حوالہ نوٹس میں $a = 6.61$ ہے؛ درست $a = 6.65$ سینٹی میٹر ہے۔"),
    ("c10-ex7.2-q1", "iv"): ("The reference notes give $c = 4.20$; $c = \\frac{4\\sin 57^\\circ}{\\sin 52^\\circ} = 4.26$ cm.",
                             "حوالہ نوٹس میں $c = 4.20$ ہے؛ درست $c = 4.26$ سینٹی میٹر ہے۔"),
    ("c10-ex7.2-q1", "v"): ROUND,
    ("c10-ex7.2-q1", "vii"): ROUND,
    ("c10-ex7.2-q1", "viii"): ("The reference notes give $c = 2.29$; $c = \\frac{12\\sin 11^\\circ}{\\sin 77^\\circ} = 2.35$ cm.",
                               "حوالہ نوٹس میں $c = 2.29$ ہے؛ درست $c = 2.35$ سینٹی میٹر ہے۔"),
    ("c10-ex7.2-q2", "ii"): ROUND,
    ("c10-ex7.2-q2", "iii"): ROUND,
    ("c10-ex7.2-q2", "iv"): ROUND,
}
for it in UNIT["items"]:
    for part in it["parts"]:
        note = NOTES.get((it["id"], part["label"]))
        if note:
            part["key_note"] = {"en": note[0], "ur": note[1]}
