# Deploying the tutor on Vercel

## What runs where

| Part | Runs on | Needs |
|---|---|---|
| Page, book, rule engine, retrieval, sympy checking | **Vercel** (Python function) | `flask`, `sympy` only (about 100 MB installed, limit 250 MB) |
| Writing a solution the engine cannot (the model) | Gemini **or** your own model service | one of the options below |
| Reading a photo into LaTeX (vision) | the same backend | the same option |

Vercel has no GPU and no room for torch, so the two neural models never run there. Without any model backend the site still
works for every question the engine and the book cover; photo reading is switched off and the page says so
(`GET /api/status` shows `{"model": null, "photo": null}`).

Every model answer is checked the same way whichever backend wrote it: each step is re-run with sympy, a reply with a
false check is retried (first greedy, then sampled), and one that still fails is shown as **unverified**.

## Nothing to retrain

- The book, the engine and retrieval are plain code and data in this repository. Adding an exercise means adding
  `data/src/*.py`, running `python tools/build_dataset.py`, and pushing. No training.
- The trained LoRA adapter (from the Kaggle run) is a one-time artifact. Publish it once with `tools/publish_models.py`; every
  model service downloads it from the Hub by name. Retraining is optional, only to improve the model on new question types.
- The Gemini option needs no training at all.

## Option A: Gemini (Google AI Studio or Vertex AI)

1. Create an API key (AI Studio: `GEMINI_API_KEY`; Vertex AI express mode: `VERTEX_API_KEY`).
2. On Vercel: Project > Settings > Environment Variables, add the key. Optional: `VERTEX_MODEL` (default `gemini-2.5-flash`;
   use a stronger model id if you want more accuracy), `VERTEX_THINKING_BUDGET`.
3. Redeploy. `/api/status` should show `"model": "vertex", "photo": "vertex"`.

Costs money per call and has rate limits. Question text and photos are sent to Google. Never commit the key.

## Option B: your own model service (Hugging Face Space or any GPU host)

1. Publish the adapter once: `set HF_TOKEN=...` then `python tools/publish_models.py --repo yourname/math-tutor-lora`.
2. Create a Space with SDK **Docker**, push this repository to it (the root `Dockerfile` builds `service/app.py`), and add
   `app_port: 7860` to the Space README front matter. Space variables: `GEN_ADAPTER=yourname/math-tutor-lora`, `SERVICE_TOKEN=<random>`;
   secret `HF_TOKEN` if the adapter repo is private.
3. On Vercel set `MODEL_SERVICE_URL=https://<space>.hf.space` and `MODEL_SERVICE_TOKEN=<the same random value>`.
4. `/api/status` should show `"model": "service", "photo": "service"`.

A free CPU Space can load the models but answers slowly (a model solution can take minutes, longer than Vercel's 60 s limit,
so the page then reports the service as unreachable). A GPU Space or other GPU host is what makes this practical.

## Vercel steps

1. Import the GitHub repository in Vercel (framework: Other). `vercel.json`, `api/index.py`, `requirements.txt` and
   `.python-version` are already set up; the page is served from `public/`.
2. Add the environment variables of the option you chose, then deploy.
3. Check `https://<your-site>/api/status`, then ask `(√8 + √3) / (√8 − √3)`: the answer is `(11 + 4√6)/5` without any model.

Notes: `maxDuration` is 60 s; what your plan allows is set by Vercel. Photos are shrunk in the browser to stay under Vercel's
4.5 MB request limit. Nothing is written to disk by the function. Keep `9th/`, page images and the answer key out of the
repository (they are in `.gitignore`); `.vercelignore` also keeps them out of the deployment.

## Local development

`python server.py` runs the same app on http://127.0.0.1:5057. Locally, with `models/` populated, the local models are used;
`MODEL_BACKEND=vertex|service|local` forces one.
