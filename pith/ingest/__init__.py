"""Ingest pipeline — parse, chunk, compile, and write wiki pages.

Public interface:
    SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".xlsx", ".csv", ".pptx", ".txt", ".md"}

    if path.suffix.lower() not in SUPPORTED_EXTENSIONS:
        error(t("ingest.unsupported_format", suffix=path.suffix))
        raise typer.Exit(code=1)
    result = await ingest_file(path, config)
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

from pith.config.models import PithConfig
from pith.i18n import t
from pith.ingest.chunker import Chunk, chunk_document
from pith.llm import LLMError, call_claude_async
from pith.output import error, info, summary
from pith.parsers import parse
from pith.schema import SchemaPack, load_schema

_SYSTEM_PROMPT = (
    "You are a knowledge compiler. Convert the following document chunk "
    "into a structured wiki page section in markdown."
)


@dataclass(frozen=True)
class IngestResult:
    """Outcome of ingesting a single file.

    Attributes:
        page_path: Path where the wiki page was written.
        created:   True if the page is new.
        updated:   True if an existing page was overwritten.
        conflicts: Number of chunks that failed compilation.
    """

    page_path: Path
    created: bool
    updated: bool
    conflicts: int


def _build_system_prompt(schema: SchemaPack | None) -> str:
    """Build the full system prompt, appending schema instructions if present."""
    if schema and schema.agent_instructions:
        return _SYSTEM_PROMPT + "\n\n" + schema.agent_instructions
    return _SYSTEM_PROMPT


def _infer_entity_type(
    schema: SchemaPack | None,
) -> str | None:
    """Return a single entity type if the schema defines exactly one."""
    if schema and len(schema.entities) == 1:
        return next(iter(schema.entities))
    return None


def _build_frontmatter(
    title: str,
    source: Path,
    schema: str | None,
    entity_type: str | None = None,
) -> str:
    """Render YAML frontmatter for a wiki page."""
    now = datetime.now(timezone.utc).isoformat()
    schema_value = schema if schema else "null"
    lines = [
        "---",
        f"title: {title}",
        f"source: {source}",
        f"ingested_at: {now}",
        f"schema: {schema_value}",
    ]
    if entity_type:
        lines.append(f"entity_type: {entity_type}")
    lines.append("---")
    return "\n".join(lines) + "\n"


def _page_path_for(source: Path, vault_path: Path) -> Path:
    """Derive the wiki page path from the source file name.

    Raises:
        ValueError: If the resolved path escapes the vault directory.
    """
    page_path = (vault_path / f"{source.stem}.md").resolve()
    if not page_path.is_relative_to(vault_path.resolve()):
        raise ValueError(
            t("ingest.path_escape", path=page_path, vault=vault_path),
        )
    return page_path


async def ingest_file(path: Path, config: PithConfig) -> IngestResult:
    """Ingest a single file into the wiki vault.

    Steps:
        1. Parse the file into a ParsedDocument.
        2. Chunk the document by token count with overlap.
        3. Send each chunk to Claude Code CLI for compilation.
        4. Assemble responses into a wiki page with YAML frontmatter.
        5. Write the page to the vault directory.

    Args:
        path:   Path to the source file.
        config: Validated PITH configuration.

    Returns:
        IngestResult with page path, created/updated flags, and conflict count.
    """

    doc = parse(path)

    chunks = chunk_document(
        doc,
        chunk_size_tokens=config.ingest.chunk_size_tokens,
        overlap_tokens=config.ingest.overlap_tokens,
    )

    # Load schema pack if configured.
    schema_pack: SchemaPack | None = None
    if config.vault.schema_:
        schema_pack = load_schema(config.vault.schema_)

    system_prompt = _build_system_prompt(schema_pack)
    entity_type = _infer_entity_type(schema_pack)
    model = config.models.ingest

    total = len(chunks)
    sem = asyncio.Semaphore(config.ingest.max_concurrency)
    completed = 0

    async def _process_chunk(chunk: Chunk) -> str | None:
        nonlocal completed
        async with sem:
            try:
                result = await call_claude_async(
                    chunk.text,
                    system=system_prompt,
                    model=model,
                )
                completed += 1
                info(t(
                    "ingest.chunk_progress",
                    current=completed, total=total,
                ))
                return result
            except LLMError as exc:
                error(t(
                    "ingest.api_error",
                    index=chunk.index, detail=str(exc),
                ))
                completed += 1
                return None

    tasks = [_process_chunk(c) for c in chunks]
    results = await asyncio.gather(*tasks)

    sections = [r for r in results if r is not None]
    conflicts = sum(1 for r in results if r is None)
    if not config.vault.path:
        raise ValueError(t("error.vault_path_not_configured"))
    vault_path = config.vault.path
    page_path = _page_path_for(path, vault_path)
    existed = page_path.exists()

    schema_name = config.vault.schema_
    frontmatter = _build_frontmatter(
        doc.title, path, schema_name, entity_type,
    )
    body = "\n\n".join(sections)
    page_content = f"{frontmatter}\n{body}\n"

    info(t("ingest.writing_page", path=page_path))
    page_path.parent.mkdir(parents=True, exist_ok=True)
    page_path.write_text(page_content, encoding="utf-8")

    created = not existed
    updated = existed

    summary(updated=int(updated), created=int(created), conflicts=conflicts)

    return IngestResult(
        page_path=page_path,
        created=created,
        updated=updated,
        conflicts=conflicts,
    )


__all__ = [
    "IngestResult",
    "ingest_file",
]
