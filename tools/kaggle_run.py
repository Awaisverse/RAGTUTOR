"""Run the training notebook on Kaggle's free GPU, wait for it, and fetch the results.

Needs the Kaggle command-line tool and a token (KAGGLE_API_TOKEN or ~/.kaggle). The notebook clones the
project from GitHub, so push your code to GitHub first.

  python tools/kaggle_run.py --push            quick test run (about 15 minutes)
  python tools/kaggle_run.py --push --full     the real run (about 2 hours)
  python tools/kaggle_run.py --wait            poll until the run ends
  python tools/kaggle_run.py --fetch           download the zip, reports and log to train/kaggle_out/
"""
import argparse
import os
import pathlib
import re
import subprocess
import sys
import time

ROOT = pathlib.Path(__file__).resolve().parent.parent
KERNEL = "awaisverse/math-tutor-train"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8", "PYTHONUTF8": "1"}


def kaggle(*args, check=True):
    r = subprocess.run(["kaggle", *args], capture_output=True, text=True, encoding="utf-8", errors="replace", env=ENV)
    out = "\n".join(l for l in (r.stdout + r.stderr).splitlines() if "outdated" not in l)
    if check and r.returncode != 0:
        sys.exit(f"kaggle {' '.join(args)} failed:\n{out}")
    return out


def status():
    out = kaggle("kernels", "status", KERNEL, check=False)
    m = re.search(r'status "?([A-Za-z_.]+)"?', out)
    return (m.group(1).split(".")[-1] if m else out.strip()), out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--full", action="store_true", help="with --push: real run instead of the quick test")
    ap.add_argument("--wait", action="store_true")
    ap.add_argument("--fetch", action="store_true")
    ap.add_argument("--timeout-min", type=int, default=240)
    args = ap.parse_args()

    if args.push:
        subprocess.run([sys.executable, str(ROOT / "train" / "make_notebook.py")] + (["--full"] if args.full else []), check=True)
        print(kaggle("kernels", "push", "-p", str(ROOT / "kaggle")))
        print("started:", "FULL run" if args.full else "QUICK test", "| https://www.kaggle.com/code/" + KERNEL)
    if args.wait:
        t0 = time.time()
        last = None
        while time.time() - t0 < args.timeout_min * 60:
            st, raw = status()
            if st != last:
                print(time.strftime("%H:%M:%S"), st, flush=True)
                last = st
            if st.upper() in ("COMPLETE", "ERROR", "CANCELACKNOWLEDGED", "CANCEL_ACKNOWLEDGED"):
                break
            time.sleep(60)
        else:
            sys.exit("timed out while waiting")
    if args.fetch:
        dest = ROOT / "train" / "kaggle_out"
        dest.mkdir(parents=True, exist_ok=True)
        print(kaggle("kernels", "output", KERNEL, "-p", str(dest), "-o"))
        print("saved to", dest)


if __name__ == "__main__":
    main()
