"""The hosted model service: the only part of the tutor that needs a GPU (or a patient CPU) and torch.

The web app on Vercel calls it for two things: solving a question the rule engine cannot, and reading a photo.
It holds no state and no training: the base models and the trained LoRA adapter come from the Hugging Face Hub
(GEN_MODEL, GEN_ADAPTER, VISION_MODEL), so a new machine only needs these settings, never a retrain.

  GET  /health   {"generator": bool, "vision": bool}
  POST /solve    {"question": "...", "focus_part": "ii"}   -> a solution (every maths check re-run by sympy)
  POST /read     raw image bytes (Content-Type: image/*)   -> {"readable", "exercise", "number", "parts", "question", ...}

  SERVICE_TOKEN  if set, every call except /health must send  Authorization: Bearer <token>
  WARM=1         load the models at start instead of on the first request

Run:  python service/app.py          (port from PORT, default 7860: what Hugging Face Spaces expects)
"""
import hmac
import json
import os
import pathlib
import sys
import threading

ROOT = pathlib.Path(__file__).resolve().parent.parent
for p in (ROOT, ROOT / "tools"):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from flask import Flask, jsonify, request  # noqa: E402

import local_models  # noqa: E402
import tutor_live  # noqa: E402

app = Flask(__name__)
MAX_IMAGE_BYTES = 8 * 1024 * 1024
IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp"}
_gpu_lock = threading.Lock()          # one generation at a time: two at once only slow both down and can exhaust memory


@app.before_request
def check_token():
    token = os.environ.get("SERVICE_TOKEN", "")
    if not token or request.path == "/health":
        return None
    sent = request.headers.get("Authorization", "")
    if not hmac.compare_digest(sent.encode(), ("Bearer " + token).encode()):
        return jsonify({"error": "unauthorised"}), 401
    return None


@app.get("/health")
def health():
    return jsonify({"generator": local_models.generator_available(), "vision": local_models.vision_available()})


@app.post("/solve")
def solve():
    body = request.get_json(silent=True) or {}
    q = str(body.get("question", "")).strip()
    if not q or len(q) > 2000:
        return jsonify({"error": "send a question of 1 to 2000 characters"}), 400
    if not local_models.generator_available():
        return jsonify({"error": "the generator model is not configured on the service"}), 503
    try:
        with _gpu_lock:
            return jsonify(tutor_live.live_solve(q, focus_part=body.get("focus_part") or None))
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"the model gave no usable solution: {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": f"solving failed: {exc}"}), 502


@app.post("/read")
def read():
    if not local_models.vision_available():
        return jsonify({"error": "the vision model is not configured on the service"}), 503
    if (request.mimetype or "") not in IMAGE_TYPES:
        return jsonify({"error": "send a JPEG, PNG or WEBP image as the request body"}), 400
    raw = request.get_data(cache=False)
    if not raw or len(raw) > MAX_IMAGE_BYTES:
        return jsonify({"error": "the image is empty or larger than 8 MB"}), 413
    try:
        with _gpu_lock:
            return jsonify(tutor_live.read_photo(raw))
    except (ValueError, json.JSONDecodeError) as exc:
        return jsonify({"error": f"could not read the photo: {exc}"}), 502
    except Exception as exc:
        return jsonify({"error": f"reading failed: {exc}"}), 502


if __name__ == "__main__":
    if os.environ.get("WARM") == "1":
        def warm():
            if local_models.generator_available():
                local_models._load_generator()
            if local_models.vision_available():
                local_models._load_vision()
        threading.Thread(target=warm, daemon=True).start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 7860)), debug=False, threaded=True)
