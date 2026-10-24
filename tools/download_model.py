"""Download a Hugging Face model folder, retrying and resuming when the connection drops.

Usage: python tools/download_model.py Qwen/Qwen2.5-Math-1.5B-Instruct models/Qwen2.5-Math-1.5B-Instruct
"""
import os
import sys
import time

os.environ.setdefault("HF_HUB_DISABLE_XET", "1")
from huggingface_hub import snapshot_download  # noqa: E402

repo, dest = sys.argv[1], sys.argv[2]
for attempt in range(1, 301):
    try:
        path = snapshot_download(repo, local_dir=dest, allow_patterns=["*.json", "*.safetensors", "*.txt"])
        import pathlib
        d = pathlib.Path(dest)
        incomplete = list(d.rglob("*.incomplete"))
        if not any(d.glob("*.safetensors")) or incomplete:
            raise RuntimeError("weights not complete yet (offline or interrupted)")
        print("DONE", path, flush=True)
        break
    except Exception as exc:  # network drops: wait, then resume
        print(f"attempt {attempt} failed: {type(exc).__name__}", flush=True)
        time.sleep(15)
else:
    print("GAVE_UP", flush=True)
