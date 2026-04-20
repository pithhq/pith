"""Query pipeline — send questions to Claude Code CLI with wiki context."""

from __future__ import annotations

import re
from pathlib import Path

from pith.config.models import PithConfig
from pith.i18n import t
from pith.llm import LLMError, call_claude
from pith.output import info


class QueryError(Exception):
    """Raised when the query pipeline cannot complete."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


_MAX_CONTEXT_WORDS = 8000
_FRONTMATTER_RE = re.compile(r"\A---\s*\n.*?\n---\s*\n", re.DOTALL)


def _read_wiki_pages(vault_path: Path) -> list[str]:
    """Read all .md files from the vault directory, return their bodies.

    Frontmatter (YAML between ``---`` fences) is stripped.
    """
    pages: list[str] = []
    for md_file in sorted(vault_path.rglob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        body = _FRONTMATTER_RE.sub("", raw).strip()
        if body:
            pages.append(body)
    return pages


def _build_context(pages: list[str]) -> str:
    """Concatenate page bodies, trimmed to the word budget."""
    combined: list[str] = []
    word_count = 0
    for page in pages:
        words = page.split()
        if word_count + len(words) > _MAX_CONTEXT_WORDS:
            remaining = _MAX_CONTEXT_WORDS - word_count
            if remaining > 0:
                combined.append(" ".join(words[:remaining]))
            break
        combined.append(page)
        word_count += len(words)
    return "\n\n".join(combined)


def query_wiki(query: str, config: PithConfig) -> str:
    """Send *query* to Claude Code CLI with wiki pages as context.

    Args:
        query:  The user's natural-language question.
        config: Validated PITH configuration.

    Returns:
        The model's response text.

    Raises:
        QueryError: If the CLI call fails.
    """
    vault_path = config.vault.path
    if vault_path is None:
        raise QueryError(t("query.no_pages", path="(not configured)"))

    pages = _read_wiki_pages(vault_path)
    if not pages:
        raise QueryError(t("query.no_pages", path=str(vault_path)))

    context = _build_context(pages)
    system_message = t("query.system_prompt", context=context)

    try:
        answer = call_claude(
            query,
            system=system_message,
            model=config.models.query,
        )
    except LLMError as exc:
        raise QueryError(exc.detail) from exc

    info(answer)
    return answer
