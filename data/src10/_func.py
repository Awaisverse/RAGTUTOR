"""Templates for Unit 4 (functions and graphs): operations on functions, composition, inverses, absolute-value equations,
inequalities and graphs. Built on _gen."""
import re

import sympy as sp

from _gen import X, Graph, P, S, T, ex, ps, tex

Y = sp.Symbol("y")


def fx(s):
    return sp.sympify(s, locals={"x": X, "y": Y, "sqrt": sp.sqrt, "Abs": sp.Abs, "R": sp.Rational})


def lt(e):
    return sp.latex(e)


def combine(label, fname, f, gname, g, op, prompt, simplify_to=None):
    """f(x) op g(x) with the working."""
    F, G = fx(f), fx(g)
    sym = {"+": "+", "-": "-", "*": r"\cdot", "/": "/"}[op]
    val = {"+": F + G, "-": F - G, "*": F * G, "/": F / G}[op]
    res = sp.simplify(sp.factor(val)) if op == "/" else sp.expand(val)
    if simplify_to is not None:
        res = fx(simplify_to)
    shown = (rf"\frac{{{lt(F)}}}{{{lt(G)}}}" if op == "/" else
             rf"({lt(F)}) {sym} ({lt(G)})")
    lhs = rf"\frac{{{fname}(x)}}{{{gname}(x)}}" if op == "/" else rf"{fname}(x) {sym} {gname}(x)"
    steps = [S(rf"{lhs} = {shown}", "Put in the two functions.", "دونوں تفاعل رکھیں۔"),
             S(rf"= {lt(res)}", {"+": "Add like terms.", "-": "Remove the brackets (change the signs of the second) and collect like terms.",
                                  "*": "Multiply out and collect like terms.", "/": "Factorize and cancel the common factor."}[op],
               {"+": "متشابہ ارکان جمع کریں۔", "-": "قوسین ہٹائیں (دوسری کی علامتیں بدلیں) اور متشابہ ارکان اکٹھے کریں۔",
                "*": "ضرب دے کر متشابہ ارکان اکٹھے کریں۔", "/": "تجزی کر کے مشترک جزو کاٹ دیں۔"}[op],
               f"{ps(val)} == {ps(res)}")]
    return P(label, steps, f"${lt(res)}$", prompt=prompt)


def shortest(e):
    """The simplest-looking equivalent form: expanded, combined over one denominator, factored or as written."""
    cands = [sp.expand(e), sp.together(sp.expand(e)), sp.cancel(e), sp.factor(e), e, sp.simplify(e)]
    return min(cands, key=lambda c: (len(sp.latex(c)), sp.count_ops(c)))


def compose(label, outer_name, outer, inner_name, inner, prompt=None):
    """(outer o inner)(x) = outer(inner(x))."""
    O, I_ = fx(outer), fx(inner)
    sub = O.subs(X, sp.Symbol("u")).subs(sp.Symbol("u"), I_)
    res = shortest(sub)
    steps = [S(rf"({outer_name}\circ {inner_name})(x) = {outer_name}({inner_name}(x)) = {outer_name}\left({lt(I_)}\right)",
               f"Put ${inner_name}(x)$ in place of $x$ in ${outer_name}$.", f"${outer_name}$ میں $x$ کی جگہ ${inner_name}(x)$ رکھیں۔"),
             S(rf"= {lt(sp.UnevaluatedExpr(sub)) if False else lt(sub)}", f"Substitute into ${outer_name}(x) = {lt(O)}$.",
               f"${outer_name}(x) = {lt(O)}$ میں رکھیں۔", f"({sp.sstr(O)}).subs(x, {ps(I_)}) == {ps(sub)}"),
             S(rf"= {lt(res)}", "Simplify.", "سادہ کریں۔", f"{ps(sub)} == {ps(res)}")]
    if sp.srepr(sub) == sp.srepr(res):
        steps = steps[:2]
    return P(label, steps, f"${lt(res)}$", prompt=prompt or rf"$({outer_name}\circ {inner_name})(x)$"), res


