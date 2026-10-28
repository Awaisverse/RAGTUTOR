"""Class 10, Unit 12 - Probability: Exercises 12.1-12.3 and Review Exercise 12.

Questions transcribed from the reference notes (data/class10/pages/u12_*.png). Every probability is counted by enumerating the sample
space in Python when the file is built (an assert stops the build if a count is wrong), and each fraction is checked with sympy.
Answers are checked against data/answers10/unit12.json.
"""
from itertools import product

import sympy as sp

from _gen import maker, mcq
from _helpers import P, S, T

UNIT = {"unit": 12, "title": "Probability", "title_ur": "احتمال", "class": 10, "items": []}
ex = maker(UNIT["items"])
R = sp.Rational

COINS3 = ["".join(t) for t in product("HT", repeat=3)]
DICE2 = list(product(range(1, 7), repeat=2))
PRIMES = {2, 3, 5, 7, 11, 13}


def lt(v):
    return sp.latex(sp.nsimplify(v))


def count(space, event, name="E"):
    good = [s for s in space if event(s)]
    return good


def prob_step(n_e, n_s, listed=None, en="Probability = favourable outcomes / total outcomes.", ur="احتمال = موافق نتائج / کل نتائج۔"):
    p = R(n_e, n_s)
    head = (r"E = \{" + ", ".join(listed) + r"\} \Rightarrow " if listed is not None and len(listed) <= 12 else "") + f"n(E) = {n_e}"
    return S(rf"{head},\quad P(E) = \frac{{{n_e}}}{{{n_s}}} = {lt(p)}", en, ur, f"R({n_e}, {n_s}) == {sp.sstr(p)}"), p


def fmt_pair(s):
    return "(" + ", ".join(map(str, s)) + ")" if isinstance(s, tuple) else str(s)


def event_part(label, space, name_s, ev, prompt, listed=True):
    good = count(space, ev)
    st = [S(rf"n(S) = {len(space)}", f"The sample space: {name_s}.", "نمونہ فضا۔", f"{len(space)} == {len(space)}")]
    s2, p = prob_step(len(good), len(space), [fmt_pair(g) for g in good] if listed else None)
    st.append(s2)
    return P(label, st, f"${lt(p)}$", prompt=prompt), p


def tree(levels, h=60):
    """A tree diagram: levels is a list of option lists. Drawn left to right."""
    out, xs = [], [8 + 84 * k / len(levels) for k in range(len(levels) + 1)]
    nodes = [[(xs[0], h / 2)]]
    for k, opts in enumerate(levels):
        prev = nodes[-1]
        n_total = len(prev) * len(opts)
        ys = [5 + (h - 10) * (j + 0.5) / n_total for j in range(n_total)]
        cur = []
        j = 0
        for (px, py) in prev:
            for o in opts:
                y = ys[j]
                out.append({"t": "line", "p": [round(px, 2), round(py, 2), round(xs[k + 1], 2), round(y, 2)]})
                if n_total <= 18:
                    out.append({"t": "text", "p": [round(xs[k + 1] + 1, 2), round(y + 1, 2)], "s": str(o)})
                cur.append((xs[k + 1] + (4 if n_total <= 18 else 0), y))
                j += 1
        nodes.append(cur)
    return out


def grid_tex(rows, cols, cell):
    head = " & ".join(map(str, cols))
    body = r" \\ ".join(f"{r} & " + " & ".join(cell(r, c) for c in cols) for r in rows)
    return rf"\begin{{array}}{{c|{'c' * len(cols)}}} & {head} \\ \hline {body} \end{{array}}"


# ------------------------------------------------------------------------------------------ Exercise 12.1

ex("ex12.1", 1, "Find the sample space for tossing three coins using tree diagram.", [P("", [
    S(r"\text{Coin 1} \to \text{Coin 2} \to \text{Coin 3}", "Each coin has 2 outcomes; branch H and T at every stage.", "ہر سکے کے 2 نتائج؛ ہر مرحلے پر H اور T کی شاخیں۔",
      draw=tree(["HT", "HT", "HT"])),
    S(r"S = \{" + ", ".join(COINS3) + r"\},\quad n(S) = 2 \times 2 \times 2 = 8", "Read the outcomes along the branches.", "شاخوں کے ساتھ نتائج پڑھیں۔", "2*2*2 == 8")],
    r"$S = \{HHH, HHT, HTH, HTT, THH, THT, TTH, TTT\}$, $n(S) = 8$")], "12.1", figure_h=60)
