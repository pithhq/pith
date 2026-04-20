"""Pydantic models for pith.config.json validation."""

from __future__ import annotations

import json
from enum import Enum
from pathlib import Path

from pydantic import BaseModel, Field, field_validator, model_validator


class VaultConfig(BaseModel):
    """Vault location, schema, and language settings."""

    path: Path | None = None
    schema_: str | None = Field(None, alias="schema")
    schema_version: str | None = None
    language: str | None = None
    mixed_script: bool = False


class ModelsConfig(BaseModel):
    """Model assignments per operation — all routed through ``claude -p``."""

    ingest: str = "claude-sonnet-4-6"
    query: str = "claude-sonnet-4-6"
    lint: str = "claude-sonnet-4-6"


class IngestFormat(str, Enum):
    """Supported ingest file formats."""

    pdf = "pdf"
    docx = "docx"
    txt = "txt"
    md = "md"
    xlsx = "xlsx"
    csv = "csv"
    pptx = "pptx"


class IngestConfig(BaseModel):
    """Ingest pipeline settings."""

    chunk_size_tokens: int = 2048
    overlap_tokens: int = 128
    max_concurrency: int = 5
    formats: list[IngestFormat] = Field(
        default_factory=lambda: list(IngestFormat),
    )

    @field_validator("chunk_size_tokens")
    @classmethod
    def _chunk_size_positive(cls, v: int) -> int:
        if v <= 0:
            msg = "chunk_size_tokens must be positive"
            raise ValueError(msg)
        return v

    @field_validator("overlap_tokens")
    @classmethod
    def _overlap_non_negative(cls, v: int) -> int:
        if v < 0:
            msg = "overlap_tokens must be non-negative"
            raise ValueError(msg)
        return v

    @field_validator("max_concurrency")
    @classmethod
    def _max_concurrency_positive(cls, v: int) -> int:
        if v < 1:
            msg = "max_concurrency must be at least 1"
            raise ValueError(msg)
        return v


class ActiveHours(BaseModel):
    """Time window for sync operations."""

    start: str = "08:00"
    end: str = "20:00"


class SyncConfig(BaseModel):
    """Git sync settings."""

    remote: str | None = None
    interval_minutes: int = 30
    active_hours: ActiveHours = ActiveHours()


class LintChecks(BaseModel):
    """Toggles for individual lint checks."""

    orphans: bool = True
    contradictions: bool = True
    stale_references: bool = True


class LintSchedule(str, Enum):
    """Supported lint schedule frequencies."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"


class LintDay(str, Enum):
    """Days of the week for scheduling."""

    monday = "monday"
    tuesday = "tuesday"
    wednesday = "wednesday"
    thursday = "thursday"
    friday = "friday"
    saturday = "saturday"
    sunday = "sunday"


class LintConfig(BaseModel):
    """Lint scheduling and check toggles."""

    schedule: LintSchedule = LintSchedule.weekly
    day: LintDay = LintDay.monday
    time: str = "09:00"
    checks: LintChecks = LintChecks()


class PrivacyConfig(BaseModel):
    """Privacy settings — telemetry is always off."""

    telemetry: bool = False
    update_check: bool = True

    @model_validator(mode="after")
    def _telemetry_must_be_false(self) -> PrivacyConfig:
        if self.telemetry:
            msg = "Telemetry must be disabled. PITH never collects telemetry."
            raise ValueError(msg)
        return self


class UIConfig(BaseModel):
    """UI integration settings."""

    obsidian_vault_path: Path | None = None
    openwebui_port: int = 3000


class PithConfig(BaseModel):
    """Root configuration model for pith.config.json."""

    vault: VaultConfig = VaultConfig()  # type: ignore[call-arg]
    models: ModelsConfig = ModelsConfig()
    ingest: IngestConfig = IngestConfig()
    sync: SyncConfig = SyncConfig()
    lint: LintConfig = LintConfig()
    privacy: PrivacyConfig = PrivacyConfig()
    ui: UIConfig = UIConfig()


def load_config(path: Path) -> PithConfig:
    """Load and validate a PITH config file.

    Args:
        path: Path to pith.config.json.

    Returns:
        Validated PithConfig instance.

    Raises:
        FileNotFoundError: If the config file does not exist.
        pydantic.ValidationError: If the config file is invalid.
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    return PithConfig.model_validate(data)
