"""Parser dispatch — routes files to the correct format parser.

Usage:
    from pith.parsers import parse
    doc = parse(Path("report.pdf"))
"""

from __future__ import annotations

from pathlib import Path

from pith.i18n import t
from pith.parsers.base import ParsedDocument, ParseError, Section, Table

_DISPATCH: dict[str, str] = {
    ".pdf": "pdf",
    ".docx": "docx",
    ".txt": "text",
    ".md": "text",
    ".xlsx": "xlsx",
    ".csv": "csv",
    ".pptx": "pptx",
}


def parse(path: Path) -> ParsedDocument:
    """Parse a file into a ``ParsedDocument``, dispatching by suffix.

    Args:
        path: Path to the source file.

    Returns:
        A ``ParsedDocument`` with the extracted content.

    Raises:
        ParseError: If the format is unsupported or parsing fails.
    """
    if not path.exists():
        raise ParseError(path, t("parser.file_not_found", path=path))

    suffix = path.suffix.lower()
    parser_key = _DISPATCH.get(suffix)

    if parser_key is None:
        raise ParseError(path, t("ingest.unsupported_format", suffix=suffix))

    if parser_key == "pdf":
        from pith.parsers.pdf import parse_pdf
        return parse_pdf(path)
    elif parser_key == "docx":
        from pith.parsers.docx import parse_docx
        return parse_docx(path)
    elif parser_key == "xlsx":
        from pith.parsers.xlsx import parse_xlsx
        return parse_xlsx(path)
    elif parser_key == "csv":
        from pith.parsers.csv import parse_csv
        return parse_csv(path)
    elif parser_key == "pptx":
        from pith.parsers.pptx import parse_pptx
        return parse_pptx(path)
    else:
        from pith.parsers.text import parse_text
        return parse_text(path)


__all__ = [
    "ParsedDocument",
    "ParseError",
    "Section",
    "Table",
    "parse",
]
