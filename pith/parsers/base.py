"""Base types for the parser pipeline.

Every parser returns a ``ParsedDocument`` — a format-agnostic
intermediate representation that the ingest layer consumes.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from pith.i18n import t


@dataclass(frozen=True)
class Section:
    """A titled section of a document."""

    heading: str
    body: str


@dataclass(frozen=True)
class Table:
    """A table extracted from a document."""

    headers: list[str]
    rows: list[list[str]]


@dataclass(frozen=True)
class ParsedDocument:
    """Format-agnostic intermediate document representation.

    Attributes:
        title:    Document title (filename stem when no title is found).
        sections: Ordered list of headed text sections.
        tables:   Tables found in the document.
        metadata: Provenance info — source path, format, page count, etc.
    """

    title: str
    sections: list[Section]
    tables: list[Table] = field(default_factory=list)
    metadata: dict[str, str] = field(default_factory=dict)


class ParseError(Exception):
    """Raised when a file cannot be parsed.

    Attributes:
        path:   The file that failed to parse.
        detail: Human-readable explanation of the failure.
    """

    def __init__(self, path: Path, detail: str) -> None:
        self.path = path
        self.detail = detail
        super().__init__(t("ingest.parse_failed", path=path, detail=detail))
