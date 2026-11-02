"""Review every Class 10 solution against the book's own pages, from every angle a teacher would check.

For each question the Vertex vision model gets the page image(s) that print the question and its worked solution, a
picture of the figure our board draws (if any), and our whole solution: every step with its English line, Urdu line and
"why", the final answer and its "what this answer means". It reports problems under six headings:

  answer       our final answer differs from the book's printed answer (and which one is right)
  method       our working ignores the method the instruction asks for ("by factorization", "using Cramer's rule", ...)
  steps        a step is wrong, does not follow from the one before, or skips a step a student needs
  explanation  a "why" or "meaning" is wrong, contradicts the maths, or is generic rather than about this question
  urdu         the Urdu says something different from the English, has different maths, or is left in English
  figure       the figure we draw disagrees with the book's figure or with the question's data

Nothing is changed: the report goes to data/class10/review.json (private) and is triaged by hand.

  python tools/review10.py [--units 2,3] [--only id,id] [--workers 6] [--redo]
"""
import argparse
import base64
import io
import json
import math
import os
import pathlib
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from audit_questions10 import PAGES, _env, _json  # noqa: E402

REPORT = ROOT / "data" / "class10" / "review.json"
AUDIT = ROOT / "data" / "class10" / "audit.json"
CHUNK = 22000          # characters of our solution per call; a long question is reviewed a few parts at a time

PROMPT = """You are an experienced Class 10 mathematics teacher (Punjab Curriculum and Textbook Board) checking a tutor
app's solution. The first image(s) are the page(s) of a solutions book that print question {ref} (Unit {unit}) and its
worked solution.{fig_note} Below is OUR solution, as a student sees it: each step shows the maths, an English line,
an Urdu line and a "why"; each part ends with the final answer and "what this answer means".

Check OUR solution under these headings and report only definite problems, not style preferences:
* answer: our final answer differs from the book's printed final answer. Work it out yourself and say which is right
  (the book can be wrong). Equivalent forms (2/4 vs 1/2, rationalised or not, order of roots) are NOT a difference.
* method: the instruction asks for a particular method (e.g. "by factorization", "by completing the square", "using
  Cramer's rule", "synthetic division", "graphically", "prove") and our working uses a different one, or does not do what
  is asked (e.g. only states the answer to a "prove" question).
* steps: a step is mathematically wrong, does not follow from the step before, uses a value not in the question, or
  leaves out a step a Class 10 student needs to follow the working.
* explanation: a "why" or "meaning" is mathematically wrong, contradicts the steps, describes a different question, or
  is generic filler that does not refer to this question's numbers.
* urdu: an Urdu line says something different from its English line, has different maths or numbers, or is left in
  English. Normal Urdu use of English maths words (e.g. فنکشن, ٹرم) is fine.
* figure: the figure we draw is wrong for the question (wrong labels, values, shape, missing part of the book's figure).
  Our figure is a rough preview of a canvas drawing: ignore fonts, colours, tick spacing and exact proportions.
Use "error" when a student would learn something wrong or get confused, "minor" for small slips.
Steps are numbered per part as [part label] step N.

OUR SOLUTION:
{ours}

Return ONLY JSON: {{"ok": true|false, "issues": [{{"part": "<label>", "step": <number or null>,
"kind": "answer|method|steps|explanation|urdu|figure", "severity": "error|minor", "what": "<the problem>",
"fix": "<what it should say>"}}]}}"""


def _w(v):
    return (v or {}).get("en", "") if isinstance(v, dict) else (v or "")


def part_text(p):
    lab = p.get("label") or "-"
    out = [f"=== Part [{lab}] {p.get('prompt', '')}".rstrip()]
    for i, s in enumerate(p["steps"], 1):
        out.append(f"[{lab}] step {i}: $${s.get('math', '')}$$")
        out.append(f"   EN: {s.get('en', '')}")
        out.append(f"   UR: {s.get('ur', '')}")
        if s.get("why"):
            out.append(f"   WHY: {_w(s['why'])}")
            if isinstance(s["why"], dict) and s["why"].get("ur"):
                out.append(f"   WHY-UR: {s['why']['ur']}")
    out.append(f"[{lab}] FINAL ANSWER: {p.get('answer', '')}")
    if p.get("key_note"):
        out.append(f"[{lab}] NOTE ON BOOK KEY: {p['key_note']}")
    m = p.get("meaning")
    if m:
        out.append(f"[{lab}] MEANING: {_w(m)}")
        if isinstance(m, dict) and m.get("ur"):
            out.append(f"[{lab}] MEANING-UR: {m['ur']}")
    return "\n".join(out)


def chunks(it):
    """Groups of parts, each under CHUNK characters (a single long part goes alone)."""
    groups, cur, size = [], [], 0
    for p in it["parts"]:
        t = part_text(p)
        if cur and size + len(t) > CHUNK:
            groups.append(cur)
            cur, size = [], 0
        cur.append(p)
        size += len(t)
    if cur:
        groups.append(cur)
    return groups


