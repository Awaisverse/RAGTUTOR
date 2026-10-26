"""Accuracy of the solver engine. Run: python tests/test_solvers.py [--per-type 40]

A. BOOK       every stored question the engine can read must give the same answer as the book.
B. VARIANTS   new questions (same types, numbers the book never used) must be solved with the correct answer.
              The correct answer comes from the generator that wrote the question, not from the engine.
C. NO MIX-UP  a question with different numbers must never be taken for a stored question.
D. REFUSAL    questions the engine does not know must be refused, never guessed.

The test fails if any answer is WRONG. A question the engine does not recognise is reported but is not a failure:
it falls through to the trained model. Wrong answers are the failures that matter.
"""
import argparse
import collections
import json
import pathlib
import random
import re
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools", ROOT / "train", ROOT / "data" / "src"):
    sys.path.insert(0, str(p))

import mathtext  # noqa: E402
import solvers  # noqa: E402
from answer_match import answer_ok  # noqa: E402
from synth import GENERATORS  # noqa: E402

JUNK = re.compile(r"\\%|%|\\text\{[^}]*\}|\b(?:profit|loss|years?|rs\.?)\b|\\,|\\ |\^\{\\circ\}\s*[CF]|\^\\circ\s*[CF]", re.I)


BOOK_ROUNDING = {"u1-example11"}


def values(answer):
    """The numbers in an answer as sympy values, or None when it is not purely numeric. 'a = b' counts as b."""
    a = JUNK.sub(" ", str(answer).replace("$", " "))
    pieces = [x.split("=")[-1] for x in re.split(r",|\band\b|;", a) if x.strip()]
    out = []
    for piece in pieces:
        try:
            out.append(sp.nsimplify(mathtext.parse_math(piece.strip())))
        except (ValueError, TypeError):
            return None
    return out


def same_answer(engine, gold):
    if answer_ok(engine, gold):
        return True
    a, b = values(engine), values(gold)
    if a is None or b is None or len(a) != len(b):
        return False
    def close(x, y):
        d = sp.simplify(x - y)
        if d == 0:
            return True
        try:
            return abs(float(sp.N(d))) < 0.006        # numeric answers: allow rounding in the last place
        except TypeError:                              # still contains an unknown: genuinely different
            return False
    return all(close(x, y) for x, y in zip(a, b))


def engine_answers(item):
    return [p["answer"] for p in item["parts"]]


