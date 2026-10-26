"""Word-problem solvers. Each reads the numbers from the sentence and builds the working for THOSE numbers."""
import re
from decimal import ROUND_HALF_UP, Decimal

import sympy as sp

from .common import P, R, S, T, failed_checks, mathtext, py, solved_item, tex

NUM = r"(\d+(?:\.\d+)?)"


def _r(text):
    """'2400' / '0.75' -> exact Rational."""
    return sp.Rational(text)


def _two_places(x):
    return Decimal(x.p) / Decimal(x.q)


def _round2(x):
    return (Decimal(int(x.p)) / Decimal(int(x.q))).quantize(Decimal("0.01"), ROUND_HALF_UP)


def _num_tex(x):
    """An integer, a terminating decimal (98.6, 7.25), or else a fraction."""
    x = sp.Rational(x)
    if x.is_Integer:
        return str(int(x))
    q = int(x.q)
    while q % 2 == 0:
        q //= 2
    while q % 5 == 0:
        q //= 5
    return format(Decimal(int(x.p)) / Decimal(int(x.q)), "f") if q == 1 else tex(x)


def _finish(question, parts):
    item = solved_item(question, parts)
    return item if not failed_checks(item) else None


# --------------------------------------------------------------------------- consecutive integers

def try_consecutive(text):
    t = mathtext.clean(text)
    m = re.search(r"sum of (\d+) consecutive (?:(odd|even) )?(?:integers?|numbers?)", t)
    if not m:
        return None
    k, kind = int(m.group(1)), m.group(2) or ""
    after = re.search(r"(?:is|are|equals?|=)\s*" + NUM, t[m.end():])
    if not after or not 2 <= k <= 6:
        return None
    total = int(_r(after.group(1)))
    d = 2 if kind else 1
    c = d * k * (k - 1) // 2
    x0 = sp.Rational(total - c, k)
    if not x0.is_Integer or (kind == "odd" and x0 % 2 == 0) or (kind == "even" and x0 % 2 == 1):
        return None
    x0 = int(x0)
    vals = [x0 + d * i for i in range(k)]
    terms = ["x"] + [f"x+{d * i}" for i in range(1, k)]
    what = f"{kind + ' ' if kind else ''}integers"
    steps = [
        S(rf"\text{{Let the {what} be }} " + ",\\; ".join(terms),
          f"Consecutive {what} differ by {d}, so call them " + ", ".join(terms) + ".",
          f"متواتر {'طاق' if kind == 'odd' else 'جفت' if kind == 'even' else 'صحیح'} اعداد میں {d} کا فرق ہوتا ہے، انہیں " + "، ".join(terms) + " فرض کریں۔"),
        S(" + ".join(f"({tm})" if i else tm for i, tm in enumerate(terms)) + rf" = {total} \;\Rightarrow\; {k}x + {c} = {total}",
          f"Their sum is {total}. Add the like terms.", f"ان کا مجموعہ {total} ہے۔ ملتے جلتے ارکان جمع کریں۔",
          " + ".join(f"({tm})" for tm in terms) + f" == {k}*x + {c}"),
        S(rf"{k}x = {total - c} \;\Rightarrow\; x = {x0}", f"Subtract {c} from both sides, then divide by {k}.",
          f"دونوں طرف سے {c} منفی کریں، پھر {k} سے تقسیم کریں۔", f"{total} - {c} == {total - c}", f"Rational({total - c},{k}) == {x0}"),
        S(",\\quad ".join(f"{tm} = {v}" for tm, v in zip(terms, vals)), f"Put x = {x0} back to get the {k} {what}.",
          f"x = {x0} واپس رکھ کر {k} اعداد معلوم کریں۔", f"{' + '.join(map(str, vals))} == {total}"),
    ]
    q = f"The sum of {k} consecutive {what} is {total}. Find the {what}."
    return _finish(q, [P("", steps, "$" + ",\\ ".join(map(str, vals)) + "$")])


# --------------------------------------------------------------------------- two numbers: sum and difference

