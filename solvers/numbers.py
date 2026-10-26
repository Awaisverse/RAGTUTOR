"""Number-system solvers: recurring decimals as p/q, scientific notation, rational numbers between two numbers."""
import re
from decimal import Decimal

import sympy as sp

from .common import P, R, S, T, failed_checks, labels, mathtext, part_markers, py, solved_item, tex
from _steps import between_part  # noqa: E402  (data/src is on the path, see common.py)


def _finish(question, parts):
    item = solved_item(question, parts)
    return item if not failed_checks(item) else None


# --------------------------------------------------------------------------- recurring decimals as p/q

_REC = re.compile(
    r"(?P<ip>\d+)\.(?P<a1>\d*)\\(?:overline|bar)\s*\{?(?P<b1>\d+)\}?"        # 0.3\overline{7}   0.\bar{4}
    r"|(?P<ip2>\d+)\.(?P<a2>\d*)\((?P<b2>\d+)\)"                              # 0.3(7)
    r"|(?P<ip3>\d+)\.(?P<d3>\d{3,})\s*(?:\.\.\.|…)"                           # 0.4444...   0.1666...
    r"|(?P<ip4>\d+)\.(?P<d4>\d+)\s*(?:recurring|repeating|recurs|repeats)")  # 0.37 recurring


