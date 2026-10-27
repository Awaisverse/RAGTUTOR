"""Two classes in one site, and "Exercise 1.2 Q3 (iv)" lookups with confirmation. Run: python tests/test_server_classes.py"""
import os

os.environ["TUTOR_NO_ENV_FILE"] = "1"          # never the real credentials in .env.local
import pathlib
import sys

os.environ["NO_EMBEDDINGS"] = "1"
os.environ["MODEL_BACKEND"] = "local"          # no model here: what is answered comes from the book and the engines
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402

c = server.app.test_client()


def ask(q, klass=None):
    body = {"question": q}
    if klass:
        body["class"] = klass
    r = c.post("/api/answer", json=body)
    assert r.status_code == 200, (q, r.status_code)
    return r.get_json()


# each class lists its own book
n9, n10 = len(c.get("/api/items").get_json()), len(c.get("/api/items?class=10").get_json())
assert n9 > 0 and n10 > 0 and n9 != n10, (n9, n10)
assert c.get("/api/status").get_json()["classes"] == {"9": n9, "10": n10}

# Class 10: a book question, and the same type with new numbers (solved by the Class 10 engine)
d = ask("Simplify and write in the form a+bi: (3-5i) ÷ (2-4i)", 10)
assert d["mode"] == "book" and d["item"]["parts"][0]["answer"] == r"$\frac{13}{10} + \frac{1}{10}i$", d
d = ask("Simplify (7+2i)(3-5i)", 10)
assert d["mode"] == "solved" and d["item"]["parts"][0]["answer"] == "$31 - 29i$", d
d = ask("Find the values of x and y: (2+i)x + (1-2i)y = 7+i", 10)
assert d["mode"] == "solved" and d["item"]["parts"][0]["answer"] == r"$x = 3,\ y = 1$", d

# the Class 9 engine is not used for Class 10, and the other way round
assert ask("Simplify (7+2i)(3-5i)")["mode"] != "solved"
assert ask("Rationalize the denominator of 11/(5+sqrt3)", 10)["mode"] != "solved"
assert ask("Rationalize the denominator of 11/(5+sqrt3)")["mode"] == "solved"

# exercise / question / part references: shown for confirmation, the exact part only
d = ask("Exercise 1.2 Q1 (vii)", 10)
assert d["mode"] == "confirm" and d["message"] == "Is this the question you are asking?", d
assert len(d["item"]["parts"]) == 1 and "3-5i" in d["item"]["question"].replace(" ", ""), d["item"]["question"]
d = ask("ex 1.4 question 2 part 3", 10)
assert d["mode"] == "confirm" and d["item"]["part_label"] == "iii", d
d = ask("Review exercise 1 Q8", 10)
assert d["mode"] == "confirm" and len(d["item"]["parts"]) == 1, d
d = ask("Exercise 1.2 Q3 (iv)")                                   # Class 9 has its own Exercise 1.2
assert d["mode"] == "confirm" and d["item"]["id"].startswith("ex1.2-q3"), d["item"]["id"]

# clear messages when the reference does not exist
assert "has no Exercise 9.9" in ask("Exercise 9.9 Q1", 10)["message"]
assert "there is no question 42" in ask("Exercise 1.2 Q42", 10)["message"]
assert "there is no part (ix)" in ask("Exercise 1.2 Q2 (ix)", 10)["message"]

# a real question that mentions an exercise is still solved as a question, not taken for a reference
assert ask("Exercise 1.2: simplify (7+2i)(3-5i)", 10)["mode"] == "solved"

# bad input never crashes
assert c.post("/api/answer", json={"question": "x" * 3000}).status_code == 400
assert c.post("/api/answer", json={"question": "   "}).status_code == 400
assert ask("((((((", 10)["mode"] == "none"
print("server classes: all tests passed")
