"""The question reader with a fake model: rewrites are used only when they keep the student's numbers.
Run: python tests/test_question_reader.py"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import question_reader as qr  # noqa: E402


def fake(reply):
    return lambda prompt: json.dumps(reply)


# a faithful rewrite is used
r = qr.normalize("two plus three i divided by one minus i", "10", fake({"question": "Simplify (2+3i)/(1-i)", "reference": None}))
assert r == {"question": "Simplify (2+3i)/(1-i)", "reference": None}, r

# a rewrite that changes a number is refused, never used
assert qr.normalize("(2+3i)(1-i)", "10", fake({"question": "Simplify (2+3i)(1-2i)", "reference": None})) is None
assert qr.normalize("(2+3i)(1-i)", "10", fake({"question": "Simplify (2+3i)", "reference": None})) is None   # a number dropped

# a textbook reference comes back as a reference
r = qr.normalize("ex 1.4 sawal 2 part 3", "10", fake({"question": "", "reference": {"exercise": "1.4", "number": "2", "part": "(iii)"}}))
assert r == {"question": "", "reference": {"exercise": "1.4", "number": "2", "part": "iii"}}, r

# junk from the model is refused
assert qr.normalize("x", "10", lambda p: "sorry, I cannot help") is None
assert qr.normalize("x", "10", lambda p: "{not json") is None

# the numbers guard reads words, superscripts and decimals, and leaves words like "phone" alone
assert qr.same_numbers("((1+i)/(1-i))¹⁵", "((1+i)/(1-i))^15")
assert qr.same_numbers("two point five", "two point five") and not qr.same_numbers("my phone", "1")
print("question reader: all tests passed")
