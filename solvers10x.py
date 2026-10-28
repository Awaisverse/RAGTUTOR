"""Class 10 engine for Units 2-12: reads the student's OWN question (typed, LaTeX or phone-typed, any numbers) and solves it with
the same templates that wrote the book (data/src10/_*.py), so every line carries sympy checks. Complex numbers (Unit 1) are
solvers10.py; engine10.solve tries both.

    solve(text) -> a solved item {"kind": "solved", "parts": [...], "verified": True, ...} or None when it is not a question
                   type the engine knows. It never guesses: an item is returned only when every check of every step is true.

Each part also carries "values": the answer as sympy strings, so tests can compare it with an independent computation.
"""
import math
import re
import sys
from itertools import product
from pathlib import Path

import sympy as sp

ROOT = Path(__file__).resolve().parent
for p in (ROOT, ROOT / "tools", ROOT / "data" / "src", ROOT / "data" / "src10"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

import mathtext  # noqa: E402
from build_dataset import verify  # noqa: E402
import _frac as fr  # noqa: E402
import _func as fu  # noqa: E402
import _gen as g  # noqa: E402
import _mat as mt  # noqa: E402
import _quad as qd  # noqa: E402
from _helpers import P, S, T  # noqa: E402

R = sp.Rational
X = sp.Symbol("x")
UNITS = {2: "Quadratic Equations and Inequalities", 3: "Matrices and Determinants", 4: "Functions and Graphs", 5: "Algebraic Fractions",
         6: "Vectors in Plane", 7: "Trigonometry", 8: "Chords and Arcs of a Circle", 9: "Tangent and Angles of a Circle",
         11: "Information Handling", 12: "Probability"}

_unit_cache = {}


def _unit(name):
    """The helper functions that live in a unit file (vectors, statistics, probability)."""
    if name not in _unit_cache:
        import importlib
        _unit_cache[name] = importlib.import_module(name)
    return _unit_cache[name]


# ------------------------------------------------------------------------------------------ reading the text


def norm(text):
    """Unicode and spacing tidied, superscripts as ^, the student's ≤ ≥ as <= >=; keeps case for matrix names."""
    t = str(text)
    t = re.sub(r"(?<=\b[A-Za-z])-(?=[A-Za-z]\b)", " - ", t)       # a-b is a minus b, never one hyphenated word
    t = re.sub(r"(?<![A-Za-z])([a-z])([23])(?=\s*[-+=<>)]|\s*$)", r"\1^\2", t)   # phone typing: x2 - 5x + 6 means x^2 - 5x + 6
    sup = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")
    t = re.sub(r"([⁰¹²³⁴⁵⁶⁷⁸⁹⁻]+)", lambda m: "^(" + m.group(1).translate(sup) + ")", t)
    for a, b in (("≤", "<="), ("≥", ">="), ("≦", "<="), ("≧", ">="), ("−", "-"), ("–", "-"), ("×", "*"), ("÷", "/"), ("√", "sqrt"),
                 ("π", "pi"), ("°", " deg"), ("\\le ", "<= "), ("\\ge ", ">= "), ("\\leq", "<="), ("\\geq", ">="), ("\\lt", "<"), ("\\gt", ">"),
                 ("\\left", ""), ("\\right", ""), ("\\cdot", "*"), ("\\times", "*")):
        t = t.replace(a, b)
    t = re.sub(r"\^\s*\{?\s*\\circ\s*\}?", " deg", t)                  # 45^\circ and 45^{\circ} are degrees
    return t


def word_problem(text, allowed=()):
    """True when the question has prose the algebra solvers do not read (a story: 'Ishmal runs 10 km ...'). Such a question is
    declined by the algebra solvers rather than guessed at; the student sees the model or a labelled example instead."""
    t = re.sub(r"\$[^$]*\$", " ", norm(text).lower())
    words = set(re.findall(r"[a-z]{3,}", t)) - BASIC - set(allowed)
    return len(words) > 2


BASIC = {"solve", "find", "simplify", "reduce", "evaluate", "calculate", "compute", "determine", "work", "out", "write", "express", "form",
         "show", "the", "following", "equation", "equations", "using", "use", "method", "for", "and", "then", "when", "lowest", "terms",
         "factorization", "factorisation", "factorizing", "completing", "complete", "square", "quadratic", "formula", "graphically",
         "please", "kindly", "karo", "kro", "kariye", "question", "value", "values", "root", "roots", "are", "its", "what", "with", "given",
         "that", "this", "where", "whose", "real", "numbers", "number", "standard", "inequality", "inequalities", "expression", "expressions",
         "rational", "fraction", "fractions", "algebraic", "answer", "get", "obtain", "into", "each", "from", "find", "both", "line", "show",
         "sqrt", "pi", "deg", "degrees", "set", "solution", "line"}


def expr(s):
    """A maths expression -> sympy, with plain (not positive) symbols so signs and absolute values behave."""
    s = s.strip().strip(".,;:")
    s = re.sub(r"\\ell", "l", s)
    s = re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " - ", s)      # x-y is x minus y (the text cleaner joins hyphenated words)
    e = mathtext.parse_math(s)
    return e.subs({v: sp.Symbol(v.name) for v in e.free_symbols})


def dollar_math(text):
    return [re.sub(r"(?<=[A-Za-z])-(?=[A-Za-z])", " - ", m.strip()) for m in re.findall(r"\$([^$]+)\$", text)]


WORDS = r"(?:solve|find|simplify|reduce|evaluate|calculate|compute|determine|work out|write|express|form|show|prove|the|a|an|following|equation|equations|" \
        r"by|using|use|method|of|for|and|if|then|when|in|lowest|form|terms|factori[sz]ation|factori[sz]ing|completing|complete|square|quadratic|formula|" \
        r"graphically|please|kindly|karo|kro|kariye|question|value|values|roots?|is|are|its|it|what|with|to|me)"


MATH_WORDS = {"sqrt", "root", "pi"}


PROSE2 = {"is", "of", "by", "to", "in", "if", "an", "as", "at", "be", "or", "on", "we", "it", "so", "do", "my", "me", "kr", "ho", "ka", "ki", "ke"}


def _mathy(tok):
    """A token is maths when it has digits or operators, or is a single letter, or a known maths word; prose words are never maths."""
    w = tok.strip(".?!:;")
    if not w or not re.fullmatch(r"[0-9a-zA-Z+\-*/^().=<>|,\\{}_]+", w):
        return False
    for l in re.findall(r"[a-zA-Z]+", w):
        low = l.lower()
        if low in MATH_WORDS:
            continue
        if len(l) > 2 or low in PROSE2:
            return False
    return bool(re.search(r"[0-9=<>+\-*/^|()]", w)) or len(w) == 1


def math_runs(text):
    """Every run of maths in the text, split at prose words and at ' and '. '$...$' segments win when present."""
    d = dollar_math(text)
    if d:
        return d
    t = norm(text)
    runs, cur = [], []
    for tok in re.split(r"\s+", t):
        if tok.endswith(":"):
            if cur:
                runs.append(" ".join(cur))
            cur = []
            continue
        if _mathy(tok) and tok.lower() not in ("a", "i"):
            cur.append(tok.strip(".?!:;") if tok.endswith((".", "?", "!", ":")) else tok)
        else:
            if cur:
                runs.append(" ".join(cur))
            cur = []
    if cur:
        runs.append(" ".join(cur))
    flat = re.sub(r"\s+", " ", t)
    return [r.strip(" ,;") for r in runs if re.search(r"\d|[a-z]", r) and r.strip(" ,;") in flat]


def tail_math(text):
    """The main maths of the question: the run with a relation sign (=, <, >) if any, else the longest run."""
    runs = math_runs(text)
    if not runs:
        return ""
    rel = [r for r in runs if re.search(r"[=<>]", r)]
    return max(rel or runs, key=len)


def numbers_in(text):
    t = re.sub(r"(?<=\d),(?=\d{3}\b)", "", norm(text))
    return [sp.nsimplify(v) for v in re.findall(r"-?\d+(?:\.\d+)?", t)]


