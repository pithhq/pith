"""Tests for CSV export using stdlib csv (P9)."""

from __future__ import annotations

import csv

from pith.export import WikiPage, _export_csv


def _make_page(
    title: str = "Test Page",
    body: str = "Hello world",
) -> WikiPage:
    return WikiPage(
        title=title,
        source="test.pdf",
        ingested_at="2026-01-01T00:00:00",
        schema="test-schema",
        references_legislation="",
        body=body,
    )


def test_csv_export_writes_header_and_rows(tmp_path):
    """CSV output contains correct header and row data."""
    pages = [_make_page(title="Page 1"), _make_page(title="Page 2")]
    out = tmp_path / "export.csv"

    _export_csv(pages, out)

    with out.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows) == 2
    assert rows[0]["title"] == "Page 1"
    assert rows[1]["title"] == "Page 2"
    assert set(reader.fieldnames or []) == {
        "title", "source", "ingested_at", "schema",
        "references_legislation", "body",
    }


def test_csv_export_truncates_body(tmp_path):
    """Body field is truncated to 500 characters."""
    long_body = "x" * 1000
    pages = [_make_page(body=long_body)]
    out = tmp_path / "export.csv"

    _export_csv(pages, out)

    with out.open(encoding="utf-8") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    assert len(rows[0]["body"]) == 500
