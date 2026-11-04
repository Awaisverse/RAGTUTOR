"""Render the typed Class 11 notes (data/class11/notes/*.md) as clean pages: one HTML file per exercise plus a combined
one, with KaTeX for the maths, and a PDF of each printed by headless Chrome.

  python tools/render_notes11.py            -> data/class11/notes/html/*.html and data/class11/notes/pdf/*.pdf
"""
import html
import pathlib
import re
import subprocess

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
NOTES = ROOT / "data" / "class11" / "notes"
OUT_HTML = NOTES / "html"
OUT_PDF = NOTES / "pdf"
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

PAGE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.css">
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/katex.min.js"></script>
<script defer src="https://cdn.jsdelivr.net/npm/katex@0.16.11/dist/contrib/auto-render.min.js"></script>
<style>
  :root {{ --ink:#1b1f2a; --muted:#5b6475; --line:#e3e6ee; --accent:#4F46E5; --warn:#9a3412; --warnbg:#fff7ed; --bg:#ffffff; }}
  body {{ background:var(--bg); color:var(--ink); font:16px/1.65 "Segoe UI", system-ui, sans-serif; margin:0; }}
  main {{ max-width:820px; margin:0 auto; padding:32px 20px 64px; }}
  h1 {{ font-size:1.7rem; border-bottom:3px solid var(--accent); padding-bottom:.3em; }}
  h2 {{ font-size:1.3rem; color:var(--accent); margin-top:1.6em; }}
  h3 {{ font-size:1.1rem; margin-top:1.4em; }}
  hr {{ border:0; border-top:1px dashed var(--line); margin:2em 0; }}
  table {{ border-collapse:collapse; margin:1em 0; }} td, th {{ border:1px solid var(--line); padding:.35em .7em; vertical-align:top; }}
  .katex-display {{ margin:.5em 0; overflow-x:auto; overflow-y:hidden; }}
  .check {{ background:var(--warnbg); color:var(--warn); border-radius:4px; padding:0 .3em; font-size:.92em; }}
  .fig {{ background:#f4f6fb; border-left:3px solid var(--accent); padding:.3em .7em; display:block; margin:.6em 0; font-size:.95em; }}
  .src {{ color:var(--muted); font-size:.8rem; margin-top:2em; }}
  .toc a {{ color:var(--accent); }}
  @media print {{ main {{ padding:0; }} h2, h3 {{ break-after:avoid; }} .katex-display {{ break-inside:avoid; }} }}
</style></head>
<body><main>
{body}
</main>
<script>
document.addEventListener("DOMContentLoaded", () => renderMathInElement(document.body, {{
  delimiters: [{{left: "$$", right: "$$", display: true}}, {{left: "$", right: "$", display: false}}], throwOnError: false }}));
</script>
</body></html>"""


def to_html(md_text):
    # keep the maths away from the Markdown parser: it would eat underscores and backslashes
    maths = []

    def keep(m):
        chunk, note = m.group(0), ""
        # a "[check: ...]" written inside the maths becomes a note after it, with its own bits of maths kept as maths
        c = re.search(r"(\\quad\s*|\\qquad\s*)?\\text\{\s*\[check:(.*)\]\s*\}", chunk, re.S)
        if c:
            inner = re.sub(r"\}\s*(.*?)\s*\\text\{", lambda k: f" ${k.group(1)}$ ", c.group(2), flags=re.S)
            note = f" [check:{inner}]"
            chunk = chunk[:c.start()] + chunk[c.end():]
        maths.append(chunk)
        return f"@@MATH{len(maths) - 1}@@{note}"
    t = re.sub(r"\$\$.+?\$\$|\$[^$\n]+?\$", keep, md_text, flags=re.S)
    t = re.sub(r"<!--\s*source page (\d+).*?-->", r'<p class="src">Handwritten page \1</p>', t)
    t = re.sub(r"<!--.*?-->", "", t, flags=re.S)
    h = markdown.markdown(t, extensions=["tables"])
    h = re.sub(r"`?\[check:(.*?)\]`?", lambda m: f'<span class="check">Check: {m.group(1).strip()}</span>', h)
    h = re.sub(r"<code>(.*?)</code>", r"\1", h)
    h = re.sub(r"\[Figure:(.*?)\]", lambda m: f'<span class="fig">Figure: {m.group(1).strip()}</span>', h, flags=re.S)
    h = re.sub(r"@@MATH(\d+)@@", lambda m: html.escape(maths[int(m.group(1))], quote=False), h)
    return h


def main():
    OUT_HTML.mkdir(parents=True, exist_ok=True)
    OUT_PDF.mkdir(parents=True, exist_ok=True)
    files = sorted(NOTES.glob("ex*.md"))
    parts = []
    for f in files:
        md_text = f.read_text(encoding="utf-8")
        title = md_text.splitlines()[0].lstrip("# ").strip()
        body = to_html(md_text)
        (OUT_HTML / f"{f.stem}.html").write_text(PAGE.format(title=html.escape(title), body=body), encoding="utf-8")
        parts.append((f.stem, title, body))
    toc = "<ul class='toc'>" + "".join(f"<li><a href='#{s}'>{html.escape(t)}</a></li>" for s, t, _ in parts) + "</ul>"
    allbody = "<h1>Class 11 Mathematics: Unit 1, Complex Numbers (typed notes)</h1>" + toc + "".join(
        f"<section id='{s}'>{b}</section>" for s, _, b in parts)
    (OUT_HTML / "unit1_all.html").write_text(PAGE.format(title="Unit 1 Complex Numbers notes", body=allbody), encoding="utf-8")
    for h in sorted(OUT_HTML.glob("*.html")):
        pdf = OUT_PDF / (h.stem + ".pdf")
        subprocess.run([CHROME, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", "--virtual-time-budget=15000",
                        f"--print-to-pdf={pdf}", h.as_uri()], check=False, capture_output=True, timeout=180)
        print("wrote", h.name, "and", pdf.name if pdf.exists() else "(no PDF)")


if __name__ == "__main__":
    main()
