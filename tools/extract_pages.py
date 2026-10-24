"""Extract each scanned page of the textbook PDF as a readable JPEG.

The PDF stores each page as black ink + a transparency mask, so we paste
it onto a white background (dropping the mask gives dark, unreadable pages).
"""
import sys, pathlib
import pypdf
from PIL import Image

pdf = sys.argv[1]
out = pathlib.Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
r = pypdf.PdfReader(pdf)
for i, page in enumerate(r.pages, 1):
    ims = page.images
    if not ims:
        continue
    im = ims[0].image
    bg = Image.new("RGB", im.size, "white")
    if im.mode == "RGBA":
        bg.paste(im, mask=im.split()[3])
    else:
        bg.paste(im.convert("RGB"))
    w, h = bg.size
    s = 1600 / h
    bg.resize((int(w * s), 1600), Image.LANCZOS).save(out / f"p{i:03d}.jpg", quality=85)
print("done", len(r.pages))
