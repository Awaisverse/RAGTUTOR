"""Hard questions: Gemini breaks the question into small chunks, the engine works each chunk out with checked steps.

Gemini only PLANS. It never computes a value: every chunk is an expression in the question's own numbers and the names of
earlier chunks, e.g.
    A = (1+i)/(1-i),  B = A^15,  C = (1-i)/(1+i),  D = C^10,  answer = B + D
The engine (solvers10.eval_steps and the templates) evaluates each chunk exactly, one checked operation at a time.

The plan is trusted only when it is the SAME question:
  * its numbers are exactly the numbers of the question (nothing invented, nothing dropped), and
  * when the question itself is an expression the engine can evaluate directly, the chunked answer equals that value.
Otherwise the plan is refused. Class 10 (complex numbers) only, for now.

  VERTEX_MODEL   the model that plans (the high-end model; planning is where its reasoning helps)
"""
import json
import re

import sympy as sp

import question_reader
import solvers10
import _complex as cx

PROMPT = """You plan the solution of a Class {klass} mathematics question (complex numbers, Punjab textbook). You NEVER compute
any value: a strict calculator will do every calculation from your plan.

Break the question into small chunks, in order. Each chunk is ONE simple expression that uses only numbers from the question,
the imaginary unit i, and the names of EARLIER chunks. Allowed: + - * / ^ (whole-number powers), brackets, and the functions
conj(X), abs(X), re(X), im(X).

Return ONLY one JSON object:
{{"chunks": [{{"name": "A", "what": "<a few words: what this chunk is>", "expr": "<expression>"}}, ...],
  "answer": "<the name of the chunk that is the final answer, or an expression in chunk names>",
  "asks": "<what the question asks for, in a few words>"}}

Rules:
- Use every number of the question exactly as written; never introduce a number that is not in the question.
- Keep chunks small: one idea per chunk (simplify a fraction, raise to a power, take a conjugate, add two results).
- Names are single capital letters A, B, C, ...
- If the question asks for several things, make one chunk per thing and give them as a list: "answer": ["E", "F"].

Question:
{question}"""


def _gemini(prompt):
    import os
    import vertex_models
    return vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=2048, temperature=0.0,
                                  model=os.environ.get("VERTEX_MODEL") or None)


def plan(question, klass="10", generate=None):
    """-> {"chunks": [...], "answer": str or list, "asks": str} or None."""
    raw = (generate or _gemini)(PROMPT.format(klass=klass, question=str(question)[:1500]))
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return None
    try:
        p = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    chunks = p.get("chunks")
    if not isinstance(chunks, list) or not chunks or len(chunks) > 12:
        return None
    names = []
    for c in chunks:
        if not isinstance(c, dict) or not re.fullmatch(r"[A-H]|[J-Z]", str(c.get("name", ""))) or not c.get("expr"):
            return None                              # 'I' is not a name: it is the imaginary unit
        names.append(c["name"])
    if len(set(names)) != len(names):
        return None
    return p


def _plan_numbers(p):
    text = " ".join(str(c["expr"]) for c in p["chunks"])
    return question_reader._numbers(re.sub(r"\b[A-HJ-Z]\b", " ", text))


def _subst(expr, values):
    """Put earlier chunks into an expression as exact bracketed values."""
    out = str(expr)
    for name, v in values.items():
        out = re.sub(rf"\b{name}\b", f"({sp.sstr(v)})", out)
    return out


def _py(expr, values):
    """Chunk expression -> engine text (None if it is not plain maths)."""
    return solvers10._to_py(_subst(expr, values))


def _function_chunk(fn, arg_py):
    steps, z = solvers10.eval_steps(arg_py)
    if fn == "conj":
        v = sp.conjugate(z)
        steps.append(cx.S(rf"\overline{{{cx.ctex(z)}}} = {cx.ctex(v)}", "The conjugate changes the sign of the imaginary part.",
                          "مزدوج میں خیالی حصے کی علامت بدل جاتی ہے۔", f"conjugate({cx.py(z)}) == {cx.py(v)}"))
    elif fn == "abs":
        part = cx.p_modulus("", z)
        steps += part["steps"]
        v = sp.sqrt(sp.re(z) ** 2 + sp.im(z) ** 2)
    elif fn in ("re", "im"):
        v = sp.re(z) if fn == "re" else sp.im(z)
        word = "real part" if fn == "re" else "imaginary part"
        steps.append(cx.S(rf"\operatorname{{{fn.capitalize()}}}({cx.ctex(z)}) = {cx.ctex(v)}", f"Read off the {word}.",
                          "حقیقی حصہ پڑھیں۔" if fn == "re" else "خیالی حصہ پڑھیں۔", f"{fn}({cx.py(z)}) == {cx.py(v)}"))
    else:
        raise ValueError(fn)
    return steps, sp.expand(v)


_FN = re.compile(r"\b(conj|abs|re|im)\s*\(")


