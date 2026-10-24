# Math Tutor for Punjab Class 9: Own RAG System Plan

Written for: the project owner and any developer who will build or maintain this system.

## 1. Goal

A tutor where a student can:
1. type a question, or upload a photo of one;
2. get the right solved answer, shown step by step on an animated board, with an English or Urdu explanation;
3. get a live solution for questions that are not in the book, grounded in the book's method.

Scope for v1: the Class 9 Mathematics book (Punjab textbook 2026, 288 pages). Units 1 and 2 first, then the rest.

Principle: **no closed-source API in the loop.** Every model is a Hugging Face model that we host and can run offline. Math correctness is enforced by a symbolic checker (sympy), not by trusting the model.

## 2. Architecture

```
            ┌──────────── OFFLINE: build the knowledge base ────────────┐
 Book PDF → page images → OCR / manual labeling → structured JSON (items)
                                   │
                                chunking  (one chunk per question part)
                                   │
                    embeddings (fine-tuned bge-small, HF)
                                   │
                 vector index (FAISS)  +  lexical index (BM25)
            └───────────────────────────────────────────────────────────┘

            ┌──────────── ONLINE: answer a student ─────────────────────┐
 text or photo → [vision model, HF: Qwen2-VL-2B]  (photo → question, exercise, number, part)
               → query normalisation
               → hybrid retrieval (dense + BM25, RRF fusion)
               → decision:
                   exact match by number  → show stored verified solution
                   strong match           → show stored verified solution
                   weak match             → generator with retrieved examples (RAG)
               → generator [HF: Qwen2.5-Math-1.5B-Instruct, LoRA fine-tuned]
               → verifier (sympy checks every step; failing steps are rejected)
               → board renderer (canvas animation, KaTeX maths, EN/UR explanation)
            └───────────────────────────────────────────────────────────┘
```

### Components and model choices

| Component | Hugging Face model (start) | Why | Size / CPU feasible |
|---|---|---|---|
| Embeddings | `BAAI/bge-small-en-v1.5` | strong for its size, runs on CPU | 33M params, yes |
| Embeddings (Urdu queries) | `intfloat/multilingual-e5-small` | handles Urdu and English | 118M, yes |
| Reranker (optional) | `BAAI/bge-reranker-base` | re-orders the top 10 hits | 278M, yes |
| Vision: photo reading | `Qwen/Qwen2-VL-2B-Instruct` | reads printed math and layout | 2B, needs ~8 GB RAM, slow on CPU |
| Vision: OCR fallback | `microsoft/trocr-base-printed` or PaddleOCR | cheaper text reading | small |
| Generator (live solving) | `Qwen/Qwen2.5-Math-1.5B-Instruct`, LoRA fine-tuned | maths-tuned, small enough to fine-tune | 1.5B, GPU for training, CPU ok for inference (slow) |
| Generator (bigger option) | `Qwen/Qwen2.5-Math-7B-Instruct` | better accuracy | needs GPU ≥ 16 GB |
| Verifier | sympy (not a model) | exact, deterministic | — |

Hardware today: CPU only, no CUDA GPU. Training runs need a free GPU (Kaggle or Colab) or a rented one. Inference runs on CPU with the small models; the 1.5B generator will be slow on CPU (tens of seconds per solution), so GPU or a quantised build is needed for a good student experience.

## 3. Data

### 3.1 Sources
- `9th/…taleem360….pdf`: 288 pages, scanned images with no text layer. Page images were extracted to `data/pages/` (white background, see `tools/extract_pages.py`).
- `ch01-matric-science.pdf`: science book, out of scope for v1.

### 3.2 Structured dataset (the source of truth)
Every question becomes one JSON item in `data/book/unitNN.json`, described in `data/SCHEMA.md`:
- `id`, `kind` (example / exercise / review), `exercise`, `number`, `page`
- `question`, `parts[]` with `label`, `prompt`, `steps[]`, `answer`
- each step: `math` (LaTeX), `en`, `ur`, `check[]` (sympy), `draw[]` (figure commands)

Rule: **a step with no `check` is not allowed for computed values.** The build (`tools/build_dataset.py`) fails if any check is false.

### 3.3 Labeling workflow (how the data grows)
1. OCR the page image (or type from the image).
2. Write the item in Python under `data/src/unitNN.py` using the helpers in `_helpers.py`.
3. Run `python tools/build_dataset.py`. It must report 0 failed checks.
4. A second person reviews the Urdu and the figure.
5. Items enter the index only after step 4.

Target: all examples and exercises in Units 1–8, about 600–800 items. Estimated effort: 2–4 minutes per item for a careful writer; the first unit took the longest.

