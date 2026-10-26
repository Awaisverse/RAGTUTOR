"""Synthetic problem generators: many new, correct, step-by-step solved questions per book type.

Why: 14 hand-solved examples are far too few to fine-tune on. Each generator below knows how to
solve one TYPE of textbook question. It picks new numbers, computes the solution exactly, writes
the board steps in English and Urdu, and attaches sympy checks. The checks are re-verified by
tools/build_dataset.verify, so a wrong step cannot enter the training data.

These items are for TRAINING ONLY. The tutor's index contains only real book items.

Usage (as a library):  from synth import generate;  items = generate(per_type=40, seed0=0)
"""
import pathlib
import random
import sys
from decimal import ROUND_HALF_UP, Decimal
from math import gcd

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "data" / "src"))
from _helpers import P, Q, S, T, one  # noqa: E402

NON_SQUARES = [2, 3, 5, 6, 7, 10, 11, 13]
NAMES = ["Ali", "Sara", "Bilal", "Ayesha", "Hamza", "Zainab", "Umair", "Noor"]
THINGS = ["bicycle", "book", "watch", "bag", "shirt", "mobile cover", "table", "fan"]


# ---------- small LaTeX helpers ----------

def frac(p, q):
    return str(p) if q == 1 else f"\\frac{{{p}}}{{{q}}}"


def pw(var, e):
    return var if e == 1 else f"{var}^{{{e}}}"


def reduce(p, q):
    g = gcd(p, q)
    return p // g, q // g


def dec_str(x):
    """Plain decimal text without exponent, e.g. 0.0000347 or 78000000."""
    return format(x, "f")


def item(type_name, seed, unit, title, question, parts):
    it = Q(f"syn-{type_name}-{seed}", "synthetic", "", 0, question, parts)
    it["unit"] = unit
    it["unit_title"] = title
    it["synthetic"] = True
    return it


# ---------- Unit 1: Real Numbers ----------

def gen_recurring1(rng, seed):
    d = rng.randint(1, 8)
    p, q = reduce(d, 9)
    steps = [
        S(f"x = 0.{d}{d}{d}\\ldots", "Let x be the recurring decimal.", "فرض کریں x یہ دوری اعشاری عدد ہے۔"),
        S(f"10x = {d}.{d}{d}\\ldots", "One digit repeats, so multiply both sides by 10.",
          "ایک ہندسہ دہرایا جاتا ہے، اس لیے دونوں طرف 10 سے ضرب دیں۔",
          f"10*Rational({d},9) == {d} + Rational({d},9)"),
        S(f"9x = {d}", "Subtract the first line from the second so the repeating part cancels.",
          "پہلی لکیر کو دوسری میں سے منہا کریں، دہرایا جانے والا حصہ ختم ہو جاتا ہے۔",
          f"10*Rational({d},9) - Rational({d},9) == {d}"),
        S(f"x = \\frac{{{d}}}{{9}}" + ("" if (p, q) == (d, 9) else f" = {frac(p, q)}"),
          "Divide by 9" + ("." if (p, q) == (d, 9) else " and cancel the common factor."),
          "9 سے تقسیم کریں" + ("۔" if (p, q) == (d, 9) else " اور مشترک جزو کاٹ دیں۔"),
          f"Rational({d},9) == Rational({p},{q})"),
    ]
    return item("recurring1", seed, 1, "Real Numbers",
                f"Express $0.\\bar{{{d}}}$ as $\\frac{{p}}{{q}}$, where $p$ and $q$ are integers.",
                one(steps, f"${frac(p, q)}$"))


def gen_recurring2(rng, seed):
    ab = rng.randint(10, 98)
    s = f"{ab:02d}"
    p, q = reduce(ab, 99)
    steps = [
        S(f"x = 0.{s}{s}{s}\\ldots", "Let x be the recurring decimal.", "فرض کریں x یہ دوری اعشاری عدد ہے۔"),
        S(f"100x = {s}.{s}{s}\\ldots", "Two digits repeat, so multiply both sides by 100.",
          "دو ہندسے دہرائے جاتے ہیں، اس لیے دونوں طرف 100 سے ضرب دیں۔",
          f"100*Rational({ab},99) == {ab} + Rational({ab},99)"),
        S(f"99x = {ab}", "Subtract the first line from the second.", "پہلی لکیر کو دوسری میں سے منہا کریں۔",
          f"100*Rational({ab},99) - Rational({ab},99) == {ab}"),
        S(f"x = \\frac{{{ab}}}{{99}}" + ("" if (p, q) == (ab, 99) else f" = {frac(p, q)}"),
          "Divide by 99" + ("." if (p, q) == (ab, 99) else " and cancel the common factor."),
          "99 سے تقسیم کریں" + ("۔" if (p, q) == (ab, 99) else " اور مشترک جزو کاٹ دیں۔"),
          f"Rational({ab},99) == Rational({p},{q})"),
    ]
    return item("recurring2", seed, 1, "Real Numbers",
                f"Express $0.\\overline{{{s}}}$ as $\\frac{{p}}{{q}}$, where $p$ and $q$ are integers.",
                one(steps, f"${frac(p, q)}$"))


