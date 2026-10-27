"""The model backends, against stand-in servers (no key, no GPU). Run: python tests/test_backends.py

  1. Gemini backend (vertex_models): a question the engine cannot solve is answered by the "model", its check is re-run by
     sympy, a wrong check is retried, a photo is read into LaTeX and then answered like typed text.
  2. Hosted-service backend (remote_models + service/app.py contract): the same, through /solve and /read.
  3. No backend: the engine and the book still answer, and a model question is refused without crashing.
"""
import json
import os
import pathlib
import sys
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

os.environ["NO_EMBEDDINGS"] = "1"
ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import server  # noqa: E402

READ = {"readable": True, "exercise": None, "number": None, "parts": [], "part_requested": "", "confidence": 0.9, "notes": "",
        "question": "Rationalize the denominator of $\\frac{7}{3+\\sqrt{2}}$"}


def solution(answer, check):
    return {"id": "t", "kind": "generated", "number": "", "page": 0, "question": "q", "parts": [
        {"label": "", "prompt": "", "figure": None, "steps": [{"math": "x", "en": "e", "ur": "u", "check": [check]}], "answer": answer}]}


class Stub(BaseHTTPRequestHandler):
    calls = []

    def log_message(self, *a):
        pass

    def _send(self, obj, code=200):
        data = json.dumps(obj).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_POST(self):
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        Stub.calls.append((self.path, self.headers.get("x-goog-api-key"), self.headers.get("Authorization")))
        if self.path.endswith(":generateContent"):                      # Gemini
            req = json.loads(body)
            if "inlineData" in json.dumps(req):
                text = json.dumps(READ)
            else:                                                      # first reply has a false check, the retry is right
                Stub.gem = getattr(Stub, "gem", 0) + 1
                text = json.dumps(solution("49pi", "pi*7**2 == 49*pi") if Stub.gem % 2 == 0 else solution("22", "pi*7**2 == 22"))
            self._send({"candidates": [{"content": {"parts": [{"text": text}]}}]})
        elif self.path == "/solve":                                     # hosted service
            self._send({**solution("49pi", "pi*7**2 == 49*pi"), "verified": True, "unverified_checks": [], "tries": [1],
                        "unit": 0, "unit_title": "Live"})
        elif self.path == "/read":
            self._send(READ)
        else:
            self._send({"error": "not found"}, 404)

    def do_GET(self):
        self._send({"generator": True, "vision": True})


def start():
    srv = HTTPServer(("127.0.0.1", 0), Stub)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_port}"


def clear():
    for k in ("GEMINI_API_KEY", "VERTEX_API_KEY", "VERTEX_BASE_URL", "MODEL_SERVICE_URL", "MODEL_SERVICE_TOKEN", "MODEL_BACKEND"):
        os.environ.pop(k, None)


client = server.app.test_client()
ask = lambda q: client.post("/api/answer", json={"question": q}).get_json()          # noqa: E731
srv, url = start()

# ---- 1. Gemini
clear()
os.environ.update(GEMINI_API_KEY="test-key", VERTEX_BASE_URL=url)
assert client.get("/api/status").get_json()["model"] == "vertex"
d = ask("Find the area of a circle of radius 7")
assert d["mode"] == "model", d
assert d["item"]["verified"] is True and d["item"]["parts"][0]["answer"] == "49pi", d["item"]["parts"][0]["answer"]
assert d["item"]["tries"] == [2], "the first reply had a false check and must have been retried"
assert all(c[1] == "test-key" for c in Stub.calls if c[0].endswith(":generateContent"))

r = client.post("/api/photo", data={"image": (__import__("io").BytesIO(b"\xff\xd8\xff fake jpeg"), "q.jpg", "image/jpeg")}).get_json()
assert r["detected"]["question"].startswith("Rationalize"), r
assert r["resolution"] == "solved" and "sqrt{2}" in r["item"]["parts"][0]["answer"], r["resolution"]      # the LaTeX went to the engine

# ---- 2. hosted service
clear()
Stub.calls.clear()
os.environ.update(MODEL_SERVICE_URL=url, MODEL_SERVICE_TOKEN="s3cret")
assert client.get("/api/status").get_json()["model"] == "service"
d = ask("Find the area of a circle of radius 7")
assert d["mode"] == "model" and d["item"]["parts"][0]["answer"] == "49pi", d
assert Stub.calls[0][2] == "Bearer s3cret"
r = client.post("/api/photo", data={"image": (__import__("io").BytesIO(b"\xff\xd8\xff fake jpeg"), "q.jpg", "image/jpeg")}).get_json()
assert r["resolution"] == "solved", r

# service unreachable: a clean message, not a crash
os.environ["MODEL_SERVICE_URL"] = "http://127.0.0.1:9"
d = ask("Find the area of a circle of radius 7")
assert d["mode"] in ("example_only", "none") and d["error"], d

# ---- 3. nothing configured
clear()
os.environ["MODEL_BACKEND"] = "local"                    # no weights on this machine either
st = client.get("/api/status").get_json()
assert st["model"] is None and st["photo"] is None, st
assert ask("Rationalize the denominator of 11/(5+sqrt3)")["mode"] == "solved"           # the engine needs no model
assert ask("Find the area of a circle of radius 7")["mode"] in ("example_only", "none")
assert client.post("/api/photo", data={"image": (__import__("io").BytesIO(b"x"), "q.jpg", "image/jpeg")}).status_code == 503
print("backends: all tests passed")