def has(text, *words):
    t = text.lower()
    return any(re.search(rf"\b{w}\b", t) for w in words)


# ------------------------------------------------------------------------------------------ the result


def solved(unit, question, parts):
    return {"id": "solved10-" + re.sub(r"[^a-z0-9]+", "-", question.lower())[:40].strip("-"), "kind": "solved", "number": "", "page": 0,
            "question": question.strip(), "parts": parts, "verified": True, "source": "solver", "unit": unit, "unit_title": UNITS.get(unit, ""),
            "class": 10}


def all_true(parts):
    n = 0
    for p in parts:
        for st in p["steps"]:
            for c in st.get("check", []):
                n += 1
                try:
                    if not verify(c):
                        return False
                except Exception:
                    return False
    return n > 0


def part(p, values, prompt=""):
    p = dict(p)
    p["values"] = [sp.sstr(v) for v in values]
    p["prompt"] = prompt or p.get("prompt", "")
    return p


# ------------------------------------------------------------------------------------------ Unit 2: quadratics


def _eq_sides(s):
    s = s.replace("==", "=")
    if s.count("=") != 1 or re.search(r"[<>]", s):
        return None
    l, r = s.split("=")
    return expr(l), expr(r)


def _poly_of(L, Rr):
    n, d = sp.fraction(sp.together(L - Rr))
    return sp.expand(n), d


def quadratic(text):
    t = text.lower()
    if word_problem(text, ("factorization", "nature")) or re.search(r"\\sum|∑|\bsum of|alpha|beta|α|β|\bk\b|\bm\b\s*(?:in|when)", text):
        return None
    if "standard form" in t:                                   # write it as ax^2 + bx + c = 0, do not solve
        try:
            L_, R_ = _eq_sides(tail_math(text))
            st, poly = g.standard_form(f"{sp.sstr(L_)} = {sp.sstr(R_)}")
        except (ValueError, TypeError, sp.SympifyError):
            return None
        return solved(2, text, [part(P("", st, f"${sp.latex(poly)} = 0$"), [poly])])
    m = tail_math(text)
    sides = None
    for cand in [m] + [c for c in re.split(r"[,;]", m) if "=" in c]:
        try:
            sides = _eq_sides(cand)
            if sides:
                break
        except ValueError:
            sides = None
    if not sides:
        return None
    L, Rr = sides
    syms = (L - Rr).free_symbols
    if len(syms) != 1:
        return None
    var = syms.pop()
    num, den = _poly_of(L, Rr)
    try:
        poly = sp.Poly(num, var)
    except sp.PolynomialError:
        return None
    if poly.degree() != 2:
        return None
    if var != X:
        L, Rr = L.subs(var, X), Rr.subs(var, X)
    eq = f"{sp.sstr(L)} = {sp.sstr(Rr)}"
    a, b, c = sp.Poly(sp.expand(num.subs(var, X)), X).all_coeffs()
    D = b * b - 4 * a * c
    rational = D >= 0 and sp.sqrt(D).is_Rational
    if "complet" in t:
        method = "square"
    elif "formula" in t:
        method = "formula"
    elif "factori" in t and rational:
        method = "factor"
    else:
        method = "factor" if rational else "formula"
    if not all(c_.is_Rational for c_ in (a, b, c)):
        return None
    p = g.q_solve("", eq, method)
    # roots that make a denominator zero are not solutions
    roots = [r for r in sp.solve(sp.expand(num.subs(var, X)), X) if r.is_real and (den == 1 or den.subs(var, r) != 0)]
    if den != 1:
        bad = [r for r in sp.solve(sp.expand(num.subs(var, X)), X) if den.subs(var, r) == 0]
        if bad:
            p["steps"].append(S(r"\text{Reject } " + ", ".join(f"x = {sp.latex(r)}" for r in bad), "This value makes a denominator zero, so it is not a solution.",
                                "یہ قیمت نسب نما کو صفر کر دیتی ہے، اس لیے حل نہیں۔"))
            p["answer"] = g.answer_roots("x", sorted(roots, key=float))
    if str(var) != "x":
        p = _rename(p, "x", str(var))
    return solved(2, text, [part(p, sorted(roots, key=lambda r: float(r)) if all(r.is_real for r in roots) else roots)])


def _rename(p, a, b):
    """Show the student's letter (y, t, ...) instead of x in the board text (checks stay in x)."""
    def sw(s):
        return re.sub(rf"(?<![a-zA-Z\\]){a}(?![a-zA-Z])", b, s)
    p = dict(p)
    p["steps"] = [{**st, "math": sw(st["math"])} for st in p["steps"]]
    p["answer"] = sw(p["answer"])
    return p


def nature(text):
    if not has(text, "nature", "discriminant"):
        return None
    m = tail_math(text)
    try:
        L, Rr = _eq_sides(m) or (expr(m), sp.Integer(0))
    except ValueError:
        return None
    num, _ = _poly_of(L, Rr)
    if len(num.free_symbols) != 1:
        return None
    v = num.free_symbols.pop()
    num = sp.expand(num.subs(v, X))
    if sp.Poly(num, X).degree() != 2:
        return None
    if sp.Poly(num, X).LC() < 0:
        num = -num
    p = qd.nature("", sp.sstr(num))
    a, b, c = sp.Poly(num, X).all_coeffs()
    return solved(2, text, [part(p, [b * b - 4 * a * c])])


def roots_to_eq(text):
    if not re.search(r"roots?\s+(?:are|is|be)|whose roots|with roots|having roots", text, re.I):
        return None
    m = re.split(r"roots?\s+(?:are|is|be)|whose roots(?:\s+are)?|with roots|having roots", norm(text), flags=re.I)[-1]
    m = m.replace("$", " ").replace(" and ", ",")
    pieces = [s for s in re.split(r",|;", m) if s.strip()]
    if len(pieces) != 2:
        return None
    try:
        r1, r2 = [sp.nsimplify(expr(s)) for s in pieces]
    except ValueError:
        return None
    if r1.free_symbols or r2.free_symbols:
        return None
    p = qd.roots_to_eq("", r1, r2)
    poly = sp.expand((X - r1) * (X - r2))
    return solved(2, text, [part(p, [poly])])


def q_inequality(text):
    m = tail_math(text)
    mm = re.match(r"(.+?)(<=|>=|<|>)(.+)$", m)
    if not mm:
        return None
    try:
        L, Rr = expr(mm.group(1)), expr(mm.group(3))
    except ValueError:
        return None
    if any("Abs" in str(a) for a in (L, Rr)):
        return None
    d = sp.expand(L - Rr)
    if len(d.free_symbols) != 1:
        return None
    v = d.free_symbols.pop()
    d = sp.expand(d.subs(v, X))
    if sp.Poly(d, X).degree() != 2 or not all(c.is_Rational for c in sp.Poly(d, X).all_coeffs()):
        return None
    op = mm.group(2)
    p = qd.inequality("", sp.sstr(d), op)
    sol = sp.solveset({"<": sp.Lt, ">": sp.Gt, "<=": sp.Le, ">=": sp.Ge}[op](d, 0), X, sp.S.Reals)
    return solved(2, text, [part(p, [sol])])


# ------------------------------------------------------------------------------------------ Unit 3: matrices


def _matrix_from(s):
    s = s.strip()
    if "bmatrix" in s or "vmatrix" in s or "pmatrix" in s:
        body = re.sub(r"\\(begin|end)\{[bvp]matrix\}", "", s)
        rows = [r for r in body.split("\\\\") if r.strip()]
        return mt.M([[expr(c) for c in r.split("&")] for r in rows])
    if s.startswith("[["):
        rows = re.findall(r"\[([^\[\]]+)\]", s)
        return mt.M([[expr(c) for c in re.split(r"[,\s]+", r.strip()) if c] for r in rows])
    if s.startswith("[") and ";" in s:
        rows = s.strip("[]").split(";")
        return mt.M([[expr(c) for c in re.split(r"[,\s]+", r.strip()) if c] for r in rows])
    return None


