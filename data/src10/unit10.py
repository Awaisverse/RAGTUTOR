"""Class 10, Unit 10 - Practical Geometry of Circles: Exercises 10.1-10.2 and Review Exercise 10.

Constructions are given as numbered steps, each drawn on the board from exact coordinates; the checks prove the construction works
(the centre is equidistant from the points, a tangent is perpendicular to the radius, the angle between tangents is 30 degrees).
Questions transcribed from the reference notes (data/class10/pages/u10_*.png); answers checked against data/answers10/unit10.json.
"""
import math

import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 10, "title": "Practical Geometry of Circles", "title_ur": "دائروں کی عملی جیومیٹری", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational
H = 60                      # figure height on the board


def pt(x, y):
    return [round(float(x), 2), round(float(y), 2)]


def circ(c, r):
    return {"t": "circle", "c": pt(*c), "r": round(float(r), 2)}


def line(a, b, dash=False):
    return {"t": "line", "p": pt(*a) + pt(*b), "dash": dash}


def lab(p, s, dx=1.5, dy=-2.5):
    return {"t": "text", "p": pt(p[0] + dx, p[1] + dy), "s": s}


def dot(p):
    return {"t": "dot", "p": pt(*p)}


def ext(a, b, k=1.6):
    """The segment ab extended both ways (to draw a full line)."""
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    return line((mx + (a[0] - mx) * k, my + (a[1] - my) * k), (mx + (b[0] - mx) * k, my + (b[1] - my) * k))


def on(c, r, deg):
    """Point on a circle at an angle (degrees, measured anticlockwise on the page)."""
    return (c[0] + r * math.cos(math.radians(deg)), c[1] - r * math.sin(math.radians(deg)))


def bisector(a, b, length=14):
    mx, my = (a[0] + b[0]) / 2, (a[1] + b[1]) / 2
    dx, dy = b[0] - a[0], b[1] - a[1]
    n = math.hypot(dx, dy)
    ux, uy = -dy / n, dx / n
    return line((mx - ux * length, my - uy * length), (mx + ux * length, my + uy * length), dash=True)


def step(math_, en, ur, *checks, draw=None):
    return S(math_, en, ur, *checks, draw=draw)


GIVEN = (r"Given and required.", r"دیا گیا اور مطلوب۔")


# ------------------------------------------------------------------------------------------ construction templates


def centre_by_bisectors(label, r_cm, prompt):
    """Draw a circle of radius r, then find its centre from two chords and their perpendicular bisectors."""
    s = 12                                   # board units per cm (r up to 2 cm fits)
    O = (50, 30)
    r = r_cm * s
    A, B = on(O, r, 200), on(O, r, 95)
    C, D = on(O, r, 75), on(O, r, -20)
    steps = [step(rf"r = {r_cm}\ \text{{cm}}", r"Mark a point $O$, open the compasses to the radius and draw the circle.",
                  r"نقطہ $O$ لگائیں، پرکار کو رداس کے برابر کھول کر دائرہ کھینچیں۔", draw=[circ(O, r)]),
             step(r"\text{Draw chords } AB \text{ and } CD", r"Draw any two chords that are not parallel.", r"کوئی دو غیر متوازی وتر کھینچیں۔",
                  draw=[line(A, B), line(C, D), lab(A, "A", -4, 1), lab(B, "B"), lab(C, "C"), lab(D, "D")]),
             step(r"\text{Perpendicular bisectors of } AB \text{ and } CD", r"With $A$ and $B$ as centres draw equal arcs (radius more than half of $AB$); join their crossings. Do the same for $CD$.",
                  r"$A$ اور $B$ کو مرکز بنا کر برابر قوسیں کھینچیں اور ان کے نقاط تقاطع ملائیں؛ $CD$ کے لیے بھی یہی کریں۔",
                  draw=[bisector(A, B), bisector(C, D)]),
             step(r"\text{The bisectors meet at } O", r"The perpendicular bisector of every chord passes through the centre, so they meet at the centre.",
                  r"ہر وتر کا عمودی ناصف مرکز سے گزرتا ہے، اس لیے یہ مرکز پر ملتے ہیں۔",
                  f"Abs(sqrt(({A[0]}-{O[0]})**2 + ({A[1]}-{O[1]})**2) - sqrt(({B[0]}-{O[0]})**2 + ({B[1]}-{O[1]})**2)) < 1e-6",
                  f"Abs(sqrt(({C[0]}-{O[0]})**2 + ({C[1]}-{O[1]})**2) - sqrt(({D[0]}-{O[0]})**2 + ({D[1]}-{O[1]})**2)) < 1e-6",
                  draw=[dot(O), lab(O, "O")]),
             step(rf"OA = OB = OC = OD = {r_cm}\ \text{{cm}}", r"Verify: the point found is the centre (it is the radius away from every point of the circle).",
                  r"تصدیق: یہ نقطہ دائرے کے ہر نقطے سے رداس کے فاصلے پر ہے، اس لیے یہی مرکز ہے۔")]
    return P(label, steps, f"circle of radius {r_cm} cm; its centre verified by perpendicular bisectors of two chords", prompt=prompt)


