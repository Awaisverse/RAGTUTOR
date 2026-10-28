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


def _load_env_file(path):
    """Local runs only: KEY=VALUE lines from .env.local, without overriding what is already set and skipping empty values.
    On Vercel the settings come from the project's environment variables instead."""
    if os.environ.get("VERCEL") or os.environ.get("TUTOR_NO_ENV_FILE") or not path.exists():   # tests never use real keys
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key, value = key.strip(), value.strip().strip('"').strip("'")
        if key and value and key not in os.environ:
            os.environ[key] = value


_load_env_file(ROOT / ".env.local")
sys.path.insert(0, str(ROOT / "tools"))
sys.path.insert(0, str(ROOT))

import local_models  # noqa: E402
import mathtext  # noqa: E402
import planner  # noqa: E402
import question_reader  # noqa: E402
import modelsolve  # noqa: E402
import rag  # noqa: E402
import remote_models  # noqa: E402
import solvers  # noqa: E402
import solvers10  # noqa: E402
import tutor_live  # noqa: E402
import vertex_models  # noqa: E402

MAX_IMAGE_BYTES = 4 * 1024 * 1024          # Vercel rejects larger request bodies; the page shrinks photos before sending
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}

app = Flask(__name__, static_folder=str(ROOT / "public"), static_url_path="")


CLASSES = ("9", "10")
ENGINES = {"9": solvers.solve, "10": solvers10.solve}      # each class has its own engine: Class 9's would read i as an unknown
_DATA = {}


def _embeddings_wanted():
    """The embedding model needs torch: off on Vercel and wherever sentence-transformers is not installed."""
    if os.environ.get("NO_EMBEDDINGS") == "1" or os.environ.get("VERCEL"):
        return False
    return importlib.util.find_spec("sentence_transformers") is not None


def data(klass="9"):
    """The book of one class: its items, an id lookup and its search index (built on first use)."""
    k = str(klass) if str(klass) in CLASSES else "9"
    if k not in _DATA:
        items = tutor_live.load_items(k)
        _DATA[k] = {"items": items, "by_id": {it["id"]: it for it in items},
                    "index": rag.Index([c for it in items for c in rag.chunk_item(it)], use_embeddings=_embeddings_wanted())}
    return _DATA[k]


def _klass():
    """The class a request is about: ?class=10 or {"class": 10}; Class 9 by default."""
    body = request.get_json(silent=True) if request.is_json else None
    k = str((body or {}).get("class") or request.args.get("class") or request.form.get("class") or "9")
    return k if k in CLASSES else "9"


ITEMS = data("9")["items"]
BY_ID = data("9")["by_id"]
INDEX = data("9")["index"]


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
    return jsonify([summary(it) for it in data(_klass())["items"]])


@app.get("/api/item/<item_id>")
def item(item_id):
    it = data(_klass())["by_id"].get(item_id) or next((data(k)["by_id"][item_id] for k in CLASSES if item_id in data(k)["by_id"]), None)
    if not it:
        return jsonify({"error": "not found"}), 404
    return jsonify(it)


def similar_examples(question, k=3, klass="9"):
    """Stored questions that are about the same topic. They are NOT answers: their numbers differ from the student's."""
    d = data(klass)
    hits = d["index"].search(question, k=k * 3)
    if not d["index"].is_confident(hits):
        return []
    out, seen = [], set()
    for h in hits:                                     # one entry per stored question: two parts of it are not two examples
        if h["id"] in seen:
            continue
        seen.add(h["id"])
        out.append({**summary(d["by_id"][h["id"]]), "part": h["part"], "cos": h["cos"], "lex": h["lex"]})
        if len(out) == k:
            break
    return out


# ---------- "Exercise 1.2, Q3 (iv)": find that question and ask the student to confirm it ----------

ROMAN = ["i", "ii", "iii", "iv", "v", "vi", "vii", "viii", "ix", "x", "xi", "xii"]


