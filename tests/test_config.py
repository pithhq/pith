"""Tests for PITH config loading and validation."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest
from pydantic import ValidationError

from pith.config import PithConfig, load_config

EXAMPLE_CONFIG = Path(__file__).resolve().parent.parent / "pith.config.example.json"


@pytest.fixture()
def example_data() -> dict[str, Any]:
    """Return the example config as a dict."""
    return json.loads(EXAMPLE_CONFIG.read_text(encoding="utf-8"))


@pytest.fixture()
def config_file(tmp_path: Path, example_data: dict[str, Any]) -> Path:
    """Write example config to a temp file and return its path."""
    p = tmp_path / "pith.config.json"
    p.write_text(json.dumps(example_data), encoding="utf-8")
    return p


# --- Valid config loads correctly ---


class TestValidConfig:
    def test_load_example_config(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.models.ingest == "claude-sonnet-4-6"
        assert cfg.models.query == "claude-sonnet-4-6"
        assert cfg.models.lint == "claude-sonnet-4-6"

    def test_vault_defaults(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.vault.path is None
        assert cfg.vault.schema_ is None
        assert cfg.vault.mixed_script is False

    def test_ingest_settings(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.ingest.chunk_size_tokens == 2048
        assert cfg.ingest.overlap_tokens == 128
        assert len(cfg.ingest.formats) == 7

    def test_sync_settings(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.sync.interval_minutes == 30
        assert cfg.sync.active_hours.start == "08:00"
        assert cfg.sync.active_hours.end == "20:00"

    def test_lint_settings(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.lint.schedule.value == "weekly"
        assert cfg.lint.day.value == "monday"
        assert cfg.lint.checks.orphans is True
        assert cfg.lint.checks.contradictions is True
        assert cfg.lint.checks.stale_references is True

    def test_privacy_defaults(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.privacy.telemetry is False
        assert cfg.privacy.update_check is True

    def test_ui_settings(self, config_file: Path) -> None:
        cfg = load_config(config_file)
        assert cfg.ui.obsidian_vault_path is None
        assert cfg.ui.openwebui_port == 3000


# --- Privacy enforcement ---


class TestPrivacy:
    def test_telemetry_true_raises(self, example_data: dict[str, Any]) -> None:
        example_data["privacy"]["telemetry"] = True
        with pytest.raises(ValidationError) as exc_info:
            PithConfig.model_validate(example_data)
        assert "telemetry" in str(exc_info.value).lower()


# --- Edge cases ---


class TestEdgeCases:
    def test_negative_chunk_size_raises(
        self, example_data: dict[str, Any]
    ) -> None:
        example_data["ingest"]["chunk_size_tokens"] = -1
        with pytest.raises(ValidationError, match="chunk_size_tokens"):
            PithConfig.model_validate(example_data)

    def test_invalid_format_raises(
        self, example_data: dict[str, Any]
    ) -> None:
        example_data["ingest"]["formats"] = ["pdf", "exe"]
        with pytest.raises(ValidationError):
            PithConfig.model_validate(example_data)

    def test_config_file_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.json")

    def test_models_default_to_claude(self) -> None:
        cfg = PithConfig.model_validate({})
        assert cfg.models.ingest == "claude-sonnet-4-6"
        assert cfg.models.query == "claude-sonnet-4-6"
        assert cfg.models.lint == "claude-sonnet-4-6"
