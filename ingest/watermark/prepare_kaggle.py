"""Package the notes pages and the stamp shape as a PRIVATE Kaggle dataset, and the cleaning job as a private Kaggle kernel.

  python ingest/watermark/prepare_kaggle.py --stamp <folder with stamp .npy files>      build data/notes/kaggle_pkg/
  python ingest/watermark/prepare_kaggle.py --upload                                     create or version the dataset
  python ingest/watermark/prepare_kaggle.py --push-kernel                                start the GPU job

The pages are copied byte for byte from the PDF (no recompression). Everything lands under data/notes/ (ignored by git).
"""
import argparse
import json
import pathlib
import shutil
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
PDF = ROOT / "9th" / "9th-Class-Math-Unique-Notes-New-Syllabus-Full-Book-Pdf.pdf"
PKG = ROOT / "data" / "notes" / "kaggle_pkg"
KERNEL = ROOT / "data" / "notes" / "kaggle_kernel"
USER = "awaisverse"
DATASET = "math9-notes-pages"
KERNEL_ID = "notes-stamp-unet"


def build(stamp_dir):
    import pypdf
    (PKG / "pages").mkdir(parents=True, exist_ok=True)
    (PKG / "stamp").mkdir(exist_ok=True)
    r = pypdf.PdfReader(str(PDF))
    for i, p in enumerate(r.pages):
        imgs = p.images
        if len(imgs) != 1:
            print(f"page {i + 1}: {len(imgs)} images, skipped")
            continue
        (PKG / "pages" / f"p{i + 1:03d}.jpg").write_bytes(imgs[0].data)
    src = pathlib.Path(stamp_dir)
    shutil.copy(src / "tmpl1.npy", PKG / "stamp" / "stamp_coarse_1x.npy")
    shutil.copy(src / "tmpl_sharp.npy", PKG / "stamp" / "stamp_strokes_2x.npy")
    (PKG / "dataset-metadata.json").write_text(json.dumps({
        "title": DATASET, "id": f"{USER}/{DATASET}", "licenses": [{"name": "other"}],
        "description": "Private: page images of a notes book, for watermark removal and dataset preparation. Not for redistribution.",
    }, indent=1), encoding="utf-8")
    n = len(list((PKG / "pages").glob("*.jpg")))
    mb = sum(f.stat().st_size for f in PKG.rglob("*") if f.is_file()) / 1e6
    print(f"package: {n} pages + stamp files, {mb:.1f} MB in {PKG}")


def kaggle(*args):
    print("$ kaggle", " ".join(args))
    r = subprocess.run(["kaggle", *args], capture_output=True, text=True)
    print((r.stdout + r.stderr).strip()[-1500:])
    return r.returncode


def upload():
    exists = subprocess.run(["kaggle", "datasets", "status", f"{USER}/{DATASET}"], capture_output=True, text=True).returncode == 0
    if exists:
        return kaggle("datasets", "version", "-p", str(PKG), "-m", "update", "-r", "zip")
    return kaggle("datasets", "create", "-p", str(PKG), "-r", "zip")       # private unless --public is given


def push_kernel(quick=False):
    KERNEL.mkdir(parents=True, exist_ok=True)
    shutil.copy(ROOT / "ingest" / "watermark" / "unet_clean.py", KERNEL / "notes_stamp_unet.py")
    runner = (KERNEL / "notes_stamp_unet.py").read_text(encoding="utf-8")
    # the Kaggle job: install the OCR used by the check, find the dataset folder, run, zip the clean pages
    run_args = ["--steps", "60", "--pages", "30"] if quick else ["--steps", "6000"]
    mode = "quick test" if quick else "full run"
    runner += f"\n\nRUN_ARGS = {run_args!r}   # set by prepare_kaggle.py ({mode})\n"
    runner += '''

if __name__ == "__main__" and "--data" not in sys.argv:
    import glob, os, subprocess as sp, zipfile
    sp.run([sys.executable, "-m", "pip", "install", "-q", "rapidocr_onnxruntime"], check=False)
    found = glob.glob("/kaggle/input/**/pages", recursive=True)
    if not found:
        sys.exit("dataset folder with pages/ not found under /kaggle/input")
    sys.argv = [sys.argv[0], "--data", os.path.dirname(found[0]), "--out", "/kaggle/working/out"] + RUN_ARGS
    main()
    with zipfile.ZipFile("/kaggle/working/notes_clean.zip", "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob("/kaggle/working/out/clean/*.png")):
            z.write(f, "clean/" + os.path.basename(f))
'''
    # the original __main__ guard must not run first on Kaggle (no --data there)
    runner = runner.replace('if __name__ == "__main__":\n    main()\n', 'if __name__ == "__main__" and "--data" in sys.argv:\n    main()\n', 1)
    (KERNEL / "notes_stamp_unet.py").write_text(runner, encoding="utf-8")
    (KERNEL / "kernel-metadata.json").write_text(json.dumps({
        "id": f"{USER}/{KERNEL_ID}", "title": KERNEL_ID, "code_file": "notes_stamp_unet.py", "language": "python",
        "kernel_type": "script", "is_private": True, "enable_gpu": True, "enable_tpu": False, "enable_internet": True,
        "dataset_sources": [f"{USER}/{DATASET}"], "competition_sources": [], "kernel_sources": [], "model_sources": [],
    }, indent=1), encoding="utf-8")
    return kaggle("kernels", "push", "-p", str(KERNEL))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--stamp", help="folder with tmpl1.npy and tmpl_sharp.npy: builds the package")
    ap.add_argument("--upload", action="store_true")
    ap.add_argument("--push-kernel", action="store_true")
    ap.add_argument("--quick", action="store_true", help="with --push-kernel: 60 steps on 30 pages, to test the pipeline")
    a = ap.parse_args()
    if a.stamp:
        build(a.stamp)
    if a.upload:
        sys.exit(upload())
    if a.push_kernel:
        sys.exit(push_kernel(a.quick))
