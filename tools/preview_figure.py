"""Render the drawing commands of a solved question to a PNG, to check figures by eye.

It follows the same rules as drawCmd in static/index.html (logical canvas 100 x 60), drawing the commands of
every step cumulatively, one panel per step.

Usage:  python tools/preview_figure.py ex1.1-q2 ii out.png     (item id, part label, output file)
"""
import json
import math
import pathlib
import sys

from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
W, H, S = 600, 360, 6.0   # panel size and pixels per logical unit


def X(x):
    return x * S


def Y(y):
    return y * S


def draw_cmd(d, c):
    t = c["t"]
    ink = (30, 36, 51)
    if t == "line":
        x1, y1, x2, y2 = c["p"]
        d.line([X(x1), Y(y1), X(x2), Y(y2)], fill=ink, width=2)
    elif t == "poly":
        p = c["p"]
        pts = [(X(p[i]), Y(p[i + 1])) for i in range(0, len(p), 2)]
        d.line(pts + ([pts[0]] if c.get("close") else []), fill=ink, width=2)
    elif t in ("circle", "arc"):
        cx, cy, r = X(c["c"][0]), Y(c["c"][1]), c["r"] * S
        a0, a1 = (c["a"] if t == "arc" else (0, 360))
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a1, fill=ink, width=2)   # PIL angles: clockwise from +x, like canvas
    elif t == "dot":
        x, y = X(c["p"][0]), Y(c["p"][1])
        d.ellipse([x - 4, y - 4, x + 4, y + 4], fill=ink)
    elif t == "text":
        d.text((X(c["p"][0]) - 3, Y(c["p"][1]) - 6), c["s"], fill=ink)
    elif t == "right":
        x, y = c["p"]
        (d1x, d1y, d2x, d2y), k = c["d"], 3
        d.line([X(x + d1x * k), Y(y + d1y * k), X(x + d1x * k + d2x * k), Y(y + d1y * k + d2y * k), X(x + d2x * k), Y(y + d2y * k)], fill=ink, width=2)
    elif t in ("numberline", "subdiv"):
        lo_, hi_ = c["from"], c["to"]

        def nx(v):
            return 6 + (v - lo_) / (hi_ - lo_) * 88
        y = c["y"]
        if t == "subdiv":
            for j in range(1, c["n"]):
                x = nx(c["lo"] + (c["hi"] - c["lo"]) * j / c["n"])
                d.line([X(x), Y(y - 1.6), X(x), Y(y + 1.6)], fill=ink, width=2)
            return
        d.line([X(nx(lo_)), Y(y), X(nx(hi_)), Y(y)], fill=ink, width=2)
        for v in range(math.ceil(lo_), math.floor(hi_) + 1):
            d.line([X(nx(v)), Y(y - 2), X(nx(v)), Y(y + 2)], fill=ink, width=2)
            d.text((X(nx(v)) - 4, Y(y + 7) - 6), str(v), fill=ink)
        for m in c.get("marks", []):
            x = X(nx(m["v"]))
            d.ellipse([x - 5, Y(y) - 5, x + 5, Y(y) + 5], fill=(200, 40, 40))
            d.text((x - 12, Y(y - 8) - 6), m["s"], fill=(200, 40, 40))


def main():
    item_id, label, out = sys.argv[1], sys.argv[2], sys.argv[3]
    item = None
    for path in (ROOT / "data" / "book").glob("unit*.json"):
        for it in json.loads(path.read_text(encoding="utf-8"))["items"]:
            if it["id"] == item_id:
                item = it
    part = next(p for p in item["parts"] if p.get("label", "") == label)
    steps = [s for s in part["steps"]]
    cols = min(3, len(steps))
    rows = math.ceil(len(steps) / cols)
    sheet = Image.new("RGB", (W * cols, H * rows), "white")
    for i in range(len(steps)):
        panel = Image.new("RGB", (W, H), (251, 252, 254))
        d = ImageDraw.Draw(panel)
        for s in steps[: i + 1]:
            for c in s.get("draw", []):
                draw_cmd(d, c)
        d.text((8, 6), f"step {i + 1}: {steps[i]['math'][:60]}", fill=(90, 90, 90))
        sheet.paste(panel, ((i % cols) * W, (i // cols) * H))
    sheet.save(out)
    print("saved", out, f"({len(steps)} steps)")


if __name__ == "__main__":
    main()