MATRIX = r"(\\begin\{[bvp]matrix\}.*?\\end\{[bvp]matrix\}|\[\[[^\]]*\](?:\s*,?\s*\[[^\]]*\])*\]|\[[^\[\]]*;[^\[\]]*\])"


def matrices(text):
    t = text.replace("$", " ")
    named = {}
    for m in re.finditer(rf"\b([A-Z])\s*=\s*{MATRIX}", t, re.S):
        try:
            named[m.group(1)] = _matrix_from(m.group(2))
        except (ValueError, TypeError):
            return None
    if not named:
        ms = re.findall(MATRIX, t, re.S)
        if len(ms) == 1:
            try:
                named["A"] = _matrix_from(ms[0])
            except (ValueError, TypeError):
                return None
        elif len(ms) == 2 and re.search(r"multipl|product|add|sum|subtract|differ", t, re.I):
            named["A"], named["B"] = _matrix_from(ms[0]), _matrix_from(ms[1])
    if not named or any(m is None for m in named.values()):
        return None
    low = t.lower()
    if re.search(r"verify|prove|show that|such that", low) or re.search(r"\(\s*[A-Z]\s*[A-Z+\-]", t) or re.search(r"[A-Z]\s*\^\s*\{?\s*t\b.*[A-Z]\s*\^", t):
        return None                                            # laws to verify and expressions like (AB)^t are not single operations
    names = sorted(named)
    if len(names) > 1 and re.search(r"inverse|determinant|adjoint|transpose|\|\s*[A-Z]\s*\|", low + t):
        tgt = re.search(r"(?:inverse|determinant|adjoint|transpose)\s+of\s+(?:the\s+)?(?:matrix\s+)?([A-Z])\b|\|\s*([A-Z])\s*\||\b([A-Z])\s*\^\s*\{?\s*(?:-\s*1|t)\b"
                        r"|\\operatorname\{Adj\}\s*([A-Z])|\bAdj\s*([A-Z])\b", t)
        n_ = next((v for v in tgt.groups() if v), None) if tgt else None
        if n_ not in named:
            return None                                        # several matrices and no clear target
        names = [n_] + [n for n in names if n != n_]
    A = named[names[0]]
    n0 = names[0]
    parts = []
    if re.search(r"additive inverse|negative of", low):
        which = names if re.search(r"matrices", low) else [n0]          # 'negative of the following matrices': every one
        steps = [S(rf"-{n} = -{mt.mtex(named[n])} = {mt.mtex(-named[n])}", "The additive inverse changes the sign of every entry.",
                   "جمعی معکوس میں ہر رکن کی علامت بدل جاتی ہے۔", mt.meq(named[n] - named[n], sp.zeros(*named[n].shape)), mt.meq(-named[n], -1 * named[n]))
                 for n in which]
        ans_ = "; ".join(f"$-{n} = {mt.mtex(-named[n])}$" for n in which) if len(which) > 1 else mt.ans(-A)
        parts.append(part(P("", steps, ans_), [-named[n] for n in which]))
        return solved(3, text, parts)
    if len(names) >= 2 and re.search(r"\bAB\b", t) and re.search(r"\bBA\b", t) and "A" in named and "B" in named:
        s1, ab = mt.mul(named["A"], named["B"])
        s2, ba = mt.mul(named["B"], named["A"], "B", "A")
        ans_ = ", ".join([f"$AB = {mt.mtex(ab)}$" if ab is not None else "$AB$ not possible", f"$BA = {mt.mtex(ba)}$" if ba is not None else "$BA$ not possible"])
        return solved(3, text, [part(P("", s1 + s2, ans_), [m for m in (ab, ba) if m is not None])])
    if re.search(r"inverse", low):
        st, v = mt.inv(A, n0)
        if v is None:
            parts.append(part(P("", st, f"$|{n0}| = 0$: no inverse"), [0]))
        else:
            parts.append(part(P("", st, mt.ans(v)), [v]))
    elif re.search(r"determinant|\|\s*[A-Z]\s*\|", low + t) and A.rows == A.cols == 2:
        st, v = mt.det(A, n0)
        parts.append(part(P("", st, f"${sp.latex(v)}$"), [v]))
    elif "adjoint" in low:
        st, v = mt.adj(A, n0)
        parts.append(part(P("", st, mt.ans(v)), [v]))
    elif "transpose" in low:
        st, v = mt.tr(A, n0)
        parts.append(part(P("", st, mt.ans(v)), [v]))
    elif len(names) >= 2:
        a, b = names[0], names[1]
        M1, M2 = named[a], named[b]
        op = re.search(rf"\b({a}\s*\+\s*{b}|{a}\s*-\s*{b}|{a}\s*\*?\s*{b}|{b}\s*\*?\s*{a}|{b}\s*-\s*{a})\b", t)
        if re.search(r"multipl|product", low) or (op and re.fullmatch(rf"{a}\s*\*?\s*{b}", op.group(1))):
            st, v = mt.mul(M1, M2, a, b)
        elif op and re.fullmatch(rf"{b}\s*\*?\s*{a}", op.group(1)):
            st, v = mt.mul(M2, M1, b, a)
        elif (op and "+" in op.group(1)) or re.search(r"\badd|\bsum", low):
            st, v = mt.add(M1, M2, a, b)
        elif op and re.fullmatch(rf"{b}\s*-\s*{a}", op.group(1)):
            st, v = mt.add(M2, M1, b, a, -1)
        elif (op and "-" in op.group(1)) or re.search(r"subtract|differ", low):
            st, v = mt.add(M1, M2, a, b, -1)
        else:
            return None
        if v is None:
            parts.append(part(P("", st, "not possible (orders do not match)"), [0]))
        else:
            parts.append(part(P("", st, mt.ans(v)), [v]))
    else:
        return None
    return solved(3, text, parts)


def _linear_eqs(text):
    raw = [c for r in math_runs(text) for c in re.split(r",|;|\band\b", r) if "=" in c]
    eqs = []
    for c in raw:
        try:
            s = _eq_sides(c)
        except ValueError:
            return None
        if not s:
            return None
        eqs.append(sp.expand(s[0] - s[1]))
    if len(eqs) != 2:
        return None
    syms = sorted(set().union(*[e.free_symbols for e in eqs]), key=str)
    if len(syms) != 2 or any(sp.Poly(e, *syms).total_degree() != 1 for e in eqs):
        return None
    if not any(len(e.free_symbols) == 2 for e in eqs) or re.search(r"\b(?:arc|radius|theta|sector|chord)\b", text, re.I):
        return None
    A = mt.M([[e.coeff(s) for s in syms] for e in eqs])
    Bv = mt.M([-e.subs({s: 0 for s in syms}) for e in eqs])
    return A, Bv, tuple(str(s) for s in syms)


def linear_system(text):
    if word_problem(text, ("cramer", "cramer's", "rule", "matrix", "matrices", "inversion", "inverse", "pair", "linear", "simultaneous", "system", "elimination",
                           "substitution")):
        return None
    got = _linear_eqs(text)
    if not got:
        return None
    A, Bv, names = got
    if A.det() == 0:
        return None
    method = mt.inverse_solve if re.search(r"invers|matri", text, re.I) and not re.search(r"cramer", text, re.I) else mt.cramer
    st, vals = method(A, Bv, names)
    return solved(3, text, [part(P("", st, mt.sys_answer(vals, names)), list(vals))])


# ------------------------------------------------------------------------------------------ Unit 4: functions and absolute value