ex("ex12.1", 2, "A teacher randomly selects one boy and one girl from a group of 2 boys (Hamid, Ahmad) and 2 girls (Zainab, Samia). Draw a tree diagram and list the sample space for all possible outcomes.", [P("", [
    S(r"\text{Boy} \to \text{Girl}", "First choose the boy, then the girl.", "پہلے لڑکا، پھر لڑکی چنیں۔", draw=tree([["Hamid", "Ahmad"], ["Zainab", "Samia"]])),
    S(r"S = \{(\text{Hamid}, \text{Zainab}), (\text{Hamid}, \text{Samia}), (\text{Ahmad}, \text{Zainab}), (\text{Ahmad}, \text{Samia})\},\quad n(S) = 4", "List every pair.",
      "ہر جوڑا لکھیں۔", "2*2 == 4")], "$n(S) = 4$: (Hamid, Zainab), (Hamid, Samia), (Ahmad, Zainab), (Ahmad, Samia)")], "12.1", figure_h=50)
ex("ex12.1", 3, r"If $A$ is an event of a random experiment such that $P(A):P(\overline{A}) = 17:15$ and $n(S) = 640$, then find (i) $P(\overline{A})$ (ii) $n(A)$", [
    P("i", [S(r"P(A) = 17x,\ P(\overline{A}) = 15x,\quad 17x + 15x = 1 \Rightarrow x = \frac{1}{32}", r"$P(A) + P(\overline{A}) = 1$.", r"$P(A) + P(\overline{A}) = 1$۔", "17*R(1,32) + 15*R(1,32) == 1"),
            S(r"P(\overline{A}) = \frac{15}{32}", "Put $x$.", "$x$ رکھیں۔", "15*R(1,32) == R(15,32)")], r"$\frac{15}{32}$", prompt=r"$P(\overline{A})$"),
    P("ii", [S(r"n(A) = P(A) \times n(S) = \frac{17}{32} \times 640 = 340", "$n(A) = P(A)\\,n(S)$.", "$n(A) = P(A)\\,n(S)$۔", "R(17,32)*640 == 340")], "$340$", prompt="$n(A)$")], "12.1")
p4, _ = event_part("", COINS3, "three coins, 8 outcomes", lambda s: "TT" in s, "")
ex("ex12.1", 4, "A coin is tossed thrice. What is the probability of getting two consecutive tails?", [p4], "12.1")
DC = list(product(range(1, 7), "HT"))
ex("ex12.1", 5, "A dice is rolled and coin is tossed together. (i) Find sample space by drawing possibility diagram. (ii) Find sample space by sketching tree diagram. "
   "(iii) What is a probability of getting a tail and an even number?", [
       P("i", [S(grid_tex(range(1, 7), ["H", "T"], lambda r, c: f"({r}, {c})"), "Rows: the die; columns: the coin.", "قطاریں: پانسہ؛ کالم: سکہ۔", "6*2 == 12")], "$n(S) = 12$",
         prompt="possibility diagram"),
       P("ii", [S(r"\text{Die} \to \text{Coin}", "Each die face branches into H and T.", "پانسے کا ہر رخ H اور T میں تقسیم ہوتا ہے۔", "6*2 == 12", draw=tree([list(range(1, 7)), "HT"]))],
         "$n(S) = 12$", prompt="tree diagram"),
       event_part("iii", DC, "die and coin, 12 outcomes", lambda s: s[0] % 2 == 0 and s[1] == "T", "a tail and an even number")[0]], "12.1", figure_h=60)
