"""Query pipeline — send questions to the local Ollama model with wiki context."""

from __future__ import annotations

import re
from pathlib import Path

import httpx

from pith.config.models import PithConfig
from pith.i18n import t
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


async def query_wiki(query: str, config: PithConfig) -> str:
    """Send *query* to Ollama with wiki pages as context.

    Args:
        query:  The user's natural-language question.
        config: Validated PITH configuration.

    Returns:
        The model's response text.

    Raises:
        QueryError: If Ollama is unreachable or returns a non-2xx status.
    """
    vault_path = config.vault.path
    if vault_path is None:
        raise QueryError(t("query.no_pages", path="(not configured)"))

    pages = _read_wiki_pages(vault_path)
    if not pages:
        raise QueryError(t("query.no_pages", path=str(vault_path)))

    context = _build_context(pages)
    system_message = t("query.system_prompt", context=context)

    base_url = config.providers.ollama.base_url.rstrip("/")
    url = f"{base_url}/api/chat"
    payload = {
        "model": config.models.query.model,
        "messages": [
            {"role": "system", "content": system_message},
            {"role": "user", "content": query},
        ],
        "stream": False,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url, json=payload, timeout=120.0)
        except httpx.ConnectError as exc:
            raise QueryError(
                t("query.ollama_unreachable", url=url, detail=str(exc)),
            ) from exc

        if response.status_code != 200:
            raise QueryError(
                t(
                    "query.ollama_error",
                    status=response.status_code,
                    detail=response.text,
                ),
            )

    data = response.json()
    answer: str = data["message"]["content"]
    info(answer)
    return answer
