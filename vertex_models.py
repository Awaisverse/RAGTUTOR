"""Gemini through Google's HTTPS API: a hosted alternative to running the models yourself. Standard library only.

Used for the same two jobs as the local models, and nothing else is trusted to it: the answer it writes is re-checked step by
step with sympy (modelsolve.py) and shown as unverified when a check fails.

  GOOGLE_PALM_API_SECRET_*  a service account (client email, private key, project id): signs in to Vertex AI
                      (google_auth_lite.py). Preferred when present; VERTEX_LOCATION defaults to "global".
  GEMINI_API_KEY      a Google AI Studio key: calls https://generativelanguage.googleapis.com
  VERTEX_API_KEY      a Vertex AI (express mode) key: calls https://aiplatform.googleapis.com
  VERTEX_BASE_URL     override the endpoint root (another region, a proxy, a test stub)
  VERTEX_MODEL        model that solves questions; default gemini-3.8-flash (gemini-2.5-* were retired on 20 Oct 2026)
  VERTEX_VISION_MODEL model that reads photos; default: the same as VERTEX_MODEL
  VERTEX_TIMEOUT      seconds per call, default 40 (a Vercel function stops at 60)

The key is a secret: set it as an environment variable on the host, never in the repository or the page.
Photos and question text are sent to Google when this is on.
"""
import base64
import json
import os
import re
import urllib.error
import urllib.request

from remote_models import RemoteError


def _service_account():
    import google_auth_lite
    return google_auth_lite.account()


def configured():
    """A service account (Vertex AI) or an API key is set."""
    return bool(_service_account() or os.environ.get("GEMINI_API_KEY") or os.environ.get("VERTEX_API_KEY"))


DEFAULT_MODEL = "gemini-3.8-flash"


def _endpoint(model=None):
    """-> (url, headers). A service account is preferred: it signs in to the project's Vertex AI endpoint. The newest models
    are served from the 'global' location (VERTEX_LOCATION), not from regions such as us-central1."""
    model = model or os.environ.get("VERTEX_MODEL") or DEFAULT_MODEL
    if os.environ.get("VERTEX_BASE_URL"):
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("VERTEX_API_KEY", "")
        return f"{os.environ['VERTEX_BASE_URL'].rstrip('/')}/models/{model}:generateContent", {"x-goog-api-key": key}
    acc = _service_account()
    if acc and os.environ.get("VERTEX_AUTH", "service_account") != "key":
        import google_auth_lite
        loc = os.environ.get("VERTEX_LOCATION", "global")
        host = "aiplatform.googleapis.com" if loc == "global" else f"{loc}-aiplatform.googleapis.com"
        try:
            token = google_auth_lite.access_token()
        except google_auth_lite.AuthError as exc:
            raise RemoteError(str(exc)) from None
        return (f"https://{host}/v1/projects/{acc['project']}/locations/{loc}/publishers/google/models/{model}:generateContent",
                {"Authorization": "Bearer " + token})
    if os.environ.get("GEMINI_API_KEY"):
        return (f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent",
                {"x-goog-api-key": os.environ["GEMINI_API_KEY"]})
    return (f"https://aiplatform.googleapis.com/v1/publishers/google/models/{model}:generateContent",
            {"x-goog-api-key": os.environ.get("VERTEX_API_KEY", "")})


def _post(body, model=None):
    url, auth = _endpoint(model)
    req = urllib.request.Request(url, data=json.dumps(body).encode("utf-8"), method="POST",
                                 headers={"Content-Type": "application/json", **auth})
    try:
        with urllib.request.urlopen(req, timeout=float(os.environ.get("VERTEX_TIMEOUT", "40"))) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error", {}).get("message", "")
        except Exception:
            detail = ""
        raise RemoteError(f"Google's API answered HTTP {exc.code}" + (f": {detail[:160]}" if detail else "")) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise RemoteError(f"Google's API is not reachable ({getattr(exc, 'reason', exc)})") from None
    parts = ((data.get("candidates") or [{}])[0].get("content") or {}).get("parts") or []
    text = "".join(p.get("text", "") for p in parts)
    if not text:
        reason = (data.get("promptFeedback") or {}).get("blockReason") or (data.get("candidates") or [{}])[0].get("finishReason") or "no text"
        raise RemoteError(f"Google's API returned no answer ({reason})")
    return text


def _config(max_tokens, temperature):
    cfg = {"temperature": temperature, "maxOutputTokens": max(int(max_tokens), 4096), "responseMimeType": "application/json"}
    if os.environ.get("VERTEX_THINKING_BUDGET"):
        cfg["thinkingConfig"] = {"thinkingBudget": int(os.environ["VERTEX_THINKING_BUDGET"])}
    return cfg


def generate(messages, max_new_tokens=2048, temperature=0.0, model=None, thinking_budget=None):
    """Same call shape as local_models.generate, so modelsolve can retry with it. messages: [{"role", "content"}, ...]."""
    system = "\n\n".join(m["content"] for m in messages if m["role"] == "system")
    contents = [{"role": "model" if m["role"] == "assistant" else "user", "parts": [{"text": m["content"]}]}
                for m in messages if m["role"] != "system"]
    body = {"contents": contents, "generationConfig": _config(max_new_tokens, temperature)}
    if thinking_budget is not None:
        body["generationConfig"]["thinkingConfig"] = {"thinkingBudget": int(thinking_budget)}
    if system:
        body["systemInstruction"] = {"parts": [{"text": system}]}
    return _post(body, model)


def read_photo(image_bytes, mimetype="image/jpeg"):
    """The question in the picture as the JSON described in prompts.READ_PROMPT (LaTeX inside $...$). Solves nothing."""
    from prompts import READ_PROMPT
    body = {"contents": [{"role": "user", "parts": [
        {"inlineData": {"mimeType": mimetype, "data": base64.b64encode(image_bytes).decode("ascii")}},
        {"text": READ_PROMPT + "\n\nRead this question photo as instructed."}]}],
        "generationConfig": _config(1500, 0.0)}
    text = _post(body, os.environ.get("VERTEX_VISION_MODEL") or None)
    m = re.search(r"\{.*\}", text, re.S)
    if not m:
        raise ValueError("no JSON object in the model's reading of the photo")
    return json.loads(m.group(0))