def circle_through(label, pts, names, prompt, intro=None):
    (ax, ay), (bx, by), (cx, cy) = pts
    d = 2 * (ax * (by - cy) + bx * (cy - ay) + cx * (ay - by))
    ux = ((ax * ax + ay * ay) * (by - cy) + (bx * bx + by * by) * (cy - ay) + (cx * cx + cy * cy) * (ay - by)) / d
    uy = ((ax * ax + ay * ay) * (cx - bx) + (bx * bx + by * by) * (ax - cx) + (cx * cx + cy * cy) * (bx - ax)) / d
    O = (ux, uy)
    r = math.hypot(ax - ux, ay - uy)
    A, B, C = pts
    a, b, c = names
    dist = lambda p: f"sqrt(({p[0]}-({ux}))**2 + ({p[1]}-({uy}))**2)"  # noqa: E731
    steps = []
    if intro:
        steps.append(T(*intro))
    steps += [step(rf"\text{{Join }} {a}{b} \text{{ and }} {b}{c}", r"Join the points to make two chords.", r"نقاط ملا کر دو وتر بنائیں۔",
                   draw=[dot(A), dot(B), dot(C), lab(A, a), lab(B, b), lab(C, c), line(A, B), line(B, C)]),
              step(rf"\text{{Perpendicular bisectors of }} {a}{b} \text{{ and }} {b}{c}", r"Construct the perpendicular bisector of each chord.", r"ہر وتر کا عمودی ناصف بنائیں۔",
                   draw=[bisector(A, B, 22), bisector(B, C, 22)]),
              step(r"\text{They meet at } O", r"$O$ is equally far from all three points.", r"$O$ تینوں نقاط سے برابر فاصلے پر ہے۔",
                   f"Abs({dist(A)} - {dist(B)}) < 1e-6", f"Abs({dist(B)} - {dist(C)}) < 1e-6", draw=[dot(O), lab(O, "O")]),
              step(rf"\text{{With centre }} O \text{{ and radius }} O{a} \text{{ draw the circle}}", r"The circle passes through all three points.", r"دائرہ تینوں نقاط سے گزرتا ہے۔",
                   draw=[circ(O, r)])]
    return P(label, steps, "the circle through the three points (centre where the perpendicular bisectors meet)", prompt=prompt)


