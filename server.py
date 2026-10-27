"""Math tutor web app: the book, the solver engine, and (through a model service) the trained model and photo reading.

Routes
  GET  /              the whiteboard UI (public/index.html)
  GET  /api/items     every solved question (summary)
  GET  /api/item/<id> full solution for one question
  GET  /api/status    which abilities this deployment has: engine, model, photo
  POST /api/answer    {"question": "..."} -> the answer to THAT question: book, engine, model or labelled examples
  POST /api/ask       {"question": "..."} -> retrieval hits only
  POST /api/solve     {"question": "..."} -> the trained model solves it (needs the model)
  POST /api/photo     multipart "image" -> the vision model reads the question as LaTeX, then it is answered like typed text

Where the models run
  MODEL_SERVICE_URL   a hosted service (service/app.py): the Vercel setup, where this app has no GPU and no torch
  otherwise           local models if models/ holds them (local_models.py), else the engine and book still work alone

This file imports no torch, numpy or scikit-learn, so it fits in a serverless function.
Run locally:  python server.py
"""
import importlib.util
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
import mathtext  # noqa: E402
import modelsolve  # noqa: E402
import rag  # noqa: E402
import remote_models  # noqa: E402
import solvers  # noqa: E402
import tutor_live  # noqa: E402
import vertex_models  # noqa: E402

MAX_IMAGE_BYTES = 4 * 1024 * 1024          # Vercel rejects larger request bodies; the page shrinks photos before sending
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = Flask(__name__, static_folder=str(ROOT / "public"), static_url_path="")


ITEMS = tutor_live.load_items()
BY_ID = {it["id"]: it for it in ITEMS}


def _embeddings_wanted():
    """The embedding model needs torch: off on Vercel and wherever sentence-transformers is not installed."""
    if os.environ.get("NO_EMBEDDINGS") == "1" or os.environ.get("VERCEL"):
        return False
    return importlib.util.find_spec("sentence_transformers") is not None


INDEX = rag.Index(rag.load_chunks(), use_embeddings=_embeddings_wanted())


def summary(item):
    return {
        "id": item["id"], "unit": item["unit"], "unit_title": item["unit_title"],
        "exercise": item.get("exercise"), "number": item["number"], "kind": item["kind"],
        "page": item["page"], "question": item["question"],
    }


# ---------- basic routes ----------

@app.get("/")
def index():
    return send_from_directory(ROOT / "public", "index.html")


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


def only_part(item, index):
    """The student asked for ONE part: return the item cut down to that part, question = the stem plus that part's text,
    so the board and the explanation show just what was asked. The part's label is kept in `part_label`."""
    if len(item["parts"]) < 2 or index is None:
        return item
    label = item["parts"][index].get("label") or str(index + 1)
    cut = modelsolve.explode(item)[index]
    return {**cut, "id": item["id"], "part_label": label}


def resolve(question, focus_part=None):
    """Answer THIS question. Order: a stored solution only if it is the same question, then the solver engine, then the
    trained model, and otherwise a clearly labelled similar example that is never presented as the answer."""
    q = question.strip()
    for it in ITEMS:                                   # 1. exactly a stored question (same numbers, same instruction)
        same, part = mathtext.same_question(q, it)
        if same:                                       # a part asked alone is answered alone; the whole question shows every part
            return {"mode": "book", "item": only_part(it, part), "part_index": 0}
    solved = solvers.solve(q)                          # 2. the solver engine: reads the numbers and solves this question
    if solved:
        return {"mode": "solved", "item": solved, "part_index": 0}
    error = None
    if model_mode():                                   # 3. the model (its steps are checked with sympy afterwards)
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
    return jsonify({"mode": "book" if exact else "none", "results": results, "live_available": model_mode() is not None})


# ---------- the models: Gemini, a hosted service, or local ----------


def _backend(kind):
    """Which backend does `kind` ("model" or "vision") use? MODEL_BACKEND=vertex|service|local forces one; otherwise the
    first one that is set up, in that order. None means only the engine and the book are available."""
    forced = os.environ.get("MODEL_BACKEND", "").strip().lower()
    ready = {"vertex": vertex_models.configured(), "service": remote_models.configured(),
             "local": local_models.generator_available() if kind == "model" else local_models.vision_available()}
    if forced:
        return forced if ready.get(forced) else None
    return next((name for name in ("vertex", "service", "local") if ready[name]), None)


