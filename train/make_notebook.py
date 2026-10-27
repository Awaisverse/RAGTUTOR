"""Generates train/colab_train.ipynb. Run:  python train/make_notebook.py"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent

CELLS = []


def md(text):
    CELLS.append(("md", text.strip("\n")))


def code(text):
    CELLS.append(("code", text.strip("\n")))


# =====================================================================================
md(r'''
# Math Tutor: training notebook (Punjab Class 9)

**Goal:** produce models that give *accurate* answers when plugged into the tutor, and **prove** they are accurate
before you integrate them. Nothing here calls a paid API: every model is a Hugging Face model trained on a free GPU (Colab or Kaggle).

## How accuracy is achieved (and measured)
| Layer | What makes it accurate |
|---|---|
| Retrieval | Questions in the book are answered with the stored, hand-checked solution. No generation at all. |
| Generator (new questions) | Fine-tuned on computed solutions (rule engine + generators), one part at a time, then every step is re-checked with sympy. |
| Training data | Synthetic questions come from Python solvers, so each answer is correct by construction. |
| Honest test | Exercise 1.2 is held out and never trained on. The score on its 26 parts is the one that matters. |
| Retries | A reply that fails its own sympy checks is discarded and the model tries again (first greedy, then sampled). |

## Phases
| Phase | What happens | Pass condition |
|---|---|---|
| 0 Setup | GPU, code, libraries, settings | GPU found |
| 1 Data | Verify the book, generate synthetic solved questions, build training files | 0 failed math checks |
| 2 Retrieval | Fine-tune the embedding model, keep it only if it is better | automatic decision |
| 3 Baseline | Score the *untuned* generator with retrieved examples in the prompt | numbers recorded |
| 4 Training | LoRA fine-tune the generator | adapter saved |
| 5 Evaluation | Score the tuned generator, compare with baseline, apply gates | gates A, B, C pass |
| 6 Export | Zip the models, write integration steps | zip downloaded |

## How to run
1. **First run with `QUICK_TEST = True`** (about 15 minutes). It checks that every phase works. The model it produces is not usable.
2. Set `QUICK_TEST = False` in the settings cell, then **Runtime > Restart and run all** (about 2 hours on a free T4).
3. If a cell fails, it stops with a clear message. Fix or retry from that cell; earlier results stay in `train/out/`.
''')

# =====================================================================================
md(r'''
## Phase 0: Setup
**Purpose:** make sure the GPU, code and libraries are ready, and set the run size.
**Time:** 2 to 4 minutes.
''')

code(r'''
# 0.1 GPU check (training and generation are far too slow on CPU)
import os
os.environ["CUDA_VISIBLE_DEVICES"] = "0"   # one GPU only (Kaggle offers two; the trainer would otherwise split every batch)
import torch
assert torch.cuda.is_available(), "No GPU found. Colab: Runtime > Change runtime type > GPU. Kaggle: Session options > Accelerator."
print("GPU:", torch.cuda.get_device_name(0), "| memory:", round(torch.cuda.get_device_properties(0).total_memory / 1e9, 1), "GB")
''')

code(r'''
# 0.2 SETTINGS. Change only this cell.
QUICK_TEST = True     # True: tiny run to test the pipeline (~15 min). False: the real run (~2 h).
USE_DRIVE = False     # True: copy results to Google Drive after each phase (survives a Colab restart)
HF_REPO = ""          # optional, e.g. "yourname/math-tutor": uploads the models to your private Hugging Face repo

if QUICK_TEST:
    SYNTH_PER_TYPE, ENGINE_PER_TYPE, EPOCHS_EMBED, EPOCHS_GEN, LIMIT_REAL, LIMIT_SYNTH = 4, 2, 1, 1, 2, 3
    BASE_REAL, BASE_SYNTH, ATTEMPTS = 2, 3, 2
else:
    SYNTH_PER_TYPE, ENGINE_PER_TYPE, EPOCHS_EMBED, EPOCHS_GEN, LIMIT_REAL, LIMIT_SYNTH = 25, 20, 3, 2, 0, 40   # 0 = evaluate every test item
    BASE_REAL, BASE_SYNTH, ATTEMPTS = 4, 8, 3     # the untuned model is only a reference point, so a small sample is enough
print("QUICK_TEST =", QUICK_TEST, "| synthetic per type:", SYNTH_PER_TYPE, "| generator epochs:", EPOCHS_GEN)
''')

code(r'''
# 0.3 Get the code, install libraries, define helpers
import json, os, subprocess

REPO_URL = "https://github.com/Awaisverse/RAGTUTOR.git"
IN_KAGGLE = os.path.exists("/kaggle/working")
REPO_DIR = "/tmp/RAGsystemfromnotes" if IN_KAGGLE else "/content/RAGsystemfromnotes"


def run(cmd):
    """Run a shell command, stream its output, and STOP the notebook if it fails."""
    print("$", cmd, flush=True)
    p = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    for line in p.stdout:
        print(line, end="")
    if p.wait() != 0:
        raise RuntimeError(f"FAILED (exit code {p.returncode}): {cmd}\nRead the output above for the cause.")


if os.path.exists(REPO_DIR):
    run(f"git -C {REPO_DIR} pull")
else:
    run(f"git clone {REPO_URL} {REPO_DIR}")
os.chdir(REPO_DIR)

run("pip -q uninstall -y torchao")   # Colab's old torchao breaks peft
run('pip -q install "transformers>=4.45" peft accelerate sentence-transformers sympy scikit-learn flask pillow')

USE_DRIVE = USE_DRIVE and not IN_KAGGLE   # Drive exists only on Colab
if USE_DRIVE:
    from google.colab import drive
    drive.mount("/content/drive")


def backup(tag):
    if USE_DRIVE:
        run(f"mkdir -p /content/drive/MyDrive/math-tutor && cp -r train/out /content/drive/MyDrive/math-tutor/out_{tag}")


print("ready in", os.getcwd())
''')

# =====================================================================================
md(r'''
## Phase 1: Data
**Purpose:** build everything the models learn from, and make sure none of it is wrong.
1. Re-check every hand-solved book item with sympy.
2. Generate synthetic solved questions (20 question types, including multi-part questions and drawn number lines) and re-check all of them.
   Add **engine** questions: Exercise 1.2 style questions with new numbers, solved by the rule engine and checked against an independent sympy answer.
   Any generated question that copies a real book question is removed, so the real test stays unseen.
3. Split: **all of Exercise 1.2 is held out** as the honest test (26 parts, one per example); generated questions get a separate test set with new numbers.
4. Split multi-part questions into **one part per example**, so replies are short and a slip in one part cannot spoil another.
5. Write the training files. Each generator example puts retrieved neighbours in the prompt, exactly like the real tutor.

**Time:** 1 to 2 minutes. **Pass:** every math check true.
**If it fails:** the message names the wrong step. Fix it in `data/src/` or `train/synth.py`, push to GitHub, rerun cell 0.3.
''')

code(r'''
# 1.1 The hand-solved book: every math step must verify
run("python tools/build_dataset.py --report")
''')

code(r'''
# 1.2 The synthetic generators: every math step must verify
run("python train/check_synth.py --per-type 60")
''')

code(r'''
# 1.3 Build training and test files
run(f"python train/make_dataset.py --eval-prefix ex1.2- --synth-per-type {SYNTH_PER_TYPE} --engine-per-type {ENGINE_PER_TYPE} --synth-eval-per-type 2")

rows = [json.loads(l) for l in open("train/out/data/gen_sft.jsonl", encoding="utf-8")]
pairs = sum(1 for _ in open("train/out/data/embed_pairs.jsonl", encoding="utf-8"))
assert len(rows) > 0 and pairs > 0, "No training data was produced"
print(f"\ngenerator examples: {len(rows)} | embedding pairs: {pairs}\n")
ex = rows[0]["messages"]
print("USER QUESTION :", ex[1]["content"][:200])
print("RETRIEVED CONTEXT in prompt (start):", ex[0]["content"].split("EXAMPLE 1")[1][:250].replace("\n", " "), "...")
print("TARGET ANSWER (start):", ex[2]["content"][:350], "...")
backup("phase1")
''')

# =====================================================================================
md(r'''
## Phase 2: Retrieval (embedding model)
**Purpose:** a student's question must find the right book item even when worded differently. The embedding model
(`BAAI/bge-small-en-v1.5`) is fine-tuned on question paraphrases.
**Time:** 3 to 10 minutes. **Pass:** automatic. The tuned model is used only if it is **strictly better** than the base model on the held-out
queries (Recall@3, then MRR). Otherwise the base model is kept, which is the safe choice.
**Note:** with a small book, both models usually score 1.0, so the base model is kept. That is expected until more items exist.
''')

code(r'''
# 2.1 Baseline: the untouched embedding model
run("python train/evaluate.py --tag retr_base --no-generation --embed-model BAAI/bge-small-en-v1.5")
''')

code(r'''
# 2.2 Fine-tune the embedding model on paraphrase pairs
run(f"python train/train_embeddings.py --epochs {EPOCHS_EMBED} --batch 32")
assert os.path.exists("train/out/embed-ft/config.json"), "Embedding training did not produce a model"
''')

code(r'''
# 2.3 Compare, then choose
run("python train/evaluate.py --tag retr_tuned --no-generation --embed-model train/out/embed-ft")
b = json.load(open("train/out/eval_retr_base.json"))["retrieval"]
t = json.load(open("train/out/eval_retr_tuned.json"))["retrieval"]
print("base :", b)
print("tuned:", t)
BASE_EMBED = "BAAI/bge-small-en-v1.5"
BEST_EMBED = "train/out/embed-ft" if (t["recall@3"], t["mrr"]) > (b["recall@3"], b["mrr"]) else BASE_EMBED
print("\nDECISION: use", "the FINE-TUNED embedding model" if BEST_EMBED != BASE_EMBED else "the BASE embedding model (tuning did not help)")
backup("phase2")
''')

# =====================================================================================
md(r'''
## Phase 3: Baseline generator (before training)
**Purpose:** measure the *untuned* `Qwen2.5-Math-1.5B-Instruct` on the test questions, with retrieved book examples in the prompt.
Without this number you cannot tell whether fine-tuning helped.
**Time:** 10 to 25 minutes (the model downloads once, about 3 GB, then writes a solution per test question).
**Metrics** (see `train/evaluate.py`): valid JSON, share of the model's own math checks that are true, fully verified solutions, final answer matches.
''')

code(r'''
# 3.1 Score the base model
run(f"python train/evaluate.py --tag gen_base --no-retrieval --attempts 1 --limit-real {BASE_REAL} --limit-synth {BASE_SYNTH}")
print(json.dumps(json.load(open("train/out/eval_gen_base.json"))["generation"], indent=1))
backup("phase3")
''')

# =====================================================================================
md(r'''
## Phase 4: Train the generator (LoRA)
**Purpose:** teach the model to write the exact solution format, with correct, sympy-checkable steps, using retrieved examples as guidance.
Only the answer part of each example is learned; the prompt and retrieved context are masked out of the loss.
**Time:** 60 to 80 minutes on a T4 in the full run (about 2 minutes in quick mode).
**If you see "out of memory":** lower `--max-len` to 2560 or `--neighbours` to 1 in `make_dataset.py`, and retrain.
''')

code(r'''
# 4.1 LoRA fine-tune
run(f"python train/train_generator.py --epochs {EPOCHS_GEN} --lr 2e-4")
assert os.path.exists("train/out/gen-lora/adapter_config.json"), "Generator training did not produce an adapter"
backup("phase4")
''')

# =====================================================================================
md(r'''
## Phase 5: Evaluate and decide
**Purpose:** score the tuned generator on the same test questions and decide whether it is safe to integrate.

| Gate | Meaning | Needed to integrate |
|---|---|---|
| A | tuned replies are valid JSON (at least 95%) on both test sets | yes |
| B | verified-step rate is not worse than the baseline on both sets | yes |
| C | fully-verified rate on the **real** book questions is not worse than the baseline | yes |
| D | release target: at least 90% fully verified **and** at least 90% correct final answer on the real questions | for a trustworthy tutor |

**How answers are compared:** `answer_match` accepts the same final numbers and signs in the same order (so "15.29%" and "15.29% loss" agree, but "5/9" and "9/5" do not),
and requires text answers such as property names to match exactly. `answer_exact` is the strict comparison, shown for reference.
A reply whose LaTeX backslashes were mis-escaped is repaired before it is scored; the repaired count is reported.

**Time:** 15 to 30 minutes.
''')

code(r'''
# 5.1 Score the tuned generator
run(f"python train/evaluate.py --tag gen_tuned --no-retrieval --gen-adapter train/out/gen-lora --attempts {ATTEMPTS} --limit-real {LIMIT_REAL} --limit-synth {LIMIT_SYNTH}")
''')

code(r'''
# 5.2 Compare with the baseline and apply the gates
base = json.load(open("train/out/eval_gen_base.json"))["generation"]
tuned = json.load(open("train/out/eval_gen_tuned.json"))["generation"]
metrics = ["json_valid", "verified_step_rate", "fully_verified", "answer_match", "answer_exact"]

print(f"{'set':6} {'metric':20} {'base':>7} {'tuned':>7}")
for s in ("real", "synth"):
    for m in metrics:
        print(f"{s:6} {m:20} {base[s][m]:7.3f} {tuned[s][m]:7.3f}")
    print(f"{'':6} {'test items':20} {base[s]['items']:7d} {tuned[s]['items']:7d}")
    print(f"{'':6} {'first try fully_ver.':20} {base[s]['first_try']['fully_verified']:7.3f} {tuned[s]['first_try']['fully_verified']:7.3f}   (without retries)")
    print(f"{'':6} {'first try answer':20} {base[s]['first_try']['answer_match']:7.3f} {tuned[s]['first_try']['answer_match']:7.3f}   avg tries {tuned[s]['avg_tries']}")

gates = {
    "A  valid JSON >= 0.95 on both sets": all(tuned[s]["json_valid"] >= 0.95 for s in tuned),
    "B  verified-step rate >= baseline on both sets": all(tuned[s]["verified_step_rate"] >= base[s]["verified_step_rate"] for s in tuned),
    "C  fully-verified on REAL >= baseline": tuned["real"]["fully_verified"] >= base["real"]["fully_verified"],
    "D  REAL: fully-verified >= 0.90 and answer match >= 0.90": tuned["real"]["fully_verified"] >= 0.90 and tuned["real"]["answer_match"] >= 0.90,
}
print()
for name, ok in gates.items():
    print("PASS" if ok else "FAIL", "|", name)

gate_a, gate_b, gate_c, gate_d = gates.values()
can_integrate = gate_a and gate_b and gate_c
trustworthy = can_integrate and gate_d
print()
if QUICK_TEST:
    print("QUICK_TEST is on: these numbers only prove the pipeline runs. Set QUICK_TEST = False and run everything again.")
elif trustworthy:
    print("RESULT: the tuned model passes every gate. Safe to integrate.")
elif can_integrate:
    print("RESULT: better than the baseline, but below the 90% accuracy target. Integrate only with the sympy verification on and the 'unverified' label visible. Add more data (see below) to reach the target.")
else:
    print("RESULT: do NOT integrate this model. See the failures below.")
''')

code(r'''
# 5.3 Look at the failures (this tells you what data to add next)
items = [json.loads(l) for l in open("train/out/eval_gen_tuned_items.jsonl", encoding="utf-8")]
bad = [r for r in items if not (r["json_valid"] and r["fully_verified"] and r["answer_match"])]
print(f"{len(bad)} of {len(items)} test questions were not fully correct\n")
for r in bad[:5]:
    print("SET     :", r["set"], "|", r["id"])
    print("QUESTION:", r["question"][:160])
    print("GOLD    :", r["gold_answers"])
    print("MODEL   :", r["model_answers"], "| checks passed", f"{r['checks_ok']}/{r['checks']}", "| valid JSON:", r["json_valid"])
    if not r["json_valid"]:
        print("REPLY START:", r["raw"][:200].replace("\n", " "))
        print("REPLY END  :", r["raw"][-250:].replace("\n", " "), f"  (length {len(r['raw'])} chars; cut off = ends mid-sentence)")
    print()
backup("phase5")
''')

# =====================================================================================
md(r'''
## Phase 6: Export and integrate
**Purpose:** package the models and write the exact steps to plug them into the tutor.
The zip contains the generator adapter (a few MB), the embedding model only if it beat the base model, the evaluation reports and `INTEGRATION.txt`.

**After downloading:**
1. Download the zip (Colab downloads it automatically; on Kaggle use the Output tab or `python tools/kaggle_run.py --fetch`). Unzip into your project folder so that `models/gen-lora/` exists (and `models/embed-ft/` if included).
2. Download the base models once: `python tools/download_model.py Qwen/Qwen2.5-Math-1.5B-Instruct models/Qwen2.5-Math-1.5B-Instruct`
3. Run `python server.py` (with `EMB_MODEL=models/embed-ft` if the embedding model is included).
4. Ask a book question (it must come straight from the book), then a new question of the same type (it must be solved and show all checks passing).

**Time:** 1 to 2 minutes.
''')

code(r'''
# 6.1 Package
import shutil, zipfile

use_embed = "BEST_EMBED" in globals() and BEST_EMBED != "BAAI/bge-small-en-v1.5"
notes = [
    "MATH TUTOR: trained models",
    f"QUICK_TEST run: {QUICK_TEST}" + ("  <-- NOT a real model, do not integrate" if QUICK_TEST else ""),
    "",
    "1. Unzip into the project folder: models/gen-lora/" + (" and models/embed-ft/" if use_embed else ""),
    "2. python tools/download_model.py Qwen/Qwen2.5-Math-1.5B-Instruct models/Qwen2.5-Math-1.5B-Instruct",
    ("3. EMB_MODEL=models/embed-ft python server.py" if use_embed else "3. python server.py"),
    "",
    "Evaluation (tuned generator):",
    json.dumps(tuned, indent=1),
]
open("train/out/INTEGRATION.txt", "w").write("\n".join(notes))

os.makedirs("export", exist_ok=True)
for name in ("gen-lora",) + (("embed-ft",) if use_embed else ()):
    shutil.copytree(f"train/out/{name}", f"export/{name}", dirs_exist_ok=True)
for f in ("eval_retr_base.json", "eval_retr_tuned.json", "eval_gen_base.json", "eval_gen_tuned.json", "eval_gen_tuned_items.jsonl", "INTEGRATION.txt"):
    shutil.copy(f"train/out/{f}", f"export/{f}")
ZIP_BASE = "/kaggle/working/math-tutor-trained" if IN_KAGGLE else "math-tutor-trained"   # Kaggle keeps files in /kaggle/working
shutil.make_archive(ZIP_BASE, "zip", "export")
print("zip:", ZIP_BASE + ".zip", "| size (MB):", round(os.path.getsize(ZIP_BASE + ".zip") / 1e6, 1))
''')

code(r'''
# 6.2 Optional: upload to a private Hugging Face repo (add a secret named HF_TOKEN first)
if HF_REPO:
    try:
        from google.colab import userdata
        hf_token = userdata.get("HF_TOKEN")
    except ImportError:
        from kaggle_secrets import UserSecretsClient
        hf_token = UserSecretsClient().get_secret("HF_TOKEN")
    from huggingface_hub import HfApi
    api = HfApi(token=hf_token)
    api.create_repo(HF_REPO, private=True, exist_ok=True)
    api.upload_folder(folder_path="export", repo_id=HF_REPO)
    print("uploaded to https://huggingface.co/" + HF_REPO)
else:
    print("HF_REPO is empty: skipping the upload")
''')

code(r'''
# 6.3 Download
if IN_KAGGLE:
    print("Kaggle: the zip is saved in the notebook output. Download it from the Output tab, or run tools/kaggle_run.py --fetch")
else:
    from google.colab import files
    files.download("math-tutor-trained.zip")
''')

md(r'''
## What to do next to raise accuracy
Accuracy comes from data, not from more epochs. In order of value:
1. **Read the failures (cell 5.3).** If one question type fails, add a generator for it in `train/synth.py` (a solver that picks numbers, computes the solution, writes the steps, and adds sympy checks).
2. **Add the book's exercises** to `data/src/`. Each one becomes retrieval content (answered with the stored solution) and real test data.
3. **Collect real student questions** and use them as paraphrases for the embedding model.
4. **Try the 7B model** (`Qwen/Qwen2.5-Math-7B-Instruct`) if the 1.5B model cannot reach the target. It needs a larger GPU.
''')


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
print("wrote", out, "-", len(CELLS), "cells")

# Kaggle copy: same cells; QUICK_TEST is set by the command line (--full for the real run)
full = "--full" in sys.argv
kb = json.loads(json.dumps(nb))
for c in kb["cells"]:
    if c["cell_type"] == "code":
        text = "".join(c["source"])
        if "QUICK_TEST = True " in text:
            text = text.replace("QUICK_TEST = True ", f"QUICK_TEST = {not full} ", 1)
            c["source"] = text.splitlines(keepends=True)
kb["metadata"]["accelerator"] = "GPU"
kdir = ROOT / "kaggle"
kdir.mkdir(exist_ok=True)
(kdir / "math-tutor-train.ipynb").write_text(json.dumps(kb, ensure_ascii=False, indent=1), encoding="utf-8")
(kdir / "kernel-metadata.json").write_text(json.dumps({
    "id": "awaisverse/math-tutor-train", "title": "math-tutor-train", "code_file": "math-tutor-train.ipynb",
    "language": "python", "kernel_type": "notebook", "is_private": True, "enable_gpu": True,
    "enable_tpu": False, "enable_internet": True, "dataset_sources": [], "competition_sources": [],
    "kernel_sources": [], "model_sources": []}, indent=2), encoding="utf-8")
print("wrote kaggle/ (QUICK_TEST =", not full, ")")
