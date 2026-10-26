"""Unit tests for solution_io.parse_solution. Run: python train/test_solution_io.py"""
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))
from solution_io import parse_solution  # noqa: E402

LATEX = r"\frac{1}{2} \times 3 \neq \sqrt{5} \bar{x} \text{ok} \right) \theta"
GOOD = json.dumps({"math": LATEX, "a": "ok"})               # correctly escaped: every backslash doubled
SINGLE = GOOD.replace("\\\\", "\\")                         # the model wrote single backslashes
MIXED = '{"m1": ' + json.dumps(LATEX) + ', "m2": "' + "\\frac{3}{4}" + '"}'


def check(name, raw, want_repaired, key="math"):
    obj, repaired = parse_solution(raw)
    assert repaired is want_repaired, f"{name}: repaired={repaired}, expected {want_repaired}"
    assert obj[key] == LATEX or key == "m2", f"{name}: LaTeX was corrupted: {obj[key]!r}"
    return obj


check("correctly escaped", GOOD, False)
check("single backslashes", SINGLE, True)
check("prose around JSON", "Here it is:\n" + GOOD + "\nDone.", False)
obj = check("mixed good and bad", MIXED, True, key="m1")
assert obj["m2"] == "\\frac{3}{4}", f"mixed: second value corrupted: {obj['m2']!r}"

for name, raw in {"truncated": GOOD[:-8], "no json": "prose only", "broken syntax": '{"math": }'}.items():
    try:
        parse_solution(raw)
    except ValueError:
        continue
    raise AssertionError(f"{name}: should have raised ValueError")

print("solution_io: all tests passed")
