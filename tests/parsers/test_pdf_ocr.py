"""Tests for PDF parser OCR fallback via pytesseract."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pytest

from pith.parsers.base import ParseError
from pith.parsers.pdf import parse_pdf


def _make_page(*, text: str | None, page_number: int) -> MagicMock:
    """Create a mock pdfplumber page."""
    page = MagicMock()
    page.extract_text.return_value = text
    page.extract_tables.return_value = []
    page.page_number = page_number
    page.to_image.return_value = SimpleNamespace(original=MagicMock())
    return page


@pytest.fixture()
def mock_pdf():
    """Patch pdfplumber.open to return controlled pages."""

    def _build(pages: list[MagicMock]):
        pdf = MagicMock()
        pdf.pages = pages
        pdf.close = MagicMock()
        patcher = patch("pith.parsers.pdf.pdfplumber")
        mock_plumber = patcher.start()
        mock_plumber.open.return_value = pdf
        return patcher

    return _build


def _make_pytesseract_mock(return_value: str = "OCR text") -> MagicMock:
    """Create a mock pytesseract module."""
    mock = MagicMock()
    mock.image_to_string.return_value = return_value
    return mock


class TestOcrFallback:
    def test_ocr_triggered_on_blank_page(
        self, tmp_path: Path, mock_pdf: object
    ) -> None:
        """A page with no text layer triggers OCR and sets metadata."""
        blank_page = _make_page(text=None, page_number=1)
        patcher = mock_pdf([blank_page])
        mock_tess = _make_pytesseract_mock("OCR extracted text")

        with patch.dict(sys.modules, {"pytesseract": mock_tess}):
            with patch("pith.parsers.pdf._ocr_language", return_value="eng"):
                doc = parse_pdf(tmp_path / "scan.pdf")

        assert len(doc.sections) == 1
        assert doc.sections[0].body == "OCR extracted text"
        assert doc.metadata["ocr_used"] == "true"
        mock_tess.image_to_string.assert_called_once()
        patcher.stop()

    def test_no_ocr_when_text_present(
        self, tmp_path: Path, mock_pdf: object
    ) -> None:
        """Pages with text do not trigger OCR."""
        text_page = _make_page(text="Hello world", page_number=1)
        patcher = mock_pdf([text_page])
        mock_tess = _make_pytesseract_mock()

        with patch.dict(sys.modules, {"pytesseract": mock_tess}):
            doc = parse_pdf(tmp_path / "text.pdf")

        assert len(doc.sections) == 1
        assert doc.sections[0].body == "Hello world"
        assert "ocr_used" not in doc.metadata
        mock_tess.image_to_string.assert_not_called()
        patcher.stop()

    def test_mixed_pages(self, tmp_path: Path, mock_pdf: object) -> None:
        """Mix of text and blank pages: OCR only on blank ones."""
        text_page = _make_page(text="Page one text", page_number=1)
        blank_page = _make_page(text="   ", page_number=2)
        patcher = mock_pdf([text_page, blank_page])
        mock_tess = _make_pytesseract_mock("OCR page two")

        with patch.dict(sys.modules, {"pytesseract": mock_tess}):
            with patch("pith.parsers.pdf._ocr_language", return_value="eng"):
                doc = parse_pdf(tmp_path / "mixed.pdf")

        assert len(doc.sections) == 2
        assert doc.sections[0].body == "Page one text"
        assert doc.sections[1].body == "OCR page two"
        assert doc.metadata["ocr_used"] == "true"
        assert doc.metadata["pages"] == "2"
        patcher.stop()

    def test_pytesseract_not_installed_raises(
        self, tmp_path: Path, mock_pdf: object
    ) -> None:
        """Missing pytesseract raises ParseError with correct i18n key."""
        blank_page = _make_page(text=None, page_number=1)
        patcher = mock_pdf([blank_page])

        # Remove pytesseract from sys.modules so import fails
        saved = sys.modules.pop("pytesseract", None)
        try:
            with patch.dict(sys.modules, {"pytesseract": None}):
                with pytest.raises(ParseError) as exc_info:
                    parse_pdf(tmp_path / "scan.pdf")
                assert "pytesseract" in exc_info.value.detail
        finally:
            if saved is not None:
                sys.modules["pytesseract"] = saved
            patcher.stop()

    def test_ocr_returns_empty_still_skips_page(
        self, tmp_path: Path, mock_pdf: object
    ) -> None:
        """If OCR also returns empty text, the page is skipped."""
        blank_page = _make_page(text=None, page_number=1)
        text_page = _make_page(text="Real content", page_number=2)
        patcher = mock_pdf([blank_page, text_page])
        mock_tess = _make_pytesseract_mock("   ")

        with patch.dict(sys.modules, {"pytesseract": mock_tess}):
            with patch("pith.parsers.pdf._ocr_language", return_value="eng"):
                doc = parse_pdf(tmp_path / "partial.pdf")

        assert len(doc.sections) == 1
        assert doc.sections[0].body == "Real content"
        assert "ocr_used" not in doc.metadata
        patcher.stop()


class TestOcrLanguage:
    def test_mixed_script_config(self) -> None:
        """Config with mixed_script=true returns srp+srp_latn."""
        from pith.parsers.pdf import _ocr_language

        mock_cfg = MagicMock()
        mock_cfg.vault.mixed_script = True
        mock_cfg.vault.language = "sr"

        with patch("pith.config.load_config", return_value=mock_cfg):
            assert _ocr_language() == "srp+srp_latn"

    def test_language_from_config(self) -> None:
        """Config with language set (no mixed_script) returns that language."""
        from pith.parsers.pdf import _ocr_language

        mock_cfg = MagicMock()
        mock_cfg.vault.mixed_script = False
        mock_cfg.vault.language = "deu"

        with patch("pith.config.load_config", return_value=mock_cfg):
            assert _ocr_language() == "deu"

    def test_no_config_defaults_to_eng(self) -> None:
        """When config cannot be loaded, default to eng."""
        from pith.parsers.pdf import _ocr_language

        with patch("pith.config.load_config", side_effect=FileNotFoundError):
            assert _ocr_language() == "eng"
