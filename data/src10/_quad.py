"""Templates for Unit 2 (quadratic equations and inequalities). Built on _gen."""
import sympy as sp

from _gen import (X, Graph, P, R, S, T, answer_roots, coeffs, eq_chain, eq_tex, ex, factor_steps, formula_steps, order_roots, ps,
                  pt_label, roots_line, sset, standard_form, table_step, tex, tex_root)

Y = sp.Symbol("y")


def p_standard(label, eq, var=X):
    steps, poly = standard_form(eq, var)
    return P(label, steps, f"${sp.latex(poly)} = 0$", prompt=f"${eq_tex(eq)}$"), poly


def _graph_ranges(polys_or_exprs, roots, extra_x=()):
    xs = [float(r) for r in roots] + [float(v) for v in extra_x]
    lo, hi = min(xs + [0]) - 2, max(xs + [0]) + 2
    lo, hi = float(sp.floor(lo)), float(sp.ceiling(hi))
    ys = []
    for e in polys_or_exprs:
        f = sp.lambdify(X, ex(e))
        ys += [float(f(lo + (hi - lo) * j / 40)) for j in range(41)]
    ylo, yhi = min(ys + [0]), max(ys + [0])
    pad = (yhi - ylo) * 0.08 + 1
    return (lo, hi), (float(sp.floor(ylo - pad)), float(sp.ceiling(yhi + pad)))


def q_graph(label, poly_str, prompt=None):
    """Solve a x^2 + b x + c = 0 graphically: table, curve, the points where it cuts the x-axis."""
    poly = ex(poly_str)
    if (sp.discriminant(poly, X)) >= 0 and sp.sqrt(sp.discriminant(poly, X)).is_Rational:
        alg, roots = factor_steps(poly)
    else:
        alg, roots = formula_steps(poly)
    xr, yr = _graph_ranges([poly], roots)
    g = Graph(xr, yr)
    vx = -coeffs(poly)[1] / (2 * coeffs(poly)[0])
    xs = sorted({int(sp.floor(vx)) + d for d in range(-3, 4)})
    tab, ys = table_step(sp.sstr(poly), xs)
    steps = [S(rf"y = {sp.latex(poly)}", "Draw the graph of $y$ = the left side; the roots are where the graph cuts the $x$-axis ($y = 0$).",
               "بائیں جانب کے برابر $y$ کا گراف بنائیں؛ جذر وہاں ہیں جہاں گراف $x$-محور کو کاٹتا ہے ($y = 0$)۔", draw=g.axes()),
             {**tab, "draw": sum((g.point(x, y) for x, y in zip(xs, ys) if yr[0] <= y <= yr[1]), [])},
             S(r"\text{Join the points with a smooth curve (a parabola).}", "Join the points with a smooth curve.",
               "نقاط کو ایک ہموار خم سے ملا دیں۔", draw=g.curve(sp.sstr(poly)))]
    steps += [s for s in alg[1:]]
    steps.append(S(r"\text{The graph cuts the } x\text{-axis at } " + ", ".join(f"x = {tex_root(r)}" for r in roots),
                   "Read the roots where the curve meets the $x$-axis; they agree with the algebra.",
                   "جہاں خم $x$-محور سے ملتا ہے وہاں سے جذر پڑھیں؛ یہ الجبرا سے مطابقت رکھتے ہیں۔",
                   *[f"({sp.sstr(poly)}).subs(x, {ps(r)}) == 0" for r in roots],
                   draw=sum((g.point(float(r), 0, f"({tex_plain(r)}, 0)") for r in roots), [])))
    return P(label, steps, answer_roots("x", roots), prompt=prompt or f"${sp.latex(poly)} = 0$")


def tex_plain(v):
    v = sp.nsimplify(v)
    return str(v) if v.is_Integer else (f"{v.p}/{v.q}" if v.is_Rational else f"{float(v):.2f}")


