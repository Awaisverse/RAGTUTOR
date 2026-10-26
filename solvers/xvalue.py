"""Questions that give x = a + sqrt(b) and ask for x + 1/x, x^2 - 1/x^2, ...; and 'find p and q' after rationalizing."""
import re

import sympy as sp

import mathast as A

from .algebra import rationalize_part
from .common import P, R, S, T, failed_checks, mathtext, paren, part_markers, py, solved_item, tex


def _finish(question, parts):
    item = solved_item(question, parts)
    return item if not failed_checks(item) else None


def _plain(s):
    return s.replace("$", " ").strip().rstrip(".,;?:").strip()


# =========================================================================================================
# If x = 3 + sqrt8, find x + 1/x, x - 1/x, x^2 + 1/x^2, x^2 - 1/x^2, x^4 + 1/x^4, (x - 1/x)^2
# =========================================================================================================

def _target_kind(expr, X):
    inv = 1 / X
    patterns = {"sum": X + inv, "diff": X - inv, "sq_sum": X ** 2 + inv ** 2, "sq_diff": X ** 2 - inv ** 2, "fourth_sum": X ** 4 + inv ** 4,
                "diff_sq": (X - inv) ** 2, "sum_sq": (X + inv) ** 2}
    for kind, pat in patterns.items():
        if sp.simplify(expr - pat) == 0:
            return kind
    return None


