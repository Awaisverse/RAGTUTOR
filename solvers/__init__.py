"""The solver engine: read a student's question, work out its type and numbers, and solve THAT question.

solve(text) returns a solved item (same shape as the stored book items, plus "source": "solver") or None when the
question is not one of the types the engine knows. Every item it returns has passed its own sympy checks; an item with
a failing check is discarded, never shown.

Add a new question type by writing a function try_xxx(text) -> item | None and listing it in SOLVERS.
"""
from . import algebra, numbers, problems
from .common import part_markers

SOLVERS = [
    problems.try_consecutive,
    problems.try_sum_difference,
    problems.try_profit_loss,
    problems.try_simple_profit_rate,
    problems.try_temperature,
    algebra.try_rationalize,
    numbers.try_recurring,
    numbers.try_scientific,
    numbers.try_between,
    algebra.try_power,
]


def solve(text):
    markers = len(part_markers(text)) - 1          # how many (i), (ii), ... parts the question has
    for fn in SOLVERS:
        try:
            item = fn(text)
        except Exception:        # a solver that cannot read the question must never break the others
            item = None
        if not item:
            continue
        if markers > 0 and len(item["parts"]) != markers:
            continue             # it answered only some parts: a partial answer looks complete, so never return it
        return item
    return None