def functions(text):
    t = norm(text).replace("$", " ")
    defs = {}
    for m in re.finditer(r"\b([fgh])\s*\(\s*x\s*\)\s*=\s*([^,;]+?)(?=(?:,|;|\band\b|\bthen\b|\bfind\b|$))", t, re.I):
        try:
            defs[m.group(1)] = expr(m.group(2))
        except ValueError:
            return None
    if not defs:
        return None
    rest = t.lower()
    if re.search(r"verify|prove|without|such that|domain|range|graph|plot|\bk\b|break even|discount|model", rest):
        return None                                            # not a single computation on the functions
    parts = []
    # composition: fog, f o g, (f∘g)(x), f(g(x))
    comp = re.search(r"\(?\s*([fgh])\s*(?:o|∘|\\circ)\s*([fgh])\s*\)?\s*\(\s*x\s*\)|\b([fgh])\s*\(\s*([fgh])\s*\(\s*x\s*\)\s*\)|\b([fgh])([fgh])\s*\(x\)|\b([fgh])o([fgh])\b", rest)
    inv = re.search(r"\b([fgh])\s*(?:\^\s*\(?\s*-\s*1\s*\)?|\^\{-1\}|-1|inverse)|inverse of\s+([fgh])", rest)
    val = re.search(r"\b([fgh])\s*\(\s*(-?\d+(?:\.\d+)?)\s*\)", rest)
    arith = re.search(r"\b([fgh])\s*\(\s*x\s*\)\s*([+\-*/]|\\div)\s*([fgh])\s*\(\s*x\s*\)", rest)
    if comp:
        o, i = [x for x in comp.groups() if x][:2]
        if o not in defs or i not in defs:
            return None
        p, res = fu.compose("", o, sp.sstr(defs[o]), i, sp.sstr(defs[i]))
        parts.append(part(p, [res]))
    elif arith:
        a, op, b = arith.groups()
        if a not in defs or b not in defs:
            return None
        op = "/" if op == "\\div" else op
        p = fu.combine("", a, sp.sstr(defs[a]), b, sp.sstr(defs[b]), op, "")
        v = {"+": defs[a] + defs[b], "-": defs[a] - defs[b], "*": defs[a] * defs[b], "/": defs[a] / defs[b]}[op]
        parts.append(part(p, [sp.simplify(v)]))
    elif inv:
        f = inv.group(1) or inv.group(2)
        F = defs.get(f)
        if F is None or len(F.free_symbols - {sp.Symbol("x")}) or sp.Symbol("x") not in F.free_symbols:
            return None
        y = sp.Symbol("y")
        sols = sp.solve(sp.Eq(y, F.subs(sp.Symbol("x"), X)), X)
        if len(sols) != 1:
            return None
        fi = sp.factor(sp.together(sp.cancel(sols[0].subs(y, X))))
        if sp.denom(fi) == 1 and not fi.is_Add:
            fi = sp.together(sp.expand(fi))
        domain = ""
        if any(isinstance(a, sp.Pow) and a.exp == R(1, 2) for a in sp.preorder_traversal(F)):
            domain = r"x \ge 0"                                # the outputs of a square root are never negative
        elif sp.denom(sp.together(fi)) != 1:
            bad = sp.solve(sp.denom(sp.together(fi)), X)
            domain = r",\ ".join(rf"x \ne {sp.latex(b)}" for b in bad)
        steps = [S(rf"y = {sp.latex(F)}", "Write $y = f(x)$.", "$y = f(x)$ لکھیں۔"),
                 S(rf"x = {sp.latex(sols[0])}", "Make $x$ the subject.", "$x$ کو موضوع بنائیں۔", f"simplify(({sp.sstr(F)}).subs(x, {g.ps(sols[0])}) - y) == 0"),
                 S(rf"{f}^{{-1}}(x) = {sp.latex(fi)}" + (rf",\quad {domain}" if domain else ""), "Replace $y$ by $x$.", "$y$ کی جگہ $x$ لکھیں۔",
                   f"simplify(({sp.sstr(F)}).subs(x, {g.ps(fi)})) == x")]
        parts.append(part(P("", steps, f"${f}^{{-1}}(x) = {sp.latex(fi)}$" + (f", ${domain}$" if domain else "")), [fi]))
    elif val:
        f, a = val.group(1), sp.nsimplify(val.group(2))
        F = defs.get(f)
        if F is None:
            return None
        v = F.subs(sp.Symbol("x"), a)
        parts.append(part(P("", [S(rf"{f}({sp.latex(a)}) = {sp.latex(F).replace('x', '(' + sp.latex(a) + ')')} = {sp.latex(v)}", f"Put $x = {sp.latex(a)}$.",
                                   f"$x = {sp.latex(a)}$ رکھیں۔", f"({sp.sstr(F)}).subs(x, {g.ps(a)}) == {g.ps(v)}")], f"${sp.latex(v)}$"), [v]))
    else:
        return None
    return solved(4, text, parts)


def absolute(text):
    t = norm(text).replace("$", " ")
    m = re.search(r"\|([^|]+)\|", t)
    if not m:
        return None
    try:
        inner = expr(m.group(1))
    except ValueError:
        return None
    if inner.free_symbols != {sp.Symbol("x")} and len(inner.free_symbols) != 1:
        return None
    v = inner.free_symbols.pop()
    inner = inner.subs(v, X)
    after = t[m.end():].strip()
    before = t[:m.start()]
    mm = re.match(r"(<=|>=|<|>|=)\s*(-?\d+(?:\.\d+)?)", after)
    if not mm or re.search(r"[0-9)]\s*[-+*/]?\s*$", before.split(":")[-1].strip()):
        return None
    op, k = mm.group(1), sp.nsimplify(mm.group(2))
    if op == "=":
        if k < 0:
            return None
        if k == 0:
            r = sp.solve(inner, X)[0]
            p = P("", [S(rf"{sp.latex(inner)} = 0 \Rightarrow x = {sp.latex(r)}", "An absolute value is 0 only when the inside is 0.", "مطلق قیمت صرف تب 0 ہے جب اندر 0 ہو۔",
                         f"({sp.sstr(inner)}).subs(x, {g.ps(r)}) == 0")], f"$x = {sp.latex(r)}$")
            return solved(4, text, [part(p, [r])])
        p = fu.abs_equation("", sp.sstr(inner), k, f"$|{sp.latex(inner)}| = {sp.latex(k)}$")
        roots = sorted(sp.solve(inner - k, X) + sp.solve(inner + k, X), key=float)
        return solved(4, text, [part(p, roots)])
    lo = rf"-{sp.latex(k)} {'<' if op in ('<', '>') else r'\le'} {sp.latex(inner)} {'<' if op in ('<', '>') else r'\le'} {sp.latex(k)}"
    hi = rf"{sp.latex(inner)} {'<' if op in ('>', '<') else r'\le'} -{sp.latex(k)} \ \text{{or}}\ {sp.latex(inner)} {'>' if op in ('>', '<') else r'\ge'} {sp.latex(k)}"
    steps_tex = [(lo if op in ("<", "<=") else hi, "Remove the absolute value: $|A| \\le k$ means $-k \\le A \\le k$; $|A| \\ge k$ means $A \\le -k$ or $A \\ge k$.",
                  "مطلق قیمت ہٹائیں۔")]
    p, sol = fu.abs_inequality("", f"Abs({sp.sstr(inner)})", op, sp.sstr(k), steps_tex, f"$|{sp.latex(inner)}| {op} {sp.latex(k)}$")
    return solved(4, text, [part(p, [sol])])


# ------------------------------------------------------------------------------------------ Unit 5: algebraic fractions