def parse_reference(text):
    """'Exercise 1.2 Q3 (iv)', 'ex 1.2 question 3 part iv', 'Review exercise 1 Q5' -> {"exercise", "number", "part"} or None.
    Only when the text is essentially a reference: a question with its own numbers is not one."""
    t = str(text).lower().strip()
    ex = re.search(r"\b(?:exercise|ex)\s*\.?\s*(?:no\.?\s*)?(\d+\.\d+)", t)
    rev = re.search(r"\breview\s*(?:exercise|ex)?\s*\.?\s*(\d+)", t)
    q = re.search(r"\b(?:q|qno|question)\s*\.?\s*(?:no\.?\s*)?(\d+)", t)
    if not (ex or rev) or not q:
        return None
    part = re.search(r"\(\s*([ivx]+|[a-h]|\d+)\s*\)|\bpart\s*\(?\s*([ivx]+|[a-h]|\d+)\s*\)?", t[q.end():])
    label = (part.group(1) or part.group(2)) if part else ""
    if label.isdigit():
        label = ROMAN[int(label) - 1] if 0 < int(label) <= len(ROMAN) else label
    rest = t
    for m in (ex or rev, q, part):
        if m is not None:
            rest = rest.replace(m.group(0), " ")
    if re.search(r"[0-9=+*/^]", rest):                 # more maths than a reference: it is a real question
        return None
    return {"exercise": ex.group(1) if ex else f"Review {rev.group(1)}", "number": q.group(1), "part": label}


def lookup_reference(ref, klass="9"):
    """-> {"mode": "confirm", item cut to the part} or {"mode": "ref_error", "message"} saying what does exist."""
    items = [it for it in data(klass)["items"] if it["kind"] in ("exercise", "review")]
    exercises = sorted({it.get("exercise") for it in items if it.get("exercise")}, key=str)
    wanted = _norm_exercise(ref["exercise"])
    in_ex = [it for it in items if _norm_exercise(it.get("exercise")) == wanted]
    if not in_ex:
        return {"mode": "ref_error", "message": f"Class {klass} has no Exercise {ref['exercise']} solved here yet. "
                                                f"Available: {', '.join(exercises) or 'none'}."}
    it = next((x for x in in_ex if str(x["number"]) == str(ref["number"])), None)
    if it is None:
        nums = ", ".join(sorted({str(x["number"]) for x in in_ex}, key=lambda n: int(n) if n.isdigit() else 0))
        return {"mode": "ref_error", "message": f"Exercise {ref['exercise']} has questions {nums}; there is no question {ref['number']}."}
    if str(ref.get("part", "")).isdigit():            # "part 3" means (iii): the book labels parts in roman numerals
        n = int(ref["part"])
        if 0 < n <= len(ROMAN) and any(p.get("label") == ROMAN[n - 1] for p in it["parts"]):
            ref = {**ref, "part": ROMAN[n - 1]}
    if ref["part"]:
        idx = _part_index(it, ref["part"])
        if idx is None:
            labels_ = ", ".join(f"({p.get('label')})" for p in it["parts"] if p.get("label"))
            return {"mode": "ref_error", "message": f"Exercise {ref['exercise']}, question {ref['number']} has parts {labels_}; there is no part ({ref['part']})."}
        shown = only_part(it, idx)
    else:
        shown = it
    return {"mode": "confirm", "item": shown, "part_index": 0, "ref": ref,
            "message": "Is this the question you are asking?"}


def only_part(item, index):
    """The student asked for ONE part: return the item cut down to that part, question = the stem plus that part's text,
    so the board and the explanation show just what was asked. The part's label is kept in `part_label`."""
    if len(item["parts"]) < 2 or index is None:
        return item
    label = item["parts"][index].get("label") or str(index + 1)
    cut = modelsolve.explode(item)[index]
    return {**cut, "id": item["id"], "part_label": label}


