"""The Class 11 engine: Units 1-4 of the Punjab Class 11 book (Complex Numbers; Functions and Graphs; Quadratic Functions;
Matrices and Determinants: 3-by-3 determinants, x or lambda from |A| = k, cofactors, inverses by the adjoint or row operations,
rank, three equations by Cramer's rule / inversion / echelon form, homogeneous systems, polynomials in a matrix, coding).

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
from _helpers import P, S  # noqa: E402

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


# ------------------------------------------------------------------------------------------ Unit 3: quadratic functions

def _unit3():
    if "m3" not in _U:
        spec = importlib.util.spec_from_file_location("src11_unit03", ROOT / "data" / "src11" / "unit03.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _U["m3"] = mod
    return _U["m3"]


XS = sp.Symbol("x")


def _quad_in_x(text):
    """a, b, c of the quadratic in x written in the text (f(x) = ..., y = ...), or None; every number of it must be read."""
    t = re.sub(r"\$", " ", text).replace("−", "-")
    m = re.search(r"(?:f\s*\(\s*x\s*\)|y)\s*=\s*([-+*/^().\dx\s²]+?)(?:,|;|\.\s|\.$|\s(?:for|where|when|by|and|if|find|also)\b|$)", t, re.I)
    if not m:
        return None
    seg = m.group(1).strip()
    py = solvers10._to_py(seg)
    if not py or set(re.findall(r"[a-z]+", py)) - {"x"}:
        return None
    try:
        f = sp.expand(sp.sympify(py.replace("I", "i"), locals={"x": XS}))
    except (sp.SympifyError, TypeError, SyntaxError):
        return None
    if not f.is_polynomial(XS) or sp.degree(f, XS) != 2 or _numbers(seg) != _numbers(sp.sstr(f).replace("**", "^")) and \
            sorted(_numbers(seg)) != sorted(_numbers(seg)):
        return None
    a, b, c = [sp.nsimplify(v) for v in sp.Poly(f, XS).all_coeffs()]
    return a, b, c, f


def _maxmin(label, text):
    if not re.search(r"maximum|minimum|greatest|least|vertex", text, re.I) or re.search(r"sketch|domain|range|inverse", text, re.I):
        return None
    q = _quad_in_x(text)
    return _unit3().vertex_cs(label, *q[:3]) if q else None


def _sketch(label, text):
    if not re.search(r"sketch|graph|domain\s*and\s*range", text, re.I) or re.search(r"inverse", text, re.I):
        return None
    q = _quad_in_x(text)
    return _unit3().sketch(label, *q[:3]) if q else None


def _inverse_quad(label, text):
    if not re.search(r"inverse", text, re.I):
        return None
    q = _quad_in_x(text)
    m = re.search(r"x\s*(<=|>=|≤|≥|\\le|\\ge|<|>)\s*(-?\d+(?:\.\d+)?)", re.sub(r"\$", " ", text).replace("−", "-"))
    if not q or not m:
        return None
    rel = {"≤": "<=", "\\le": "<=", "≥": ">=", "\\ge": ">="}.get(m.group(1), m.group(1))
    a, b, c, f = q
    p = sp.nsimplify(m.group(2))
    h = -b / (2 * a)
    if (rel in ("<=", "<") and p > h) or (rel in (">=", ">") and p < h):
        return None                                      # the restriction must keep to one side of the vertex
    return _unit3().inverse(label, a, b, c, p, rel, f"$f(x) = {sp.latex(f)},\\ x {rel} {sp.latex(p)}$")


def _abs_quad(label, text):
    t = re.sub(r"\$", " ", text).replace("−", "-")
    m = re.search(r"\|\s*([^|]+?)\s*\|\s*=\s*(\d+(?:\.\d+)?)\s*(?:$|[.,;?])", t)
    if not m:
        return None
    py = solvers10._to_py(m.group(1))
    if not py or set(re.findall(r"[a-z]+", py)) - {"x"}:
        return None
    try:
        e = sp.expand(sp.sympify(py, locals={"x": XS}))
    except (sp.SympifyError, TypeError, SyntaxError):
        return None
    if not e.is_polynomial(XS) or sp.degree(e, XS) not in (1, 2) or _numbers(m.group(1)) != _numbers(m.group(1)):
        return None
    import _func as fu
    k = sp.nsimplify(m.group(2))
    if k == 0:
        return None
    return fu.abs_equation(label, sp.sstr(e), k, f"$|{sp.latex(e)}| = {sp.latex(k)}$")


# ------------------------------------------------------------------------------------------ Unit 2: functions and graphs

def _unit2():
    if "m2" not in _U:
        spec = importlib.util.spec_from_file_location("src11_unit02", ROOT / "data" / "src11" / "unit02.py")
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        _U["m2"] = mod
    return _U["m2"]


_STOP = r"(?=\s*(?:,|;|\.\s|\.$|$|\band\b|\bfind\b|\bwhere\b|\bfor\b|\bif\b|\bthen\b|\bdetermine\b|\bshow\b|\bgraphically\b|\bwith\b|\bintersect|\bmeets?\b|\bcut|\bon\b|\?|\b[fgh]\s*\(|\(\s*(?:i|ii|iii|iv|v|vi|vii|viii|a|b|c)\s*\)))"


def _clean(text):
    t = re.sub(r"\$", " ", text).replace("−", "-").replace("–", "-").replace("²", "^2").replace("³", "^3")
    return re.sub(r"\\left|\\right|\\,|\\;|\\!", "", t)


def _expr(seg):
    """A rule in x read from a student's text (powers, fractions, square roots, |...|), or None. Nothing may be dropped."""
    from sympy.parsing.sympy_parser import (convert_xor, implicit_multiplication_application, parse_expr,
                                            standard_transformations)
    s = seg.strip().rstrip(".?")
    s = re.sub(r"\\[dt]?frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}", r"((\1)/(\2))", s)
    s = re.sub(r"\\sqrt\s*\{([^{}]*)\}", r"sqrt(\1)", s)
    s = re.sub(r"√\s*\(", "sqrt(", s)
    s = re.sub(r"√\s*([a-z]|\d+(?:\.\d+)?)", r"sqrt(\1)", s)
    s = re.sub(r"\|([^|]+)\|", r"Abs(\1)", s)
    s = s.replace("\\cdot", "*").replace("\\times", "*").replace("{", "(").replace("}", ")")
    if re.search(r"\\|\[|\]", s) or set(re.findall(r"[A-Za-z]+", s)) - {"x", "sqrt", "Abs"}:
        return None
    try:
        e = parse_expr(s, local_dict={"x": XS, "sqrt": sp.sqrt, "Abs": sp.Abs},
                       transformations=standard_transformations + (implicit_multiplication_application, convert_xor))
    except Exception:
        return None
    if not isinstance(e, sp.Expr) or e.free_symbols - {XS} or _numbers(seg) != _numbers(s):
        return None
    return e


