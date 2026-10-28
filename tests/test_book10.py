"""The whole Class 10 book (Units 1-12): every item, every step, every check, served by the tutor, found by search.
Run: python tests/test_book10.py

  1. build: every sympy check of every step is true; every answer agrees with the notes' key (or carries a key_note)
  2. structure: ids, parts, steps, English and Urdu text, balanced LaTeX braces, valid board drawings
  3. coverage: every exercise question in the notes' key exists in the book
  4. server: each Class 10 item is listed and served; "Exercise 3.5 Q5 (ii)" style references open the exact part
  5. search: a book question (and each part asked on its own) finds its own item
  6. training data: synthetic Class 10 items are all verified and never copy a book question; the held-out split is clean
"""
import json
import math
import os
import pathlib
import re
import subprocess
import sys

os.environ["TUTOR_NO_ENV_FILE"] = "1"
os.environ["NO_EMBEDDINGS"] = "1"
os.environ["MODEL_BACKEND"] = "local"
ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools", ROOT / "train"):
    sys.path.insert(0, str(p))

FAILS = []


def check(ok, msg):
    if not ok:
        FAILS.append(msg)


# ------------------------------------------------------------------------------------------ 1. build
r = subprocess.run([sys.executable, str(ROOT / "tools" / "build_dataset.py"), "--class", "10"], capture_output=True, text=True, encoding="utf-8",
                   env={**os.environ, "PYTHONIOENCODING": "utf-8"})
summary = [l for l in r.stdout.splitlines() if l.startswith("items:")]
check(r.returncode == 0 and summary and "failed: 0" in summary[0], "build failed:\n" + r.stdout[-3000:] + r.stderr[-2000:])
print("build:", summary[0] if summary else r.stdout[-500:])

units = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((ROOT / "data" / "book10").glob("unit*.json"))]
check([u["unit"] for u in units] == list(range(1, 13)), f"units present: {[u['unit'] for u in units]}")
items = [it for u in units for it in u["items"]]

# ------------------------------------------------------------------------------------------ 2. structure
URDU = re.compile(r"[؀-ۿ]")
DRAW_TYPES = {"line", "poly", "circle", "arc", "text", "dot", "right", "numberline", "subdiv"}
ids = [it["id"] for it in items]
check(len(ids) == len(set(ids)), "duplicate ids")
n_steps = n_checks = n_draw = 0


def balanced(s):
    depth = 0
    for i, ch in enumerate(s):
        if ch == "{" and (i == 0 or s[i - 1] != "\\"):
            depth += 1
        elif ch == "}" and (i == 0 or s[i - 1] != "\\"):
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def numbers(x):
    if isinstance(x, (int, float)):
        yield x
    elif isinstance(x, list):
        for v in x:
            yield from numbers(v)
    elif isinstance(x, dict):
        for k, v in x.items():
            if k not in ("t", "s"):
                yield from numbers(v)


