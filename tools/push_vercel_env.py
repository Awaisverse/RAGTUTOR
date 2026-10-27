"""Copy the Vertex AI service-account settings from .env.local to the Vercel project (production). You run this yourself.

  python tools/push_vercel_env.py            sends the four values below, then redeploys so the site uses them

Only these names are sent; their values are read from .env.local and are never printed:
  GOOGLE_PALM_API_SECRET_CLIENT_EMAIL, GOOGLE_PALM_API_SECRET_PRIVATE_KEY, GOOGLE_PALM_API_SECRET_PROJECT_ID,
  GOOGLE_PALM_API_SECRET_TOKEN_URI
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
NAMES = ["GOOGLE_PALM_API_SECRET_CLIENT_EMAIL", "GOOGLE_PALM_API_SECRET_PRIVATE_KEY",
         "GOOGLE_PALM_API_SECRET_PROJECT_ID", "GOOGLE_PALM_API_SECRET_TOKEN_URI"]


def read_env(path):
    out = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line and not line.startswith("#") and "=" in line:
            k, v = line.split("=", 1)
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def main():
    env = read_env(ROOT / ".env.local")
    missing = [n for n in NAMES if not env.get(n)]
    if missing:
        sys.exit("missing in .env.local: " + ", ".join(missing))
    vercel = "vercel.cmd" if sys.platform == "win32" else "vercel"
    for name in NAMES:
        r = subprocess.run([vercel, "env", "add", name, "production", "--force"], input=env[name], text=True,
                           capture_output=True, cwd=ROOT)
        print(f"{name}: {'set' if r.returncode == 0 else 'FAILED (' + (r.stderr or r.stdout).strip().splitlines()[-1][:120] + ')'}")
    print("redeploying so the site picks the settings up ...")
    r = subprocess.run([vercel, "--prod", "--yes"], capture_output=True, text=True, cwd=ROOT)
    print("done" if r.returncode == 0 else "redeploy failed: " + (r.stderr or r.stdout).strip()[-300:])


if __name__ == "__main__":
    main()
