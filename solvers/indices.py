"""Laws of indices: products and quotients of numeric powers, powers with an unknown exponent, roots of variables, the cube identity.

Every solver reads the question into a tree (mathast), solves THAT expression, and builds the working from its own structure.
"""
import re

import sympy as sp

import mathast as A

from .algebra import _power_part
from .common import P, R, S, T, failed_checks, labels, mathtext, part_markers, py, solved_item, tex


def _finish(question, parts):
    item = solved_item(question, parts)
    return item if not failed_checks(item) else None


def expression_texts(text):
    """The maths of a question, one string per part: from (i)(ii) markers, else the first $...$, else the text from the first maths symbol."""
    pieces = part_markers(text)
    raw = [p for p in pieces[1:] if p] if len(pieces) > 1 else [text]
    if len(pieces) > 1 and len(raw) != len(pieces) - 1:
        return None
    out = []
    for r in raw:
        dollars = re.findall(r"\$([^$]+)\$", r)
        if len(raw) == 1 and len(dollars) > 1:
            return None                       # several maths pieces and no (i)(ii) markers: do not guess which one is meant
        piece = dollars[0] if dollars else re.sub(r"^.*?(?:simplify|evaluate|calculate|compute|value of)\s*:?\s*", "", r, flags=re.I)
        out.append(piece.strip().rstrip(".,;?:").strip())
    return out


def _question(prefix, parts):
    return prefix + " " + (" ".join(f"({p['label']}) {p['prompt']}" for p in parts) if len(parts) > 1 else parts[0]["prompt"])


# =========================================================================================================
# numeric expressions made of powers: (3/4)^-2 / (4/9)^3 * 16/27,  25^(3/2) * 243^(3/5) / (16^(5/4) * 8^(4/3)),  sqrt(...)
# =========================================================================================================

class _Unsupported(Exception):
    pass


def _is_fraction(n):
    """Only numbers, brackets, minus signs and / : 16/27, (-3/4), 4."""
    n = A.strip(n)
    if n[0] == "num":
        return True
    if n[0] == "neg":
        return _is_fraction(n[1])
    return n[0] == "bin" and n[1] == "/" and _is_fraction(n[2]) and _is_fraction(n[3])


def _value_tex(v):
    return tex(v)


def _node_steps(node):
    """-> (steps, value) for a numeric expression tree; raises _Unsupported for anything that is not numbers and rational powers."""
    n = A.strip(node)
    value = A.to_sympy(n)
    if value.free_symbols:
        raise _Unsupported
    if _is_fraction(n):
        return [], value
    if n[0] == "bin" and n[1] == "^":
        bsteps, bval = _node_steps(n[2])
        esteps, eval_ = _node_steps(n[3])
        if esteps or not (bval.is_Rational and eval_.is_Rational):
            raise _Unsupported
        part = _power_part("", bval, eval_)
        if part is None:
            raise _Unsupported
        return bsteps + part["steps"], value
    if n[0] == "call" and n[1] in ("sqrt", "cbrt"):
        isteps, ival = _node_steps(n[2][0])
        part = _power_part("", ival, R(1, 2) if n[1] == "sqrt" else R(1, 3))
        if part is None:
            raise _Unsupported
        return isteps + part["steps"], value
    if n[0] == "bin" and n[1] in ("*", "/", "imp"):
        fs = A.factors(n)
        steps, vals = [], []
        for f, sign in fs:
            s, v = _node_steps(f)
            steps += s
            vals.append((v, sign))
        if not value.is_Rational:
            raise _Unsupported
        line = _value_tex(vals[0][0])
        expr = f"({py(vals[0][0])})" if vals[0][1] == 1 else f"1/({py(vals[0][0])})"
        if vals[0][1] == -1:
            line = rf"\frac{{1}}{{{line}}}"
        for v, sign in vals[1:]:
            line += (r" \times " if sign == 1 else r" \div ") + (rf"\left({_value_tex(v)}\right)" if not v.is_Integer else _value_tex(v))
            expr += f"*({py(v)})" if sign == 1 else f"/({py(v)})"
        steps.append(S(f"{line} = {_value_tex(value)}",
                       "Now multiply and divide from left to right. Dividing by a fraction means multiplying by its reciprocal.",
                       "اب بائیں سے دائیں ضرب اور تقسیم کریں۔ کسر سے تقسیم کا مطلب اس کے معکوس سے ضرب ہے۔", f"{expr} == {py(value)}"))
        return steps, value
    raise _Unsupported


