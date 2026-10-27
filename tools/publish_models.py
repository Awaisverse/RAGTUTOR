"""Publish the trained generator adapter to the Hugging Face Hub, once, so no machine ever needs to retrain or copy it.

  set HF_TOKEN=<a write token from huggingface.co/settings/tokens>      (never put the token in a file or in git)
  python tools/publish_models.py --repo yourname/math-tutor-lora [--folder models/gen-lora] [--public]

The repo is private unless --public is given. The adapter is small (about 74 MB); the textbook and the training data are
never uploaded. Afterwards set GEN_ADAPTER=yourname/math-tutor-lora (and HF_TOKEN if private) on the model service.
"""
import argparse
import os
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
ADAPTER_FILES = ("adapter_config.json", "adapter_model.safetensors", "README.md", "tokenizer.json", "tokenizer_config.json", "chat_template.jinja")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True, help="owner/name on the Hub")
    ap.add_argument("--folder", default=str(ROOT / "models" / "gen-lora"))
    ap.add_argument("--public", action="store_true")
    args = ap.parse_args()
    token = os.environ.get("HF_TOKEN")
    if not token:
        sys.exit("Set HF_TOKEN first (a write token). It is read from the environment and never stored.")
    folder = pathlib.Path(args.folder)
    files = [folder / f for f in ADAPTER_FILES if (folder / f).exists()]
    if not (folder / "adapter_model.safetensors").exists():
        sys.exit(f"No adapter in {folder}. It comes from the Kaggle run: train/kaggle_out/*.zip -> gen-lora/")
    from huggingface_hub import HfApi
    api = HfApi(token=token)
    api.create_repo(args.repo, private=not args.public, exist_ok=True)
    for f in files:
        api.upload_file(path_or_fileobj=str(f), path_in_repo=f.name, repo_id=args.repo)
        print("uploaded", f.name)
    print(f"done: https://huggingface.co/{args.repo}  ({'public' if args.public else 'private'})")


if __name__ == "__main__":
    main()
