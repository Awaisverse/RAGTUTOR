"""Solvers for radical expressions and numeric powers: rationalizing denominators, evaluating a^(m/n)."""
import math
import re

import sympy as sp

from .common import P, R, S, T, failed_checks, first_math_start, labels, mathtext, paren, part_markers, py, solved_item, tex


def _surd_factor(den):
    """For a denominator like sqrt(5) or 2*sqrt(5): the square-root factor (sqrt(5)), else None."""
    for f in sp.Mul.make_args(den):
        if f.is_Pow and f.exp == R(1, 2) and f.base.is_Integer:
            return f
    return None


def _ordered_terms(den):
    """The two terms of a binomial denominator in the book's order (constant first, then ascending radicand)."""
    terms = list(sp.Add.make_args(den))
    return sorted(terms, key=lambda t: (0 if t.is_Rational else 1, sp.default_sort_key(abs(t) if t.could_extract_minus_sign() else t)))


def _frac_tex(num, den):
    return rf"\frac{{{tex(num)}}}{{{tex(den)}}}"


def rationalize_part(label, num, den):
    """Steps that rationalize num/den exactly as the student wrote them, or None when there is nothing to rationalize."""
    num, den = sp.sympify(num), sp.sympify(den)
    expr = num / den
    if den.is_Rational or den.free_symbols or num.free_symbols:
        return None
    steps = []
    if not den.is_Add:
        surd = _surd_factor(den)
        if surd is None:
            return None
        mult = surd
        new_den = sp.expand(den * mult)
        new_num = sp.expand(num * mult)
        en1 = (f"The denominator has the single root ${tex(surd)}$, so multiply the numerator and the denominator by ${tex(mult)}$.")
        ur1 = (f"نسب نما میں ایک ہی جذر ${tex(surd)}$ ہے، اس لیے شمار کنندہ اور نسب نما کو ${tex(mult)}$ سے ضرب دیں۔")
        steps.append(S(rf"{_frac_tex(num, den)} \times \frac{{{tex(mult)}}}{{{tex(mult)}}}", en1, ur1,
                       f"({py(num)})/({py(den)}) == ({py(num)})*({py(mult)})/(({py(den)})*({py(mult)}))"))
        steps.append(S(rf"= \frac{{{paren(num)}\cdot {tex(mult)}}}{{{paren(den)}\cdot {tex(mult)}}} = {_frac_tex(new_num, new_den)}",
                       f"Multiply out. The denominator becomes rational because $\\sqrt{{a}}\\cdot\\sqrt{{a}} = a$.",
                       "ضرب دیں۔ نسب نما ناطق ہو جاتا ہے کیونکہ $\\sqrt{a}\\cdot\\sqrt{a} = a$۔",
                       f"({py(den)})*({py(mult)}) == {py(new_den)}", f"({py(num)})*({py(mult)}) == {py(new_num)}"))
    else:
        if len(sp.Add.make_args(den)) != 2:
            return None
        first, second = _ordered_terms(den)
        conj = first - second if den == first + second else first + second
        # use the conjugate that gives a positive denominator, as the book does
        new_den = sp.expand(den * conj)
        if new_den < 0:
            conj = -conj
            new_den = sp.expand(den * conj)
        new_num = sp.expand(num * conj)
        conj_tex = tex_conj(conj)
        steps.append(S(rf"{_frac_tex(num, den)} \times \frac{{{conj_tex}}}{{{conj_tex}}}",
                       f"Multiply the numerator and the denominator by the conjugate of the denominator, ${conj_tex}$.",
                       f"شمار کنندہ اور نسب نما کو نسب نما کے مزدوج ${conj_tex}$ سے ضرب دیں۔",
                       f"({py(num)})/({py(den)}) == ({py(num)})*({py(conj)})/(({py(den)})*({py(conj)}))"))
        steps.append(S(rf"{paren(den)}{paren(conj)} = {tex(new_den)}",
                       "In the denominator use $(a+b)(a-b) = a^2-b^2$, so the roots disappear.",
                       "نسب نما میں $(a+b)(a-b) = a^2-b^2$ استعمال کریں، اس سے جذر ختم ہو جاتے ہیں۔",
                       f"({py(den)})*({py(conj)}) == {py(new_den)}"))
        steps.append(S(rf"{paren(num)}{paren(conj)} = {tex(new_num)}",
                       "Multiply out the numerator.", "شمار کنندہ کو ضرب دے کر پھیلائیں۔",
                       f"({py(num)})*({py(conj)}) == {py(new_num)}"))
    result = sp.radsimp(expr)
    rn, rd = sp.fraction(sp.together(result))
    if not rd.is_Rational:
        result = sp.simplify(result)
        rn, rd = sp.fraction(sp.together(result))
        if not rd.is_Rational:
            return None
    if rn != sp.expand(rn):                       # radsimp can leave (a + b*sqrt(c))**2 / 5 unexpanded: write it out
        result = sp.radsimp(sp.expand(rn) / rd)
    before = _frac_tex(new_num, new_den)
    steps.append(S(f"{before} = {tex(result)}" if before != tex(result) else tex(result),
                   "Cancel the common factor and write the answer in simplest form." if before != tex(result)
                   else "No common factor remains, so this is the answer in simplest form.",
                   "مشترک جزو کاٹیں اور جواب کو مختصر ترین شکل میں لکھیں۔" if before != tex(result)
                   else "کوئی مشترک جزو باقی نہیں، اس لیے یہی مختصر ترین جواب ہے۔", f"{py(expr)} == {py(result)}"))
    return P(label, steps, f"${tex(result)}$", prompt=f"${_frac_tex(num, den)}$")