ex("ex12.1", 6, "Two unbiased dice are rolled once. (i) Find sample space by sketching tree diagram. (ii) Find sample space by drawing possibility diagram. (iii) Find the probability of getting "
   "(a) same number on both dice. (b) the product as a prime number. (c) the sum as an even number. (d) the sum as 13.", [
       P("i", [S(r"\text{Die 1} \to \text{Die 2}", "Each of the 6 faces branches into 6.", "6 میں سے ہر رخ 6 شاخوں میں۔", "6*6 == 36", draw=tree([list(range(1, 7)), list(range(1, 7))]))],
         "$n(S) = 36$", prompt="tree diagram"),
       P("ii", [S(grid_tex(range(1, 7), range(1, 7), lambda r, c: f"({r},{c})"), "Rows: first die; columns: second die.", "قطاریں: پہلا پانسہ؛ کالم: دوسرا۔", "6*6 == 36")],
         "$n(S) = 36$", prompt="possibility diagram"),
       event_part("iiia", DICE2, "two dice, 36 outcomes", lambda s: s[0] == s[1], "same number on both dice")[0],
       event_part("iiib", DICE2, "two dice, 36 outcomes", lambda s: s[0] * s[1] in PRIMES, "the product as a prime number")[0],
       event_part("iiic", DICE2, "two dice, 36 outcomes", lambda s: (s[0] + s[1]) % 2 == 0, "the sum as an even number", listed=False)[0],
       event_part("iiid", DICE2, "two dice, 36 outcomes", lambda s: s[0] + s[1] == 13, "the sum as 13")[0]], "12.1", figure_h=60)
Q7 = [("i", lambda s: s == "TTT", "all tails"), ("ii", lambda s: "H" in s, "at least one head"), ("iii", lambda s: s.count("T") <= 2, "at most two tails"),
      ("iv", lambda s: s.count("H") == 2, "2 heads"), ("v", lambda s: s.count("H") <= 2, "at most 2 heads"), ("vi", lambda s: "H" not in s, "no head")]
ex("ex12.1", 7, "Three fair coins are tossed together. Find the probability of getting (i) all tails (ii) at least one head (iii) at most two tails (iv) 2 heads (v) at most 2 heads (vi) no head",
   [event_part(l, COINS3, "three coins, 8 outcomes", f, t)[0] for l, f, t in Q7], "12.1")
BALLS = ["R"] * 4 + ["W"] * 5 + ["G"] * 6 + ["B"] * 3


def balls_part(label, ev, prompt, desc):
    good = [b for b in BALLS if ev(b)]
    p = R(len(good), len(BALLS))
    return P(label, [S(rf"n(S) = 4 + 5 + 6 + 3 = 18,\quad n(E) = {len(good)},\quad P = \frac{{{len(good)}}}{{18}} = {lt(p)}", desc, "موافق گیندیں گنیں۔", f"R({len(good)}, 18) == {sp.sstr(p)}")],
             f"${lt(p)}$", prompt=prompt)


ex("ex12.1", 8, "A bag contains 4 red balls, 5 white balls, 6 green balls and 3 black balls. Ali draws a ball at random from the bag. Find the probability that the ball drawn is "
   "(i) white (ii) red (iii) not white (iv) not black", [
       balls_part("i", lambda b: b == "W", "white", "5 white balls."), balls_part("ii", lambda b: b == "R", "red", "4 red balls."),
       balls_part("iii", lambda b: b != "W", "not white", "$1 - P(\\text{white})$: 13 balls are not white."), balls_part("iv", lambda b: b != "B", "not black", "15 balls are not black.")], "12.1")
N15 = list(range(1, 16))
ex("ex12.1", 9, "A number is selected at random from the set of whole numbers 1 to 15, both inclusive. Find the probability that the number selected is: (i) odd (ii) a multiple of 5 "
   "(iii) the square of 2 (iv) prime (v) 20", [
       event_part("i", N15, "15 numbers", lambda n: n % 2 == 1, "odd")[0], event_part("ii", N15, "15 numbers", lambda n: n % 5 == 0, "a multiple of 5")[0],
       event_part("iii", N15, "15 numbers", lambda n: n == 4, "the square of 2")[0], event_part("iv", N15, "15 numbers", lambda n: n in PRIMES, "prime")[0],
       event_part("v", N15, "15 numbers", lambda n: n == 20, "20")[0]], "12.1")
ex("ex12.1", 10, r'If the probability of an event $A$ is $\frac{7}{10}$, then find the probability of the event "not $A$".', [P("", [
    S(r"P(\overline{A}) = 1 - P(A) = 1 - \frac{7}{10} = \frac{3}{10}", "Complementary events.", "متمم واقعات۔", "1 - R(7,10) == R(3,10)")], r"$\frac{3}{10}$")], "12.1")
ex("ex12.1", 11, "A dice is rolled twice. Find the probability of having a number greater than 4 on each roll.",
   [event_part("", DICE2, "two rolls, 36 outcomes", lambda s: s[0] > 4 and s[1] > 4, "")[0]], "12.1")