def try_sum_difference(text):
    t = mathtext.clean(text)
    if not re.search(r"\bnumbers?\b", t):
        return None
    t = re.sub(r"\b2\s+(?:real\s+)?numbers\b", "numbers", t)      # "two real numbers": the word two became the digit 2
    m = re.search(r"sum[^0-9]*?" + NUM + r"[^0-9]*?differ(?:ence|s)?[^0-9]*?" + NUM, t)
    if not m:
        return None
    s_, d_ = _r(m.group(1)), _r(m.group(2))
    a, b = (s_ + d_) / 2, (s_ - d_) / 2
    steps = [
        S(rf"a+b = {_num_tex(s_)} \quad \text{{(i)}}, \qquad a-b = {_num_tex(d_)} \quad \text{{(ii)}}", "Let the numbers be a and b and write both conditions.",
          "اعداد کو a اور b فرض کریں اور دونوں شرطیں لکھیں۔"),
        S(rf"2a = {_num_tex(s_ + d_)} \;\Rightarrow\; a = {_num_tex(a)}", "Add (i) and (ii). The b terms cancel.", "(i) اور (ii) کو جمع کریں، b والے رکن ختم ہو جاتے ہیں۔",
          f"{py(s_)} + {py(d_)} == {py(s_ + d_)}", f"({py(s_ + d_)})/2 == {py(a)}"),
        S(rf"{_num_tex(a)} + b = {_num_tex(s_)} \;\Rightarrow\; b = {_num_tex(b)}", "Put the value of a in (i).", "a کی قیمت (i) میں رکھیں۔",
          f"{py(s_)} - {py(a)} == {py(b)}", f"{py(a)} - {py(b)} == {py(d_)}"),
    ]
    q = f"The sum of two numbers is {_num_tex(s_)} and their difference is {_num_tex(d_)}. Find the numbers."
    return _finish(q, [P("", steps, f"${_num_tex(a)},\\ {_num_tex(b)}$")])


# --------------------------------------------------------------------------- profit and loss percentage

def try_profit_loss(text):
    t = mathtext.clean(text)
    if not re.search(r"percent|%", t):
        return None
    m = re.search(r"(?:bought|purchased|buys|cost price|cost)[^0-9]*?" + NUM + r"[^0-9]*?(?:sold|sell|selling price)[^0-9]*?" + NUM, t)
    if not m:
        return None
    cp, sp_ = _r(m.group(1)), _r(m.group(2))
    if cp == sp_ or cp <= 0:
        return None
    profit = sp_ > cp
    amt = abs(sp_ - cp)
    pct = _round2(amt * 100 / cp)
    word = "profit" if profit else "loss"
    first = (rf"\text{{Profit}} = SP - CP = {_num_tex(sp_)} - {_num_tex(cp)} = {_num_tex(amt)}" if profit
             else rf"\text{{Loss}} = CP - SP = {_num_tex(cp)} - {_num_tex(sp_)} = {_num_tex(amt)}")
    steps = [
        S(first, "Profit is selling price minus cost price." if profit else "Loss is cost price minus selling price.",
          "منافع = فروخت قیمت − خرید قیمت۔" if profit else "نقصان = خرید قیمت − فروخت قیمت۔", f"{py(max(sp_, cp))} - {py(min(sp_, cp))} == {py(amt)}"),
        S(rf"\text{{{word.capitalize()}\%}} = \frac{{{_num_tex(amt)}}}{{{_num_tex(cp)}}} \times 100 = {pct}\%", f"{word.capitalize()} % = {word} / CP × 100.",
          ("منافع فیصد = منافع / خرید قیمت × 100۔" if profit else "نقصان فیصد = نقصان / خرید قیمت × 100۔"),
          f"abs(({py(amt)})*100/({py(cp)}) - Rational('{pct}')) < Rational(1,100)"),
    ]
    q = f"An article is bought for Rs. {_num_tex(cp)} and sold for Rs. {_num_tex(sp_)}. Find the {word} percentage."
    return _finish(q, [P("", steps, f"${pct}\\%$ {word}")])


# --------------------------------------------------------------------------- rate of simple profit

def try_simple_profit_rate(text):
    t = mathtext.clean(text)
    m = re.search(r"simple (?:profit|interest|markup) on (?:rs\.?\s*)?" + NUM + r" for " + NUM + r" years? is (?:rs\.?\s*)?" + NUM, t)
    if not m or "rate" not in t:
        return None
    principal, years, profit = _r(m.group(1)), _r(m.group(2)), _r(m.group(3))
    rate = profit * 100 / (years * principal)
    steps = [
        S(r"\text{Rate} = \frac{\text{profit} \times 100}{\text{time} \times \text{principal}}", "Use the formula for the rate of simple profit.", "سادہ منافع کی شرح کا فارمولا استعمال کریں۔"),
        S(rf"= \frac{{{_num_tex(profit)} \times 100}}{{{_num_tex(years)} \times {_num_tex(principal)}}} = {_num_tex(rate)}\%", "Put in the values and simplify.", "قیمتیں رکھیں اور سادہ کریں۔",
          f"({py(profit)})*100/(({py(years)})*({py(principal)})) == {py(rate)}"),
    ]
    q = f"If the simple profit on Rs. {_num_tex(principal)} for {_num_tex(years)} years is Rs. {_num_tex(profit)}, find the rate of profit."
    return _finish(q, [P("", steps, f"${_num_tex(rate)}\\%$")])


