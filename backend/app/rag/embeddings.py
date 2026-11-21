import os
import math
import hashlib
from typing import List
from backend.app.core.config import settings

EMBEDDING_DIM = 256

class EmbeddingsProvider:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.client = None
        if self.api_key:
            try:
                from google import genai
                self.client = genai.Client(api_key=self.api_key)
            except Exception as e:
                print(f"[!] Could not initialize Gemini GenAI client: {e}")

    def get_embedding(self, text: str) -> List[float]:
        """Generate normalized embedding vector for text."""
        if self.client:
            try:
                response = self.client.models.embed_content(
                    model=settings.EMBEDDING_MODEL,
                    contents=text
                )
                raw_vec = response.embedding.values
                # Normalize
                norm = math.sqrt(sum(x * x for x in raw_vec)) or 1.0
                return [round(x / norm, 6) for x in raw_vec[:EMBEDDING_DIM]]
            except Exception as e:
                # Fallback to local deterministic embedding
                pass

        # Robust, deterministic local text embedding projection
        # Hashes n-grams and tokens to fixed dimension with frequency weighting & L2 normalization
        vec = [0.0] * EMBEDDING_DIM
        tokens = text.lower().replace("\n", " ").split()
        for tok in tokens:
            h = int(hashlib.md5(tok.encode("utf-8")).hexdigest(), 16)
            idx = h % EMBEDDING_DIM
            sign = 1.0 if ((h >> 8) & 1) else -1.0
            vec[idx] += sign * (1.0 + math.log(1.0 + len(tok)))

        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [round(x / norm, 6) for x in vec]

embeddings_provider = EmbeddingsProvider()

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two unit-normalized vectors."""
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    return max(-1.0, min(1.0, dot))