def fractions(text):
    if not re.search(r"simplif|reduce|lowest|add|subtract|multiply|divide", text, re.I):
        return None
    sub = re.search(r"subtract\s+(.+?)\s+from\s+(.+?)\s*\.?\s*$", norm(text), re.I | re.S)
    if sub:                                                   # 'Subtract A from B' means B - A
        try:
            a_, b_ = expr(" ".join(math_runs(sub.group(1))) or sub.group(1)), expr(" ".join(math_runs(sub.group(2))) or sub.group(2))
        except ValueError:
            return None
        E = b_ - a_
        terms = []
        for sign, part_ in (("+", b_), ("-", a_)):
            an, ad = sp.fraction(sp.together(part_))
            terms.append((sign, sp.sstr(an), sp.sstr(ad)))
        p = fr.combine("", terms, "")
        return solved(5, text, [part(p, [sp.cancel(E)])])
    if re.search(r"subtract", text, re.I) or word_problem(text, ("add", "subtract", "multiply", "divide", "product", "quotient", "sum", "difference")):
        return None
    m = tail_math(text)
    if "=" in m or not ("/" in m or "frac" in m or "\\div" in m):
        return None
    try:
        E = expr(m)
    except ValueError:
        return None
    syms = E.free_symbols
    if not syms or any(len(str(s)) > 1 for s in syms):
        return None
    py = mathtext.to_py(m)
    n, d = sp.fraction(sp.together(E))
    if d == 1:
        return None
    final = sp.cancel(E)
    # one fraction: reduce; a sum/difference of fractions: combine over the L.C.D.; a product/quotient: multiply/divide
    split = mathtext.split_fraction(m)
    if split and not re.search(r"\*|\\div|/.*\(.*\)\s*/", py.replace(split[0], "", 1).replace(split[1], "", 1)):
        num, den = expr(split[0]), expr(split[1])
        if sp.simplify(num / den - E) != 0:                    # the split must be the same expression the student wrote
            return None
        p = fr.reduce("", sp.sstr(num), sp.sstr(den), f"$\\frac{{{sp.latex(num)}}}{{{sp.latex(den)}}}$")
    elif E.is_Add:
        terms = []
        for a in E.as_ordered_terms():
            an, ad = sp.fraction(sp.together(a))
            sign = "-" if an.could_extract_minus_sign() else "+"
            terms.append((sign, sp.sstr(-an if sign == "-" else an), sp.sstr(ad)))
        p = fr.combine("", terms, f"${sp.latex(E)}$")
    else:
        pieces = re.split(r"(\*|/(?=\s*\())", py)
        return None if len(pieces) < 2 else _muldiv(text, py, final)
    return solved(5, text, [part(p, [final])])


def _muldiv(text, py, final):
    """a/b * c/d  or  a/b / (c/d): top-level factors written as (num)/(den)."""
    tokens, depth, cur = [], 0, ""
    ops = []
    i = 0
    while i < len(py):
        ch = py[i]
        depth += ch == "("
        depth -= ch == ")"
        if depth == 0 and ch in "*/" and cur.strip() and (cur.count("(") == cur.count(")")):
            # a top-level / between two bracketed groups is the fraction bar when the next group is a denominator of the
            # current factor; we treat "(a)/(b)" as one factor and a following "*"/"/" as the operation
            nxt = py[i + 1:].lstrip()
            if ch == "/" and cur.strip().endswith(")") and "/" not in cur and nxt.startswith("("):
                cur += ch
            else:
                tokens.append(cur.strip())
                ops.append(ch)
                cur = ""
            i += 1
            continue
        cur += ch
        i += 1
    tokens.append(cur.strip())
    if len(tokens) < 2:
        return None
    factors = []
    for k, tok in enumerate(tokens):
        try:
            e = expr(tok)
        except ValueError:
            return None
        n, d = sp.fraction(sp.together(e))
        factors.append(("" if k == 0 else ("/" if ops[k - 1] == "/" else "*"), sp.sstr(n), sp.sstr(d)))
    p = fr.muldiv("", factors, "")
    return solved(5, text, [part(p, [final])])


# ------------------------------------------------------------------------------------------ Unit 6: vectors


def _vec(s):
    s = s.replace(" ", "").replace("\\underline{i}", "i").replace("\\underline{j}", "j").replace("\\hat{i}", "i").replace("\\hat{j}", "j")
    m = re.fullmatch(r"([+-]?[\d./]*)\*?i([+-][\d./]*)\*?j", s) or re.fullmatch(r"([+-]?[\d./]*)\*?i", s) or re.fullmatch(r"([+-]?[\d./]*)\*?j", s)
    if not m:
        return None

    def c(v):
        return sp.Integer(1) if v in ("", "+") else sp.Integer(-1) if v == "-" else sp.nsimplify(v)
    if s.endswith("j") and "i" in s:
        return c(m.group(1)), c(m.group(2))
    return (c(m.group(1)), sp.Integer(0)) if s.endswith("i") else (sp.Integer(0), c(m.group(1)))


def vectors(text):
    t = norm(text).replace("$", " ")
    low = t.lower()
    u6 = _unit("unit06")
    vecs = {}
    for m in re.finditer(r"\\?(?:underline\{)?\b([a-z])\}?\s*=\s*([-+]?\s*[\d./]*\s*(?:\\underline\{)?[ij]\}?\s*(?:[-+]\s*[\d./]*\s*(?:\\underline\{)?[ij]\}?)?)", t):
        v = _vec(m.group(2).replace("\\underline{", "").replace("}", ""))
        if v and m.group(1) not in "ij":
            vecs[m.group(1)] = v
    if re.search(r"translat|plot|parallelogram|isosceles|kite|square|triangle|project|velocity|parallel|opposite|thrice|double|quadrant|tail|tip", low):
        return None                                            # shapes, motion and drawing questions are not read here
    pts = dict((n, (sp.nsimplify(a), sp.nsimplify(b))) for n, a, b in re.findall(r"\b([A-Z])\s*\(\s*(-?[\d.]+)\s*,\s*(-?[\d.]+)\s*\)", t))
    if len(pts) > 2:
        return None
    if not vecs and len(pts) == 2 and re.search(r"vector|magnitude|\\overrightarrow|distance", low):
        (a, A), (b, B) = list(pts.items())[:2]
        s, v = u6.ab_vector(A, B, a, b)
        steps = [s]
        if "magnitude" in low or "length" in low or "distance" in low:
            ms, mg = u6.mag_steps(v, rf"\overrightarrow{{{a}{b}}}")
            return solved(6, text, [part(P("", steps + ms, f"${u6.num(mg)}$"), [mg])])
        return solved(6, text, [part(P("", steps, f"${u6.vt(v)}$"), list(v))])
    if not vecs:
        lone = re.search(r"([-+]?\s*[\d./]*\s*i\s*[-+]\s*[\d./]*\s*j)", t)
        if lone and re.search(r"magnitude|unit vector|\|", low):
            vecs["a"] = _vec(lone.group(1))
    if not vecs or any(v is None for v in vecs.values()):
        return None
    # a combination of the named vectors written anywhere outside their definitions: 'b - c', '2a - 3b', '\frac{3}{2}a - b'
    rest = re.sub(r"\\underline\{([a-z])\}", r"\1", low)
    rest = re.sub(r"\\frac\{(\d+)\}\{(\d+)\}", r"\1/\2", rest)
    rest = re.sub(r"\b[a-h]\s*=\s*[-+]?\s*[\d./]*\s*i\s*(?:[-+]\s*[\d./]*\s*j)?|\b[a-h]\s*=\s*[-+]?\s*[\d./]*\s*j", " ", rest)
    combo = None
    for m in re.finditer(r"(?<![a-z\\])([-+]?\s*[\d./]*\s*\*?\s*[a-h](?:\s*[-+]\s*[\d./]*\s*\*?\s*[a-h])+)(?![a-z])", rest):
        if all(n in vecs for n in re.findall(r"[a-h]", m.group(1))):
            combo = m
    if len(vecs) > 1 and not combo:
        return None                                            # several vectors and no combination named: not sure what is asked
    if combo and "unit vector" in low:
        terms = re.findall(r"([-+]?)\s*([\d./]*)\s*\*?\s*([a-h])", combo.group(1))
        coefs = [(-1 if sg == "-" else 1) * (sp.nsimplify(k) if k else 1) for sg, k, _ in terms]
        st, v, expr_ = u6.combo(coefs, [vecs[n] for _, _, n in terms], [n for _, _, n in terms])
        us, u = u6.unit_steps(v, "v")
        return solved(6, text, [part(P("", st + [S(rf"\underline{{v}} = {expr_} = {u6.vt(v)}", "Call the result $\\underline{v}$.", "نتیجہ کو $\\underline{v}$ کہیں۔")] + us,
                                       f"${u6.vt(u)}$"), list(u))])
    if "unit vector" in low:
        n = next(iter(vecs))
        st, u = u6.unit_steps(vecs[n], n)
        return solved(6, text, [part(P("", st, f"${u6.vt(u)}$"), list(u))])
    if combo:
        terms = re.findall(r"([-+]?)\s*([\d./]*)\s*\*?\s*([a-h])", combo.group(1))
        coefs, vs, names = [], [], []
        for sg, k, n in terms:
            if n not in vecs:
                return None
            kk = sp.nsimplify(k) if k else sp.Integer(1)
            coefs.append(-kk if sg == "-" else kk)
            vs.append(vecs[n])
            names.append(n)
        st, v, _ = u6.combo(coefs, vs, names)
        if "magnitude" in low:
            ms, mg = u6.mag_steps(v, "v")
            return solved(6, text, [part(P("", st + ms, f"${u6.num(mg)}$"), [mg])])
        return solved(6, text, [part(P("", st, f"${u6.vt(v)}$"), list(v))])
    if "magnitude" in low or re.search(r"\|\s*[a-z]\s*\|", low):
        n = next(iter(vecs))
        st, mg = u6.mag_steps(vecs[n], n)
        return solved(6, text, [part(P("", st, f"${u6.num(mg)}$"), [mg])])
    return None