def gen_rationalize1(rng, seed):
    a, b = rng.randint(1, 12), rng.choice(NON_SQUARES)
    g = gcd(a, b)
    p, q = a // g, b // g
    coef = (f"{p}" if p != 1 else "") + f"\\sqrt{{{b}}}"
    res = coef if q == 1 else f"\\frac{{{coef}}}{{{q}}}"
    steps = [
        S(f"\\frac{{{a}}}{{\\sqrt{{{b}}}}}\\times\\frac{{\\sqrt{{{b}}}}}{{\\sqrt{{{b}}}}}",
          "Multiply the numerator and the denominator by $\\sqrt{%d}$ to remove the root below." % b,
          "نیچے سے جذر ختم کرنے کے لیے شمار کنندہ اور نسب نما کو $\\sqrt{%d}$ سے ضرب دیں۔" % b,
          f"{a}/sqrt({b}) == {a}*sqrt({b})/{b}"),
        S(f"= \\frac{{{a}\\sqrt{{{b}}}}}{{{b}}}", "The denominator becomes $\\sqrt{%d}\\cdot\\sqrt{%d} = %d$." % (b, b, b),
          "نسب نما $\\sqrt{%d}\\cdot\\sqrt{%d} = %d$ ہو جاتا ہے۔" % (b, b, b), f"sqrt({b})*sqrt({b}) == {b}"),
    ]
    if g > 1:
        steps.append(S(f"= {res}", "Cancel the common factor.", "مشترک جزو کاٹ دیں۔",
                       f"Rational({a},{b})*sqrt({b}) == Rational({p},{q})*sqrt({b})"))
    return item("rationalize1", seed, 1, "Real Numbers",
                f"Rationalize the denominator of $\\frac{{{a}}}{{\\sqrt{{{b}}}}}$.",
                one(steps, f"${res}$"))


def gen_rationalize2(rng, seed):
    b, c = sorted(rng.sample(NON_SQUARES, 2), reverse=True)
    a = rng.randint(1, 12)
    sg = rng.choice(["+", "-"])
    ng = "-" if sg == "+" else "+"
    d = b - c
    g = gcd(a, d)
    k, den = a // g, d // g
    num = f"{k if k != 1 else ''}(\\sqrt{{{b}}}{ng}\\sqrt{{{c}}})" if k != 1 or den != 1 else f"\\sqrt{{{b}}}{ng}\\sqrt{{{c}}}"
    if den == 1:
        res = num if k != 1 else f"\\sqrt{{{b}}}{ng}\\sqrt{{{c}}}"
    else:
        res = f"\\frac{{{num}}}{{{den}}}" if k != 1 else f"\\frac{{\\sqrt{{{b}}}{ng}\\sqrt{{{c}}}}}{{{den}}}"
    steps = [
        S(f"\\frac{{{a}}}{{\\sqrt{{{b}}}{sg}\\sqrt{{{c}}}}}\\times\\frac{{\\sqrt{{{b}}}{ng}\\sqrt{{{c}}}}}{{\\sqrt{{{b}}}{ng}\\sqrt{{{c}}}}}",
          "Multiply the numerator and denominator by the conjugate of the denominator.",
          "شمار کنندہ اور نسب نما کو نسب نما کے مزدوج سے ضرب دیں۔",
          f"{a}/(sqrt({b}){sg}sqrt({c})) == {a}*(sqrt({b}){ng}sqrt({c}))/({b}-{c})"),
        S(f"(\\sqrt{{{b}}})^2-(\\sqrt{{{c}}})^2 = {b}-{c} = {d}",
          "In the denominator use $(x+y)(x-y) = x^2-y^2$.", "نسب نما میں $(x+y)(x-y) = x^2-y^2$ استعمال کریں۔",
          f"(sqrt({b}))**2 - (sqrt({c}))**2 == {d}"),
        S(f"= {res}", "Write the result" + (" and cancel the common factor." if g > 1 else "."),
          "نتیجہ لکھیں" + (" اور مشترک جزو کاٹ دیں۔" if g > 1 else "۔"),
          f"{a}/(sqrt({b}){sg}sqrt({c})) == Rational({k},{den})*(sqrt({b}){ng}sqrt({c}))"),
    ]
    return item("rationalize2", seed, 1, "Real Numbers",
                f"Rationalize the denominator of $\\frac{{{a}}}{{\\sqrt{{{b}}}{sg}\\sqrt{{{c}}}}}$.",
                one(steps, f"${res}$"))


def gen_sumdiff(rng, seed):
    b = rng.randint(1, 40)
    a = b + rng.randint(1, 30)
    s, d = a + b, a - b
    steps = [
        S(f"a+b = {s} \\quad (i), \\qquad a-b = {d} \\quad (ii)", "Let the numbers be a and b and write both conditions.",
          "اعداد کو a اور b فرض کریں اور دونوں شرطیں لکھیں۔"),
        S(f"2a = {s + d} \\Rightarrow a = {a}", "Add (i) and (ii). The b terms cancel.", "(i) اور (ii) کو جمع کریں، b والے رکن ختم ہو جاتے ہیں۔",
          f"{s}+{d} == 2*{a}"),
        S(f"{a} + b = {s} \\Rightarrow b = {b}", "Put a in (i) to find b.", "b معلوم کرنے کے لیے a کی قیمت (i) میں رکھیں۔",
          f"{s}-{a} == {b}"),
    ]
    return item("sumdiff", seed, 1, "Real Numbers",
                f"The sum of two real numbers is {s} and their difference is {d}. Find the numbers.",
                one(steps, f"${a}$ and ${b}$"))


