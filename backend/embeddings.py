import json
import os
import re

import numpy as np
import requests

OLLAMA_URL = "http://localhost:11434/api/embed"
MODEL = "nomic-embed-text"
BATCH_SIZE = 500

EMBED_CACHE = {
    "en": ("data/esco_embeddings.npy", "data/esco_index.json"),
    "fr": ("data/rome_embeddings.npy", "data/rome_index.json"),
}

DEFAULT_THRESHOLD = 0.80


def _ollama_embed_batch(texts):
    resp = requests.post(OLLAMA_URL, json={"model": MODEL, "input": texts}, timeout=120)
    resp.raise_for_status()
    return resp.json()["embeddings"]


def embed_texts(texts):
    all_vecs = []
    for i in range(0, len(texts), BATCH_SIZE):
        batch = texts[i:i + BATCH_SIZE]
        all_vecs.extend(_ollama_embed_batch(batch))
    return np.array(all_vecs, dtype=np.float32)


def build_cache(lang):
    cache_path, source_path = EMBED_CACHE[lang]
    with open(source_path, encoding="utf-8") as f:
        entries = json.load(f)
    # nomic-embed-text exige un préfixe d'instruction pour bien discriminer en recherche
    # (asymétrique : les documents indexés vs la requête n'utilisent pas le même préfixe).
    labels = ["search_document: " + e["label"] for e in entries]
    vecs = embed_texts(labels)
    np.save(cache_path, vecs)
    print(f"{len(entries)} embeddings ({lang}) écrits dans {cache_path}")
    return vecs, entries


_cache = {}


def _get_index(lang):
    if lang not in _cache:
        cache_path, source_path = EMBED_CACHE[lang]
        with open(source_path, encoding="utf-8") as f:
            entries = json.load(f)
        if os.path.exists(cache_path):
            vecs = np.load(cache_path)
        else:
            vecs, entries = build_cache(lang)
        _cache[lang] = (vecs, entries)
    return _cache[lang]


def _cosine_sim_matrix(query_vecs, matrix):
    q = query_vecs / np.linalg.norm(query_vecs, axis=1, keepdims=True)
    m = matrix / np.linalg.norm(matrix, axis=1, keepdims=True)
    return q @ m.T


def split_into_chunks(text):
    parts = re.split(r"[\n.;:!?,]+", text)
    return [p.strip() for p in parts if p and len(p.strip()) >= 3]


def semantic_matches(text, lang, threshold=DEFAULT_THRESHOLD, top_k=3):
    matrix, entries = _get_index(lang)
    chunks = split_into_chunks(text)
    if not chunks:
        return []
    query_vecs = embed_texts(["search_query: " + c for c in chunks])
    sims = _cosine_sim_matrix(query_vecs, matrix)

    seen = {}
    for i, chunk in enumerate(chunks):
        row = sims[i]
        top_idx = np.argsort(-row)[:top_k]
        for idx in top_idx:
            score = float(row[idx])
            if score < threshold:
                continue
            entry = entries[idx]
            key = (entry["label"], entry["type"], entry.get("code"))
            if key not in seen or seen[key]["score"] < score:
                seen[key] = {
                    "label": entry["label"],
                    "type": entry["type"],
                    "code": entry.get("code"),
                    "score": round(score, 3),
                    "source_chunk": chunk,
                }
    return sorted(seen.values(), key=lambda m: -m["score"])


if __name__ == "__main__":
    import sys
    lang = sys.argv[1] if len(sys.argv) > 1 else "fr"
    build_cache(lang)