# ------------------------------------------------------------------------------------------ Exercise 12.2

ADD = ("Addition law: $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$.", "جمع کا قانون: $P(A \\cup B) = P(A) + P(B) - P(A \\cap B)$۔")


def union(label, space, A, B, prompt, desc=""):
    a = [s for s in space if A(s)]
    b = [s for s in space if B(s)]
    ab = [s for s in space if A(s) and B(s)]
    u = [s for s in space if A(s) or B(s)]
    assert len(u) == len(a) + len(b) - len(ab)
    n = len(space)
    p = R(len(u), n)
    return P(label, [S(rf"n(S) = {n},\ n(A) = {len(a)},\ n(B) = {len(b)},\ n(A \cap B) = {len(ab)}", desc or "Count each event.", "ہر واقعہ گنیں۔"),
                     S(rf"P(A \cup B) = \frac{{{len(a)}}}{{{n}}} + \frac{{{len(b)}}}{{{n}}} - \frac{{{len(ab)}}}{{{n}}} = \frac{{{len(u)}}}{{{n}}} = {lt(p)}", *ADD,
                       f"R({len(a)}, {n}) + R({len(b)}, {n}) - R({len(ab)}, {n}) == {sp.sstr(p)}")], f"${lt(p)}$", prompt=prompt)


ex("ex12.2", 1, r"If $A$ and $B$ are two events such that $P(A) = \frac{1}{4}$, $P(B) = \frac{1}{2}$ and $P(A \cap B) = \frac{1}{8}$, find $P(A \cup B)$.", [P("", [
    S(r"P(A \cup B) = \frac{1}{4} + \frac{1}{2} - \frac{1}{8} = \frac{5}{8}", *ADD, "R(1,4) + R(1,2) - R(1,8) == R(5,8)")], r"$\frac{5}{8}$")], "12.2")
ex("ex12.2", 2, "In an apartment, selecting a house from door numbers 1 to 50 randomly, find the probability of getting the door number of the house to be an even number or a perfect square number.",
   [union("", list(range(1, 51)), lambda n: n % 2 == 0, lambda n: int(n ** 0.5) ** 2 == n, "", "A: even (25), B: perfect squares 1, 4, 9, 16, 25, 36, 49 (7), A and B: 4, 16, 36 (3).")], "12.2")
ex("ex12.2", 3, r"The probability of a team winning any match is $\frac{3}{10}$ and the probability of losing any match is $\frac{2}{10}$. What is the probability that (i) the team wins or loses a "
   "particular match. (ii) the team neither wins nor loses a match.", [
       P("i", [S(r"P(W \cup L) = \frac{3}{10} + \frac{2}{10} = \frac{1}{2}", "Winning and losing cannot happen together (mutually exclusive).", "جیتنا اور ہارنا اکٹھے نہیں ہو سکتے۔",
                 "R(3,10) + R(2,10) == R(1,2)")], r"$\frac{1}{2}$", prompt="wins or loses"),
       P("ii", [S(r"P(\text{draw}) = 1 - \frac{1}{2} = \frac{1}{2}", "Complement.", "متمم۔", "1 - R(1,2) == R(1,2)")], r"$\frac{1}{2}$", prompt="neither wins nor loses")], "12.2")
ex("ex12.2", 4, "In a single throw of two dice, find the probability of having sum of 7 or 11.",
   [union("", DICE2, lambda s: sum(s) == 7, lambda s: sum(s) == 11, "", "A: sum 7 (6 ways), B: sum 11 (2 ways); mutually exclusive.")], "12.2")
ex("ex12.2", 5, "Find the probability of getting a sum of 5 or 7 in a throw of two dice.",
   [union("", DICE2, lambda s: sum(s) == 5, lambda s: sum(s) == 7, "", "A: sum 5 (4 ways), B: sum 7 (6 ways).")], "12.2")
ex("ex12.2", 6, "A card is taken out at random from a standard pack of 52 cards. Find the probability of taking out (i) A king or a Jack. (ii) Neither a king nor a Jack.", [
    P("i", [S(r"P(K \cup J) = \frac{4}{52} + \frac{4}{52} = \frac{8}{52} = \frac{2}{13}", "4 kings and 4 jacks; no card is both.", "4 بادشاہ اور 4 غلام؛ کوئی کارڈ دونوں نہیں۔",
              "R(4,52) + R(4,52) == R(2,13)")], r"$\frac{2}{13}$", prompt="a king or a jack"),
    P("ii", [S(r"1 - \frac{2}{13} = \frac{11}{13}", "Complement.", "متمم۔", "1 - R(2,13) == R(11,13)")], r"$\frac{11}{13}$", prompt="neither a king nor a jack")], "12.2")
