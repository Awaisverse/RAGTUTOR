"""The model service's HTTP contract without any model: auth, validation and clear refusals. Run: python tests/test_service.py"""
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "service"))

os.environ["GEN_MODEL"] = str(ROOT / "models" / "does-not-exist")
os.environ["GEN_ADAPTER"] = ""
os.environ["VISION_MODEL"] = str(ROOT / "models" / "does-not-exist")
os.environ["SERVICE_TOKEN"] = "s3cret"

import app as service  # noqa: E402

c = service.app.test_client()
auth = {"Authorization": "Bearer s3cret"}

assert c.get("/health").get_json() == {"generator": False, "vision": False}          # health needs no token
assert c.post("/solve", json={"question": "x"}).status_code == 401                    # everything else does
assert c.post("/solve", json={"question": "x"}, headers={"Authorization": "Bearer nope"}).status_code == 401
assert c.post("/solve", json={"question": ""}, headers=auth).status_code == 400
assert c.post("/solve", json={"question": "a" * 3000}, headers=auth).status_code == 400
assert c.post("/solve", json={"question": "area of a circle of radius 7"}, headers=auth).status_code == 503
assert c.post("/read", data=b"x", headers={**auth, "Content-Type": "image/jpeg"}).status_code == 503
print("service: all tests passed")
