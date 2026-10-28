"""Class 10, Unit 8 - Chords and Arcs of a Circle: Exercises 8.1-8.2 and Review Exercise 8.

Questions transcribed from the reference notes (data/class10/pages/u08_*.png); lengths are checked with sympy (exact surds, and the
decimal value to the stated rounding); answers are checked against data/answers10/unit08.json.
Ex 8.2 Q2 and Q3: the notes' working contradicts their boxed answers; recorded with key_note.
"""
import math

import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 8, "title": "Chords and Arcs of a Circle", "title_ur": "دائرے کے وتر اور قوسیں", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational


def near(expr, value, k):
    return f"Abs(({expr}) - {value}) <= {0.5 * 10 ** (-k) + 1e-9}"


def chord_fig(half_ratio, labels=("A", "B"), show_r=True):
    """Circle of radius 25 at (50, 30); a horizontal chord whose half-length is half_ratio * r, its perpendicular from O."""
    r, cx, cy = 25, 50, 30
    h = max(0.15, min(0.97, half_ratio)) * r
    d = math.sqrt(r * r - h * h)
    y = cy + d
    out = [{"t": "circle", "c": [cx, cy], "r": r}, {"t": "dot", "p": [cx, cy]}, {"t": "text", "p": [cx + 1.5, cy - 2], "s": "O"},
           {"t": "line", "p": [cx - h, y, cx + h, y]}, {"t": "text", "p": [cx - h - 4, y + 1], "s": labels[0]}, {"t": "text", "p": [cx + h + 1.5, y + 1], "s": labels[1]},
           {"t": "line", "p": [cx, cy, cx, y], "dash": True}, {"t": "right", "p": [cx, y], "d": [1, 0, 0, -1]}, {"t": "text", "p": [cx + 1.5, y + 4], "s": "M"}]
    if show_r:
        out.append({"t": "line", "p": [cx, cy, cx + h, y]})
    return out


def chord_q(eid, n, question, rows, answer, half_ratio, exercise, note=None):
    steps = [S("", "Draw $OM$ perpendicular to the chord: it bisects the chord, and $OM$, half the chord and the radius form a right triangle.",
               "$OM$ کو وتر پر عمود کھینچیں: یہ وتر کی تنصیف کرتا ہے؛ $OM$، آدھا وتر اور رداس قائمہ مثلث بناتے ہیں۔", draw=chord_fig(half_ratio))]
    steps += [S(t, en, ur, *c) for t, en, ur, c in rows]
    p = P("", steps, answer)
    if note:
        p["key_note"] = note
    ex(eid, n, question, [p], exercise, figure_h=60)


def simple(eid, n, question, rows, answer, exercise, note=None):
    p = P("", [S(t, en, ur, *c) for t, en, ur, c in rows], answer)
    if note:
        p["key_note"] = note
    ex(eid, n, question, [p], exercise)


PY = ("Pythagoras in the right triangle $OMA$: $r^2 = OM^2 + AM^2$.", "قائمہ مثلث $OMA$ میں فیثا غورث: $r^2 = OM^2 + AM^2$۔")

# ------------------------------------------------------------------------------------------ Exercise 8.1

chord_q("ex8.1", 1, "Calculate the length of a chord which stands at a distance of 5 cm from the centre of a circle whose radius is 13 cm.", [
    (r"AM = \sqrt{r^2 - d^2} = \sqrt{13^2 - 5^2} = \sqrt{144} = 12", *PY, ["sqrt(13**2 - 5**2) == 12"]),
    (r"\text{Chord} = 2 \times AM = 2 \times 12 = 24\ \text{cm}", "The perpendicular bisects the chord.", "عمود وتر کی تنصیف کرتا ہے۔", ["2*sqrt(13**2 - 5**2) == 24"])],
    "$24$ cm", 12 / 13, "8.1")
simple("ex8.1", 2, "In construction, three steel rods are fixed at points $A$, $B$, and $C$ (not in a straight line). A circular hoop needs to pass through all three. How many hoops can be used?", [
    (r"\text{Number of hoops} = 1", "Three non-collinear points determine exactly one circle (its centre is where the perpendicular bisectors meet).",
     "تین غیر ہم خط نقاط سے صرف ایک دائرہ گزرتا ہے۔", [])], "1 hoop", "8.1")
