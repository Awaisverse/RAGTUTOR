"""Stage 1 of book ingestion: clean every page image and find its text lines with their positions.

For each page image in data/pages/ this writes data/ocr/pNNN.json:
  page          PDF page number (the printed page number is page - 2)
  size          [width, height] of the cleaned image
  skew_deg      the skew that was measured (and corrected when large enough)
  rows          text rows with boxes, top to bottom: {x0, y0, x1, y1, text, conf}

Computer-vision steps (OpenCV): grayscale, contrast normalisation, skew estimation and correction.
Text detection and reading use RapidOCR (ONNX, runs on the CPU). OCR text is only used to find the layout
(headings, question numbers, page header). Maths is NOT trusted from OCR: the question regions are cropped
and read from the image in the next stages.

It resumes: pages that already have a JSON file are skipped.

Usage:  python ingest/ocr_pages.py --start 1 --end 288
"""
import argparse
import json
import pathlib
import sys
import time

import cv2
import numpy as np
from rapidocr_onnxruntime import RapidOCR

ROOT = pathlib.Path(__file__).resolve().parent.parent
PAGES = ROOT / "data" / "pages"
CLEAN = ROOT / "data" / "pages_clean"
OUT = ROOT / "data" / "ocr"
ROW_GAP = 14   # text segments whose vertical centres differ by less than this belong to one row


def estimate_skew(gray):
    """Angle (degrees) of the text lines, from the minimum-area rectangle around all ink pixels."""
    ink = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)[1]
    ys, xs = np.nonzero(ink)
    if len(xs) < 500:
        return 0.0
    angle = cv2.minAreaRect(np.column_stack([xs, ys]).astype(np.float32))[-1]
    angle = angle - 90 if angle > 45 else angle      # minAreaRect returns 0..90
    return float(-angle if abs(angle) < 45 else 0.0)


def clean_page(path):
    img = cv2.imread(str(path))
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    skew = estimate_skew(gray)
    if 0.3 < abs(skew) < 5:                           # correct only a real, plausible skew
        h, w = gray.shape
        m = cv2.getRotationMatrix2D((w / 2, h / 2), skew, 1.0)
        img = cv2.warpAffine(img, m, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return img, skew


def rows_from_segments(segments):
    """Merge OCR segments that sit on the same line into rows, left to right."""
    segs = []
    for box, text, conf in segments:
        xs, ys = [p[0] for p in box], [p[1] for p in box]
        segs.append({"x0": int(min(xs)), "y0": int(min(ys)), "x1": int(max(xs)), "y1": int(max(ys)),
                     "text": text.strip(), "conf": round(float(conf), 3)})
    segs.sort(key=lambda s: (s["y0"] + s["y1"]) / 2)
    rows, cur = [], []
    for s in segs:
        if cur and abs((s["y0"] + s["y1"]) / 2 - sum((c["y0"] + c["y1"]) / 2 for c in cur) / len(cur)) > ROW_GAP:
            rows.append(cur)
            cur = []
        cur.append(s)
    if cur:
        rows.append(cur)
    out = []
    for r in rows:
        r.sort(key=lambda s: s["x0"])
        out.append({"x0": min(s["x0"] for s in r), "y0": min(s["y0"] for s in r),
                    "x1": max(s["x1"] for s in r), "y1": max(s["y1"] for s in r),
                    "text": " ".join(s["text"] for s in r),
                    "conf": round(sum(s["conf"] for s in r) / len(r), 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", type=int, default=1)
    ap.add_argument("--end", type=int, default=288)
    args = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    CLEAN.mkdir(parents=True, exist_ok=True)
    engine = RapidOCR()
    t_all = time.time()
    for n in range(args.start, args.end + 1):
        src, dst = PAGES / f"p{n:03d}.jpg", OUT / f"p{n:03d}.json"
        if dst.exists() or not src.exists():
            continue
        t0 = time.time()
        img, skew = clean_page(src)
        cv2.imwrite(str(CLEAN / f"p{n:03d}.jpg"), img, [cv2.IMWRITE_JPEG_QUALITY, 90])
        result, _ = engine(img)
        rows = rows_from_segments(result or [])
        dst.write_text(json.dumps({"page": n, "size": [img.shape[1], img.shape[0]], "skew_deg": round(skew, 2),
                                   "rows": rows}, ensure_ascii=False), encoding="utf-8")
        print(f"page {n:3d}: {len(rows):3d} rows, skew {skew:+.2f} deg, {time.time() - t0:.1f}s", flush=True)
    print(f"done in {(time.time() - t_all) / 60:.1f} min", flush=True)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