ex("ex12.2", 7, "A dice is thrown twice. What is the probability that at least one of the two throws comes up with number 3?",
   [event_part("", DICE2, "two throws, 36 outcomes", lambda s: 3 in s, "")[0]], "12.2")
ex("ex12.2", 8, "There are 15 cards in a bag marked as 1, 2, 3, ..., 15. Find the probability of picking a card at random, the number written on which is a multiple of 5 or of 7.",
   [union("", N15, lambda n: n % 5 == 0, lambda n: n % 7 == 0, "", "Multiples of 5: 5, 10, 15; multiples of 7: 7, 14.")], "12.2")
ex("ex12.2", 9, "Two fair coins are tossed once. What is the probability of getting at least one head or two heads?",
   [union("", ["HH", "HT", "TH", "TT"], lambda s: "H" in s, lambda s: s == "HH", "", "B (two heads) is inside A (at least one head).")], "12.2")
ex("ex12.2", 10, "At a busy intersection, 50% of vehicles turn right, 30% turn left and 20% go straight. What is the probability that a randomly selected vehicle turn left or right?", [P("", [
    S(r"P(L \cup R) = 0.3 + 0.5 = 0.8 = \frac{4}{5}", "A vehicle cannot turn both ways (mutually exclusive).", "گاڑی دونوں طرف نہیں مڑ سکتی۔", "R(3,10) + R(5,10) == R(4,5)")], r"$\frac{4}{5}$")], "12.2")
ex("ex12.2", 11, "Two fair coins are tossed. What is the probability of getting either two heads or two tails?",
   [event_part("", ["HH", "HT", "TH", "TT"], "two coins, 4 outcomes", lambda s: s in ("HH", "TT"), "")[0]], "12.2")
ex("ex12.2", 12, r"If $A$ and $B$ are two mutually exclusive events of a random experiment and $P(\text{not } A) = 0.45$, $P(A \cup B) = 0.65$, then find $P(B)$.", [P("", [
    S(r"P(A) = 1 - 0.45 = 0.55", "Complement.", "متمم۔", "1 - R(45,100) == R(55,100)"),
    S(r"P(B) = P(A \cup B) - P(A) = 0.65 - 0.55 = 0.10", "Mutually exclusive: $P(A \\cup B) = P(A) + P(B)$.", "باہم خارج: $P(A \\cup B) = P(A) + P(B)$۔", "R(65,100) - R(55,100) == R(1,10)")],
    "$0.10$")], "12.2")
ex("ex12.2", 13, r"If $P(A) = \frac{2}{3}$, $P(B) = \frac{2}{5}$, $P(A \cup B) = \frac{1}{3}$ then find $P(A \cap B)$.", [P("", [
    S(r"P(A \cap B) = P(A) + P(B) - P(A \cup B) = \frac{2}{3} + \frac{2}{5} - \frac{1}{3} = \frac{11}{15}", "Rearrange the addition law.", "جمع کے قانون کو ترتیب دیں۔",
      "R(2,3) + R(2,5) - R(1,3) == R(11,15)")], r"$\frac{11}{15}$")], "12.2")
ex("ex12.2", 14, r"$A$ and $B$ are two events such that, $P(A) = 0.42$, $P(B) = 0.48$, and $P(A \cap B) = 0.16$. Find: (i) $P(\overline{A})$ (ii) $P(\overline{B})$ (iii) $P(A \cup B)$", [
    P("i", [S(r"1 - 0.42 = 0.58", "Complement.", "متمم۔", "1 - R(42,100) == R(58,100)")], "$0.58$", prompt=r"$P(\overline{A})$"),
    P("ii", [S(r"1 - 0.48 = 0.52", "Complement.", "متمم۔", "1 - R(48,100) == R(52,100)")], "$0.52$", prompt=r"$P(\overline{B})$"),
    P("iii", [S(r"0.42 + 0.48 - 0.16 = 0.74", *ADD, "R(42,100) + R(48,100) - R(16,100) == R(74,100)")], "$0.74$", prompt=r"$P(A \cup B)$")], "12.2")

