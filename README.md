# RAG Math Tutor (Punjab Class 9)

Ask a question (typed or from a photo) and get a step-by-step solution drawn on an animated board, with English and Urdu explanations. Runs on local Hugging Face models; no API keys.

See `docs/PLAN.md` for the full design.

## Train on Colab

[Open the notebook in Colab](https://colab.research.google.com/github/Awaisverse/RAGTUTOR/blob/main/train/colab_train.ipynb)
(set the runtime to GPU, then run all cells). It builds the training data, fine-tunes the embedding model and the generator (LoRA), evaluates them, and produces `math-tutor-trained.zip`.

Unzip it into the project so these exist:

```
models/embed-ft/
models/gen-lora/
```

## Run locally

```
pip install flask scikit-learn sentence-transformers transformers peft sympy pillow
# download the base models into models/ (see tools/download_model.py)
python tools/download_model.py Qwen/Qwen2.5-Math-1.5B-Instruct models/Qwen2.5-Math-1.5B-Instruct
EMB_MODEL=models/embed-ft python server.py      # then open http://127.0.0.1:5057
```

Without the generator and vision models the book search and the animated board still work; live solving and photo reading return a clear "model not found" message.

## Data

- `data/src/` solutions authored in Python (source of truth); `data/SCHEMA.md` describes the format.
- `python tools/build_dataset.py` checks every math step with sympy and writes `data/book/*.json`.
- The textbook PDF and page images are not in this repository.
