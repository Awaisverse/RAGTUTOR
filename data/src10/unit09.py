"""Class 10, Unit 9 - Tangent and Angles of a Circle: Exercises 9.1-9.2 and Review Exercise 9.

Questions transcribed from the reference notes (data/class10/pages/u09_*.png); every angle sum, length and sector value is checked
with sympy; answers are checked against data/answers10/unit09.json.
"""
import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 9, "title": "Tangent and Angles of a Circle", "title_ur": "مماس اور دائرے کے زاویے", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational


def near(expr, value, k):
    return f"Abs(({expr}) - {value}) <= {0.5 * 10 ** (-k) + 1e-9}"


def rows(rs):
    return [S(t, en, ur, *c) for t, en, ur, c in rs]


def one(eid, n, question, rs, answer, exercise, note=None):
    p = P("", rows(rs), answer)
    if note:
        p["key_note"] = note
    ex(eid, n, question, [p], exercise)


TAN = (r"A tangent is perpendicular to the radius at the point of contact.", r"مماس نقطہ تماس پر رداس کے عمود ہوتا ہے۔")
CEN = (r"The angle at the centre is twice the angle at the circumference on the same arc.", r"ایک ہی قوس پر مرکزی زاویہ محیطی زاویے کا دگنا ہوتا ہے۔")
SEG = (r"Angles in the same segment (on the same chord, same side) are equal.", r"ایک ہی قطعے کے زاویے (ایک ہی وتر پر، ایک ہی طرف) برابر ہوتے ہیں۔")
CYC = (r"Opposite angles of a cyclic quadrilateral add to $180^\circ$.", r"دائروی چوکور کے مخالف زاویوں کا مجموعہ $180^\circ$ ہوتا ہے۔")
SEMI = (r"The angle in a semicircle is a right angle.", r"نصف دائرے میں زاویہ قائمہ ہوتا ہے۔")
ALT = (r"Alternate segment theorem: the angle between a tangent and a chord equals the angle in the alternate segment.",
       r"متبادل قطعہ کا مسئلہ: مماس اور وتر کے درمیان زاویہ متبادل قطعے کے زاویے کے برابر ہوتا ہے۔")
TRI = (r"The angles of a triangle add to $180^\circ$.", r"مثلث کے زاویوں کا مجموعہ $180^\circ$ ہے۔")
PY = (r"Pythagoras in the right triangle formed by the radius, the tangent and the line to the centre.", r"رداس، مماس اور مرکز تک کے خط سے بننے والی قائمہ مثلث میں فیثا غورث۔")

# ------------------------------------------------------------------------------------------ Exercise 9.1

one("ex9.1", 1, r"Find the value of $x$ ($AB$ is a tangent at $B$, $OB$ a radius, $\angle BAO = 38^\circ$, $x = \angle AOB$).", [
    (r"\angle ABO = 90^\circ", *TAN, []),
    (r"x + 38^\circ + 90^\circ = 180^\circ \Rightarrow x = 52^\circ", *TRI, ["180 - 38 - 90 == 52"])], r"$x = 52^\circ$", "9.1")
one("ex9.1", 2, r"Find the angle $ABC$ ($AB$ and $AC$ are tangents from $A$, $\angle BAC = 65^\circ$).", [
    (r"AB = AC \Rightarrow \angle ABC = \angle ACB = y", r"Tangents from an external point are equal, so triangle $ABC$ is isosceles.", r"بیرونی نقطے سے مماس برابر ہوتے ہیں، اس لیے مثلث متساوی الساقین ہے۔", []),
    (r"y + y + 65^\circ = 180^\circ \Rightarrow 2y = 115^\circ \Rightarrow y = 57.5^\circ", *TRI, ["(180 - 65)/R(2) == R(115,2)"])], r"$\angle ABC = 57.5^\circ$", "9.1")