def figure_png(it, parts):
    """One picture of the final figure each part draws (all steps' commands together), or None."""
    from PIL import Image, ImageDraw
    import preview_figure as pf
    drawn = [p for p in parts if any(s.get("draw") for s in p["steps"])]
    if not drawn:
        return None
    h = float(it.get("figure_h") or 60)
    panels = []
    for p in drawn:
        cmds = [c for s in p["steps"] for c in s.get("draw", [])]
        xs, ys = [0, 100], [0, h]
        for c in cmds:
            pts = c.get("p") or []
            if c["t"] in ("line", "poly", "dot", "text", "right"):
                xs += pts[0::2]
                ys += pts[1::2]
            elif c["t"] in ("circle", "arc"):
                xs += [c["c"][0] - c["r"], c["c"][0] + c["r"]]
                ys += [c["c"][1] - c["r"], c["c"][1] + c["r"]]
        x0, x1, y0, y1 = min(xs) - 4, max(xs) + 4, min(ys) - 4, max(ys) + 4
        img = Image.new("RGB", (int((x1 - x0) * pf.S), int((y1 - y0) * pf.S) + 20), (251, 252, 254))
        d = ImageDraw.Draw(img)
        sx, sy = pf.X, pf.Y
        pf.X = lambda x, x0=x0: (x - x0) * pf.S
        pf.Y = lambda y, y0=y0: (y - y0) * pf.S + 20
        try:
            for c in cmds:
                try:
                    pf.draw_cmd(d, c)
                except Exception:
                    pass
        finally:
            pf.X, pf.Y = sx, sy
        d.text((6, 4), f"OUR FIGURE, part [{p.get('label') or '-'}]", fill=(200, 40, 40))
        panels.append(img)
    w = max(i.width for i in panels)
    sheet = Image.new("RGB", (w, sum(i.height for i in panels)), "white")
    y = 0
    for i in panels:
        sheet.paste(i, (0, y))
        y += i.height
    if sheet.width > 1400:
        sheet = sheet.resize((1400, int(sheet.height * 1400 / sheet.width)))
    buf = io.BytesIO()
    sheet.save(buf, "PNG")
    return buf.getvalue()


def review(it, parts, pages, unit):
    import vertex_models
    imgs = [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode((PAGES / f"u{unit:02d}_p{p:02d}.png").read_bytes()).decode("ascii")}}
            for p in pages[:5]]
    fig = figure_png(it, parts)
    if fig:
        imgs.append({"inlineData": {"mimeType": "image/png", "data": base64.b64encode(fig).decode("ascii")}})
    ref = it["id"].removeprefix("c10-").replace("ex", "Exercise ").replace("rev", "Review Exercise ").replace("-q", " Q")
    ours = f"QUESTION: {it['question']}\n\n" + "\n\n".join(part_text(p) for p in parts)
    note = " The LAST image is the figure OUR board draws." if fig else ""
    labels = [q.get("label") or "-" for q in parts]
    if len(parts) < len(it["parts"]):
        note += (f" This check covers ONLY part(s) {', '.join(labels)} of the question; the other parts are checked"
                 " separately, so do not report them as missing.")
    body = {"contents": [{"role": "user", "parts": imgs + [{"text": PROMPT.format(ref=ref, unit=unit, fig_note=note, ours=ours)}]}],
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


_lock = threading.Lock()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--redo", action="store_true", help="review again even if already reviewed")
    a = ap.parse_args()
    _env()
    os.environ.setdefault("VERTEX_TIMEOUT", "180")
    units = [int(u) for u in a.units.split(",") if u] or list(range(1, 13))
    only = set(x for x in a.only.split(",") if x)
    report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
    audit = json.loads(AUDIT.read_text(encoding="utf-8"))
    jobs = []
    for u in units:
        for it in json.loads((ROOT / "data" / "book10" / f"unit{u:02d}.json").read_text(encoding="utf-8"))["items"]:
            if only and it["id"] not in only:
                continue
            if not a.redo and not only and report.get(it["id"], {}).get("ok") is not None:
                continue
            pages = audit.get(it["id"], {}).get("pages")
            if not pages:
                report[it["id"]] = {"ok": None, "error": "no pages known"}
                continue
            jobs.append((it, pages, u))

    def run(job):
        it, pages, u = job
        issues, ok, errs = [], True, []
        for parts in chunks(it):
            r = review(it, parts, pages, u)
            if r.get("ok") is None:
                errs.append(r.get("error", ""))
                continue
            ok = ok and bool(r["ok"]) and not r.get("issues")
            issues += r.get("issues") or []
        res = {"ok": None if errs else ok, "issues": issues}
        if errs:
            res["error"] = errs[0]
        with _lock:
            report[it["id"]] = res
            REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")
            print(f"{it['id']}: {'ok' if res['ok'] else ('ERROR ' + errs[0][:80] if errs else str(len(issues)) + ' issues')}", flush=True)

    with ThreadPoolExecutor(a.workers) as ex:
        list(ex.map(run, jobs))
    vals = list(report.values())
    print(f"reviewed {len(vals)}: ok {sum(1 for v in vals if v.get('ok'))}, with issues {sum(1 for v in vals if v.get('ok') is False)}, "
          f"not reviewed {sum(1 for v in vals if v.get('ok') is None)}", flush=True)


if __name__ == "__main__":
    main()