def arc_without_centre(label, prompt):
    O, r = (50, 32), 22
    arc = {"t": "arc", "c": [50, 32], "r": 22, "a": [200, 340]}
    marks = [on(O, r, a) for a in range(160, -200, -30)]
    steps = [step(r"\text{Given arc } " + ("PQR" if "PQR" in prompt else "ABC"), r"Start from the given arc.", r"دی گئی قوس سے شروع کریں۔", draw=[arc]),
             step(r"\text{Mark equal chords along the arc}", r"Keep the compasses at a fixed small opening; from one end step along the arc marking equal chords.",
                  r"پرکار کو ایک ہی چھوٹے فاصلے پر رکھیں؛ قوس پر برابر وتر لگاتے جائیں۔", draw=[dot(p) for p in marks[:6]]),
             step(r"\text{Continue the equal steps beyond the arc}", r"Equal chords subtend equal angles, so the steps keep to the same circle; carry on until you come back to the start.",
                  r"برابر وتر برابر زاویے بناتے ہیں، اس لیے یہ قدم اسی دائرے پر رہتے ہیں؛ شروع تک واپس آنے تک جاری رکھیں۔", draw=[dot(p) for p in marks[6:]]),
             step(r"\text{Join the points smoothly}", r"Join all the marked points with a smooth curve: the circle is complete without finding its centre.",
                  r"تمام نقاط کو ہموار خم سے ملائیں: مرکز معلوم کیے بغیر دائرہ مکمل ہو گیا۔", draw=[circ(O, r)])]
    return P(label, steps, "circle completed by stepping equal chords (no centre needed)", prompt=prompt)


def tangent_at_point(label, r_cm, prompt):
    s = 14 if r_cm <= 2.2 else 10
    O, r = (40, 30), r_cm * s
    Pp = (O[0] + r, O[1])
    steps = [step(rf"r = {r_cm}\ \text{{cm}}", r"Draw the circle with centre $O$ and mark $P$ on it.", r"مرکز $O$ سے دائرہ کھینچیں اور اس پر $P$ لگائیں۔",
                  draw=[circ(O, r), dot(O), lab(O, "O"), dot(Pp), lab(Pp, "P")]),
             step(r"\text{Join } OP", r"Draw the radius $OP$.", r"رداس $OP$ کھینچیں۔", draw=[line(O, Pp)]),
             step(r"\text{At } P \text{ draw } AB \perp OP", r"Construct a line through $P$ perpendicular to $OP$ (bisect the straight angle at $P$).",
                  r"$P$ سے $OP$ پر عمود خط کھینچیں۔", f"({Pp[0]}-{O[0]})*0 + ({Pp[1]}-{O[1]})*1 == 0",
                  draw=[line((Pp[0], Pp[1] - 20), (Pp[0], Pp[1] + 20)), {"t": "right", "p": pt(*Pp), "d": [-1, 0, 0, -1]}, lab((Pp[0], Pp[1] - 18), "A"), lab((Pp[0], Pp[1] + 18), "B")]),
             step(r"AB \text{ is the tangent at } P", r"A line perpendicular to the radius at its end touches the circle at exactly one point.",
                  r"رداس کے سرے پر عمود خط دائرے کو صرف ایک نقطے پر چھوتا ہے۔")]
    return P(label, steps, f"tangent at $P$ perpendicular to $OP$ (radius {r_cm} cm)", prompt=prompt)