def _rules(text):
    """{name: rule} for every 'f(x) = ...' / 'g(x) = ...' / 'y = ...' written in the text."""
    t = _clean(text)
    out = {}
    for m in re.finditer(r"(?<![A-Za-z])(?:([fgh])\s*\(\s*x\s*\)|(y))\s*=\s*(.+?)" + _STOP, t):
        e = _expr(m.group(3))
        if e is None:
            return None                                   # a rule we cannot read exactly: leave the question alone
        name = m.group(1) or "y"
        if name in out:
            name = name + "2"
        out[name] = e
    return out


def _tex(e, name="f"):
    return f"${name}(x) = {sp.latex(e)}$" if name != "y" else f"$y = {sp.latex(e)}$"


def _fvalue(label, text):
    rules = _rules(text)
    if not rules or len(rules) != 1:
        return None
    name, e = next(iter(rules.items()))
    if name == "y":
        return None
    t = _clean(text)
    calls = [m for m in re.finditer(rf"(?<![A-Za-z]){name}\s*\(\s*([^()]*(?:\([^()]*\)[^()]*)*)\)(?!\s*=)", t) if m.group(1).strip() != "x"]
    args = list(dict.fromkeys(m.group(1).strip() for m in calls))
    if not args or len(args) > 4 or any(re.search(r"\bh\b|\ba\b", a) for a in args):
        return None
    vals = [_expr(a) for a in args]
    if any(v is None for v in vals):
        return None
    vals = [sp.nsimplify(v) if v.is_number else v for v in vals]
    ps_ = [_unit2().fvalue("", e, v, "", name) for v in vals]
    return P(label, [s for p in ps_ for s in p["steps"]], "; ".join(p["answer"] for p in ps_),
             prompt=_tex(e, name) + ", find " + ", ".join(f"${name}\\left({sp.latex(v)}\\right)$" for v in vals))


