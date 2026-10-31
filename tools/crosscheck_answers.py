"""Independent second solve of every stored answer: the Vertex model solves each question itself (without seeing our
working) and says, part by part, whether its own answer equals ours. Disagreements go to
data/class<K>/crosscheck.json for review by hand; nothing in the book is changed.

  python tools/crosscheck_answers.py --class 10 [--workers 6] [--only id,id]
"""
import argparse
import json
import os
import pathlib
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PROMPT = """Solve this Class {klass} mathematics question (Punjab textbook) yourself, carefully, part by part. Then compare
YOUR final answer for each part with the PROPOSED answer below and say whether they are mathematically the same
(equivalent forms, rounding to the stated places, or an equivalent statement count as the same).

Question: {question}
{parts}

Return ONLY JSON: {{"parts": [{{"label": "<label>", "yours": "<your final answer>", "same": true|false,
"why": "<if not the same: the exact point where they differ>"}}]}}"""

_lock = threading.Lock()


def _env():
    env = ROOT / ".env.local"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip() and k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")


def check(klass, it):
    import vertex_models
    parts = "\n".join(f"Part ({p.get('label') or '-'}): {p.get('prompt', '')}\n   PROPOSED answer: {p['answer']}" for p in it["parts"])
    prompt = PROMPT.format(klass=klass, question=it["question"], parts=parts)
    err = "no answer"
    for _ in range(3):
        try:
            raw = vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=12000, temperature=0.0,
                                         model=os.environ.get("VERTEX_MODEL") or "gemini-4-argon")
            m = re.search(r"\{.*\}", raw or "", re.S)
            txt = m.group(0) if m else "{}"
            try:
                out = json.loads(txt)
            except json.JSONDecodeError:
                out = json.loads(re.sub(r'(?<!\\)\\(?![\\"])', r"\\\\", txt))
            if isinstance(out.get("parts"), list):
                return out
        except Exception as exc:
            err = str(exc)
    return {"error": err}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--class", dest="klass", default="10")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default="")
    a = ap.parse_args()
    _env()
    folder = ROOT / "data" / ("book" if a.klass == "9" else f"book{a.klass}")
    path = ROOT / "data" / f"class{a.klass}" / "crosscheck.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    report = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    only = set(x for x in a.only.split(",") if x)
    jobs = [it for f in sorted(folder.glob("unit*.json")) for it in json.loads(f.read_text(encoding="utf-8"))["items"]
            if (it["id"] in only) or (not only and ("parts" not in report.get(it["id"], {})))]

    def run(it):
        r = check(a.klass, it)
        with _lock:
            report[it["id"]] = r
            path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(run, jobs))
    parts = [p for v in report.values() for p in v.get("parts", [])]
    print(f"items {len(report)}, parts {len(parts)}, same {sum(1 for p in parts if p.get('same'))}, "
          f"different {sum(1 for p in parts if p.get('same') is False)}, errors {sum(1 for v in report.values() if 'error' in v)}")


if __name__ == "__main__":
    main()
