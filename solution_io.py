"""Reading the generator's reply: find the JSON solution and repair the usual LaTeX escaping slip.

The solution is JSON, and LaTeX is full of backslashes (\\frac, \\sqrt, \\times). A model that writes
a single backslash where JSON needs two produces text that json.loads rejects, or worse, accepts and
silently corrupts (\\f becomes a form feed, \\t a tab). parse_solution handles both cases.
"""
import json
import re

# a backslash pair is already correct; any other backslash that is not a legal JSON escape is LaTeX
_LONE_BACKSLASH = re.compile(r'(\\\\)|\\(?!["/]|u[0-9a-fA-F]{4})')
_CONTROL = re.compile(r"[\x00-\x1f]")   # any control character (form feed, tab, newline, ...) means a LaTeX backslash was misread


def _repair(text):
    """Double every backslash that is not part of a correct escape (\\\\, \\", \\/, \\uXXXX)."""
    return _LONE_BACKSLASH.sub(lambda m: m.group(1) or "\\\\", text)


def _has_control_chars(obj):
    if isinstance(obj, str):
        return bool(_CONTROL.search(obj))
    if isinstance(obj, dict):
        return any(_has_control_chars(v) for v in obj.values())
    if isinstance(obj, list):
        return any(_has_control_chars(v) for v in obj)
    return False


def parse_solution(raw):
    """-> (solution dict, repaired flag). Raises ValueError when no usable JSON can be recovered."""
    m = re.search(r"\{.*\}", raw, re.S)
    if not m:
        raise ValueError("no JSON object in the reply")
    text = m.group(0)
    try:
        obj = json.loads(text)
        if not _has_control_chars(obj):
            return obj, False
    except json.JSONDecodeError:
        pass
    try:
        return json.loads(_repair(text)), True
    except json.JSONDecodeError as exc:
        raise ValueError(f"reply is not valid JSON even after repair: {exc}") from exc
