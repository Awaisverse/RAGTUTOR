"""Turn the handwritten Class 11 notes (11th/*.pdf, page images in data/class11/pages/) into clean typed notes.

Stage 1 (read): the Vertex vision model writes each page out in full as Markdown with LaTeX maths. Nothing is left out:
headings, definitions, every line of working, tables, diagram labels, side notes. Only the handwriting is cleaned
(spelling of English words, layout). The maths is copied exactly as written; a line that looks like a slip in the notes is
kept as written and marked with a [check: ...] note, so nothing is silently changed.
Stage 2 (verify): the model compares its transcript with the same page image line by line and returns the corrected,
complete transcript (missing lines added, misread symbols fixed).
Output: data/class11/transcript/<page>.md (per page), then data/class11/notes/<exercise>.md (all pages of an exercise).

  python tools/transcribe_notes11.py [--stage read|verify|join|all] [--only ex1.1] [--workers 6]
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
PAGES = ROOT / "data" / "class11" / "pages"
TRANS = ROOT / "data" / "class11" / "transcript"
NOTES = ROOT / "data" / "class11" / "notes"

READ = """This image is one page of a student's handwritten mathematics notes (Class 11, Punjab textbook, Unit 1: Complex
Numbers, Exercise {ex}). Write the WHOLE page out as clean typed notes in Markdown, with all mathematics in LaTeX
($...$ inline, $$...$$ for displayed lines).

Rules:
* Leave out NOTHING written on the page: the date and day, unit and exercise headings, question numbers and labels
  ((i), (ii), ...), every question statement, every line of every solution in the same order, every definition, note,
  remark, "e.g.", table, arrow, box, tick, crossed answer, and every label of any diagram. One handwritten line of working
  becomes one typed line: do not merge, shorten, summarise or skip steps, even repeated or trivial ones.
* Keep the maths EXACTLY as written: the same numbers, signs, symbols, order of terms and steps. Do not correct, simplify or
  re-solve anything. If a line looks like a slip in the notes, copy it as written and add right after it
  `[check: <what looks wrong>]`.
* Clean only the handwriting: correct the spelling of English words (e.g. "Conjagate" -> "Conjugate"), use proper
  capitals and punctuation, and lay the page out neatly (headings with ##/###, question numbers in bold, two-column
  layouts as Markdown tables or one after the other).
* A diagram: describe it in a short block starting `[Figure: ...]` with every label, value and arrow it shows.
* Anything you cannot read: write your best reading followed by `[unclear]`.
* Page number or margin marks: put the page number as `<!-- page n -->` at the top if one is written.
Return only the Markdown."""

VERIFY = """The image is one page of handwritten mathematics notes. Below is a typed transcript of it. Check the transcript
against the page line by line, from the top of the page to the bottom:
* every handwritten line, heading, label, note, table cell and diagram label must be present, in the same order;
* every number, sign, exponent, fraction, root, subscript, letter and symbol must be exactly as handwritten
  (do NOT correct the maths: a slip in the notes stays, marked `[check: ...]`);
* nothing may be added that is not on the page, except `[check: ...]`, `[unclear]` and `[Figure: ...]` notes.
Return the corrected, complete transcript in the same Markdown + LaTeX style, and nothing else. If it is already
complete and exact, return it unchanged.

TRANSCRIPT:
{text}"""

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


def _call(png, prompt):
    import vertex_models
    body = {"contents": [{"role": "user", "parts": [
        {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(png.read_bytes()).decode("ascii")}},
        {"text": prompt}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 16000}}
    last = None
    for _ in range(3):
        try:
            out = vertex_models._post(body, os.environ.get("VERTEX_VISION_MODEL") or "gemini-4-argon")
            out = re.sub(r"^```(?:markdown|md)?\s*|\s*```\s*$", "", out.strip())
            if len(out) > 40:
                return out
        except Exception as exc:
            last = exc
    raise RuntimeError(f"no transcript for {png.name}: {last}")


def read_page(png):
    out = TRANS / (png.stem + ".read.md")
    if out.exists():
        return "cached"
    out.write_text(_call(png, READ.format(ex=png.stem.split("_")[0].removeprefix("ex"))), encoding="utf-8")
    return "read"


def verify_page(png):
    src = TRANS / (png.stem + ".read.md")
    out = TRANS / (png.stem + ".md")
    if out.exists() or not src.exists():
        return "cached" if out.exists() else "missing"
    out.write_text(_call(png, VERIFY.format(text=src.read_text(encoding="utf-8"))), encoding="utf-8")
    return "verified"


def join(only):
    NOTES.mkdir(parents=True, exist_ok=True)
    exs = sorted({p.stem.split("_")[0] for p in PAGES.glob("*.png")})
    for ex in exs:
        if only and ex not in only:
            continue
        pages = sorted(TRANS.glob(f"{ex}_p*.md"))
        pages = [p for p in pages if not p.name.endswith(".read.md")]
        body = [f"# Unit 1: Complex Numbers, Exercise {ex.removeprefix('ex')}", ""]
        for p in pages:
            n = int(p.stem.split("_p")[1])
            body += [f"<!-- source page {n} of the handwritten notes -->", p.read_text(encoding="utf-8").strip(), "", "---", ""]
        (NOTES / f"{ex}.md").write_text("\n".join(body), encoding="utf-8")
        print("wrote", NOTES / f"{ex}.md", f"({len(pages)} pages)")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--stage", default="all")
    ap.add_argument("--only", default="")
    ap.add_argument("--workers", type=int, default=6)
    a = ap.parse_args()
    _env()
    os.environ.setdefault("VERTEX_TIMEOUT", "240")
    TRANS.mkdir(parents=True, exist_ok=True)
    only = set(x for x in a.only.split(",") if x)
    pngs = [p for p in sorted(PAGES.glob("*.png")) if not only or p.stem.split("_")[0] in only]
    for stage, fn in (("read", read_page), ("verify", verify_page)):
        if a.stage in (stage, "all"):
            counts = {}
            with ThreadPoolExecutor(a.workers) as ex:
                for r in ex.map(fn, pngs):
                    counts[r] = counts.get(r, 0) + 1
            print(stage, counts, flush=True)
    if a.stage in ("join", "all"):
        join(only)


if __name__ == "__main__":
    main()
