"""Tests for init wizard config overwrite guard (S12)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from pith.init import _write_config


def _minimal_config() -> MagicMock:
    """Return a mock PithConfig that serialises to valid JSON."""
    config = MagicMock()
    config.model_dump.return_value = {"version": "1.0"}
    return config


def test_write_config_creates_new_without_prompt(
    tmp_path, monkeypatch,
):
    """No existing config -> no confirmation prompt."""
    monkeypatch.chdir(tmp_path)
    config = _minimal_config()

    with patch("pith.init.typer.confirm") as mock_confirm:
        _write_config(config)

    mock_confirm.assert_not_called()
    assert (tmp_path / "pith.config.json").exists()


def test_write_config_prompts_on_existing(tmp_path, monkeypatch):
    """Existing config triggers typer.confirm; overwrite if accepted."""
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "pith.config.json"
    existing.write_text('{"old": true}', encoding="utf-8")

    config = _minimal_config()

    with patch("pith.init.typer.confirm", return_value=True):
        _write_config(config)

    data = json.loads(existing.read_text(encoding="utf-8"))
    assert "old" not in data
    assert data == {"version": "1.0"}


def test_write_config_aborts_when_declined(tmp_path, monkeypatch):
    """Existing config preserved when user declines overwrite."""
    monkeypatch.chdir(tmp_path)
    existing = tmp_path / "pith.config.json"
    existing.write_text('{"old": true}', encoding="utf-8")

    config = _minimal_config()

    with patch("pith.init.typer.confirm", return_value=False):
        _write_config(config)

    data = json.loads(existing.read_text(encoding="utf-8"))
    assert data == {"old": True}
