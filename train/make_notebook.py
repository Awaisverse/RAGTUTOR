"""Generates train/colab_train.ipynb. Run:  python train/make_notebook.py"""
import json
import pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent

CELLS = [
    ("md", """# Math Tutor: training on Colab (free GPU)

Trains three things on the verified solved book, with the RAG principles from `docs/PLAN.md`:

1. **Embedding model** (`bge-small-en-v1.5`): contrastive fine-tune on question paraphrases.
2. **Generator** (`Qwen2.5-Math-1.5B-Instruct`): LoRA fine-tune on verified solutions, with retrieved examples in the prompt.
3. **Evaluation** on a held-out split (base vs fine-tuned).

Runtime: **GPU** (Runtime > Change runtime type > T4 GPU). Everything runs locally on Colab, no API keys.

At the end, download `train/out/` and copy the folders into your project:
- `train/out/embed-ft`  ->  `models/embed-ft`
- `train/out/gen-lora`  ->  `models/gen-lora`

Then run the server with `EMB_MODEL=models/embed-ft` (the generator adapter is loaded from `models/gen-lora` automatically)."""),
    ("code", """!nvidia-smi --query-gpu=name,memory.total --format=csv"""),
    ("code", """# 1) Get the project (clones the first time, pulls updates on later runs)
import os
REPO_URL = "https://github.com/Awaisverse/RAGTUTOR.git"
REPO_DIR = "/content/RAGsystemfromnotes"
if os.path.exists(REPO_DIR):
    !git -C {REPO_DIR} pull
else:
    !git clone {REPO_URL} {REPO_DIR}
%cd {REPO_DIR}
!ls data/book"""),
    ("code", """# 2) Install (Colab already has torch and CUDA)
!pip -q uninstall -y torchao
!pip -q install "transformers>=4.45" peft accelerate sentence-transformers sympy scikit-learn flask pillow"""),
    ("code", """# 3) Build training data from the verified book (split by unit; here: every 5th item is held out)
!python train/make_dataset.py --eval-units 0
assert os.path.exists("train/out/data/gen_sft.jsonl"), "Step 3 failed: see the error above"
"""),
    ("code", """# 4) Baseline retrieval with the untouched embedding model
!python train/evaluate.py --embed-model BAAI/bge-small-en-v1.5 --no-generation --report train/out/eval_base.json"""),
    ("code", """# 5) Fine-tune the embedding model
!python train/train_embeddings.py --epochs 3 --batch 32
assert os.path.exists("train/out/embed-ft/config.json"), "Step 5 failed: see the error above"
"""),
    ("code", """# 6) Retrieval after fine-tuning. Keep the new model only if recall@3 is higher than the baseline.
!python train/evaluate.py --embed-model train/out/embed-ft --no-generation --report train/out/eval_ft.json
import json
base = json.load(open("train/out/eval_base.json"))["retrieval"]
ft = json.load(open("train/out/eval_ft.json"))["retrieval"]
print("baseline:", base)
print("fine-tuned:", ft)"""),
    ("code", """# 7) LoRA fine-tune the generator (T4 fits the 1.5B model with gradient checkpointing; ~20-60 min for the sample data)
!python train/train_generator.py --epochs 3 --lr 1e-4
assert os.path.exists("train/out/gen-lora/adapter_config.json"), "Step 7 failed: see the error above"
"""),
    ("md", """If a step fails after the code was fixed on GitHub, rerun cell 1 (it pulls the update) and the install cell, then rerun from the failed step. Files from steps that passed stay in `train/out/` for the whole session. If Colab restarts, they are lost and you must start again from step 3."""),
    ("code", """# 8) Generation quality on the held-out items: valid JSON, verified steps, fully verified solutions
!python train/evaluate.py --embed-model train/out/embed-ft --gen-adapter train/out/gen-lora --report train/out/eval_gen.json
assert os.path.exists("train/out/eval_gen.json"), "Step 8 failed: see the error above"
print(open("train/out/eval_gen.json").read())"""),
    ("code", """# 9) Package the results for download
!cd train/out && zip -qr ../../math-tutor-trained.zip embed-ft gen-lora eval_base.json eval_ft.json eval_gen.json
from google.colab import files
files.download("math-tutor-trained.zip")"""),
]


def cell(kind, src):
    lines = src.split("\n")
    body = [l + "\n" for l in lines[:-1]] + [lines[-1]]
    if kind == "md":
        return {"cell_type": "markdown", "metadata": {}, "source": body}
    return {"cell_type": "code", "execution_count": None, "metadata": {}, "outputs": [], "source": body}


nb = {
    "cells": [cell(k, s) for k, s in CELLS],
    "metadata": {"accelerator": "GPU", "colab": {"provenance": []},
                 "kernelspec": {"display_name": "Python 3", "name": "python3"},
                 "language_info": {"name": "python"}},
    "nbformat": 4, "nbformat_minor": 5,
}
out = ROOT / "train" / "colab_train.ipynb"
out.write_text(json.dumps(nb, ensure_ascii=False, indent=1), encoding="utf-8")
print("wrote", out)