# ------------------------------------------------------------------------------------------ Unit 7: trigonometry


FN = {"sin": sp.sin, "cos": sp.cos, "tan": sp.tan, "cot": sp.cot, "sec": sp.sec, "cosec": sp.csc, "csc": sp.csc}


def trig_value(text):
    t = norm(text).lower().replace("\\", " ")
    found = re.findall(r"\b(sin|cos|tan|cot|sec|cosec|csc)\s*\(?\s*(-?\d+)\s*(?:deg|\^\s*\{?\s*circ\s*\}?|o\b)?\)?", t)
    if len(found) != 1 or re.search(r"triangle|angle of elevation|ladder|height|theta|θ|blank|alpha|beta|\.\.\.", t):
        return None
    f, d = found[0]
    d = int(d)
    v = FN[f](sp.pi * d / 180)
    if not (v.is_Rational or (v ** 2).is_Rational) or v == sp.zoo:
        return None
    fname = r"\operatorname{cosec}" if f in ("cosec", "csc") else "\\" + f
    q, r = divmod(d % 360, 90)
    quad = ["I", "II", "III", "IV"][(d % 360) // 90] if d % 90 else "an axis"
    steps = [S(rf"{d}^\circ \text{{ is in quadrant {quad}}}", "Find the quadrant; the ratio's sign there gives the sign.", "ربع معلوم کریں؛ وہاں ریشو کی علامت سے علامت ملتی ہے۔"),
             S(rf"{fname}\ {d}^\circ = {sp.latex(v)}", "Use the reference angle and the sign of the ratio in that quadrant.", "حوالہ زاویہ اور اس ربع میں ریشو کی علامت استعمال کریں۔",
               f"{'csc' if f in ('cosec', 'csc') else f}({d}*pi/180) == {sp.sstr(v)}")]
    return solved(7, text, [part(P("", steps, f"${sp.latex(v)}$"), [v])])


def _given(t, names):
    out = {}
    for n in names:
        m = re.search(rf"(?<![a-z\\]){n}\s*=\s*(\d+(?:\.\d+)?)", t)
        if m:
            out[n] = float(m.group(1))
    return out


def triangle(text):
    t = norm(text).lower().replace("\\", "").replace("$", " ").replace("cm", " ")
    if "triangle" not in t and "area" not in t:
        return None
    s = _given(t, ["a", "b", "c"])
    ang = {k: (int(v) if float(v).is_integer() else v) for k, v in _given(t, ["alpha", "beta", "gamma"]).items()}   # 65 degrees, not 65.0
    u7 = _unit("unit07")
    if "area" in t:
        if len(s) == 3:
            p = u7.heron("", s["a"], s["b"], s["c"], "")
            ss = (s["a"] + s["b"] + s["c"]) / 2
            return solved(7, text, [part(p, [round(math.sqrt(ss * (ss - s["a"]) * (ss - s["b"]) * (ss - s["c"])), 2)])])
        pairs = {("a", "b"): "gamma", ("b", "c"): "alpha", ("a", "c"): "beta"}
        for (x1, x2), an in pairs.items():
            if x1 in s and x2 in s and an in ang:
                p = u7.area_sas("", x1, s[x1], x2, s[x2], an, ang[an], "")
                return solved(7, text, [part(p, [round(0.5 * s[x1] * s[x2] * math.sin(math.radians(ang[an])), 2)])])
        if len(s) == 1 and len(ang) == 2:
            (sn, sv), = s.items()
            opp = {"a": "alpha", "b": "beta", "c": "gamma"}[sn]
            p = u7.area_asa("", sn, sv, ang, opp, "")
            third = 180 - sum(ang.values())
            allang = {**ang, [n for n in ("alpha", "beta", "gamma") if n not in ang][0]: third}
            others = [n for n in ("alpha", "beta", "gamma") if n != opp]
            v = sv * sv * math.sin(math.radians(allang[others[0]])) * math.sin(math.radians(allang[others[1]])) / (2 * math.sin(math.radians(allang[opp])))
            return solved(7, text, [part(p, [round(v, 2)])])
        return None
    if "solve" not in t:
        return None
    if len(s) == 1 and len(ang) == 2:
        (sn, sv), = s.items()
        opp = {"a": "alpha", "b": "beta", "c": "gamma"}[sn]
        if opp not in ang:
            return None
        p = u7.solve_aas("", sn, sv, opp, ang, "")
        return solved(7, text, [part(p, [180 - sum(ang.values())])])
    if len(s) == 2 and len(ang) == 1:
        (an, av), = ang.items()
        own = {"alpha": "a", "beta": "b", "gamma": "c"}[an]
        if own not in s:
            return None
        other = [k for k in s if k != own][0]
        if s[other] * math.sin(math.radians(av)) / s[own] >= 1:
            return None
        p = u7.solve_ssa("", own, s[own], other, s[other], an, av, "")
        return solved(7, text, [part(p, [round(math.degrees(math.asin(s[other] * math.sin(math.radians(av)) / s[own])), 1)])])
    return None


# ------------------------------------------------------------------------------------------ Units 8-9: circles


def _len(t, *names):
    for n in names:
        m = re.search(rf"{n}\D{{0,20}}?(\d+(?:\.\d+)?)\s*(?:cm|m|units?)?", t)
        if m:
            return sp.nsimplify(m.group(1))
    return None


def circles(text):
    t = norm(text).lower().replace("$", " ")
    rows, names = None, ("",)
    if "chord" in t:
        r = _len(t, r"radius(?: of the circle)?(?: is)?", r"\br\s*=")
        d = _len(t, r"distance(?: of)?", r"\bd\s*=", r"from the cent(?:re|er) (?:is|at)")
        md = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm|m|units?)?\s*(?:away\s+)?from (?:the )?cent", t)
        if md:
            d = sp.nsimplify(md.group(1))
        ch = _len(t, r"chord(?: of length| of)?", r"(\d+(?:\.\d+)?)\s*(?:cm|m)\s*(?:long|chord)")
        m_long = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm|m)?\s*long", t)
        if m_long:
            ch = sp.nsimplify(m_long.group(1))
        asks_len = re.search(r"length of (?:the |a )?chord|find the chord|length of chord", t)
        if r and d and (asks_len or ch is None):
            if d >= r:
                return None
            h = sp.sqrt(r ** 2 - d ** 2)
            rows = ([(rf"AM = \sqrt{{r^2 - d^2}} = \sqrt{{{sp.latex(r)}^2 - {sp.latex(d)}^2}} = {sp.latex(h)}", "Pythagoras: the perpendicular from the centre bisects the chord.",
                      "فیثا غورث: مرکز سے عمود وتر کی تنصیف کرتا ہے۔", [f"sqrt({g.ps(r)}**2 - {g.ps(d)}**2) == {g.ps(h)}"]),
                     (rf"\text{{Chord}} = 2 \times {sp.latex(h)} = {sp.latex(2 * h)}", "Double the half-chord.", "آدھے وتر کا دگنا۔", [f"2*{g.ps(h)} == {g.ps(2 * h)}"])], 2 * h)
        elif ch and d and re.search(r"radius", t):
            r_ = sp.sqrt(d ** 2 + (ch / 2) ** 2)
            rows = ([(rf"r = \sqrt{{d^2 + \left(\frac{{\text{{chord}}}}{{2}}\right)^2}} = \sqrt{{{sp.latex(d)}^2 + {sp.latex(ch / 2)}^2}} = {sp.latex(r_)}",
                      "Pythagoras in the right triangle formed by the radius, the distance and half the chord.", "رداس، فاصلہ اور آدھے وتر کی قائمہ مثلث میں فیثا غورث۔",
                      [f"sqrt({g.ps(d)}**2 + ({g.ps(ch)}/2)**2) == {g.ps(r_)}"])], r_)
        elif ch and r and re.search(r"distance", t):
            if ch / 2 >= r:
                return None
            d_ = sp.sqrt(r ** 2 - (ch / 2) ** 2)
            rows = ([(rf"d = \sqrt{{r^2 - \left(\frac{{\text{{chord}}}}{{2}}\right)^2}} = \sqrt{{{sp.latex(r)}^2 - {sp.latex(ch / 2)}^2}} = {sp.latex(d_)}",
                      "Pythagoras in the right triangle formed by the radius, the distance and half the chord.", "رداس، فاصلہ اور آدھے وتر کی قائمہ مثلث میں فیثا غورث۔",
                      [f"sqrt({g.ps(r)}**2 - ({g.ps(ch)}/2)**2) == {g.ps(d_)}"])], d_)
        unit = 8
    elif re.search(r"tangent", t) and re.search(r"radius", t) and re.search(r"distance|away|from the cent", t):
        r = _len(t, r"radius(?: of)?(?: is)?", r"\br\s*=")
        d = _len(t, r"(\d+(?:\.\d+)?)\s*(?:cm|m)?\s*(?:away|from the cent)", r"distance(?: of)?")
        m = re.search(r"(\d+(?:\.\d+)?)\s*(?:cm|m)?\s*(?:away )?from the cent", t)
        d = sp.nsimplify(m.group(1)) if m else d
        if not (r and d) or d <= r:
            return None
        L = sp.sqrt(d ** 2 - r ** 2)
        rows = ([(rf"L = \sqrt{{d^2 - r^2}} = \sqrt{{{sp.latex(d)}^2 - {sp.latex(r)}^2}} = {sp.latex(L)}", "The radius is perpendicular to the tangent: Pythagoras.",
                  "رداس مماس پر عمود ہے: فیثا غورث۔", [f"sqrt({g.ps(d)}**2 - {g.ps(r)}**2) == {g.ps(L)}"])], L)
        unit = 9
    elif re.search(r"sector|arc length|arc of length|\bl\s*=|theta|θ|slice", t):
        t = t.replace("\\theta", "theta").replace("\\ell", "l")
        r = _len(t, r"radius(?: of)?(?: is)?", r"\br\s*=")
        th = re.search(r"(?:theta|θ|angle)\s*(?:of|=|is)?\s*(\d+(?:\.\d+)?)\s*(deg|radians?|rad)?", t)
        l_ = _len(t, r"\bl\s*=", r"arc length(?: of| is)?", r"arc of length")
        if r and th and not re.search(r"find\s+(?:the\s+)?(?:radius|\br\b)", t):
            v = sp.nsimplify(th.group(1))
            th_r = v * sp.pi / 180 if (th.group(2) or "").startswith("deg") else v
            l, A = r * th_r, R(1, 2) * r ** 2 * th_r
            rows = ([(rf"\theta = {sp.latex(th_r)}\ \text{{rad}},\quad \ell = r\theta = {sp.latex(sp.nsimplify(l))} \approx {float(l):.2f}", "Arc length $\\ell = r\\theta$ ($\\theta$ in radians).",
                      "قوس کی لمبائی $\\ell = r\\theta$۔", [f"{g.ps(r)}*{g.ps(th_r)} == {g.ps(l)}"]),
                     (rf"A = \frac{{1}}{{2}}r^2\theta = {sp.latex(sp.nsimplify(A))} \approx {float(A):.2f}", "Area of the sector.", "قطاع کا رقبہ۔",
                      [f"R(1,2)*{g.ps(r)}**2*{g.ps(th_r)} == {g.ps(A)}"])], (l, A))
            names = (r"\ell", "A")
        elif l_ and r and re.search(r"\barea\b", t):
            A = R(1, 2) * l_ * r
            rows = ([(rf"A = \frac{{1}}{{2}}\ell r = \frac{{1}}{{2}}({sp.latex(l_)})({sp.latex(r)}) = {sp.latex(A)}", "Area of a sector from its arc: $A = \\frac{1}{2}r^2\\theta = \\frac{1}{2}\\ell r$.",
                      "قوس سے قطاع کا رقبہ: $A = \\frac{1}{2}\\ell r$۔", [f"R(1,2)*{g.ps(l_)}*{g.ps(r)} == {g.ps(A)}"])], A)
        elif l_ and r:
            thv = l_ / r
            rows = ([(rf"\theta = \frac{{\ell}}{{r}} = \frac{{{sp.latex(l_)}}}{{{sp.latex(r)}}} = {sp.latex(thv)} \approx {float(thv):.2f}\ \text{{rad}}", "$\\ell = r\\theta$, so $\\theta = \\frac{\\ell}{r}$.",
                      "$\\theta = \\frac{\\ell}{r}$۔", [f"{g.ps(l_)}/{g.ps(r)} == {g.ps(thv)}"])], thv)
        unit = 9
    else:
        return None
    if not rows:
        return None
    steps_, val = rows
    steps = [S(a, b, c, *d) for a, b, c, d in steps_]
    vals = list(val) if isinstance(val, tuple) else [val]
    labels = names if isinstance(val, tuple) else [""]
    ans = ",\\ ".join((f"{n} = " if n else "") + f"{sp.latex(sp.nsimplify(v))}" + (f" \\approx {float(v):.2f}" if not sp.nsimplify(v).is_Rational else "")
                       for n, v in zip(labels, vals))
    return solved(unit, text, [part(P("", steps, f"${ans}$"), vals)])


