"""Retrieval layer: chunk the solved book, index it two ways, and search with hybrid fusion.

Pipeline
  1. Chunk     one chunk per question part (question text + part prompt + final answer).
               Long solutions are not embedded; their steps are returned with the chunk.
  2. Embed     BAAI/bge-small-en-v1.5 from Hugging Face (local, ~130 MB, CPU is fine).
  3. Lexical   TF-IDF over normalized math text (catches exact symbols like "sqrt", "10^-4"). Plain Python, so the
               serverless deployment needs no numpy or scikit-learn; it scores the same as sklearn's TfidfVectorizer.
  4. Fuse      Reciprocal Rank Fusion of the embedding and lexical rankings.
  5. Decide    a match is accepted only if its best cosine similarity or its lexical score
               clears a threshold. Otherwise the caller falls back to live solving, with the
               nearest book chunks passed in as worked examples.
"""
import hashlib
import json
import math
import os
import pathlib
import re
from collections import Counter

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
    question = item["question"]
    # For a multi-part question use only the stem ("Represent the following numbers on the number line:") plus
    # this part's own prompt. Repeating every part in every chunk would dilute the match for one part.
    stem = re.split(r"\s*\(i\)\s", question, maxsplit=1)[0] if len(item["parts"]) > 1 else question
    for p in item["parts"]:
        text = " ".join(filter(None, [stem, p.get("prompt", ""), p.get("label", ""), p.get("answer", "")]))
        yield {**base, "part": p.get("label", ""), "text": text, "question": question}


def load_chunks():
    chunks = []
    for path in sorted(BOOK.glob("unit*.json")):
        unit = json.loads(path.read_text(encoding="utf-8"))
        for it in unit["items"]:
            it["unit"] = unit["unit"]
            it["unit_title"] = unit["title"]
            chunks.extend(chunk_item(it))
    return chunks


_WORD = re.compile(r"(?u)\b\w+\b")


def _word_terms(doc):
    """Unigrams and bigrams of the words, as sklearn makes them with ngram_range=(1, 2) and word-boundary tokens."""
    toks = _WORD.findall(doc.lower())
    return toks + [a + " " + b for a, b in zip(toks, toks[1:])]


def _char_terms(doc):
    """Character 2-4-grams inside word boundaries, as TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 4))."""
    out = []
    for w in re.sub(r"\s\s+", " ", doc.lower()).split():
        w = " " + w + " "
        for n in (2, 3, 4):
            offset = 0
            out.append(w[offset:offset + n])
            while offset + n < len(w):
                offset += 1
                out.append(w[offset:offset + n])
            if offset == 0:        # a word shorter than n counts once
                break
    return out


class _Tfidf:
    """TF-IDF with smoothed idf and l2 norm, the TfidfVectorizer defaults. Vectors are {term: weight} dicts."""

    def __init__(self, terms_fn, docs):
        self.terms_fn = terms_fn
        counts = [Counter(terms_fn(d)) for d in docs]
        df = Counter(t for c in counts for t in c)
        n = len(docs)
        self.idf = {t: math.log((1 + n) / (1 + d)) + 1 for t, d in df.items()}
        self.docs = [self._weigh(c) for c in counts]

    def _weigh(self, counts):
        v = {t: c * self.idf[t] for t, c in counts.items() if t in self.idf}     # terms unseen in the corpus are dropped
        norm = math.sqrt(sum(x * x for x in v.values()))
        return {t: x / norm for t, x in v.items()} if norm else {}

    def scores(self, query):
        q = self._weigh(Counter(self.terms_fn(query)))
        return [sum(w * d.get(t, 0.0) for t, w in q.items()) for d in self.docs]


def _ranks(scores):
    """Indices from best to worst; ties keep the book's order."""
    return sorted(range(len(scores)), key=lambda i: (-scores[i], i))


class Index:
    def __init__(self, chunks, use_embeddings=True):
        self.chunks = chunks or []
        docs = [normalize(c["text"]) for c in self.chunks] or ["empty"]
        self.tfidf_word = _Tfidf(_word_terms, docs)
        self.tfidf_char = _Tfidf(_char_terms, docs)
        self.model = None
        self.E = None
        if use_embeddings and self.chunks:
            self._load_embeddings(docs)

    # ---- embeddings (Hugging Face model, cached to disk; needs numpy and sentence-transformers) ----
    def _load_embeddings(self, docs):
        import numpy as np
        from sentence_transformers import SentenceTransformer
        self.model = SentenceTransformer(EMB_MODEL)
        # cache key = model + chunk text, so switching models or editing an item never reuses stale vectors
        ids = [hashlib.md5((EMB_MODEL + "|" + c["id"] + "|" + c["part"] + "|" + d).encode("utf-8")).hexdigest()
               for c, d in zip(self.chunks, docs)]
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
        lex = [0.5 * a + 0.5 * b for a, b in zip(self.tfidf_word.scores(qn), self.tfidf_char.scores(qn))]
        qe = self._embed_query(query)
        cos = [float(x) for x in self.E @ qe] if qe is not None else [0.0] * len(self.chunks)

        fused = [0.0] * len(self.chunks)
        for r, i in enumerate(_ranks(lex)):
            fused[i] += 1.0 / (RRF_K + r + 1)
        if qe is not None:   # without an embedding model the dense ranking would be pure noise, so leave it out
            for r, i in enumerate(_ranks(cos)):
                fused[i] += 1.0 / (RRF_K + r + 1)

        out = []
        for i in _ranks(fused)[:k]:
            c = self.chunks[i]
            out.append({**c, "lex": round(lex[i], 3), "cos": round(cos[i], 3), "fused": round(fused[i], 4)})
        return out

    def is_confident(self, hits):
        if not hits:
            return False
        top = hits[0]
        return top["cos"] >= COS_ACCEPT or top["lex"] >= LEX_ACCEPT
