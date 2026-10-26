"""Verify every synthetic item: all sympy checks must pass. Used by the notebook as a data gate.

Usage: python train/check_synth.py --per-type 60
"""
import argparse
import collections
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT / "train"))
from build_dataset import verify  # noqa: E402
from synth import generate  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--per-type", type=int, default=60)
    args = ap.parse_args()
    items = generate(args.per_type)
    bad, n_checks = [], 0
    per_type = collections.Counter()
    for it in items:
        per_type[it["id"].split("-")[1]] += 1
        for p in it["parts"]:
            for i, st in enumerate(p["steps"]):
                for chk in st.get("check", []):
                    n_checks += 1
                    try:
                        ok = verify(chk)
                    except Exception as exc:
                        ok, chk = False, f"{chk}  [{exc}]"
                    if not ok:
                        bad.append(f"{it['id']} step {i+1}: {chk}")
    print(f"items {len(items)} | types {len(per_type)} | checks {n_checks} | failed {len(bad)}")
    for b in bad[:15]:
        print("  FAIL", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
