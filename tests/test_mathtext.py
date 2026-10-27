"""Tests for mathtext: signatures, same-question matching, and safe parsing. Run: python tests/test_mathtext.py"""
import json
import pathlib
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import mathtext as m  # noqa: E402

# ---- signatures: equal for the same numbers however they are written, different for different numbers
assert m.signature("Rationalize 13/(4+sqrt3)") == m.signature(r"Rationalize $\frac{13}{4+\sqrt{3}}$") == ["13", "4", "+", "3"]
assert m.signature("find 13/(4-sqrt3)") != m.signature("find 13/(4+sqrt3)")                 # the sign matters
assert m.signature("13/(4+sqrt3)") != m.signature("4/(13+sqrt3)")                           # the order matters
assert m.signature("sum of three consecutive integers is forty-two") == ["3", "42"]
assert m.signature("income Rs. 9,60,000 exempt Rs. 1,30,000 at 0.75%") == ["960000", "130000", "0.75"]
assert m.signature("non-terminating decimal 0.35") == ["0.35"]                              # a hyphen between words is not a minus

# ---- a stored question is the same only when the numbers are
book = {x["id"]: x for f in sorted((ROOT / "data" / "book").glob("unit*.json")) for x in json.loads(f.read_text(encoding="utf-8"))["items"]}
same = m.same_question
assert same("sum of three consecutive integers is forty-two, find the three integers", book["ex1.3-q1"]) == (True, None)
assert same("sum of three consecutive integers is 57", book["ex1.3-q1"])[0] is False
assert same("find two numbers whose sum is 68 and difference is 22", book["ex1.3-q4"])[0] is True
assert same("find two numbers whose sum is 90 and difference is 14", book["ex1.3-q4"])[0] is False
assert same("Rationalize 13/(4+sqrt3)", book["ex1.2-q1"]) == (True, 0)                       # one part of a multi-part question
assert same("Rationalize 5/(sqrt7+sqrt3)", book["u1-example8"])[0] is False
assert same("sqrt2+sqrt5 over sqrt3, rationalize", book["ex1.2-q1"])[0] in (True, False)    # must not crash
# "two" reads as 2, so these numbers (2, 3, 4) equal part (vi) "2 3/4" of Represent-on-the-number-line; a sentence with its
# own instruction is not a bare part, and a bare part still is
assert same("Find two rational numbers between 3 and 4.", book["ex1.1-q2"])[0] is False
assert same(r"$2\frac{3}{4}$", book["ex1.1-q2"]) == (True, 5)
assert same("Represent 2 3/4 on the number line", book["ex1.1-q2"]) == (True, 5)

# ---- parsing
P = m.parse_math
assert sp.simplify(P("13/(4+sqrt3)") - 13 / (4 + sp.sqrt(3))) == 0
assert sp.simplify(P(r"\frac{\sqrt{2}+\sqrt{5}}{\sqrt{3}}") - (sp.sqrt(2) + sp.sqrt(5)) / sp.sqrt(3)) == 0
assert P("4sqrt3/(sqrt7+sqrt5)") == 4 * sp.sqrt(3) / (sp.sqrt(7) + sp.sqrt(5))
assert P("(81/16)^(-3/4)") == sp.Rational(81, 16) ** sp.Rational(-3, 4)
assert P(r"\left(\frac{81}{16}\right)^{-\frac{3}{4}}") == sp.Rational(8, 27)
assert P("2sqrt3+3sqrt2") == 2 * sp.sqrt(3) + 3 * sp.sqrt(2)
for bad in ("sqrtt3", "foo(3)", "abc"):                       # unknown words are refused, not split into letters
    try:
        P(bad)
    except ValueError:
        continue
    raise AssertionError(f"should be refused: {bad!r}")
assert P("√7") == sp.sqrt(7) and P("root 7") == sp.sqrt(7)
assert P(r"\sqrt[3]{27}") == 3
for evil in ("__import__('os').system('x')", "open('f')", "x.__class__", "lambda: 1", "eval('1')", "a; b"):
    try:
        P(evil)
    except ValueError:
        continue
    raise AssertionError(f"unsafe text was accepted: {evil!r}")

print("mathtext: all tests passed")