def inverse(label, f, lines, result, prompt, domain_note=None):
    """lines: LaTeX lines of the rearrangement (y = f(x) solved for x). Checked: f(f^-1(x)) = x."""
    F, Fi = fx(f), fx(result)
    Fi = Fi.replace(lambda a: isinstance(a, sp.Pow) and not a.exp.is_Integer, lambda a: sp.Pow(sp.together(a.base), a.exp, evaluate=False))
    Fi = Fi if any(isinstance(a, sp.Pow) and not a.exp.is_Integer for a in sp.preorder_traversal(Fi)) else sp.together(Fi)
    steps = [S(rf"y = {lt(F)}", "Write $y = f(x)$.", "$y = f(x)$ لکھیں۔")]
    for t in lines:
        steps.append(S(t, "Make $x$ the subject.", "$x$ کو موضوع بنائیں۔"))
    steps.append(S(rf"f^{{-1}}(x) = {lt(Fi)}" + (rf",\quad {domain_note}" if domain_note else ""),
                   "Replace $y$ by $x$ to write the inverse function.", "معکوس تفاعل لکھنے کے لیے $y$ کی جگہ $x$ لکھیں۔",
                   f"simplify(({sp.sstr(F)}).subs(x, {ps(Fi)})) == x" if "sqrt" not in f else f"simplify(({sp.sstr(Fi)}).subs(x, {ps(F)})) == x"))
    return P(label, steps, f"$f^{{-1}}(x) = {lt(Fi)}$" + (f", ${domain_note}$" if domain_note else ""), prompt=prompt)


def abs_equation(label, inner, rhs, prompt):
    """|inner| = rhs (rhs > 0): inner = rhs or inner = -rhs, on a number line."""
    E = fx(inner)
    s1 = sp.solve(sp.Eq(E, rhs), X)[0]
    s2 = sp.solve(sp.Eq(E, -rhs), X)[0]
    roots = sorted([s1, s2])
    lo, hi = float(min(roots)) - 2, float(max(roots)) + 2
    steps = [S(rf"{lt(E)} = {rhs} \quad\text{{or}}\quad {lt(E)} = -{rhs}", "$|A| = k$ means $A = k$ or $A = -k$.", "$|A| = k$ کا مطلب $A = k$ یا $A = -k$۔"),
             S(rf"x = {lt(s1)} \quad\text{{or}}\quad x = {lt(s2)}", "Solve each equation.", "ہر مساوات حل کریں۔",
               f"Abs({_xr(sp.sstr(E))}).subs(xr, {ps(s1)}) == {rhs}", f"Abs({_xr(sp.sstr(E))}).subs(xr, {ps(s2)}) == {rhs}"),
             S(r"\text{S.S} = \{" + ", ".join(lt(r) for r in roots) + r"\}", "Mark both solutions on the number line.", "دونوں حل عددی خط پر لگائیں۔",
               draw=[{"t": "numberline", "from": float(sp.floor(lo)), "to": float(sp.ceiling(hi)), "y": 30,
                      "marks": [{"v": float(r), "s": _plain(r)} for r in roots]}])]
    return P(label, steps, "$x = " + r",\ x = ".join(lt(r) for r in roots) + "$", prompt=prompt)


def _plain(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):.2f}")


def _xr(expr_str):
    """The same expression with x renamed xr: the verifier makes single letters positive, which would turn |x + 3| into x + 3."""
    return re.sub(r"(?<![A-Za-z_])x(?![A-Za-z_])", "xr", expr_str)


def interval_tex(sol):
    """A sympy set as student notation."""
    if sol == sp.S.EmptySet:
        return r"\varnothing"
    if isinstance(sol, sp.FiniteSet):
        return r"\{" + ", ".join(lt(v) for v in sorted(sol)) + r"\}"
    if isinstance(sol, sp.Union):
        return r" \cup ".join(interval_tex(a) for a in sol.args)
    if isinstance(sol, sp.Interval):
        lb = "(" if sol.left_open or sol.left == -sp.oo else "["
        rb = ")" if sol.right_open or sol.right == sp.oo else "]"
        return f"{lb}{lt(sol.left)}, {lt(sol.right)}{rb}"
    if isinstance(sol, sp.Complement):
        return interval_tex(sp.Union(sp.Interval.open(-sp.oo, list(sol.args[1])[0]), sp.Interval.open(list(sol.args[1])[0], sp.oo)))
    return lt(sol)


