"""modelsolve with a fake model: retry on a failed check, per-part split, nothing usable. Run: python train/test_modelsolve.py"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import modelsolve  # noqa: E402


def reply(answer, check):
    return json.dumps({"id": "t", "kind": "generated", "number": "", "page": 0, "question": "q", "parts": [
        {"label": "", "prompt": "", "figure": None, "steps": [{"math": "x", "say": "s", "check": [check]}], "answer": answer}]})


def fake(replies):
    seen = []

    def gen(messages, max_new_tokens, temperature):
        seen.append((messages[1]["content"], temperature))
        return replies[min(len(seen) - 1, len(replies) - 1)]
    return gen, seen


def main():
    # 1. first reply has a false check, the sampled retry is right
    gen, seen = fake([reply("5", "2 + 2 == 5"), reply("4", "2 + 2 == 4")])
    r = modelsolve.attempt("What is 2+2?", "", 3, generate=gen)
    assert r["verified"] and r["tries"] == 2 and r["solution"]["parts"][0]["answer"] == "4", r
    assert [t for _, t in seen] == [0.0, 0.5]

    # 2. always wrong: returned, but marked unverified with the failed check listed
    gen, _ = fake([reply("5", "2 + 2 == 5")])
    r = modelsolve.attempt("What is 2+2?", "", 3, generate=gen)
    assert not r["verified"] and r["tries"] == 3 and r["bad"] == ["2 + 2 == 5"]

    # 3. not JSON at all
    gen, _ = fake(["sorry, I cannot"])
    assert modelsolve.attempt("q", "", 2, generate=gen)["solution"] is None

    # 4. two parts are asked separately, with the stem repeated
    gen, seen = fake([reply("4", "2 + 2 == 4"), reply("6", "3 + 3 == 6")])
    sol = modelsolve.solve_question("Add: (i) 2+2 (ii) 3+3", lambda q: "", 3, generate=gen)
    assert [q for q, _ in seen] == ["Add: 2+2", "Add: 3+3"], seen
    assert sol["verified"] and [p["label"] for p in sol["parts"]] == ["i", "ii"] and [p["answer"] for p in sol["parts"]] == ["4", "6"]

    # 5. one failing part makes the whole answer unverified
    gen, _ = fake([reply("4", "2 + 2 == 4"), reply("7", "3 + 3 == 7")])
    sol = modelsolve.solve_question("Add: (i) 2+2 (ii) 3+3", lambda q: "", 1, generate=gen)
    assert not sol["verified"] and sol["unverified_checks"] == ["3 + 3 == 7"]
    print("modelsolve ok")


if __name__ == "__main__":
    main()
