"""The Class 11 engine: Unit 1 (Complex Numbers) of the Punjab Class 11 book.

    solve(text) -> a solved item whose every step is checked, or None

The new Class 11 topics are solved with the very templates that wrote the book (data/src11): square roots of a complex
number and (x + iy)^2 = w, the multiplicative inverse of an ordered pair, polar form, cube and fourth roots of a number,
factorizing a polynomial into linear factors, solving polynomial equations (completing the square for quadratics) and a
polynomial with given zeros. Plain complex arithmetic, conjugates, moduli and equations go to the Class 10 complex-number
engine. Every step of every part is checked with sympy; all parts or nothing.
"""
import importlib.util
import pathlib
import re
import sys

import sympy as sp

import solvers10

ROOT = pathlib.Path(__file__).resolve().parent
for _p in (ROOT / "tools", ROOT / "data" / "src", ROOT / "data" / "src10", ROOT / "data" / "src11"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))
from build_dataset import verify  # noqa: E402
from solvers.common import labels, part_markers  # noqa: E402

I = sp.I
Z = sp.Symbol("z")
_U = {}


def _unit():
    """The Class 11 Unit 1 source module (its templates), loaded once."""
    if "m" not in _U:
        spec = importlib.util.spec_from_file_location("src11_unit01", ROOT / "data" / "src11" / "unit01.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _U["m"] = mod
    return _U["m"]


def _num(text):
    """A complex number (or real expression) typed by a student, or None."""
    py = solvers10._to_py(text.strip().strip(".?:;,"))
    if not py or re.search(r"[a-hj-z]", py.replace("sqrt", "").replace("I", "")):
        return None
    try:
        v = sp.nsimplify(sp.sympify(py, locals={"I": I, "sqrt": sp.sqrt}), rational=True) if "." in py else sp.sympify(py, locals={"I": I, "sqrt": sp.sqrt})
        v = sp.expand(sp.radsimp(v))
        return v if v.is_number else None
    except (sp.SympifyError, TypeError, SyntaxError, ZeroDivisionError):
        return None


def _poly(text):
    """A polynomial in z with numeric (possibly complex) coefficients, or None."""
    py = solvers10._to_py(text.split("=")[0])
    if not py or set(re.findall(r"[a-z]+", py)) - {"z", "sqrt"}:
        return None
    try:
        p = sp.expand(sp.sympify(py, locals={"z": Z, "I": I, "sqrt": sp.sqrt}))
        rhs = text.split("=")[1] if "=" in text else "0"
        r = _num(rhs) if rhs.strip() not in ("", "0") else 0
        if r is None:
            return None
        p = sp.expand(p - r)
        return p if p.is_polynomial(Z) and sp.degree(p, Z) >= 2 else None
    except (sp.SympifyError, TypeError, SyntaxError, sp.PolynomialError):
        return None


def _math(text):
    """The maths in a piece of question text (inside $...$, or the first stretch that reads as maths)."""
    d = re.findall(r"\$([^$]+)\$", text)
    if d:
        return " ".join(d)
    m = solvers10._math_of(text)
    return m if isinstance(m, str) and m else text


# ------------------------------------------------------------------------------------------ the new Class 11 topics


def _sqrt(label, text):
    m = re.search(r"square\s*roots?\s*of\s*(.+)", text, re.I)
    if not m:
        return None
    z = _num(_math(m.group(1)).split(" and ")[0])
    if z is None or (sp.im(z) == 0 and sp.re(z) >= 0):
        return None
    return _unit().sqrt_part(label, sp.nsimplify(z))


def _square_eq(label, text):
    m = re.search(r"\(\s*x\s*\+\s*i\s*\*?\s*y\s*\)\s*(?:\^\s*2|\*\*\s*2|²)\s*=\s*(.+)", _math(text).replace("$", ""))
    if not m:
        return None
    w = _num(m.group(1))
    if w is None or sp.im(w) == 0:
        return None
    return _unit().sq_eq(label, w, f"$(x+iy)^2 = {sp.latex(w)}$")


def _inverse_pair(label, text):
    if not re.search(r"inverse", text, re.I):
        return None
    m = re.search(r"\(\s*([^(),]+)\s*,\s*([^(),]+)\s*\)", _math(text))
    if not m:
        return None
    a, b = _num(m.group(1)), _num(m.group(2))
    if a is None or b is None or sp.im(a) or sp.im(b) or (a == 0 and b == 0):
        return None
    return _unit().mi_pair(label, a, b)


def _polar(label, text):
    if not re.search(r"polar\s*form", text, re.I):
        return None
    m = re.search(r"polar\s*form\s*(?:of|:)\s*(.+)", text, re.I) or re.search(r"(?:express|write|convert|change|put)?\s*(.+?)\s*(?:in|into|to)\s*(?:the\s*)?polar\s*form", text, re.I)
    z = _num(_math(m.group(1))) if m else None
    if z is None or z == 0:
        return None
    u = _unit()
    exact = sp.nsimplify(sp.arg(z) / sp.pi).is_Rational
    if not exact and not (sp.re(z) > 0 and sp.im(z) >= 0):
        return None                                      # the non-exact template covers quadrant I only
    return u.polar_form(label, f"${sp.latex(z)}$", [], z, exact_angle=exact)


def _nth_roots(label, text):
    m = re.search(r"(cube|fourth|4th|3rd)\s*roots?\s*of\s*(?:unity)?\s*(-?\d+)?", text, re.I)
    if not m:
        return None
    kind = "cube" if m.group(1).lower() in ("cube", "3rd") else "fourth"
    n = int(m.group(2)) if m.group(2) else 1
    u = _unit()
    if kind == "cube":
        c = sp.nsimplify(sp.Integer(abs(n)) ** sp.Rational(1, 3))
        return u.cube_roots(label, n) if c.is_Integer and n != 0 else None
    c = sp.nsimplify(sp.Integer(abs(n)) ** sp.Rational(1, 4))
    return u.fourth_roots(label, n) if n > 0 and c.is_Integer else None


_POLY = re.compile(r"[-+(\d.z][-+*/^().\dz\s²³⁴⁵]*(?:=\s*[-+]?\s*[\d.]+)?")


def _poly_text(text):
    """The longest stretch of the text that is a polynomial in z (with '= number' if there is one)."""
    t = re.sub(r"\$", " ", text).replace("−", "-")
    best = ""
    for m in _POLY.finditer(t):
        s = m.group(0).strip()
        if "z" in s and re.search(r"[-+]", s) and len(s) > len(best):
            best = s
    return best


def _numbers(s):
    """Numbers written in the text, without part labels and exponent-free: z^4 + 5z^2 - 36 -> 4, 5, 2, 36."""
    s = re.sub(r"\((?:i|ii|iii|iv|v|vi|vii|viii|ix|x|[a-h])\)", " ", s)
    return sorted(re.findall(r"\d+(?:\.\d+)?", s))


def _factor_or_solve(label, text):
    want_factor = re.search(r"factori[sz]e|linear\s*factors", text, re.I)
    want_solve = re.search(r"solve|roots?\s*of|zeros?\s*of|completing", text, re.I) or "=" in text
    if not (want_factor or want_solve):
        return None
    seg = _poly_text(text)
    p = _poly(seg) if seg else None
    if p is not None and _numbers(seg) != _numbers(re.sub(r"(?i)\b(?:by|using)\b.*$", "", text)):
        return None                                      # part of the maths was left out: never solve a different question
    if p is None:
        return None
    u = _unit()
    deg = sp.degree(p, Z)
    coeffs = sp.Poly(p, Z).all_coeffs()
    real = all(sp.im(c) == 0 and c.is_Rational for c in coeffs)
    if deg == 2 and real:
        a, b, c = [int(x) if x.is_Integer else None for x in coeffs]
        if None not in (a, b, c) and b * b - 4 * a * c < 0:
            return u.complete_sq(label, a, b, c, "solve" if want_solve and not want_factor else "factor")
    rts = sp.roots(sp.Poly(p, Z))
    if sum(rts.values()) != deg or deg > 5:
        return None
    roots = []
    for r, k in rts.items():
        roots += [sp.nsimplify(sp.radsimp(r))] * k
    roots = sorted(roots, key=lambda r: (float(sp.im(r)) != 0, -float(sp.re(r)), -float(sp.im(r))))
    lead = coeffs[0]
    ptex = sp.latex(p)
    steps = [u.S(rf"{ptex} = 0", "Set the polynomial equal to zero and find its zeros (try factor pairs, grouping or a substitution such as $u = z^2$).",
                 "کثیر رقمی کو صفر کے برابر رکھیں اور اس کے صفر معلوم کریں۔")]
    for r in dict.fromkeys(roots):
        steps.append(u.S(rf"P\left({u.ctex(r)}\right) = 0", f"$z = {u.ctex(r)}$ makes the polynomial zero, so it is a root.",
                         f"$z = {u.ctex(r)}$ سے کثیر رقمی صفر ہو جاتی ہے، اس لیے یہ جذر ہے۔", f"expand(({sp.sstr(p)}).subs(z, {u.py(r)})) == 0"))
    ftex = ("" if lead == 1 else sp.latex(lead)) + "".join(rf"\left(z {u._minus(r)}\right)" for r in roots)
    steps.append(u.S(rf"{ptex} = {ftex}", "Each root $r$ gives a linear factor $z - r$; multiplying out gives back the polynomial.",
                     "ہر جذر $r$ سے خطی جزو $z - r$ بنتا ہے؛ ضرب دینے سے وہی کثیر رقمی واپس آتی ہے۔", u.product_check(roots, lead, p)))
    if want_factor:
        return u.P(label, steps, f"${ftex}$", prompt=f"${ptex}$")
    return u.P(label, steps, u.roots_answer(roots), prompt=f"${ptex} = 0$")


def _with_zeros(label, text):
    m = re.search(r"zeros?\s*(.+?)\s*and\s*satisfying\s*P\s*\(\s*(-?\d+)\s*\)\s*=\s*(-?\d+)", _math(text).replace("$", ""), re.I)
    if not m or not re.search(r"polynomial", text, re.I):
        return None
    zs = [_num(t) for t in re.split(r",|\band\b", m.group(1)) if t.strip()]
    if not zs or any(z is None for z in zs):
        return None
    base = sp.expand(sp.Mul(*[(Z - z) for z in zs]))
    if any(sp.im(c) != 0 for c in sp.Poly(base, Z).all_coeffs()):
        return None
    at, val = int(m.group(2)), int(m.group(3))
    bval = base.subs(Z, at)
    if bval == 0:
        return None
    k = sp.Rational(val) / bval
    u = _unit()
    ftex = "".join(rf"\left(z {u._minus(z)}\right)" for z in zs)
    p = u.poly_from_zeros(len(zs), ftex, sp.sstr(sp.Mul(*[(Z - z) for z in zs])), at, val, k)
    p["label"] = label
    return p


TOPICS = (_inverse_pair, _square_eq, _sqrt, _polar, _nth_roots, _with_zeros, _factor_or_solve)


def _one(label, text):
    for f in TOPICS:
        try:
            p = f(label, text)
        except (sp.SympifyError, TypeError, ValueError, ZeroDivisionError, SyntaxError, AttributeError, KeyError, IndexError):
            p = None
        if p is not None:
            return p
    return None


def _checked(parts):
    for p in parts:
        for st in p["steps"]:
            for chk in st.get("check", []):
                try:
                    if not verify(chk):
                        return False
                except Exception:
                    return False
    return True


def solve(text):
    """-> a solved Class 11 item, or None."""
    text = text or ""
    pieces = part_markers(text)
    stem = pieces[0]
    texts = [p for p in pieces[1:] if p.strip()] if len(pieces) > 1 else [text]
    names = labels(len(texts)) if len(texts) > 1 else [""]
    parts = []
    for lab, t in zip(names, texts):
        p = _one(lab, (stem + " " + t) if len(texts) > 1 else t)
        if p is None:
            parts = None
            break
        parts.append(p)
    if parts and _checked(parts):
        q = text.strip()
        return {"id": "solved11-" + re.sub(r"[^a-z0-9]+", "-", q.lower())[:40].strip("-"), "kind": "solved", "number": "", "page": 0,
                "question": q, "parts": parts, "verified": True, "source": "solver", "unit": 1, "unit_title": "Complex Numbers", "class": 11}
    res = solvers10.solve(text)                           # complex arithmetic, conjugates, moduli, equations
    if res:
        res = dict(res, **{"class": 11, "id": res["id"].replace("solved10-", "solved11-")})
    return res
