"""
Resume Chunking Module
Splits resume text into 400–700 token chunks for better embedding accuracy.
"""
import re


def _approximate_token_count(text: str) -> int:
    """Rough token count (≈ words × 1.3 to account for sub-word tokenization)."""
    return int(len(text.split()) * 1.3)


def _split_into_sentences(text: str) -> list[str]:
    """Split text into sentences using a simple regex."""
    sentences = re.split(r"(?<=[.!?])\s+|\n{2,}", text)
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, min_tokens: int = 400, max_tokens: int = 700) -> list[str]:
    """Split resume text into semantically coherent chunks.

    Each chunk targets 400–700 tokens. Sentences are merged greedily; a new
    chunk starts when adding the next sentence would exceed max_tokens.

    If the entire resume is shorter than min_tokens, it is returned as a
    single chunk.

    Args:
        text: Full resume text.
        min_tokens: Minimum desired tokens per chunk.
        max_tokens: Maximum desired tokens per chunk.

    Returns:
        List of text chunks.
    """
    if not text.strip():
        return []

    # If entire text is short, return as-is
    if _approximate_token_count(text) <= max_tokens:
        return [text.strip()]

    sentences = _split_into_sentences(text)
    chunks: list[str] = []
    current_chunk: list[str] = []
    current_tokens = 0

    for sentence in sentences:
        sent_tokens = _approximate_token_count(sentence)

        # If a single sentence exceeds max_tokens, keep it as its own chunk
        if sent_tokens > max_tokens:
            if current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = []
                current_tokens = 0
            chunks.append(sentence)
            continue

        if current_tokens + sent_tokens > max_tokens:
            # Flush current chunk
            if current_chunk:
                chunks.append(" ".join(current_chunk))
            current_chunk = [sentence]
            current_tokens = sent_tokens
        else:
            current_chunk.append(sentence)
            current_tokens += sent_tokens

    # Flush remaining
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks
