"""Check that every Class 10 question we solve and show in "Browse the book" is word-for-word the textbook's question.

Stage 1 (read): the Vertex AI vision model transcribes the QUESTION statements (instruction and every part, not the
solutions) printed on each page image in data/class10/pages/. Cached in data/class10/transcript/ (private, not in git).
Stage 2 (compare): for each of our items, the book's transcription of the same question (matched by exercise and
question number) is compared with ours, part by part, by the Vertex model. Differences go to data/class10/audit.json.

  python tools/audit_questions10.py [--stage read|compare|both] [--units 2,3] [--workers 6]
Nothing is changed in the book: the report is reviewed against the page images, then the sources are corrected.
"""
import argparse
import base64
import json
import os
import pathlib
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
PAGES = ROOT / "data" / "class10" / "pages"
TRANS = ROOT / "data" / "class10" / "transcript"
REPORT = ROOT / "data" / "class10" / "audit.json"

READ = """This is one page of a Class 10 mathematics solutions book (Punjab textbook, Unit {unit}). The page prints the
textbook's QUESTIONS, each followed by its worked solution. Transcribe ONLY the question statements, exactly as printed:
the exercise or review heading, the question number, the instruction sentence, and every part with its label. Do NOT
transcribe solutions, working, answers, page headers or footers. For multiple-choice questions include the options
(a) (b) (c) (d) exactly. Write maths in LaTeX inside $...$. Copy every number, sign, variable and word exactly.

Return ONLY JSON:
{{"questions": [{{"heading": "<e.g. Exercise 2.1, or Review Exercise 2; the heading in force for this question, carried
                 from the page if it is above>",
                 "number": "<question number, e.g. 4; null if this page starts in the middle of a question whose number
                 is on an earlier page>",
                 "instruction": "<the instruction sentence, or empty>",
                 "parts": [{{"label": "<i, ii, a, ... or empty>", "text": "<the part as printed>"}}]}}]}}
If the page has no question statement, return {{"questions": []}}."""

COMPARE = """Two transcriptions of the SAME textbook question are below: BOOK (read from the printed page) and OURS (what the
tutor app shows and solves). Decide whether OURS states exactly the same question as BOOK.

Count as a DIFFERENCE: any number, sign, exponent, variable, operator, fraction, root, angle, unit, multiple-choice
option, missing or extra part, wrong part label order, or an instruction that asks for something different (e.g. "factorize"
vs "solve", "find x" vs "find y", "in radians" vs "in degrees").
Do NOT count: LaTeX spelling (\\dfrac vs \\frac, spaces, braces, $ placement), typography, punctuation, capitals, or
small wording that asks for the same thing. If BOOK is clearly a misreading (garbled, cut off by the page edge), say so
in "book_unclear" instead of reporting it as a difference.

BOOK:
{book}

OURS:
{ours}

Return ONLY JSON: {{"same": true|false, "differences": [{{"part": "<label or 'instruction'>", "book": "...", "ours": "...",
"what": "<short description>"}}], "book_unclear": "<empty, or what could not be read>"}}"""

VISION = """The attached image(s) are the page(s) of a Class 10 mathematics solutions book that print question {ref}
(Unit {unit}). Below is the question as our tutor app states it. Look at the printed QUESTION (not the solution) and any
figure, diagram, table or graph that belongs to it, and check OUR text against the page:
* every number, sign, exponent, variable, operator, angle, length, unit and multiple-choice option;
* every value OUR text gives "from the figure" or in brackets must be exactly what the figure/table shows;
* every part present, with the same label; the instruction asks for the same thing.
Ignore LaTeX spelling, spacing, punctuation and capitals. Values that the page omits but the printed solution
clearly uses may be added in brackets: that is fine if they match the solution.

OUR TEXT:
{ours}

Return ONLY JSON: {{"ok": true|false, "problems": [{{"part": "...", "page_shows": "...", "ours": "...", "what": "..."}}]}}"""

_lock = threading.Lock()