def tangent_from_outside(label, r_cm, d_cm, prompt):
    s = 80 / (d_cm + r_cm + 0.6)
    s = min(s, 14)
    O = (10 + r_cm * s, 30)
    r, d = r_cm * s, d_cm * s
    Pp = (O[0] + d, O[1])
    M = ((O[0] + Pp[0]) / 2, O[1])
    a = math.degrees(math.acos(r / d))
    Tp, Sp = on(O, r, a), on(O, r, -a)
    L = math.sqrt(d_cm ** 2 - r_cm ** 2)
    steps = [step(rf"r = {r_cm}\ \text{{cm}},\quad OP = {d_cm}\ \text{{cm}}", r"Draw the circle and the point $P$ outside it; join $OP$.", r"دائرہ اور اس کے باہر نقطہ $P$ لگائیں؛ $OP$ ملائیں۔",
                  draw=[circ(O, r), dot(O), lab(O, "O"), dot(Pp), lab(Pp, "P"), line(O, Pp)]),
             step(r"\text{Bisect } OP \text{ at } M", r"Construct the perpendicular bisector of $OP$; it cuts $OP$ at its midpoint $M$.", r"$OP$ کا عمودی ناصف بنائیں؛ یہ $OP$ کو $M$ پر کاٹتا ہے۔",
                  draw=[bisector(O, Pp, 12), dot(M), lab(M, "M", 1, 4)]),
             step(r"\text{Circle with centre } M \text{ and radius } MO", r"It cuts the given circle at $T$ and $S$.", r"یہ دیے گئے دائرے کو $T$ اور $S$ پر کاٹتا ہے۔",
                  draw=[{"t": "arc", "c": pt(*M), "r": round(d / 2, 2), "a": [180, 360]}, {"t": "arc", "c": pt(*M), "r": round(d / 2, 2), "a": [0, 180]},
                        dot(Tp), dot(Sp), lab(Tp, "T", 0, -3), lab(Sp, "S", 0, 5)]),
             step(r"\text{Join } PT \text{ and } PS", r"$\angle OTP$ is an angle in a semicircle (on diameter $OP$), so $OT \perp PT$: $PT$ and $PS$ are the tangents.",
                  r"$\angle OTP$ نصف دائرے کا زاویہ ہے، اس لیے $OT \perp PT$: $PT$ اور $PS$ مماس ہیں۔",
                  f"Abs(({Tp[0]}-{O[0]})*({Pp[0]}-{Tp[0]}) + ({Tp[1]}-{O[1]})*({Pp[1]}-{Tp[1]})) < 1e-6",
                  draw=[ext(Pp, Tp, 1.15), ext(Pp, Sp, 1.15)]),
             step(rf"PT = PS = \sqrt{{OP^2 - r^2}} = \sqrt{{{d_cm}^2 - {r_cm}^2}} \approx {L:.2f}\ \text{{cm}}", r"Both tangents have the same length (Pythagoras in $OTP$).",
                  r"دونوں مماس برابر ہیں (مثلث $OTP$ میں فیثا غورث)۔", f"Abs(sqrt(({d_cm})**2 - ({r_cm})**2) - {L:.2f}) <= 0.005")]
    return P(label, steps, f"tangents $PT$ and $PS$ from $P$, each $\\approx {L:.2f}$ cm", prompt=prompt)


def tangents_at_angle(label, r_cm, ang, prompt):
    s = 7 if r_cm > 1.8 else 9
    O, r = (68, 30), r_cm * s
    half = (180 - ang) / 2                   # angle AOP
    A, B = on(O, r, 180 - half), on(O, r, 180 + half)
    dist = r / math.cos(math.radians(half))
    Pp = (O[0] - dist, O[1])
    steps = [step(rf"r = {r_cm}\ \text{{cm}}", r"Draw the circle with centre $O$.", r"مرکز $O$ سے دائرہ کھینچیں۔", draw=[circ(O, r), dot(O), lab(O, "O")]),
             step(rf"\angle AOB = 180^\circ - {ang}^\circ = {180 - ang}^\circ", r"In quadrilateral $OAPB$ the angles at $A$ and $B$ are $90^\circ$, so $\angle AOB + \angle APB = 180^\circ$.",
                  r"چوکور $OAPB$ میں $A$ اور $B$ پر زاویے $90^\circ$ ہیں، اس لیے $\angle AOB + \angle APB = 180^\circ$۔", f"360 - 90 - 90 - {ang} == {180 - ang}",
                  draw=[line(O, A), line(O, B), lab(A, "A", -1, -3), lab(B, "B", -1, 5)]),
             step(r"\text{At } A \text{ and } B \text{ draw perpendiculars to } OA, OB", r"These are the tangents at $A$ and $B$; let them meet at $P$.", r"یہ $A$ اور $B$ پر مماس ہیں؛ یہ $P$ پر ملتے ہیں۔",
                  draw=[ext(Pp, A, 1.2), ext(Pp, B, 1.2), dot(Pp), lab(Pp, "P", -3, -3)]),
             step(rf"\angle APB = {ang}^\circ", r"Check: the angle between the two tangents.", r"جانچ: دونوں مماسوں کے درمیان زاویہ۔",
                  f"Abs(acos((({A[0]}-({Pp[0]}))*({B[0]}-({Pp[0]})) + ({A[1]}-({Pp[1]}))*({B[1]}-({Pp[1]})))/(sqrt(({A[0]}-({Pp[0]}))**2+({A[1]}-({Pp[1]}))**2)*sqrt(({B[0]}-({Pp[0]}))**2+({B[1]}-({Pp[1]}))**2)))*180/pi - {ang}) < 1e-6",
                  f"Abs(({A[0]}-{O[0]})*(({Pp[0]})-{A[0]}) + ({A[1]}-{O[1]})*(({Pp[1]})-{A[1]})) < 1e-6")]
    return P(label, steps, f"tangents $PA$ and $PB$ meeting at ${ang}^\\circ$ ($\\angle AOB = {180 - ang}^\\circ$)", prompt=prompt)


