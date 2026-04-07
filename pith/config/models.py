"""Pydantic models for pith.config.json validation."""

from __future__ import annotations

import json
import os
from enum import Enum
from pathlib import Path
from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator, model_validator


class VaultConfig(BaseModel):
    """Vault location, schema, and language settings."""

    path: Optional[Path] = None
    schema_: Optional[str] = Field(None, alias="schema")
    schema_version: Optional[str] = None
    language: Optional[str] = None
    mixed_script: bool = False


class ModelProvider(str, Enum):
    """Supported model providers."""

    anthropic = "anthropic"
    ollama = "ollama"


class ModelRef(BaseModel):
    """Provider + model pair for a single operation."""

    provider: ModelProvider
    model: str


class ModelsConfig(BaseModel):
    """Model assignments per operation."""

    ingest: ModelRef
    query: ModelRef
    lint: ModelRef


class AnthropicProvider(BaseModel):
    """Anthropic provider — stores only the env var name, never the key."""

    api_key_env: str = "ANTHROPIC_API_KEY"

    def resolve_api_key(self) -> str:
        """Read the API key from the environment.

        Raises:
            ValueError: If the env var is unset or empty.
        """
        value = os.environ.get(self.api_key_env, "")
        if not value:
            msg = (
                f"Environment variable {self.api_key_env!r} is not set. "
                f"API keys must be provided via environment variables, "
                f"never in the config file."
            )
            raise ValueError(msg)
        return value


class OllamaProvider(BaseModel):
    """Ollama provider connection settings."""

    base_url: str = "http://localhost:11434"

    @field_validator("base_url")
    @classmethod
    def _validate_url(cls, v: str) -> str:
        HttpUrl(v)
        return v


class ProvidersConfig(BaseModel):
    """Provider connection details."""

    anthropic: AnthropicProvider = AnthropicProvider()
    ollama: OllamaProvider = OllamaProvider()


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


class ActiveHours(BaseModel):
    """Time window for sync operations."""

    start: str = "08:00"
    end: str = "20:00"


class SyncConfig(BaseModel):
    """Git sync settings."""

    remote: Optional[str] = None
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


class LicenseConfig(BaseModel):
    """License data — written by ``pith activate``, never by users."""

    key: Optional[str] = None
    machine_id: Optional[str] = None
    tier: Optional[str] = None
    activated_at: Optional[str] = None


class UIConfig(BaseModel):
    """UI integration settings."""

    obsidian_vault_path: Optional[Path] = None
    openwebui_port: int = 3000


class PithConfig(BaseModel):
    """Root configuration model for pith.config.json."""

    vault: VaultConfig = VaultConfig()
    models: ModelsConfig
    providers: ProvidersConfig = ProvidersConfig()
    ingest: IngestConfig = IngestConfig()
    sync: SyncConfig = SyncConfig()
    lint: LintConfig = LintConfig()
    privacy: PrivacyConfig = PrivacyConfig()
    license: LicenseConfig = Field(default_factory=LicenseConfig, alias="license")
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