def _period(digits):
    """Digits of a decimal that ends in '...': (non-repeating, repeating) using the shortest repeating tail."""
    for start in range(len(digits)):
        for p in range(1, (len(digits) - start) // 2 + 1):
            block = digits[start:start + p]
            tail = digits[start:]
            if (block * (len(tail) // p + 1))[:len(tail)] == tail and len(tail) >= 2 * p:
                return digits[:start], block
    return None


def _rec_candidates(text):
    out = []
    for m in _REC.finditer(text):
        g = m.groupdict()
        if g["b1"]:
            out.append((g["ip"], g["a1"], g["b1"]))
        elif g["b2"]:
            out.append((g["ip2"], g["a2"], g["b2"]))
        elif g["d3"]:
            per = _period(g["d3"])
            if per:
                out.append((g["ip3"], per[0], per[1]))
        elif g["d4"]:
            out.append((g["ip4"], "", g["d4"]))
    return out


def _rec_part(label, ip, a_digits, b_digits):
    a, b = len(a_digits), len(b_digits)
    n1, n0 = int(ip + a_digits + b_digits), int(ip + a_digits)
    den = 10 ** (a + b) - 10 ** a
    value = sp.Rational(n1 - n0, den)
    frac_b = sp.Rational(int(b_digits), 10 ** b - 1)
    rep = rf"\bar{{{b_digits}}}" if b == 1 else rf"\overline{{{b_digits}}}"
    shown = f"{ip}.{a_digits}{rep}"
    expand = f"{ip}.{a_digits}{b_digits * 3}\\ldots"
    v = f"Rational({value.p},{value.q})"
    steps = [S(rf"x = {shown} = {expand}", "Let x be the recurring decimal.", "فرض کریں x یہ دوری اعشاری عدد ہے۔")]
    if a:
        steps.append(S(rf"10^{{{a}}}x = {ip}{a_digits}.{b_digits * 3}\ldots",
                       f"Multiply by $10^{{{a}}}$ so that the repeating digits start right after the decimal point.",
                       f"$10^{{{a}}}$ سے ضرب دیں تاکہ دہرائے جانے والے ہندسے اعشاریہ کے فوراً بعد شروع ہوں۔",
                       f"{10 ** a}*{v} == {n0} + Rational({int(b_digits)},{10 ** b - 1})"))
    steps.append(S(rf"10^{{{a + b}}}x = {ip}{a_digits}{b_digits}.{b_digits * 3}\ldots",
                   f"{'One digit repeats' if b == 1 else f'{b} digits repeat'}, so multiply by $10^{{{b}}}$ once more.",
                   f"{'ایک ہندسہ دہرایا جاتا ہے' if b == 1 else f'{b} ہندسے دہرائے جاتے ہیں'}، اس لیے ایک بار اور $10^{{{b}}}$ سے ضرب دیں۔",
                   f"{10 ** (a + b)}*{v} == {n1} + Rational({int(b_digits)},{10 ** b - 1})"))
    lhs = rf"10^{{{a + b}}}x - 10^{{{a}}}x" if a else rf"10^{{{b}}}x - x"
    steps.append(S(rf"{lhs} = {n1} - {n0} \;\Rightarrow\; {den}x = {n1 - n0}", "Subtract the shorter line from the longer one so the repeating part cancels.",
                   "چھوٹی لکیر کو بڑی میں سے منہا کریں، دہرایا جانے والا حصہ ختم ہو جاتا ہے۔",
                   f"{10 ** (a + b)}*{v} - {10 ** a}*{v} == {n1 - n0}"))
    reduced = "" if sp.Rational(n1 - n0, den) == sp.Rational(n1 - n0, den) and sp.gcd(n1 - n0, den) == 1 else rf" = \frac{{{value.p}}}{{{value.q}}}"
    steps.append(S(rf"x = \frac{{{n1 - n0}}}{{{den}}}{reduced}", f"Divide both sides by {den}." + (" Then cancel the common factor." if reduced else ""),
                   f"دونوں طرف {den} سے تقسیم کریں۔" + (" پھر مشترک جزو کاٹیں۔" if reduced else ""), f"Rational({n1 - n0},{den}) == {v}"))
    return P(label, steps, rf"$\frac{{{value.p}}}{{{value.q}}}$" if value.q != 1 else f"${value.p}$", prompt=f"${shown}$")


def try_recurring(text):
    t = text
    cands = _rec_candidates(t)
    # the question must ask for a fraction, and the engine must be able to do EVERY part (a question like "is each of these
    # rational or irrational?" mentions a recurring decimal but asks something else)
    if not cands or not re.search(r"p\s*/\s*q|\\frac\{p\}\{q\}|as a? ?fraction|rational number|express|convert|write", t, re.I):
        return None
    if re.search(r"irrational|rational or|identify|classify", t, re.I):
        return None
    markers = len(part_markers(t)) - 1
    if markers > 0 and markers != len(cands):
        return None
    names = labels(len(cands)) if len(cands) > 1 else [""]
    parts = [_rec_part(lab, *c) for lab, c in zip(names, cands)]
    q = "Express the recurring decimal" + ("s" if len(parts) > 1 else "") + " as $\\frac{p}{q}$, where $p$ and $q$ are integers: " + \
        " ".join((f"({p['label']}) " if p["label"] else "") + p["prompt"] for p in parts)
    return _finish(q, parts)


# --------------------------------------------------------------------------- scientific notation

def _plain(d):
    return format(d, "f")


def _sci_parts(label, value):
    """value (Decimal, non-zero) -> a part that writes it as m x 10^n with 1 <= m < 10."""
    n = value.adjusted()
    m = (value.scaleb(-n)).normalize()
    m_txt = _plain(m)
    ordinary = _plain(value)
    direction = ("left", "positive") if n > 0 else ("right", "negative")
    chk = f"Rational('{m_txt}')*10**({n}) == Rational('{ordinary}')"
    steps = [
        S(f"{m_txt}", "Move the decimal point so that the number is between 1 and 10.", "اعشاری نقطہ اس طرح منتقل کریں کہ عدد 1 اور 10 کے درمیان آ جائے۔"),
        S(rf"\text{{places moved}} = {abs(n)}", "Count the places the decimal point moved.", "اعشاری نقطہ کتنے مقام منتقل ہوا، گنیں۔"),
        S(rf"{ordinary} = {m_txt} \times 10^{{{n}}}", f"The decimal point moved to the {direction[0]}, so the exponent is {direction[1]}.",
          "اعشاری نقطہ بائیں طرف گیا، اس لیے قوت مثبت ہے۔" if n > 0 else "اعشاری نقطہ دائیں طرف گیا، اس لیے قوت منفی ہے۔", chk),
    ]
    return P(label, steps, rf"${m_txt} \times 10^{{{n}}}$", prompt=f"${ordinary}$")


def _ord_part(label, mant, exp):
    value = Decimal(mant).scaleb(exp)
    ordinary = _plain(value)
    move = "right" if exp > 0 else "left"
    steps = [
        S(rf"\text{{Coefficient}} = {mant}, \quad \text{{Exponent}} = 10^{{{exp}}}", "Identify the coefficient and the power of 10.", "عددی سر اور 10 کی طاقت پہچانیں۔"),
        S(rf"{mant} \times 10^{{{exp}}} = {ordinary}", f"The exponent is {'positive' if exp > 0 else 'negative'} {abs(exp)}, so move the decimal point {abs(exp)} places to the {move}.",
          "قوت مثبت ہے، اس لیے اعشاری نقطہ دائیں طرف منتقل کریں۔" if exp > 0 else "قوت منفی ہے، اس لیے اعشاری نقطہ بائیں طرف منتقل کریں۔",
          f"Rational('{mant}')*10**({exp}) == Rational('{ordinary}')"),
    ]
    return P(label, steps, f"${ordinary}$", prompt=rf"${mant} \times 10^{{{exp}}}$")


_PROD = re.compile(r"(\d+(?:\.\d+)?)\s*(?:\*|x)\s*10\s*\^?\s*\(?\{?\s*(-?\d+)\s*\}?\)?")


def try_scientific(text):
    t = re.sub(r"\\times|\\cdot", "*", mathtext.clean(text.replace("{", "").replace("}", "")))
    to_ordinary = re.search(r"ordinary|decimal (?:notation|form)|standard notation|expand", t) is not None
    to_scientific = re.search(r"scientific|standard form", t) is not None
    if not (to_ordinary or to_scientific):
        return None
    pieces = part_markers(t)
    chunks = [p for p in pieces[1:] if p] if len(pieces) > 1 else [t]
    names = labels(len(chunks)) if len(chunks) > 1 else [""]
    parts = []
    for lab, chunk in zip(names, chunks):
        pm = _PROD.search(chunk)
        if pm:
            mant, exp = pm.group(1), int(pm.group(2))
            if to_ordinary and not to_scientific:
                parts.append(_ord_part(lab, mant, exp))
                continue
            value = Decimal(mant).scaleb(exp)
        else:
            nums = re.findall(r"\d+(?:\.\d+)?", chunk)
            if len(nums) != 1 or to_ordinary:
                return None
            value = Decimal(nums[0])
        if value == 0:
            return None
        parts.append(_sci_parts(lab, value))
    if not parts:
        return None
    what = "scientific notation" if to_scientific else "ordinary notation"
    q = f"Convert to {what}: " + " ".join((f"({p['label']}) " if p["label"] else "") + p["prompt"] for p in parts)
    return _finish(q, parts)


# --------------------------------------------------------------------------- two rational numbers between a and b

def try_between(text):
    t = mathtext.clean(text)
    m = re.search(r"(?:two|2)?\s*rational numbers?\s+between\s+(.+?)\s+and\s+(.+?)\s*[.?]?\s*$", t)
    if not m or re.search(r"\b(?:three|3|four|4|five|5)\s+rational", t):
        return None
    try:
        lo, hi = mathtext.parse_math(m.group(1).strip(" ,:")), mathtext.parse_math(m.group(2).strip(" ,:."))
    except ValueError:
        return None
    if not (lo.is_Rational and hi.is_Rational) or lo == hi:
        return None
    lo, hi = min(lo, hi), max(lo, hi)
    m1 = (lo + hi) / 2
    m2 = (m1 + hi) / 2
    part = between_part("", tex(lo), tex(hi), lo, hi, m1, m2)
    return _finish(f"Find two rational numbers between ${tex(lo)}$ and ${tex(hi)}$.", [part])