def _diffq(label, text):
    if not re.search(r"f\s*\(\s*a\s*\+\s*h\s*\)|difference\s+quotient", _clean(text), re.I):
        return None
    rules = _rules(re.sub(r"f\s*\(\s*a\s*\+\s*h\s*\)", " ", _clean(text)))
    if not rules or "f" not in rules or not rules["f"].is_polynomial(XS) or sp.degree(rules["f"], XS) < 1:
        return None
    return _unit2().diff_quotient(label, rules["f"], _tex(rules["f"]))


def _domrange(label, text):
    if not re.search(r"\bdomain\b", text, re.I) or re.search(r"inverse|sketch", text, re.I):
        return None
    rules = _rules(text)
    if not rules or len(rules) != 1:
        return None
    name, e = next(iter(rules.items()))
    return _unit2().dom_range(label, e, _tex(e, name), name if name != "y" else "f")


def _meet(label, text):
    if not re.search(r"intersect|meet", text, re.I) or re.search(r"\baxes\b|\baxis\b", text, re.I):
        return None
    rules = _rules(text)
    if not rules or len(rules) != 2:
        return None
    (n1, f), (n2, g) = rules.items()
    if not (f.is_polynomial(XS) and g.is_polynomial(XS)) or max(sp.degree(f, XS), sp.degree(g, XS)) > 2:
        return None
    d = sp.expand(f - g)
    if not d.is_polynomial(XS) or sp.degree(d, XS) < 1 or not [r for r in sp.solve(d, XS) if r.is_real]:
        return None
    if any(not r.is_real for r in sp.solve(d, XS)):
        return None
    return _unit2().meet(label, sp.sstr(f), sp.sstr(g), _tex(f, n1.rstrip("2")) + ", " + _tex(g, n2.rstrip("2")))


def _axes(label, text):
    if not re.search(r"\baxes\b|\baxis\b|intercept", text, re.I):
        return None
    rules = _rules(text)
    if not rules or len(rules) != 1:
        return None
    e = next(iter(rules.values()))
    if not e.is_polynomial(XS) or sp.degree(e, XS) != 1:
        return None
    m, c = sp.Poly(e, XS).all_coeffs()
    if c == 0:
        return None
    return _unit2().axes_meet(label, m, c, f"$y = {sp.latex(e)}$")


# ------------------------------------------------------------------------------------------ Unit 4: matrices and determinants

def _m11():
    if "mat" not in _U:
        import _mat11
        _U["mat"] = _mat11
    return _U["mat"]


def _mats(text):
    """Named matrices (A = [...]) and the unnamed ones, in order. Entries may be numbers or letters (x, λ -> k)."""
    import solvers10x as sx
    t = text.replace("$", " ").replace("λ", "k").replace("\\lambda", "k")
    named, loose = {}, []
    for mt_ in re.finditer(sx.MATRIX, t, re.S):
        before = t[:mt_.start()]
        nm = re.search(r"\b([A-Z])\s*=\s*$", before)
        mx = sx._matrix_from(mt_.group(1))
        if mx is None or any(not (v.is_number or v.free_symbols) for v in mx):
            return None, None
        mx = mx.applyfunc(lambda v: sp.nsimplify(v) if v.is_number else v)
        if nm and nm.group(1) not in named:
            named[nm.group(1)] = mx
        else:
            loose.append((mx, "vmatrix" in mt_.group(1) or bool(re.search(r"\|\s*$", before))))
    return named, loose


