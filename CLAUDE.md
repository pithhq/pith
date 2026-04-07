# PITH — Development Context

## What PITH Is

PITH is a self-contained, locally deployable knowledge intelligence
system. Raw documents go in. A compiled, cross-referenced, growing
wiki comes out. Knowledge compounds over time. Data never leaves
the client's infrastructure.

Core distinction: PITH is NOT a RAG system. The wiki is a
persistent compiled artifact, not a retrieval index. Every ingest
makes it richer. Ask again in six months — a RAG system's knowledge
base is identical. PITH's has been growing.

## Brand

Name: PITH (always all caps)
Tagline: "Your knowledge, compiled."
Domain: pithhq.com
Email: hello@pithhq.com
GitHub: github.com/pithhq
PyPI: pithhq

Never write: "Pith", "pith", "PithHQ", "Pith HQ"
Domains and handles use lowercase: pithhq.com, @pithhq

### Colours
Obsidian:   #111110  — primary background
Surface:    #1C1B18  — secondary background
Parchment:  #F7F6F2  — light background
Copper:     #B07858  — accent (warnings, tags, highlights)
Sage:       #5C8A5A  — success states
Stone:      #E0DDD0  — UI elements, tags

### Voice
Precise. Honest. Direct. Calm. No filler words.
No exclamation marks. No AI hype language.
CLI output: terse, factual, no emoji.

## Technical Stack (locked)

Language:           Python
CLI framework:      typer
Config validation:  pydantic + pydantic-settings
File parsers:
  PDF (text):       pdfplumber
  PDF (scanned):    pytesseract (v1.1)
  DOCX:             python-docx
  Excel/CSV:        openpyxl + pandas
  PPTX:             python-pptx
Git operations:     gitpython
HTTP:               httpx (async)
CLI packaging:      pyinstaller
GUI framework:      Tauri (Rust runtime + Python sidecar)
GUI ships:          v1.0 alongside CLI (not a later addition)

## Architecture (locked)

Four independently swappable layers:

1. Storage     — local filesystem (default), NAS mount,
                 cloud-synced folder
2. Model       — Ollama (local), Anthropic API,
                 OpenAI-compatible endpoint
3. Schema      — vertical-specific YAML + AGENT.md pairs
4. Interface   — Obsidian (wiki), Open WebUI (team queries),
                 CLI (power users) — all three simultaneously

Model split (locked):
 Ingest:  Ollama + Gemma 4 (default) — local, private
         Anthropic API (claude-sonnet-4-5-20250929) — opt-in for quality
         Note: Anthropic ingest sends document chunks to external API
  Query:   Ollama + Gemma 4 — private, zero marginal cost
  Lint:    Ollama + Gemma 4

## CLI Commands

pith init          — guided setup wizard
pith ingest [file] — ingest source files into wiki
pith query [text]  — query wiki using local model
pith lint          — health check: orphans, contradictions,
                     stale legislation references
pith sync          — manual git commit + push
pith export        — export wiki to PDF/DOCX/CSV
pith activate [key]— offline license activation

## Config Format (locked — treat as public API)

File: pith.config.json
Breaking changes require migration scripts.
Adding fields with defaults = non-breaking.
Removing or renaming fields = breaking.

API keys NEVER stored in config — environment variables only.

Key sections:
  vault:    path, schema name + version, language settings
  models:   provider + model per operation (ingest/query/lint)
  providers:api_key_env references, Ollama base_url
  ingest:   chunk_size_tokens, overlap, format support
  sync:     remote type, interval, active hours
  lint:     schedule, day, time, check toggles
  privacy:  telemetry (false), update_check (true)
  license:  written by activation — never by user
  ui:       Obsidian path, Open WebUI port

## Schema Format (locked)

Each schema pack: schemas/[vertical-name]/
  schema.yaml  — entities, cross-references, lint rules,
                 ingest hints, references_legislation tracking
  AGENT.md     — LLM ingest instructions (not CLAUDE.md —
                 that name is Anthropic-specific)
  seeds/       — 3-5 example wiki pages shipped with schema
  README.md    — domain-language guide for practitioners,
                 not developers

Schema packs live in a SEPARATE PRIVATE REPO from the
open source engine. Referenced via submodule or separate
package install in the product build.

## Open Core Boundary (locked)

