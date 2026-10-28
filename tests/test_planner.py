"""The planner with a fake model: chunked plans are executed by the engine, and only for the SAME question.
Run: python tests/test_planner.py"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import planner  # noqa: E402


def fake(p):
    return lambda prompt: json.dumps(p)


Q = "Simplify ((1+i)/(1-i))^15 + ((1-i)/(1+i))^10"
good = {"chunks": [{"name": "A", "what": "first fraction", "expr": "(1+i)/(1-i)"}, {"name": "B", "what": "its 15th power", "expr": "A^15"},
                   {"name": "C", "what": "second fraction", "expr": "(1-i)/(1+i)"}, {"name": "D", "what": "its 10th power", "expr": "C^10"},
                   {"name": "E", "what": "add them", "expr": "B + D"}], "answer": "E", "asks": "the simplified value"}
it = planner.solve(Q, "10", fake(good))
assert it and it["parts"][0]["answer"] == "$-1 - i$", it and it["parts"][0]["answer"]
assert [c["name"] for c in it["plan"]] == list("ABCDE")
assert any("Chunk B" in s.get("en", "") for s in it["parts"][0]["steps"])

# a plan that brings in a number not in the question is refused
bad_number = json.loads(json.dumps(good))
bad_number["chunks"][1]["expr"] = "A^16"
assert planner.solve(Q, "10", fake(bad_number)) is None

# a plan that uses the question's numbers but answers a different question is refused (direct value differs)
wrong = json.loads(json.dumps(good))
wrong["chunks"][4]["expr"] = "B - D"
assert planner.solve(Q, "10", fake(wrong)) is None

# functions and several answers
Q2 = "If z = (2+i)^2, find the conjugate of z and |3+4i|"
two = {"chunks": [{"name": "A", "what": "z", "expr": "(2+i)^2"}, {"name": "B", "what": "conjugate of z", "expr": "conj(A)"},
                  {"name": "C", "what": "modulus", "expr": "abs(3+4i)"}], "answer": ["B", "C"], "asks": "conjugate and modulus"}
it = planner.solve(Q2, "10", fake(two))
assert it and [p["answer"] for p in it["parts"]] == ["$3 - 4i$", "$5$"], it and [p["answer"] for p in it["parts"]]

# junk plans are refused; Class 9 is not planned
assert planner.solve(Q, "10", lambda p: "no plan") is None
assert planner.solve(Q, "10", fake({"chunks": [{"name": "I", "expr": "2"}], "answer": "I"})) is None     # I is the imaginary unit
assert planner.solve(Q, "9", fake(good)) is None
print("planner: all tests passed")

# functions inside a sum, nested
Q3 = "Simplify conj((2+i)^2) + |3+4i|"
nested = {"chunks": [{"name": "A", "what": "square", "expr": "(2+i)^2"}, {"name": "B", "what": "sum", "expr": "conj(A) + abs(3+4i)"}],
          "answer": "B", "asks": "the value"}
it = planner.solve(Q3, "10", fake(nested))
assert it and it["parts"][0]["answer"] == "$8 - 4i$", it and it["parts"][0]["answer"]
print("planner nested functions: passed")

# a plan that stops early (answers only part of the question) is refused: it would answer a related question
early = json.loads(json.dumps(nested))
early["chunks"] = [{"name": "A", "what": "square", "expr": "(2+i)^2"}, {"name": "B", "what": "conjugate", "expr": "conj(A)"}]
early["answer"] = "B"
assert planner.solve(Q3, "10", fake(early)) is None
# a chunk computed but never used for the answer does not count as covering the question
unused = json.loads(json.dumps(early))
unused["chunks"].append({"name": "C", "what": "modulus", "expr": "abs(3+4i)"})
assert planner.solve(Q3, "10", fake(unused)) is None
# a plan that reuses a chunk (z^2 used twice) is fine
Q4 = "If z = 1+i, find z^2 + 1/z^2"
reuse = {"chunks": [{"name": "A", "expr": "1+i"}, {"name": "B", "expr": "A^2"}, {"name": "C", "expr": "1/B"}, {"name": "D", "expr": "B + C"}], "answer": "D"}
it = planner.solve(Q4, "10", fake(reuse))
assert it and it["parts"][0]["answer"] == r"$\frac{3}{2}i$", it and it["parts"][0]["answer"]
print("planner same-question coverage: passed")
