"""Small helpers for writing solution files compactly.

    S(math, en, ur, *checks, draw=None)   -> one step on the board
    P(label, steps, answer, prompt="", figure=None) -> one part of a question
    Q(id, kind, number, page, question, parts, exercise=None) -> a book item
"""


def S(math, en, ur, *checks, draw=None):
    step = {"math": math, "en": en, "ur": ur}
    if checks:
        step["check"] = list(checks)
    if draw:
        step["draw"] = draw
    return step


def T(en, ur, *checks, draw=None):
    """A step with no math line (pure explanation / drawing)."""
    return S("", en, ur, *checks, draw=draw)


def P(label, steps, answer, prompt="", figure=None):
    part = {"label": label, "prompt": prompt, "steps": steps, "answer": answer}
    if figure:
        part["figure"] = figure
    return part


def Q(id, kind, number, page, question, parts, exercise=None):
    item = {"id": id, "kind": kind, "number": str(number), "page": page,
            "question": question, "parts": parts}
    if exercise:
        item["exercise"] = exercise
    return item


def one(steps, answer, figure=None):
    """Shortcut for a question with a single unlabeled part."""
    return [P("", steps, answer, figure=figure)]
