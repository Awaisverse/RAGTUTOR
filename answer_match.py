"""Comparing a final answer with a reference answer (the book's printed key, or a stored solution).

Used by train/evaluate.py (scoring the model) and tools/build_dataset.py (checking every solution against
the book's Answers section).

Rule: the answers agree when their normalised text is equal, or, when the reference contains numbers, when
the numbers and the + / - signs appear in the same order. So "15.29%" and "15.29% loss" agree, but
"5/9" and "9/5", or "sqrt5+sqrt2" and "sqrt5-sqrt2", do not. Text answers (property names) must match exactly.
"""
import re


def norm_ans(a):
    a = str(a)
    a = re.sub(r"\\text\{([^}]*)\}", r"\1", a)
    for old, new in (("\\dfrac", "\\frac"), ("\\tfrac", "\\frac"), ("\\left", ""), ("\\right", ""),
                     ("\\%", "%"), ("\\,", ""), ("\\!", ""), ("\\;", "")):
        a = a.replace(old, new)
    a = re.sub(r"\^\\circ", "^{\\\\circ}", a)
    return re.sub(r"[\s$]", "", a).lower().rstrip(".")


def _tokens(a):
    """Numbers and + / - signs in order, ignoring LaTeX words and spacing."""
    a = re.sub(r"\\(?:text|left|right|frac|dfrac|sqrt|times|cdot|ldots|bar|overline|circ|Rightarrow)\b", " ", str(a))
    return re.findall(r"\d+(?:\.\d+)?|[+\-]", a)


def answer_ok(model_answer, gold_answer):
    if norm_ans(model_answer) == norm_ans(gold_answer):
        return True
    gold = _tokens(gold_answer)
    return any(t[0].isdigit() for t in gold) and gold == _tokens(model_answer)