### 3.4 Synthetic data (for training, not for the answer key)
- **Paraphrases:** for each question, generate 5–10 rewordings (student style, short, with and without LaTeX, Urdu-English mix). Use the generator model or hand-written templates. These become training pairs for embeddings.
- **Parameter variants:** change the numbers in a question and recompute the answer with sympy. This gives many verified problems from one solved template.
- **Negatives:** questions from other units, and near-miss questions (same wording, different number), for hard-negative mining.

Every synthetic item is marked `"synthetic": true` and is never used as the test set.

### 3.5 Splits (to prevent leakage)
- Split by **unit**, not by item. Example: train on Units 1–6, validate on 7, test on 8. Paraphrases and variants of an item stay in the same split as the item.
- Keep a frozen test set of real student-style photos (see 6.4) that no one tunes against.

## 4. RAG pipeline (step by step)

### Step 1: Ingest
Read JSON items, validate with `build_dataset.py`, write `data/book/*.json`.

### Step 2: Chunk
- One chunk per **question part**: question text + part prompt + answer. This is the retrieval unit, because a student asks about one part.
- Steps are not separate chunks. They are returned together with the chunk they belong to.
- Keep chunks under ~256 tokens. Long multi-part questions are split by part.
- Each chunk carries metadata: `id`, `part`, `unit`, `exercise`, `number`, `page`, `kind`, `synthetic`.

### Step 3: Normalise text
Convert LaTeX and plain maths to words so `\sqrt{5}`, `sqrt5` and `sqrt 5` are the same (`rag.normalize`). Keep the raw form for display.

### Step 4: Embed
- Model: `bge-small-en-v1.5` (start), fine-tuned in Section 5.
- Queries get the instruction prefix the model expects (`Represent this sentence for searching relevant passages: `). Check the model card for the exact prefix.
- Store vectors with `normalize_embeddings=True`; use cosine similarity.
- Cache to disk, keyed by a hash of the chunk texts, so changing one item only re-embeds that item.

### Step 5: Index
- Dense: FAISS `IndexFlatIP` (exact, fine up to ~100k chunks).
- Lexical: BM25 over normalised text (`rank-bm25`) or the TF-IDF already in `rag.py`.

### Step 6: Retrieve (hybrid)
- Get top 20 from dense and top 20 from BM25.
- Fuse with Reciprocal Rank Fusion, `score = Σ 1/(60 + rank)`.
- Rerank the top 10 with `bge-reranker-base` (optional, measure first whether it helps).
- Return the top 3 chunks with scores.

### Step 7: Decide (routing)
| Condition | Action |
|---|---|
| Photo gives exercise + number and that item exists | show the stored solution for that part (no generation) |
| Top chunk is a near-paraphrase (dense cosine ≥ threshold T1 calibrated on the validation set) | show the stored solution |
| Top chunk is related but not the same | generate, with the top 3 chunks as worked examples |
| Nothing relevant | say so, and offer to solve with the generator with no examples, marked "unverified" |

Thresholds T1 are calibrated on the validation split to a target precision (for example 98% of accepted matches must be correct).

### Step 8: Generate (RAG)
- Prompt = system rules (JSON schema, check rules, draw command list) + retrieved examples + the student's question.
- The generator is the LoRA-tuned Qwen2.5-Math model. It must output the JSON schema only.
- Decoding: greedy or low temperature (0–0.2), because maths should be deterministic.

### Step 9: Verify
- Parse the JSON. On failure, retry once with the parse error appended.
- Run every `check` through sympy (`tools/build_dataset.verify`).
- If a step fails: retry once with the failing step quoted back to the model. If it still fails, mark the solution as unverified and show a warning. Never present an unverified answer as checked.
- Only verified solutions can be added to the book index (after human review).

### Step 10: Present
- Board animation: steps appear one at a time; geometry figures are drawn with the `draw` commands.
- Explanation panel: English, Urdu, or both.
- Show where the answer came from: "from the book", "solved, all checks passed", or "solved, unverified".

## 5. Training

Training is needed in three places. Do them in this order, because each one needs the previous to be measured.

### 5.1 Embedding model (do first; cheapest, biggest gain)
- Base: `bge-small-en-v1.5`.
- Data: positive pairs of (question, paraphrase of the same question). Negatives: in-batch negatives plus mined hard negatives (same unit, different answer).
- Loss: `MultipleNegativesRankingLoss` in `sentence-transformers`.
- Settings to start: 3 epochs, batch 64, lr 2e-5, warmup 10%. About 10–30 minutes on a free GPU for ~5k pairs; a few hours on CPU.
- Gate: keep the new model only if validation Recall@3 improves over the base model by a clear margin (target ≥ 5 points) without hurting the test split.

