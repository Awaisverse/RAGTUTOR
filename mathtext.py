"""Reading a student's question: normalise the text, compare questions by their numbers, and parse maths safely.

Three jobs:
  clean(text)             typed text / LaTeX -> plain text with number words as digits, unicode symbols as ASCII
  signature(text)         the numbers and +/- signs of a question, in order. Two questions are "the same question"
                          only when these agree, so "13/(4+sqrt3)" never matches "3/(5+sqrt2)".
  parse_math(text)        a maths expression (typed or LaTeX) -> sympy expression. The text is checked against a
                          whitelist first, because the parser evaluates what it is given.
"""
import re

import sympy as sp
from sympy.parsing.sympy_parser import convert_xor, implicit_multiplication_application, parse_expr, standard_transformations

_ONES = {"two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11,
         "twelve": 12, "thirteen": 13, "fourteen": 14, "fifteen": 15, "sixteen": 16, "seventeen": 17, "eighteen": 18, "nineteen": 19}
_ONE = {"one": 1, **_ONES}
_TENS = {"twenty": 20, "thirty": 30, "forty": 40, "fifty": 50, "sixty": 60, "seventy": 70, "eighty": 80, "ninety": 90}


def words_to_digits(text):
    """'forty-two' -> '42', 'three' -> '3'. The word 'one' alone is left (it is mostly the pronoun)."""
    t = re.sub(r"\b(" + "|".join(_TENS) + r")[\s-]+(" + "|".join(_ONE) + r")\b",
               lambda m: str(_TENS[m.group(1).lower()] + _ONE[m.group(2).lower()]), text, flags=re.I)
    return re.sub(r"\b(" + "|".join(list(_ONES) + list(_TENS)) + r")\b",
                  lambda m: str({**_ONES, **_TENS}[m.group(1).lower()]), t, flags=re.I)


def clean(text):
    t = str(text)
    for old, new in (("√", " sqrt "), ("−", "-"), ("–", "-"), ("—", "-"), ("×", "*"), ("÷", "/"), ("·", "*"), ("²", "^2"), ("³", "^3"),
                     ("π", " pi "), ("°", " deg "), ("’", "'"), ("“", '"'), ("”", '"'), ("…", "..."), ("$", " ")):
        t = t.replace(old, new)
    t = re.sub(r"\b\d{1,3}(?:,\d{3})+\b|\b\d{1,2}(?:,\d{2})*,\d{3}\b", lambda m: m.group(0).replace(",", ""), t)   # 78,000,000 and 9,60,000
    t = words_to_digits(t)
    t = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " ", t)                                        # non-terminating -> non terminating
    return t.lower()


def signature(text):
    """Numbers and + / - signs of the question, in order. LaTeX commands and ordinary words contribute nothing."""
    t = re.sub(r"\\[a-zA-Z]+", " ", clean(text))
    return re.findall(r"\d+(?:\.\d+)?|[+\-]", t)


_TASKS = {"identify": "classify", "classify": "classify", "express": "convert", "convert": "convert", "write": "convert", "change": "convert",
          "rationalize": "rationalize", "rationalise": "rationalize", "simplify": "simplify", "evaluate": "simplify", "verify": "verify",
          "represent": "represent", "name": "name", "state": "state", "solve": "solve", "prove": "prove", "show": "prove"}


def task_of(text):
    """The instruction word of a question ('express', 'identify', 'rationalize', ...) or None. 'find' is too general to count."""
    m = re.search(r"\b(" + "|".join(_TASKS) + r")\b", str(text).lower())
    return _TASKS[m.group(1)] if m else None


def same_question(query, item):
    """Is `query` the same question as the stored item (or one of its parts)? -> (True, part_index or None) or (False, None).

    The comparison is by numbers and signs in order. A student may type the whole question, or one part with the stem
    (the sentence before "(i)"), or just the part, so those three forms are all accepted."""
    q = signature(query)
    if len(q) < 2:
        return False, None
    question = item["question"]
    asked, stored = task_of(query), task_of(question)
    if asked and stored and asked != stored:       # same numbers but a different instruction ("express" vs "identify")
        return False, None
    if q == signature(question):
        return True, None
    stem = re.split(r"\s*\(i\)\s", question, maxsplit=1)[0] if len(item["parts"]) > 1 else ""
    stem_sig = signature(stem) if stem else []
    for i, part in enumerate(item["parts"]):
        prompt = signature(part.get("prompt", ""))
        if not prompt:
            continue
        if q in (prompt, stem_sig + prompt, prompt + stem_sig):
            return True, i
    return False, None