# ------------------------------------------------------------------------------------------ Unit 11: statistics


def statistics(text):
    t = norm(text).lower()
    if not re.search(r"mean|average|variance|standard deviation|\bs\.?d\b|range|median|quartile|dispersion", t):
        return None
    # one plain list of data only: no grouped classes, given sums, summaries, ranges of classes or two data sets to compare
    if re.search(r"class|frequency|\bf\b|interval|grouped|\\sum|∑|sum of|summary|min\.?\s*value|max\.?\s*value|box|family|machine|person|"
                 r"\bfirst\s+\d+|speed|velocity|km|rate of|table|number of|places", t) or re.search(r"\d\s*-\s*\d", t) \
            or len(re.findall(r"(?:-?\d+(?:\.\d+)?\s*,\s*){2,}-?\d+(?:\.\d+)?", t)) > 1:
        return None
    if not re.search(r"(-?\d+(?:\.\d+)?\s*,\s*){2,}-?\d+(?:\.\d+)?", t):
        return None
    data = numbers_in(t.split(":", 1)[1] if ":" in t else t)
    if len(data) < 3:
        return None
    u11 = _unit("unit11")
    parts = []
    if re.search(r"variance|standard deviation|\bs\.?d\b|dispersion", t):
        st, m, v, s = u11.dispersion([str(d) for d in data])
        parts.append(part(P("", st, f"Mean = {u11.fmt(m, 2)}, Variance = {u11.fmt(v, 2)}, SD = {u11.fmt(s, 2)}"), [m, v, s]))
    elif re.search(r"median|quartile|box", t):
        p = u11.five_number("", [str(d) for d in data], "")
        d = sorted(data)
        n = len(d)
        parts.append(part(p, [u11.item(d, R(n + 1, 2)), u11.item(d, R(n + 1, 4)), u11.item(d, R(3 * (n + 1), 4))]))
    elif "range" in t:
        hi, lo = max(data), min(data)
        parts.append(part(P("", [S(rf"\text{{Range}} = {sp.latex(hi)} - {sp.latex(lo)} = {sp.latex(hi - lo)}", "Highest minus lowest.", "بڑی منفی چھوٹی۔",
                                   f"{g.ps(hi)} - {g.ps(lo)} == {g.ps(hi - lo)}")], f"${sp.latex(hi - lo)}$"), [hi - lo]))
    elif re.search(r"mean|average", t):
        m = sum(data) / len(data)
        parts.append(part(P("", [S(rf"\bar{{x}} = \frac{{{' + '.join(map(str, data))}}}{{{len(data)}}} = {sp.latex(m)}", "Sum divided by the number of values.", "مجموعہ تقسیم تعداد۔",
                                   f"({' + '.join(g.ps(d) for d in data)})/{len(data)} == {g.ps(m)}")], f"${sp.latex(m)}$"), [m]))
    return solved(11, text, parts) if parts else None


