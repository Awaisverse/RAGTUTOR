"""Remove the "www.ilmkidunya.com" stamp from the notes pages with a small U-Net trained on this exact stamp.

Why a network: the stamp's outline strokes are as dark and thin as the real text at this scan resolution (~95 dpi), so a
fixed template cannot be divided out precisely enough. Instead, exact training pairs are synthesised:
  clean patch  = a part of a real page that the stamp does not touch (found by template matching)
  stamped      = that patch with the real stamp shape composited on it (random position, size, angle, strength, blur),
                 then JPEG-compressed like the scans
and the network learns stamped -> clean. Because the target is the real page, it learns to keep every pixel of ink.

Checks (written to report.json; the run fails loudly if the synthetic gates are missed):
  synthetic test pages (never trained on):  ink kept >= 99.5%, stamp removed, clean pixels left alone
  every real page:  stamp match score before -> after, ink pixels lost, OCR must not read "ilmkidunya"

Runs on Kaggle (GPU) or locally for a smoke test:
  python ingest/watermark/unet_clean.py --data <folder with pages/ and stamp/> --out <folder> [--steps 20 --pages 6]
Single file on purpose: a Kaggle script job uploads one file.
"""
import argparse
import json
import math
import pathlib
import random
import sys
import time

import cv2
import numpy as np

# ------------------------------------------------------------------------------------------ stamp geometry


def norm(g):
    """grey (0..1) / local paper level: paper ~1, ink and stamp < 1."""
    bg = cv2.morphologyEx(g, cv2.MORPH_CLOSE, cv2.getStructuringElement(cv2.MORPH_RECT, (25, 25)))
    bg = cv2.GaussianBlur(bg, (0, 0), 8)
    return np.clip(g / np.maximum(bg, 1e-3), 0, 1).astype(np.float32), bg.astype(np.float32)


def band_mask(dark, width=42):
    """The stamp's diagonal band: a line through its strongest pixels, +-width around it."""
    ys, xs = np.nonzero(dark > 0.5 * float(dark.max()))
    vx, vy, x0, y0 = cv2.fitLine(np.stack([xs, ys], 1).astype(np.float32), cv2.DIST_HUBER, 0, 0.01, 0.01).ravel()
    H, W = dark.shape
    yy, xx = np.mgrid[0:H, 0:W]
    dist = np.abs((xx - x0) * vy - (yy - y0) * vx)
    along = (xx - x0) * vx + (yy - y0) * vy
    a = (xs - x0) * vx + (ys - y0) * vy
    return ((dist < width) & (along > a.min() - 12) & (along < a.max() + 12)).astype(np.uint8)


