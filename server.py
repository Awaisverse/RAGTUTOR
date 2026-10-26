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
import rag  # noqa: E402
from build_dataset import verify  # noqa: E402
from solution_io import parse_solution  # noqa: E402
from prompts import READ_PROMPT, SOLVE_RULES  # noqa: E402

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


@app.post("/api/ask")
def ask():
    q = (request.get_json(silent=True) or {}).get("question", "")
    hits = INDEX.search(q, k=3)
    results = [{**summary(BY_ID[h["id"]]), "part": h["part"], "cos": h["cos"], "lex": h["lex"]} for h in hits]
    mode = "book" if INDEX.is_confident(hits) else "none"
    return jsonify({"mode": mode, "results": results,
                    "live_available": local_models.generator_available()})


# ---------- live solver ----------


def _retrieve_examples(question, k=3):
    seen, out = set(), []
    for h in INDEX.search(question, k=k * 2):
        if h["id"] in seen or h["id"] not in BY_ID:
            continue
        seen.add(h["id"])
        out.append(BY_ID[h["id"]])
        if len(out) == k:
            break
    return out


def _verify(solution):
    bad = []
    for p in solution.get("parts", []):
        for i, st in enumerate(p.get("steps", [])):
            for chk in st.get("check", []):
                try:
                    if not verify(chk):
                        bad.append(f"step {i+1}: {chk}")
                except Exception as exc:
                    bad.append(f"step {i+1}: {chk} ({exc})")
    return bad


def live_solve(question, focus_part=None):
    """Solve with Claude, grounded in retrieved book examples, then verify every check with sympy."""
    examples = _retrieve_examples(question)
    example_text = "\n\n".join(
        f"EXAMPLE {i+1} ({e['id']}):\n" + json.dumps({k: e[k] for k in ("question", "parts")}, ensure_ascii=False)
        for i, e in enumerate(examples))
    user = question
    if focus_part:
        user += f"\n\nSolve only part ({focus_part}). Return a single part in the parts list."
    raw = local_models.generate([
        {"role": "system", "content": SOLVE_RULES + "\n\n" + example_text},
        {"role": "user", "content": user},
    ], max_new_tokens=3000)
    sol, _repaired = parse_solution(raw)
    bad = _verify(sol)
    sol["verified"] = not bad
    sol["unverified_checks"] = bad
    sol["unit"] = 0
    sol["unit_title"] = "Live"
    sol["used_examples"] = [e["id"] for e in examples]
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
    for it in ITEMS:
        if it["kind"] != "exercise":
            continue
        if str(it.get("number")) == str(number) and (exercise is None or str(it.get("exercise")) == str(exercise)):
            return it
    return None


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

    # 1) Printed exercise + question number matches a book item -> show the verified book solution.
    book = _find_by_number(exercise, number)
    how = "book_by_number"
    # 2) Otherwise search the book by the text that was read.
    if book is None:
        hits = INDEX.search(read["question"], k=3)
        if INDEX.is_confident(hits):
            book = BY_ID[hits[0]["id"]]
            how = "book_by_text"

    if book is not None:
        idx = _part_index(book, part)
        if idx is None:
            idx = 0
            detected["notes"] += f" Part ({part}) not found in the book; showing the first part."
        return jsonify({"resolution": how, "detected": detected, "item": book,
                        "part_index": idx, "part_label": book["parts"][idx].get("label", "")})

    # 3) Not in the book -> live solve, focused on the requested part when one was marked.
    try:
        sol = live_solve(read["question"], focus_part=part or None)
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"model output was not valid JSON: {exc}", "detected": detected}), 502
    except Exception as exc:  # API / network errors from the SDK
        return jsonify({"error": f"live solver failed: {exc}", "detected": detected}), 502
    return jsonify({"resolution": "live", "detected": detected, "item": sol,
                    "part_index": 0, "part_label": sol["parts"][0].get("label", "")})


if __name__ == "__main__":
    print(f"loaded {len(ITEMS)} solved questions, {len(INDEX.chunks)} chunks")
    app.run(host="127.0.0.1", port=int(os.environ.get("PORT", 5057)), debug=False)