ex("ex9.1", 3, r"$A$, $B$ and $C$ are points on the circumference of a circle with centre at $O$. $\overline{AC}$ is the diameter of the circle and $\overleftrightarrow{DE}$ is the "
   r"tangent to the circle at the point $C$ and $m\angle BCD = 62^\circ$. Find (i) $m\angle BCA$ (ii) $m\angle BAC$", [
       P("i", rows([(r"\angle ACD = 90^\circ", *TAN, []), (r"\angle BCA = \angle ACD - \angle BCD = 90^\circ - 62^\circ = 28^\circ", r"Subtract the given angle.", r"دیا گیا زاویہ تفریق کریں۔",
                                                             ["90 - 62 == 28"])]), r"$28^\circ$", prompt=r"$m\angle BCA$"),
       P("ii", rows([(r"\angle BAC = \angle BCD = 62^\circ", *ALT, ["90 - 28 == 62"])]), r"$62^\circ$", prompt=r"$m\angle BAC$")], "9.1")
one("ex9.1", 4, r"$D$, $E$ and $F$ are points on the circumference of a circle with centre at $O$ and $m\angle DOF = 130^\circ$. Find $m\angle DEF$.", [
    (r"m\angle DEF = \frac{m\angle DOF}{2} = \frac{130^\circ}{2} = 65^\circ", *CEN, ["130/2 == 65"])], r"$65^\circ$", "9.1")
one("ex9.1", 5, r"$X$, $Y$ and $Z$ are points on the circumference of a circle with centre at $O$ and $m\angle XYZ = 85^\circ$. Find $x$ ($x = \angle XOZ$ on the same arc).", [
    (r"x = 2 \times m\angle XYZ = 2 \times 85^\circ = 170^\circ", *CEN, ["2*85 == 170"])], r"$x = 170^\circ$", "9.1")
one("ex9.1", 6, "In a historical monument, a circular fountain with a radius of 3 m is built. A flagpole is erected 7 m away from the centre of the fountain. Two ropes from the pole are "
    "tied to the edge of the fountain, just touching it. Find the length of each rope.", [
        (r"d^2 = r^2 + L^2 \Rightarrow 7^2 = 3^2 + L^2", *PY, []),
        (r"L^2 = 49 - 9 = 40 \Rightarrow L = \sqrt{40} = 2\sqrt{10} \approx 6.32\ \text{m}", r"Solve for $L$.", r"$L$ معلوم کریں۔", ["sqrt(7**2 - 3**2) == 2*sqrt(10)", near("sqrt(40)", "6.32", 2)])],
    r"$2\sqrt{10} \approx 6.32$ m", "9.1")
one("ex9.1", 7, "Two circular gears touch each other externally for proper rotation in a machine. The radii of the two circular gears are 5 cm and 7 cm. What is the distance between their centres if they touch externally?", [
    (r"d = r_1 + r_2 = 5 + 7 = 12\ \text{cm}", r"Circles touching externally: distance between centres = sum of the radii.", r"بیرونی طور پر ملنے والے دائروں کے مراکز کا فاصلہ = رداسوں کا مجموعہ۔", ["5 + 7 == 12"])],
    "$12$ cm", "9.1")
one("ex9.1", 8, "A small sensor lies inside a satellite dish and touches its wall internally. If the dish has radius 15 cm and the sensor has radius 2.5 cm, find the distance between their centres.", [
    (r"d = R - r = 15 - 2.5 = 12.5\ \text{cm}", r"Circles touching internally: distance between centres = difference of the radii.", r"اندرونی طور پر ملنے والے دائروں کے مراکز کا فاصلہ = رداسوں کا فرق۔",
     ["15 - R(5,2) == R(25,2)"])], "$12.5$ cm", "9.1")
one("ex9.1", 9, "An inner holder touches the outer cylindrical container internally. If the outer container has radius 8 cm and the inner holder has radius 6 cm, find the distance between their centres.", [
    (r"d = R - r = 8 - 6 = 2\ \text{cm}", r"Internal contact: difference of the radii.", r"اندرونی تماس: رداسوں کا فرق۔", ["8 - 6 == 2"])], "$2$ cm", "9.1")
