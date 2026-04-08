"""Lint pass — wiki health checks (orphans, contradictions, stale refs).

Public interface:
    result = await run_lint(config)
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import httpx
import yaml

from pith.config.models import PithConfig
from pith.i18n import t
from pith.output import info, success, warning

_FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

# Patterns for wiki-style links: [[PageName]] or [text](PageName.md)
_WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")
_MDLINK_RE = re.compile(r"\[[^\]]*\]\(([^)]+\.md)\)")

_CONTRADICTION_PROMPT = (
    "You are a fact-checking assistant. Given two wiki page excerpts, "
    "identify any factual contradictions between them. If there are none, "
    "respond with exactly: NONE\n\n"
    "Page A:\n{page_a}\n\n"
    "Page B:\n{page_b}"
)


@dataclass
class LintResult:
    """Aggregated results from all lint checks."""

    orphans: list[Path] = field(default_factory=list)
    contradictions: list[tuple[Path, Path, str]] = field(default_factory=list)
    stale: list[Path] = field(default_factory=list)


def _parse_frontmatter(text: str) -> dict[str, object]:
    """Extract YAML frontmatter from a markdown file."""
    match = _FRONTMATTER_RE.match(text)
    if not match:
        return {}
    try:
        data = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return {}
    return data if isinstance(data, dict) else {}


def _strip_frontmatter(text: str) -> str:
    """Return the body of a markdown file without frontmatter."""
    return _FRONTMATTER_RE.sub("", text).strip()


def _collect_pages(vault_path: Path) -> dict[Path, str]:
    """Read all .md files from the vault, return {path: raw_content}."""
    pages: dict[Path, str] = {}
    for md_file in sorted(vault_path.rglob("*.md")):
        raw = md_file.read_text(encoding="utf-8")
        pages[md_file] = raw
    return pages


# -- Orphan check ----------------------------------------------------------


def _check_orphans(pages: dict[Path, str]) -> list[Path]:
    """Find pages not referenced by any other page."""
    # Collect all referenced names from all pages
    referenced: set[str] = set()
    for raw in pages.values():
        body = _strip_frontmatter(raw)
        for match in _WIKILINK_RE.finditer(body):
            referenced.add(match.group(1))
        for match in _MDLINK_RE.finditer(body):
            # Strip .md suffix to get the stem
            referenced.add(Path(match.group(1)).stem)

    orphans: list[Path] = []
    for page_path in sorted(pages):
        if page_path.stem not in referenced:
            orphans.append(page_path)
    return orphans


# -- Contradictions check ---------------------------------------------------


def _pages_by_tags(
    pages: dict[Path, str],
) -> dict[str, list[Path]]:
    """Group pages by their frontmatter tags."""
    tag_map: dict[str, list[Path]] = {}
    for page_path, raw in pages.items():
        fm = _parse_frontmatter(raw)
        tags = fm.get("tags", [])
        if isinstance(tags, list):
            for tag in tags:
                tag_str = str(tag)
                tag_map.setdefault(tag_str, []).append(page_path)
    return tag_map


def _candidate_pairs(
    pages: dict[Path, str],
) -> list[tuple[Path, Path]]:
    """Return unique page pairs that share at least one entity tag."""
    tag_map = _pages_by_tags(pages)
    seen: set[tuple[Path, Path]] = set()
    pairs: list[tuple[Path, Path]] = []
    for paths in tag_map.values():
        for i, a in enumerate(paths):
            for b in paths[i + 1 :]:
                key = (min(a, b), max(a, b))
                if key not in seen:
                    seen.add(key)
                    pairs.append(key)
    return pairs


async def _check_contradictions(
    pages: dict[Path, str],
    config: PithConfig,
) -> list[tuple[Path, Path, str]]:
    """Send page pairs sharing tags to Ollama for contradiction detection."""
    pairs = _candidate_pairs(pages)
    if not pairs:
        return []

    base_url = config.providers.ollama.base_url.rstrip("/")
    url = f"{base_url}/api/chat"
    model = config.models.lint.model
    results: list[tuple[Path, Path, str]] = []

    async with httpx.AsyncClient(timeout=120.0) as client:
        for page_a, page_b in pairs:
            body_a = _strip_frontmatter(pages[page_a])
            body_b = _strip_frontmatter(pages[page_b])
            prompt = _CONTRADICTION_PROMPT.format(page_a=body_a, page_b=body_b)

            try:
                response = await client.post(
                    url,
                    json={
                        "model": model,
                        "messages": [{"role": "user", "content": prompt}],
                        "stream": False,
                    },
                )
            except httpx.ConnectError:
                warning(t("lint.skip_contradictions"))
                return results

            if response.status_code != 200:
                warning(t("lint.skip_contradictions"))
                return results

            data = response.json()
            answer: str = data["message"]["content"].strip()
            if answer.upper() != "NONE":
                results.append((page_a, page_b, answer))

    return results


# -- Stale references check -------------------------------------------------


def _check_stale_references(
    pages: dict[Path, str],
    vault_path: Path,
) -> list[Path]:
    """Find pages whose references_legislation includes an updated statute."""
    statutes_file = vault_path / "updated_statutes.txt"
    if not statutes_file.exists():
        return []

    updated: set[str] = set()
    for line in statutes_file.read_text(encoding="utf-8").splitlines():
        slug = line.strip()
        if slug:
            updated.add(slug)

    if not updated:
        return []

    stale: list[Path] = []
    for page_path, raw in sorted(pages.items()):
        fm = _parse_frontmatter(raw)
        refs = fm.get("references_legislation", [])
        if isinstance(refs, list):
            for ref in refs:
                if str(ref) in updated:
                    stale.append(page_path)
                    break
    return stale


# -- Main entry point -------------------------------------------------------


async def run_lint(config: PithConfig) -> LintResult:
    """Run enabled lint checks on the wiki vault.

    Args:
        config: Validated PITH configuration.

    Returns:
        LintResult with findings from all enabled checks.

    Raises:
        ValueError: If no vault path is configured.
    """
    vault_path = config.vault.path
    if vault_path is None:
        raise ValueError(t("lint.no_vault"))

    info(t("lint.running"))
    pages = _collect_pages(vault_path)
    checks = config.lint.checks
    result = LintResult()

    if checks.orphans:
        result.orphans = _check_orphans(pages)

    if checks.contradictions:
        result.contradictions = await _check_contradictions(pages, config)

    if checks.stale_references:
        result.stale = _check_stale_references(pages, vault_path)

    # Print results
    has_findings = result.orphans or result.contradictions or result.stale

    if result.orphans:
        warning(t("lint.orphans", n=len(result.orphans)))
        for orphan in result.orphans:
            warning(t("lint.orphan_detail", path=orphan))

    if result.contradictions:
        warning(t("lint.contradictions", n=len(result.contradictions)))
        for page_a, page_b, detail in result.contradictions:
            warning(t("lint.contradiction_detail", a=page_a, b=page_b, detail=detail))

    if result.stale:
        warning(t("lint.stale_references", n=len(result.stale)))
        for stale_page in result.stale:
            warning(t("lint.stale_detail", path=stale_page))

    if not has_findings:
        success(t("lint.clean"))

    return result


__all__ = [
    "LintResult",
    "run_lint",
]
