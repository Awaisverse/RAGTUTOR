"""Drawing commands for number-line figures. Logical canvas: 100 wide, 60 high, y grows downward.

The UI draws these step by step (see static/index.html, drawCmd). A figure for a question is a list of
steps; each step carries the commands that appear at that step, and earlier steps stay on the board.
"""
import math

Y = 46.0   # height of the number line; labels go below it and constructions above it


def nx(v, lo, hi):
    """x position of the value v on a number line drawn from lo to hi."""
    return round(6 + (v - lo) / (hi - lo) * 88, 2)


def axis(lo, hi, marks=None):
    cmd = {"t": "numberline", "from": lo, "to": hi, "y": Y}
    if marks:
        cmd["marks"] = marks
    return cmd


def text(x, y, s):
    return {"t": "text", "p": [round(x, 2), round(y, 2)], "s": s}


def subdivide(lo, hi, from_, to_, n):
    """Divide the interval [lo, hi] of a number line drawn from from_ to to_ into n equal parts."""
    return {"t": "subdiv", "from": from_, "to": to_, "y": Y, "lo": lo, "hi": hi, "n": n}


def triangle(lo, hi, base, height, start=0.0):
    """Right triangle O-A-B standing on the number line: O at `start`, A at start+base, B above A.
    Returns (commands, B's y coordinate)."""
    unit = 88 / (hi - lo)
    ox, ax = nx(start, lo, hi), nx(start + base, lo, hi)
    by = round(Y - height * unit, 2)
    return [{"t": "poly", "p": [ox, Y, ax, Y, ax, by], "close": True},
            {"t": "right", "p": [ax, Y], "d": [-1, 0, 0, -1]}], by


def arc_to_axis(lo, hi, base, height, radius_value, start=0.0):
    """Arc centred at O with radius `radius_value` (in number-line units), from the top of the
    triangle down to the number line, plus a dot where it lands."""
    unit = 88 / (hi - lo)
    theta = round(math.degrees(math.atan2(height, base)), 1)
    cx = nx(start, lo, hi)
    return [{"t": "arc", "c": [cx, Y], "r": round(radius_value * unit, 2), "a": [-theta, 0]},
            {"t": "dot", "p": [nx(start + radius_value, lo, hi), Y]}]