chord_q("ex8.1", 3, "In a park, lamp posts are 14 m apart on the edge of a circular part of radius 10 m as shown in figure. Find the distance of the chord from the centre of the park.", [
    (r"d = \sqrt{r^2 - \left(\frac{\text{chord}}{2}\right)^2} = \sqrt{10^2 - 7^2} = \sqrt{51} \approx 7.14\ \text{m}", *PY, ["10**2 - 7**2 == 51", near("sqrt(51)", "7.14", 2)])],
    r"$\sqrt{51} \approx 7.14$ m", 0.7, "8.1")
simple("ex8.1", 4, "In a circle, chords $AB$ and $CD$ both have length 10 cm. If the distance from the centre to $\\overline{AB}$ is 6 cm, what is the distance from centre to $\\overline{CD}$?", [
    (r"d_{CD} = d_{AB} = 6\ \text{cm}", "Equal chords of a circle are equidistant from the centre.", "دائرے کے برابر وتر مرکز سے برابر فاصلے پر ہوتے ہیں۔", [])], "$6$ cm", "8.1")
chord_q("ex8.1", 5, "Two holes $A$ and $B$ are drilled 12 cm apart on a circular tabletop of radius 10 cm. Find the perpendicular distance from the centre to $AB$.", [
    (r"d = \sqrt{10^2 - 6^2} = \sqrt{100 - 36} = \sqrt{64} = 8\ \text{cm}", *PY, ["sqrt(10**2 - 6**2) == 8"])], "$8$ cm", 0.6, "8.1")
chord_q("ex8.1", 6, "A chord 8 cm long is at a distance of 3 cm from the centre. Calculate the radius of the circle.", [
    (r"r = \sqrt{d^2 + \left(\frac{\text{chord}}{2}\right)^2} = \sqrt{3^2 + 4^2} = \sqrt{25} = 5\ \text{cm}", *PY, ["sqrt(3**2 + 4**2) == 5"])], "$5$ cm", 0.8, "8.1")
simple("ex8.1", 7, r"In the given figure, $m\overline{CD} = 121$ units and $m\overline{BC} = 3x$ units. Find the value of $x$.", [
    (r"m\overline{BC} = \frac{1}{2}m\overline{CD} \Rightarrow 3x = \frac{1}{2}(121)", "In the figure $AB$ (through the centre) is perpendicular to the chord $CD$ at $B$, "
     "so $B$ is the midpoint of $CD$.", "شکل میں مرکز سے گزرنے والا خط وتر $CD$ پر $B$ پر عمود ہے، اس لیے $B$ وتر کا وسطی نقطہ ہے۔", []),
    (r"x = \frac{121}{6} \approx 20.17\ \text{units}", "Solve.", "حل کریں۔", ["3*R(121,6) == R(121,2)", near("R(121,6)", "20.17", 2)])], r"$x = \frac{121}{6} \approx 20.17$", "8.1")
chord_q("ex8.1", 8, "In a circle with centre at $O$, the perpendicular distance of the each chord $PQ$ and $RS$ from the centre is 6 cm. If the length of chord $PQ$ is 18 cm, find the length of the other chord.", [
    (r"r^2 = d^2 + \left(\frac{PQ}{2}\right)^2 = 6^2 + 9^2 = 117", *PY, ["6**2 + 9**2 == 117"]),
    (r"RS = 2\sqrt{r^2 - d^2} = 2\sqrt{117 - 36} = 2\sqrt{81} = 18\ \text{cm}", "Chords at the same distance from the centre are equal.", "مرکز سے برابر فاصلے پر وتر برابر ہوتے ہیں۔",
     ["2*sqrt(117 - 36) == 18"])], "$18$ cm", 0.83, "8.1")
chord_q("ex8.1", 9, "A line from the centre of a circle cuts a 10 cm chord at right angle where radius of the circle is 6 cm. What is the length from the centre to the chord?", [
    (r"d = \sqrt{6^2 - 5^2} = \sqrt{36 - 25} = \sqrt{11} \approx 3.32\ \text{cm}", *PY, ["6**2 - 5**2 == 11", near("sqrt(11)", "3.32", 2)])], r"$\sqrt{11} \approx 3.32$ cm", 5 / 6, "8.1")