def model_mode():
    return _backend("model")


def vision_mode():
    return _backend("vision")


def live_solve(question, focus_part=None):
    """Solve with the model: one part at a time, each reply checked with sympy and retried when a check fails."""
    mode = model_mode()
    if mode == "vertex":
        return tutor_live.live_solve(question, focus_part, generate=vertex_models.generate)
    if mode == "service":
        return remote_models.solve(question, focus_part)
    if mode == "local":
        return tutor_live.live_solve(question, focus_part)
    raise ValueError("no model is configured")


def read_photo(raw, mimetype):
    mode = vision_mode()
    if mode == "vertex":
        return vertex_models.read_photo(raw, mimetype)
    if mode == "service":
        return remote_models.read_photo(raw, mimetype)
    return tutor_live.read_photo(raw)


@app.get("/api/status")
def status():
    """What this deployment can do, so the page can say so instead of failing."""
    return jsonify({"engine": True, "model": model_mode(), "photo": vision_mode(), "items": len(ITEMS)})


@app.post("/api/solve")
def solve():
    if model_mode() is None:
        return jsonify({"error": "No model is configured. The rule engine and the book still answer many questions."}), 503
    q = (request.get_json(silent=True) or {}).get("question", "").strip()
    if not q:
        return jsonify({"error": "empty question"}), 400
    try:
        return jsonify(live_solve(q))
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"the model gave no usable solution: {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": f"live solver failed: {exc}"}), 502


# ---------- photo of a question ----------


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
    if vision_mode() is None:
        return jsonify({"error": "Photo reading is not set up on this server (it needs a vision model)."}), 503
    f = request.files.get("image")
    if not f:
        return jsonify({"error": "no image uploaded (field name must be 'image')"}), 400
    if f.mimetype not in IMAGE_TYPES:
        return jsonify({"error": "only JPEG, PNG or WEBP images are accepted"}), 400
    raw = f.read(MAX_IMAGE_BYTES + 1)
    if len(raw) > MAX_IMAGE_BYTES:
        return jsonify({"error": "image is larger than 4 MB"}), 413

    try:
        read = read_photo(raw, f.mimetype)
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"could not read the photo: {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": f"could not read the photo: {exc}"}), 502

    if not read.get("readable") or not read.get("question"):
        return jsonify({"error": "No math question found in the photo.", "detected": read}), 422

    exercise, number = read.get("exercise"), read.get("number")
    part = (read.get("part_requested") or "").strip()
    detected = {"exercise": exercise, "number": number, "parts": read.get("parts", []), "question": read.get("question", ""),
                "part_requested": part, "confidence": read.get("confidence"), "notes": read.get("notes", "")}

    # 1) The printed exercise and question number identify a stored question exactly.
    book = _find_by_number(exercise, number)
    if book is not None:
        idx = _part_index(book, part)
        if idx is None:
            idx = 0
            detected["notes"] += f" Part ({part}) not found in the book; showing the first part."
            part = book["parts"][0].get("label", "")
        shown = only_part(book, idx) if part else book            # a part was named: show only that part
        return jsonify({"resolution": "book_by_number", "detected": detected, "item": shown,
                        "part_index": 0 if part else idx, "part_label": book["parts"][idx].get("label", "")})

    # 2) Otherwise answer the question that was read: stored solution only if it is the same question, then the solver
    #    engine, then the model. A merely similar example is returned as such, never as the answer.
    res = resolve(read["question"], focus_part=part or None)
    if res["mode"] in ("book", "solved", "model"):
        item = res["item"]
        idx = res.get("part_index", 0)
        return jsonify({"resolution": res["mode"], "detected": detected, "item": item,
                        "part_index": idx, "part_label": item.get("part_label") or item["parts"][idx].get("label", "")})
    return jsonify({"resolution": res["mode"], "detected": detected, "similar": res.get("similar", []), "message": res["message"]})


if __name__ == "__main__":
    print(f"loaded {len(ITEMS)} solved questions, {len(INDEX.chunks)} chunks")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5057)), debug=False)