def try_numeric_expression(text):
    exprs = expression_texts(text)
    if not exprs:
        return None
    parts = []
    for lab, e in zip(labels(len(exprs)) if len(exprs) > 1 else [""], exprs):
        try:
            tree = A.parse(e)
            steps, value = _node_steps(tree)
        except (ValueError, _Unsupported):
            return None
        if not steps or not value.is_Rational:
            return None
        parts.append(P(lab, steps, f"${_value_tex(value)}$", prompt=f"${A.tex(tree, 0, True)}$"))
    return _finish(_question("Simplify", parts) + ("" if len(parts) > 1 else "."), parts)


# =========================================================================================================
# powers with an unknown exponent:  (5*25^(n+1) - 25*5^(2n)) / (5*5^(2n+3) - 25^(n+1))
# =========================================================================================================

def _prime_power(b):
    f = sp.factorint(int(b))
    return (next(iter(f)), next(iter(f.values()))) if len(f) == 1 else None


def _bases_with_symbol(node, sym, found):
    n = A.strip(node)
    if n[0] == "bin":
        if n[1] == "^" and sym in A.symbols(n[3]):
            base = A.strip(n[2])
            if base[0] != "num":
                raise _Unsupported
            found.append(int(sp.Rational(base[1])))
        for sub in (n[2], n[3]):
            _bases_with_symbol(sub, sym, found)
    elif n[0] in ("neg", "group"):
        _bases_with_symbol(n[1], sym, found)
    elif n[0] == "call":
        for a in n[2]:
            _bases_with_symbol(a, sym, found)


def _sum_in_prime_power(node, p, s):
    """A sum of terms c * p^(a*s + d) -> (steps text pieces, a, n0): every term as K * p^(a*s), K a number, a common to all terms."""
    pieces, a_common, total = [], None, 0
    for term, sign in A.terms(node):
        t = A.to_sympy(term)
        K = sp.simplify(t.subs(s, 0))
        a = sp.simplify(sp.diff(sp.log(t), s) / sp.log(p))
        if not (K.is_Rational and a.is_Rational):
            raise _Unsupported
        if a_common is None:
            a_common = a
        elif a != a_common:
            raise _Unsupported
        pieces.append((term, sign, t, K * sign))
        total += K * sign
    return pieces, a_common, total


def _exponent_part(label, text):
    tree = A.strip(A.parse(text))
    if tree[0] == "bin" and tree[1] == "/":
        n_node, d_node = tree[2], tree[3]
    else:
        n_node, d_node = tree, ("num", "1")
    syms = A.symbols(tree)
    if len(syms) != 1:
        raise _Unsupported
    sname = next(iter(syms))
    s = sp.Symbol(sname, positive=True)
    bases = []
    _bases_with_symbol(tree, sname, bases)
    primes = {_prime_power(b)[0] if _prime_power(b) else None for b in bases}
    if not bases or None in primes or len(primes) != 1:
        raise _Unsupported
    p = primes.pop()
    n_pieces, a_n, n0 = _sum_in_prime_power(n_node, p, s)
    d_pieces, a_d, d0 = _sum_in_prime_power(d_node, p, s)
    if d0 == 0:
        raise _Unsupported
    steps = []

    def rewrite(pieces, a):
        out = ""
        for i, (term, sign, t, signed_k) in enumerate(pieces):
            body = rf"{tex(abs(signed_k))}\cdot {p}^{{{_exp_tex(a, sname)}}}" if abs(signed_k) != 1 else rf"{p}^{{{_exp_tex(a, sname)}}}"
            out += (("-" if sign < 0 else "") if i == 0 else (" - " if sign < 0 else " + ")) + body
        return out

    for name, node, pieces, a, total in (("numerator", n_node, n_pieces, a_n, n0), ("denominator", d_node, d_pieces, a_d, d0)):
        if name == "denominator" and d_node == ("num", "1"):
            continue
        checks = [f"{py(t)} == {py(t.subs(s, 0))}*{p}**({py(a)}*{sname})" for _, _, t, _ in pieces]
        steps.append(S(rf"{A.tex(node, 0, True)} = {rewrite(pieces, a)}",
                       f"Write every term of the {name} as a number times a power of {p}, using $(a^m)^n = a^{{mn}}$ and $a^{{m+n}} = a^m a^n$.",
                       f"{'شمار کنندہ' if name == 'numerator' else 'نسب نما'} کے ہر رکن کو ایک عدد ضرب {p} کی طاقت کی شکل میں لکھیں۔", *checks))
        common = rf"{p}^{{{_exp_tex(a, sname)}}}"
        steps.append(S(rf"= {common}\left({_sum_tex(pieces)}\right) = {tex(total)}\cdot {common}",
                       f"Take out the common factor ${common}$ and add the numbers.", f"مشترک جزو ${common}$ نکالیں اور اعداد جمع کریں۔",
                       f"{py(sum(x[1] * x[2] for x in pieces))} == {py(total)}*{p}**({py(a)}*{sname})"))
    ratio = sp.nsimplify(n0 / d0) * sp.Pow(p, (a_n - a_d) * s) if a_n != a_d else sp.nsimplify(n0 / d0)
    full = A.to_sympy(tree)
    if d_node == ("num", "1"):
        raise _Unsupported
    if a_n == a_d:
        steps.append(S(rf"\frac{{{tex(n0)}\cdot {p}^{{{_exp_tex(a_n, sname)}}}}}{{{tex(d0)}\cdot {p}^{{{_exp_tex(a_d, sname)}}}}} = \frac{{{tex(n0)}}}{{{tex(d0)}}} = {tex(ratio)}",
                       f"Cancel the common factor ${p}^{{{_exp_tex(a_n, sname)}}}$ and simplify the fraction.",
                       f"مشترک جزو ${p}^{{{_exp_tex(a_n, sname)}}}$ کاٹیں اور کسر کو مختصر کریں۔", f"{py(full)} == {py(ratio)}"))
    else:
        raise _Unsupported
    return P(label, steps, f"${tex(ratio)}$", prompt=f"${A.tex(tree, 0, True)}$"), ratio


