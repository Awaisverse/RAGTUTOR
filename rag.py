"""Retrieval layer: chunk the solved book, index it two ways, and search with hybrid fusion.

Pipeline
  1. Chunk     one chunk per question part (question text + part prompt + final answer).
               Long solutions are not embedded; their steps are returned with the chunk.
  2. Embed     BAAI/bge-small-en-v1.5 from Hugging Face (local, ~130 MB, CPU is fine).
  3. Lexical   TF-IDF over normalized math text (catches exact symbols like "sqrt", "10^-4").
  4. Fuse      Reciprocal Rank Fusion of the embedding and lexical rankings.
  5. Decide    a match is accepted only if its best cosine similarity or its lexical score
               clears a threshold. Otherwise the caller falls back to live solving, with the
               nearest book chunks passed in as worked examples.
"""
import json
import os
import pathlib
import re

import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = pathlib.Path(__file__).resolve().parent
BOOK = ROOT / "data" / "book"
EMB_MODEL = os.environ.get("EMB_MODEL", "BAAI/bge-small-en-v1.5")  # or a local folder from train/
EMB_CACHE = ROOT / "data" / "index" / "embeddings.npz"
RRF_K = 60
COS_ACCEPT = 0.80     # bge-small: near-paraphrase questions score about 0.85+
LEX_ACCEPT = 0.22     # tf-idf cosine; below this the lexical side has no real overlap


def normalize(text):
    """LaTeX and plain math -> plain words, so 'sqrt5', '\\sqrt{5}' and 'sqrt 5' look the same."""
    t = re.sub(r"\\(?:left|right)", "", text)
    t = re.sub(r"\\([a-zA-Z]+)", r" \1 ", t)
    t = re.sub(r"[{}$^_()\[\]\\]", " ", t)
    t = re.sub(r"([a-zA-Z])(\d)", r"\1 \2", t)
    t = re.sub(r"(\d)([a-zA-Z])", r"\1 \2", t)
    return re.sub(r"\s+", " ", t).strip().lower()


def chunk_item(item):
    """Yield retrieval chunks: one per part, carrying the item's metadata."""
    base = {k: item.get(k) for k in ("id", "unit", "unit_title", "exercise", "number", "kind", "page")}
    for p in item["parts"]:
        text = " ".join(filter(None, [item["question"], p.get("prompt", ""), p.get("label", ""), p.get("answer", "")]))
        yield {**base, "part": p.get("label", ""), "text": text, "question": item["question"]}


def load_chunks():
    chunks = []
    for path in sorted(BOOK.glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            it["unit_title"] = unit["title"]
            chunks.extend(chunk_item(it))
    return chunks


class Index:
    def __init__(self, chunks, use_embeddings=True):
        self.chunks = chunks or []
        docs = [normalize(c["text"]) for c in self.chunks] or ["empty"]
        self.tfidf_word = TfidfVectorizer(ngram_range=(1, 2), token_pattern=r"(?u)\b\w+\b")
        self.tfidf_char = TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))
        self.Xw = self.tfidf_word.fit_transform(docs)
        self.Xc = self.tfidf_char.fit_transform(docs)
        self.model = None
        self.E = None
        if use_embeddings and self.chunks:
            self._load_embeddings(docs)

    # ---- embeddings (Hugging Face model, cached to disk) ----
    def _load_embeddings(self, docs):
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(EMB_MODEL)
        ids = [c["id"] + "|" + c["part"] for c in self.chunks]
        if EMB_CACHE.exists():
            cached = np.load(EMB_CACHE, allow_pickle=True)
            if list(cached["ids"]) == ids:
                self.E = cached["E"]
                return
        self.E = self.model.encode(docs, normalize_embeddings=True, batch_size=32, show_progress_bar=False)
        EMB_CACHE.parent.mkdir(parents=True, exist_ok=True)
        np.savez(EMB_CACHE, ids=np.array(ids, dtype=object), E=self.E)

    def _embed_query(self, q):
        if self.model is None:
            return None
        return self.model.encode([normalize(q)], normalize_embeddings=True)[0]

    # ---- search ----
    def search(self, query, k=3):
        if not self.chunks or not query.strip():
            return []
        qn = normalize(query)
        lex = 0.5 * (self.Xw @ self.tfidf_word.transform([qn]).T).toarray().ravel() \
            + 0.5 * (self.Xc @ self.tfidf_char.transform([qn]).T).toarray().ravel()
        qe = self._embed_query(query)
        cos = self.E @ qe if qe is not None else np.zeros(len(self.chunks))

        rank_lex = np.argsort(-lex)
        rank_emb = np.argsort(-cos)
        fused = np.zeros(len(self.chunks))
        for r, i in enumerate(rank_lex):
            fused[i] += 1.0 / (RRF_K + r + 1)
        for r, i in enumerate(rank_emb):
            fused[i] += 1.0 / (RRF_K + r + 1)

        order = np.argsort(-fused)[:k]
        out = []
        for i in order:
            c = self.chunks[i]
            out.append({**c, "lex": round(float(lex[i]), 3), "cos": round(float(cos[i]), 3),
                        "fused": round(float(fused[i]), 4)})
        return out

    def is_confident(self, hits):
        if not hits:
            return False
        top = hits[0]
        return top["cos"] >= COS_ACCEPT or top["lex"] >= LEX_ACCEPT
