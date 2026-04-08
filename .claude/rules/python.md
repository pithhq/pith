---
description: Python coding standards for PITH. Enforced on all .py files.
globs: "**/*.py"
---

# Python Standards — PITH

## Paths — Non-Negotiable
```python
# ALWAYS
from pathlib import Path
config_path = Path.home() / ".pith" / "config.json"
wiki_root = Path(config.wiki.root)

# NEVER
import os
config_path = os.path.join(os.path.expanduser("~"), ".pith", "config.json")
```

No string path concatenation. No `os.path`. `pathlib.Path` everywhere.

## Type Hints — Required Throughout
```python
# Required on all function signatures
def ingest_file(path: Path, config: PithConfig) -> IngestResult:
    ...

# Required on all class fields
class WikiEntity:
    entity_id: str
    entity_type: str
    content: str
    tags: list[str] = []
```

## Pydantic for All Config and Data Models
```python
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings

class PithConfig(BaseSettings):
    wiki_root: Path = Field(default=Path("./wiki"))
    schema_name: str = Field(...)
    
    model_config = ConfigDict(env_prefix="PITH_")

# Always validate on load — fail fast with clear error
config = PithConfig.model_validate_json(config_path.read_text())
```

## Typer CLI Patterns
```python
import typer
from typing import Annotated

app = typer.Typer(help="PITH — local knowledge intelligence system")

@app.command()
def ingest(
    path: Annotated[Path, typer.Argument(help="File or directory to ingest")],
    schema: Annotated[str | None, typer.Option("--schema", "-s")] = None,
    verbose: Annotated[bool, typer.Option("--verbose", "-v")] = False,
) -> None:
    """Ingest a source file into the wiki."""
    ...
```

## Error Handling
```python
# Specific exceptions with context
class PithSchemaError(Exception):
    """Raised when a schema file is invalid or missing."""

class PithIngestError(Exception):
    """Raised when file ingestion fails."""

# Always include context in error messages
try:
    schema = load_schema(schema_path)
except FileNotFoundError:
    raise PithSchemaError(
        f"Schema not found at {schema_path}. "
        f"Run 'pith init' to configure a schema."
    ) from None
```

## Testing — Required for All Parsers
```python
# tests/parsers/test_pdf_parser.py
import pytest
from pathlib import Path
from pith.parsers.pdf import PdfParser

FIXTURES = Path(__file__).parent / "fixtures"

def test_extracts_text_from_simple_pdf():
    parser = PdfParser()
    result = parser.parse(FIXTURES / "simple.pdf")
    assert result.content
    assert result.page_count == 1

def test_handles_scanned_pdf_gracefully():
    parser = PdfParser()
    result = parser.parse(FIXTURES / "scanned.pdf")
    # Scanned PDFs return empty content, not error
    assert result.content == ""
    assert result.requires_ocr is True
```

## Imports — Organized
```python
# Standard library
import json
from pathlib import Path
from typing import Any

# Third-party
import typer
from pydantic import BaseModel
import httpx

# Internal
from pith.config import PithConfig
from pith.schema import SchemaLoader
```

## i18n — From Day One
```python
# Never hardcode user-facing strings
# ❌
print("Schema not found. Run pith init first.")

# ✅ 
from pith.i18n import t
print(t("error.schema_not_found"))
```
