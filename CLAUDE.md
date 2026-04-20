# PITH — Development Context

**PITH** is a self-contained, locally deployable knowledge intelligence system. Raw documents go in. A compiled, cross-referenced, growing wiki comes out. Knowledge compounds over time. Data never leaves the client's infrastructure.

Core insight: PITH is NOT RAG. The wiki is a persistent compiled artifact, not a retrieval index. Every ingest makes it richer. The LLM does the bookkeeping humans abandon.

**Status: Personal use only. No commercial launch planned.**

---

## Project Context

```
Project Name:     PITH
Type:             desktop CLI tool
Track:            software
Primary Stack:    Python 3.12+, Typer, Pydantic
Target Platform:  Linux (primary), macOS, Windows
Current Phase:    Personal simplification
Repository:       github.com/pithhq/pith
```

---

## Architecture

**Four modular layers:**

1. **Storage**: local filesystem (default), NAS mount, cloud-synced folder
2. **LLM**: all calls route through `claude -p` (Claude Code CLI via Max subscription)
3. **Schema**: vertical-specific YAML + AGENT.md pairs — the extensible knowledge layer
4. **Interface**: Obsidian (wiki browsing), CLI (power users)

**Model layer:**
- All operations (ingest, query, lint) use `claude -p --model [model]`
- No API keys needed — routes through Claude Code Max subscription
- Model per operation is configurable in `pith.config.json`
- Default: `claude-sonnet-4-6` for all operations

---

## Tech Stack

```
Language:           Python 3.12+
CLI framework:      Typer
Schema validation:  Pydantic + pydantic-settings
Config validation:  Pydantic
LLM interface:      subprocess → claude -p (Claude Code CLI)
File parsers:       pdfplumber (PDF text)
                    python-docx (DOCX)
                    openpyxl / pandas (Excel/CSV)
                    python-pptx (PPTX)
                    pytesseract (scanned PDF OCR — v1.1)
Git operations:     gitpython
Packaging:          PyInstaller (CLI binary)
Testing:            pytest + pytest-cov
Formatting:         Black
Linting:            ruff
Type checking:      mypy
```

---

## CLI Commands

```bash
pith init          # Guided setup wizard — creates pith.config.json
pith ingest [file] # Ingest one or more source files into wiki
pith query [text]  # Query the wiki
pith lint          # Health check: orphans, contradictions, stale refs
pith sync          # Manual git commit + push
pith export        # Export wiki to PDF/DOCX/CSV
```

All command signatures are stable and locked. Do not change them.

---

## Config Format (pith.config.json)

```json
{
  "vault": {
    "path": "./wiki",
    "schema": "law-firm-sr",
    "language": "en"
  },
  "models": {
    "ingest": "claude-sonnet-4-6",
    "query": "claude-sonnet-4-6",
    "lint": "claude-sonnet-4-6"
  },
  "sync": {
    "interval_minutes": 30
  },
  "privacy": {
    "telemetry": false,
    "update_check": true
  }
}
```

---

## Schema Format (Locked)

Each schema pack lives at: `schemas/[vertical-name]/`
```
schema.yaml    — entity definitions, cross-reference rules, lint rules, staleness windows
AGENT.md       — LLM instruction layer for ingest pipeline
seeds/         — 3-5 example wiki pages shipped with schema
README.md      — human-readable guide for this vertical
```

---

## Privacy Constraints (Non-Negotiable)

- No telemetry (zero — never send usage data)
- No account required
- No API keys in config files — LLM calls go through `claude -p` (no key needed)
- Update check: single GET to `api.pithhq.com/version`, no user identifier sent, opt-out via config

These constraints are the product's identity. Never compromise them for convenience.

---

## Coding Standards (Locked)

- `pathlib.Path` for ALL file paths — never string concatenation
- No hardcoded strings — i18n string table from day one (gettext)
- Pydantic validation on every config load — fail fast with clear error
- Tests required for all parsers — no untested file format code ships
- Type hints throughout — mypy must pass with no errors
- Black formatting, ruff linting — enforced in CI
- Commits: conventional commits (`feat:`, `fix:`, `chore:`, `docs:`, `refactor:`)

---

## Platform Support

- Windows: `.exe` native (PyInstaller + git bundled)
- macOS: `.dmg` (PyInstaller + code signing via Sectigo)
- Linux: `AppImage`
- OS scheduler: systemd (Linux), launchd (macOS), Task Scheduler (Windows)

---

## Planned Integrations

### Firecrawl (URL ingest)

- Purpose: `pith ingest [url]` scrapes clean text via Firecrawl
  before passing to the ingest pipeline
- Alternative: direct fetch (no external service) with a --local-fetch flag

### GWS CLI (export channel)

- Purpose: `pith export --channel=gdoc` pushes compiled wiki pages
  to Google Drive

## Current Verticals

**law-firm-sr** (v1 — complete)
- Serbian law firm schema
- Languages: Serbian Latin + Cyrillic
- Entities: client, matter, precedent, doctrine
- Key feature: `references_legislation` frontmatter for staleness tracking

**writing-agency** (v1 — in development)
- Writing company client intelligence schema
- Entities: client, voice-document, brief, deliverable, research-note, contributor, performance-record
- Key feature: outcome tracking loop, cross-client knowledge graph

---

## Session Rules

1. Read this CLAUDE.md at the start of every session
2. Check `wiki/` for current development state if it exists
3. Privacy constraints are non-negotiable — never compromise them
4. pathlib.Path everywhere — if you see string path concatenation, fix it
5. All parsers need tests — no exceptions