# --------------------------------------------------------------------------- temperature scales (K = C + 273, as in the book)

_UNIT = {"f": "F", "fahrenheit": "F", "c": "C", "celsius": "C", "centigrade": "C", "k": "K", "kelvin": "K"}


def try_temperature(text):
    t = mathtext.clean(text)
    m = re.search(r"(-?\d+(?:\.\d+)?)\s*(?:deg\s*)?(fahrenheit|celsius|centigrade|kelvin|f|c|k)\b", t)
    if not m or not re.search(r"\b(?:convert|change|express|find|into|to|in)\b", t):
        return None
    value, src = _r(m.group(1)), _UNIT[m.group(2)]
    rest = t[m.end():]
    targets = []
    for w in re.findall(r"\b(fahrenheit|celsius|centigrade|kelvin)\b", rest):
        u = _UNIT[w]
        if u != src and u not in targets:
            targets.append(u)
    targets = targets or {"F": ["C", "K"], "C": ["F"], "K": ["C"]}[src]
    c = value if src == "C" else (sp.Rational(5, 9) * (value - 32) if src == "F" else value - 273)
    steps, answers = [], []
    if src == "F" and ("C" in targets or "K" in targets):
        steps.append(S(rf"^\circ C = \frac{{5}}{{9}}(F-32) = \frac{{5}}{{9}}({_num_tex(value)}-32) = {_fmt(c)}", "Use the Fahrenheit-to-Celsius formula.",
                       "فارن ہائیٹ سے سیلسیس کا فارمولا استعمال کریں۔", f"abs(Rational(5,9)*({py(value)}-32) - Rational('{_val(c)}')) < Rational(1,100)"))
    if src == "K":
        steps.append(S(rf"^\circ C = K - 273 = {_num_tex(value)} - 273 = {_fmt(c)}", "Subtract 273 from the Kelvin value.", "کیلون کی قیمت سے 273 منفی کریں۔", f"{py(value)} - 273 == {py(c)}"))
    for u in targets:
        if u == "C":
            answers.append(rf"{_fmt(c)}^{{\circ}}C")
        elif u == "K":
            kv = c + 273
            steps.append(S(rf"K = C + 273 = {_fmt(c)} + 273 = {_fmt(kv)}", "Add 273 to the Celsius value to get Kelvin.", "کیلون کے لیے سیلسیس کی قیمت میں 273 جمع کریں۔",
                           f"abs(Rational('{_val(c)}') + 273 - Rational('{_val(kv)}')) < Rational(1,100)"))
            answers.append(rf"{_fmt(kv)}\text{{ K}}")
        elif u == "F":
            fv = sp.Rational(9, 5) * c + 32
            steps.append(S(rf"^\circ F = \frac{{9}}{{5}}\,^\circ C + 32 = \frac{{9}}{{5}} \times {_fmt(c)} + 32 = {_fmt(fv)}".replace(r"\,^\circ", r"\,{}^\circ"),
                           "Use the Celsius-to-Fahrenheit formula.", "سیلسیس سے فارن ہائیٹ کا فارمولا استعمال کریں۔",
                           f"abs(Rational(9,5)*Rational('{_val(c)}') + 32 - Rational('{_val(fv)}')) < Rational(1,100)"))
            answers.append(rf"{_fmt(fv)}^{{\circ}}F")
    if not steps or not answers:
        return None
    unit_name = {"F": "°F", "C": "°C", "K": "K"}[src]
    q = f"Convert {_num_tex(value)} {unit_name} into " + " and ".join({"F": "Fahrenheit", "C": "Celsius", "K": "Kelvin"}[u] for u in targets) + "."
    return _finish(q, [P("", steps, "$" + "$ and $".join(answers) + "$")])


def _val(x):
    """A plain decimal string with at most 2 places for a Rational (used inside checks): 100, 37.78, 0.5."""
    x = sp.Rational(x)
    if x.q == 1:
        return str(int(x))
    text = format(_round2(x), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def _fmt(x):
    return _val(x)