def gen_between(rng, seed):
    a = rng.randint(1, 20)
    b = a + rng.randint(1, 3)
    from sympy import Rational
    m1 = Rational(a + b, 2)
    m2 = (m1 + b) / 2

    def tx(r):
        return frac(int(r.p), int(r.q))

    steps = [
        S(f"\\frac{{{a}+{b}}}{{2}} = {tx(m1)}", "The average of two numbers lies between them.", "دو اعداد کا اوسط ان کے درمیان ہوتا ہے۔",
          f"Rational({a}+{b},2) == Rational({m1.p},{m1.q})"),
        S(f"\\frac{{{tx(m1)}+{b}}}{{2}} = {tx(m2)}", "Take the average of this number and the larger number to get another.",
          "اس عدد اور بڑے عدد کا اوسط لیں، یہ ایک اور عدد دے گا۔",
          f"(Rational({m1.p},{m1.q})+{b})/2 == Rational({m2.p},{m2.q})"),
    ]
    return item("between", seed, 1, "Real Numbers", f"Find two rational numbers between {a} and {b}.",
                one(steps, f"${tx(m1)}$ and ${tx(m2)}$"))


def gen_indices_root(rng, seed):
    n = rng.choice([2, 3, 4])
    k, p, q = rng.randint(2, 5), rng.randint(1, 3), rng.randint(1, 3)
    K = k ** n
    rad = f"\\sqrt{{{K}x^{{{n * p}}}y^{{{n * q}}}}}" if n == 2 else f"\\sqrt[{n}]{{{K}x^{{{n * p}}}y^{{{n * q}}}}}"
    steps = [
        S(f"{rad} = ({K})^{{1/{n}}}(x^{{{n * p}}})^{{1/{n}}}(y^{{{n * q}}})^{{1/{n}}}",
          "Write the root as the power $1/%d$ and use $(ab)^m = a^m b^m$." % n,
          "جذر کو طاقت $1/%d$ کی شکل میں لکھیں اور $(ab)^m = a^m b^m$ استعمال کریں۔" % n,
          f"{K}**Rational(1,{n}) == {k}"),
        S(f"= {k}\\cdot {pw('x', p)}\\cdot {pw('y', q)}", "Multiply the exponents: $(a^m)^n = a^{mn}$.",
          "قوتوں کو ضرب دیں: $(a^m)^n = a^{mn}$۔", f"Rational({n * p},{n}) == {p}", f"Rational({n * q},{n}) == {q}"),
    ]
    return item("indices_root", seed, 1, "Real Numbers", f"Simplify ${rad}$.",
                one(steps, f"${k}{pw('x', p)}{pw('y', q)}$"))


def gen_indices_neg(rng, seed):
    n = rng.choice([2, 3])
    k, m = rng.randint(2, 5), rng.randint(1, 4)
    K = k ** n
    steps = [
        S(f"({K})^{{-{m}/{n}}} = \\frac{{1}}{{({K})^{{{m}/{n}}}}}", "A negative exponent means the reciprocal.",
          "منفی طاقت کا مطلب معکوس ہے۔", f"{K}**Rational(-{m},{n}) == 1/{K}**Rational({m},{n})"),
        S(f"{K} = {k}^{n} \\Rightarrow ({k}^{n})^{{{m}/{n}}} = {k}^{m} = {k ** m}", "Write the base as a power and multiply the exponents.",
          "اساس کو طاقت کی شکل میں لکھیں اور قوتوں کو ضرب دیں۔", f"{K} == {k}**{n}", f"{K}**Rational({m},{n}) == {k ** m}"),
        S(f"= \\frac{{1}}{{{k ** m}}}", "Put the value back.", "قیمت واپس رکھیں۔", f"{K}**Rational(-{m},{n}) == Rational(1,{k ** m})"),
    ]
    return item("indices_neg", seed, 1, "Real Numbers", f"Simplify $({K})^{{-\\frac{{{m}}}{{{n}}}}}$.",
                one(steps, f"$\\frac{{1}}{{{k ** m}}}$"))


# ---------- Unit 1: applications ----------