def resolve(question, focus_part=None, klass="9", _rewritten=False):
    """Answer THIS question. Order: an exercise reference (shown for confirmation), a stored solution only if it is the same
    question, then the class's solver engine, then (when the question cannot be read as typed) Gemini rewrites it into the
    form the tutor reads and the same steps run again, then the model, and otherwise a labelled similar example."""
    q = question.strip()
    klass = str(klass) if str(klass) in CLASSES else "9"
    ref = parse_reference(q)
    if ref:
        return lookup_reference(ref, klass)
    for it in data(klass)["items"]:                                   # 1. exactly a stored question (same numbers, same instruction)
        same, part = mathtext.same_question(q, it)
        if same:                                       # a part asked alone is answered alone; the whole question shows every part
            return {"mode": "book", "item": only_part(it, part), "part_index": 0}
    solved = ENGINES[klass](q)                         # 2. the solver engine: reads the numbers and solves this question
    if solved:
        return {"mode": "solved", "item": solved, "part_index": 0}
    error = None
    if not _rewritten and reader_on():                 # 3. not readable as typed: Gemini rewrites it (never solves it)
        try:
            n = question_reader.normalize(q, klass)
        except Exception as exc:
            n, error = None, f"question reader: {exc}"
        if n and n["reference"]:
            res = lookup_reference(n["reference"], klass)
            return {**res, "read_as": "Exercise {exercise}, Q{number}".format(**n["reference"]) + (f" ({n['reference']['part']})" if n["reference"]["part"] else "")}
        if n and n["question"] != q:
            res = resolve(n["question"], focus_part, klass, _rewritten=True)
            return {**res, "read_as": n["question"]}
    if klass == "10" and reader_on():                  # 4. too complex as one piece: Gemini plans small chunks, the engine solves each
        try:
            planned = planner.solve(q, klass)
        except Exception as exc:
            planned, error = None, f"planner: {exc}"
        if planned:
            return {"mode": "solved", "item": planned, "part_index": 0, "plan": planned["plan"]}
    if model_mode():                                   # 5. the model (its steps are checked with sympy afterwards)
        try:
            sol = live_solve(q, focus_part=focus_part, klass=klass)
            # the SAME question: the model restates the question it answered; if its numbers differ from the student's,
            # it answered something else (perhaps a similar question it has seen), so it is not presented as the answer
            stated = str(sol.get("question", ""))
            if stated and not question_reader.same_numbers(q, stated):
                sol["verified"] = False
                sol["warning"] = "The model's working may be for a different question (its numbers differ from yours). Do not rely on it."
            sol["question"] = q
            return {"mode": "model", "item": sol, "part_index": 0}
        except Exception as exc:
            error = str(exc)
    similar = similar_examples(q, klass=klass)         # 4. nothing could solve it: show related examples, labelled as such
    return {"mode": "example_only" if similar else "none", "similar": similar, "error": error,
            "message": "I could not solve this exact question here. The examples below are about the same topic but use different numbers, "
                       "so they are not the answer to your question." if similar else "I could not recognise this question."}


@app.post("/api/answer")
def answer():
    q = (request.get_json(silent=True) or {}).get("question", "")
    if not q.strip():
        return jsonify({"error": "empty question"}), 400
    if len(q) > 2000:
        return jsonify({"error": "the question is too long (2000 characters at most)"}), 400
    try:
        return jsonify(resolve(q, klass=_klass()))
    except Exception as exc:                            # never a bare 500: say what failed
        app.logger.exception("answer failed")
        return jsonify({"mode": "none", "error": str(exc), "message": "Something went wrong while solving this question. Please rephrase it or try again."})


@app.post("/api/ask")
def ask():
    """Search only: which stored questions are related. 'book' means one of them is exactly this question."""
    q = (request.get_json(silent=True) or {}).get("question", "")
    klass = _klass()
    results = similar_examples(q, klass=klass)
    exact = any(mathtext.same_question(q, it)[0] for it in data(klass)["items"])
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


def reader_on():
    """Gemini rewrites unreadable questions when Vertex AI is configured (QUESTION_READER=off turns it off)."""
    return vertex_models.configured() and os.environ.get("QUESTION_READER", "on") != "off"


def model_mode():
    return _backend("model")


def vision_mode():
    return _backend("vision")


def live_solve(question, focus_part=None, klass="9"):
    """Solve with the model: one part at a time, each reply checked with sympy and retried when a check fails."""
    mode = model_mode()
    if mode == "vertex":
        return tutor_live.live_solve(question, focus_part, generate=vertex_models.generate, klass=klass, attempts=2)
    if mode == "service":
        return remote_models.solve(question, focus_part)
    if mode == "local":
        return tutor_live.live_solve(question, focus_part, klass=klass)
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
    return jsonify({"engine": True, "model": model_mode(), "photo": vision_mode(), "reader": reader_on(), "items": len(ITEMS),
                    "classes": {k: len(data(k)["items"]) for k in CLASSES}})


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


def _find_by_number(exercise, number, klass="9"):
    """Exact lookup of a printed exercise question, e.g. exercise 1.3, question 2."""
    if number is None:
        return None
    wanted = _norm_exercise(exercise) if exercise else None
    for it in data(klass)["items"]:
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
    book = _find_by_number(exercise, number, _klass())
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
    res = resolve(read["question"], focus_part=part or None, klass=_klass())
    if res["mode"] in ("book", "solved", "model"):
        item = res["item"]
        idx = res.get("part_index", 0)
        return jsonify({"resolution": res["mode"], "detected": detected, "item": item,
                        "part_index": idx, "part_label": item.get("part_label") or item["parts"][idx].get("label", "")})
    return jsonify({"resolution": res["mode"], "detected": detected, "similar": res.get("similar", []), "message": res["message"]})


if __name__ == "__main__":
    print(f"loaded {len(ITEMS)} solved questions, {len(INDEX.chunks)} chunks")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5057)), debug=False)
