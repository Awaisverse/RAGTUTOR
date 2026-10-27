"""Math tutor server: RAG over the solved book, live solving, and photo-of-question support.

Routes
  GET  /              the whiteboard UI
  GET  /api/items     every solved question (summary)
  GET  /api/item/<id> full solution for one question
  POST /api/ask       {"question": "..."} -> retrieval hits + mode ("book" or "none")
  POST /api/solve     {"question": "..."} -> the local generator solves it, grounded in retrieved examples
  POST /api/photo     multipart "image" -> the local vision model reads the photo (exercise, number, part),
                      then resolves that part from the book or solves it live

Everything runs locally with Hugging Face models. No API key is used.
  NO_EMBEDDINGS=1     skip the embedding model (TF-IDF only)
  GEN_MODEL / GEN_ADAPTER / VISION_MODEL   see local_models.py

Run:  python server.py
"""
import io
import json
import os
import pathlib
import re
import sys

from flask import Flask, jsonify, request, send_from_directory

ROOT = pathlib.Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import local_models  # noqa: E402
import modelsolve  # noqa: E402
import mathtext  # noqa: E402
import rag  # noqa: E402
import solvers  # noqa: E402
from solvers.common import labels, part_markers  # noqa: E402
from prompts import READ_PROMPT  # noqa: E402

GEN = ROOT / "data" / "generated"
BOOK = ROOT / "data" / "book"
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = Flask(__name__, static_folder=str(ROOT / "static"), static_url_path="/static")


def load_items():
    items = []
    for path in sorted(BOOK.glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            it["unit_title"] = unit["title"]
            items.append(it)
    return items


ITEMS = load_items()
BY_ID = {it["id"]: it for it in ITEMS}
INDEX = rag.Index(rag.load_chunks(), use_embeddings=os.environ.get("NO_EMBEDDINGS") != "1")


def summary(item):
    return {
        "id": item["id"], "unit": item["unit"], "unit_title": item["unit_title"],
        "exercise": item.get("exercise"), "number": item["number"], "kind": item["kind"],
        "page": item["page"], "question": item["question"],
    }


def _json_from(text):
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in model output")
    return json.loads(m.group(0))


# ---------- basic routes ----------

@app.get("/")
def index():
    return send_from_directory(ROOT / "static", "index.html")


@app.get("/api/items")
def items():
    return jsonify([summary(it) for it in ITEMS])


@app.get("/api/item/<item_id>")
def item(item_id):
    it = BY_ID.get(item_id)
    if not it:
        return jsonify({"error": "not found"}), 404
    return jsonify(it)


def similar_examples(question, k=3):
    """Stored questions that are about the same topic. They are NOT answers: their numbers differ from the student's."""
    hits = INDEX.search(question, k=k)
    return [{**summary(BY_ID[h["id"]]), "part": h["part"], "cos": h["cos"], "lex": h["lex"]} for h in hits] if INDEX.is_confident(hits) else []


def resolve(question, focus_part=None):
    """Answer THIS question. Order: a stored solution only if it is the same question, then the solver engine, then the
    trained model, and otherwise a clearly labelled similar example that is never presented as the answer."""
    q = question.strip()
    for it in ITEMS:                                   # 1. exactly a stored question (same numbers, same instruction)
        same, part = mathtext.same_question(q, it)
        if same:
            return {"mode": "book", "item": it, "part_index": part or 0}
    solved = solvers.solve(q)                          # 2. the solver engine: reads the numbers and solves this question
    if solved:
        return {"mode": "solved", "item": solved, "part_index": 0}
    error = None
    if local_models.generator_available():             # 3. the trained model (its steps are checked with sympy afterwards)
        try:
            sol = live_solve(q, focus_part=focus_part)
            return {"mode": "model", "item": sol, "part_index": 0}
        except Exception as exc:
            error = str(exc)
    similar = similar_examples(q)                      # 4. nothing could solve it: show related examples, labelled as such
    return {"mode": "example_only" if similar else "none", "similar": similar, "error": error,
            "message": "I could not solve this exact question here. The examples below are about the same topic but use different numbers, "
                       "so they are not the answer to your question." if similar else "I could not recognise this question."}


@app.post("/api/answer")
def answer():
    q = (request.get_json(silent=True) or {}).get("question", "")
    if not q.strip():
        return jsonify({"error": "empty question"}), 400
    return jsonify(resolve(q))


@app.post("/api/ask")
def ask():
    """Search only: which stored questions are related. 'book' means one of them is exactly this question."""
    q = (request.get_json(silent=True) or {}).get("question", "")
    results = similar_examples(q)
    exact = any(mathtext.same_question(q, it)[0] for it in ITEMS)
    return jsonify({"mode": "book" if exact else "none", "results": results, "live_available": local_models.generator_available()})


# ---------- live solver ----------


_EX = {}


def _example_pool():
    """Solved book examples, one part each (the shape the model was trained on), with their own TF-IDF index."""
    if not _EX:
        items = modelsolve.explode_all(ITEMS)
        _EX["by_id"] = {it["id"]: it for it in items}
        _EX["index"] = rag.Index([c for it in items for c in rag.chunk_item(it)], use_embeddings=False)
    return _EX["index"], _EX["by_id"]


def live_solve(question, focus_part=None):
    """Solve with the trained model: one part at a time, each reply checked with sympy and retried when a check fails."""
    index, by_id = _example_pool()
    if focus_part:
        pieces = part_markers(question)
        if len(pieces) >= 3 and focus_part in labels(len(pieces) - 1):
            question = f"{pieces[0]} {pieces[labels(len(pieces) - 1).index(focus_part) + 1]}".strip()
    sol = modelsolve.solve_question(question, lambda q: modelsolve.examples_text(index, by_id, q), attempts=3, max_new_tokens=2500)
    if sol is None:
        raise ValueError("the model did not return a usable solution")
    sol["unit"] = 0
    sol["unit_title"] = "Live"
    GEN.mkdir(parents=True, exist_ok=True)
    slug = re.sub(r"[^a-z0-9]+", "-", sol.get("id", "solution").lower()).strip("-") or "solution"
    (GEN / f"{slug}.json").write_text(json.dumps(sol, ensure_ascii=False, indent=1), encoding="utf-8")
    return sol


@app.post("/api/solve")
def solve():
    if not local_models.generator_available():
        return jsonify({"error": "Generator model not found. Download it to models/ (see docs/PLAN.md)."}), 503
    q = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not q:
        return jsonify({"error": "empty question"}), 400
    try:
        return jsonify(live_solve(q))
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"model output was not valid JSON: {exc}"}), 502
    except Exception as exc:  # API / network errors from the SDK
        return jsonify({"error": f"live solver failed: {exc}"}), 502


