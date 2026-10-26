"""Tests for the evaluation scoring. Run: python train/test_scoring.py

A fair metric accepts equivalent wording and rejects wrong answers. Both directions are tested, using
the real cases from the first training run.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "train"))
from evaluate import answer_ok, score_solution  # noqa: E402
from make_dataset import load_items, solution_json  # noqa: E402

SAME = [  # equivalent answers that the strict first metric wrongly rejected
    (r"$15.29\%$ loss", "15.29%"),
    (r"$28.21\%$ profit", r"$28.21\%$ profit"),
    (r"$37\,^{\circ}C$ and $310\text{ K}$", "37 °C and 310 K"),
    (r"$\sqrt5-\sqrt2$", r"$\sqrt{5}-\sqrt{2}$"),
    ("Rational", "rational"),
]
DIFFERENT = [  # wrong answers that must stay wrong
    (r"$\sqrt{5}+\sqrt{2}$", r"$\sqrt{5}-\sqrt{2}$"),
    (r"$\frac{9}{5}$", r"$\frac{5}{9}$"),
    (r"$28.19\%$ profit", r"$28.21\%$ profit"),
    ("Bilal Rs. 6500; Umair Rs. 56000", "Bilal Rs. 7000; Umair Rs. 56000"),
    ("Addition property of inequality", "Order property w.r.t. addition"),     # text answers must match exactly
    ("Irrational", "Rational"),
    ("$310$", "$37$ and $310$"),
]
for model, gold in SAME:
    assert answer_ok(model, gold), f"should match: {model!r} vs {gold!r}"
for model, gold in DIFFERENT:
    assert not answer_ok(model, gold), f"should NOT match: {model!r} vs {gold!r}"

# every real book item, answered perfectly, must score perfectly; a corrupted answer must not
for it in load_items():
    r = score_solution("Solution:\n" + solution_json(it), it)
    assert r["json_valid"] and r["fully_verified"] and r["checks_ok"] == r["checks"] and r["answer_match"], it["id"]
    sol = json.loads(solution_json(it))
    sol["parts"][0]["answer"] = "$999999$"
    assert not score_solution(json.dumps(sol), it)["answer_match"], f"{it['id']}: wrong answer accepted"

# a reply written with single LaTeX backslashes is repaired and still scores
it = load_items()[0]
single = solution_json(it).replace("\\\\", "\\")
r = score_solution(single, it)
assert r["json_valid"], "single-backslash reply should be repaired"
print("scoring: all tests passed")