def p_intercepts(label, lhs, rhs, prompt=None):
    """Points where the line lhs = rhs (in x, y) meets the axes, with its graph."""
    L, Rr = ex(lhs), ex(rhs)
    xs = sp.solve((L - Rr).subs(Y, 0), X)[0]
    ys = sp.solve((L - Rr).subs(X, 0), Y)[0]
    span = max(abs(float(xs)), abs(float(ys)), 1)
    m = float(sp.ceiling(span * 1.4)) if span >= 1 else round(span * 1.6, 1)
    g = Graph((-m, m), (-m, m))
    yexpr = sp.solve(L - Rr, Y)[0]
    steps = [S(rf"y = 0:\ {tex(str(L.subs(Y, 0)))} = {tex(str(Rr.subs(Y, 0)))} \Rightarrow x = {sp.latex(xs)}",
               "On the $x$-axis $y = 0$: put $y = 0$ and solve for $x$.", "$x$-محور پر $y = 0$: $y = 0$ رکھ کر $x$ معلوم کریں۔",
               f"(({lhs}) - ({rhs})).subs({{y: 0, x: {ps(xs)}}}) == 0", draw=g.axes() + g.point(float(xs), 0, f"({tex_plain(xs)}, 0)")),
             S(rf"x = 0:\ {tex(str(L.subs(X, 0)))} = {tex(str(Rr.subs(X, 0)))} \Rightarrow y = {sp.latex(ys)}",
               "On the $y$-axis $x = 0$: put $x = 0$ and solve for $y$.", "$y$-محور پر $x = 0$: $x = 0$ رکھ کر $y$ معلوم کریں۔",
               f"(({lhs}) - ({rhs})).subs({{x: 0, y: {ps(ys)}}}) == 0", draw=g.point(0, float(ys), f"(0, {tex_plain(ys)})")),
             S(rf"\text{{Points: }} ({sp.latex(xs)}, 0) \text{{ and }} (0, {sp.latex(ys)})",
               "Draw the straight line through these two points.", "ان دو نقاط سے گزرتا ہوا خط مستقیم کھینچیں۔", draw=g.curve(sp.sstr(yexpr)))]
    return P(label, steps, f"$({sp.latex(xs)}, 0)$ and $(0, {sp.latex(ys)})$", prompt=prompt or f"${tex(lhs)} = {tex(rhs)}$")


def p_system(label, eq1, eq2, alg_steps, prompt):
    """Two linear equations: the algebra (given as checked steps) and both lines on one graph."""
    (l1, r1), (l2, r2) = [tuple(s.strip() for s in e.split("=")) for e in (eq1, eq2)]
    sol = sp.solve([ex(l1) - ex(r1), ex(l2) - ex(r2)], [X, Y], dict=True)[0]
    x0, y0 = sol[X], sol[Y]
    m = max(abs(float(x0)), abs(float(y0)), 4) + 4
    m = float(sp.ceiling(m))
    g = Graph((-m, m), (-m, m))
    f1 = sp.solve(ex(l1) - ex(r1), Y)[0]
    f2 = sp.solve(ex(l2) - ex(r2), Y)[0]
    steps = [S(rf"{tex(l1)} = {tex(r1)} \Rightarrow y = {sp.latex(f1)}", "Write the first equation as $y = \\ldots$ and draw its line.",
               "پہلی مساوات کو $y = \\ldots$ کی صورت میں لکھ کر اس کا خط کھینچیں۔", draw=g.axes() + g.curve(sp.sstr(f1))),
             S(rf"{tex(l2)} = {tex(r2)} \Rightarrow y = {sp.latex(f2)}", "Do the same for the second equation.",
               "دوسری مساوات کے لیے بھی یہی کریں۔", draw=g.curve(sp.sstr(f2)))]
    steps += alg_steps
    steps.append(S(rf"\text{{The lines meet at }} ({sp.latex(x0)}, {sp.latex(y0)})", "The point where the two lines cross is the solution.",
                   "جہاں دونوں خطوط ایک دوسرے کو کاٹتے ہیں وہ نقطہ حل ہے۔",
                   f"(({l1}) - ({r1})).subs({{x: {ps(x0)}, y: {ps(y0)}}}) == 0", f"(({l2}) - ({r2})).subs({{x: {ps(x0)}, y: {ps(y0)}}}) == 0",
                   draw=g.point(float(x0), float(y0), pt_label(x0, y0))))
    return P(label, steps, f"$x = {sp.latex(x0)},\\ y = {sp.latex(y0)}$", prompt=prompt)