Apache 2.0 (open source — public repo):
  - CLI engine (all commands)
  - All file format parsers
  - Git sync layer
  - Model provider abstraction
  - Schema loader and validator
  - AGENT.md template system
  - Frontmatter tracking system

Proprietary (paid product — private repo):
  - Vertical schema packs
  - GUI installer and setup wizard
  - Obsidian configuration pack
  - Priority support tier

The schema FORMAT (schema.yaml structure) is documented
and stable — anyone can write personal schemas. We only
sell pre-built, domain-researched, tested vertical packs.

## Platform Support (locked — all from v1.0)

Windows:  native .exe (pyinstaller + bundled git)
macOS:    .dmg
Linux:    AppImage

Path handling: pathlib.Path EVERYWHERE.
String concatenation with / or \ is forbidden.

OS schedulers (git auto-sync):
  Linux:   systemd timer
  macOS:   launchd plist
  Windows: Task Scheduler
All three generated automatically by `pith init`.

Windows code signing: Sectigo certificate required
before launch to prevent Defender false positives.

## Privacy Constraints (non-negotiable)

- No telemetry whatsoever
- No account required to use the product
- API keys in environment variables only — never config file
- License validation offline after first activation
- Update check: single GET to api.pithhq.com/version,
  no user identifier sent, opt-out via config flag

## License System

Provider:    Lemon Squeezy (Merchant of Record — handles
             VAT, sales tax globally)
Validation:  offline after first activation via signed
             license file + machine fingerprint (hashed
             hardware ID)
Tiers:       Personal (1 machine)
             Team (5 machines)
             Enterprise (unlimited)

## Business Context

Legal entity:  Wyoming LLC
Payment:       Lemon Squeezy
Trademark:     PITH — filing USPTO Classes 9 + 42
               EUIPO within 6 months of USPTO filing date

## First Vertical: Law Firm (Serbian)

Schema name:   law-firm-sr
Language:      Serbian, Latin + Cyrillic (mixed_script: true)
Client:        Law firm, Belgrade (beta tester)
Entities:      client, matter, precedent, doctrine
Key feature:   references_legislation frontmatter field
               enables staleness tracking when laws update

Law update workflow: client ingests updated legislation →
ingest creates/updates doctrine page → targeted lint pass
flags all pages with references_legislation matching the
updated statute → client reviews flagged pages.

## Development Phases

Phase 1 (6 weeks):
  Config system, schema loader/validator, file parsers
  (PDF text, DOCX, plain text, markdown), ingest pipeline,
  git sync automation.
  Deliverable: `pith ingest file.pdf` produces correct wiki page.

Phase 2 (4 weeks):
  Query layer (Ollama + Gemma 4), lint pass,
  `pith init` CLI wizard.
  Deliverable: full CLI working end-to-end.

Phase 3 (3 weeks):
  Excel/CSV, PPTX parsers, scanned PDF OCR (pytesseract),
  law-firm-sr schema v1 tested on real documents.
  Deliverable: law firm schema working on real legal docs.

Phase 4 (6 weeks):
  Tauri GUI (setup wizard, dashboard, ingest panel, settings),
  pyinstaller Windows binary, macOS dmg, Linux AppImage,
  Lemon Squeezy license system integration.
  Deliverable: installable product on all three platforms.

Phase 5 (2 weeks):
  Landing page on pithhq.com, launch prep.
  Deliverable: public launch.

## Coding Standards

- pathlib.Path for ALL file paths — no exceptions
- pydantic validation on every config load at startup
- i18n string table from day one (gettext) — no hardcoded
  user-facing strings anywhere in the codebase
- Type hints throughout — no untyped functions
- Black formatting, ruff linting
- Tests required for all parsers before merge
- No hardcoded colors or strings in CLI output —
  all routed through the output module

## CLI Output Standards

Copper (#B07858): warnings, flagged items
Sage (#5C8A5A):   success, clean states
Red:              errors only
No color:         progress, informational

Format: "N pages updated · N created · N conflicts"
Never: emoji, exclamation marks, cheerful language

## Key Reminders for Claude Code Sessions

- Schema packs are in a SEPARATE private repo
- AGENT.md (not CLAUDE.md) is the per-schema LLM instruction file
- The config format is a public API — no breaking changes
  without migration scripts
- Windows path handling requires pathlib.Path — enforce at PR
- pyinstaller bundles git for Windows — verify in build spec
- Lemon Squeezy license keys start with `pithhq_`
- The product is PITH, the org is pithhq, never mix the casing
