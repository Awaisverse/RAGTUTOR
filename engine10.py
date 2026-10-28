"""The Class 10 engine: complex numbers (solvers10, Unit 1) and every other unit (solvers10x, Units 2-12).

    solve(text) -> a solved item whose every step is checked, or None

A question that shows complex-number signs (5i, i^7, conjugate, modulus, imaginary) goes to the complex-number engine first;
every other question goes only to the Units 2-12 engine, so a fraction like 1/3 in 'roots are -9 and 1/3' is never read
as a complex number.
"""
import re

import solvers10
import solvers10x

COMPLEX = re.compile(r"\d\s*i\b|\bi\s*\^|\bi\b\s*[-+*/)]|[-+(]\s*i\b|conjugate|modulus|imaginary|complex|real part|\ba\s*\+\s*bi\b|\bz\s*=", re.I)


def solve(text):
    text = re.sub(r"\$\s*a\s*\+\s*bi\s*\$", "a+bi", text or "")     # "in the form $a+bi$": the form, not the question
    vector = re.search(r"\\underline\{[ij]\}|\\hat\{[ij]\}|\bvectors?\b|(?:^|[^a-z])\d*\s*j\b", text, re.I)   # i and j unit vectors, not i = sqrt(-1)
    if COMPLEX.search(text) and not vector:
        return solvers10.solve(text)        # never the Units 2-12 engine: it would read i as an unknown
    return solvers10x.solve(text)          # the complex-number engine only sees questions with complex-number signs
