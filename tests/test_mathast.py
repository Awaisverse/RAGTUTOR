"""Tests for mathast: reading, printing as written, evaluating. Run: python tests/test_mathast.py"""
import pathlib
import sys

import sympy as sp

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
import mathast as A  # noqa: E402

# printed back as written
shown = {
    "x + 1/x": r"x + \frac{1}{x}",
    "13/(4+sqrt3)": r"\frac{13}{4 + \sqrt{3}}",
    "(3/4)^(-2)": r"\left(\frac{3}{4}\right)^{-2}",
    "(0.027)^(-1/3)": r"0.027^{-\frac{1}{3}}",
    "25^(n+1)": r"25^{n + 1}",
    "5*25^(n+1) - 25*5^(2n)": r"5 \times 25^{n + 1} - 25 \times 5^{2n}",
    "4sqrt3/(sqrt7+sqrt5)": r"\frac{4\sqrt{3}}{\sqrt{7} + \sqrt{5}}",
    r"\left(\frac{81}{16}\right)^{-\frac{3}{4}}": r"\left(\frac{81}{16}\right)^{-\frac{3}{4}}",
}
for text, want in shown.items():
    got = A.text_to_tex(text)
    assert got == want, f"{text!r}\n  got  {got!r}\n  want {want!r}"

# evaluated
V = lambda t: A.to_sympy(A.parse(t))  # noqa: E731
assert V("(3/4)^(-2) / (4/9)^3 * 16/27") == 12
assert V("(81/16)^(-3/4)") == sp.Rational(8, 27)
assert V("13/(4+sqrt3)") == 13 / (4 + sp.sqrt(3))
assert V("-2^2") == -4 and V("2^-3") == sp.Rational(1, 8) and V("2^3^2") == 512      # unary minus below power; power is right-associative
assert sp.simplify(V("20(4^(2x))") - 20 * 4 ** (2 * sp.Symbol("x", positive=True))) == 0
assert V("3(2+1)") == 9 and V("2sqrt3") == 2 * sp.sqrt(3)

# reading order of a chain of * and /
f = A.factors(A.parse("a/b*c/d"))
assert [s for _, s in f] == [1, -1, 1, -1]
assert [len(t) for t in (A.terms(A.parse("a - b + c")),)] == [3] and [s for _, s in A.terms(A.parse("a - b + c"))] == [1, -1, 1]
assert A.top_split("a = (b, c) = d", "=") == ["a ", " (b, c) ", " d"]

# refused, not guessed
for bad in ("foo(3)", "2 +", "(1+2", "1 2 )", "x y z q w e r"[:0] + ")"):
    try:
        A.parse(bad)
    except ValueError:
        continue
    raise AssertionError(f"should be refused: {bad!r}")

print("mathast: all tests passed")