one("ex9.1", 10, "A pyramid-shaped sculpture is placed in the center of a circular plaza with a radius of 10 m. A decorative pole stands 26 m from the center of the circle. Two guide wires are attached "
    "from the pole to the plaza edge, just touching the circle. Find the length of each wire.", [
        (r"26^2 = 10^2 + w^2 \Rightarrow w^2 = 676 - 100 = 576 \Rightarrow w = 24\ \text{m}", *PY, ["sqrt(26**2 - 10**2) == 24"])], "$24$ m", "9.1")

# ------------------------------------------------------------------------------------------ Exercise 9.2

one("ex9.2", 1, r"$A$, $B$, $C$ and $D$ are points on circumference of a circle with centre at $O$ as shown in figure (the exterior angle at $C$ is $114^\circ$, $x = \angle BOD$). Find the angle $x$.", [
    (r"\angle BCD = 180^\circ - 114^\circ = 66^\circ", r"The interior and exterior angles at $C$ are on a straight line.", r"$C$ پر اندرونی اور بیرونی زاویے ایک خط مستقیم پر ہیں۔", ["180 - 114 == 66"]),
    (r"x = 2 \times 66^\circ = 132^\circ", *CEN, ["2*66 == 132"])], r"$x = 132^\circ$", "9.2")
ex("ex9.2", 2, r"In the adjoining figure $m\angle BDC = 74^\circ$, find $m\angle BAC$, $m\angle BOC$ and $m\angle OBC$.", [P("", rows([
    (r"\angle BAC = \angle BDC = 74^\circ", *SEG, []),
    (r"\angle BOC = 2 \times 74^\circ = 148^\circ", *CEN, ["2*74 == 148"]),
    (r"OB = OC \Rightarrow \angle OBC = \frac{180^\circ - 148^\circ}{2} = 16^\circ", r"Triangle $BOC$ is isosceles (two radii).", r"مثلث $BOC$ متساوی الساقین ہے (دو رداس)۔", ["(180 - 148)/2 == 16"])]),
    r"$\angle BAC = 74^\circ,\ \angle BOC = 148^\circ,\ \angle OBC = 16^\circ$")], "9.2")
ex("ex9.2", 3, r"Find the angles $x$ and $y$ in the following figures: (i) cyclic quadrilateral with angles $74^\circ$ and $159^\circ$ (ii) $PQ$ a diameter, $\angle QPR = 38^\circ$ "
   r"(iii) $XY$ a tangent at $Y$, $\angle XOY = 62^\circ$", [
       P("i", rows([(r"x + 74^\circ = 180^\circ \Rightarrow x = 106^\circ", *CYC, ["180 - 74 == 106"]), (r"y + 159^\circ = 180^\circ \Rightarrow y = 21^\circ", *CYC, ["180 - 159 == 21"])]),
         r"$x = 106^\circ,\ y = 21^\circ$", prompt="(i)"),
       P("ii", rows([(r"y = 90^\circ", *SEMI, []), (r"x + 90^\circ + 38^\circ = 180^\circ \Rightarrow x = 52^\circ", *TRI, ["180 - 90 - 38 == 52"])]), r"$x = 52^\circ,\ y = 90^\circ$", prompt="(ii)"),
       P("iii", rows([(r"x = 90^\circ", *TAN, []), (r"62^\circ + 90^\circ + y = 180^\circ \Rightarrow y = 28^\circ", *TRI, ["180 - 62 - 90 == 28"])]), r"$x = 90^\circ,\ y = 28^\circ$", prompt="(iii)")],
   "9.2")
one("ex9.2", 4, r"Find the angle $x$ in the given figure ($EF$ is a tangent at $C$, $\angle BCE = 70^\circ$, $AC$ a diameter through $O$, $x = \angle ACD$, $\widehat{AB} = \widehat{AD}$).", [
    (r"\angle OCE = 90^\circ \Rightarrow \angle OCB = 90^\circ - 70^\circ = 20^\circ", *TAN, ["90 - 70 == 20"]),
    (r"\widehat{AB} = \widehat{AD} \Rightarrow \angle ACD = \angle ACB \text{ ... so } x = \angle ACD = 20^\circ", r"Equal arcs subtend equal angles at the circumference.",
     r"برابر قوسیں محیط پر برابر زاویے بناتی ہیں۔", [])], r"$x = 20^\circ$", "9.2")
