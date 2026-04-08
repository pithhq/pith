"""Plain text and Markdown parser.

Handles ``.txt`` and ``.md`` files. Markdown files are split on
``#``-style headings; plain text is returned as a single section.
"""

from __future__ import annotations

import re
from pathlib import Path

from pith.i18n import t
from pith.parsers.base import ParsedDocument, ParseError, Section

_MD_HEADING_RE = re.compile(r"^(#{1,6})\s+(.+)$", re.MULTILINE)


def _parse_markdown(text: str, path: Path) -> ParsedDocument:
    """Split Markdown text on headings into sections."""
    sections: list[Section] = []
    current_heading = ""
    body_parts: list[str] = []

    for line in text.splitlines():
        match = _MD_HEADING_RE.match(line)
        if match:
            if body_parts:
                sections.append(
                    Section(heading=current_heading, body="\n".join(body_parts))
                    )
                body_parts = []
            current_heading = match.group(2).strip()
        else:
            stripped = line.strip()
            if stripped:
                body_parts.append(stripped)

    if body_parts:
        sections.append(Section(heading=current_heading, body="\n".join(body_parts)))

    return ParsedDocument(
        title=path.stem,
        sections=sections,
        tables=[],
        metadata={
            "source": str(path),
            "format": path.suffix.lstrip("."),
        },
    )


def _parse_plain(text: str, path: Path) -> ParsedDocument:
    """Wrap plain text as a single section."""
    return ParsedDocument(
        title=path.stem,
        sections=[Section(heading="", body=text.strip())] if text.strip() else [],
        tables=[],
        metadata={
            "source": str(path),
            "format": "txt",
        },
    )


def parse_text(path: Path) -> ParsedDocument:
    """Parse a ``.txt`` or ``.md`` file into a ``ParsedDocument``.

    Args:
        path: Path to the text file.

    Returns:
        A ``ParsedDocument``. Markdown files are split on headings;
        plain text files are returned as a single section.

    Raises:
        ParseError: If the file cannot be read.
    """
    try:
        text = path.read_text(encoding="utf-8")
    except Exception as exc:
        raise ParseError(path, t("parser.text_read_error", detail=str(exc))) from exc

    if path.suffix.lower() == ".md":
        return _parse_markdown(text, path)
    return _parse_plain(text, path)