def tangent_at_endpoint(label, prompt):
    O, r = (50, 30), 22
    Pp = on(O, r, 120)
    t = (math.sin(math.radians(120)), math.cos(math.radians(120)))
    steps = [step(r"\text{Given arc } PQR \text{ with } P \text{ an endpoint}", r"Find the centre $O$ (perpendicular bisectors of two chords) if it is not given.",
                  r"اگر مرکز نہ دیا ہو تو دو وتروں کے عمودی ناصف سے $O$ معلوم کریں۔", draw=[{"t": "arc", "c": [50, 30], "r": 22, "a": [-60, 240]}, dot(Pp), lab(Pp, "P"), dot(O), lab(O, "O")]),
             step(r"\text{Join } OP", r"Draw the radius to $P$.", r"$P$ تک رداس کھینچیں۔", draw=[line(O, Pp)]),
             step(r"\text{At } P \text{ draw a line } \perp OP", r"The perpendicular to the radius at $P$ is the tangent.", r"$P$ پر رداس کا عمود ہی مماس ہے۔",
                  f"Abs(({Pp[0]}-{O[0]})*({t[0]:.12f}) + ({Pp[1]}-{O[1]})*({t[1]:.12f})) < 1e-6",
                  draw=[line((Pp[0] - 18 * t[0], Pp[1] - 18 * t[1]), (Pp[0] + 18 * t[0], Pp[1] + 18 * t[1]))])]
    return P(label, steps, "tangent at $P$ perpendicular to $OP$", prompt=prompt)


def tangent_at_midpoint(label, prompt):
    O, r = (50, 40), 26
    A, B = on(O, r, 150), on(O, r, 30)
    Pp = on(O, r, 90)
    steps = [step(r"\text{Join } AB", r"Join the ends of the arc $APB$.", r"قوس $APB$ کے سرے ملائیں۔",
                  draw=[{"t": "arc", "c": [50, 40], "r": 26, "a": [210, 330]}, line(A, B), lab(A, "A", -4, 1), lab(B, "B"), dot(Pp), lab(Pp, "P", 1, -3)]),
             step(r"\text{Perpendicular bisector of } AB \text{ passes through } P", r"Its foot is the midpoint of $AB$ and it meets the arc at its midpoint $P$.",
                  r"یہ $AB$ کے وسط سے گزرتا ہے اور قوس کو اس کے وسط $P$ پر ملتا ہے۔", draw=[bisector(A, B, 16)]),
             step(r"\text{At } P \text{ draw } CD \perp \text{the bisector, i.e. } CD \parallel AB", r"This line is perpendicular to the radius through $P$, so it is the tangent.",
                  r"یہ خط $P$ والے رداس پر عمود ہے، اس لیے مماس ہے۔", f"Abs(({A[1]}) - ({B[1]})) < 1e-6",
                  draw=[line((Pp[0] - 20, Pp[1]), (Pp[0] + 20, Pp[1])), lab((Pp[0] - 20, Pp[1]), "C", -2, -2), lab((Pp[0] + 20, Pp[1]), "D")])]
    return P(label, steps, "tangent $CD$ at $P$, parallel to $AB$", prompt=prompt)


# ------------------------------------------------------------------------------------------ Exercise 10.1

ex("ex10.1", 1, r"Construct a circle with the help of given radius and verify its centre by construction: (i) $r = 1.5$ cm (ii) $r = 1.7$ cm (iii) $r = 2$ cm", [
    centre_by_bisectors("i", 1.5, r"$r = 1.5$ cm"), centre_by_bisectors("ii", 1.7, r"$r = 1.7$ cm"), centre_by_bisectors("iii", 2, r"$r = 2$ cm")], "10.1", figure_h=H)