one("ex9.2", 5, "In a circular arch over a monument entrance, two spotlight fixtures are placed such that they each shine from two different points on the arch to the same chord $PQ$ on the base of "
    "the arch. If the angle formed at one light is $55^\\circ$, what is the angle at the second light on the same side of chord $PQ$?", [
        (r"\text{Second angle} = 55^\circ", *SEG, [])], r"$55^\circ$", "9.2")
one("ex9.2", 6, "A circular garden has a walking path forming a quadrilateral inscribed in it. If one angle is $87^\\circ$, what is the opposite angle?", [
    (r"180^\circ - 87^\circ = 93^\circ", *CYC, ["180 - 87 == 93"])], r"$93^\circ$", "9.2")
one("ex9.2", 7, "A ferris wheel has a radius of 12 m. If a passenger travels a distance of 18 m along the circumference of the ferris wheel, what is the angle (in radians) swept by the passenger's position from the starting point?", [
    (r"\ell = r\theta \Rightarrow \theta = \frac{\ell}{r} = \frac{18}{12} = 1.5\ \text{radian}", r"Arc length $= r\theta$ ($\theta$ in radians).", r"قوس کی لمبائی $= r\theta$۔", ["R(18,12) == R(3,2)"])],
    "$1.5$ radian", "9.2")
ex("ex9.2", 8, r"Find $\theta$, when (i) $\ell = 3$ cm, $r = 2.2$ cm (ii) $\ell = 5.6$ cm, $r = 2$ cm", [
    P("i", rows([(r"\theta = \frac{\ell}{r} = \frac{3}{2.2} \approx 1.36\ \text{rad}", r"$\theta = \frac{\ell}{r}$.", r"$\theta = \frac{\ell}{r}$۔", [near("3/R(22,10)", "1.36", 2)])]), "$1.36$ rad",
      prompt=r"$\ell=3$ cm, $r=2.2$ cm"),
    P("ii", rows([(r"\theta = \frac{5.6}{2} = 2.8\ \text{rad}", r"$\theta = \frac{\ell}{r}$.", r"$\theta = \frac{\ell}{r}$۔", ["R(56,10)/2 == R(28,10)"])]), "$2.8$ rad",
      prompt=r"$\ell=5.6$ cm, $r=2$ cm")], "9.2")
ex("ex9.2", 9, r"Find $r$, when (i) $\ell = 5.5$ cm, $\theta = 40^\circ 20'$ (ii) $\ell = 13$ cm, $\theta = 70^\circ$", [
    P("i", rows([(r"\theta = 40^\circ 20' = 40\tfrac{1}{3}^\circ = 40\tfrac{1}{3} \times \frac{\pi}{180} \approx 0.704\ \text{rad}", r"Convert to radians ($20' = \frac{1}{3}^\circ$).",
                  r"ریڈین میں بدلیں ($20' = \frac{1}{3}^\circ$)۔", [near("R(121,3)*pi/180", "0.704", 3)]),
                 (r"r = \frac{\ell}{\theta} = \frac{5.5}{0.704} \approx 7.81\ \text{cm}", r"$r = \frac{\ell}{\theta}$.", r"$r = \frac{\ell}{\theta}$۔", [near("R(11,2)/(R(121,3)*pi/180)", "7.81", 2)])]),
      "$7.81$ cm", prompt=r"$\ell=5.5$ cm, $\theta=40^\circ 20'$"),
    P("ii", rows([(r"\theta = 70^\circ = 70 \times \frac{\pi}{180} \approx 1.222\ \text{rad}", r"Convert to radians.", r"ریڈین میں بدلیں۔", [near("70*pi/180", "1.222", 3)]),
                  (r"r = \frac{13}{1.222} \approx 10.64\ \text{cm}", r"$r = \frac{\ell}{\theta}$.", r"$r = \frac{\ell}{\theta}$۔", [near("13/(70*pi/180)", "10.64", 2)])]),
      "$10.64$ cm", prompt=r"$\ell=13$ cm, $\theta=70^\circ$")], "9.2")