def gen_profit_loss(rng, seed):
    cp = rng.randint(100, 9999)
    delta = rng.randint(1, max(2, cp // 3)) * rng.choice([1, -1])
    sp = cp + delta
    who, thing = rng.choice(NAMES), rng.choice(THINGS)
    profit = delta > 0
    amt = abs(delta)
    pct = (Decimal(amt) * 100 / Decimal(cp)).quantize(Decimal("0.01"), ROUND_HALF_UP)
    word, formula = ("profit", "SP - CP") if profit else ("loss", "CP - SP")
    first = f"\\text{{{word.capitalize()}}} = {formula} = {sp} - {cp} = {amt}" if profit else \
        f"\\text{{{word.capitalize()}}} = {formula} = {cp} - {sp} = {amt}"
    steps = [
        S(first, "%s is %s." % (word.capitalize(), "selling price minus cost price" if profit else "cost price minus selling price"),
          ("منافع = فروخت قیمت − خرید قیمت۔" if profit else "نقصان = خرید قیمت − فروخت قیمت۔"),
          f"{sp}-{cp} == {delta}" if profit else f"{cp}-{sp} == {amt}"),
        S(f"\\text{{{word.capitalize()}\\%}} = \\frac{{{amt}}}{{{cp}}}\\times 100 = {pct}\\%",
          "%s %% = %s / CP x 100." % (word.capitalize(), word),
          ("منافع فیصد = منافع / خرید قیمت × 100۔" if profit else "نقصان فیصد = نقصان / خرید قیمت × 100۔"),
          f"abs(Rational({amt}*100,{cp}) - Rational('{pct}')) < Rational(1,100)"),
    ]
    q = f"{who} bought a {thing} for Rs. {cp} and sold it for Rs. {sp}. Find the {word} percentage."
    return item("profit_loss", seed, 1, "Real Numbers", q, one(steps, f"${pct}\\%$ {word}"))


def gen_ratio_share(rng, seed):
    r = sorted(rng.sample(range(1, 16), 3))
    S_ = sum(r)
    T_ = S_ * rng.randint(1, 9) * 1000
    names = rng.sample(NAMES, 3)
    shares = [T_ * x // S_ for x in r]
    steps = [S(f"\\text{{Sum of ratios}} = {r[0]}+{r[1]}+{r[2]} = {S_}", "Add the parts of the ratio.", "تناسب کے حصے جمع کریں۔",
               f"{r[0]}+{r[1]}+{r[2]} == {S_}")]
    for nm, x, sh in zip(names, r, shares):
        steps.append(S(f"\\text{{{nm}}} = \\frac{{{x}}}{{{S_}}}\\times {T_} = {sh}",
                       "Each person gets (own part / %d) of the profit." % S_, "ہر شخص کو (اپنا حصہ / %d) کے برابر منافع ملتا ہے۔" % S_,
                       f"Rational({x},{S_})*{T_} == {sh}"))
    q = (f"{names[0]}, {names[1]} and {names[2]} earned a profit of Rs. {T_} from a business. Their investments "
         f"are in the ratio {r[0]} : {r[1]} : {r[2]}. Find each person's profit.")
    ans = "; ".join(f"{nm} Rs. {sh}" for nm, sh in zip(names, shares))
    return item("ratio_share", seed, 1, "Real Numbers", q, one(steps, ans))


def gen_simple_rate(rng, seed):
    pr = 100 * rng.randint(5, 900)
    t, rate = rng.randint(1, 10), rng.randint(2, 15)
    prof = pr * rate * t // 100
    steps = [
        S("\\text{Rate} = \\frac{\\text{profit}\\times 100}{\\text{time}\\times\\text{principal}}", "Use the formula for the rate of simple profit.",
          "سادہ منافع کی شرح کا فارمولا استعمال کریں۔"),
        S(f"= \\frac{{{prof}\\times 100}}{{{t}\\times {pr}}} = {rate}\\%", "Substitute the values and simplify.", "قیمتیں رکھیں اور سادہ کریں۔",
          f"Rational({prof}*100,{t}*{pr}) == {rate}"),
    ]
    q = f"If the simple profit on Rs. {pr} for {t} years is Rs. {prof}, find the rate of profit."
    return item("simple_rate", seed, 1, "Real Numbers", q, one(steps, f"${rate}\\%$"))


def gen_temperature(rng, seed):
    c = 5 * rng.randint(-4, 24)
    f = 9 * c // 5 + 32
    if rng.random() < 0.5:
        steps = [
            S(f"^\\circ C = \\frac{{5}}{{9}}({f}-32) = {c}", "Use $^\\circ C = \\frac{5}{9}(F-32)$.",
              "فارمولا $^\\circ C = \\frac{5}{9}(F-32)$ استعمال کریں۔", f"Rational(5,9)*({f}-32) == {c}"),
            S(f"K = {c} + 273 = {c + 273}", "Add 273 to get Kelvin.", "کیلون کے لیے 273 جمع کریں۔", f"{c}+273 == {c + 273}"),
        ]
        return item("temperature", seed, 1, "Real Numbers", f"Convert {f} °F into Celsius and Kelvin scales.",
                    one(steps, f"${c}^{{\\circ}}C$ and ${c + 273}\\text{{ K}}$"))
    steps = [S(f"^\\circ F = \\frac{{9}}{{5}}({c}) + 32 = {f}", "Use $F = \\frac{9}{5}C + 32$.",
               "فارمولا $F = \\frac{9}{5}C + 32$ استعمال کریں۔", f"Rational(9,5)*({c}) + 32 == {f}")]
    return item("temperature", seed, 1, "Real Numbers", f"Convert {c} °C into Fahrenheit.", one(steps, f"${f}^{{\\circ}}F$"))


# ---------- Unit 2: Logarithms (scientific notation) ----------

def _mantissa(rng):
    ip = rng.randint(1, 9)
    kind = rng.random()
    if kind < 0.2:
        return str(ip)
    frac_digits = rng.randint(1, 2)
    fd = "".join(str(rng.randint(0, 9)) for _ in range(frac_digits))
    if fd.endswith("0"):
        fd = fd[:-1] + str(rng.randint(1, 9))
    return f"{ip}.{fd}"


def gen_sci(rng, seed):
    m = _mantissa(rng)
    n = rng.choice([x for x in range(-8, 10) if abs(x) >= 2])
    ordinary = dec_str(Decimal(m).scaleb(n))
    chk = f"Rational('{m}')*10**({n}) == Rational('{ordinary}')"
    direction = "left" if n > 0 else "right"
    sign = "positive" if n > 0 else "negative"
    if rng.random() < 0.5:
        steps = [
            S(f"{m}", "Move the decimal point so that the number is between 1 and 10.", "اعشاری نقطہ اس طرح منتقل کریں کہ عدد 1 اور 10 کے درمیان آ جائے۔"),
            S(f"\\text{{places moved}} = {abs(n)}", "Count the places the decimal point moved.", "اعشاری نقطہ کتنے مقام منتقل ہوا، گنیں۔"),
            S(f"{ordinary} = {m}\\times 10^{{{n}}}",
              f"The decimal moved to the {direction}, so the exponent is {sign}.",
              ("اعشاری نقطہ بائیں طرف گیا، اس لیے قوت مثبت ہے۔" if n > 0 else "اعشاری نقطہ دائیں طرف گیا، اس لیے قوت منفی ہے۔"), chk),
        ]
        return item("sci", seed, 2, "Logarithms", f"Convert {ordinary} to scientific notation.", one(steps, f"${m}\\times 10^{{{n}}}$"))
    move = "right" if n > 0 else "left"
    steps = [
        S(f"\\text{{Coefficient}} = {m}, \\quad \\text{{Exponent}} = 10^{{{n}}}", "Identify the coefficient and the power of 10.",
          "عددی سر اور 10 کی طاقت پہچانیں۔"),
        S(f"{m}\\times 10^{{{n}}} = {ordinary}", f"The exponent is {sign} {abs(n)}, so move the decimal point {abs(n)} places to the {move}.",
          ("قوت مثبت ہے، اس لیے اعشاری نقطہ دائیں طرف منتقل کریں۔" if n > 0 else "قوت منفی ہے، اس لیے اعشاری نقطہ بائیں طرف منتقل کریں۔"), chk),
    ]
    return item("sci", seed, 2, "Logarithms", f"Convert ${m}\\times 10^{{{n}}}$ to ordinary notation.", one(steps, f"${ordinary}$"))


# ---------- Unit 1: question types the first training run was missing ----------

def tex_rat(r):
    """sympy Rational -> LaTeX (positive values only)."""
    return frac(int(r.p), int(r.q))


def _fr(n, d):
    from sympy import Rational
    return Rational(n, d)


def gen_classify(rng, seed):
    from fractions import Fraction
    from math import isqrt
    kinds = ["term", "rec1", "rec2", "mixed", "sqrt", "sqrt", "nonrec", "pi_e"]
    parts, exprs = [], []
    chosen = rng.sample(kinds, 4)
    if not any(k in ("sqrt", "nonrec", "pi_e") for k in chosen):
        chosen[-1] = "sqrt"
    if not any(k in ("term", "rec1", "rec2", "mixed") for k in chosen):
        chosen[0] = "term"
    for lab, kind in zip(["i", "ii", "iii", "iv"], chosen):
        if kind == "term":
            ip, fd = rng.randint(0, 9), "".join(str(rng.randint(0, 9)) for _ in range(rng.randint(1, 3)))
            fd = fd[:-1] + str(rng.randint(1, 9))
            s = f"{ip}.{fd}"
            f = Fraction(s)
            expr = s
            steps = [T(f"{s} has a finite number of digits after the decimal point, so it is a terminating decimal and therefore rational.",
                       f"{s} میں اعشاریہ کے بعد ہندسے محدود ہیں، یہ محدود اعشاری عدد ہے، اس لیے ناطق ہے۔",
                       f"Rational('{s}') == Rational({f.numerator},{f.denominator})")]
            ans = "Rational"
        elif kind in ("rec1", "rec2", "mixed"):
            if kind == "rec2":
                ab = rng.randint(10, 98)
                digits = f"{ab:02d}"
                f, expr = Fraction(ab, 99), f"0.\\overline{{{digits}}}"
                shown = f"0.{digits}{digits}{digits}\\ldots"
                chk = f"99*Rational({f.numerator},{f.denominator}) == {ab}"
            else:
                d = rng.randint(1, 8)
                ip = rng.randint(1, 9) if kind == "mixed" else 0
                f, expr = Fraction(d, 9) + ip, f"{ip}.\\bar{{{d}}}"
                shown = f"{ip}.{d}{d}{d}{d}\\ldots"
                chk = f"9*(Rational({f.numerator},{f.denominator}) - {ip}) == {d}"
            steps = [S(f"{expr} = {shown}", "The digits repeat forever, so this is a non-terminating recurring decimal. It can be written as p/q, so it is rational.",
                       "ہندسے بار بار دہرائے جاتے ہیں، یہ غیر محدود دوری اعشاری عدد ہے۔ اسے p/q کی شکل میں لکھا جا سکتا ہے، اس لیے ناطق ہے۔",
                       chk)]
            ans = "Rational"
        elif kind == "sqrt":
            n = rng.choice([x for x in range(2, 40) if isqrt(x) ** 2 != x])
            expr = f"\\sqrt{{{n}}}"
            k = isqrt(n)
            steps = [T(f"{n} lies between the consecutive squares {k * k} and {(k + 1) ** 2}, so it is not a perfect square. Therefore $\\sqrt{{{n}}}$ is a non-terminating, non-recurring decimal and is irrational.",
                       f"{n} دو متواتر مربعات {k * k} اور {(k + 1) ** 2} کے درمیان ہے، یہ مکمل مربع نہیں۔ اس لیے $\\sqrt{{{n}}}$ غیر محدود غیر دوری اعشاری عدد ہے اور غیر ناطق ہے۔",
                       f"floor(sqrt({n}))**2 < {n}", f"(floor(sqrt({n}))+1)**2 > {n}")]
            ans = "Irrational"
        elif kind == "nonrec":
            ds = "".join(str(rng.randint(0, 9)) for _ in range(8))
            expr = f"{rng.randint(1, 4)}.{ds}\\ldots"
            steps = [T("The decimal does not end and no group of digits repeats, so it is non-terminating and non-recurring, hence irrational.",
                       "اعشاری عدد ختم نہیں ہوتا اور ہندسوں کا کوئی گروہ دہرایا نہیں جاتا، اس لیے یہ غیر ناطق ہے۔")]
            ans = "Irrational"
        else:
            sym = rng.choice(["\\pi", "e"])
            expr = sym
            steps = [T(f"${sym}$ is a well-known non-terminating, non-recurring decimal, so it is irrational.",
                       f"${sym}$ ایک معروف غیر محدود غیر دوری اعشاری عدد ہے، اس لیے غیر ناطق ہے۔")]
            ans = "Irrational"
        parts.append(P(lab, steps, ans, prompt=f"${expr}$"))
        exprs.append(f"({lab}) ${expr}$")
    q = "Identify the following as rational or irrational numbers: " + " ".join(exprs)
    return item("classify", seed, 1, "Real Numbers", q, parts)


def gen_numberline(rng, seed):
    import math
    pairs = [(1, 1), (2, 1), (3, 1), (3, 2), (4, 1), (4, 2), (5, 1), (5, 2), (5, 3), (6, 1), (6, 2), (6, 3)]   # triangles that fit the canvas
    a, b = rng.choice(pairs)
    n = a * a + b * b
    unit = 88 / (a + 2)
    ay = 46.0   # axis height; labels go below it and the triangle above, all inside the 100 x 60 canvas

    def nx(v):
        return round(6 + v * unit, 2)

    ox, ax = nx(0), nx(a)
    by = round(ay - b * unit, 2)
    theta = round(math.degrees(math.atan2(b, a)), 1)
    px = nx(math.sqrt(n))
    r = round(math.sqrt(n) * unit, 2)
    line = {"t": "numberline", "from": 0, "to": a + 2, "y": ay}
    steps = [
        S(f"\\sqrt{{{n}}} = \\sqrt{{{a}^2+{b}^2}}",
          f"Write {n} as a sum of two squares: {n} = {a}^2 + {b}^2. Then $\\sqrt{{{n}}}$ is the hypotenuse of a right triangle with legs {a} and {b}.",
          f"{n} کو دو مربعات کے مجموعے کی شکل میں لکھیں: {n} = {a}^2 + {b}^2۔ تب $\\sqrt{{{n}}}$ اس قائمۃ الزاویہ مثلث کا وتر ہے جس کے ضلع {a} اور {b} ہیں۔",
          f"sqrt({n}) == sqrt({a}**2 + {b}**2)", draw=[line]),
        S(f"m\\overline{{OA}} = {a}, \\quad m\\overline{{AB}} = {b}",
          f"Mark O at 0 and A at {a} on the number line. At A draw AB = {b} unit(s) perpendicular to the line. This gives the right-angled triangle OAB.",
          f"نمبر لائن پر O کو 0 پر اور A کو {a} پر لگائیں۔ A پر خط کے عمود {b} اکائی کا AB کھینچیں۔ یوں قائمۃ الزاویہ مثلث OAB بنتا ہے۔",
          draw=[{"t": "poly", "p": [ox, ay, ax, ay, ax, by], "close": True},
                {"t": "right", "p": [ax, ay], "d": [-1, 0, 0, -1]},
                {"t": "text", "p": [ox - 2, ay + 12], "s": "O"}, {"t": "text", "p": [ax, ay + 12], "s": "A"},
                {"t": "text", "p": [ax + 3, by], "s": "B"}]),
        S(f"(m\\overline{{OB}})^2 = {a}^2 + {b}^2 = {n} \\;\\Rightarrow\\; m\\overline{{OB}} = \\sqrt{{{n}}}",
          "By the Pythagoras theorem, the hypotenuse OB is the square root of the sum of the squares of the legs.",
          "فیثاغورث کے قضیے سے وتر OB اضلاع کے مربعات کے مجموعے کا جذر ہے۔",
          f"{a}**2 + {b}**2 == {n}"),
        S(f"|\\overline{{OP}}| = \\sqrt{{{n}}}",
          "With O as the centre and radius OB, draw an arc. It cuts the number line at P, so P represents the required number.",
          "O کو مرکز اور OB کو رداس لے کر قوس کھینچیں۔ یہ نمبر لائن کو P پر کاٹتی ہے، اس لیے P مطلوبہ عدد کو ظاہر کرتا ہے۔",
          draw=[{"t": "arc", "c": [ox, ay], "r": r, "a": [-theta, 0]}, {"t": "dot", "p": [px, ay]},
                {"t": "text", "p": [px, ay + 12], "s": "P"}]),
    ]
    ans = f"P represents $\\sqrt{{{n}}}$ on the number line, since OP = $\\sqrt{{{n}}}$."
    return item("numberline", seed, 1, "Real Numbers", f"Represent $\\sqrt{{{n}}}$ on a number line.", one(steps, ans))


def gen_distributive(rng, seed):
    from sympy import Rational
    while True:
        a, b, c = (_fr(rng.randint(1, 7), rng.randint(2, 5)) for _ in range(3))
        if (a, b, c) != (Rational(2, 3), Rational(3, 2), Rational(5, 3)):
            break

    def R(x):
        return f"Rational({int(x.p)},{int(x.q)})"

    s_bc, s_ab = b + c, a + b
    left, right = a * s_bc, a * b + a * c
    left2, right2 = s_ab * c, a * c + b * c
    p1 = [
        S(f"\\text{{LHS}} = a(b+c) = {tex_rat(a)}\\left({tex_rat(b)}+{tex_rat(c)}\\right) = {tex_rat(a)}\\left({tex_rat(s_bc)}\\right) = {tex_rat(left)}",
          "First add inside the bracket, then multiply by a.", "پہلے قوسین کے اندر جمع کریں، پھر a سے ضرب دیں۔",
          f"{R(b)}+{R(c)} == {R(s_bc)}", f"{R(a)}*({R(s_bc)}) == {R(left)}"),
        S(f"\\text{{RHS}} = ab+ac = {tex_rat(a * b)}+{tex_rat(a * c)} = {tex_rat(right)}",
          "Multiply a by b and by c separately, then add.", "a کو b اور c سے الگ الگ ضرب دیں، پھر جمع کریں۔",
          f"{R(a)}*{R(b)} + {R(a)}*{R(c)} == {R(right)}"),
        T("LHS = RHS, so a(b+c) = ab+ac is verified.", "LHS = RHS ہے، لہذا a(b+c) = ab+ac کی تصدیق ہوگئی۔"),
    ]
    p2 = [
        S(f"\\text{{LHS}} = (a+b)c = \\left({tex_rat(a)}+{tex_rat(b)}\\right){tex_rat(c)} = {tex_rat(s_ab)}\\cdot{tex_rat(c)} = {tex_rat(left2)}",
          "First add inside the bracket, then multiply by c.", "پہلے قوسین کے اندر جمع کریں، پھر c سے ضرب دیں۔",
          f"{R(a)}+{R(b)} == {R(s_ab)}", f"({R(s_ab)})*{R(c)} == {R(left2)}"),
        S(f"\\text{{RHS}} = ac+bc = {tex_rat(a * c)}+{tex_rat(b * c)} = {tex_rat(right2)}",
          "Multiply a by c and b by c separately, then add.", "a کو c سے اور b کو c سے الگ الگ ضرب دیں، پھر جمع کریں۔",
          f"{R(a)}*{R(c)} + {R(b)}*{R(c)} == {R(right2)}"),
        T("LHS = RHS, so (a+b)c = ac+bc is verified.", "LHS = RHS ہے، لہذا (a+b)c = ac+bc کی تصدیق ہوگئی۔"),
    ]
    parts = [P("i", p1, f"Verified: ${tex_rat(left)} = {tex_rat(right)}$", prompt="Left distributive property"),
             P("ii", p2, f"Verified: ${tex_rat(left2)} = {tex_rat(right2)}$", prompt="Right distributive property")]
    q = f"If $a={tex_rat(a)}$, $b={tex_rat(b)}$, $c={tex_rat(c)}$ then verify the distributive properties over addition."
    return item("distributive", seed, 1, "Real Numbers", q, parts)


def _prop_templates(rng):
    """(property name, statement in LaTeX, sympy check, English, Urdu) built from random numbers."""
    a, b, c = (rng.randint(2, 15) for _ in range(3))
    p, k = rng.randint(5, 30), rng.randint(1, 9)
    x, u = rng.randint(1, 9), rng.randint(1, 9)
    y, v = x + rng.randint(1, 9), u + rng.randint(1, 9)
    nn = rng.randint(1, 5)
    lo, hi = -(nn + rng.randint(1, 6)), -nn          # lo < hi < 0
    cneg = -rng.randint(2, 6)
    return [
        ("Associative property of addition", f"{a}+({b}+{c}) = ({a}+{b})+{c}", f"{a}+({b}+{c}) == ({a}+{b})+{c}",
         "Changing the grouping of the numbers does not change the sum.", "جمع میں اعداد کی گروہ بندی بدلنے سے مجموعہ نہیں بدلتا۔"),
        ("Commutative property of addition", f"{a}+{b} = {b}+{a}", f"{a}+{b} == {b}+{a}",
         "Changing the order of the numbers does not change the sum.", "جمع میں اعداد کی ترتیب بدلنے سے مجموعہ نہیں بدلتا۔"),
        ("Associative property of multiplication", f"{a}\\times({b}\\times{c}) = ({a}\\times{b})\\times{c}", f"{a}*({b}*{c}) == ({a}*{b})*{c}",
         "Changing the grouping of the numbers does not change the product.", "ضرب میں اعداد کی گروہ بندی بدلنے سے حاصل ضرب نہیں بدلتا۔"),
        ("Commutative property of multiplication", f"{a}\\times{b} = {b}\\times{a}", f"{a}*{b} == {b}*{a}",
         "Changing the order of the numbers does not change the product.", "ضرب میں اعداد کی ترتیب بدلنے سے حاصل ضرب نہیں بدلتا۔"),
        ("Additive identity property", f"{a}+0 = {a}", f"{a}+0 == {a}",
         "Adding 0 to a number leaves it unchanged, so 0 is the additive identity.", "کسی عدد میں 0 جمع کرنے سے عدد نہیں بدلتا، اس لیے 0 جمعی محائدہ ہے۔"),
        ("Multiplicative identity property", f"{a}\\times 1 = {a}", f"{a}*1 == {a}",
         "Multiplying a number by 1 leaves it unchanged, so 1 is the multiplicative identity.", "کسی عدد کو 1 سے ضرب دینے سے عدد نہیں بدلتا، اس لیے 1 ضربی محائدہ ہے۔"),
        ("Additive inverse property", f"{a}+(-{a}) = 0", f"{a}+(-{a}) == 0",
         "A number plus its negative is 0, so -a is the additive inverse of a.", "کسی عدد اور اس کے منفی کا مجموعہ 0 ہوتا ہے، اس لیے -a عدد a کا جمعی معکوس ہے۔"),
        ("Multiplicative inverse property", f"{a}\\times\\frac{{1}}{{{a}}} = 1", f"{a}*Rational(1,{a}) == 1",
         "A non-zero number times its reciprocal is 1.", "غیر صفر عدد اور اس کے مقلوب کا حاصل ضرب 1 ہوتا ہے۔"),
        ("Left distributive property of multiplication over addition", f"{a}({b}+{c}) = {a}\\times{b}+{a}\\times{c}", f"{a}*({b}+{c}) == {a}*{b}+{a}*{c}",
         "Multiplying a sum by a number equals multiplying each term and adding.", "مجموعے کو کسی عدد سے ضرب دینا ہر رکن کو ضرب دے کر جمع کرنے کے برابر ہے۔"),
        ("Order property w.r.t. addition", f"\\text{{If }} a > {p} \\text{{ then }} a+{k} > {p + k}", f"{p}+{k} == {p + k}",
         "Adding the same number to both sides of an inequality keeps its direction.", "عدم مساوات کے دونوں طرف ایک ہی عدد جمع کرنے سے علامت نہیں بدلتی۔"),
        ("Order property w.r.t. addition", f"{x} < {y} \\text{{ and }} {u} < {v} \\Rightarrow {x}+{u} < {y}+{v}", f"{x}+{u} < {y}+{v}",
         "Adding two inequalities of the same direction gives an inequality in that direction.", "ایک ہی سمت کی دو عدم مساواتوں کو جمع کرنے سے اسی سمت کی عدم مساوات ملتی ہے۔"),
        ("Order property w.r.t. multiplication", f"{y} > {x} \\text{{ and }} {v} > {u} \\Rightarrow {y}\\times{v} > {x}\\times{u}", f"{y}*{v} > {x}*{u}",
         "Multiplying two inequalities of positive numbers gives an inequality in the same direction.", "مثبت اعداد کی دو عدم مساواتوں کو ضرب دینے سے اسی سمت کی عدم مساوات ملتی ہے۔"),
        ("Order property w.r.t. multiplication", f"{lo} < {hi} \\Rightarrow ({lo})({cneg}) > ({hi})({cneg})", f"({lo})*({cneg}) > ({hi})*({cneg})",
         "Multiplying both sides by a negative number reverses the inequality.", "دونوں طرف منفی عدد سے ضرب دینے پر عدم مساوات کی علامت الٹ جاتی ہے۔"),
    ]


def gen_property_name(rng, seed):
    # skip any statement that reuses the book's own example numbers, keeping the real test questions unseen
    for _ in range(50):
        chosen = rng.sample(_prop_templates(rng), 4)
        text = " ".join(t[1] for t in chosen)
        if not any(s in text for s in ("a > 13", "3 < 9", "7 > 4", "(-5)(-4)", "-5 < -4")):
            break
    parts, listing = [], []
    for lab, (name, stmt, chk, en, ur) in zip(["i", "ii", "iii", "iv"], chosen):
        parts.append(P(lab, [S(stmt, en, ur, chk)], name, prompt=f"${stmt}$"))
        listing.append(f"({lab}) ${stmt}$")
    return item("property_name", seed, 1, "Real Numbers", "Identify the property that justifies each statement: " + " ".join(listing), parts)


# ---------- multi-part questions (the book often asks (i), (ii), (iii) together) ----------

def _combine(type_name, makers, rng, seed, prefix):
    import re
    singles = [mk(rng, seed) for mk in makers]
    parts, listing = [], []
    for lab, s in zip(["i", "ii", "iii"], singles):
        expr = re.search(r"\$([^$]+)\$", s["question"]).group(1)
        part = s["parts"][0]
        parts.append(P(lab, part["steps"], part["answer"], prompt=f"${expr}$"))
        listing.append(f"({lab}) ${expr}$")
    return item(type_name, seed, 1, "Real Numbers", prefix + " " + " ".join(listing), parts)


def gen_recurring_pair(rng, seed):
    return _combine("recurring_pair", [gen_recurring1, gen_recurring2], rng, seed,
                    "Express the following recurring decimals as the rational number $\\frac{p}{q}$, where $p$ and $q$ are integers:")


def gen_rationalize_pair(rng, seed):
    return _combine("rationalize_pair", [gen_rationalize2, gen_rationalize2], rng, seed, "Rationalize the denominator:")


def gen_indices_pair(rng, seed):
    return _combine("indices_pair", [gen_indices_root, gen_indices_root, gen_indices_neg], rng, seed, "Simplify the following:")


GENERATORS = {
    "recurring1": gen_recurring1, "recurring2": gen_recurring2,
    "rationalize1": gen_rationalize1, "rationalize2": gen_rationalize2,
    "sumdiff": gen_sumdiff, "between": gen_between,
    "indices_root": gen_indices_root, "indices_neg": gen_indices_neg,
    "profit_loss": gen_profit_loss, "ratio_share": gen_ratio_share,
    "simple_rate": gen_simple_rate, "temperature": gen_temperature, "sci": gen_sci,
    "classify": gen_classify, "numberline": gen_numberline, "distributive": gen_distributive,
    "property_name": gen_property_name, "recurring_pair": gen_recurring_pair,
    "rationalize_pair": gen_rationalize_pair, "indices_pair": gen_indices_pair,
}


def generate(per_type=40, seed0=0, avoid=()):
    """per_type unique items for every generator. `avoid` is a set of question texts to skip
    (used to keep the synthetic eval set disjoint from the synthetic train set)."""
    out, seen = [], set(avoid)
    for name, fn in GENERATORS.items():
        got, seed = 0, seed0
        while got < per_type and seed < seed0 + per_type * 60:
            it = fn(random.Random(f"{name}-{seed}"), seed)
            seed += 1
            if it["question"] in seen:
                continue
            seen.add(it["question"])
            out.append(it)
            got += 1
    return out


if __name__ == "__main__":
    items = generate(per_type=3)
    print(len(items), "items;", len(GENERATORS), "types")
    for it in items[::3]:
        print("-", it["question"][:90])