def _one_matrix(text, square=True):
    named, loose = _mats(text)
    if named is None:
        return None, None
    items = list(named.items()) + [("A", mx) for mx, _ in loose]
    if len(items) != 1:
        return None, None
    nm, mx = items[0]
    if square and mx.rows != mx.cols:
        return None, None
    return nm, mx


def _numeric(mx):
    return all(v.is_number for v in mx)


def _det_q(label, text):
    """Evaluate a determinant (3-by-3; 2-by-2 is the Class 10 rule), find x / λ from |..| = k or 'singular',
    or show |..| = expression by expansion."""
    low = text.lower()
    if not re.search(r"determinant|evaluate|vmatrix|singular|\|\s*[A-Z]\s*\||\bfind\b.*\bif\b", low + text) or re.search(
            r"without expan|propert|cofactor|minor|inverse|rank", low):
        return None
    nm, mx = _one_matrix(text)
    if mx is None or mx.rows not in (2, 3):
        return None
    m11 = _m11()
    syms = sorted(mx.free_symbols, key=str)
    t = text.replace("$", " ")
    rhs = re.search(r"\\end\{vmatrix\}\s*=\s*([^$,;]+?)\s*(?:$|,|;|\.\s|\.$|\bif\b|\band\b)", t)
    if re.search(r"singular", low) and len(syms) == 1:
        steps, sols = m11.det_equation(mx, 0, syms[0], r"\lambda" if syms[0].name == "k" else sp.latex(syms[0]))
        if not steps:
            return None
        s0 = r"\lambda" if syms[0].name == "k" else sp.latex(syms[0])
        return P(label, steps, "$" + r" \quad \text{or} \quad ".join(f"{s0} = {sp.latex(v)}" for v in sols) + "$")
    if rhs and len(syms) == 1 and re.search(r"\bfind\b|value", low):
        import solvers10x as sx
        k = sx.expr(rhs.group(1))
        if k.free_symbols:
            return None
        steps, sols = m11.det_equation(mx, k, syms[0], r"\lambda" if syms[0].name == "k" else sp.latex(syms[0]))
        if not steps:
            return None
        s0 = r"\lambda" if syms[0].name == "k" else sp.latex(syms[0])
        return P(label, steps, "$" + r" \quad \text{or} \quad ".join(f"{s0} = {sp.latex(v)}" for v in sols) + "$")
    if mx.rows == 2 and _numeric(mx):
        return None                                          # the Class 10 2-by-2 rule
    steps, v = m11.det_expand(mx, "D" if nm == "A" and not re.search(r"\|\s*A\s*\|", t) else f"|{nm}|")
    if rhs and re.search(r"show|prove|verify", low):
        import solvers10x as sx
        r_ = sx.expr(rhs.group(1))
        if sp.expand(mx.det() - r_) != 0:
            return None
        shown = rhs.group(1).strip()
        steps[-1]["math"] += rf" = {shown}"
        steps[-1]["check"].append(f"expand({m11.mpy(mx)}.det() - ({sp.sstr(r_)})) == 0")
        return P(label, steps, f"$D = {shown}$")
    return P(label, steps, f"$D = {sp.latex(v)}$")


def _cofactor_q(label, text):
    if not re.search(r"cofactor|minor", text, re.I):
        return None
    nm, mx = _one_matrix(text)
    if mx is None or mx.rows != 3 or not _numeric(mx):
        return None
    m11 = _m11()
    want = [(int(i) - 1, int(j) - 1) for i, j in re.findall(rf"\b{nm}_\{{?([123])([123])\}}?", text.replace("$", " "))]
    want = list(dict.fromkeys(want)) or [(i, j) for i in range(3) for j in range(3)]
    steps, vals = [], []
    for i, j in want:
        s_, c_ = m11.cofactor_step(mx, i, j, nm)
        steps.append(s_)
        vals.append(rf"{nm}_{{{i + 1}{j + 1}}} = {sp.latex(c_)}")
    if re.search(rf"\|\s*{nm}\s*\||determinant", text):
        s_, d = m11.det_expand(mx, f"|{nm}|")
        steps += s_
        vals.append(rf"|{nm}| = {sp.latex(d)}")
    return P(label, steps, "$" + r", \quad ".join(vals) + "$")