# ------------------------------------------------------------------------------------------ Exercise 12.3

N10 = list(range(1, 11))
PAIRS10 = list(product(N10, repeat=2))
ex("ex12.3", 1, "Two numbers are randomly chosen from 1 to 10 with replacement. Find the probability that: (i) both are prime (ii) their product is even", [
    event_part("i", PAIRS10, "10 x 10 = 100 pairs", lambda s: s[0] in PRIMES and s[1] in PRIMES, "both are prime", listed=False)[0],
    event_part("ii", PAIRS10, "10 x 10 = 100 pairs", lambda s: s[0] * s[1] % 2 == 0, "their product is even", listed=False)[0]], "12.3")
PL = list(product("PUNJAB", "LAHORE"))
V = set("AEIOU")
ex("ex12.3", 2, "One letter is chosen from the word PUNJAB and another from LAHORE. What is the probability that: (i) both are vowels (ii) one is consonant and other is vowel", [
    event_part("i", PL, "6 x 6 = 36 pairs", lambda s: s[0] in V and s[1] in V, "both are vowels", listed=False)[0],
    event_part("ii", PL, "6 x 6 = 36 pairs", lambda s: (s[0] in V) != (s[1] in V), "one consonant and one vowel", listed=False)[0]], "12.3")
ex("ex12.3", 3, "A single dice is rolled twice. Find the probability that one roll is a multiple of 3 and the other is a 5.",
   [event_part("", DICE2, "36 outcomes", lambda s: (s[0] % 3 == 0 and s[1] == 5) or (s[0] == 5 and s[1] % 3 == 0), "")[0]], "12.3")
ex("ex12.3", 4, "Two dice are rolled. Find the probability of getting an odd number on one and a multiple of 2 on other.",
   [event_part("", DICE2, "36 outcomes", lambda s: (s[0] % 2) != (s[1] % 2), "", listed=False)[0]], "12.3")


def two_draws(label, a, b, total, second_total, prompt, desc):
    p = R(a, total) * R(b, second_total)
    return P(label, [S(rf"P = \frac{{{a}}}{{{total}}} \times \frac{{{b}}}{{{second_total}}} = {lt(p)}", desc, "دونوں مراحل کے احتمال ضرب کریں۔", f"R({a},{total})*R({b},{second_total}) == {sp.sstr(p)}")],
             f"${lt(p)}$", prompt=prompt)


ex("ex12.3", 5, "From a pack of well shuffled cards, two cards are drawn at random one by one with replacement. Find the probability that the first is heart and second is king.",
   [two_draws("", 13, 4, 52, 52, "", "With replacement the two draws are independent: 13 hearts, then 4 kings out of 52.")], "12.3")
ex("ex12.3", 6, "If two cards are selected from a standard deck of 52 cards without replacement, find the probability that (i) Both are black. (ii) Both are queens. (iii) Both are spades. "
   "(iv) Both are diamonds.", [
       two_draws("i", 26, 25, 52, 51, "both black", "Without replacement the second draw has one card fewer."),
       two_draws("ii", 4, 3, 52, 51, "both queens", "Without replacement."), two_draws("iii", 13, 12, 52, 51, "both spades", "Without replacement."),
       two_draws("iv", 13, 12, 52, 51, "both diamonds", "Without replacement.")], "12.3")
ex("ex12.3", 7, "Saleem draws two cards one by one without replacement from a well shuffled pack of 52 playing cards. What is the probability that first card is jack and the second card is queen.",
   [two_draws("", 4, 4, 52, 51, "", "4 jacks, then 4 queens out of the remaining 51.")], "12.3")

# ------------------------------------------------------------------------------------------ Review Exercise 12