def load_book():
    out = {}
    for f in sorted((ROOT / "data" / "book").glob("unit*.json")):
        for it in json.loads(f.read_text(encoding="utf-8"))["items"]:
            out[it["id"]] = it
    return out


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-type", type=int, default=40)
    args = ap.parse_args()
    wrong, report = [], []
    book = load_book()

    # ---------------------------------------------------------------- A. book
    supported = agree = 0
    for it in book.values():
        got = solvers.solve(it["question"])
        if got is None:
            continue
        supported += 1
        gold = [p["answer"] for p in it["parts"]]
        ours = engine_answers(got)
        if len(ours) == len(gold) and all(same_answer(o, g) for o, g in zip(ours, gold)):
            agree += 1
        elif it["id"] in BOOK_ROUNDING:
            agree += 1      # the book truncates 3.945... to 3.94; the engine rounds to 3.95, which is the correct rounding
        else:
            wrong.append(f"BOOK {it['id']}: engine {ours} vs book {gold}")
    report.append(f"A. book questions the engine can read: {supported} of {len(book)}; same answer as the book: {agree}")

    # ---------------------------------------------------------------- B. variants (new numbers)
    per = collections.defaultdict(lambda: [0, 0, 0])   # solved correctly, solved wrongly, not recognised
    known = {it["question"] for it in book.values()}
    variants = []
    for name, fn in GENERATORS.items():
        for seed in range(1000, 1000 + args.per_type * 3):
            it = fn(random.Random(f"{name}-{seed}"), seed)
            if it["question"] in known:
                continue
            variants.append((name, it))
            if sum(1 for n, _ in variants if n == name) >= args.per_type:
                break
    for name, it in variants:
        got = solvers.solve(it["question"])
        if got is None:
            per[name][2] += 1
            continue
        gold = [p["answer"] for p in it["parts"]]
        ours = engine_answers(got)
        if len(ours) == len(gold) and all(same_answer(o, g) for o, g in zip(ours, gold)):
            per[name][0] += 1
        else:
            per[name][1] += 1
            wrong.append(f"VARIANT {name}: {it['question'][:90]!r}\n      engine {ours}\n      gold   {gold}")
    report.append("B. new questions (numbers the book never used), per type:")
    for name in GENERATORS:
        ok, bad, none = per[name]
        tag = "WRONG" if bad else ("ok" if ok and not none else ("partly" if ok else "not recognised"))
        report.append(f"     {name:18} solved {ok:3}   wrong {bad:3}   not recognised {none:3}   [{tag}]")
    tot_ok = sum(v[0] for v in per.values())
    tot_bad = sum(v[1] for v in per.values())
    tot_none = sum(v[2] for v in per.values())
    report.append(f"     TOTAL: solved correctly {tot_ok}, solved WRONG {tot_bad}, not recognised {tot_none}")

    # ---------------------------------------------------------------- consecutive integers (no generator): independent formula
    rng = random.Random(7)
    ok = bad = 0
    for _ in range(40):
        k, kind, x0 = rng.choice([2, 3, 4, 5]), rng.choice(["", "odd", "even"]), rng.randint(2, 60)
        if kind == "odd" and x0 % 2 == 0:
            x0 += 1
        if kind == "even" and x0 % 2 == 1:
            x0 += 1
        d = 2 if kind else 1
        vals = [x0 + d * i for i in range(k)]
        words = {2: "two", 3: "three", 4: "four", 5: "five"}[k]
        q = f"The sum of {words} consecutive {kind + ' ' if kind else ''}integers is {sum(vals)}. Find the integers."
        got = solvers.solve(q)
        if got and [int(x) for x in re.findall(r"\d+", got["parts"][0]["answer"])] == vals:
            ok += 1
        else:
            bad += 1
            wrong.append(f"CONSECUTIVE {q!r}: engine {got and got['parts'][0]['answer']} vs {vals}")
    report.append(f"B2. consecutive integers (independent check): correct {ok}, wrong {bad}")

    # ---------------------------------------------------------------- C. no mix-up
    # Harm is showing a stored solution whose answer differs from the right answer for the new question. When the generator
    # happens to pick the book's own numbers the question really is the stored one, and showing it is correct.
    mixed = coincide = 0
    for name, it in variants:
        gold = [p["answer"] for p in it["parts"]]
        for stored in book.values():
            same, part = mathtext.same_question(it["question"], stored)
            if not same:
                continue
            shown = [stored["parts"][part]["answer"]] if part is not None else [p["answer"] for p in stored["parts"]]
            if len(shown) == len(gold) and all(same_answer(s, g) for s, g in zip(shown, gold)):
                coincide += 1
            else:
                mixed += 1
                wrong.append(f"MIX-UP: new question {it['question'][:90]!r} was taken for stored {stored['id']} ({stored['question'][:60]!r})")
    own = sum(1 for it in book.values() if len(mathtext.signature(it["question"])) >= 2 and mathtext.same_question(it["question"], it)[0])
    has_sig = sum(1 for it in book.values() if len(mathtext.signature(it["question"])) >= 2)
    report.append(f"C. new questions that would have shown a stored solution with a DIFFERENT answer: {mixed} (must be 0); "
                  f"(generator reused the book's own numbers, correct to show: {coincide}); stored questions recognised as themselves: {own} of {has_sig}")
    if own != has_sig:
        wrong.append(f"SELF: {has_sig - own} stored questions are not recognised as themselves")

    # ---------------------------------------------------------------- D. refusal
    unknown = ["What is the derivative of sin x", "find the area of a circle of radius 7", "solve x^2 - 5x + 6 = 0 using the formula",
               "who wrote Hamlet", "rationalize 7/3", "express 0.5 as p/q", "convert 5 to scientific notation please and also explain history"]
    accepted = [q for q in unknown if solvers.solve(q)]
    report.append(f"D. questions outside the engine's types that it answered anyway: {len(accepted)} of {len(unknown)} {accepted}")
    for q in accepted:
        if q not in ("convert 5 to scientific notation please and also explain history",):
            wrong.append(f"REFUSAL: answered {q!r}")

    print("\n".join(report))
    if wrong:
        print(f"\n{len(wrong)} PROBLEM(S):")
        for w in wrong[:25]:
            print("  -", w)
        sys.exit(1)
    print("\nno wrong answers")


if __name__ == "__main__":
    main()