# ---------------------------------------------------------------- LaTeX / typed text -> python expression text

def _group(s, i):
    """s[i] == '{': return (content, index after the matching '}')."""
    depth = 0
    for j in range(i, len(s)):
        if s[j] == "{":
            depth += 1
        elif s[j] == "}":
            depth -= 1
            if depth == 0:
                return s[i + 1:j], j + 1
    return s[i + 1:], len(s)


def latex_to_py(s):
    s = re.sub(r"\\(left|right|big|Big|displaystyle)\b", "", s.replace("$", ""))
    for old in ("\\,", "\\;", "\\!", "\\ ", "\\quad", "\\qquad"):
        s = s.replace(old, " ")
    out, i = "", 0
    while i < len(s):
        if re.match(r"\\[dt]?frac", s[i:]):
            j = s.index("{", i)
            a, k = _group(s, j)
            while k < len(s) and s[k] == " ":
                k += 1
            b, k = _group(s, k)
            out += f"(({latex_to_py(a)})/({latex_to_py(b)}))"
            i = k
        elif s.startswith("\\sqrt", i):
            j = i + 5
            if s[j:j + 1] == "[":
                close = s.index("]", j)
                n = s[j + 1:close]
                a, i = _group(s, close + 1)
                out += f"root({latex_to_py(a)},{latex_to_py(n)})"
            elif s[j:j + 1] == "{":
                a, i = _group(s, j)
                out += f"sqrt({latex_to_py(a)})"
            else:
                m = re.match(r"\s*(\d+(?:\.\d+)?|[a-zA-Z])", s[j:])
                out += f"sqrt({m.group(1)})" if m else "sqrt"
                i = j + (m.end() if m else 0)
        elif s.startswith("\\text", i):
            a, i = _group(s, s.index("{", i))
            out += " " + a + " "
        elif s.startswith("\\times", i) or s.startswith("\\cdot", i):
            out += "*"
            i += 6 if s.startswith("\\times", i) else 5
        elif s.startswith("\\div", i):
            out += "/"
            i += 4
        elif s.startswith("\\pi", i):
            out += " pi "
            i += 3
        elif s.startswith("\\ldots", i) or s.startswith("\\dots", i):
            out += "..."
            i += 6 if s.startswith("\\ldots", i) else 5
        elif s[i] == "^" and s[i + 1:i + 2] == "{":
            a, i = _group(s, i + 1)
            out += f"**({latex_to_py(a)})"
        elif s[i] == "^":
            out += "**"
            i += 1
        elif s[i] in "{}":
            i += 1
        elif s[i] == "\\":
            m = re.match(r"\\[a-zA-Z]+", s[i:])
            i += m.end() if m else 1
        else:
            out += s[i]
            i += 1
    return out


def ascii_to_py(s):
    t = clean(s)
    t = re.sub(r"cube\s*root\s*(?:of)?\s*(\d+(?:\.\d+)?|[a-z])", r"root(\1,3)", t)
    # "4sqrt3", "sqrt 3", "root3", "sqrt(3)" all mean a square root; a digit may come right before the word
    t = re.sub(r"(?<![a-z])(?:sqrt|root)\s*\(", "sqrt(", t)
    t = re.sub(r"(?<![a-z])(?:sqrt|root)\s*(?:of\s*)?(\d+(?:\.\d+)?|[a-z])(?![a-z0-9])", r"sqrt(\1)", t)
    t = re.sub(r"(?<![a-z])pi(?![a-z])", " pi ", t)
    return t.replace("^", "**")


def to_py(text):
    """Typed text or LaTeX -> the python-style text that parse_math reads (no evaluation)."""
    raw = text.strip()
    s = latex_to_py(raw) if ("\\" in raw or "{" in raw) else ascii_to_py(raw)
    return re.sub(r"\s+", " ", s).strip()