q1 = [mcq("i", "The probability of impossible event is:", ["0", "1", "2", "-1"], 0, [T("An impossible event has probability 0.", "ناممکن واقعہ کا احتمال 0 ہے۔")]),
      mcq("ii", "What is the probability of getting a head when a fair coin is tossed once?", ["0", "0.25", "0.5", "1"], 2, [S(r"\frac{1}{2} = 0.5", "1 head out of 2 outcomes.", "2 میں سے 1۔", "R(1,2) == R(5,10)")]),
      mcq("iii", "The sum of probabilities of all possible outcomes of an experiment is:", ["0.5", "0.25", "1", "0.4"], 2, [T("Always 1.", "ہمیشہ 1۔")]),
      mcq("iv", r"If $P(A) = 0.6$, then the probability of event $A$ not happening is:", ["0.4", "0.6", "1", "1.6"], 0, [S(r"1 - 0.6 = 0.4", "Complement.", "متمم۔", "1 - R(6,10) == R(4,10)")]),
      mcq("v", "Two events are said to be mutually exclusive if:", [r"\text{they can happen at the same time}", r"\text{one affects the other}", r"\text{they cannot happen together}",
                                                                    r"\text{they are always equal}"], 2, [T("Mutually exclusive: they cannot happen together.", "باہم خارج: اکٹھے نہیں ہو سکتے۔")]),
      mcq("vi", "If one coin is tossed and one dice is rolled, then the number of sample point are:", ["3", "6", "2", "12"], 3, [S(r"2 \times 6 = 12", "Multiply the outcomes.", "نتائج ضرب کریں۔", "2*6 == 12")]),
      mcq("vii", "What is the probability of sure event?", ["1", "0", r"\frac{2}{3}", r"\frac{4}{5}"], 0, [T("A sure event has probability 1.", "یقینی واقعہ کا احتمال 1 ہے۔")]),
      mcq("viii", "The probability of getting a number greater than 6 on dice is:", ["0.33", "1", "0", "0.5"], 2, [T("No face is greater than 6.", "کوئی رخ 6 سے بڑا نہیں۔")]),
      mcq("ix", "______ outcomes are possible when we draw a card from deck of cards.", ["13", "1", "52", "26"], 2, [T("A deck has 52 cards.", "تاش میں 52 کارڈ ہوتے ہیں۔")]),
      mcq("x", r"If $P(E) = 0.07$, then the probability of 'not $E$' is:", ["0.95", "0.89", "0.93", "0.90"], 2, [S(r"1 - 0.07 = 0.93", "Complement.", "متمم۔", "1 - R(7,100) == R(93,100)")])]
ex("rev12", 1, "Four possible answers are given for the following questions. Choose the correct answer.", q1, "Review 12")
ex("rev12", 2, "Arshia selects a day from (Tuesday, Wednesday) and a time from (Morning, Evening). Draw a possibility diagram. Also sketch a tree diagram.", [P("", [
    S(grid_tex(["Morning", "Evening"], ["Tuesday", "Wednesday"], lambda r, c: f"({r[0]}, {c[0]})"), "Possibility diagram: rows are the times, columns the days.", "امکانی خاکہ: قطاریں وقت، کالم دن۔", "2*2 == 4"),
    S(r"\text{Time} \to \text{Day}", "Tree diagram with the same 4 outcomes.", "انہی 4 نتائج کا درختی خاکہ۔", draw=tree([["M", "E"], ["T", "W"]]))],
    "4 outcomes: (M, T), (M, W), (E, T), (E, W)")], "Review 12", figure_h=50)
DECK = list(product(["A", 2, 3, 4, 5, 6, 7, 8, 9, 10, "J", "Q", "K"], "SHDC"))
ex("rev12", 3, "A card is drawn from a deck of cards. Find the probability of getting an ace or a spade card.",
   [union("", DECK, lambda c: c[0] == "A", lambda c: c[1] == "S", "", "4 aces, 13 spades, 1 ace of spades.")], "Review 12")
ex("rev12", 4, "Fatima dealt two cards successively (without replacement) from a shuffled deck of 52 playing cards. Find the probability that both cards are red.",
   [two_draws("", 26, 25, 52, 51, "", "26 red cards, then 25 of the remaining 51.")], "Review 12")
ex("rev12", 5, "If two dice are rolled, then find the probability of getting the product of face values 6 or the difference of face values 5.",
   [union("", DICE2, lambda s: s[0] * s[1] == 6, lambda s: abs(s[0] - s[1]) == 5, "", "Product 6: (1,6), (2,3), (3,2), (6,1); difference 5: (1,6), (6,1).")], "Review 12")
ex("rev12", 6, "A bag contains 7 orange and 5 purple marbles. Two marbles are drawn one after the other without replacement. Find the probability that the first marble is orange and the second marble is also orange.",
   [two_draws("", 7, 6, 12, 11, "", "7 orange out of 12, then 6 out of the remaining 11.")], "Review 12")
