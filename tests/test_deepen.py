"""A new question solved in one or two steps gets detailed working, but only working that keeps the answer and passes
every check; a rewrite that changes the answer or carries a false check is thrown away."""
import json
import os
import pathlib
import sys

os.environ["TUTOR_NO_ENV_FILE"] = "1"
os.environ["QUESTION_READER"] = "on"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import server  # noqa: E402
import vertex_models  # noqa: E402

server.reader_on = lambda: True


def item():
    return {"question": "Find the mean of 2, 4, 9", "unit_title": "Information Handling",
            "parts": [{"label": "", "answer": "$5$", "steps": [{"math": r"\bar{x} = \frac{15}{3} = 5", "en": "Mean.", "ur": "اوسط۔", "check": ["15/3 == 5"]}]}]}


def reply(steps, answer):
    return lambda *a, **k: json.dumps({"steps": steps, "answer": answer}, ensure_ascii=False)


S = lambda m, c: {"math": m, "en": "Explain.", "ur": "وضاحت۔", "check": c}
good = [S(r"2, 4, 9", []), S(r"\sum x = 2 + 4 + 9 = 15", ["2 + 4 + 9 == 15"]), S(r"n = 3", []), S(r"\bar{x} = \frac{15}{3} = 5", ["15/3 == 5"])]

vertex_models.generate = reply(good, "$5$")
it = server.deepen(item(), "10")
assert it["parts"][0].get("enriched") and len(it["parts"][0]["steps"]) == 4, it

vertex_models.generate = reply(good, "$6$")                              # the answer changed: keep the engine's steps
it = server.deepen(item(), "10")
assert not it["parts"][0].get("enriched") and len(it["parts"][0]["steps"]) == 1

bad = good[:1] + [S(r"\sum x = 2 + 4 + 9 = 16", ["2 + 4 + 9 == 16"])] + good[2:]   # a false check
vertex_models.generate = reply(bad, "$5$")
it = server.deepen(item(), "10")
assert not it["parts"][0].get("enriched")

def boom(*a, **k):
    raise RuntimeError("network down")
vertex_models.generate = boom                                            # a failing model never breaks the answer
it = server.deepen(item(), "10")
assert it["parts"][0]["answer"] == "$5$" and len(it["parts"][0]["steps"]) == 1

os.environ["DEEPEN_STEPS"] = "off"
vertex_models.generate = reply(good, "$5$")
assert not server.deepen(item(), "10")["parts"][0].get("enriched")
print("deepen: all tests passed")
