"""Google service-account login with the standard library and the small pure-Python `rsa` package (no google-auth).

A service account signs a short JWT; Google's token endpoint exchanges it for an access token (valid about an hour),
which is cached and refreshed. Used by vertex_models.py for Vertex AI when no API key works.

The account is read from environment variables with a common prefix (default GOOGLE_PALM_API_SECRET_, the names in
.env.local): <prefix>CLIENT_EMAIL, <prefix>PRIVATE_KEY (PEM, \\n allowed), <prefix>PROJECT_ID, <prefix>TOKEN_URI.
Nothing secret is ever logged or returned in an error message.
"""
import base64
import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

SCOPE = "https://www.googleapis.com/auth/cloud-platform"
_cache = {"token": None, "exp": 0}


class AuthError(RuntimeError):
    pass


def _prefix():
    return os.environ.get("VERTEX_SA_PREFIX", "GOOGLE_PALM_API_SECRET_")


def account():
    """-> dict with email, key, project, token_uri, or None when no service account is configured."""
    p = _prefix()
    email, key = os.environ.get(p + "CLIENT_EMAIL", ""), os.environ.get(p + "PRIVATE_KEY", "")
    if not email or not key:
        return None
    return {"email": email, "key": key.replace("\\n", "\n"), "project": os.environ.get(p + "PROJECT_ID", ""),
            "token_uri": os.environ.get(p + "TOKEN_URI") or "https://oauth2.googleapis.com/token"}


def _der_read(buf, i):
    """One DER element at i -> (tag, content start, content end)."""
    tag = buf[i]
    length = buf[i + 1]
    j = i + 2
    if length & 0x80:
        n = length & 0x7F
        length = int.from_bytes(buf[j:j + n], "big")
        j += n
    return tag, j, j + length


def _pkcs1_from_pem(pem):
    """Service-account keys are PKCS#8 ('BEGIN PRIVATE KEY'); the rsa package reads PKCS#1, which sits inside it."""
    lines = [l for l in pem.strip().splitlines() if l and not l.startswith("-----")]
    der = base64.b64decode("".join(lines))
    if "BEGIN RSA PRIVATE KEY" in pem:
        return der
    tag, s, e = _der_read(der, 0)                      # PrivateKeyInfo SEQUENCE
    i = s
    _, s1, e1 = _der_read(der, i)                      # version INTEGER
    i = e1
    _, s2, e2 = _der_read(der, i)                      # algorithm SEQUENCE
    i = e2
    tag3, s3, e3 = _der_read(der, i)                   # privateKey OCTET STRING = the PKCS#1 key
    if tag3 != 0x04:
        raise AuthError("the service-account private key is not in a format that can be read")
    return der[s3:e3]


def _b64(data):
    return base64.urlsafe_b64encode(data).rstrip(b"=").decode("ascii")


def access_token():
    """A cached OAuth access token for the configured service account."""
    if _cache["token"] and time.time() < _cache["exp"] - 120:
        return _cache["token"]
    acc = account()
    if acc is None:
        raise AuthError("no service account is configured")
    import rsa                                        # small pure-Python dependency, only needed here
    try:
        key = rsa.PrivateKey.load_pkcs1(_pkcs1_from_pem(acc["key"]), format="DER")
    except Exception:
        raise AuthError("the service-account private key could not be read") from None
    now = int(time.time())
    header = _b64(json.dumps({"alg": "RS256", "typ": "JWT"}).encode())
    claims = _b64(json.dumps({"iss": acc["email"], "scope": SCOPE, "aud": acc["token_uri"], "iat": now, "exp": now + 3600}).encode())
    signature = _b64(rsa.sign(f"{header}.{claims}".encode(), key, "SHA-256"))
    body = urllib.parse.urlencode({"grant_type": "urn:ietf:params:oauth:grant-type:jwt-bearer",
                                   "assertion": f"{header}.{claims}.{signature}"}).encode()
    req = urllib.request.Request(acc["token_uri"], data=body, method="POST", headers={"Content-Type": "application/x-www-form-urlencoded"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            data = json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        try:
            detail = json.loads(exc.read().decode("utf-8")).get("error_description", "")
        except Exception:
            detail = ""
        raise AuthError(f"Google refused the service-account login (HTTP {exc.code}) {detail[:120]}".strip()) from None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        raise AuthError(f"Google's login service is not reachable ({getattr(exc, 'reason', exc)})") from None
    _cache["token"], _cache["exp"] = data["access_token"], now + int(data.get("expires_in", 3600))
    return _cache["token"]
