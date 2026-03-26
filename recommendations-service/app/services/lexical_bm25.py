import functools
import hashlib
import math
import re
from collections import Counter

import snowballstemmer

LEXICAL_DIM = 2**20
BM25_K1 = 1.2
BM25_B = 0.75


@functools.lru_cache(maxsize=1)
def get_stemmer():
    return snowballstemmer.stemmer("russian")


def tokenize(text: str) -> list[str]:
    """Токены: буквы и цифры, нижний регистр"""
    if not text or not text.strip():
        return []
    lower = text.lower().strip()
    tokens = re.findall(r"[^\W_]+", lower)
    return [t for t in tokens if t]


def stem_tokens(tokens: list[str]) -> list[str]:
    """Стемминг для русского"""
    stemmer = get_stemmer()
    return [stemmer.stemWord(t) for t in tokens]


def tokenize_and_stem(text: str) -> list[str]:
    """Токенизация + стемминг"""
    return stem_tokens(tokenize(text))


def term_id(term: str) -> int:
    """Детерминированный id термина (одинаковый в любом процессе/контейнере)"""
    h = hashlib.sha256(term.encode("utf-8")).digest()
    idx = int.from_bytes(h[:4], "big") % LEXICAL_DIM
    return idx


def compute_corpus_bm25_stats(
    docs_tokenized: list[list[str]],
) -> tuple[dict[str, float], float, int]:
    """IDF и avgdl по корпусу (список документов = список списков стеммов)"""
    N = len(docs_tokenized)
    if N == 0:
        return {}, 0.0, 0
    doc_freq = Counter()
    total_len = 0
    for tokens in docs_tokenized:
        total_len += len(tokens)
        for t in set(tokens):
            doc_freq[t] += 1
    avgdl = total_len / N
    idf_map: dict[str, float] = {}
    for term, df in doc_freq.items():
        idf_map[term] = math.log((N - df + 0.5) / (df + 0.5) + 1.0)
    return idf_map, avgdl, N


def build_bm25_doc_vector(
    tokens: list[str],
    idf_map: dict[str, float],
    avgdl: float,
    k1: float = BM25_K1,
    b: float = BM25_B,
) -> tuple[list[int], list[float]]:
    """Sparse-вектор документа для BM25 (indices, values)."""
    if not tokens or avgdl <= 0:
        return [], []
    doc_len = len(tokens)
    tf = Counter(tokens)
    norm = 1.0 - b + b * (doc_len / avgdl)
    seen: set[int] = set()
    indices: list[int] = []
    values: list[float] = []
    for term, cnt in tf.items():
        idx = term_id(term)
        if idx in seen:
            continue
        seen.add(idx)
        idf = idf_map.get(term, 0.0)
        val = (cnt * (k1 + 1)) / (cnt + k1 * norm)
        indices.append(idx)
        values.append(idf * val)
    paired = sorted(zip(indices, values))
    return [p[0] for p in paired], [p[1] for p in paired]


def build_bm25_query_vector(
    tokens: list[str],
    idf_map: dict[str, float],
) -> tuple[list[int], list[float]]:
    """Sparse-вектор запроса для BM25 (indices, values)"""
    if not tokens:
        return [], []
    seen: set[int] = set()
    indices: list[int] = []
    values: list[float] = []
    for t in tokens:
        idx = term_id(t)
        if idx in seen:
            continue
        idf = idf_map.get(t, 0.0)
        if idf <= 0.0:
            continue
        seen.add(idx)
        indices.append(idx)
        values.append(idf)
    paired = sorted(zip(indices, values))
    return [p[0] for p in paired], [p[1] for p in paired]
