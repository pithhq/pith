"""PDF parser — text-layer extraction via pdfplumber with OCR fallback.

Text-based pages use pdfplumber directly. Pages with no extractable
text fall back to pytesseract OCR on the rendered page image.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path

import pdfplumber

from pith.i18n import t
from pith.parsers.base import ParsedDocument, ParseError, Section, Table


def _set_tessdata_prefix() -> None:
    """Set TESSDATA_PREFIX if not already set, based on OS defaults."""
    if os.environ.get("TESSDATA_PREFIX"):
        return

    system = platform.system()
    candidates: list[Path] = {
        "Linux":   [Path("/usr/share/tessdata")],
        "Darwin":  [
            Path("/opt/homebrew/share/tessdata"),   # Apple Silicon
            Path("/usr/local/share/tessdata"),       # Intel
        ],
        "Windows": [
            Path(r"C:\Program Files\Tesseract-OCR\tessdata"),
        ],
    }.get(system, [])

    for path in candidates:
        if path.exists():
            os.environ["TESSDATA_PREFIX"] = str(path)
            return

def _ocr_language() -> str:
    """Determine the pytesseract language hint from config.
    Tries to load ``pith.config.json`` from the current directory.
    If the config specifies ``mixed_script: true``, returns
    ``"srp+srp_latn"`` for Serbian mixed-script support.
    Otherwise falls back to ``"eng"``.
    """
    _LANG_MAP: dict[str, str] = {
        "en": "eng",
        "sr": "srp",
        "de": "deu",
        "fr": "fra",
        "es": "spa",
        "it": "ita",
        "pt": "por",
    }
    try:
        from pith.config import load_config
        cfg = load_config(Path("pith.config.json"))
        if cfg.vault.mixed_script:
            return "srp+srp_latn"
        if cfg.vault.language:
            return _LANG_MAP.get(cfg.vault.language, cfg.vault.language)
    except Exception:
        pass
    return "eng"


def _ocr_page(page: pdfplumber.pdf.Page) -> str:
    _set_tessdata_prefix()
    image = page.to_image().original
    """Render a page to an image and run pytesseract OCR.

    Args:
        page: A pdfplumber page object.

    Returns:
        Extracted text from OCR.

    Raises:
        ParseError: If pytesseract is not installed.
    """
    try:
        import pytesseract
    except ImportError:
        raise ParseError(
            Path("<ocr>"),
            t("parsers.ocr_not_available"),
        )

    image = page.to_image().original
    lang = _ocr_language()
    return pytesseract.image_to_string(image, lang=lang)


def parse_pdf(path: Path) -> ParsedDocument:
    """Parse a PDF into a ``ParsedDocument``.

    Text-based pages use pdfplumber extraction. Pages that yield no
    text fall back to pytesseract OCR on the rendered page image.

    Args:
        path: Path to the PDF file.

    Returns:
        A ``ParsedDocument`` with one section per page and any
        tables found across all pages. Metadata includes
        ``ocr_used: "true"`` if any page required OCR.

    Raises:
        ParseError: If the file cannot be opened, contains no
            extractable text (even after OCR), or pytesseract
            is not installed when OCR is needed.
    """
    try:
        pdf = pdfplumber.open(path)
    except Exception as exc:
        raise ParseError(path, t("parser.pdf_read_error", detail=str(exc))) from exc

    sections: list[Section] = []
    tables: list[Table] = []
    page_count = len(pdf.pages)
    ocr_used = False

    try:
        for page in pdf.pages:
            text = page.extract_text() or ""

            if not text.strip():
                text = _ocr_page(page)
                if text.strip():
                    ocr_used = True

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

    metadata: dict[str, str] = {
        "source": str(path),
        "format": "pdf",
        "pages": str(page_count),
    }
    if ocr_used:
        metadata["ocr_used"] = "true"

    return ParsedDocument(
        title=path.stem,
        sections=sections,
        tables=tables,
        metadata=metadata,
    )