# ---------- photo of a question ----------


def read_photo(image_bytes):
    from PIL import Image
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    raw = local_models.read_image(img, READ_PROMPT + "\n\nRead this question photo as instructed.")
    return _json_from(raw)


def _find_by_number(exercise, number):
    """Exact lookup of a printed exercise question, e.g. exercise 1.3, question 2."""
    if number is None:
        return None
    wanted = _norm_exercise(exercise) if exercise else None
    for it in ITEMS:
        if it["kind"] not in ("exercise", "review"):
            continue
        if str(it.get("number")) == str(number) and (wanted is None or _norm_exercise(it.get("exercise")) == wanted):
            return it
    return None


def _norm_exercise(label):
    """'Exercise 1.3' and '1.3' agree; 'Review Exercise 1' and 'Review 1' agree."""
    return re.sub(r"\s+|exercise", "", str(label or "").lower())


def _part_index(item, label):
    """Index of the part with this label. Single-part items always match part 0; None if not found."""
    if len(item["parts"]) == 1 or not label:
        return 0
    for i, p in enumerate(item["parts"]):
        if (p.get("label") or "").strip().lower() == label.strip().lower():
            return i
    return None


@app.post("/api/photo")
def photo():
    if not local_models.vision_available():
        return jsonify({"error": "Vision model not found. Download it to models/ (see docs/PLAN.md)."}), 503
    f = request.files.get("image")
    if not f:
        return jsonify({"error": "no image uploaded (field name must be 'image')"}), 400
    if f.mimetype not in IMAGE_TYPES:
        return jsonify({"error": "only JPEG, PNG or WEBP images are accepted"}), 400
    raw = f.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        return jsonify({"error": "image is larger than 8 MB"}), 413

    try:
        read = read_photo(raw)
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"could not read the photo: {exc}"}), 502

    if not read.get("readable") or not read.get("question"):
        return jsonify({"error": "No math question found in the photo.", "detected": read}), 422

    exercise, number = read.get("exercise"), read.get("number")
    part = (read.get("part_requested") or "").strip()
    detected = {"exercise": exercise, "number": number, "parts": read.get("parts", []),
                "part_requested": part, "confidence": read.get("confidence"), "notes": read.get("notes", "")}

    # 1) The printed exercise and question number identify a stored question exactly.
    book = _find_by_number(exercise, number)
    if book is not None:
        idx = _part_index(book, part)
        if idx is None:
            idx = 0
            detected["notes"] += f" Part ({part}) not found in the book; showing the first part."
        return jsonify({"resolution": "book_by_number", "detected": detected, "item": book,
                        "part_index": idx, "part_label": book["parts"][idx].get("label", "")})

    # 2) Otherwise answer the question that was read: stored solution only if it is the same question, then the solver
    #    engine, then the model. A merely similar example is returned as such, never as the answer.
    res = resolve(read["question"], focus_part=part or None)
    if res["mode"] in ("book", "solved", "model"):
        item = res["item"]
        idx = res.get("part_index", 0)
        return jsonify({"resolution": res["mode"], "detected": detected, "item": item,
                        "part_index": idx, "part_label": item["parts"][idx].get("label", "")})
    return jsonify({"resolution": res["mode"], "detected": detected, "similar": res.get("similar", []), "message": res["message"]})


if __name__ == "__main__":
    print(f"loaded {len(ITEMS)} solved questions, {len(INDEX.chunks)} chunks")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5057)), debug=False)