def _exp_tex(a, s):
    return s if a == 1 else f"{tex(a)}{s}"


def _sum_tex(pieces):
    out = ""
    for i, (_, sign, _, k) in enumerate(pieces):
        out += (("-" if sign < 0 else "") if i == 0 else (" - " if sign < 0 else " + ")) + tex(abs(k))
    return out


def try_exponent_algebra(text):
    exprs = expression_texts(text)
    if not exprs:
        return None
    parts = []
    for lab, e in zip(labels(len(exprs)) if len(exprs) > 1 else [""], exprs):
        try:
            part, _ = _exponent_part(lab, e)
        except (ValueError, _Unsupported, TypeError, ZeroDivisionError):
            return None
        parts.append(part)
    return _finish(_question("Simplify", parts) + ("" if len(parts) > 1 else "."), parts)


# =========================================================================================================
# a root of powers of variables:  7th root of (x^14 y^21 z^35 / (y^14 z^7))
# =========================================================================================================

def _var_exponents(node):
    """A product of numbers and powers of unknowns -> (exponent of each unknown, numeric coefficient, value).
    Raises _Unsupported for anything else (a sum inside the root, for example)."""
    v = A.to_sympy(node)
    names = {str(s) for s in v.free_symbols}
    coef = sp.simplify(v.subs({s: 1 for s in v.free_symbols}))
    exps = {str(k): sp.Rational(e) for k, e in v.as_powers_dict().items() if k.is_Symbol}
    rebuilt = coef * sp.Mul(*[sp.Symbol(k, positive=True) ** e for k, e in exps.items()])
    if not coef.is_Rational or coef <= 0 or sp.simplify(v - rebuilt) != 0 or set(exps) != names:
        raise _Unsupported
    return exps, coef, v


def _monomial_tex(exps, coef=1):
    out = "" if coef == 1 else tex(coef)
    for name in sorted(exps):
        e = exps[name]
        if e == 0:
            continue
        out += (r"\," if out else "") + (name if e == 1 else rf"{name}^{{{tex(e)}}}")
    return out or "1"


def _monomial_expr(exps, coef=1):
    return coef * sp.Mul(*[sp.Symbol(k, positive=True) ** e for k, e in exps.items()])


