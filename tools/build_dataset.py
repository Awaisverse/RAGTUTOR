"""Compile data/src/unitNN.py files into data/book/unitNN.json and verify the math.

Every step may carry `check` strings such as "13*(4-sqrt(3))/13 == 4-sqrt(3)".
Each check is verified with sympy: first symbolically, then numerically by
substituting random positive values for any variables. A failed check stops
the build so wrong arithmetic never reaches students.

Usage:  python tools/build_dataset.py            (build + verify all units)
        python tools/build_dataset.py --report   (also print item counts)
"""
import importlib.util
import json
import pathlib
import random
import re
import sys

import sympy as sp

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "src"
OUT = ROOT / "data" / "book"
ANSWERS = ROOT / "data" / "answers"
sys.path.insert(0, str(ROOT))
from answer_match import answer_ok  # noqa: E402

NS = {name: getattr(sp, name) for name in dir(sp) if not name.startswith("_")}
NS.update({"e": sp.E, "pi": sp.pi, "R": sp.Rational, "I": sp.I})
for ch in "abcdfghjklmnpqrstuvwxyz":
    NS.setdefault(ch, sp.Symbol(ch, positive=True))
for ch in "abcdfghjklmnpqrstuvwxyz":
    NS[ch] = sp.Symbol(ch, positive=True)
NS["E"] = sp.E

OPS = ["==", "<=", ">=", "<", ">"]


def _num_equal(a, b):
    syms = sorted((a - b).free_symbols, key=str)
    for _ in range(4):
        subs = {s: sp.Rational(random.randint(11, 37), random.randint(3, 9)) for s in syms}
        va = sp.N(a.subs(subs), 30)
        vb = sp.N(b.subs(subs), 30)
        if abs(complex(va) - complex(vb)) > 1e-9 * max(1, abs(complex(vb))):
            return False
    return True


def verify(expr):
    for op in OPS:
        if op in expr:
            lhs, rhs = expr.split(op, 1)
            break
    else:
        val = sp.sympify(expr, locals=NS)
        return bool(val)
    a = sp.sympify(lhs, locals=NS)
    b = sp.sympify(rhs, locals=NS)
    if op == "==":
        try:
            if sp.simplify(a - b) == 0:
                return True
        except Exception:
            pass
        return _num_equal(a, b)
    av, bv = float(sp.N(a)), float(sp.N(b))
    return {"<": av < bv, ">": av > bv, "<=": av <= bv, ">=": av >= bv}[op]


def load(path):
    spec = importlib.util.spec_from_file_location(path.stem, path)
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(SRC))
    spec.loader.exec_module(mod)
    return mod.UNIT


def load_keys(unit_no):
    """The book's printed answers for a unit (data/answers/unitNN.json), or {} when not transcribed yet."""
    path = ANSWERS / f"unit{unit_no:02d}.json"
    return json.loads(path.read_text(encoding="utf-8")).get("exercises", {}) if path.exists() else {}


def key_for(keys, item, label):
    """The printed answer for one part of an exercise question, or None when the book prints none (figures, open answers)."""
    exercise = re.sub(r"\s+", "", str(item.get("exercise", ""))).lower()
    entry = keys.get(exercise, {}).get(str(item["number"]))
    if isinstance(entry, dict):
        return entry.get(label)
    if isinstance(entry, str) and not entry.startswith(("figures only", "no printed")) and not label:
        return entry
    return None


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    report = "--report" in sys.argv
    failures, total_checks, total_items = [], 0, 0
    key_ok = key_known_errors = 0
    for path in sorted(SRC.glob("unit*.py")):
        unit = load(path)
        keys = load_keys(unit["unit"])
        ids = set()
        for item in unit["items"]:
            if item["id"] in ids:
                failures.append(f"{path.name}: duplicate id {item['id']}")
            ids.add(item["id"])
            for part in item["parts"]:
                if item["kind"] in ("exercise", "review"):
                    printed = key_for(keys, item, part.get("label", ""))
                    if printed is not None:
                        part["book_key"] = printed
                        if answer_ok(part["answer"], printed):
                            key_ok += 1
                        elif part.get("key_note"):
                            key_known_errors += 1
                            print(f"  KNOWN KEY ERROR {item['id']} ({part['label']}): ours {part['answer']!r} vs key {printed!r}")
                        else:
                            failures.append(f"{item['id']} ({part['label'] or '-'}) DIFFERS FROM THE BOOK'S KEY: "
                                            f"ours {part['answer']!r} vs key {printed!r}")
                for i, step in enumerate(part["steps"]):
                    for chk in step.get("check", []):
                        total_checks += 1
                        try:
                            ok = verify(chk)
                        except Exception as exc:  # bad check syntax is a failure too
                            ok = False
                            chk = f"{chk}  [{exc}]"
                        if not ok:
                            failures.append(f"{item['id']} ({part['label'] or '-'}) step {i+1}: {chk}")
        total_items += len(unit["items"])
        out = OUT / f"{path.stem}.json"
        out.write_text(json.dumps(unit, ensure_ascii=False, indent=1), encoding="utf-8")
        if report:
            kinds = {}
            for it in unit["items"]:
                kinds[it["kind"]] = kinds.get(it["kind"], 0) + 1
            print(f"{path.stem}: {unit['title']:<35} {kinds}")
    print(f"items: {total_items}   math checks: {total_checks}   answers agreeing with the book's key: {key_ok}   "
          f"known key errors: {key_known_errors}   failed: {len(failures)}")
    for f in failures:
        print("  FAIL", f)
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
