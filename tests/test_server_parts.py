"""A part asked alone is answered alone; a whole question shows every part. Run: python tests/test_server_parts.py"""
import os
import pathlib
import sys

os.environ["NO_EMBEDDINGS"] = "1"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402

client = server.app.test_client()


def ask(q):
    return client.post("/api/answer", json={"question": q}).get_json()


# one part of Exercise 1.2 Q1, typed alone -> one part, the book's own answer
d = ask("Rationalize the denominator of 13/(4+sqrt3)")
assert d["mode"] == "book" and len(d["item"]["parts"]) == 1, d["mode"]
assert d["item"]["parts"][0]["answer"] == r"$4-\sqrt{3}$" and d["item"]["part_label"] == "i"
assert "(ii)" not in d["item"]["question"] and d["item"]["parts"][0]["label"] == ""

# the same part with its stem, then the 4th part of that question
d = ask(r"Rationalize the denominator of the following: $\frac{\sqrt{2}-1}{\sqrt{5}}$")
assert d["mode"] == "book" and len(d["item"]["parts"]) == 1 and d["item"]["part_label"] == "iii"

# new numbers: the engine answers just that question
d = ask("Rationalize the denominator of 11/(5+sqrt3)")
assert d["mode"] == "solved" and len(d["item"]["parts"]) == 1

# a question that really has two parts keeps both
d = ask("Rationalize the denominator of the following: (i) 3/(2+sqrt5) (ii) 7/(3+sqrt2)")
assert d["mode"] == "solved" and len(d["item"]["parts"]) == 2, (d["mode"], len(d["item"]["parts"]))
print("server parts: all tests passed")
