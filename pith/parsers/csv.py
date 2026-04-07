"""CSV parser — extraction via pandas.

The entire CSV becomes a single Section (heading = filename stem)
and a single Table (first row = headers via pandas).
Delimiter is auto-detected.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from pith.i18n import t
from pith.parsers.base import ParsedDocument, ParseError, Section, Table


def parse_csv(path: Path) -> ParsedDocument:
    """Parse a CSV file into a ``ParsedDocument``.

    Uses pandas with ``sep=None`` and ``engine="python"`` to
    auto-detect the delimiter.

    Args:
        path: Path to the ``.csv`` file.

    Returns:
        A ``ParsedDocument`` with a single section and table.

    Raises:
        ParseError: If the file is malformed or unreadable.
    """
    try:
        df = pd.read_csv(str(path), sep=None, engine="python")
    except Exception as exc:
        raise ParseError(path, t("parser.csv_read_error", detail=str(exc))) from exc

    headers = [str(c) for c in df.columns.tolist()]
    rows: list[list[str]] = []
    for _, row in df.iterrows():
        rows.append([str(v) if pd.notna(v) else "" for v in row])

    body_lines = ["\t".join(headers)]
    for r in rows:
        body_lines.append("\t".join(r))

    sections: list[Section] = []
    if body_lines:
        sections.append(Section(heading=path.stem, body="\n".join(body_lines)))

    return ParsedDocument(
        title=path.stem,
        sections=sections,
        tables=[Table(headers=headers, rows=rows)],
        metadata={
            "source": str(path),
            "format": "csv",
            "row_count": str(len(rows)),
            "column_count": str(len(headers)),
        },
    )
