"""Vercel entry point: serves the Flask app (server.py) as a serverless function. `app` is the WSGI object Vercel looks for."""
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from server import app  # noqa: E402,F401