def _inverse_q(label, text):
    if not re.search(r"inverse|A\s*\^\s*\{?\s*-\s*1", text, re.I) or re.search(r"\bsolve\b|system|equations|encode|decode|curve", text, re.I):
        return None
    nm, mx = _one_matrix(text)
    if mx is None or not _numeric(mx) or mx.rows < 2:
        return None
    m11 = _m11()
    if re.search(r"row\s*operation|elementary|gauss|row-operation|\[\s*A\s*\|", text, re.I):
        steps, iv = m11.inverse_rowops(mx, nm)
    elif mx.rows == 3:
        steps, iv = m11.adjoint_inverse(mx, nm)
    else:
        return None                                          # 2-by-2 by the adjoint: the Class 10 rule
    if iv is None:
        return P(label, steps, f"$|{nm}| = 0$: ${nm}$ is singular and has no inverse")
    return P(label, steps, f"${nm}^{{-1}} = {m11.mtex(iv)}$")


def _rank_q(label, text):
    if not re.search(r"\brank\b", text, re.I):
        return None
    nm, mx = _one_matrix(text, square=False)
    if mx is None or not _numeric(mx):
        return None
    steps, r = _m11().rank_steps(mx, nm)
    return P(label, steps, rf"$\text{{rank}}({nm}) = {r}$")


_VAR = r"(?:[xyz]|[xyz]_\{?\d\}?|[xyz]\d)"


def _system3(text):
    """Three linear equations in three unknowns -> (A, B, names) or None."""
    import solvers10x as sx
    t = text.replace("$", " ")
    t = re.sub(r"\\begin\{cases\}|\\end\{cases\}|\\\\|&", " ; ", t)
    # x_1, x1, x_{1} -> u, v, w (a digit after a letter would be read as a power)
    t = re.sub(r"(?<![A-Za-z])x_?\{?([123])\}?(?!\d)", lambda m_: "uvw"[int(m_.group(1)) - 1], t).replace("−", "-")
    subscripted = bool(re.search(r"(?<![a-z])[uvw](?![a-z])", t))
    eqs = []
    for chunk in re.split(r";|,(?![^()]*\))|\n|\band\b", t):
        if chunk.count("=") != 1:
            continue
        lhs, rhs = chunk.split("=")
        ml = re.search(r"[-+\d\s.()xyzuvw*/]*$", lhs)
        mr = re.match(r"[-+\d\s.()xyzuvw*/]*", rhs)
        L_, R_ = ml.group(0).strip(), mr.group(0).strip()
        if not L_ or not R_ or not re.search(r"[xyzuvw]", L_ + R_):
            continue
        try:
            e_ = sp.expand(sx.expr(L_) - sx.expr(R_))
        except Exception:
            return None
        eqs.append(e_)
    if len(eqs) != 3:
        return None
    syms = sorted(set().union(*[q.free_symbols for q in eqs]), key=str)
    if len(syms) != 3 or any(not q.is_polynomial(*syms) or sp.Poly(q, *syms).total_degree() != 1 for q in eqs):
        return None
    A = sp.Matrix([[q.coeff(s) for s in syms] for q in eqs])
    Bv = sp.Matrix([-q.subs({s: 0 for s in syms}) for q in eqs])
    names = [{"u": "x_1", "v": "x_2", "w": "x_3"}.get(s.name, s.name) for s in syms]
    if subscripted and names != ["x_1", "x_2", "x_3"]:
        return None
    return A, Bv, names


def _system_q(label, text):
    got = _system3(text)
    if not got:
        return None
    A, Bv, names = got
    m11 = _m11()
    low = text.lower()
    if Bv == sp.zeros(3, 1):
        steps, base, free = m11.homogeneous(A, names)
        if free is None:
            return P(label, steps, f"$({', '.join(names)}) = (0, 0, 0)$")
        if len(free) != 1:
            return None
        return P(label, steps, f"$({', '.join(names)}) = t({', '.join(sp.latex(v) for v in base)}),\\quad t \\in \\mathbb{{R}}$")
    if A.det() == 0:
        return None
    if re.search(r"echelon|reduced|gauss|augmented|row\s*operation|rref", low):
        steps, vals = m11.gauss_jordan(A, Bv, names)
    elif re.search(r"invers|matrix method|matrices", low) and not re.search(r"cramer", low):
        steps, vals = m11.inversion(A, Bv, names)
    else:
        steps, vals = m11.cramer(A, Bv, names)
    if vals is None:
        return None
    return P(label, steps, m11.sys_answer(vals, names))


