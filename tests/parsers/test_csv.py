"""Tests for the CSV parser."""

from __future__ import annotations

from pathlib import Path

import pytest

from pith.parsers.base import ParseError
from pith.parsers.csv import parse_csv


class TestParseCsv:
    def test_comma_delimited(self, tmp_path: Path) -> None:
        path = tmp_path / "data.csv"
        path.write_text("Name,Age\nAlice,30\nBob,25\n", encoding="utf-8")

        doc = parse_csv(path)

        assert doc.title == "data"
        assert len(doc.sections) == 1
        assert doc.sections[0].heading == "data"
        assert len(doc.tables) == 1
        assert doc.tables[0].headers == ["Name", "Age"]
        assert doc.tables[0].rows == [["Alice", "30"], ["Bob", "25"]]
        assert doc.metadata["source"] == str(path)
        assert doc.metadata["format"] == "csv"
        assert doc.metadata["row_count"] == "2"
        assert doc.metadata["column_count"] == "2"

    def test_semicolon_delimited(self, tmp_path: Path) -> None:
        path = tmp_path / "semi.csv"
        path.write_text("X;Y;Z\n1;2;3\n4;5;6\n", encoding="utf-8")

        doc = parse_csv(path)

        assert doc.tables[0].headers == ["X", "Y", "Z"]
        assert doc.tables[0].rows == [["1", "2", "3"], ["4", "5", "6"]]

    def test_tab_delimited(self, tmp_path: Path) -> None:
        path = tmp_path / "tabs.csv"
        path.write_text("A\tB\n10\t20\n", encoding="utf-8")

        doc = parse_csv(path)

        assert doc.tables[0].headers == ["A", "B"]
        assert doc.tables[0].rows == [["10", "20"]]

    def test_missing_values_become_empty(self, tmp_path: Path) -> None:
        path = tmp_path / "missing.csv"
        path.write_text("A,B,C\nfoo,,bar\n", encoding="utf-8")

        doc = parse_csv(path)

        assert doc.tables[0].rows[0] == ["foo", "", "bar"]

    def test_nonexistent_file_raises(self, tmp_path: Path) -> None:
        path = tmp_path / "does_not_exist.csv"

        with pytest.raises(ParseError) as exc_info:
            parse_csv(path)
        assert exc_info.value.path == path

    def test_single_column(self, tmp_path: Path) -> None:
        path = tmp_path / "single.csv"
        path.write_text("Items,\napple,\nbanana,\n", encoding="utf-8")

        doc = parse_csv(path)

        assert doc.tables[0].headers[0] == "Items"
        assert len(doc.tables[0].rows) == 2

    def test_dispatch_integration(self, tmp_path: Path) -> None:
        """Verify .csv routes through the dispatch map."""
        from pith.parsers import parse

        path = tmp_path / "dispatch.csv"
        path.write_text("H1,H2\nV1,V2\n", encoding="utf-8")

        doc = parse(path)
        assert doc.metadata["format"] == "csv"
