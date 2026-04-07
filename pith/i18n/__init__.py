"""Internationalisation — all user-facing strings live here.

Usage:
    from pith.i18n import t
    error(t("config.not_found", path=path))

Keys follow dot notation: module.snake_case_description.
Placeholders use str.format_map — {name} syntax.

Only English strings ship in the open source engine.
Translated .po/.mo files are loaded at runtime if present.
"""

from __future__ import annotations

import gettext
import os
from pathlib import Path

_LOCALE_DIR = Path(__file__).parent / "locale"
_DOMAIN = "pith"

# Attempt to load a compiled translation catalogue.
# Falls back to the identity function if none is found.
try:
    _lang = os.environ.get("PITH_LANG") or os.environ.get("LANG", "en")[:2]
    _translation = gettext.translation(
        _DOMAIN,
        localedir=str(_LOCALE_DIR),
        languages=[_lang],
    )
    _translation.install()
    _gettext = _translation.gettext
except FileNotFoundError:
    _gettext = lambda s: s  # noqa: E731


# String table — English source strings, keyed by dot-notation id.
_STRINGS: dict[str, str] = {
    # config
    "config.not_found":          "config file not found: {path}",
    "config.invalid":            "config validation failed: {detail}",
    "config.api_key_missing":    "environment variable {var} is not set",

    # ingest
    "ingest.start":              "ingesting {path}",
    "ingest.unsupported_format": "unsupported format: {suffix}",
    "ingest.summary":            "{updated} pages updated · {created} created · {conflicts} conflicts",
    "ingest.chunk_progress":     "chunk {current}/{total} sent",
    "ingest.api_error":          "API error on chunk {index}: {detail}",
    "ingest.writing_page":       "writing wiki page: {path}",
    "ingest.parse_failed":       "could not parse {path}: {detail}",

    # parsers
    "parser.file_not_found":     "file not found: {path}",
    "parser.pdf_no_text":        "no extractable text in PDF: {path}",
    "parser.pdf_read_error":     "failed to read PDF: {detail}",
    "parser.docx_read_error":    "failed to read DOCX: {detail}",
    "parser.text_read_error":    "failed to read text file: {detail}",

    # schema
    "schema.not_found":          "schema not found: {name}",
    "schema.version_mismatch":   "schema version mismatch: expected {expected}, got {got}",

    # sync
    "sync.no_remote":            "no remote configured — skipping push",
    "sync.committed":            "committed {n} changes",

    # lint
    "lint.orphans":              "{n} orphaned pages",
    "lint.contradictions":       "{n} contradictions detected",
    "lint.stale_references":     "{n} stale legislation references",
    "lint.clean":                "no issues found",

    # license
    "license.invalid":           "license invalid or expired",
    "license.activated":         "license activated on this machine",
}


def t(key: str, **kwargs: object) -> str:
    """Look up a string by key and interpolate placeholders.

    Args:
        key:    Dot-notation string key, e.g. "ingest.summary".
        **kwargs: Placeholder values for str.format_map.

    Returns:
        The translated and interpolated string.

    Raises:
        KeyError: If the key is not in the string table.
    """
    raw = _STRINGS[key]
    translated = _gettext(raw)
    if kwargs:
        return translated.format_map(kwargs)
    return translated