def _x_part(label, name, X, xval, rhs_tree, target_text):
    tree = A.parse(target_text)
    target = A.to_sympy(tree)
    if {str(s) for s in target.free_symbols} != {name}:
        return None
    inv_part = rationalize_part("", sp.Integer(1), xval)
    if inv_part is None:
        return None
    inv = sp.radsimp(1 / xval)
    steps = []
    typed = A.tex(rhs_tree, 0, True)
    if typed.replace(" ", "") != tex(xval).replace(" ", ""):
        steps.append(S(rf"{name} = {typed} = {tex(xval)}", "Simplify the root in x first.", f"پہلے {name} میں موجود جذر کو سادہ کریں۔",
                       f"{py(A.to_sympy(rhs_tree))} == {py(xval)}"))
    for st in inv_part["steps"]:
        steps.append(st)
    s_val, d_val = sp.simplify(xval + inv), sp.simplify(xval - inv)
    inv_tex = rf"\frac{{1}}{{{name}}}"
    kind = _target_kind(target, X)
    value = sp.simplify(sp.expand(target.subs(X, xval)))

    def line_sum():
        return S(rf"{name}+{inv_tex} = {tex(xval)} + {paren(inv)} = {tex(s_val)}", "Add. The roots cancel.", "جمع کریں۔ جذر ختم ہو جاتے ہیں۔",
                 f"({py(xval)}) + ({py(inv)}) == {py(s_val)}")

    def line_diff():
        return S(rf"{name}-{inv_tex} = {tex(xval)} - \left({tex(inv)}\right) = {tex(d_val)}", "Subtract. The whole numbers cancel.", "منفی کریں۔ پورے اعداد ختم ہو جاتے ہیں۔",
                 f"({py(xval)}) - ({py(inv)}) == {py(d_val)}")

    sq_sum = sp.simplify(s_val ** 2 - 2)
    if kind == "sum":
        steps.append(line_sum())
    elif kind == "diff":
        steps.append(line_diff())
    elif kind == "sq_sum":
        steps += [line_sum(),
                  S(rf"\left({name}+{inv_tex}\right)^2 = {name}^2+2+\frac{{1}}{{{name}^2}} \;\Rightarrow\; {name}^2+\frac{{1}}{{{name}^2}} = {tex(s_val)}^2 - 2 = {tex(value)}",
                    "Square both sides and use $(a+b)^2 = a^2+2ab+b^2$.", "دونوں طرف مربع لیں اور $(a+b)^2 = a^2+2ab+b^2$ استعمال کریں۔",
                    f"({py(xval)})**2 + ({py(inv)})**2 == ({py(s_val)})**2 - 2", f"({py(s_val)})**2 - 2 == {py(value)}")]
    elif kind == "sq_diff":
        steps += [line_sum(), line_diff(),
                  S(rf"{name}^2-\frac{{1}}{{{name}^2}} = \left({name}+{inv_tex}\right)\left({name}-{inv_tex}\right) = {tex(s_val)} \times {paren(d_val)} = {tex(value)}",
                    "Use $a^2-b^2 = (a+b)(a-b)$.", "$a^2-b^2 = (a+b)(a-b)$ استعمال کریں۔",
                    f"({py(xval)})**2 - ({py(inv)})**2 == ({py(s_val)})*({py(d_val)})", f"({py(s_val)})*({py(d_val)}) == {py(value)}")]
    elif kind == "fourth_sum":
        steps += [line_sum(),
                  S(rf"{name}^2+\frac{{1}}{{{name}^2}} = \left({name}+{inv_tex}\right)^2 - 2 = {tex(s_val)}^2 - 2 = {tex(sq_sum)}",
                    "Square $x+\\frac{1}{x}$ and subtract 2.", "$x+\\frac{1}{x}$ کا مربع لیں اور 2 منفی کریں۔",
                    f"({py(xval)})**2 + ({py(inv)})**2 == ({py(s_val)})**2 - 2"),
                  S(rf"{name}^4+\frac{{1}}{{{name}^4}} = \left({name}^2+\frac{{1}}{{{name}^2}}\right)^2 - 2 = {tex(sq_sum)}^2 - 2 = {tex(value)}",
                    "Square again and subtract 2.", "دوبارہ مربع لیں اور 2 منفی کریں۔",
                    f"({py(xval)})**4 + ({py(inv)})**4 == ({py(sq_sum)})**2 - 2", f"({py(sq_sum)})**2 - 2 == {py(value)}")]
    elif kind == "diff_sq":
        steps += [line_diff(),
                  S(rf"\left({name}-{inv_tex}\right)^2 = \left({tex(d_val)}\right)^2 = {tex(value)}", "Square the result of $x-\\frac{1}{x}$.", "$x-\\frac{1}{x}$ کے نتیجے کا مربع لیں۔",
                    f"({py(d_val)})**2 == {py(value)}")]
    elif kind == "sum_sq":
        steps += [line_sum(),
                  S(rf"\left({name}+{inv_tex}\right)^2 = \left({tex(s_val)}\right)^2 = {tex(value)}", "Square the result of $x+\\frac{1}{x}$.", "$x+\\frac{1}{x}$ کے نتیجے کا مربع لیں۔",
                    f"({py(s_val)})**2 == {py(value)}")]
    else:
        steps.append(S(rf"{A.tex(tree, 0, True)} = {tex(value)}", f"Put {name} = {tex(xval)} and {inv_tex} = {tex(inv)} into the expression and simplify.",
                       f"{name} = {tex(xval)} اور {inv_tex} = {tex(inv)} کو عبارت میں رکھ کر سادہ کریں۔", f"{py(target.subs(X, xval))} == {py(value)}"))
    return P(label, steps, f"${tex(value)}$", prompt=f"${A.tex(tree, 0, True)}$")