simple("ex8.1", 10, r"In a circle, a perpendicular is drawn from the centre to chord $AB$. If $m\overline{AB} = 12$ cm, what is the length of each segment after bisecting?", [
    (r"\frac{12}{2} = 6\ \text{cm}", "The perpendicular from the centre bisects the chord.", "مرکز سے عمود وتر کی تنصیف کرتا ہے۔", ["12/2 == 6"])], "$6$ cm", "8.1")

# ------------------------------------------------------------------------------------------ Exercise 8.2

simple("ex8.2", 1, r"In the given figure, if $m\overline{PQ} = m\overline{QR} = m\overline{RS} = m\overline{ST}$ and $m\angle POT = 70^\circ$, then find the value of $x$ "
       r"($x = m\angle TOR$, the angle at the centre over the two chords $TS$ and $SR$).", [
    (r"\angle POQ = \angle QOR = \angle ROS = \angle SOT = \theta", "Equal chords subtend equal central angles.", "برابر وتر مرکز پر برابر زاویے بناتے ہیں۔", []),
    (r"70^\circ + 4\theta = 360^\circ \Rightarrow 4\theta = 290^\circ \Rightarrow \theta = 72.5^\circ", r"The angles round the centre add to $360^\circ$.",
     r"مرکز کے گرد زاویوں کا مجموعہ $360^\circ$ ہے۔", ["(360 - 70)/R(4) == R(145,2)"]),
    (r"x = \angle TOS + \angle SOR = 2\theta = 145^\circ", "$x$ covers two of the equal angles.", "$x$ دو برابر زاویوں پر مشتمل ہے۔", ["2*R(145,2) == 145"])],
    r"$x = 145^\circ$", "8.2")
simple("ex8.2", 2, r"In the given figure, find the values of $x$ and $y$ ($\angle AOB = 80^\circ$ with arc $AB = 6$ cm, $\angle BOC = x$ with arc $BC = 2$ cm, $\angle COD = 52^\circ$ with arc $CD = y$ cm).", [
    (r"\frac{\text{arc}}{\text{angle}} \text{ is the same for every arc of the circle}", "In one circle, arcs are proportional to their central angles.",
     "ایک ہی دائرے میں قوسیں اپنے مرکزی زاویوں کے متناسب ہوتی ہیں۔", []),
    (r"\frac{6}{80} = \frac{2}{x} \Rightarrow x = \frac{80 \times 2}{6} \approx 26.67^\circ", "Arc $BC$.", "قوس $BC$۔", [near("R(160,6)", "26.67", 2)]),
    (r"\frac{6}{80} = \frac{y}{52} \Rightarrow y = \frac{6 \times 52}{80} = 3.9\ \text{cm}", "Arc $CD$.", "قوس $CD$۔", ["R(6*52,80) == R(39,10)"])],
    r"$x \approx 26.67^\circ,\ y = 3.9$ cm", "8.2",
    note={"en": "The reference notes find $x = 26.67^\\circ$ and $y = 3.9$ cm in the working but box $x = 77^\\circ$, $y = 6$ cm; the box does not follow from the working.",
          "ur": "حوالہ نوٹس میں حل سے $x = 26.67^\\circ$ اور $y = 3.9$ آتا ہے مگر جواب $77^\\circ$ اور 6 لکھا ہے۔"})
simple("ex8.2", 3, r"Find the values of $x$ and $y$ in the given figure, such that $m\widehat{AB} = m\widehat{BD}$ (arc $AB = 3$ cm, $\angle AOB = 140^\circ$ as in the notes, $x = \angle AOD$, arc $BD = y$ cm).", [
    (r"m\widehat{AB} = m\widehat{BD} \Rightarrow \angle AOB = \angle BOD = 140^\circ", "Equal arcs subtend equal central angles.", "برابر قوسیں مرکز پر برابر زاویے بناتی ہیں۔", []),
    (r"x + 140^\circ + 140^\circ = 360^\circ \Rightarrow x = 80^\circ", "Angles round the centre.", "مرکز کے گرد زاویے۔", ["360 - 280 == 80"]),
    (r"y = \text{arc } BD = \text{arc } AB = 3\ \text{cm}", "Equal central angles subtend equal arcs.", "برابر مرکزی زاویے برابر قوسیں بناتے ہیں۔", [])],
    r"$x = 80^\circ,\ y = 3$ cm", "8.2",
    note={"en": "The reference notes' working gives $x = 80^\\circ$ and $y = 3$ cm but the boxed answer says $x = 28^\\circ$, $y = 4$ cm.",
          "ur": "حوالہ نوٹس کے حل سے $x = 80^\\circ$ اور $y = 3$ آتا ہے مگر جواب $28^\\circ$ اور 4 لکھا ہے۔"})
