"""Tests for ingest pipeline concurrency with claude -p subprocess."""

from __future__ import annotations

import asyncio
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from pydantic import ValidationError

from pith.config.models import IngestConfig
from pith.ingest import ingest_file
from pith.ingest.chunker import Chunk
from pith.parsers.base import ParsedDocument, Section


def _make_config(
    *,
    max_concurrency: int = 5,
    vault_path: Path | None = None,
) -> MagicMock:
    """Build a minimal mock PithConfig for ingest tests."""
    config = MagicMock()
    config.ingest.chunk_size_tokens = 2048
    config.ingest.overlap_tokens = 128
    config.ingest.max_concurrency = max_concurrency
    config.vault.schema_ = None
    config.vault.path = vault_path
    config.models.ingest = "claude-sonnet-4-6"
    return config


def _make_chunks(n: int) -> list[Chunk]:
    return [
        Chunk(index=i, text=f"chunk-{i}", token_estimate=10)
        for i in range(n)
    ]


def _make_doc(title: str = "test") -> ParsedDocument:
    return ParsedDocument(
        title=title,
        sections=[Section(heading="Intro", body="Hello world")],
    )


# ---------------------------------------------------------------------------
# Chunk ordering preserved
# ---------------------------------------------------------------------------


def test_chunk_ordering_preserved(tmp_path):
    """Sections must appear in original chunk order."""
    vault = tmp_path / "wiki"
    vault.mkdir()
    config = _make_config(vault_path=vault, max_concurrency=3)
    chunks = _make_chunks(3)

    async def mock_call(prompt, *, system=None, model="claude-sonnet-4-6"):
        idx = int(prompt.split("-")[-1])
        await asyncio.sleep(0.01 * (2 - idx))
        return f"section-{idx}"

    with (
        patch("pith.ingest.call_claude_async", side_effect=mock_call),
        patch("pith.ingest.parse", return_value=_make_doc()),
        patch("pith.ingest.chunk_document", return_value=chunks),
    ):
        result = asyncio.run(
            ingest_file(Path("test.txt"), config),
        )

    page_text = result.page_path.read_text(encoding="utf-8")
    idx_0 = page_text.index("section-0")
    idx_1 = page_text.index("section-1")
    idx_2 = page_text.index("section-2")
    assert idx_0 < idx_1 < idx_2


# ---------------------------------------------------------------------------
# Conflict counting
# ---------------------------------------------------------------------------


def test_conflict_counted_on_llm_error(tmp_path):
    """A chunk that raises LLMError counts as a conflict."""
    from pith.llm import LLMError

    vault = tmp_path / "wiki"
    vault.mkdir()
    config = _make_config(vault_path=vault, max_concurrency=5)
    chunks = _make_chunks(3)

    call_count = 0

    async def mock_call(prompt, *, system=None, model="claude-sonnet-4-6"):
        nonlocal call_count
        call_count += 1
        if call_count == 2:
            raise LLMError("test error")
        return "ok"

    with (
        patch("pith.ingest.call_claude_async", side_effect=mock_call),
        patch("pith.ingest.parse", return_value=_make_doc()),
        patch("pith.ingest.chunk_document", return_value=chunks),
    ):
        result = asyncio.run(
            ingest_file(Path("test.txt"), config),
        )

    assert result.conflicts == 1


# ---------------------------------------------------------------------------
# Config validation
# ---------------------------------------------------------------------------


def test_max_concurrency_config_valid():
    """max_concurrency=3 should be accepted."""
    cfg = IngestConfig(max_concurrency=3)
    assert cfg.max_concurrency == 3


def test_max_concurrency_config_invalid():
    """max_concurrency=0 should raise ValidationError."""
    with pytest.raises(ValidationError, match="at least 1"):
        IngestConfig(max_concurrency=0)