def roots_to_eq(label, a, b, prompt=None):
    """x^2 - (a+b)x + ab = 0 for the roots a, b, cleared of fractions."""
    a, b = sp.nsimplify(a), sp.nsimplify(b)
    s_, p_ = sp.radsimp(a + b), sp.radsimp(sp.expand(a * b))
    poly = sp.expand(X ** 2 - s_ * X + p_)
    den = sp.ilcm(*[sp.fraction(c)[1] for c in sp.Poly(poly, X).all_coeffs()])
    final = sp.expand(poly * den)
    steps = [S(r"x^2 - (\alpha + \beta)x + \alpha\beta = 0", "A quadratic with roots $\\alpha$ and $\\beta$ is $x^2 - (\\text{sum})x + \\text{product} = 0$.",
               "جذر $\\alpha$ اور $\\beta$ والی دو درجی مساوات $x^2 - (\\text{مجموعہ})x + \\text{حاصل ضرب} = 0$ ہے۔"),
             S(rf"\alpha + \beta = {tex_root(a)} + ({tex_root(b)}) = {sp.latex(s_)}", "Add the roots.", "جذروں کو جمع کریں۔",
               f"{ps(a)} + {ps(b)} == {ps(s_)}"),
             S(rf"\alpha\beta = ({tex_root(a)})({tex_root(b)}) = {sp.latex(p_)}", "Multiply the roots.", "جذروں کو ضرب دیں۔",
               f"{ps(a)} * {ps(b)} == {ps(p_)}"),
             S(rf"x^2 - ({sp.latex(s_)})x + ({sp.latex(p_)}) = 0 \Rightarrow {sp.latex(poly)} = 0", "Substitute the sum and the product.",
               "مجموعہ اور حاصل ضرب کی قیمتیں رکھیں۔", f"expand((x - {ps(a)})*(x - {ps(b)})) == {ps(poly)}")]
    if den != 1:
        steps.append(S(rf"{sp.latex(final)} = 0", f"Multiply both sides by {den} to clear the fractions.",
                       f"کسور ختم کرنے کے لیے دونوں اطراف کو {den} سے ضرب دیں۔", f"{den}*{ps(poly)} == {ps(final)}"))
    steps.append(S(rf"\text{{Check: }} x = {tex_root(a)} \text{{ and }} x = {tex_root(b)} \text{{ satisfy it}}",
                   "Both given numbers make the equation true.", "دونوں دیے گئے اعداد مساوات کو درست کرتے ہیں۔",
                   f"({sp.sstr(final)}).subs(x, {ps(a)}) == 0", f"({sp.sstr(final)}).subs(x, {ps(b)}) == 0"))
    return P(label, steps, f"${sp.latex(final)} = 0$", prompt=prompt or f"${tex_root(a)},\\ {tex_root(b)}$")


NATURE = {
    "rational": ("rational and unequal", "ناطق اور غیر مساوی"),
    "irrational": ("irrational and unequal", "غیر ناطق اور غیر مساوی"),
    "equal": ("real and equal", "حقیقی اور مساوی"),
    "imaginary": ("imaginary", "خیالی"),
}


def nature(label, poly_str, prompt=None):
    poly = ex(poly_str)
    a, b, c = coeffs(poly)
    D = b * b - 4 * a * c
    if D > 0:
        kind = "rational" if sp.sqrt(D).is_Rational else "irrational"
    elif D == 0:
        kind = "equal"
    else:
        kind = "imaginary"
    en_word, ur_word = NATURE[kind]
    why = {"rational": f"$D > 0$ and $D = {D}$ is a perfect square ($= {sp.sqrt(D)}^2$)",
           "irrational": f"$D > 0$ and $D = {D}$ is not a perfect square",
           "equal": "$D = 0$", "imaginary": "$D < 0$"}[kind]
    why_ur = {"rational": f"$D > 0$ اور $D = {D}$ مکمل مربع ہے", "irrational": f"$D > 0$ اور $D = {D}$ مکمل مربع نہیں",
              "equal": "$D = 0$", "imaginary": "$D < 0$"}[kind]
    checks = [f"({b})**2 - 4*({a})*({c}) == {D}"]
    if kind == "rational":
        checks.append(f"sqrt({D}) == {sp.sqrt(D)}")
    steps = [S(rf"a = {a},\quad b = {b},\quad c = {c}", "Compare with $ax^2 + bx + c = 0$.", "$ax^2 + bx + c = 0$ سے موازنہ کریں۔"),
             S(rf"D = b^2 - 4ac = ({b})^2 - 4({a})({c}) = {b * b} {'-' if 4 * a * c >= 0 else '+'} {abs(4 * a * c)} = {D}",
               "Work out the discriminant $D = b^2 - 4ac$.", "ممیز $D = b^2 - 4ac$ معلوم کریں۔", *checks),
             S(rf"\text{{Roots are {en_word}}}", f"Since {why}, the roots are {en_word}.", f"چونکہ {why_ur}، اس لیے جذر {ur_word} ہیں۔")]
    return P(label, steps, f"$D = {D}$: roots are {en_word}", prompt=prompt or f"${sp.latex(poly)} = 0$")