### 5.2 Generator (LoRA on the maths model)
- Base: `Qwen2.5-Math-1.5B-Instruct`.
- Method: LoRA (rank 16, alpha 32, on attention and MLP projections), 4-bit quantised base if memory is tight (`bitsandbytes`).
- Data: for each verified item, a training example = (system rules + 3 retrieved neighbours from the training split, student question) → target JSON solution. Include some examples with no good neighbour so the model learns to work from scratch.
- Settings to start: 2–3 epochs, lr 1e-4, batch 8 with gradient accumulation, max length 2048.
- Time: about 1–3 hours on one 16 GB GPU for ~3k examples.
- Gate: the verified-solution rate on the validation set must rise over the base model, and the number of sympy-failing steps must fall.

### 5.3 Vision (photo reading)
- Option A (start): use `Qwen2-VL-2B-Instruct` zero-shot with the reading prompt. Measure first; often good enough.
- Option B (if A is weak): fine-tune Qwen2-VL-2B with LoRA on ~300 labelled photos (image → the JSON reading). Labels come from the structured dataset: photograph the printed page or render it, and pair with the known exercise and number.
- Option C (cheap fallback): OCR with `trocr` or PaddleOCR, then regex for "Exercise N.M" and "N." patterns.
- Gate: exercise and number read correctly on ≥ 90% of the held-out photos.

### 5.4 What is NOT trained
- The verifier: sympy, no training.
- The routing thresholds: calibrated on validation data, not learned.

## 6. Evaluation

### 6.1 Retrieval
- Recall@1, Recall@3, MRR on the test split, with paraphrase queries.
- Compare: TF-IDF only, dense base, dense fine-tuned, hybrid, hybrid + rerank.

### 6.2 Generation
- Verified-solution rate: share of generated solutions where all sympy checks pass.
- Answer accuracy: final answer matches the book's answer (sympy equivalence, not string match) on the test split.
- Step count and length sanity (no runaway output).

### 6.3 Explanations and Urdu
- Human rating 1–5 on a sample of 50 explanations per language: clarity, correctness, Urdu fluency.
- Automatic checks: every step has non-empty `en` and `ur`; Urdu text contains Urdu script.

### 6.4 End-to-end
- A frozen set of 100 real student-style photos and typed questions, with known correct answers.
- Metrics: correct answer shown, correct part selected, time to first step, and how often the system says "unverified".

### 6.5 Release criteria (v1)
- Retrieval Recall@3 ≥ 0.95 on paraphrase queries.
- Photo reading ≥ 90% exercise and number accuracy.
- End-to-end correct answer ≥ 90% on the frozen set; unverified answers clearly labelled 100% of the time.
- Human review passes for Urdu on a sample.

## 7. Serving

- Backend: FastAPI or the existing Flask app. Routes stay as they are (`/api/ask`, `/api/photo`, `/api/solve`, `/api/item/<id>`), with the model calls swapped for local HF inference.
- Model loading: load each model once at start-up. Embeddings and the vision model on CPU; the generator on GPU when available, else quantised CPU with a clear "slow" notice.
- Caching: cache solutions by normalised question so a repeated question is instant.
- Storage: items in JSON in git; embeddings and FAISS index as build artefacts (rebuilt by a script); generated solutions in `data/generated/` for review.

## 8. Feedback loop (how the system improves)

- Each solution has 👍 / 👎 and "wrong step" buttons. Stored with the question, the retrieved neighbours and the model version.
- Weekly: a reviewer checks the 👎 items. Corrected items go into `data/src/` and the next build.
- Verified student-generated solutions are added as synthetic-but-reviewed training data for the next embedding and generator run.
- Every retrain is compared against the frozen test set before it replaces the current model.

## 9. Repository layout (target)

```
data/
  pages/            page images (generated, git-ignored)
  src/              authoring files (unitNN.py) — source of truth
  book/             built JSON items (unitNN.json)
  index/            embeddings and FAISS index (rebuilt)
  generated/        live solutions awaiting review
  eval/             frozen test sets (never tune on these)
tools/              extract_pages.py, build_dataset.py
rag/                chunking, embedding, indexing, retrieval, routing, verification
train/              embed_train.py, generator_lora.py, vision_lora.py
eval/               retrieval_eval.py, generation_eval.py, e2e_eval.py
server.py           web API
static/             whiteboard UI
docs/PLAN.md        this file
```

## 10. Milestones

| # | Milestone | Done when |
|---|---|---|
| M0 | Pipeline works end to end with TF-IDF + 14 items | done |
| M1 | Units 1–2 fully authored, all checks pass | 0 failed checks, reviewed Urdu |
| M2 | Hybrid retrieval + bge-small baseline measured | Recall@3 table in `eval/` |
| M3 | Embedding fine-tune; keep if it beats baseline | validation gate in 5.1 met |
| M4 | Generator LoRA; verified-solution rate measured | gate in 5.2 met |
| M5 | Photo reading (Qwen2-VL zero-shot), measured | ≥ 90% on held-out photos, or fine-tune (5.3B) |
| M6 | All units authored (about 600–800 items) | build passes, reviewed |
| M7 | v1 release criteria met (Section 6.5) | frozen-set report signed off |
| M8 | Feedback loop running | weekly review in place |