ex("ex9.2", 10, r"Find $\ell$ and area of sector, when (i) $r = 1.7$ cm, $\theta = 0.25$ radian (ii) $r = 3$ cm, $\theta = 45^\circ$", [
    P("i", rows([(r"\ell = r\theta = 1.7 \times 0.25 = 0.425\ \text{cm}", r"Arc length.", r"قوس کی لمبائی۔", ["R(17,10)*R(1,4) == R(425,1000)"]),
                 (r"A = \frac{1}{2}r^2\theta = \frac{1}{2}(1.7)^2(0.25) \approx 0.361\ \text{cm}^2", r"Area of a sector.", r"قطاع کا رقبہ۔", [near("R(1,2)*R(17,10)**2*R(1,4)", "0.361", 3)])]),
      r"$\ell = 0.425$ cm, $A = 0.361$ cm$^2$", prompt=r"$r=1.7$ cm, $\theta=0.25$ rad"),
    P("ii", rows([(r"\theta = 45^\circ = \frac{\pi}{4},\quad \ell = 3 \times \frac{\pi}{4} = \frac{3\pi}{4} \approx 2.36\ \text{cm}", r"Convert to radians, then arc length.",
                   r"ریڈین میں بدل کر قوس کی لمبائی۔", [near("3*pi/4", "2.36", 2)]),
                  (r"A = \frac{1}{2}(3)^2\frac{\pi}{4} = \frac{9\pi}{8} \approx 3.53\ \text{cm}^2", r"Area of a sector.", r"قطاع کا رقبہ۔", [near("9*pi/8", "3.53", 2)])]),
      r"$\ell = \frac{3\pi}{4} \approx 2.36$ cm, $A = \frac{9\pi}{8} \approx 3.53$ cm$^2$", prompt=r"$r=3$ cm, $\theta=45^\circ$")], "9.2")
one("ex9.2", 11, "Uzma cut a pizza of radius 14 cm into 8 equal slices. What is the area of one slice (sector)?", [
    (r"\pi r^2 = \frac{22}{7} \times 14^2 = 616\ \text{cm}^2", r"Area of the whole pizza (using $\pi = \frac{22}{7}$).", r"پورے پیزا کا رقبہ ($\pi = \frac{22}{7}$)۔", ["R(22,7)*14**2 == 616"]),
    (r"\frac{616}{8} = 77\ \text{cm}^2", r"Eight equal slices.", r"آٹھ برابر ٹکڑے۔", ["616/8 == 77"])], r"$77$ cm$^2$", "9.2")
ex("ex9.2", 12, r"The perimeter and area of a sector are 14 cm and $10$ cm$^2$ respectively. Find the radius of the circle and the central angle of the sector.", [P("", rows([
    (r"14 = 2r + \ell \Rightarrow \ell = 14 - 2r", r"Perimeter of a sector = two radii + arc.", r"قطاع کا احاطہ = دو رداس + قوس۔", []),
    (r"10 = \frac{1}{2}r\ell = \frac{1}{2}r(14 - 2r) \Rightarrow r^2 - 7r + 10 = 0", r"Area $= \frac{1}{2}r\ell$; simplify.", r"رقبہ $= \frac{1}{2}r\ell$؛ سادہ کریں۔",
     ["expand(R(1,2)*r*(14 - 2*r) - 10) == -(r**2 - 7*r + 10)"]),
    (r"(r - 5)(r - 2) = 0 \Rightarrow r = 5 \text{ or } r = 2", r"Factorize.", r"تجزی کریں۔", ["expand((r - 5)*(r - 2)) == r**2 - 7*r + 10"]),
    (r"r = 5:\ \ell = 4,\ \theta = \frac{4}{5} = 0.8\ \text{rad};\quad r = 2:\ \ell = 10,\ \theta = \frac{10}{2} = 5\ \text{rad}", r"Both values satisfy the conditions.",
     r"دونوں قیمتیں شرائط پوری کرتی ہیں۔", ["R(1,2)*5*4 == 10", "R(1,2)*2*10 == 10", "2*5 + 4 == 14", "2*2 + 10 == 14"])]),
    r"$r = 5$ cm, $\theta = 0.8$ rad or $r = 2$ cm, $\theta = 5$ rad")], "9.2")