def split_power(text):
    """'(81/16)^(-3/4)' -> ('(81/16)', '(-3/4)'). Only for text that is a single power at the top level, else None."""
    s = to_py(text)
    depth, cuts = 0, []
    for i, ch in enumerate(s):
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and s.startswith("**", i) and (i == 0 or s[i - 1] != "*") and s[i + 2:i + 3] != "*":
            cuts.append(i)
    if len(cuts) != 1:
        return None
    left, right = s[:cuts[0]].strip(), s[cuts[0] + 2:].strip()
    top = lambda part: re.sub(r"\([^()]*\)", "", part)  # noqa: E731
    for part in (left, right):
        flat = part
        while flat != top(flat):
            flat = top(flat)
        if re.search(r"[+*/]", flat) or re.search(r"(?<!^)-", flat):   # an operator outside brackets: not a plain power
            return None
    return left, right


def _strip_outer(s):
    """'((a+b))' -> 'a+b' while one pair of brackets wraps the whole text."""
    s = s.strip()
    while s.startswith("(") and s.endswith(")"):
        depth = 0
        for i, ch in enumerate(s):
            depth += ch == "("
            depth -= ch == ")"
            if depth == 0 and i < len(s) - 1:
                return s
        s = s[1:-1].strip()
    return s


def split_fraction(text):
    """'13/(4+sqrt3)' or \\frac{13}{4+\\sqrt{3}} -> ('13', '(4+sqrt(3))'): the numerator and denominator as written.

    Parsing the whole thing would let sympy rewrite 1/sqrt(13) as sqrt(13)/13 and hide the denominator the
    student asked to rationalize. Returns None unless the text is exactly one fraction."""
    s = _strip_outer(to_py(text))
    depth, cuts, top_sign = 0, [], False
    for i, ch in enumerate(s):
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0:
            if ch == "/":
                cuts.append(i)
            elif ch in "+-" and i > 0:
                top_sign = True       # 13/4+sqrt3 means (13/4)+sqrt3, not a single fraction
    if len(cuts) != 1 or top_sign:
        return None
    return _strip_outer(s[:cuts[0]]), _strip_outer(s[cuts[0] + 1:])


_TRANSFORMS = standard_transformations + (implicit_multiplication_application, convert_xor)
_ALLOWED_NAMES = {"sqrt", "root", "pi", "cbrt"}
_LOCALS = {"sqrt": sp.sqrt, "root": sp.root, "pi": sp.pi, "cbrt": sp.cbrt, "Rational": sp.Rational}
for _c in "abcdfghjklmnpqrstuvwxyz":
    _LOCALS[_c] = sp.Symbol(_c, positive=True)
_LOCALS["e"] = sp.Symbol("e", positive=True)   # a letter, never Euler's number, unless the caller decides otherwise


def parse_math(text):
    """Typed text or LaTeX -> sympy expression. Raises ValueError when the text is not a plain maths expression."""
    raw = text.strip()
    s = latex_to_py(raw) if ("\\" in raw or "{" in raw) else ascii_to_py(raw)
    s = re.sub(r"\s+", " ", s).strip()
    if not s or len(s) > 300:
        raise ValueError("empty or too long")
    if re.search(r"[^0-9A-Za-z_+\-*/().,\s]", s):
        raise ValueError(f"unsupported characters in {s!r}")
    # every identifier must be a known function or a single letter; anything else (e.g. "sqrt3", "os") is refused,
    # never split into letters, because a wrong parse would give a confident wrong answer
    for name in re.findall(r"[A-Za-z_][A-Za-z_0-9]*", s):
        if name not in _ALLOWED_NAMES and len(name) > 1:
            raise ValueError(f"unknown word {name!r}")
    s = re.sub(r"(?<![\w.])(\d+\.\d+)(?![\w.])", r"Rational('\1')", s)   # 0.027 is the exact fraction 27/1000, not a float
    try:
        return parse_expr(s, local_dict=_LOCALS, transformations=_TRANSFORMS, evaluate=True)
    except Exception as exc:
        raise ValueError(f"cannot read {s!r}: {exc}") from exc