ex("ex10.1", 2, "Take any three non-collinear points $P$, $Q$, $R$ and construct a circle passing through these points.",
   [circle_through("", [(30, 45), (50, 15), (72, 42)], "PQR", "")], "10.1", figure_h=H)
ex("ex10.1", 3, "Draw an arc $ABC$ and complete a circle by finding its centre.",
   [circle_through("", [(28, 38), (50, 12), (72, 38)], "ABC", "", intro=(r"Take three points $A$, $B$, $C$ on the arc.", r"قوس پر تین نقاط $A$، $B$، $C$ لیں۔"))], "10.1", figure_h=H)
ex("ex10.1", 4, "Draw an arc $PQR$ and complete a circle without finding its centre.", [arc_without_centre("", "arc PQR")], "10.1", figure_h=H)
ex("ex10.1", 5, "Take any three non-collinear points (locations of the lamp posts in the park), construct a circle passing through all these points.",
   [circle_through("", [(32, 44), (48, 14), (70, 40)], "ABC", "")], "10.1", figure_h=H)
ex("ex10.1", 6, "A part of the Ferris wheel rim is visible as an arc. Using any three points on the arc, construct the circle by finding its centre.",
   [circle_through("", [(30, 40), (50, 13), (70, 40)], "ABC", "", intro=(r"Mark any three points $A$, $B$, $C$ on the arc.", r"قوس پر کوئی تین نقاط لگائیں۔"))], "10.1", figure_h=H)
ex("ex10.1", 7, "$ABC$ an arc of a fountain, complete a circle without finding its centre.", [arc_without_centre("", "arc ABC")], "10.1", figure_h=H)

# ------------------------------------------------------------------------------------------ Exercise 10.2

ex("ex10.2", 1, r"Draw tangent to $\widehat{APB}$ at point $P$, when $P$ is midpoint of the arc.", [tangent_at_midpoint("", "")], "10.2", figure_h=H)
ex("ex10.2", 2, r"Draw tangent to $\widehat{PQR}$ at point $P$, when $P$ is endpoint of the arc.", [tangent_at_endpoint("", "")], "10.2", figure_h=H)
ex("ex10.2", 3, r"Draw tangent to $\widehat{ABC}$ from a point $P$, when $P$ is outside the arc.", [tangent_from_outside("", 1.5, 4, "")], "10.2", figure_h=H)
UNIT["items"][-1]["parts"][0]["answer"] = "tangents $PT$ and $PS$ from $P$"
ex("ex10.2", 4, "Draw a circle of radius 1.3 cm and draw a tangent at point $P$, when $P$ lies on its circumference.", [tangent_at_point("", 1.3, "")], "10.2", figure_h=H)
ex("ex10.2", 5, "Draw a circle of radius 1.5 cm and draw a tangent at point $P$, when $P$ is at a distance of 8 cm from its centre.", [tangent_from_outside("", 1.5, 8, "")], "10.2", figure_h=H)
ex("ex10.2", 6, r"Draw a circle of radius 1.6 cm. Draw two tangents that meet an angle of $30^\circ$.", [tangents_at_angle("", 1.6, 30, "")], "10.2", figure_h=H)
ex("ex10.2", 7, "Draw a tangent to any point on a circular part of the track having radius = 2 cm.", [tangent_at_point("", 2, "")], "10.2", figure_h=H)
ex("ex10.2", 8, r"From a pulley point, construct two tangents to a machine wheel having $r = 2.1$ cm, such that the angle between them is $30^\circ$.",
   [tangents_at_angle("", 2.1, 30, "")], "10.2", figure_h=H)

# ------------------------------------------------------------------------------------------ Review Exercise 10

