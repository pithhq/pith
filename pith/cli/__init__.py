"""PITH command-line interface — typer application."""

from __future__ import annotations

import importlib.metadata
from pathlib import Path
from typing import Optional

import typer
from pydantic import ValidationError

from pith.config import PithConfig, load_config
from pith.i18n import t
from pith import output

import asyncio

app = typer.Typer(add_completion=False)


def _load_config(config_path: Path) -> PithConfig:
    """Load and validate PITH config, handling errors with i18n messages.

    Raises:
        typer.Exit: On missing or invalid config file.
    """
    try:
        return load_config(config_path)
    except FileNotFoundError:
        output.error(t("config.not_found", path=config_path))
        raise typer.Exit(code=2)
    except ValidationError as exc:
        output.error(t("config.invalid", detail=str(exc)))
        raise typer.Exit(code=2)


@app.command()
def ingest(
    file: Path = typer.Argument(..., exists=True, readable=True),
    config: Optional[Path] = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to pith.config.json.",
    ),
) -> None:
    """Ingest a source file into the wiki."""
    config_path = config if config is not None else Path("pith.config.json")
    cfg = _load_config(config_path)

    from pith.ingest import ingest_file
    from pith.parsers.base import ParseError

    output.info(t("ingest.start", path=file))

    try:
        asyncio.run(ingest_file(file, cfg))
    except ParseError as exc:
        output.error(str(exc))
        raise typer.Exit(code=1)
    except ValueError as exc:
        # Missing API key raises ValueError from provider.resolve_api_key()
        output.error(t("config.api_key_missing", var=str(exc)))
        raise typer.Exit(code=3)


@app.command()
def version() -> None:
    """Print the PITH version."""
    ver = importlib.metadata.version("pithhq")
    output.info(f"PITH {ver}")