def try_variable_root(text):
    """A root of a product or quotient of numbers and powers of unknowns: 7th root of (x^14 y^21 z^35 / (y^14 z^7)), 4th root of 81x^4y^8."""
    exprs = expression_texts(text)
    if not exprs or len(exprs) != 1:
        return None
    try:
        tree = A.strip(A.parse(exprs[0]))
        if tree[0] == "call" and tree[1] == "root":
            inner, index = A.strip(tree[2][0]), A.to_sympy(tree[2][1])
        elif tree[0] == "call" and tree[1] in ("sqrt", "cbrt"):
            inner, index = A.strip(tree[2][0]), sp.Integer(2 if tree[1] == "sqrt" else 3)
        elif tree[0] == "bin" and tree[1] == "^" and A.to_sympy(tree[3]).is_Rational and A.to_sympy(tree[3]).p == 1:
            inner, index = A.strip(tree[2]), sp.Integer(A.to_sympy(tree[3]).q)      # (inner)^(1/n) typed instead of a root sign
        else:
            return None
        if not index.is_Integer or index < 2 or not A.symbols(inner):
            return None                          # no unknown inside: this is not a question for this solver
        first = None
        if inner[0] == "bin" and inner[1] == "/":
            ne, nc, nv = _var_exponents(inner[2])
            de, dc, dv = _var_exponents(inner[3])
            names = sorted(set(ne) | set(de))
            mono = {k: ne.get(k, 0) - de.get(k, 0) for k in names}
            coef = nc / dc
            parts_tex = []
            for k in names:
                if k in ne and k in de:
                    parts_tex.append(rf"{k}^{{{ne[k]}-{de[k]}}}")
                elif k in ne:
                    parts_tex.append(rf"{k}^{{{ne[k]}}}")
                else:
                    parts_tex.append(rf"{k}^{{-{de[k]}}}")
            lead = "" if coef == 1 else rf"{tex(nc)}\div {tex(dc)}\," if dc != 1 else ""
            first = S(rf"{A.tex(inner, 0, True)} = {lead}{' '.join(parts_tex)} = {_monomial_tex(mono, coef)}",
                      "Inside the root, divide numbers and divide powers of the same base by subtracting the exponents: $\frac{a^m}{a^n} = a^{m-n}$.",
                      "جذر کے اندر اعداد کو تقسیم کریں اور ایک ہی اساس کی طاقتوں کی تقسیم میں قوتیں منفی کریں: $\frac{a^m}{a^n} = a^{m-n}$۔",
                      f"{py(A.to_sympy(inner))} == {py(_monomial_expr(mono, coef))}")
        else:
            mono, coef, _ = _var_exponents(inner)
        final = {k: e / index for k, e in mono.items()}
        final_coef = coef ** sp.Rational(1, int(index))
        if not (final_coef.is_Rational or final_coef.is_Pow):
            return None
        inside = _monomial_tex(mono, coef)
        root_tex = rf"\sqrt[{index}]{{{inside}}}" if index != 2 else rf"\sqrt{{{inside}}}"
        second = S(rf"{root_tex} = \left({inside}\right)^{{\frac{{1}}{{{index}}}}} = {_monomial_tex(final, final_coef)}",
                   f"Write the root as the power $\frac{{1}}{{{index}}}$ and apply it to the number and to every exponent.",
                   f"جذر کو طاقت $\frac{{1}}{{{index}}}$ کی شکل میں لکھیں اور اسے عدد اور ہر قوت پر لاگو کریں۔",
                   f"({py(_monomial_expr(mono, coef))})**Rational(1,{index}) == {py(_monomial_expr(final, final_coef))}")
    except (ValueError, TypeError, ZeroDivisionError, _Unsupported):
        return None
    steps = ([first] if first else []) + [second]
    part = P("", steps, f"${_monomial_tex(final, final_coef)}$", prompt=f"${A.tex(tree, 0, True)}$")
    return _finish(f"Simplify {part['prompt']}.", [part])


# =========================================================================================================
# (u + w)(u^2 - u w + w^2) = u^3 + w^3
# =========================================================================================================

def try_cube_identity(text):
    exprs = expression_texts(text)
    if not exprs or len(exprs) != 1:
        return None
    try:
        tree = A.strip(A.parse(exprs[0]))
        fs = A.factors(tree)
        if len(fs) != 2 or any(sg != 1 for _, sg in fs) or any(A.strip(f)[0] == "num" for f, _ in fs):
            return None
        for first, second in ((fs[0][0], fs[1][0]), (fs[1][0], fs[0][0])):
            ts = A.terms(first)
            if len(ts) != 2:
                continue
            u = A.to_sympy(ts[0][0]) * ts[0][1]
            w = A.to_sympy(ts[1][0]) * ts[1][1]
            other = A.to_sympy(second)
            if sp.simplify(sp.expand(other - (u ** 2 - u * w + w ** 2))) != 0:
                continue
            result = sp.expand(u ** 3 + w ** 3)
            prod_tex = A.tex(tree, 0, True)
            steps = [
                S(rf"u = {tex(u)}, \quad w = {tex(w)}", "Call the two terms of the first bracket u and w.", "پہلے قوسین کے دونوں اجزا کو u اور w کہیں۔"),
                S(rf"u^2 - uw + w^2 = {tex(sp.expand(u ** 2))} - \left({tex(sp.expand(u * w))}\right) + {tex(sp.expand(w ** 2))}",
                  "The second bracket is exactly $u^2 - uw + w^2$.", "دوسرا قوسین بالکل $u^2 - uw + w^2$ ہے۔",
                  f"{py(other)} == {py(u ** 2 - u * w + w ** 2)}"),
                S(rf"{prod_tex} = (u+w)(u^2-uw+w^2) = u^3+w^3 = {tex(result)}",
                  "Use the identity $(u+w)(u^2-uw+w^2) = u^3+w^3$.", "کلیہ $(u+w)(u^2-uw+w^2) = u^3+w^3$ استعمال کریں۔",
                  f"({py(u + w)})*({py(other)}) == {py(result)}"),
            ]
            part = P("", steps, f"${tex(result)}$", prompt=f"${prod_tex}$")
            return _finish(f"Simplify {part['prompt']}.", [part])
    except (ValueError, TypeError):
        return None
    return None
