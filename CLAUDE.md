# PITH — Development Context

**PITH** is a self-contained, locally deployable knowledge intelligence system. Raw documents go in. A compiled, cross-referenced, growing wiki comes out. Knowledge compounds over time. Data never leaves the client's infrastructure.

Core insight: PITH is NOT RAG. The wiki is a persistent compiled artifact, not a retrieval index. Every ingest makes it richer. The LLM does the bookkeeping humans abandon.

---

## Project Context

```
Project Name:     PITH
Type:             desktop CLI tool + Tauri GUI
Track:            software
Primary Stack:    Python 3.12+, Typer, Pydantic, PyInstaller, Tauri (Rust + Python sidecar)
Target Platform:  Windows (.exe), macOS (.dmg), Linux (AppImage)
Current Phase:    Phase 4 complete — production ready
Repository:       github.com/pithhq/pith
Domain:           pithhq.com
Email:            hello@pithhq.com
License:          Apache 2.0 (engine) + Proprietary (schema packs, GUI)
```

---

## Architecture (Locked)

**Four modular layers:**

1. **Storage**: local filesystem (default), NAS mount, cloud-synced folder
2. **Model provider**: Ollama (local queries), Anthropic API (ingest synthesis), OpenAI-compatible
3. **Schema**: vertical-specific YAML + AGENT.md pairs — the extensible knowledge layer
4. **Interface**: Obsidian (wiki browsing), Open WebUI (team queries), CLI (power users)

**Model split (locked):**
- Ingest/synthesis: Claude API — quality matters here
- Query (day-to-day): Ollama + Gemma 4 — private, zero marginal cost
- Lint: Ollama + Gemma 4

---

## Tech Stack (Locked)

```
Language:           Python 3.12+
CLI framework:      Typer
Schema validation:  Pydantic + pydantic-settings
Config validation:  Pydantic
File parsers:       pdfplumber (PDF text)
                    python-docx (DOCX)
                    openpyxl / pandas (Excel/CSV)
                    python-pptx (PPTX)
                    pytesseract (scanned PDF OCR — v1.1)
Git operations:     gitpython
API calls:          httpx (async)
Packaging:          PyInstaller (CLI binary)
GUI wrapper:        Tauri (Rust + Python sidecar)
Testing:            pytest + pytest-cov
Formatting:         Black
Linting:            ruff
Type checking:      mypy
```

---

## CLI Commands (Stable — Phase 4)

```bash
pith init          # Guided setup wizard — creates pith.config.json
pith ingest [file] # Ingest one or more source files into wiki
pith query [text]  # Query the wiki using local model
pith lint          # Health check: orphans, contradictions, stale refs
pith sync          # Manual git commit + push
pith export        # Export wiki to PDF/DOCX/CSV
pith activate [key]# License activation (Lemon Squeezy)
```

All command signatures are stable and locked. Do not change them.

---

## Open Core Boundary (Locked)

**Apache 2.0 (open source):**
- CLI engine (all commands)
- All file format parsers
- Git sync layer
- Model provider abstraction
- Schema loader and validator
- AGENT.md template system
- Frontmatter tracking system

**Proprietary (paid):**
- Vertical schema packs (law-firm-sr, writing-agency, etc.)
- GUI installer and setup wizard
- Obsidian configuration pack
- Priority support

Schema packs live in a **separate private repository** (`pithhq/pith-schemas`). Never commit schema pack files to the open source repo. Reference via git submodule or package install in the product build.

---

## Config Format (pith.config.json)

```json
{
  "version": "1.0",
  "wiki": {
    "root": "./wiki",
    "schema": "law-firm-sr"
  },
  "model": {
    "ingest": {
      "provider": "anthropic",
      "model": "claude-sonnet-4-6"
    },
    "query": {
      "provider": "ollama",
      "model": "gemma4",
      "base_url": "http://localhost:11434"
    }
  },
  "sync": {
    "enabled": true,
    "remote": "origin",
    "branch": "main",
    "auto_push": false
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
- No account required (license validation is offline after first activation)
- API keys in environment variables only — never in config file
- Update check: single GET to `api.pithhq.com/version`, no user identifier sent, opt-out via config
- License validation: offline after first activation (machine fingerprint hash)

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

## License System

- Provider: Lemon Squeezy (Merchant of Record — handles VAT globally)
- Tiers: Personal (1 machine), Team (5 machines), Enterprise (unlimited)
- Validation: offline after first activation
- Machine fingerprint: hashed hardware ID (never sent externally after activation)

---

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
3. The open core boundary is non-negotiable — never blur it
4. Privacy constraints are non-negotiable — never compromise them
5. pathlib.Path everywhere — if you see string path concatenation, fix it
6. All parsers need tests — no exceptions
7. Schema packs go in the private repo, never here
