"""PITH command-line interface — typer application."""

from __future__ import annotations

import asyncio
import importlib.metadata
from pathlib import Path

import typer
from pydantic import ValidationError

from pith import output
from pith.config import PithConfig, load_config
from pith.i18n import t

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
    config: Path | None = typer.Option(
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


@app.command()
def query(
    text: str = typer.Argument(..., help="Question to ask the wiki."),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to pith.config.json.",
    ),
) -> None:
    """Query the wiki using the local model."""
    config_path = config if config is not None else Path("pith.config.json")
    cfg = _load_config(config_path)

    from pith.query import QueryError, query_wiki

    try:
        query_wiki(text, cfg)
    except QueryError as exc:
        output.error(exc.detail)
        raise typer.Exit(code=1)


@app.command()
def lint(
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to pith.config.json.",
    ),
) -> None:
    """Run wiki health checks."""
    config_path = config if config is not None else Path("pith.config.json")
    cfg = _load_config(config_path)

    from pith.lint import run_lint

    result = asyncio.run(run_lint(cfg))
    has_findings = result.orphans or result.contradictions or result.stale
    if has_findings:
        raise typer.Exit(code=1)


@app.command()
def init() -> None:
    """Run the interactive setup wizard."""
    from pith.init import run_wizard

    run_wizard()


@app.command()
def export(
    fmt: str = typer.Option(
        "pdf",
        "--format",
        "-f",
        help="Export format: pdf, docx, csv.",
    ),
    output_path: Path | None = typer.Option(
        None,
        "--output",
        "-o",
        help="Output file path.",
    ),
    config: Path | None = typer.Option(
        None,
        "--config",
        "-c",
        help="Path to pith.config.json.",
    ),
) -> None:
    """Export wiki to PDF, DOCX, or CSV."""
    from pith.export import ExportFormat, export_wiki

    try:
        export_fmt = ExportFormat(fmt)
    except ValueError:
        output.error(t("config.invalid", detail=f"unknown export format: {fmt}"))
        raise typer.Exit(code=1)

    config_path = config if config is not None else Path("pith.config.json")
    cfg = _load_config(config_path)

    resolved_output = (
    output_path if output_path is not None
    else Path(f"pith-export.{export_fmt.value}"))
    export_wiki(cfg, export_fmt, resolved_output)


@app.command()
def version() -> None:
    """Print the PITH version."""
    try:
        ver = importlib.metadata.version("pithhq")
    except importlib.metadata.PackageNotFoundError:
        ver = "0.1.0"
    output.info(f"PITH {ver}")