# ------------------------------------------------------------------------------------------ Unit 12: probability


DIE = range(1, 7)


def _dice_event(t):
    k = numbers_in(t)
    if re.search(r"same number|doublet|doubles", t):
        return lambda s: s[0] == s[1], "the same number on both dice"
    for word, f in (("sum", lambda s: s[0] + s[1]), ("product", lambda s: s[0] * s[1]), ("difference", lambda s: abs(s[0] - s[1]))):
        if word in t:
            if re.search(rf"{word}\D*(?:is\s+|as\s+(?:an?\s+)?)?(even|odd|prime)", t):
                kind = re.search(rf"{word}\D*(even|odd|prime)", t).group(1)
                test = {"even": lambda v: v % 2 == 0, "odd": lambda v: v % 2 == 1, "prime": lambda v: v in {2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31}}[kind]
                return (lambda s, f=f, test=test: test(f(s))), f"the {word} {kind}"
            m = re.search(rf"{word}\D*?(greater than|more than|less than|at least|at most)\s*(\d+)", t)
            if m:
                c = int(m.group(2))
                cmp = {"greater than": lambda v: v > c, "more than": lambda v: v > c, "less than": lambda v: v < c, "at least": lambda v: v >= c,
                       "at most": lambda v: v <= c}[m.group(1)]
                return (lambda s, f=f, cmp=cmp: cmp(f(s))), f"the {word} {m.group(1)} {c}"
            vals = [int(v) for v in re.findall(rf"(?<=\D)(\d+)", t[t.index(word):])][:3]
            if vals:
                return (lambda s, f=f, vals=vals: f(s) in vals), f"the {word} " + " or ".join(map(str, vals))
    return None


def probability(text):
    t = norm(text).lower()
    if not re.search(r"probab|chance", t):
        return None
    # what this solver does not read reliably is declined, never guessed:
    if re.search(r"\beither\b|replacement|\bcards?\b|\bdeck\b|\btwo\s+(?:balls|marbles|cards)|one after the other|successively|letters?|word|"
                 r"rains?|weather|team|match|vehicles?|\bp\s*\(", t):
        return None
    if re.search(r"\b(?:dice|die)\b", t) and re.search(r"\bcoins?\b", t):          # a die and a coin together
        return None
    ops = sum(bool(re.search(rf"\b{w}\b", t)) for w in ("sum", "product", "difference", "same"))
    props = sum(bool(re.search(rf"\b{w}\b", t)) for w in ("prime", "even", "odd", "multiple", "greater", "less"))
    if ops > 1 or (props > 1 and re.search(r"\bor\b", t)):
        return None                                                                  # two different events joined by 'or'
    u12 = _unit("unit12")
    if re.search(r"\btwo\s+(?:unbiased\s+|fair\s+)?dice|\b2\s+dice|\bdice\b.*\b(?:twice|two times)|rolled twice|thrown twice|pair of dice", t):
        ev = _dice_event(t)
        if not ev:
            return None
        p, val = u12.event_part("", u12.DICE2, "two dice, 36 outcomes", ev[0], "", listed=len([s for s in u12.DICE2 if ev[0](s)]) <= 12)
        return solved(12, text, [part(p, [val])])
    if re.search(r"\bdice\b|\bdie\b", t):
        faces = list(DIE)
        if "even" in t:
            ev = lambda n: n % 2 == 0  # noqa: E731
        elif "odd" in t:
            ev = lambda n: n % 2 == 1  # noqa: E731
        elif "prime" in t:
            ev = lambda n: n in (2, 3, 5)  # noqa: E731
        elif re.search(r"greater than (\d)", t):
            c = int(re.search(r"greater than (\d)", t).group(1))
            ev = lambda n: n > c  # noqa: E731
        elif re.search(r"less than (\d)", t):
            c = int(re.search(r"less than (\d)", t).group(1))
            ev = lambda n: n < c  # noqa: E731
        elif numbers_in(t):
            c = int(numbers_in(t)[-1])
            ev = lambda n: n == c  # noqa: E731
        else:
            return None
        p, val = u12.event_part("", faces, "one die, 6 outcomes", ev, "")
        return solved(12, text, [part(p, [val])])
    coins = re.search(r"(\d+|two|three|four|one|a)\s+(?:fair\s+)?coins?|coin is tossed (once|twice|thrice|three times)", t)
    if coins:
        w = coins.group(1) or coins.group(2)
        n = {"a": 1, "one": 1, "once": 1, "two": 2, "twice": 2, "three": 3, "thrice": 3, "three times": 3, "four": 4}.get(w, None) or int(w)
        if n > 5:
            return None
        space = ["".join(s) for s in product("HT", repeat=n)]
        hd = lambda s: s.count("H")  # noqa: E731
        m = re.search(r"(at least|at most|exactly)?\s*(\d+|one|two|three|no|all)\s+(heads?|tails?)", t)
        if not m:
            return None
        q, k, side = m.groups()
        k = {"one": 1, "two": 2, "three": 3, "no": 0}.get(k, k)
        side = "H" if side.startswith("h") else "T"
        cnt = lambda s: s.count(side)  # noqa: E731
        if k == "all":
            ev = lambda s: cnt(s) == n  # noqa: E731
        else:
            k = int(k)
            ev = {"at least": lambda s: cnt(s) >= k, "at most": lambda s: cnt(s) <= k}.get(q, lambda s: cnt(s) == k)
        p, val = u12.event_part("", space, f"{n} coins, {len(space)} outcomes", ev, "")
        return solved(12, text, [part(p, [val])])
    bag = re.findall(r"(\d+)\s+(red|white|green|black|blue|yellow|orange|purple|pink)", t)
    if bag and len(bag) >= 2:
        total = sum(int(a) for a, _ in bag)
        colours = {c: int(a) for a, c in bag}
        asked = re.findall(r"(not\s+(?:a\s+)?)?(red|white|green|black|blue|yellow|orange|purple|pink)\b", t[t.find("probab"):])
        if not asked:
            return None
        neg, col = asked[-1]
        k = colours.get(col, 0)
        k = total - k if neg else k
        val = R(k, total)
        steps = [S(rf"n(S) = {' + '.join(str(v) for v in colours.values())} = {total},\quad n(E) = {k},\quad P = \frac{{{k}}}{{{total}}} = {sp.latex(val)}",
                   "Favourable balls divided by all balls.", "موافق گیندیں تقسیم کل گیندیں۔", f"R({k}, {total}) == {sp.sstr(val)}")]
        return solved(12, text, [part(P("", steps, f"${sp.latex(val)}$"), [val])])
    return None


# ------------------------------------------------------------------------------------------ the order of tries


SOLVERS = [probability, statistics, matrices, circles, linear_system, functions, absolute, vectors, roots_to_eq, nature, triangle, trig_value,
           q_inequality, quadratic, fractions]


def solve(text):
    if not text or len(text) > 1500:
        return None
    for f in SOLVERS:
        try:
            item = f(text)
        except (ValueError, TypeError, ZeroDivisionError, AttributeError, IndexError, KeyError, sp.SympifyError, sp.PolynomialError,
                NotImplementedError, RecursionError, StopIteration):
            item = None
        if item and item.get("parts") and all_true(item["parts"]):
            return item
    return None