def try_value_of_x(text):
    pieces = part_markers(text)
    stem = _plain(pieces[0])
    m = re.search(r"\b([a-z])\s*=\s*(.+?)(?=\s+(?:then|find|what|evaluate|calculate|compute|if)\b|[,;]|$)", stem, re.I)
    if not m:
        return None
    name = m.group(1).lower()
    try:
        rhs_tree = A.parse(m.group(2))
        xval = A.to_sympy(rhs_tree)
    except ValueError:
        return None
    if xval.free_symbols or xval.is_Rational:
        return None
    if len(pieces) > 1:
        targets = [_plain(p) for p in pieces[1:] if p.strip()]
        if len(targets) != len(pieces) - 1:
            return None
    else:
        # one target, in either order: "If x = 3+sqrt8 then find x+1/x"  or  "find x+1/x if x = 3+sqrt8"
        plain = _plain(text)
        rest = plain.replace(m.group(0), " ", 1) if m.group(0) in plain else plain
        rest = re.sub(r"\b(?:if|when|given|then|find|the|value|of|what|is|evaluate|calculate|compute|that)\b|[:,?]", " ", rest, flags=re.I)
        rest = re.sub(r"\s+", " ", rest).strip().rstrip(".").strip()
        if not rest or "=" in rest:
            return None
        targets = [rest]
    X = sp.Symbol(name, positive=True)
    parts = []
    names = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii"]
    for lab, tgt in zip(names if len(targets) > 1 else [""], targets):
        try:
            part = _x_part(lab, name, X, xval, rhs_tree, tgt)
        except (ValueError, TypeError):
            return None
        if part is None:
            return None
        parts.append(part)
    q = f"If ${name} = {A.tex(rhs_tree, 0, True)}$ then find the value of: " + " ".join((f"({p['label']}) " if p["label"] else "") + p["prompt"] for p in parts)
    return _finish(q, parts)


# =========================================================================================================
# Find the rational numbers p and q such that (8 - 3 sqrt2) / (4 + 3 sqrt2) = p + q sqrt2
# =========================================================================================================

def try_find_pq(text):
    if not re.search(r"\bfind\b.*\b(?:rational numbers?|values?)\b.*\b[a-z]\s+and\s+[a-z]\b.*such that", text.replace("$", " "), re.I | re.S):
        return None
    dollars = [d for d in re.findall(r"\$([^$]+)\$", text) if "=" in d]
    equation = dollars[0] if dollars else re.split(r"such that", text, flags=re.I)[-1]
    sides = A.top_split(_plain(equation), "=")
    if len(sides) != 2:
        return None
    try:
        halves = mathtext.split_fraction(sides[0])
        if halves is None:
            return None
        num, den = mathtext.parse_math(halves[0]), mathtext.parse_math(halves[1])
        right = A.parse(sides[1])
        r = A.to_sympy(right)
    except ValueError:
        return None
    syms = sorted(r.free_symbols, key=str)
    roots = [a for a in r.atoms(sp.Pow) if a.exp == R(1, 2) and a.base.is_Integer]
    if len(syms) != 2 or len(roots) != 1:
        return None
    root = roots[0]
    q_sym = next((s for s in syms if sp.simplify(r.coeff(root)) == s), None)
    p_sym = next((s for s in syms if s != q_sym), None)
    if q_sym is None or sp.simplify(r - (p_sym + q_sym * root)) != 0:
        return None
    part = rationalize_part("", num, den)
    if part is None:
        return None
    res = sp.radsimp(num / den)
    p_val = sp.simplify(res.subs(root, 0))
    q_val = sp.simplify((res - p_val) / root)
    if not (p_val.is_Rational and q_val.is_Rational):
        return None
    steps = list(part["steps"])
    steps.append(S(rf"{tex(res)} = {A.tex(right, 0, True)} \;\Rightarrow\; {p_sym} = {tex(p_val)}, \; {q_sym} = {tex(q_val)}",
                   f"Compare the rational parts and the coefficients of ${tex(root)}$ on both sides.",
                   f"دونوں طرف ناطق حصوں اور ${tex(root)}$ کے عددی سروں کا موازنہ کریں۔", f"{py(res)} == {py(p_val + q_val * root)}"))
    q = f"Find the rational numbers ${p_sym}$ and ${q_sym}$ such that ${A.tex(A.parse(sides[0]), 0, True)} = {A.tex(right, 0, True)}$."
    return _finish(q, [P("", steps, rf"${p_sym}={tex(p_val)},\ {q_sym}={tex(q_val)}$")])
