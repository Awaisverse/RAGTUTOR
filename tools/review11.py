"""Review every Class 11 solution against the typed reference pages (data/class11/ref/pages/kanwal, kept private), with
the same six headings as tools/review10.py: answer, method, steps, explanation, urdu, figure.

  python tools/review11.py [--only id,id] [--workers 6]       -> data/class11/review.json
"""
import argparse
import base64
import json
import os
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import review10 as R  # noqa: E402
from audit_questions10 import _env, _json  # noqa: E402

REF = ROOT / "data" / "class11" / "ref"
REPORT = ROOT / "data" / "class11" / "review.json"
_lock = threading.Lock()


SOURCES = {"1": ("questions_kanwal.json", "kanwal"), "3": ("questions_u03.json", "u03")}   # per unit: question index, page folder


def pages_for(it):
    unit = it["exercise"].split(".")[0]
    qfile, folder = SOURCES[unit]
    q = json.loads((REF / qfile).read_text(encoding="utf-8"))
    pre = f"{it['exercise']}|{it['number']}|"
    pages = sorted({p for k, v in q.items() if k.startswith(pre) for p in v["pages"]})
    return [REF / "pages" / folder / f"{p}.png" for p in pages][:5]


def review(it, parts, pngs):
    import vertex_models
    imgs = [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode(p.read_bytes()).decode("ascii")}} for p in pngs]
    fig = R.figure_png(it, parts)
    if fig:
        imgs.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(fig).decode("ascii")}})
    ref = f"Exercise {it['exercise']} Q{it['number']}"
    ours = f"QUESTION: {it['question']}\n\n" + "\n\n".join(R.part_text(p) for p in parts)
    note = " The LAST image is the figure OUR board draws." if fig else ""
    if len(parts) < len(it["parts"]):
        note += f" This check covers ONLY part(s) {', '.join(p.get('label') or '-' for p in parts)}; do not report the others as missing."
    prompt = R.PROMPT.format(ref=ref, unit=it["exercise"].split(".")[0], fig_note=note, ours=ours).replace("Class 10", "Class 11").replace(
        "a solutions book that print", "a typed solutions book (Class 11, Punjab/PECTAA) that print")
    body = {"contents": [{"role": "user", "parts": imgs + [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 16000, "responseMimeType": "application/json"}}
    err = "no answer"
    for _ in range(3):
        try:
            out = _json(vertex_models._post(body, os.environ.get("VERTEX_VISION_MODEL") or "gemini-4-argon"))
            if "ok" in out:
                return out
        except Exception as exc:
            err = str(exc)
    return {"ok": None, "error": err}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    _env()
    os.environ.setdefault("VERTEX_TIMEOUT", "180")
    only = set(x for x in a.only.split(",") if x)
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    items = [it for f in sorted((ROOT / "data" / "book11").glob("unit*.json")) for it in json.loads(f.read_text(encoding="utf-8"))["items"]]
    jobs = [it for it in items if (not only or it["id"] in only) and (only or report.get(it["id"], {}).get("ok") is None)]

    def run(it):
        issues, ok, errs = [], True, []
        for parts in R.chunks(it):
            r = review(it, parts, pages_for(it))
            if r.get("ok") is None:
                errs.append(r.get("error", ""))
                continue
            ok = ok and bool(r["ok"]) and not r.get("issues")
            issues += r.get("issues") or []
        with _lock:
            report[it["id"]] = {"ok": None if errs else ok, "issues": issues, **({"error": errs[0]} if errs else {})}
            REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            print(it["id"], "ok" if ok and not errs else f"{len(issues)} issues", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(run, jobs))
    v = list(report.values())
    print(f"reviewed {len(v)}: ok {sum(1 for x in v if x.get('ok'))}, with issues {sum(1 for x in v if x.get('ok') is False)}")


if __name__ == "__main__":
    main()