# ------------------------------------------------------------------------------------------ Review Exercise 9

q1 = [mcq("i", "Tangent is a line that touches the circumference of the circle at:", [r"\text{many points}", r"\text{three points}", r"\text{two points}", r"\text{one point}"], 3,
          [T(r"A tangent touches at exactly one point.", r"مماس صرف ایک نقطے پر چھوتا ہے۔")]),
      mcq("ii", "______ tangents can be drawn to a circle from a point outside the circle.", [r"\text{one}", r"\text{two}", r"\text{three}", r"\text{many}"], 1,
          [T(r"Exactly two tangents from an external point.", r"بیرونی نقطے سے دو مماس۔")]),
      mcq("iii", "______ tangents can be drawn to a circle from centre of the circle.", [r"\text{zero}", r"\text{one}", r"\text{two}", r"\text{three}"], 0,
          [T(r"The centre is inside the circle: no tangent.", r"مرکز دائرے کے اندر ہے: کوئی مماس نہیں۔")]),
      mcq("iv", "In circle, radius and tangent are:", [r"\text{parallel}", r"\text{equal}", r"\text{perpendicular}", r"\text{zero}"], 2, [T(*TAN)]),
      mcq("v", "An angle in a segment greater than a semicircle is ______ angle:", [r"\text{an acute}", r"\text{right}", r"\text{an obtuse}", r"\text{straight}"], 0,
          [T(r"In the major segment the angle is acute.", r"بڑے قطعے میں زاویہ حادہ ہوتا ہے۔")]),
      mcq("vi", "The angle subtended by the arc at the centre of the circle is called:", [r"\text{acute angle}", r"\text{central angle}", r"\text{right angle}", r"\text{complete angle}"], 1,
          [T(r"It is the central angle.", r"یہ مرکزی زاویہ ہے۔")]),
      mcq("vii", "What is the measure of an angle inscribed in a semi-circle?", [r"45^\circ", r"60^\circ", r"90^\circ", r"120^\circ"], 2, [T(*SEMI)]),
      mcq("viii", "Any two angles in the same segment of the circle are:", [r"\text{supplementary}", r"\text{complementary}", r"\text{equal}", r"\text{zero}"], 2, [T(*SEG)]),
      mcq("ix", "Area of the sector of the circle =", [r"\frac{1}{2}r\theta", r"\frac{3}{2}r^2\theta", r"\frac{1}{2}r^2\theta", r"\frac{3}{2}r\theta"], 2,
          [T(r"$A = \frac{1}{2}r^2\theta$ with $\theta$ in radians.", r"$A = \frac{1}{2}r^2\theta$ (ریڈین میں)۔")]),
      mcq("x", r"If $r = 6$ cm and $\theta = 2$ radians, then arc length is:", [r"12\text{ cm}", r"8\text{ cm}", r"6\text{ cm}", r"3\text{ cm}"], 0,
          [S(r"\ell = r\theta = 6 \times 2 = 12", r"Arc length.", r"قوس کی لمبائی۔", "6*2 == 12")])]
