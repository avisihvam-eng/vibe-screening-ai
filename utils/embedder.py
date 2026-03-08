"""
Embedding Module
Loads the all-MiniLM-L6-v2 model and computes embeddings + cosine similarity.
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# ── Global model cache ──────────────────────────────────────────────────────────
_model: SentenceTransformer | None = None


def load_model() -> SentenceTransformer:
    """Load and cache the embedding model."""
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model


def get_embeddings(texts: list[str]) -> np.ndarray:
    """Compute embeddings for a list of texts.

    Args:
        texts: List of text strings.

    Returns:
        numpy array of shape (len(texts), embedding_dim).
    """
    model = load_model()
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)


def cosine_similarity(a: np.ndarray, b: np.ndarray) -> np.ndarray:
    """Compute cosine similarity between two sets of vectors.

    Args:
        a: shape (m, d)
        b: shape (n, d)

    Returns:
        Similarity matrix of shape (m, n).
    """
    a_norm = a / (np.linalg.norm(a, axis=1, keepdims=True) + 1e-10)
    b_norm = b / (np.linalg.norm(b, axis=1, keepdims=True) + 1e-10)
    return a_norm @ b_norm.T