def tex_conj(conj):
    """The conjugate written with the larger root first when both terms are roots (sqrt5 - sqrt3, not -sqrt3 + sqrt5)."""
    return tex(conj)


def _bare_surd_fraction(text):
    """A fraction typed with no instruction at all, whose denominator contains a root: (sqrt8+sqrt3)/(sqrt8-sqrt3).
    Nothing else can be asked of it, so it is read as 'rationalize the denominator'."""
    t = text.strip().rstrip(".,;?:").strip()
    if mathtext._prose_words(re.sub(r"\\(?:sqrt|frac|left|right)", " ", t)):
        return False
    halves = mathtext.split_fraction(t.replace("$", ""))
    return bool(halves and re.search(r"sqrt|root|cbrt|√", halves[1]))


def try_rationalize(text):
    if not re.search(r"rationali[sz]e|rationali[sz]ation|denominator", text, re.I):
        if not _bare_surd_fraction(text):
            return None
        text = "Rationalize the denominator of " + text.strip()
    pieces = part_markers(text)
    if len(pieces) > 1:
        raw = [p for p in pieces[1:] if p]
    else:
        dollars = re.findall(r"\$([^$]+)\$", text)
        raw = dollars if dollars else [text[first_math_start(text):]]
    fractions = []
    for r in raw:
        dollars = re.findall(r"\$([^$]+)\$", r)
        piece = dollars[0] if dollars else r[first_math_start(r):]
        piece = piece.strip().rstrip(".,;?:").strip()
        halves = mathtext.split_fraction(piece)      # keep the denominator as written, see split_fraction
        if halves is None:
            return None
        try:
            fractions.append((mathtext.parse_math(halves[0]), mathtext.parse_math(halves[1])))
        except ValueError:
            return None
    parts = []
    names = labels(len(fractions)) if len(fractions) > 1 else [""]
    for lab, (n, d) in zip(names, fractions):
        part = rationalize_part(lab, n, d)
        if part is None:
            return None
        parts.append(part)
    question = "Rationalize the denominator: " + " ".join(f"({p['label']}) {p['prompt']}" if p["label"] else p["prompt"] for p in parts)
    item = solved_item(question, parts)
    return item if not failed_checks(item) else None


# ---------------------------------------------------------------- numeric powers: (81/16)^(-3/4), 64^(-2/3), (0.027)^(-1/3)

def _base_tex(b):
    """A power's base: an integer as is, a fraction in brackets so the exponent clearly belongs to the whole fraction."""
    return tex(b) if b.is_Integer else rf"\left({tex(b)}\right)"


