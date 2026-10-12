"""Four retrieval methods over one set of chunks: bm25, dense, hybrid, rerank."""
import os, re, unicodedata
import numpy as np
from rank_bm25 import BM25Okapi


def tok(text):
    text = unicodedata.normalize("NFKD", text.lower())
    text = "".join(c for c in text if not unicodedata.combining(c))
    return re.findall(r"\w+", text)


def load_or_embed(model, chunks, path, batch_size=64):
    if os.path.exists(path):
        return np.load(path)
    emb = model.encode(["passage: " + c["text"] for c in chunks], batch_size=batch_size,
                       normalize_embeddings=True, show_progress_bar=True)
    np.save(path, emb)
    return emb


class Retriever:
    def __init__(self, chunks, embedder, embeddings, reranker=None):
        self.chunks = chunks
        self.bm25 = BM25Okapi([tok(c["text"]) for c in chunks])
        self.embedder, self.emb, self.reranker = embedder, embeddings, reranker

    def bm25_search(self, q, k):
        return list(np.argsort(-self.bm25.get_scores(tok(q)))[:k])

    def dense_search(self, q, k):
        v = self.embedder.encode("query: " + q, normalize_embeddings=True)
        return list(np.argsort(-(self.emb @ v))[:k])

    def hybrid_search(self, q, k, pool=50, rrf_k=60):
        score = {}
        for ranked in (self.bm25_search(q, pool), self.dense_search(q, pool)):
            for rank, i in enumerate(ranked):
                score[i] = score.get(i, 0) + 1 / (rrf_k + rank + 1)
        return sorted(score, key=score.get, reverse=True)[:k]

    def rerank_search(self, q, k, pool=30):
        cand = self.hybrid_search(q, pool)
        scores = self.reranker.predict([(q, self.chunks[i]["text"]) for i in cand])
        return [cand[j] for j in np.argsort(-scores)][:k]

    def search(self, method, q, k=10):
        return getattr(self, f"{method}_search")(q, k)


METHODS = ["bm25", "dense", "hybrid", "rerank"]
