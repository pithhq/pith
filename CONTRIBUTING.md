# Contributing to PITH

## Open Core Boundary

PITH uses an open core model. Understanding what lives where
is important before contributing.

### Apache 2.0 (this repository)

- CLI engine (all commands)
- All file format parsers
- Git sync layer
- Model provider abstraction
- Schema loader and validator
- AGENT.md template system
- Frontmatter tracking system

Contributions to any of the above are welcome.

### Proprietary (separate private repository)

- Vertical schema packs
- GUI installer and setup wizard
- Obsidian configuration pack
- Priority support tier

These components are not part of this repository.

### Schema Format

The schema format (schema.yaml structure) is documented and stable.
Anyone can write personal schemas. Pre-built vertical schema packs
are distributed separately as a paid product.

## Development Setup

```
make install
make test
make lint
```

## Standards

- pathlib.Path for all file paths. No string concatenation.
- Type hints on every function.
- i18n string table for all user-facing strings (gettext).
- Black formatting, ruff linting.
- Tests required for all parsers before merge.
