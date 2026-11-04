"""Read the typed Class 11 Unit 1 solutions (data/class11/ref/unit01_kanwal_hasan.pdf, from MathCity, kept private): every
question statement word for word and its final answer, page by page, with the Vertex vision model.

  python tools/read_ref11.py           -> data/class11/ref/pages/*.png, data/class11/ref/read/*.json, data/class11/ref/questions.json
"""
import base64
import json
import os
import pathlib
import re
import sys
from concurrent.futures import ThreadPoolExecutor

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
from audit_questions10 import _env, _json  # noqa: E402

REF = ROOT / "data" / "class11" / "ref"
PDF = REF / "unit01_kanwal_hasan.pdf"
NAME = "kanwal"

PROMPT = """This is one page of a typed solutions book for Class 11 mathematics (Punjab/PECTAA), {chapter}.
For every question that STARTS or is SOLVED on this page, give:
* "exercise": e.g. "1.2" (from the heading in force; the page may continue an exercise from the previous page; null if not shown)
* "number": the question number, "part": the part label (i, ii, ...) or "",
* "statement": the question exactly as printed (word for word, maths in LaTeX), or "" if the statement is on an earlier page,
* "final": the final answer as printed at the end of the solution on this page (LaTeX), or "" if the answer is on a later page.
Return ONLY JSON: {"questions": [{"exercise": ..., "number": ..., "part": ..., "statement": ..., "final": ...}]}"""


def render(pdf_path=None, name=None):
    import pypdfium2 as pdfium
    out = REF / "pages" / (name or NAME)
    out.mkdir(parents=True, exist_ok=True)
    pdf = pdfium.PdfDocument(str(pdf_path or PDF))
    for k in range(len(pdf)):
        f = out / f"p{k + 1:02d}.png"
        if not f.exists():
            pdf[k].render(scale=2).to_pil().save(f)
    return sorted(out.glob("p*.png"))


def read(png):
    import vertex_models
    out = REF / "read" / png.parent.name / (png.stem + ".json")
    out.parent.mkdir(parents=True, exist_ok=True)
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))
    body = {"contents": [{"role": "user", "parts": [
        {"inlineData": {"mimeType": "image/png", "data": base64.b64encode(png.read_bytes()).decode("ascii")}}, {"text": PROMPT.replace("{chapter}", os.environ.get("REF_CHAPTER", "Chapter 1 Complex Numbers"))}]}],
        "generationConfig": {"temperature": 0.0, "maxOutputTokens": 12000, "responseMimeType": "application/json"}}
    for _ in range(3):
        try:
            d = _json(vertex_models._post(body, os.environ.get("VERTEX_VISION_MODEL") or "gemini-4-argon"))
            if "questions" in d:
                out.write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")
                return d
        except Exception:
            pass
    return {"questions": []}


def main():
    _env()
    os.environ.setdefault("VERTEX_TIMEOUT", "180")
    (REF / "read").mkdir(parents=True, exist_ok=True)
    name = sys.argv[1] if len(sys.argv) > 1 else NAME
    pdfs = sorted(REF.glob(f"{name}*.pdf")) if name != NAME else [PDF]
    pngs = []
    for k, f in enumerate(pdfs):
        pngs += [p for p in render(f, name) if p.name.startswith(f"p")] if len(pdfs) == 1 else []
    if len(pdfs) > 1:                                   # one PDF per exercise: pages named <exercise>_pNN
        import pypdfium2 as pdfium
        out = REF / "pages" / name
        out.mkdir(parents=True, exist_ok=True)
        for f in pdfs:
            doc = pdfium.PdfDocument(str(f))
            for k in range(len(doc)):
                g = out / f"{f.stem.split('_')[-1]}_p{k + 1:02d}.png"
                if not g.exists():
                    doc[k].render(scale=2).to_pil().save(g)
        pngs = sorted(out.glob("*.png"))
    with ThreadPoolExecutor(8) as ex:
        pages = list(ex.map(read, pngs))
    merged, cur_ex = {}, None
    for png, d in zip(pngs, pages):
        for q in d.get("questions", []):
            cur_ex = q.get("exercise") or cur_ex
            num = re.sub(r"[^0-9]", "", str(q.get("number") or ""))
            if not cur_ex or not num:
                continue
            part = re.sub(r"[().\s]", "", str(q.get("part") or "")).lower()
            e = merged.setdefault(f"{cur_ex}|{num}|{part}", {"statement": "", "final": "", "pages": []})
            if q.get("statement") and not e["statement"]:
                e["statement"] = q["statement"]
            if q.get("final"):
                e["final"] = q["final"]                   # the last page's answer is the final one
            e["pages"].append(png.stem)
    (REF / f"questions_{name}.json").write_text(json.dumps(merged, ensure_ascii=False, indent=1), encoding="utf-8")
    print(len(merged), "questions/parts")


if __name__ == "__main__":
    main()