def inequality(label, poly_str, op, prompt=None):
    """Solve a quadratic inequality poly op 0 by critical points and test points."""
    poly = ex(poly_str)
    flip = {"<": ">", ">": "<", "<=": ">=", ">=": "<="}
    texop = {"<": "<", ">": ">", "<=": r"\le", ">=": r"\ge"}
    steps = [S(rf"{sp.latex(poly)} {texop[op]} 0", "Write the inequality.", "عدم مساوات لکھیں۔")]
    work, wop = poly, op
    if sp.Poly(poly, X).LC() < 0:
        work, wop = sp.expand(-poly), flip[op]
        steps.append(S(rf"{sp.latex(work)} {texop[wop]} 0", "Multiply by $-1$: the inequality sign turns round.",
                       "$-1$ سے ضرب دیں: عدم مساوات کی علامت الٹ جاتی ہے۔", f"-({sp.sstr(poly)}) == {ps(work)}"))
    a, b, c = coeffs(work)
    D = b * b - 4 * a * c
    steps.append(T("Solve the associated equation (put = in place of the inequality sign).",
                   "متعلقہ مساوات حل کریں (عدم مساوات کی علامت کی جگہ = رکھیں)۔"))
    if D >= 0 and sp.sqrt(D).is_Rational:
        alg, roots = factor_steps(work)
    else:
        alg, roots = formula_steps(work)
    steps += alg
    roots = sorted(set(roots), key=float)
    inclusive = op in ("<=", ">=")
    lo_hi = [float(r) for r in roots]
    span = (lo_hi[-1] - lo_hi[0]) if len(lo_hi) > 1 else 2
    nl_from = float(sp.floor(lo_hi[0] - max(2, span * 0.5))) if roots else -3
    nl_to = float(sp.ceiling(lo_hi[-1] + max(2, span * 0.5))) if roots else 3
    marks = [{"v": float(r), "s": tex_plain(r)} for r in roots]
    steps.append(S(r"\text{Critical points: } " + ", ".join(tex_root(r) for r in roots),
                   "The roots split the number line into intervals.", "جذر عددی خط کو وقفوں میں تقسیم کرتے ہیں۔",
                   draw=[{"t": "numberline", "from": nl_from, "to": nl_to, "y": 30, "marks": marks}]))
    # test one point in each interval
    tests = []
    edges = [-sp.oo] + roots + [sp.oo]
    holds = []
    for k in range(len(edges) - 1):
        lo, hi = edges[k], edges[k + 1]
        if lo == -sp.oo:
            t = sp.floor(roots[0]) - 1
        elif hi == sp.oo:
            t = sp.ceiling(roots[-1]) + 1
        else:
            t = (lo + hi) / 2
            if (sp.floor(t) > lo) and (sp.floor(t) < hi):
                t = sp.floor(t)
        val = work.subs(X, t)
        ok = bool({"<": val < 0, ">": val > 0, "<=": val <= 0, ">=": val >= 0}[wop])
        holds.append(ok)
        tests.append(S(rf"x = {sp.latex(t)}:\ {sp.latex(work).replace('x', '(' + sp.latex(t) + ')')} = {sp.latex(val)} \Rightarrow "
                       + (r"\text{satisfied}" if ok else r"\text{not satisfied}"),
                       "Test a point from this interval in the inequality.", "اس وقفے کا ایک نقطہ عدم مساوات میں رکھ کر جانچیں۔",
                       f"({sp.sstr(work)}).subs(x, {ps(t)}) == {ps(val)}"))
    steps += tests
    pieces = []
    for k, ok in enumerate(holds):
        if not ok:
            continue
        lo, hi = edges[k], edges[k + 1]
        lb = "(" if (lo == -sp.oo or not inclusive) else "["
        rb = ")" if (hi == sp.oo or not inclusive) else "]"
        pieces.append(f"{lb}{'-\\infty' if lo == -sp.oo else tex_root(lo)}, {'\\infty' if hi == sp.oo else tex_root(hi)}{rb}")
    if not pieces and inclusive and roots:
        ans = r"x = " + ", ".join(tex_root(r) for r in roots)
        text = f"${ans}$"
    elif not pieces:
        ans = r"\text{no solution}"
        text = "no solution"
    else:
        # merge touching closed pieces like [a, b] when only the middle interval holds
        ans = r"x \in " + r" \cup ".join(pieces)
        text = f"${ans}$"
    if inclusive and pieces and not holds[0] and not holds[-1]:
        pass
    steps.append(S(ans, "Collect the intervals where the inequality holds" + (" (the critical points are included because of $=$)." if inclusive else "."),
                   "وہ وقفے لکھیں جہاں عدم مساوات درست ہے" + (" (= کی وجہ سے نازک نقاط شامل ہیں)۔" if inclusive else "۔")))
    if not pieces and not inclusive and len(roots) == 1:
        steps[-1] = S(ans, "A square is never negative, so no $x$ satisfies the inequality.", "مربع کبھی منفی نہیں ہوتا، اس لیے کوئی $x$ عدم مساوات کو پورا نہیں کرتا۔",
                      f"({sp.sstr(work)}) == {ps(sp.factor(work))}")
    return P(label, steps, text, prompt=prompt or f"${sp.latex(poly)} {texop[op]} 0$")