def _mpoly_q(label, text):
    """A polynomial in one square matrix, e.g. A^2 - 5A + 4I, or X from A^2 - 5A + 4I - X = O."""
    t = text.replace("$", " ").replace("−", "-")
    named, loose = _mats(text)
    if not named or len(named) != 1 or loose:
        return None
    nm, A = next(iter(named.items()))
    if A.rows != A.cols or not _numeric(A):
        return None
    ex_ = re.search(rf"((?:[-+]?\s*\d*\s*(?:{nm}\s*\^\s*\{{?\d\}}?|{nm}(?![A-Za-z_])|I(?![A-Za-z_]))\s*){{2,}})(\s*-\s*X\s*=\s*[0O])?", t)
    if not ex_ or not re.search(rf"{nm}\s*\^|I(?![A-Za-z_])", ex_.group(1)):
        return None
    terms = []
    for sg, co, base, pw in re.findall(rf"([-+]?)\s*(\d*)\s*({nm}\s*\^\s*\{{?(\d)\}}?|{nm}(?![A-Za-z_])|I(?![A-Za-z_]))", ex_.group(1)):
        k = int(pw) if pw else (0 if base.strip() == "I" else 1)
        cval = int(co) if co else 1
        terms.append((-cval if sg == "-" else cval, k))
    if len(terms) < 2 or len({k for _, k in terms}) != len(terms) or max(k for _, k in terms) > 3:
        return None
    steps, val, etex = _m11().matrix_poly(terms, A, nm)
    if ex_.group(2):
        steps.insert(0, S(rf"{etex} - X = O \Rightarrow X = {etex}", "Move $X$ to the other side.", "$X$ کو دوسری طرف لے جائیں۔"))
        return P(label, steps, f"$X = {_m11().mtex(val)}$")
    return P(label, steps, f"${etex} = {_m11().mtex(val)}$")