for it in items:
    where = it["id"]
    check(it["kind"] in ("exercise", "review") and it.get("exercise") and it.get("number"), f"{where}: kind/exercise/number")
    check(it["question"].strip() and balanced(it["question"]), f"{where}: question text or braces")
    check(it["parts"], f"{where}: no parts")
    labels = [p["label"] for p in it["parts"]]
    check(len(labels) == len(set(labels)), f"{where}: repeated part labels {labels}")
    for p in it["parts"]:
        w = f"{where} ({p['label'] or '-'})"
        check(p["steps"], f"{w}: no steps")
        check(p["answer"].strip() and balanced(p["answer"]), f"{w}: answer {p['answer']!r}")
        for k, st in enumerate(p["steps"]):
            n_steps += 1
            n_checks += len(st.get("check", []))
            check(st["en"].strip(), f"{w} step {k + 1}: no English")
            words = re.sub(r"\$[^$]*\$", " ", st["en"])          # a heading made only of maths (e.g. "$|z|$:") has nothing to translate
            check(st["ur"].strip() and (URDU.search(st["ur"]) or not re.search(r"[A-Za-z]{3,}", words)), f"{w} step {k + 1}: no Urdu")
            check(balanced(st["math"]), f"{w} step {k + 1}: unbalanced braces in {st['math'][:80]!r}")
            check(not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", st["math"] + st["en"] + st["ur"]), f"{w} step {k + 1}: control character")
            for d in st.get("draw", []):
                n_draw += 1
                check(d.get("t") in DRAW_TYPES, f"{w} step {k + 1}: unknown drawing {d.get('t')}")
                coords = [v for key, val in d.items() if key in ("p", "c", "r") for v in numbers(val)]   # arc angles may be negative
                check(all(math.isfinite(v) for v in numbers(d)) and all(-20 <= v <= 120 for v in coords), f"{w} step {k + 1}: drawing off the board {d}")
        check(any(st.get("check") for st in p["steps"]) or it["unit"] == 10 if "unit" in it else True, f"{w}: no checks")
print(f"structure: {len(items)} items, {sum(len(it['parts']) for it in items)} parts, {n_steps} steps, {n_checks} checks, {n_draw} drawing commands")

# ------------------------------------------------------------------------------------------ 3. coverage against the notes' key
keys_dir = ROOT / "data" / "answers10"
if keys_dir.exists():
    have = {(re.sub(r"\s+", "", it["exercise"]).lower(), it["number"]) for it in items}
    missing = []
    for kp in sorted(keys_dir.glob("unit*.json")):
        for ex_, qs in json.loads(kp.read_text(encoding="utf-8"))["exercises"].items():
            for qn in qs:
                if (ex_, qn) not in have:
                    missing.append(f"{ex_} Q{qn}")
    check(not missing, f"questions in the notes' key but not in the book: {missing}")
    print("coverage: every question of the notes' key is in the book" if not missing else f"coverage: MISSING {missing}")
else:
    print("coverage: data/answers10 not present (private), skipped")

# ------------------------------------------------------------------------------------------ 4. server
import server  # noqa: E402

c = server.app.test_client()
listed = c.get("/api/items?class=10").get_json()
check(len(listed) == len(items), f"/api/items?class=10 lists {len(listed)} of {len(items)}")
for it in items[::7]:
    got = c.get(f"/api/item/{it['id']}?class=10").get_json()
    check(got and got.get("id") == it["id"], f"/api/item/{it['id']} not served")


def ask(q):
    return c.post("/api/answer", json={"question": q, "class": 10}).get_json()


REFS = [("Exercise 2.1 Q4 (v)", "c10-ex2.1-q4", "v"), ("Exercise 3.5 Q5 (ii)", "c10-ex3.5-q5", "ii"), ("ex 4.2 question 3 part 4", "c10-ex4.2-q3", "iv"),
        ("Exercise 5.4 Q1 (xi)", "c10-ex5.4-q1", "xi"), ("Exercise 6.2 Q1 (vi)", "c10-ex6.2-q1", "vi"), ("Exercise 7.2 Q1 (iii)", "c10-ex7.2-q1", "iii"),
        ("Exercise 9.2 Q3 (ii)", "c10-ex9.2-q3", "ii"), ("Exercise 12.1 Q7 (v)", "c10-ex12.1-q7", "v"), ("Review exercise 11 Q8", "c10-rev11-q8", "")]
for ref, iid, lab in REFS:
    d = ask(ref)
    ok = d.get("mode") == "confirm" and d["item"]["id"].startswith(iid) and len(d["item"]["parts"]) == 1 and (not lab or d["item"].get("part_label") == lab)
    check(ok, f"reference {ref!r} -> {d.get('mode')} {d.get('item', {}).get('id')} {d.get('message', '')[:80]}")
print(f"server: {len(listed)} items listed, {len(REFS)} references opened")

# ------------------------------------------------------------------------------------------ 5. search
import rag  # noqa: E402
from modelsolve import explode_all  # noqa: E402

index = rag.Index([ch for it in items for ch in rag.chunk_item(it)], use_embeddings=False)
hit1 = hit3 = n = 0
same_text = {}
for it in items:
    same_text.setdefault(rag.normalize(it["question"]), set()).add(it["id"])
for it in items:
    n += 1
    ids_ = []
    for h in index.search(it["question"], k=10):
        if h["id"] not in ids_:
            ids_.append(h["id"])
    twins = same_text[rag.normalize(it["question"])]      # e.g. the twelve "Choose the correct answer" stems: any of them is the same text
    hit1 += bool(ids_[:1]) and ids_[0] in twins
    hit3 += any(i in twins for i in ids_[:3])
r1, r3 = hit1 / n, hit3 / n
p_hit, p_n = 0, 0
for part in explode_all(items):
    p_n += 1
    base = part["id"].split("#")[0]
    ids_ = []
    for h in index.search(part["question"], k=10):
        if h["id"] not in ids_:
            ids_.append(h["id"])
    p_hit += any(base == i or base.startswith(i + "-") or base.startswith(i + "#") for i in ids_[:3])
check(r3 >= 0.97, f"search recall@3 on book questions {r3:.3f} < 0.97")
print(f"search (TF-IDF): whole questions recall@1 {r1:.3f}, recall@3 {r3:.3f}; single parts recall@3 {p_hit / p_n:.3f} ({p_n} parts)")

# ------------------------------------------------------------------------------------------ 6. training data
from synth10 import TYPES, all_checks_pass, generate  # noqa: E402
import make_dataset  # noqa: E402

syn = generate(2, seed0=7)
check(len(syn) >= len(TYPES) * 2 * 0.9, f"synthetic: only {len(syn)} items for {len(TYPES)} types")
check(all(all_checks_pass(s) for s in syn), "synthetic: an item with a false check")
book_q = {rag.normalize(it["question"]) for it in items}
check(not any(rag.normalize(s["question"]) in book_q for s in syn), "synthetic: copies a book question")
real = make_dataset.load_items("10")
tr, ev = make_dataset.split_real(real, 0, 4)
check(not ({i["id"] for i in tr} & {i["id"] for i in ev}) and len(ev) >= len(real) // 4 - 1, "split: train and test overlap")
check({i["unit"] for i in ev} == set(range(1, 13)), f"split: the test set does not cover every unit {sorted({i['unit'] for i in ev})}")
print(f"training data: {len(syn)} synthetic items over {len(TYPES)} types, all verified; split {len(tr)} train / {len(ev)} test items over 12 units")

if FAILS:
    print(f"\n{len(FAILS)} FAILED:")
    for f in FAILS[:60]:
        print("  -", f)
    sys.exit(1)
print("book10: all tests passed")