def _perfect_power_base(n, k):
    r = round(n ** (1 / k))
    for c in (r - 1, r, r + 1):
        if c > 0 and c ** k == n:
            return c
    return None


def _root_form(b):
    """b = c**k with the largest k and a rational c: -> (c, k). For 27/1000 this is (3/10, 3)."""
    p, q = int(b.p), int(b.q)
    for k in range(max(int(math.log2(max(p, 2))), int(math.log2(max(q, 2)))) + 1, 1, -1):
        cp, cq = _perfect_power_base(p, k), _perfect_power_base(q, k)
        if cp and cq:
            return R(cp, cq), k
    return b, 1


def _power_part(label, base, expo):
    """The working for base**expo (both rational), or None when the result is not a rational number."""
    if not (base.is_Rational and expo.is_Rational) or base <= 0 or base == 1 or expo == 0:
        return None
    value = base ** expo
    if not value.is_Rational:
        return None
    steps = []
    b, x = base, expo
    if x < 0:
        steps.append(S(rf"{_base_tex(b)}^{{{tex(x)}}} = \left({tex(1 / b)}\right)^{{{tex(-x)}}}",
                       "A negative exponent means the reciprocal: $a^{-m} = \\left(\\frac{1}{a}\\right)^{m}$.",
                       "منفی طاقت کا مطلب معکوس ہے: $a^{-m} = \\left(\\frac{1}{a}\\right)^{m}$۔",
                       f"({py(b)})**({py(x)}) == ({py(1 / b)})**({py(-x)})"))
        b, x = 1 / b, -x
    c, k = _root_form(b)
    if k > 1:
        steps.append(S(rf"{tex(b)} = \left({tex(c)}\right)^{{{k}}} \;\Rightarrow\; \left(\left({tex(c)}\right)^{{{k}}}\right)^{{{tex(x)}}} = \left({tex(c)}\right)^{{{k} \times {tex(x)}}}",
                       "Write the base as a power of a simpler number and multiply the exponents: $(a^m)^n = a^{mn}$.",
                       "اساس کو سادہ عدد کی طاقت کی شکل میں لکھیں اور قوتیں ضرب دیں: $(a^m)^n = a^{mn}$۔",
                       f"{py(b)} == ({py(c)})**{k}", f"(({py(c)})**{k})**({py(x)}) == ({py(c)})**({py(k * x)})"))
        b, x = c, k * x
    steps.append(S(rf"\left({tex(b)}\right)^{{{tex(x)}}} = {tex(value)}", "Evaluate the power.", "طاقت کی قیمت نکالیں۔", f"({py(b)})**({py(x)}) == {py(value)}"))
    return P(label, steps, f"${tex(value)}$", prompt=f"${_base_tex(base)}^{{{tex(expo)}}}$")


def try_power(text):
    """Numbers raised to rational powers, e.g. 'simplify (81/16)^(-3/4)'. A question with several parts is solved only if EVERY part is."""
    pieces = part_markers(text)
    raw = [p for p in pieces[1:] if p] if len(pieces) > 1 else [text]
    if len(pieces) > 1 and len(raw) != len(pieces) - 1:
        return None
    parts = []
    names = labels(len(raw)) if len(raw) > 1 else [""]
    for lab, r in zip(names, raw):
        dollars = re.findall(r"\$([^$]+)\$", r)
        if len(raw) == 1 and len(dollars) > 1:
            return None                      # several maths pieces but no (i)(ii) markers: do not guess which one is meant
        start = re.search(r"[\d(\\]", r)
        if not start:
            return None
        piece = (dollars[0] if dollars else r[start.start():]).strip().rstrip(".,;?:").strip()
        halves = mathtext.split_power(piece)
        if halves is None:
            return None
        try:
            base, expo = mathtext.parse_math(halves[0]), mathtext.parse_math(halves[1])
        except ValueError:
            return None
        part = _power_part(lab, base, expo)
        if part is None:
            return None
        parts.append(part)
    q = "Simplify " + (" ".join(f"({p['label']}) {p['prompt']}" for p in parts) if len(parts) > 1 else parts[0]["prompt"]) + "."
    item = solved_item(q, parts)
    return item if not failed_checks(item) else None