def _eval_chunk(expr, values):
    """Evaluate one chunk: functions anywhere inside it (innermost first) are worked out with their own steps and put back
    as exact values, then the rest is evaluated. -> (steps, value). Raises ValueError when it cannot be read."""
    text, steps = _subst(expr, values), []
    for _ in range(12):
        m = None
        for cand in _FN.finditer(text):           # innermost call: its argument contains no further function call
            depth, k = 1, cand.end()
            while k < len(text) and depth:
                depth += text[k] == "("
                depth -= text[k] == ")"
                k += 1
            if depth == 0 and not _FN.search(text[cand.end():k - 1]):
                m = (cand.start(), cand.group(1), text[cand.end():k - 1], k)
                break
        if m is None:
            break
        start, fn, arg, end = m
        py = solvers10._to_py(arg)
        if py is None:
            raise ValueError("unreadable function argument")
        s, v = _function_chunk(fn, py)
        steps += s
        text = text[:start] + f"({sp.sstr(v)})" + text[end:]
    py = solvers10._to_py(text)
    if py is None:
        raise ValueError("unreadable chunk")
    s, v = solvers10.eval_steps(py)
    return steps + s, v


def _used_numbers(p):
    """Numbers in the chunks that the final answer actually depends on (a chunk computed but never used does not count)."""
    by_name = {c["name"]: c for c in p["chunks"]}
    targets = p["answer"] if isinstance(p["answer"], list) else [p["answer"]]
    todo, seen = [str(t) for t in targets], set()
    text = []
    while todo:
        expr = todo.pop()
        text.append(expr)
        for name in re.findall(r"\b([A-HJ-Z])\b", expr):
            if name in by_name and name not in seen:
                seen.add(name)
                todo.append(str(by_name[name]["expr"]))
    return set(question_reader._numbers(re.sub(r"\b[A-HJ-Z]\b", " ", " ".join(text))))


def execute(p, question):
    """Work the plan out with the engine. -> {"steps", "values", "answers", "plan"} or None when it is not the same question."""
    asked = set(question_reader._numbers(question))
    if _plan_numbers(p) and not set(_plan_numbers(p)) <= asked:
        return None                                   # the plan brought in a number that is not in the question
    if _used_numbers(p) != asked:
        return None                                   # the answer leaves part of the question out (or uses something else):
                                                      # it would answer a related question, not this one
    if set(question_reader._numbers(question)) - set(_plan_numbers(p)) - {"2", "1"}:
        pass                                          # a number may be used implicitly (e.g. a power written in words); the value check below decides
    values, steps = {}, []
    for c in p["chunks"]:
        try:
            s, v = _eval_chunk(c["expr"], values)
        except (ValueError, TypeError, ZeroDivisionError, sp.SympifyError):
            return None
        steps.append(cx.T(f"Chunk {c['name']}: {c.get('what', '')} — ${c['expr']}$".replace("^", "^"), f"حصہ {c['name']}: ${c['expr']}$"))
        steps += s
        steps.append(cx.S(rf"{c['name']} = {cx.ctex(v)}", f"So ${c['name']} = {cx.ctex(v)}$.", f"پس ${c['name']} = {cx.ctex(v)}$۔",
                          f"{cx.py(v)} == {cx.py(v)}"))
        values[c["name"]] = v
    targets = p["answer"] if isinstance(p["answer"], list) else [p["answer"]]
    answers = []
    for t in targets:
        try:
            s, v = _eval_chunk(t, values)
        except (ValueError, TypeError, ZeroDivisionError, sp.SympifyError):
            return None
        steps += s
        answers.append(v)
    # same question: when the question is itself an expression, its direct value must equal the chunked answer
    direct = solvers10._math_of(question)
    # only when the extracted maths is the WHOLE question (all its numbers); a fragment such as |3+4i| is not the question
    whole = isinstance(direct, str) and direct and question_reader._numbers(direct) == question_reader._numbers(question)
    if whole and len(answers) == 1:
        qpy = solvers10._to_py(direct.strip().strip("|"))
        if qpy and "=" not in qpy:
            try:
                dv = solvers10._complex_const(solvers10._value(qpy))
            except Exception:
                dv = None
            if dv is not None and sp.simplify(dv - answers[0]) != 0:
                return None                           # the plan answers a different question
    return {"steps": steps, "values": values, "answers": answers, "plan": p}


def solve(question, klass="10", generate=None):
    """A solved item for a hard Class 10 question, worked chunk by chunk, or None."""
    if str(klass) != "10":
        return None
    p = plan(question, klass, generate)
    if p is None:
        return None
    r = execute(p, question)
    if r is None:
        return None
    parts = []
    names = "abcdefgh"
    for k, v in enumerate(r["answers"]):
        label = names[k] if len(r["answers"]) > 1 else ""
        steps = r["steps"] if k == 0 else [cx.T("The chunks are worked out in part (a).", "حصے جز (a) میں حل کیے گئے ہیں۔")]
        parts.append(cx.P(label, steps, cx.ans(v), prompt=p.get("asks", "")))
    return {"id": "planned10-" + re.sub(r"[^a-z0-9]+", "-", question.lower())[:40].strip("-"), "kind": "solved", "number": "", "page": 0,
            "question": question, "parts": parts, "verified": True, "source": "planner+solver", "unit": 1, "unit_title": "Complex Numbers",
            "class": 10, "plan": [{"name": c["name"], "what": c.get("what", ""), "expr": c["expr"]} for c in p["chunks"]]}
