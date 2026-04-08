---
name: python-cli-patterns
description: Python CLI development patterns for PITH — Typer commands, Pydantic config, file parsers, async httpx, and PyInstaller packaging conventions.
globs: "pith/**/*.py,tests/**/*.py"
---

# Python CLI Patterns (PITH Stack)

## Typer Command Structure
```python
# pith/cli.py
import typer
from pathlib import Path
from typing import Annotated
from rich.console import Console
from rich.progress import Progress

app = typer.Typer(
    name="pith",
    help="PITH — local knowledge intelligence system",
    no_args_is_help=True,
)
console = Console()

@app.command()
def ingest(
    path: Annotated[Path, typer.Argument(
        help="File or directory to ingest",
        exists=True,
    )],
    schema: Annotated[str | None, typer.Option(
        "--schema", "-s",
        help="Schema to use (overrides config)"
    )] = None,
    verbose: Annotated[bool, typer.Option(
        "--verbose", "-v",
        help="Show detailed progress"
    )] = False,
) -> None:
    """Ingest a source file into the wiki."""
    config = load_config()
    
    with Progress() as progress:
        task = progress.add_task("Ingesting...", total=None)
        result = run_ingest(path, config, schema)
        progress.update(task, completed=True)
    
    console.print(f"[green]✓[/green] Ingested {path.name}")
    console.print(f"  Pages created: {result.pages_created}")
    console.print(f"  Pages updated: {result.pages_updated}")
```

## Pydantic Config Loading
```python
# pith/config.py
from pathlib import Path
from pydantic import BaseModel, Field, model_validator
from pydantic_settings import BaseSettings

class ModelConfig(BaseModel):
    provider: str = "ollama"
    model: str = "gemma4"
    base_url: str | None = None

class PithConfig(BaseSettings):
    wiki_root: Path = Field(default=Path("./wiki"))
    schema_name: str = Field(...)
    ingest_model: ModelConfig = Field(default_factory=ModelConfig)
    query_model: ModelConfig = Field(default_factory=ModelConfig)
    
    model_config = ConfigDict(
        env_prefix="PITH_",
        env_nested_delimiter="__",
    )
    
    @model_validator(mode="after")
    def validate_wiki_root(self) -> "PithConfig":
        if not self.wiki_root.exists():
            raise ValueError(
                f"Wiki root {self.wiki_root} does not exist. "
                "Run 'pith init' to set up a new wiki."
            )
        return self

def load_config(config_path: Path | None = None) -> PithConfig:
    path = config_path or Path.cwd() / "pith.config.json"
    if not path.exists():
        raise PithConfigError(
            f"No pith.config.json found at {path}. "
            "Run 'pith init' to get started."
        )
    return PithConfig.model_validate_json(path.read_text())
```

## File Parser Pattern
```python
# pith/parsers/base.py
from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path

@dataclass
class ParseResult:
    content: str
    metadata: dict[str, str]
    page_count: int = 1
    requires_ocr: bool = False
    
class BaseParser(ABC):
    @abstractmethod
    def supports(self, path: Path) -> bool:
        """Return True if this parser can handle the given file."""
        
    @abstractmethod
    def parse(self, path: Path) -> ParseResult:
        """Parse the file and return its content."""

# pith/parsers/pdf.py
import pdfplumber
from pith.parsers.base import BaseParser, ParseResult

class PdfParser(BaseParser):
    def supports(self, path: Path) -> bool:
        return path.suffix.lower() == ".pdf"
    
    def parse(self, path: Path) -> ParseResult:
        with pdfplumber.open(path) as pdf:
            pages = [page.extract_text() or "" for page in pdf.pages]
            content = "\n\n".join(pages).strip()
            return ParseResult(
                content=content,
                metadata={"source": str(path)},
                page_count=len(pdf.pages),
                requires_ocr=not bool(content),
            )
```

## Async httpx Pattern (for API calls)
```python
# pith/models/anthropic.py
import httpx
import os
from pith.i18n import t

async def synthesize_wiki_pages(
    content: str,
    agent_instructions: str,
    schema_context: str,
) -> str:
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise PithConfigError(t("error.anthropic_key_missing"))
    
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": api_key,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-sonnet-4-6",
                "max_tokens": 8192,
                "system": agent_instructions,
                "messages": [
                    {"role": "user", "content": content}
                ],
            },
            timeout=60.0,
        )
        response.raise_for_status()
        return response.json()["content"][0]["text"]
```

## PyInstaller Packaging
```python
# build.spec (PyInstaller spec file)
# Key patterns for PITH:

# Bundle git binary for Windows
binaries = [('C:/Program Files/Git/bin/git.exe', 'bin')]

# Include all schema files
datas = [
    ('pith/i18n/*.po', 'pith/i18n'),
    ('schemas/', 'schemas'),  # bundled open schemas only
]

# Hidden imports Pydantic needs
hiddenimports = [
    'pydantic.v1',
    'pydantic_settings',
    'pith.parsers.pdf',
    'pith.parsers.docx',
]
```
