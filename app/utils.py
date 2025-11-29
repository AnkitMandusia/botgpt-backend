import re
import json
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from typing import List

def estimate_tokens(text: str) -> int:
    return len(text.split()) + len(text) // 4

def chunk_text(text: str, max_chunk_size: int = 500) -> List[str]:
    sentences = re.split(r'(?<=[.!?])\s+', text.strip())
    chunks = []
    current = ""
    for s in sentences:
        if len(current.encode()) + len(s.encode()) < max_chunk_size:
            current += " " + s if current else s
        else:
            if current:
                chunks.append(current.strip())
            current = s
    if current:
        chunks.append(current.strip())
    return chunks

def retrieve_relevant_chunks(query: str, chunks: List[str], top_k: int = 3) -> str:
    if not chunks:
        return ""
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        tfidf = vectorizer.fit_transform(chunks + [query])
        sims = cosine_similarity(tfidf[-1], tfidf[:-1]).flatten()
        top_idx = np.argsort(sims)[-top_k:][::-1]
        return "\n\n".join([chunks[i] for i in top_idx])
    except:
        return "\n\n".join(chunks[:top_k])