ex("rev9", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 9")
one("rev9", 2, r"In the adjoining figure, find the radius of the circle ($PQ = 24$ cm is a tangent at $P$, $OQ = 25$ cm).", [
    (r"OQ^2 = OP^2 + PQ^2 \Rightarrow 625 = OP^2 + 576", *PY, ["25**2 == 625", "24**2 == 576"]),
    (r"OP^2 = 49 \Rightarrow OP = 7\ \text{cm}", r"Solve.", r"حل کریں۔", ["sqrt(625 - 576) == 7"])], "$7$ cm", "Review 9")
ex("rev9", 3, r"Find the angles $a$, $b$, $c$ and $d$ in the given figure, if $O$ is the centre of the circle ($QS$ is a diameter, $\angle PSQ = 42^\circ$, $\angle QSR = 72^\circ$).", [P("", rows([
    (r"a = \angle QPS = 90^\circ,\quad b = \angle QRS = 90^\circ", *SEMI, []),
    (r"c = 180^\circ - 90^\circ - 42^\circ = 48^\circ", r"Triangle $PQS$.", r"مثلث $PQS$۔", ["180 - 90 - 42 == 48"]),
    (r"d = 180^\circ - 90^\circ - 72^\circ = 18^\circ", r"Triangle $QRS$.", r"مثلث $QRS$۔", ["180 - 90 - 72 == 18"])]),
    r"$a = 90^\circ,\ b = 90^\circ,\ c = 48^\circ,\ d = 18^\circ$")], "Review 9")
ex("rev9", 4, r"Find the angles $a$, $b$ and $c$, if $\overrightarrow{ML}$ is a tangent line and $O$ is the centre of the circle ($\angle LMO = 22^\circ$, $C$ on $OM$).", [P("", rows([
    (r"\angle OLM = 90^\circ \Rightarrow a = \angle LOM = 180^\circ - 90^\circ - 22^\circ = 68^\circ", *TAN, ["180 - 90 - 22 == 68"]),
    (r"OL = OC \Rightarrow b = c = \frac{180^\circ - 68^\circ}{2} = 56^\circ", r"Triangle $OLC$ is isosceles (two radii).", r"مثلث $OLC$ متساوی الساقین ہے۔", ["(180 - 68)/2 == 56"])]),
    r"$a = 68^\circ,\ b = 56^\circ,\ c = 56^\circ$")], "Review 9")
ex("rev9", 5, r"Find the angles marked in the given figure, where $O$ is the centre of the circle ($\angle SOR = 100^\circ$).", [P("", rows([
    (r"OS = OR \Rightarrow a = b", r"Two radii: triangle $SOR$ is isosceles.", r"دو رداس: مثلث $SOR$ متساوی الساقین ہے۔", []),
    (r"100^\circ + 2a = 180^\circ \Rightarrow a = b = 40^\circ", *TRI, ["(180 - 100)/2 == 40"])]), r"$a = 40^\circ,\ b = 40^\circ$")], "Review 9")
one("rev9", 6, "Two round dining tables are arranged to touch at their edges. The radii of the two round dining tables are 10 cm and 12 cm. What is the distance between their centres if they touch externally?", [
    (r"d = r_1 + r_2 = 10 + 12 = 22\ \text{cm}", r"External contact: sum of the radii.", r"بیرونی تماس: رداسوں کا مجموعہ۔", ["10 + 12 == 22"])], "$22$ cm", "Review 9")
one("rev9", 7, r"A circular mosaic pattern: two tiles connect to the same chord $EF$ and reach two points $G$ and $H$ on the arc above $EF$. If $m\angle EGF = 65^\circ$, find $m\angle EHF$.", [
    (r"m\angle EHF = m\angle EGF = 65^\circ", *SEG, [])], r"$65^\circ$", "Review 9")
one("rev9", 8, "A triangular frame within a semicircular gate joins the ends of the diameter to the peak. What is the angle formed at the peak?", [
    (r"90^\circ", *SEMI, [])], r"$90^\circ$", "Review 9")
one("rev9", 9, "A circular birthday cake has a radius of 15 cm. A slice has an arc length of 10 cm. What is the area of this slice?", [
    (r"A = \frac{1}{2}\ell r = \frac{1}{2} \times 10 \times 15 = 75\ \text{cm}^2", r"$A = \frac{1}{2}r^2\theta = \frac{1}{2}r\ell$.", r"$A = \frac{1}{2}r\ell$۔", ["R(1,2)*10*15 == 75"])],
    r"$75$ cm$^2$", "Review 9")
one("rev9", 10, "A sector cut from a circle of radius 5 cm has a perimeter of 16 cm. Find area of this sector.", [
    (r"16 = 2(5) + \ell \Rightarrow \ell = 6\ \text{cm}", r"Perimeter = two radii + arc.", r"احاطہ = دو رداس + قوس۔", ["16 - 10 == 6"]),
    (r"A = \frac{1}{2}\ell r = \frac{1}{2} \times 6 \times 5 = 15\ \text{cm}^2", r"Area of the sector.", r"قطاع کا رقبہ۔", ["R(1,2)*6*5 == 15"])], r"$15$ cm$^2$", "Review 9")
