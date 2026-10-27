"""Client for the hosted model service (service/app.py). Standard library only, so the Vercel function stays small.

  MODEL_SERVICE_URL     e.g. https://yourname-math-tutor.hf.space   (empty: the models are local, or not available)
  MODEL_SERVICE_TOKEN   shared secret the service checks
  MODEL_SERVICE_TIMEOUT seconds to wait for one call (default 55, under Vercel's 60 s function limit)
"""
import json
import os
import urllib.error
import urllib.request


class RemoteError(RuntimeError):
    pass


def configured():
    return bool(os.environ.get("MODEL_SERVICE_URL", "").strip())


def _call(path, data, content_type, method="POST"):
    url = os.environ["MODEL_SERVICE_URL"].strip().rstrip("/") + path
    headers = {"Content-Type": content_type}
    token = os.environ.get("MODEL_SERVICE_TOKEN", "")
    if token:
        headers["Authorization"] = "Bearer " + token
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=float(os.environ.get("MODEL_SERVICE_TIMEOUT", "55"))) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error", "")
        except Exception:
            detail = ""
        raise RemoteError(detail or f"the model service answered HTTP {exc.code}") from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RemoteError(f"the model service is not reachable ({getattr(exc, 'reason', exc)})") from None


def health():
    """-> {"generator": bool, "vision": bool}; both False when the service cannot be reached."""
    try:
        return _call("/health", None, "application/json", method="GET")
    except RemoteError:
        return {"generator": False, "vision": False}


def solve(question, focus_part=None):
    body = json.dumps({"question": question, "focus_part": focus_part}).encode("utf-8")
    return _call("/solve", body, "application/json")


def read_photo(image_bytes, mimetype="image/jpeg"):
    return _call("/read", image_bytes, mimetype)