Estimated effort for one developer part-time: M1 ~2–3 weeks (authoring dominates), M2–M5 ~3–4 weeks, M6 ~2–3 months (authoring), M7–M8 ~1 week. Authoring is the bottleneck, not training.

## 11. Risks and mitigations

| Risk | Mitigation |
|---|---|
| Too little labelled data for fine-tuning | Authoring first; parameter variants and paraphrases; gate every fine-tune on a validation set |
| Generator makes maths errors | sympy verification on every step; unverified answers are labelled; retrieval first so generation is rare |
| Urdu quality | human review sample; keep Urdu explanations short and simple; glossary of maths terms |
| CPU-only inference is slow | small models; cache; GPU or quantised model for the generator |
| Scanned book quality, OCR errors | human check of every OCR'd item before build; build fails on bad maths |
| Copyright: book is marked "NOT FOR SALE" | internal educational use only; do not redistribute the page images; keep images out of the public repo |
| Students photograph the wrong page | the reading step reports what it found; the UI shows the detected exercise and number so the student can correct it |
| Overfitting to the test set | frozen test set, touched only for final reports |

## 12. Decisions needed from the owner

1. **Hardware:** will there be a GPU for training (Kaggle / Colab / rented), and is CPU-only inference acceptable for the first release?
2. **Generator size:** 1.5B (fast, weaker) or 7B (better, needs ≥ 16 GB GPU at inference)?
3. **Urdu:** should Urdu explanations be machine-written and reviewed, or written by a teacher?
4. **Scope:** which units must be complete before a first release?
5. **Users:** who will test the system (students, teachers), and who will do the weekly review?

## 13. Immediate next steps

1. Run the embedding baseline: measure bge-small on the 14 items with paraphrase queries. This is the first real number for the project.
2. Author Unit 1 exercises (about 60 questions). This gives the first meaningful test set.
3. Write `eval/retrieval_eval.py` and the frozen test split (by unit).
4. Decide the answers to Section 12.

## 14. Current implementation: local only, trained on Colab

No API keys are used anywhere. Every model runs from `models/` on the owner's machine.

| Piece | File | Notes |
|---|---|---|
| Local models | `local_models.py` | generator (Qwen2.5-Math-1.5B + optional LoRA), vision (Qwen2-VL-2B). Loaded lazily; GPU if present, else CPU |
| Shared prompts | `prompts.py` | solver rules and photo-reading prompt, used by server and training |
| Retrieval | `rag.py` | chunking, normalisation, hybrid search (bge embeddings + TF-IDF, RRF). `EMB_MODEL` picks the embedding folder |
| Dataset for training | `train/make_dataset.py` | embedding pairs and generator examples; split by unit; neighbours exclude the item itself |
| Embedding fine-tune | `train/train_embeddings.py` | MultipleNegativesRankingLoss |
| Generator LoRA | `train/train_generator.py` | loss on the solution only; prompt and retrieved examples masked |
| Evaluation | `train/evaluate.py` | retrieval recall@1/3, MRR (base vs fine-tuned); generation JSON validity and sympy-verified rate |
| Colab | `train/colab_train.ipynb` (built by `train/make_notebook.py`) | runs all steps on a free GPU and produces `math-tutor-trained.zip` |
| Server | `server.py` | routes unchanged; answers come from local models; returns 503 when a model folder is missing |

### Workflow
1. Author or fix items in `data/src/`, run `python tools/build_dataset.py`.
2. Open `train/colab_train.ipynb` in Colab (GPU), set `REPO_URL`, run all cells.
3. Download `math-tutor-trained.zip`, unzip so that `models/embed-ft/` and `models/gen-lora/` exist.
4. Compare `eval_base.json` and `eval_ft.json`. Keep the fine-tuned embedding model only if recall@3 is higher.
5. Run locally: `EMB_MODEL=models/embed-ft python server.py`. The generator adapter is picked up from `models/gen-lora/`.

### Gates before a model replaces the current one
- Embeddings: validation recall@3 higher than the base model.
- Generator: JSON validity and verified-step rate higher than the base model on the same held-out items.
- Vision: manual check on a set of real photos (not yet automated; see Section 5.3).

### Known limits of the current data
- Only 14 worked examples exist, so training and evaluation are a pipeline check, not a quality measure. Results only become meaningful after Unit 1 exercises are authored (Section 10, M1).
- Paraphrases are generated from the question text itself. Real student paraphrases should replace them when collected.
