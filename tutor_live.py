"""The two jobs that need a neural model: solve a question the engine cannot, and read a photo of a question.

Kept apart from server.py so the web app (which runs on Vercel without torch) and the hosted model service
(service/app.py, which has the models) share one implementation. Only the service imports torch, and only when called.
"""
import io
import json
import pathlib
import re

import modelsolve
import rag
from prompts import READ_PROMPT
from solvers.common import labels, part_markers

ROOT = pathlib.Path(__file__).resolve().parent
BOOK = ROOT / "data" / "book"


def load_items():
    items = []
    for path in sorted(BOOK.glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            it["unit_title"] = unit["title"]
            items.append(it)
    return items


_EX = {}


def _example_pool():
    """Solved book examples, one part each (the shape the model was trained on), with their own TF-IDF index."""
    if not _EX:
        items = modelsolve.explode_all(load_items())
        _EX["by_id"] = {it["id"]: it for it in items}
        _EX["index"] = rag.Index([c for it in items for c in rag.chunk_item(it)], use_embeddings=False)
    return _EX["index"], _EX["by_id"]


def live_solve(question, focus_part=None, attempts=3, generate=None):
    """Solve with a model: one part at a time, each reply checked with sympy and retried when a check fails.
    `generate` defaults to the local model; the web app passes the Gemini client instead."""
    index, by_id = _example_pool()
    if focus_part:
        pieces = part_markers(question)
        if len(pieces) >= 3 and focus_part in labels(len(pieces) - 1):
            question = f"{pieces[0]} {pieces[labels(len(pieces) - 1).index(focus_part) + 1]}".strip()
    sol = modelsolve.solve_question(question, lambda q: modelsolve.examples_text(index, by_id, q), attempts=attempts, max_new_tokens=2500, generate=generate)
    if sol is None:
        raise ValueError("the model did not return a usable solution")
    sol["unit"] = 0
    sol["unit_title"] = "Live"
    return sol


def _json_from(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    return json.loads(m.group(0))


def read_photo(image_bytes):
    """The vision model reads the picture: exercise, question number, parts, and the question as LaTeX. It solves nothing."""
    import local_models
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img.thumbnail((1600, 1600))                         # bigger pictures only cost time; the text stays readable
    raw = local_models.read_image(img, READ_PROMPT + "\n\nRead this question photo as instructed.")
    return _json_from(raw)
