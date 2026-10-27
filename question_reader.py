"""Gemini rewrites a student's question into the clean form the tutor reads. It never solves anything.

Students type questions in many ways: Roman Urdu ("(2+3i) ko (1-i) se zarb dein"), words for numbers, missing brackets,
"ex 1.2 sawal 3 part 2". The rule engine reads one clean form. This module asks a fast Gemini model to rewrite the question
into that form, and then the normal pipeline (book, engine, checked steps) answers the rewritten question.

Safety: a rewrite is accepted only when it keeps exactly the same numbers as the student's text (as a multiset), so a
rewrite can never quietly change the question. The page shows "I read your question as: ..." so the student can check it.

  VERTEX_FAST_MODEL   the model used for rewriting; default gemini-3.8-flash
"""
import json
import os
import re

import mathtext

PROMPT = """You rewrite a student's mathematics question so that a strict computer solver can read it. You NEVER solve it.

The student is in Class {klass} (Punjab textbook, Pakistan). The question may be in English, Urdu or Roman Urdu, may use words
for numbers, and may be badly formatted.

Return ONLY one JSON object:
{{"question": "<the same question, rewritten>", "reference": null}}
or, when the student only names a textbook question (e.g. "ex 1.2 sawal 3 part 2", "exercise 1.4 Q2(iii)"):
{{"question": "", "reference": {{"exercise": "1.4", "number": "2", "part": "iii"}}}}   (part "" when none is given; a review
exercise is written "Review 1")

Rules for "question":
- Keep EVERY number, sign, power and letter exactly as the student gave it. Do not simplify, do not compute, do not add or
  remove anything mathematical.
- Write numbers as digits (two -> 2). Write the maths in plain typed form: i for the imaginary unit, sqrt(5) for roots,
  ^ for powers, / for fractions, explicit brackets, e.g. (3+i)^2/(1-2i).
- Start with the textbook's instruction words in English: "Simplify", "Rationalize the denominator of", "Find the values of x
  and y", "Find the modulus of", "Find the multiplicative inverse of", "Find the real and imaginary parts of",
  "Solve for z and w", "If z = ..., find (a) ... (b) ...".
- Several parts are written (i) ..., (ii) ..., or (a) ..., (b) ... as the student had them.
- Translate Urdu or Roman Urdu wording to English.

Student's question:
{text}"""

_SUP = str.maketrans("⁰¹²³⁴⁵⁶⁷⁸⁹⁻", "0123456789-")


def _numbers(text):
    """The numbers in a text, as a sorted list (words and superscripts turned into digits), for the same-numbers guard."""
    t = mathtext.words_to_digits(str(text).translate(_SUP))
    t = re.sub(r"\bone\b", "1", re.sub(r"\bzero\b", "0", t, flags=re.I), flags=re.I)   # words_to_digits leaves these two
    return sorted(re.findall(r"\d+(?:\.\d+)?", t))


def same_numbers(original, rewritten):
    return _numbers(original) == _numbers(rewritten)


def normalize(text, klass="9", generate=None):
    """-> {"question": str, "reference": dict or None} or None when the rewrite is unusable or changed the numbers."""
    if generate is None:
        import vertex_models

        def generate(prompt):
            # rewriting needs no long thinking: with it off the fast model answers in about 5 s instead of up to 30 s
            return vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=1024, temperature=0.0,
                                          model=os.environ.get("VERTEX_FAST_MODEL") or "gemini-3.8-flash", thinking_budget=0)
    raw = generate(PROMPT.format(klass=klass, text=str(text)[:1500]))
    m = re.search(r"\{.*\}", raw or "", re.S)
    if not m:
        return None
    try:
        out = json.loads(m.group(0))
    except json.JSONDecodeError:
        return None
    ref = out.get("reference")
    if isinstance(ref, dict) and ref.get("exercise") and ref.get("number"):
        return {"question": "", "reference": {"exercise": str(ref["exercise"]), "number": str(ref["number"]),
                                              "part": str(ref.get("part") or "").strip("() ").lower()}}
    q = str(out.get("question") or "").strip()
    if not q or not same_numbers(text, q):
        return None                                  # an empty rewrite, or one that changed a number: not trusted
    return {"question": q, "reference": None}
