"""Setup wizard — interactive ``pith init`` configuration."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from pith import output
from pith.config import (
    ModelsConfig,
    PithConfig,
    SyncConfig,
    VaultConfig,
)
from pith.i18n import t
from pith.init.scheduler import generate


def _prompt_vault_path() -> Path:
    """Prompt for vault path, creating the directory if needed."""
    raw = typer.prompt(t("init.prompt_vault_path"), default="./vault")
    vault = Path(raw).resolve()
    if not vault.exists():
        create = typer.confirm(t("init.confirm_create_vault", path=vault), default=True)
        if create:
            vault.mkdir(parents=True, exist_ok=True)
            output.success(t("init.vault_created", path=vault))
        else:
            output.error(t("init.vault_not_created"))
            raise typer.Exit(code=1)
    return vault


def _prompt_schema() -> str | None:
    """Prompt for optional schema name."""
    raw = typer.prompt(t("init.prompt_schema"), default="").strip()
    return raw or None


def _prompt_language() -> str:
    """Prompt for language code."""
    return typer.prompt(t("init.prompt_language"), default="en").strip()


def _prompt_mixed_script() -> bool:
    """Prompt for mixed script toggle."""
    return typer.confirm(t("init.prompt_mixed_script"), default=False)


def _prompt_model(label: str) -> str:
    """Prompt for a model name."""
    return typer.prompt(
        t("init.prompt_model", label=label),
        default="claude-sonnet-4-6",
    ).strip()


def _prompt_git_remote() -> str | None:
    """Prompt for optional git remote URL."""
    raw = typer.prompt(t("init.prompt_git_remote"), default="").strip()
    return raw or None


def _prompt_sync_interval() -> int:
    """Prompt for sync interval in minutes."""
    return int(
        typer.prompt(t("init.prompt_sync_interval"), default="30").strip()
    )


def _build_config(
    *,
    vault_path: Path,
    schema_name: str | None,
    language: str,
    mixed_script: bool,
    ingest_model: str,
    query_model: str,
    lint_model: str,
    git_remote: str | None,
    sync_interval: int,
) -> PithConfig:
    """Assemble a PithConfig from wizard answers."""
    return PithConfig(
        vault=VaultConfig(
            path=vault_path,
            schema=schema_name,
            language=language,
            mixed_script=mixed_script,
        ),
        models=ModelsConfig(
            ingest=ingest_model,
            query=query_model,
            lint=lint_model,
        ),
        sync=SyncConfig(
            remote=git_remote,
            interval_minutes=sync_interval,
        ),
    )


def _write_config(config: PithConfig) -> None:
    """Write pith.config.json and pith.config.example.json to cwd."""
    config_path = Path("pith.config.json")
    if config_path.exists():
        overwrite = typer.confirm(
            t("init.confirm_overwrite", path=config_path),
            default=False,
        )
        if not overwrite:
            output.warning(t("init.overwrite_aborted"))
            return

    data = config.model_dump(mode="json", by_alias=True, exclude_none=True)

    config_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    output.success(t("init.config_written", path=config_path))

    # Example config
    example_path = Path("pith.config.example.json")
    example_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    output.success(t("init.example_written", path=example_path))


def run_wizard() -> PithConfig:
    """Run the interactive setup wizard.

    Collects configuration via typer.prompt(), writes config files,
    and generates OS scheduler files for git sync.

    Returns:
        The validated PithConfig.
    """
    output.info(t("init.welcome"))

    vault_path = _prompt_vault_path()
    schema_name = _prompt_schema()
    language = _prompt_language()
    mixed_script = _prompt_mixed_script()
    ingest_model = _prompt_model("ingest")
    query_model = _prompt_model("query")
    lint_model = _prompt_model("lint")
    git_remote = _prompt_git_remote()
    sync_interval = _prompt_sync_interval()

    config = _build_config(
        vault_path=vault_path,
        schema_name=schema_name,
        language=language,
        mixed_script=mixed_script,
        ingest_model=ingest_model,
        query_model=query_model,
        lint_model=lint_model,
        git_remote=git_remote,
        sync_interval=sync_interval,
    )

    _write_config(config)
    generate(config)
    output.success(t("init.complete"))

    return config