simple("ex8.2", 4, "Two congruent arcs in a circular track subtend angles of $60^\\circ$ each at the centre. If the length of one chord of the circle is 10 metres, what is the length of other chord?", [
    (r"\text{Other chord} = 10\ \text{m}", "Congruent arcs (equal central angles) subtend equal chords.", "متماثل قوسیں برابر وتر بناتی ہیں۔", [])], "$10$ m", "8.2")
simple("ex8.2", 5, "In a circular fountain, two water jets spray along arcs of equal length. If chord $PQ$ is 12 metres, what is the length of chord $RS$ for the congruent arc $RS$?", [
    (r"\widehat{RS} \cong \widehat{PQ} \Rightarrow RS = PQ = 12\ \text{m}", "Equal arcs subtend equal chords.", "برابر قوسیں برابر وتر بناتی ہیں۔", [])], "$12$ m", "8.2")
simple("ex8.2", 6, r"In a circular park, two walkways $\overline{AB}$ and $\overline{CD}$ are both straight paths (chords) of length 14 metres. What can be said about the minor arcs subtended by these walkways?", [
    (r"AB = CD \Rightarrow \widehat{AB} \cong \widehat{CD}", "Equal chords subtend equal (minor) arcs.", "برابر وتر برابر (چھوٹی) قوسیں بناتے ہیں۔", [])],
    "the minor arcs are congruent", "8.2")
simple("ex8.2", 7, "In two congruent circular clocks, the minute hand points from the centre to the 3 on both. A decorative string connects 3 to 9 on both clocks. Are the arcs from 3 to 9 on both clocks congruent?", [
    (r"\text{Yes}", "Both clocks are congruent circles and 3, 9 are in corresponding positions (each arc is half the circle).",
     "دونوں گھڑیاں متماثل دائرے ہیں اور 3 اور 9 ایک جیسی جگہوں پر ہیں۔", [])], "yes, the arcs are congruent", "8.2")

# ------------------------------------------------------------------------------------------ Review Exercise 8

q1 = [mcq("i", "Distance of a point on the circumference to the centre of the circle is called:", [r"\text{radius}", r"\text{arc}", r"\text{chord}", r"\text{tangent}"], 0,
          [T("Centre to circumference is a radius.", "مرکز سے محیط تک کا فاصلہ رداس ہے۔")]),
      mcq("ii", "Radii of same circles are:", [r"\text{all unequal}", r"\text{all equal}", r"\text{half of each chord}", r"\text{double of the diameter}"], 1,
          [T("Every radius of a circle has the same length.", "دائرے کے سب رداس برابر ہوتے ہیں۔")]),
      mcq("iii", "The boundary of the circle is called:", [r"\text{chord}", r"\text{segment}", r"\text{circumference}", r"\text{diameter}"], 2,
          [T("The boundary is the circumference.", "حد محیط کہلاتی ہے۔")]),
      mcq("iv", "Any part of a circumference is called:", [r"\text{chord}", r"\text{diameter}", r"\text{radius}", r"\text{arc}"], 3, [T("Part of the circumference is an arc.", "محیط کا حصہ قوس ہے۔")]),
      mcq("v", "A chord passing through the centre of the circle is called:", [r"\text{radius}", r"\text{diameter}", r"\text{secant}", r"\text{circumference}"], 1,
          [T("The longest chord, through the centre, is a diameter.", "مرکز سے گزرنے والا وتر قطر ہے۔")]),
      mcq("vi", "In the given figure, what is $AB$?", [r"\text{diameter}", r"\text{tangent}", r"\text{chord}", r"\text{arc}"], 3, [T("As marked in the book's figure.", "کتاب کی شکل کے مطابق۔")]),
      mcq("vii", "In the given figure, major arc is:", [r"m\widehat{AB}", r"m\widehat{BC}", r"m\widehat{BDC}", r"m\widehat{AD}"], 2,
          [T("The major arc goes the long way round, through a third point.", "بڑی قوس لمبے راستے سے تیسرے نقطے سے گزرتی ہے۔")]),
      mcq("viii", "______ circle(s) can pass through the three non-collinear points.", [r"\text{one}", r"\text{two}", r"\text{three}", r"\text{many}"], 0,
          [T("Exactly one circle.", "صرف ایک دائرہ۔")]),
      mcq("ix", "Perpendicular bisector of a chord always passes through the ______ of circle.", [r"\text{arc}", r"\text{radius}", r"\text{centre}", r"\text{circumference}"], 2,
          [T("It passes through the centre.", "یہ مرکز سے گزرتا ہے۔")]),
      mcq("x", "The sum of the measures of central angles of a circle is:", [r"90^\circ", r"180^\circ", r"270^\circ", r"360^\circ"], 3, [T("A full turn.", "پورا چکر۔")])]