q1 = [mcq("i", r"In the adjacent figure, $\overleftrightarrow{ABC}$ (touching the circle at $B$) is:", [r"\text{a chord}", r"\text{an arc}", r"\text{a tangent}", r"\text{a secant}"], 2,
          [T(r"It touches the circle at one point only.", r"یہ دائرے کو صرف ایک نقطے پر چھوتا ہے۔")]),
      mcq("ii", "There are ______ types of arcs.", ["2", "3", "4", "5"], 0, [T(r"Minor and major arcs.", r"چھوٹی اور بڑی قوس۔")]),
      mcq("iii", "Right bisector of the chord of a circle always passes through the:", [r"\text{diameter}", r"\text{non-collinear points}", r"\text{radius}", r"\text{centre}"], 3,
          [T(r"It passes through the centre.", r"یہ مرکز سے گزرتا ہے۔")]),
      mcq("iv", "A circle has only one:", [r"\text{chord}", r"\text{centre}", r"\text{diameter}", r"\text{secant}"], 1, [T(r"Exactly one centre.", r"صرف ایک مرکز۔")]),
      mcq("v", "The point where two tangents meet outside a circle forms:", [r"\text{a semicircle}", r"\text{a diameter}", r"\text{a radius}", r"\text{an angle}"], 3,
          [T(r"The two tangents make an angle at that point.", r"دونوں مماس اس نقطے پر زاویہ بناتے ہیں۔")]),
      mcq("vi", "Two equal tangents from a point to a circle can be drawn when the point is ______ the circle.", [r"\text{on}", r"\text{inside}", r"\text{outside}", r"\text{at centre of}"], 2,
          [T(r"Only from an outside point.", r"صرف بیرونی نقطے سے۔")]),
      mcq("vii", "Tangents drawn from a single external point to a circle are:", [r"\text{unequal in length}", r"\text{perpendicular to each other}", r"\text{equal in length}",
                                                                                  r"\text{inside the circle}"], 2, [T(r"They are equal in length.", r"ان کی لمبائی برابر ہوتی ہے۔")]),
      mcq("viii", "At least how many chords are needed to locate the centre of the circle?", ["1", "2", "3", "4"], 1,
          [T(r"Two perpendicular bisectors meet at the centre.", r"دو عمودی ناصف مرکز پر ملتے ہیں۔")]),
      mcq("ix", "To draw a tangent at middle point of an arc, first step is to:", [r"\text{join endpoints of an arc}", r"\text{draw radius}", r"\text{draw a line perpendicular to chord}",
                                                                                 r"\text{draw an angle}"], 0, [T(r"First join the ends of the arc.", r"پہلے قوس کے سرے ملائیں۔")]),
      mcq("x", "The angle between the radius and a tangent at the point of contact is:", [r"30^\circ", r"60^\circ", r"90^\circ", r"120^\circ"], 2,
          [T(r"Radius and tangent are perpendicular.", r"رداس اور مماس عمود ہوتے ہیں۔")])]
ex("rev10", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 10")
ex("rev10", 2, "Draw a circle of radius 1.4 cm and draw a tangent at point $P$, when $P$ lies on its circumference.", [tangent_at_point("", 1.4, "")], "Review 10", figure_h=H)
ex("rev10", 3, "Draw a circle of radius 1.2 cm and draw a tangent at point $P$, when $P$ is at a distance of 5 cm from the centre.", [tangent_from_outside("", 1.2, 5, "")], "Review 10", figure_h=H)
ex("rev10", 4, r"Draw a circle of radius 1.7 cm. Draw two tangents that meet an angle of $30^\circ$.", [tangents_at_angle("", 1.7, 30, "")], "Review 10", figure_h=H)
ex("rev10", 5, "Take a part of the circular track, use chords and perpendicular bisectors to complete a circular track.",
   [circle_through("", [(28, 38), (50, 14), (72, 38)], "ABC", "", intro=(r"Mark three points $A$, $B$, $C$ on the given part of the track.", r"ٹریک کے حصے پر تین نقاط لگائیں۔"))],
   "Review 10", figure_h=H)
ex("rev10", 6, r"Two decorative fences touch the circular flower bed of radius 2.1 cm and meet outside it at an angle of $30^\circ$ to form an entrance arch. Draw two tangents to the flower bed "
   r"from the point where the fences meet at an angle of $30^\circ$.", [tangents_at_angle("", 2.1, 30, "")], "Review 10", figure_h=H)