def vision_check(it, pages, unit):
    import vertex_models
    parts = [{"inlineData": {"mimeType": "image/png", "data": base64.b64encode((PAGES / f"u{unit:02d}_p{p:02d}.png").read_bytes()).decode("ascii")}}
             for p in pages[:4]]
    ref = it["id"].removeprefix("c10-").replace("ex", "Exercise ").replace("rev", "Review Exercise ").replace("-q", " Q")
    parts.append({"text": VISION.format(ref=ref, unit=unit, ours=ours_text(it))})
    body = {"contents": [{"role": "user", "parts": parts}],
            "generationConfig": {"temperature": 0.0, "maxOutputTokens": 8000, "responseMimeType": "application/json"}}
    err = "no answer"
    for _ in range(3):
        try:
            out = _json(vertex_models._post(body, os.environ.get("VERTEX_VISION_MODEL") or "gemini-4-argon"))
            if "ok" in out:
                return out
        except Exception as exc:
            err = str(exc)
    return {"ok": None, "error": err}


def run_vision(units, workers, only):
    path = ROOT / "data" / "class10" / "audit_vision.json"
    report = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    audit = json.loads(REPORT.read_text(encoding="utf-8"))
    jobs = []
    for u in units:
        unit = json.loads((ROOT / "data" / "book10" / f"unit{u:02d}.json").read_text(encoding="utf-8"))
        for it in unit["items"]:
            if (only and it["id"] not in only) or (not only and report.get(it["id"], {}).get("ok") is not None):
                continue
            pages = audit.get(it["id"], {}).get("pages")
            if pages:
                jobs.append((it, pages, u))

    def run(job):
        r = vision_check(*job)
        with _lock:
            report[job[0]["id"]] = r
            path.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(run, jobs))
    print(f"vision-checked {len(report)}: ok {sum(1 for v in report.values() if v.get('ok'))}, "
          f"problems {sum(1 for v in report.values() if v.get('ok') is False)}, "
          f"unchecked {sum(1 for v in report.values() if v.get('ok') is None)}", flush=True)


def _env():
    env = ROOT / ".env.local"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                if v.strip() and k.strip() not in os.environ:
                    os.environ[k.strip()] = v.strip().strip('"').strip("'")


def _json(text):
    m = re.search(r"\{.*\}", text or "", re.S)
    if not m:
        return {}
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError:                      # LaTeX with single backslashes: \sqrt is not a JSON escape
        return json.loads(re.sub(r'(?<!\\)\\(?![\\"])', r"\\\\", m.group(0)))