ex("rev8", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 8")
chord_q("rev8", 2, "On a circular clock with a radius of 6 cm, the points from 2 to 10 form a chord that is 10 cm long. Find the perpendicular distance from the centre of clock to the chord.", [
    (r"OM^2 = OP^2 - PM^2 = 6^2 - 5^2 = 11 \Rightarrow OM = \sqrt{11}\ \text{cm}", *PY, ["6**2 - 5**2 == 11"])], r"$\sqrt{11}$ cm", 5 / 6, "Review 8")
chord_q("rev8", 3, "A chord 6 cm long is at a distance of 4 cm from the centre. Calculate the radius of the circle.", [
    (r"r^2 = 4^2 + 3^2 = 25 \Rightarrow r = 5\ \text{cm}", *PY, ["sqrt(4**2 + 3**2) == 5"])], "$5$ cm", 0.6, "Review 8")
simple("rev8", 4, "In a circular park, two benches are placed so that the chords formed by their positions are both 10 m long. What can you say about the angles subtended at the centre by each bench?", [
    (r"\text{equal chords} \Rightarrow \text{equal central angles}", "Equal chords subtend equal angles at the centre.", "برابر وتر مرکز پر برابر زاویے بناتے ہیں۔", [])],
    "the angles at the centre are equal", "Review 8")
simple("rev8", 5, "Jannat is designing a triangular garden with corners at points $A(2,1)$, $B(4,4)$ and $C(1,5)$. Can she install a circular fountain that touches all three corners?", [
    (r"\text{slope } AB = \frac{3}{2},\ \text{slope } AC = -4 \Rightarrow A, B, C \text{ are not collinear}", "Different slopes, so the three points are not on one line.",
     "ڈھلوانیں مختلف ہیں، اس لیے تینوں نقاط ایک خط پر نہیں۔", ["Ne(R(3,2), -4)"]),
    (r"\text{Yes: the perpendicular bisectors meet at the circumcentre}", "Three non-collinear points always lie on exactly one circle.", "تین غیر ہم خط نقاط ہمیشہ ایک دائرے پر ہوتے ہیں۔", [])],
    "yes, she can install the fountain", "Review 8")
simple("rev8", 6, "Two chords, $PQ$ and $RS$, each measure 18 cm in length. If the distance of $PQ$ from the centre of circle is 7 cm. Find the distance of $RS$ from the centre.", [
    (r"d = 7\ \text{cm}", "Equal chords are equidistant from the centre.", "برابر وتر مرکز سے برابر فاصلے پر ہوتے ہیں۔", [])], "$7$ cm", "Review 8")
chord_q("rev8", 7, "A tree branch lies across a circular pond, forming a 20 m chord. A measuring rod having length 10 m is perpendicular to chord from the centre. What is the radius of the pond?", [
    (r"r^2 = OM^2 + AM^2 = 10^2 + 10^2 = 200 \Rightarrow r = 10\sqrt{2}\ \text{m}", *PY, ["sqrt(10**2 + 10**2) == 10*sqrt(2)"])], r"$10\sqrt{2}$ m", 0.71, "Review 8")
chord_q("rev8", 8, "A steel bar 6 m long lies inside a circular structure with ends on the circle. It is bisected by a perpendicular rod from the centre. Find the radius of the circular structure if the "
        "perpendicular distance from the centre to the bar is 4 m.", [
            (r"r^2 = 4^2 + 3^2 = 25 \Rightarrow r = 5\ \text{m}", *PY, ["sqrt(4**2 + 3**2) == 5"])], "$5$ m", 0.6, "Review 8")
