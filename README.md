# PITH

Your knowledge, compiled.

PITH is a self-contained, locally deployable knowledge intelligence system.
Raw documents go in. A compiled, cross-referenced, growing wiki comes out.
Knowledge compounds over time. Data never leaves your infrastructure.

PITH is not a RAG system. The wiki is a persistent compiled artifact,
not a retrieval index.

## Install

```
pip install pithhq
```

## Usage

```
pith init            # guided setup wizard
pith ingest file.pdf # ingest source files into wiki
pith query "..."     # query wiki using local model
pith lint            # health check
pith sync            # manual git commit + push
pith export          # export wiki to PDF/DOCX/CSV
pith activate KEY    # offline license activation
```

## Development Setup

```
make install
make test
make lint
```

## Schema Packs

Schema packs (vertical-specific entity definitions, lint rules, and
ingest instructions) are distributed separately from this engine.
The schema format is documented and stable — anyone can write personal
schemas. Pre-built, domain-researched vertical packs are available
as a paid product at [pithhq.com](https://pithhq.com).

## License

Apache 2.0. See [LICENSE](LICENSE) for details.
