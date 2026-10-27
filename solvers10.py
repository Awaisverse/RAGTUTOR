"""Rule engine for Class 10, Unit 1 (complex numbers): solves the student's own question with checked steps.

It reuses the step templates of data/src10/_complex.py, so its working looks exactly like the stored solutions, and every
step carries sympy checks. A question it cannot read is refused (None), never guessed. The Class 9 engine is not used
for Class 10: it would treat i as an ordinary unknown.
"""
import pathlib
import re
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent
for p in (ROOT / "data" / "src", ROOT / "data" / "src10", ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import _complex as cx  # noqa: E402
from build_dataset import verify  # noqa: E402
from solvers.common import labels, part_markers  # noqa: E402

I = sp.I
_ALLOWED = re.compile(r"^[0-9a-z+\-*/().,=\s^]*$")
_NAMES = {"i", "x", "y", "a", "b", "z", "w", "sqrt"}


def _to_py(text):
    """Student text or LaTeX -> python-like text with explicit *, ** and I for i. None if it is not plain maths."""
    s = str(text).replace("$", " ").replace("\\left", "").replace("\\right", "").replace("−", "-").replace("–", "-")
    s = s.replace("÷", "/").replace("×", "*").replace("\\div", "/").replace("\\times", "*").replace("\\cdot", "*")
    s = re.sub(r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", s)
    s = re.sub(r"√\s*\(?\s*(-?\s*\d+(?:\.\d+)?)\s*\)?", r"sqrt(\1)", s)
    s = re.sub(r"\^\s*\{([^{}]*)\}", r"**(\1)", s).replace("^", "**").replace("{", "(").replace("}", ")")
    s = re.sub(r"\s+", " ", s).strip().lower()
    if not s or not _ALLOWED.match(s.replace("**", "^")):
        return None
    if set(re.findall(r"[a-z]+", s)) - _NAMES:
        return None
    # implicit multiplication: 4i, 2x, )(, )i, i(, 3(
    s = re.sub(r"(\d)\s*([a-z(])", r"\1*\2", s)
    s = re.sub(r"\)\s*([a-z0-9(])", r")*\1", s)
    s = re.sub(r"\b([ixyabzw])\s*([a-z(])", lambda m: m.group(1) + "*" + m.group(2) if not (m.group(1) + m.group(2)).startswith("sq") else m.group(0), s)
    return re.sub(r"\bi\b", "I", s)


def _sym(names):
    return {n: sp.Symbol(n) for n in names}


def _value(py_text, extra=None):
    loc = {"I": I, "sqrt": sp.sqrt, **(extra or {})}
    return sp.sympify(py_text, locals=loc)


def _complex_const(v):
    v = sp.nsimplify(sp.expand(v))
    return v if not v.free_symbols else None


def _top_binary(py_text):
    """Split 'A op B' at the top level (outside brackets). -> (A, op, B) or None."""
    depth, s = 0, py_text
    for k in range(len(s) - 1, 0, -1):            # last top-level operator binds loosest
        ch = s[k]
        depth += ch == ")"
        depth -= ch == "("
        if depth == 0 and ch in "+-" and s[k - 1] not in "*(/":
            return s[:k].strip(), ch, s[k + 1:].strip()
    depth = 0
    for k in range(len(s) - 1, 0, -1):
        ch = s[k]
        depth += ch == ")"
        depth -= ch == "("
        if depth == 0 and ch in "*/" and s[k - 1] != "*" and s[k + 1:k + 2] != "*":
            return s[:k].strip(), ch, s[k + 1:].strip()
    return None


def _strip(s):
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        for k, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and k < len(s) - 1:
                return s
        s = s[1:-1].strip()
    return s


# ------------------------------------------------------------------------------------------ one expression


def _expression_part(label, py_text, tex_prompt):
    """Simplify one complex expression. Patterns: i^n (times a number), sums of powers of i, sqrt of negatives,
    A op B with complex A, B, and z^2, z^-1, z^-2, (A/B)^n."""
    body = _strip(py_text)
    m = re.fullmatch(r"(?:(\d+)\*)?I\*\*\(?(-?\d+)\)?", body)
    if m:
        coef, n = int(m.group(1) or 1), int(m.group(2))
        part = cx.p_ipower(label, n, coef)
        part["prompt"] = tex_prompt or part["prompt"]
        return part
    if re.fullmatch(r"[\sI*()\-+\d]+", body) and "I**" in body and re.fullmatch(r"(?:\s*[+-]?\s*I\*\*\(?-?\d+\)?)+", body):
        terms = re.findall(r"([+-]?)\s*I\*\*\(?(-?\d+)\)?", body)
        value = sum((-1 if s == "-" else 1) * I ** int(n) for s, n in terms)
        reduced = " ".join(f"{'-' if s == '-' else '+'} i^{{{int(n) % 4}}}" for s, n in terms).lstrip("+ ")
        steps = [cx.S(" ".join(f"{'-' if s == '-' else '+'} i^{{{n}}}" for s, n in terms).lstrip("+ ") + f" = {reduced}", *_FOUR,
                      f"{body} == " + " ".join(f"{s or '+'} I**{int(n) % 4}" for s, n in terms)),
                 cx.S(f"= {cx.ctex(value)}", *_VALUES, f"{body} == {cx.py(value)}")]
        return cx.P(label, steps, cx.ans(value), prompt=tex_prompt)
    if "sqrt(-" in body.replace(" ", ""):
        value = _complex_const(_value(body))
        if value is None:
            return None
        return cx.P(label, [cx.S(rf"{tex_prompt.strip('$') if tex_prompt else sp.latex(_value(body, {}))} = {cx.ctex(value)}",
                                 "For a positive number $a$, $\\sqrt{-a} = \\sqrt{a}\\sqrt{-1} = i\\sqrt{a}$.",
                                 "مثبت عدد $a$ کے لیے $\\sqrt{-a} = \\sqrt{a}\\sqrt{-1} = i\\sqrt{a}$۔", f"{body} == {cx.py(value)}")],
                    cx.ans(value), prompt=tex_prompt)
    pw = re.fullmatch(r"\((.*)\)\s*\*\*\s*\(?(-?[12])\)?", body)
    if pw:
        inner, n = _strip(pw.group(1)), int(pw.group(2))
        split = _top_binary(inner)
        if split and split[1] == "/":
            a, b = _complex_const(_value(split[0])), _complex_const(_value(split[2]))
            if a is None or b is None:
                return None
            if n < 0:
                a, b = b, a                       # (p/q)^-n = (q/p)^n
            steps, v = cx.div(a, b)
            if abs(n) == 2:
                s2, v = cx.square(v)
                steps += s2
            return cx.p_real_imag(label, tex_prompt, steps, v) if _WANT_PARTS[0] else cx.P(label, steps, cx.ans(v), prompt=tex_prompt)
        z = _complex_const(_value(inner))
        if z is None:
            return None
        if n == 2:
            steps, v = cx.square(z)
        elif n == -1:
            steps, v = cx.recip(z)
        else:
            s1, v1 = cx.square(z)
            s2, v = cx.recip(v1)
            steps = s1 + s2
        return cx.p_real_imag(label, tex_prompt, steps, v) if _WANT_PARTS[0] else cx.P(label, steps, cx.ans(v), prompt=tex_prompt)
    split = _top_binary(body)
    if split:
        a, op, b = split
        za, zb = _complex_const(_value(a)), _complex_const(_value(b))
        if za is None or zb is None or "**" in a + b:
            return None
        if op in "+-" and (sp.im(za) == 0 or sp.im(zb) == 0) and not (("(" in a) and ("(" in b)):
            return None                            # "2 + 5i" is one number, not a sum of two: nothing to simplify
        part = cx.p_arith(label, za, zb, op)
        if _WANT_PARTS[0]:
            v = sp.expand({"+": za + zb, "-": za - zb, "*": za * zb, "/": za / zb}[op])
            return cx.p_real_imag(label, tex_prompt, part["steps"], v)
        return part
    return None


_FOUR = ("Since $i^4 = 1$, adding or removing multiples of 4 in the power does not change the value.",
         "چونکہ $i^4 = 1$، طاقت میں 4 کے مضرب جمع یا تفریق کرنے سے قیمت نہیں بدلتی۔")
_VALUES = ("Use $i^1 = i,\\ i^2 = -1,\\ i^3 = -i,\\ i^4 = 1$.", "$i^1 = i,\\ i^2 = -1,\\ i^3 = -i,\\ i^4 = 1$ استعمال کریں۔")
_WANT_PARTS = [False]


def _number_part(label, intent, py_text, tex_prompt):
    z = _complex_const(_value(_strip(py_text)))
    if z is None:
        return None
    if intent == "modulus":
        return cx.p_modulus(label, z)
    if intent == "additive":
        return cx.p_additive_inverse(label, z)
    if intent == "multiplicative":
        return cx.p_multiplicative_inverse(label, z)
    if intent == "conjugate":
        zc = sp.conjugate(z)
        return cx.P(label, [cx.S(rf"\overline{{{cx.ctex(z)}}} = {cx.ctex(zc)}", "The conjugate changes the sign of the imaginary part.",
                                 "مزدوج میں خیالی حصے کی علامت بدل جاتی ہے۔", f"conjugate({cx.py(z)}) == {cx.py(zc)}")], cx.ans(zc), prompt=tex_prompt)
    return None


# ------------------------------------------------------------------------------------------ equations


def _equation_part(label, py_text, tex_prompt):
    sides = py_text.split("=")
    if len(sides) != 2:
        return None
    lhs, rhs = sides[0].strip(), sides[1].strip()
    names = set(re.findall(r"\b[xyab]\b", lhs + " " + rhs))
    for pair in (["x", "y"], ["a", "b"]):
        if names == set(pair):
            try:
                return cx.p_equal_parts(label, lhs, rhs, pair, tex_prompt)
            except (ValueError, TypeError, sp.SympifyError):
                return None
    return None


def _system_part(label, eq1, eq2, tex_prompt):
    zz, ww = sp.Symbol("z"), sp.Symbol("w")
    rows = []
    for e in (eq1, eq2):
        if e.count("=") != 1:
            return None
        lhs, rhs = (_value(t, {"z": zz, "w": ww}) for t in e.split("="))
        expr = sp.expand(lhs - rhs)
        a, b = expr.coeff(zz), expr.coeff(ww)
        c = -expr.subs({zz: 0, ww: 0})
        if sp.expand(expr - a * zz - b * ww + c) != 0 or (a.free_symbols | b.free_symbols | c.free_symbols):
            return None                            # not linear in z and w
        rows.append((sp.expand(a), sp.expand(b), sp.expand(c)))
    (a1, b1, c1), (a2, b2, c2) = rows
    if a1 == 0:
        (a1, b1, c1), (a2, b2, c2) = (a2, b2, c2), (a1, b1, c1)
    if a1 == 0 or sp.expand(a2 * b1 - a1 * b2) == 0:
        return None
    return cx.p_system(label, a1, b1, c1, a2, b2, c2, tex_prompt)


# ------------------------------------------------------------------------------------------ entry point


def _intent(text):
    t = text.lower()
    if "modulus" in t:
        return "modulus"
    if "additive inverse" in t:
        return "additive"
    if "multiplicative inverse" in t or re.search(r"\binverse\b", t):
        return "multiplicative"
    if "conjugate" in t:
        return "conjugate"
    if "real" in t and "imaginary" in t:
        return "parts"
    return "simplify"


def _math_of(text):
    """The mathematical part of a piece of question text."""
    dollars = re.findall(r"\$([^$]+)\$", text)
    if dollars:
        return " ".join(dollars) if len(dollars) == 1 else dollars
    # the maths may start after other numbers ("Exercise 1.2: simplify (7+2i)(3-5i)"): use the first start that reads as maths
    for m in re.finditer(r"[-(\d√|]|\bi\b|sqrt", text):
        candidate = text[m.start():].rstrip(".?:; ")
        if _to_py(candidate.strip().strip("|")):
            return candidate
    return ""


def _one(label, text, stem):
    intent = _intent(stem + " " + text)
    math = _math_of(text)
    if isinstance(math, list):                     # two equations: a z, w system
        if len(math) == 2 and all("=" in e for e in math):
            p1, p2 = _to_py(math[0]), _to_py(math[1])
            if p1 and p2 and {"z", "w"} & set(re.findall(r"[a-z]", p1 + p2)):
                return _system_part(label, p1, p2, f"${math[0]}$, ${math[1]}$")
        return None
    math = math.strip().strip("|")
    py_text = _to_py(math)
    if not py_text:
        return None
    tex_prompt = f"${math}$"
    try:
        if "=" in py_text:
            if "," in py_text and re.search(r"\bz\b", py_text):
                e1, e2 = py_text.split(",", 1)
                return _system_part(label, e1, e2, tex_prompt)
            return _equation_part(label, py_text, tex_prompt)
        if intent in ("modulus", "additive", "multiplicative", "conjugate"):
            return _number_part(label, intent, py_text, tex_prompt)
        _WANT_PARTS[0] = intent == "parts"
        return _expression_part(label, py_text, tex_prompt)
    except (sp.SympifyError, TypeError, ValueError, ZeroDivisionError, SyntaxError, AttributeError):
        return None
    finally:
        _WANT_PARTS[0] = False


def solve(text):
    """-> a solved item for this question, or None when it is not a Class 10 complex-number question the engine knows."""
    pieces = part_markers(text)
    stem = pieces[0]
    texts = [p for p in pieces[1:] if p.strip()] if len(pieces) > 1 else [text]
    names = labels(len(texts)) if len(texts) > 1 else [""]
    parts = []
    for lab, t in zip(names, texts):
        p = _one(lab, t, stem if len(texts) > 1 else "")
        if p is None:
            return None                            # all parts or nothing: a partial answer looks complete
        parts.append(p)
    for p in parts:
        for st in p["steps"]:
            for chk in st.get("check", []):
                try:
                    if not verify(chk):
                        return None
                except Exception:
                    return None
    question = text.strip()
    return {"id": "solved10-" + re.sub(r"[^a-z0-9]+", "-", question.lower())[:40].strip("-"), "kind": "solved", "number": "", "page": 0,
            "question": question, "parts": parts, "verified": True, "source": "solver", "unit": 1, "unit_title": "Complex Numbers",
            "class": 10}
