"""Tests for scheduler file permissions (S4)."""

from __future__ import annotations

from unittest.mock import patch

import pytest

from pith.init.scheduler import generate


@pytest.fixture()
def mock_config():
    """Minimal config mock with sync.interval_minutes."""
    from unittest.mock import MagicMock

    config = MagicMock()
    config.sync.interval_minutes = 30
    return config


def test_systemd_files_permissions(tmp_path, mock_config):
    """systemd service and timer must be written with 0o600."""
    unit_dir = tmp_path / ".config" / "systemd" / "user"

    with (
        patch("pith.init.scheduler.platform.system", return_value="Linux"),
        patch("pith.init.scheduler.Path.home", return_value=tmp_path),
        patch("pith.init.scheduler._pith_executable", return_value="/usr/bin/pith"),
    ):
        generate(mock_config)

    service = unit_dir / "pith-sync.service"
    timer = unit_dir / "pith-sync.timer"

    assert service.exists()
    assert timer.exists()

    service_mode = service.stat().st_mode & 0o777
    timer_mode = timer.stat().st_mode & 0o777
    assert service_mode == 0o600, f"service: {oct(service_mode)}"
    assert timer_mode == 0o600, f"timer: {oct(timer_mode)}"


def test_launchd_plist_permissions(tmp_path, mock_config):
    """launchd plist must be written with 0o600."""
    agents_dir = tmp_path / "Library" / "LaunchAgents"

    with (
        patch("pith.init.scheduler.platform.system", return_value="Darwin"),
        patch("pith.init.scheduler.Path.home", return_value=tmp_path),
        patch("pith.init.scheduler._pith_executable", return_value="/usr/bin/pith"),
    ):
        generate(mock_config)

    plist = agents_dir / "com.pithhq.sync.plist"
    assert plist.exists()

    plist_mode = plist.stat().st_mode & 0o777
    assert plist_mode == 0o600, f"plist: {oct(plist_mode)}"
