"""PDF parser — text-layer extraction via pdfplumber.

Handles text-based PDFs only. Scanned-image PDFs (OCR) are Phase 3.
"""

from __future__ import annotations

from pathlib import Path

import pdfplumber

from pith.i18n import t
from pith.parsers.base import ParseError, ParsedDocument, Section, Table


def parse_pdf(path: Path) -> ParsedDocument:
    """Parse a text-based PDF into a ``ParsedDocument``.

    Args:
        path: Path to the PDF file.

    Returns:
        A ``ParsedDocument`` with one section per page and any
        tables found across all pages.

    Raises:
        ParseError: If the file cannot be opened or contains no
            extractable text.
    """
    try:
        pdf = pdfplumber.open(path)
    except Exception as exc:
        raise ParseError(path, t("parser.pdf_read_error", detail=str(exc))) from exc

    sections: list[Section] = []
    tables: list[Table] = []
    page_count = len(pdf.pages)

    try:
        for page in pdf.pages:
            text = page.extract_text() or ""
            if text.strip():
                sections.append(
                    Section(
                        heading=str(page.page_number),
                        body=text.strip(),
                    )
                )

            for raw_table in page.extract_tables() or []:
                if not raw_table:
                    continue
                header_row = raw_table[0]
                headers = [cell or "" for cell in header_row]
                rows = [
                    [cell or "" for cell in row]
                    for row in raw_table[1:]
                ]
                tables.append(Table(headers=headers, rows=rows))
    finally:
        pdf.close()

    if not sections:
        raise ParseError(path, t("parser.pdf_no_text", path=path))

    return ParsedDocument(
        title=path.stem,
        sections=sections,
        tables=tables,
        metadata={
            "source": str(path),
            "format": "pdf",
            "pages": str(page_count),
        },
    )