def find_stamps(n, tmpl, mask, scales=np.arange(0.86, 1.15, 0.01), k=3, min_score=0.45):
    """Copies of the stamp on a normalised page: [(score, x, y, scale)], best first, at most k."""
    inv = (1 - n).astype(np.float32)
    cands = []
    for s in scales:
        ts = cv2.resize(tmpl, None, fx=s, fy=s, interpolation=cv2.INTER_AREA)
        ms = cv2.resize(mask, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
        if ts.shape[0] >= inv.shape[0] or ts.shape[1] >= inv.shape[1]:
            continue
        res = np.nan_to_num(cv2.matchTemplate(inv, ts, cv2.TM_CCORR_NORMED, mask=ms), nan=0, posinf=0, neginf=0)
        for _ in range(k + 2):
            _, mv, _, (mx, my) = cv2.minMaxLoc(res)
            cands.append((float(mv), mx, my, float(s)))
            res[max(0, my - 60):my + 60, max(0, mx - 120):mx + 120] = 0
    cands.sort(reverse=True)
    out = []
    for c in cands:
        if c[0] >= min_score and all(abs(c[2] - o[2]) > 120 for o in out):
            out.append(c)
        if len(out) == k:
            break
    return out


class Stamp:
    """The stamp: `coarse` (1x, for finding it) and `strokes` (the darkening it adds, 2x, sharp)."""

    def __init__(self, folder):
        folder = pathlib.Path(folder)
        self.coarse = np.load(folder / "stamp_coarse_1x.npy").astype(np.float32)
        self.coarse_mask = band_mask(self.coarse)
        self.coarse = self.coarse * self.coarse_mask
        strokes2 = np.load(folder / "stamp_strokes_2x.npy").astype(np.float32)
        self.strokes = cv2.resize(strokes2, (self.coarse.shape[1], self.coarse.shape[0]), interpolation=cv2.INTER_AREA)
        self.strokes /= max(float(self.strokes.max()), 1e-6)          # 1 = the darkest stroke; strength is drawn per sample

    def locate(self, n):
        return find_stamps(n, self.coarse, self.coarse_mask)

    def zone(self, shape, hits, grow=12):
        """Pixels the stamp may touch on this page (its band, slightly enlarged)."""
        z = np.zeros(shape, np.uint8)
        for _, x, y, s in hits:
            m = cv2.resize(self.coarse_mask, None, fx=s, fy=s, interpolation=cv2.INTER_NEAREST)
            h, w = min(m.shape[0], shape[0] - y), min(m.shape[1], shape[1] - x)
            z[y:y + h, x:x + w] |= m[:h, :w]
        return cv2.dilate(z, np.ones((2 * grow + 1, 2 * grow + 1), np.uint8))


# ------------------------------------------------------------------------------------------ synthetic pairs


def stamp_layer(stamp, shape, rng):
    """A random stamp darkening map of `shape`: random size, angle, position, strength and blur."""
    s = rng.uniform(0.85, 1.15)
    ang = rng.uniform(-2.0, 2.0)
    st = stamp.strokes
    h, w = st.shape
    M = cv2.getRotationMatrix2D((w / 2, h / 2), ang, s)
    H, W = shape
    # the stamp is a thin diagonal band in a wide box, so a random box position mostly misses a small patch:
    # instead put a random point of its strokes at a random point of the patch
    ys, xs = np.nonzero(st > 0.3)
    k = int(rng.integers(len(xs)))
    px, py = M[:, :2] @ np.array([xs[k], ys[k]], np.float64) + M[:, 2]
    M[0, 2] += rng.uniform(0, W) - px
    M[1, 2] += rng.uniform(0, H) - py
    a = cv2.warpAffine(st, M, (W, H), flags=cv2.INTER_LINEAR)
    if rng.random() < 0.5:                                         # real outlines are often a pixel thicker than the template
        a = cv2.dilate(a, np.ones((2, 2), np.uint8))
    sigma = rng.uniform(0, 0.7)
    if sigma > 0.15:
        a = cv2.GaussianBlur(a, (0, 0), sigma)
    return np.clip(a * rng.uniform(0.45, 0.95), 0, 0.9)            # real strokes darken the paper by about 45-90%


def jpeg(x, rng):
    q = int(rng.uniform(55, 90))
    ok, buf = cv2.imencode(".jpg", (np.clip(x, 0, 1) * 255).astype(np.uint8), [cv2.IMWRITE_JPEG_QUALITY, q])
    return cv2.imdecode(buf, cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255


class PatchSource:
    """Stamp-free patches of real pages, to be stamped synthetically."""

    def __init__(self, pages, stamp, size, rng):
        self.size, self.rng, self.items = size, rng, []
        for g in pages:
            n, _ = norm(g)
            z = stamp.zone(g.shape, stamp.locate(n))
            free = 1 - z
            integral = cv2.integral(free.astype(np.uint8))
            H, W = g.shape
            ok = []
            for y in range(0, H - size, 16):
                for x in range(0, W - size, 16):
                    tot = integral[y + size, x + size] - integral[y, x + size] - integral[y + size, x] + integral[y, x]
                    if tot == size * size:
                        ok.append((y, x))
            if ok:
                self.items.append((g, ok))
        if not self.items:
            raise RuntimeError("no stamp-free patches found: check the stamp files")

    def sample(self):
        g, ok = self.items[self.rng.randrange(len(self.items))]
        y, x = ok[self.rng.randrange(len(ok))]
        p = g[y:y + self.size, x:x + self.size].copy()
        if self.rng.random() < 0.5:
            p = p[:, ::-1].copy()                                       # mirrored text is still text-like strokes
        return p

    def pair(self, stamp, nprng, with_stamp=True):
        clean = self.sample()
        if not with_stamp:
            return jpeg(clean, nprng), clean, np.zeros_like(clean)
        a = stamp_layer(stamp, clean.shape, nprng)
        return jpeg(clean * (1 - a), nprng), clean, a


# ------------------------------------------------------------------------------------------ model


def build_unet(base=32, depth=4):
    import torch.nn as nn

    def block(i, o):
        return nn.Sequential(nn.Conv2d(i, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True),
                             nn.Conv2d(o, o, 3, padding=1), nn.BatchNorm2d(o), nn.ReLU(inplace=True))

    class UNet(nn.Module):
        """Predicts a correction added to the input, so an untouched page is the easy answer."""

        def __init__(self):
            super().__init__()
            ch = [base * 2 ** i for i in range(depth)]
            self.down = nn.ModuleList([block(1 if i == 0 else ch[i - 1], ch[i]) for i in range(depth)])
            self.pool = nn.MaxPool2d(2)
            self.mid = block(ch[-1], ch[-1] * 2)
            self.up = nn.ModuleList([nn.ConvTranspose2d(ch[i] * 2, ch[i], 2, stride=2) for i in reversed(range(depth))])
            self.dec = nn.ModuleList([block(ch[i] * 2, ch[i]) for i in reversed(range(depth))])
            self.head = nn.Conv2d(ch[0], 1, 1)

        def forward(self, x):
            skips, h = [], x
            for d in self.down:
                h = d(h)
                skips.append(h)
                h = self.pool(h)
            h = self.mid(h)
            for u, dec, s in zip(self.up, self.dec, reversed(skips)):
                h = dec(__import__("torch").cat([u(h), s], 1))
            return (x + self.head(h)).clamp(0, 1)

    return UNet()


def loss_fn(out, clean, a):
    import torch
    l1 = (out - clean).abs()
    on_stamp = (a > 0.02).float()
    ink = (clean < 0.45).float()
    lighten_ink = torch.relu(out - clean) * ink                         # erasing real ink is the costly error
    return l1.mean() + 4 * (l1 * on_stamp).sum() / on_stamp.sum().clamp(min=1) + 6 * lighten_ink.sum() / ink.sum().clamp(min=1)


def run_model(model, g, device):
    import torch
    H, W = g.shape
    ph, pw = (16 - H % 16) % 16, (16 - W % 16) % 16
    x = np.pad(g, ((0, ph), (0, pw)), mode="edge")
    with torch.no_grad():
        y = model(torch.from_numpy(x)[None, None].to(device)).cpu().numpy()[0, 0]
    return y[:H, :W]


# ------------------------------------------------------------------------------------------ checks


def synthetic_metrics(model, src, stamp, device, n, seed):
    nprng = np.random.default_rng(seed)
    src.rng = random.Random(seed)
    tot = {"psnr": 0.0, "ink_kept": 0, "ink_total": 0, "stamp_left": 0.0, "stamp_px": 0, "clean_changed": 0.0, "clean_px": 0}
    for _ in range(n):
        x, clean, a = src.pair(stamp, nprng)
        y = run_model(model, x, device)
        mse = float(np.mean((y - clean) ** 2))
        tot["psnr"] += 10 * math.log10(1 / max(mse, 1e-10))
        ink = clean < 0.45
        tot["ink_kept"] += int(np.sum(ink & (y < 0.55)))
        tot["ink_total"] += int(np.sum(ink))
        st = (a > 0.05) & (clean > 0.6)                                   # stamp over bare paper
        tot["stamp_left"] += float(np.sum(np.clip(clean - y, 0, 1)[st]))
        tot["stamp_px"] += int(np.sum(st))
        free = a < 0.005
        tot["clean_changed"] += float(np.sum(np.abs(y - x)[free]))
        tot["clean_px"] += int(np.sum(free))
    return {"pairs": n, "psnr_db": round(tot["psnr"] / n, 2),
            "ink_kept": round(tot["ink_kept"] / max(tot["ink_total"], 1), 5),
            "stamp_darkness_left": round(tot["stamp_left"] / max(tot["stamp_px"], 1), 4),
            "change_on_stamp_free_pixels": round(tot["clean_changed"] / max(tot["clean_px"], 1), 4)}


def page_checks(g, y, stamp, ocr):
    n0, paper = norm(g)
    n1 = np.clip(y / np.maximum(paper, 1e-3), 0, 1)
    before = stamp.locate(n0)
    zone = stamp.zone(g.shape, before) > 0 if before else np.zeros(g.shape, bool)
    after = find_stamps(n1, stamp.coarse, stamp.coarse_mask, k=3, min_score=0.0)
    lost_ink = int(np.sum((n0 < 0.30) & (n1 > 0.70)))
    outside = float(np.mean(np.abs(y - g)[~zone])) if (~zone).any() else 0.0
    res = {"stamp_score_before": round(max([h[0] for h in before], default=0), 3),
           "stamp_score_after": round(max([h[0] for h in after], default=0), 3),
           "copies_found": len(before), "ink_px_lost": lost_ink, "mean_change_outside_stamp": round(outside, 4)}
    if ocr is not None:
        lines, _ = ocr((np.clip(y, 0, 1) * 255).astype(np.uint8))
        text = " ".join(l[1] for l in (lines or [])).lower()
        res["ocr_sees_stamp"] = any(w in text for w in ("ilmkidunya", "kidunya", "ilmki", "dunya.com"))
        res["ocr_chars"] = len(text)
    return res


# ------------------------------------------------------------------------------------------ main


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True, help="folder with pages/pNNN.jpg and stamp/*.npy")
    ap.add_argument("--out", required=True)
    ap.add_argument("--steps", type=int, default=6000)
    ap.add_argument("--batch", type=int, default=16)
    ap.add_argument("--patch", type=int, default=256)
    ap.add_argument("--pages", type=int, default=0, help="use only the first N pages (smoke test)")
    ap.add_argument("--no-ocr", action="store_true")
    args = ap.parse_args()

    import torch
    t0 = time.time()
    data, out = pathlib.Path(args.data), pathlib.Path(args.out)
    (out / "clean").mkdir(parents=True, exist_ok=True)
    (out / "samples").mkdir(exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    files = sorted((data / "pages").glob("p*.jpg"))
    if args.pages:
        files = files[:args.pages]
    if not files:
        sys.exit(f"no pages in {data / 'pages'}")
    pages = [cv2.imread(str(f), cv2.IMREAD_GRAYSCALE).astype(np.float32) / 255 for f in files]
    stamp = Stamp(data / "stamp")
    print(f"{len(pages)} pages | device {device} | stamp {stamp.coarse.shape}", flush=True)

    # pages ending in 0 are the test pages: never used for training patches
    train_pages = [g for i, g in enumerate(pages) if i % 10 != 0] or pages
    test_pages = [g for i, g in enumerate(pages) if i % 10 == 0] or pages[:1]
    rng = random.Random(0)
    train_src = PatchSource(train_pages, stamp, args.patch, rng)
    test_src = PatchSource(test_pages, stamp, args.patch, random.Random(1))
    print(f"patch sources: train {sum(len(o) for _, o in train_src.items)} positions, test {sum(len(o) for _, o in test_src.items)}", flush=True)

    model = build_unet().to(device)
    opt = torch.optim.AdamW(model.parameters(), lr=2e-3, weight_decay=1e-4)
    sched = torch.optim.lr_scheduler.OneCycleLR(opt, max_lr=2e-3, total_steps=max(args.steps, 1))
    nprng = np.random.default_rng(0)
    model.train()
    for step in range(1, args.steps + 1):
        xs, cs, as_ = [], [], []
        for _ in range(args.batch):
            x, c, a = train_src.pair(stamp, nprng, with_stamp=rng.random() > 0.15)   # some pairs have no stamp at all
            xs.append(x), cs.append(c), as_.append(a)
        X, C, A = (torch.from_numpy(np.stack(v))[:, None].to(device) for v in (xs, cs, as_))
        loss = loss_fn(model(X), C, A)
        opt.zero_grad()
        loss.backward()
        opt.step()
        sched.step()
        if step % 200 == 0 or step == args.steps:
            print(f"step {step}/{args.steps} loss {loss.item():.4f} ({time.time() - t0:.0f}s)", flush=True)
    model.eval()
    torch.save(model.state_dict(), out / "unet_stamp.pt")

    synth = synthetic_metrics(model, test_src, stamp, device, n=min(300, 30 * len(test_pages)), seed=123)
    print("synthetic test:", synth, flush=True)

    ocr = None
    if not args.no_ocr:
        try:
            from rapidocr_onnxruntime import RapidOCR
            ocr = RapidOCR()
        except Exception as exc:
            print("OCR check skipped:", exc, flush=True)

    per_page = {}
    for f, g in zip(files, pages):
        y = run_model(model, g, device)
        cv2.imwrite(str(out / "clean" / (f.stem + ".png")), (np.clip(y, 0, 1) * 255).astype(np.uint8))
        per_page[f.stem] = page_checks(g, y, stamp, ocr)
        if int(f.stem[1:]) % 40 == 1:
            side = np.hstack([g, np.ones((g.shape[0], 8), np.float32), y])
            cv2.imwrite(str(out / "samples" / (f.stem + "_before_after.jpg")), (side * 255).astype(np.uint8))
    vals = list(per_page.values())
    flagged = [k for k, v in per_page.items() if v["stamp_score_after"] > 0.35 or v["ink_px_lost"] > 40 or v.get("ocr_sees_stamp")]
    summary = {
        "pages": len(vals),
        "stamp_score_before_median": float(np.median([v["stamp_score_before"] for v in vals])),
        "stamp_score_after_median": float(np.median([v["stamp_score_after"] for v in vals])),
        "pages_ocr_still_sees_stamp": sum(bool(v.get("ocr_sees_stamp")) for v in vals) if ocr else None,
        "ink_px_lost_total": int(sum(v["ink_px_lost"] for v in vals)),
        "mean_change_outside_stamp": round(float(np.mean([v["mean_change_outside_stamp"] for v in vals])), 4),
        "flagged_pages": flagged,
    }
    gates = {"ink_kept >= 0.995 (synthetic)": synth["ink_kept"] >= 0.995,
             "stamp mostly removed (synthetic darkness left <= 0.05)": synth["stamp_darkness_left"] <= 0.05,
             "stamp-free pixels left alone (synthetic change <= 0.02)": synth["change_on_stamp_free_pixels"] <= 0.02}
    report = {"synthetic_test": synth, "gates": gates, "real_pages": summary, "per_page": per_page,
              "settings": vars(args), "device": device, "seconds": round(time.time() - t0)}
    (out / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    print(json.dumps({"gates": gates, "real_pages": {k: v for k, v in summary.items() if k != "flagged_pages"},
                      "flagged": len(flagged)}, indent=1), flush=True)
    if not all(gates.values()):
        print("GATES FAILED: do not use these pages for training until the failures are fixed.", flush=True)


if __name__ == "__main__":
    main()
