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
    "parser.xlsx_read_error":    "failed to read Excel file: {detail}",
    "parser.xlsx_empty":         "no non-empty sheets in Excel file: {path}",
    "parser.csv_read_error":     "failed to read CSV file: {detail}",
    "parser.pptx_read_error":    "failed to read PowerPoint file: {detail}",
    "parser.pptx_slide_fallback":"Slide {n}",
    "parsers.ocr_not_available": "pytesseract is not installed — OCR fallback unavailable for scanned pages",

    # schema
    "schema.not_found":          "schema not found: {name}",
    "schema.version_mismatch":   "schema version mismatch: expected {expected}, got {got}",
    "schema.validation_error":   "schema {name} validation failed: {detail}",
    "schema.missing_yaml":       "schema.yaml not found at {path}",

    # sync
    "sync.no_remote":            "no remote configured — skipping push",
    "sync.committed":            "committed {n} changes",

    # lint
    "lint.orphans":              "{n} orphaned pages",
    "lint.contradictions":       "{n} contradictions detected",
    "lint.stale_references":     "{n} stale legislation references",
    "lint.clean":                "no issues found",
    "lint.orphan_detail":        "  orphan: {path}",
    "lint.contradiction_detail": "  contradiction: {a} <-> {b}: {detail}",
    "lint.stale_detail":         "  stale: {path}",
    "lint.running":              "running lint checks",
    "lint.skip_contradictions":  "skipping contradictions check: could not reach Ollama",
    "lint.no_vault":             "no vault path configured",

    # query
    "query.system_prompt":       "You are a knowledge assistant. Answer using only the following wiki pages as your source.\n\n{context}",
    "query.ollama_unreachable":  "could not reach Ollama at {url}: {detail}",
    "query.ollama_error":        "Ollama returned status {status}: {detail}",
    "query.no_pages":            "no wiki pages found in vault: {path}",

    # license
    "license.activating":        "activating license",
    "license.activated":         "license activated — tier: {tier}",
    "license.invalid_key":       "invalid license key format",
    "license.invalid":           "license invalid or expired",
    "license.machine_mismatch":  "license is registered to a different machine",

    # init wizard
    "init.welcome":              "PITH setup wizard",
    "init.prompt_vault_path":    "vault path (absolute or relative)",
    "init.confirm_create_vault": "directory {path} does not exist — create it?",
    "init.vault_created":        "created vault directory: {path}",
    "init.vault_not_created":    "vault directory not created — aborting",
    "init.prompt_schema":        "schema name (leave blank for none)",
    "init.prompt_language":      "language code",
    "init.prompt_mixed_script":  "enable mixed script support?",
    "init.prompt_ingest_provider": "ingest model provider (anthropic/ollama)",
    "init.invalid_provider":     "invalid provider: {value} — must be anthropic or ollama",
    "init.prompt_ingest_model":  "ingest model name",
    "init.prompt_query_lint_model": "query/lint model name (Ollama)",
    "init.prompt_ollama_url":    "Ollama base URL",
    "init.prompt_api_key_env":   "Anthropic API key env var name",
    "init.prompt_git_remote":    "git remote URL (leave blank for none)",
    "init.prompt_sync_interval": "sync interval in minutes",
    "init.config_written":       "wrote {path}",
    "init.example_written":      "wrote {path}",
    "init.complete":             "configuration written to pith.config.json",
    "init.ingest_provider_note": "note: anthropic sends document chunks to Anthropic's API — use ollama to keep all data local",

    # init scheduler
    "init.scheduler_service_desc": "PITH git sync",
    "init.scheduler_timer_desc":   "PITH git sync timer",
    "init.scheduler_written":      "wrote scheduler file: {path}",
    "init.scheduler_load_systemd": "run: systemctl --user enable --now pith-sync.timer",
    "init.scheduler_load_launchd": "run: launchctl load ~/Library/LaunchAgents/com.pithhq.sync.plist",
    "init.scheduler_load_windows": "run: schtasks /Create /XML pith-sync.xml /TN PithSync",
    "init.scheduler_no_appdata":   "APPDATA not set — cannot write scheduler file",
    "init.scheduler_unsupported":  "unsupported OS for scheduler: {os}",

    # export
    "export.start":              "exporting wiki to {fmt}",
    "export.complete":           "export written to {path}",
    "export.no_pages":           "no wiki pages found in vault",
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
