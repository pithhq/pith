"""Chunk a ParsedDocument into token-bounded pieces for API calls."""

from __future__ import annotations

from dataclasses import dataclass

from pith.parsers.base import ParsedDocument


@dataclass(frozen=True)
class Chunk:
    """A token-bounded slice of document text.

    Attributes:
        index:          Zero-based position in the chunk sequence.
        text:           The plain text content of this chunk.
        token_estimate: Approximate token count (word count * 1.3).
    """

    index: int
    text: str
    token_estimate: int


def _estimate_tokens(text: str) -> int:
    """Approximate token count without a tokenizer dependency."""
    return int(len(text.split()) * 1.3)


def _flatten_document(doc: ParsedDocument) -> str:
    """Flatten all sections of a ParsedDocument into a single string."""
    parts: list[str] = []
    for section in doc.sections:
        if section.heading:
            parts.append(f"## {section.heading}")
        parts.append(section.body)
    for table in doc.tables:
        header_row = " | ".join(table.headers)
        separator = " | ".join("---" for _ in table.headers)
        rows = "\n".join(" | ".join(row) for row in table.rows)
        parts.append(f"{header_row}\n{separator}\n{rows}")
    return "\n\n".join(parts)


def chunk_document(
    doc: ParsedDocument,
    chunk_size_tokens: int,
    overlap_tokens: int,
) -> list[Chunk]:
    """Split a parsed document into overlapping, token-bounded chunks.

    Args:
        doc:               The parsed document to chunk.
        chunk_size_tokens: Target token count per chunk.
        overlap_tokens:    Number of tokens to overlap between chunks.

    Returns:
        Ordered list of Chunk objects covering the full document.
    """
    full_text = _flatten_document(doc)
    words = full_text.split()

    if not words:
        return []

    chunk_words = max(1, int(chunk_size_tokens / 1.3))
    overlap_words = int(overlap_tokens / 1.3)
    step = max(1, chunk_words - overlap_words)

    chunks: list[Chunk] = []
    idx = 0
    pos = 0
    while pos < len(words):
        end = min(pos + chunk_words, len(words))
        text = " ".join(words[pos:end])
        chunks.append(Chunk(
            index=idx,
            text=text,
            token_estimate=_estimate_tokens(text),
        ))
        idx += 1
        pos += step
        if end == len(words):
            break

    return chunks