def read_page(png):
    import vertex_models
    out = TRANS / (png.stem + ".json")
    if out.exists():
        return "cached"
    unit = int(png.stem[1:3])
    body = {"contents": [{"role": "user", "parts": [
        {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(png.read_bytes()).decode("ascii")}},
        {"text": READ.format(unit=unit)}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 12000, "responseMimeType": "application/json"}}
    last = None
    for _ in range(3):
        try:
            data = _json(vertex_models._post(body, os.environ.get("VERTEX_VISION_MODEL") or "gemini-4-argon"))
            if "questions" in data:
                out.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
                return "read"
        except Exception as exc:
            last = exc
    print("  could not read", png.name, last, flush=True)
    return "failed"


def _ref_of_heading(heading, unit):
    h = (heading or "").lower()
    if "review" in h:
        return f"rev{unit}"
    m = re.search(r"(\d+)\s*\.\s*(\d+)", h)
    return f"ex{m.group(1)}.{m.group(2)}" if m else None


def book_questions(unit):
    """{"ex2.1-q4": {"instruction", "parts", "pages"}} for one unit, joining questions continued over pages."""
    qs, last, heading = {}, None, None
    for f in sorted(TRANS.glob(f"u{unit:02d}_p*.json")):
        page = int(f.stem.split("_p")[1])
        for q in json.loads(f.read_text(encoding="utf-8")).get("questions", []):
            new = _ref_of_heading(q.get("heading"), unit)
            num = re.sub(r"[^0-9]", "", str(q.get("number") or ""))
            if new and new != heading and not num:
                num = "1"                                 # a new exercise whose only question has no printed number
            heading = new or heading                      # a heading stays in force over later pages
            ref = heading
            for p in q.get("parts") or []:
                p["label"] = re.sub(r"[().\s]", "", str(p.get("label") or "")).lower()
            if num and ref:
                key = f"{ref}-q{num}"
            elif last:
                key = last                                # continues the previous page's question
            else:
                continue
            e = qs.setdefault(key, {"instruction": "", "parts": [], "pages": []})
            if q.get("instruction") and not e["instruction"]:
                e["instruction"] = q["instruction"]
            seen = {p["label"] for p in e["parts"] if p.get("label")}
            for p in q.get("parts") or []:
                if not p.get("label") or p["label"] not in seen:
                    e["parts"].append({"label": p.get("label", ""), "text": p.get("text", "")})
            if page not in e["pages"]:
                e["pages"].append(page)
            last = key
    return qs


def ours_text(it):
    lines = [f"Question: {it['question']}"]
    for p in it["parts"]:
        if p.get("label") or p.get("prompt"):
            lines.append(f"({p.get('label', '')}) {p.get('prompt', '')}")
    return "\n".join(lines)


def book_text(b):
    return "\n".join([f"Instruction: {b['instruction']}"] + [f"({p['label']}) {p['text']}" for p in b["parts"]])


def compare(it, b):
    import vertex_models
    prompt = COMPARE.format(book=book_text(b), ours=ours_text(it))
    for _ in range(3):
        try:
            out = _json(vertex_models.generate([{"role": "user", "content": prompt}], max_new_tokens=4000, temperature=0.0,
                                               model=os.environ.get("VERTEX_MODEL") or "gemini-4-argon"))
            if "same" in out:
                return out
        except Exception as exc:
            err = str(exc)
    return {"same": None, "error": err if "err" in dir() else "no answer"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="both")
    ap.add_argument("--units", default="")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--only", default="", help="comma-separated item ids to (re)compare")
    a = ap.parse_args()
    _env()
    units = [int(u) for u in a.units.split(",") if u] or list(range(1, 13))
    TRANS.mkdir(parents=True, exist_ok=True)
    if a.stage in ("read", "both"):
        pngs = [p for p in sorted(PAGES.glob("u*_p*.png")) if int(p.stem[1:3]) in units]
        counts = {}
        with ThreadPoolExecutor(a.workers) as ex:
            for r in ex.map(read_page, pngs):
                counts[r] = counts.get(r, 0) + 1
        print("read pages:", counts, flush=True)
    if a.stage == "vision":
        run_vision(units, a.workers, set(x for x in a.only.split(",") if x))
    if a.stage in ("compare", "both"):
        report = json.loads(REPORT.read_text(encoding="utf-8")) if REPORT.exists() else {}
        only = set(x for x in a.only.split(",") if x)
        jobs = []
        for u in units:
            book = book_questions(u)
            unit = json.loads((ROOT / "data" / "book10" / f"unit{u:02d}.json").read_text(encoding="utf-8"))
            for it in unit["items"]:
                if only and it["id"] not in only:
                    continue
                if not only and it["id"] in report and report[it["id"]].get("same") is not None:
                    continue
                key = it["id"].removeprefix("c10-")
                if key not in book:
                    report[it["id"]] = {"same": None, "error": "question not found in the page transcripts"}
                    continue
                jobs.append((it, book[key]))

        def run(job):
            it, b = job
            r = compare(it, b)
            r["pages"] = b["pages"]
            with _lock:
                report[it["id"]] = r
                REPORT.write_text(json.dumps(report, ensure_ascii=False, indent=1), encoding="utf-8")

        with ThreadPoolExecutor(a.workers) as ex:
            list(ex.map(run, jobs))
        bad = {k: v for k, v in report.items() if v.get("same") is False}
        missing = [k for k, v in report.items() if v.get("same") is None]
        print(f"compared {len(report)}: same {sum(1 for v in report.values() if v.get('same'))}, "
              f"different {len(bad)}, not compared {len(missing)}", flush=True)


if __name__ == "__main__":
    main()