def abs_inequality(label, lhs, op, rhs, steps_tex, prompt):
    """Any inequality with absolute values; the working lines are given (LaTeX), the solution set is computed and checked by
    testing a point inside every piece and every edge."""
    L, Rr = fx(lhs), fx(rhs)
    rel = {"<": sp.Lt, "<=": sp.Le, ">": sp.Gt, ">=": sp.Ge}[op](L, Rr)
    sol = sp.solveset(rel, X, sp.S.Reals)
    steps = [S(t, en, ur) for t, en, ur in steps_tex]
    checks = []
    pieces = sol.args if isinstance(sol, sp.Union) else [sol]
    for pc in pieces:
        if isinstance(pc, sp.Interval):
            a, b = pc.left, pc.right
            t = (a + b) / 2 if a != -sp.oo and b != sp.oo else (b - 1 if a == -sp.oo and b != sp.oo else (a + 1 if b == sp.oo and a != -sp.oo else 0))
            checks.append(f"({_xr(sp.sstr(L - Rr))}).subs(xr, {ps(t)}) {op} 0")
        elif isinstance(pc, sp.FiniteSet):
            for v in pc:
                checks.append(f"({_xr(sp.sstr(L - Rr))}).subs(xr, {ps(v)}) {op} 0")
    pts = [float(v) for pc in pieces for v in ([pc.left, pc.right] if isinstance(pc, sp.Interval) else list(pc) if isinstance(pc, sp.FiniteSet) else [])
           if v not in (sp.oo, -sp.oo)]
    lo, hi = (min(pts) - 2, max(pts) + 2) if pts else (-3, 3)
    marks = [{"v": v, "s": _plain(v)} for v in sorted(set(pts))]
    ans = interval_tex(sol) if not (isinstance(sol, sp.Complement) or (isinstance(sol, sp.Union) and len(pieces) == 2 and pieces[0].right == pieces[1].left)) else interval_tex(sol)
    steps.append(S(rf"x \in {ans}", "Write the solution set and show it on the number line (each part is checked with a test value).",
                   "حل سیٹ لکھیں اور عددی خط پر دکھائیں (ہر حصہ ایک جانچ قیمت سے پرکھا گیا ہے)۔", *checks,
                   draw=[{"t": "numberline", "from": float(sp.floor(lo)), "to": float(sp.ceiling(hi)), "y": 30, "marks": marks}]))
    return P(label, steps, f"$x \\in {ans}$", prompt=prompt), sol


def abs_graph(label, f, prompt):
    """y = a|x - h| + k: vertex, table of values, V-shaped graph."""
    F = fx(f)
    h = sp.solve(F.args[0] if False else [a for a in sp.preorder_traversal(F) if isinstance(a, sp.Abs)][0].args[0], X)[0]
    k = F.subs(X, h)
    xs = [h + d for d in (-3, -2, -1, 0, 1, 2, 3)]
    ys = [F.subs(X, v) for v in xs]
    xr = (float(min(xs)) - 1, float(max(xs)) + 1)
    yr = (min(float(min(ys)), 0) - 2, float(max(ys)) + 2)
    g = Graph(xr, yr)
    row1 = " & ".join(lt(v) for v in xs)
    row2 = " & ".join(lt(v) for v in ys)
    steps = [S(rf"\text{{Vertex: }} x = {lt(h)},\ f({lt(h)}) = {lt(k)}", "The corner of the V is where the expression inside $|\\;|$ is 0.",
               "V کا کونا وہاں ہے جہاں $|\\;|$ کے اندر کی قیمت 0 ہو۔", f"({_xr(sp.sstr(F))}).subs(xr, {ps(h)}) == {ps(k)}", draw=g.axes()),
             S(rf"\begin{{array}}{{c|{'c' * len(xs)}}} x & {row1} \\ \hline f(x) & {row2} \end{{array}}", "Make a table of values on both sides of the vertex.",
               "کونے کی دونوں جانب قیمتوں کا جدول بنائیں۔", *[f"({_xr(sp.sstr(F))}).subs(xr, {ps(a)}) == {ps(b)}" for a, b in zip(xs, ys)],
               draw=sum((g.point(float(a), float(b)) for a, b in zip(xs, ys)), [])),
             S(r"\text{Join the points: a V-shaped graph}", "Join the points with two straight lines meeting at the vertex.",
               "نقاط کو دو خطوط مستقیم سے ملائیں جو کونے پر ملتے ہیں۔", draw=g.curve(sp.sstr(F)) + g.point(float(h), float(k), f"({_plain(h)}, {_plain(k)})"))]
    return P(label, steps, f"V-shaped graph with vertex $({lt(h)}, {lt(k)})$", prompt=prompt)