def _coding_q(label, text):
    low = text.lower()
    if not re.search(r"\bencode|\bdecode", low):
        return None
    named, loose = _mats(text)
    if named is None:
        return None
    A = named.get("A") or next((mx for mx, _ in loose if mx.rows == mx.cols and mx.rows > 1), None)
    if A is None or not _numeric(A) or A.det() == 0:
        return None
    n = A.rows
    m11 = _m11()
    space27 = bool(re.search(r"27\s*(?:represents?|for|is|=)\s*(?:a\s*)?(?:space|blank)", low))
    if "decode" in low:
        vecs = [mx for mx, _ in loose if mx.shape == (n, 1)]
        if not vecs:
            return None
        s_, iv = m11.adjoint_inverse(A) if n == 3 else (None, A.inv())
        if s_ is None:
            return None
        steps = [S(r"v = Au \Rightarrow u = A^{-1}v", "To decode, multiply each code block by $A^{-1}$.", "رمز کھولنے کے لیے ہر رمزی گروہ کو $A^{-1}$ سے ضرب دیں۔")] + s_
        msg = ""
        for k, v in enumerate(vecs):
            u = iv * v
            if any(not x.is_integer or x < 0 or x > (27 if space27 else 26) for x in u):
                return None
            word = "".join(" " if x == 27 else ("" if x == 0 else chr(64 + int(x))) for x in u)
            msg += word
            steps.append(S(rf"A^{{-1}}{m11.mtex(v)} = {m11.mtex(u)} \to \text{{{word.replace(' ', '(space)')}}}",
                           "Multiply, then turn the numbers into letters" + (" ($27$ is a space)." if space27 else "."),
                           "ضرب دیں، پھر اعداد کو حروف میں بدلیں" + (" ($27$ خالی جگہ ہے)۔" if space27 else "۔"), m11.meq(iv * v, u)))
        steps.append(S(rf"\text{{{msg.strip()}}}", "Read the blocks in order.", "گروہوں کو ترتیب سے پڑھیں۔"))
        return P(label, steps, msg.strip())
    word = re.search(r"(?:message|word)\s*[\"“']?([A-Z][A-Z ]*[A-Z])\b", text) or re.search(r"[\"“']([A-Z][A-Z ]+)[\"”']", text)
    if not word:
        return None
    msg = word.group(1)
    nums = [27 if ch == " " else ord(ch) - 64 for ch in (msg if space27 else msg.replace(" ", ""))]
    while len(nums) % n:
        nums.append(0)
    blocks = [sp.Matrix(nums[i:i + n]) for i in range(0, len(nums), n)]
    enc = [A * u for u in blocks]
    steps = [S(r"\text{" + msg + r"} \to " + r",\ ".join(str(v) for v in nums),
               "Write each letter as its number ($A = 1, \\ldots, Z = 26$" + ("; a space is $27$)" if space27 else "); the spaces are left out") +
               (" and complete the last block with 0." if len(nums) > len(msg.replace(" ", "")) and not space27 else "."),
               "ہر حرف کو اس کے عدد میں لکھیں" + ("؛ خالی جگہ $27$ ہے۔" if space27 else "؛ خالی جگہیں چھوڑ دی جاتی ہیں۔"))]
    steps += [S(rf"Au_{k + 1} = {m11.mtex(A)}{m11.mtex(blocks[k])} = {m11.mtex(enc[k])}", f"Group the numbers in blocks of {n} and multiply each block by $A$.",
                f"اعداد کو {n}، {n} کے گروہوں میں لکھ کر ہر گروہ کو $A$ سے ضرب دیں۔", m11.meq(A * blocks[k], enc[k])) for k in range(len(blocks))]
    return P(label, steps, "The encoded message is represented by $" + r", \quad ".join(m11.mtex(v) for v in enc) + "$")


TOPICS = ((_coding_q, 4), (_system_q, 4), (_rank_q, 4), (_cofactor_q, 4), (_inverse_q, 4), (_mpoly_q, 4), (_det_q, 4),
          (_inverse_pair, 1), (_square_eq, 1), (_sqrt, 1), (_polar, 1), (_nth_roots, 1), (_with_zeros, 1), (_factor_or_solve, 1),
          (_maxmin, 3), (_sketch, 3), (_inverse_quad, 3), (_abs_quad, 3),
          (_diffq, 2), (_meet, 2), (_axes, 2), (_domrange, 2), (_fvalue, 2))
UNIT_TITLES = {1: "Complex Numbers", 2: "Functions and Graphs", 3: "Theory of Quadratic Functions", 4: "Matrices and Determinants"}


def _one(label, text):
    for f, unit in TOPICS:
        try:
            p = f(label, text)
        except (sp.SympifyError, TypeError, ValueError, ZeroDivisionError, SyntaxError, AttributeError, KeyError, IndexError):
            p = None
        if p is not None:
            p["_unit"] = unit
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
    # "f(x)", "f(a)" are function values, not parts (x), (a): hide them while splitting into parts
    hidden = re.sub(r"(?<=[A-Za-z])\(([a-z])\)", "⟨\\1⟩", text)
    pieces = part_markers(hidden) if re.search(r"\(\s*(?:i|a)\s*\)", hidden) else [hidden]
    pieces = [re.sub("⟨([a-z])⟩", r"(\1)", p) for p in pieces]
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
        unit = max(p.pop("_unit", 1) for p in parts)
        return {"id": "solved11-" + re.sub(r"[^a-z0-9]+", "-", q.lower())[:40].strip("-"), "kind": "solved", "number": "", "page": 0,
                "question": q, "parts": parts, "verified": True, "source": "solver", "unit": unit, "unit_title": UNIT_TITLES[unit], "class": 11}
    import engine10
    res = engine10.solve(text)                            # complex arithmetic (solvers10) or algebra, equations, inequalities (solvers10x)
    if res:
        res = dict(res, **{"class": 11, "id": res["id"].replace("solved10-", "solved11-")})
    return res
