"""OS scheduler file generation for ``pith sync`` automation."""

from __future__ import annotations

import platform
import shutil
from pathlib import Path

from pith.config import PithConfig
from pith.i18n import t
from pith import output


def _pith_executable() -> str:
    """Return the best-guess path to the pith executable."""
    found = shutil.which("pith")
    return found if found else "pith"


def _write_systemd(config: PithConfig, pith_bin: str) -> None:
    """Write systemd user timer and service units (Linux)."""
    unit_dir = Path.home() / ".config" / "systemd" / "user"
    unit_dir.mkdir(parents=True, exist_ok=True)

    interval = config.sync.interval_minutes

    service_path = unit_dir / "pith-sync.service"
    service_path.write_text(
        "[Unit]\n"
        f"Description={t('init.scheduler_service_desc')}\n"
        "\n"
        "[Service]\n"
        "Type=oneshot\n"
        f"ExecStart={pith_bin} sync\n",
        encoding="utf-8",
    )

    timer_path = unit_dir / "pith-sync.timer"
    timer_path.write_text(
        "[Unit]\n"
        f"Description={t('init.scheduler_timer_desc')}\n"
        "\n"
        "[Timer]\n"
        f"OnCalendar=*:0/{interval}\n"
        "Persistent=true\n"
        "\n"
        "[Install]\n"
        "WantedBy=timers.target\n",
        encoding="utf-8",
    )

    output.info(t("init.scheduler_written", path=timer_path))
    output.info(t("init.scheduler_written", path=service_path))
    output.info(t("init.scheduler_load_systemd"))


def _write_launchd(config: PithConfig, pith_bin: str) -> None:
    """Write a launchd plist (macOS)."""
    agents_dir = Path.home() / "Library" / "LaunchAgents"
    agents_dir.mkdir(parents=True, exist_ok=True)

    interval = config.sync.interval_minutes * 60  # launchd uses seconds
    plist_path = agents_dir / "com.pithhq.sync.plist"

    plist_path.write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"\n'
        '  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
        '<plist version="1.0">\n'
        "<dict>\n"
        "  <key>Label</key>\n"
        "  <string>com.pithhq.sync</string>\n"
        "  <key>ProgramArguments</key>\n"
        "  <array>\n"
        f"    <string>{pith_bin}</string>\n"
        "    <string>sync</string>\n"
        "  </array>\n"
        "  <key>StartInterval</key>\n"
        f"  <integer>{interval}</integer>\n"
        "  <key>RunAtLoad</key>\n"
        "  <false/>\n"
        "</dict>\n"
        "</plist>\n",
        encoding="utf-8",
    )

    output.info(t("init.scheduler_written", path=plist_path))
    output.info(t("init.scheduler_load_launchd"))


def _write_task_scheduler(config: PithConfig, pith_bin: str) -> None:
    """Write a Task Scheduler XML file (Windows)."""
    import os

    appdata = os.environ.get("APPDATA", "")
    if not appdata:
        output.warning(t("init.scheduler_no_appdata"))
        return

    task_dir = Path(appdata) / "pithhq"
    task_dir.mkdir(parents=True, exist_ok=True)

    interval = config.sync.interval_minutes
    xml_path = task_dir / "pith-sync.xml"

    xml_path.write_text(
        '<?xml version="1.0" encoding="UTF-16"?>\n'
        '<Task version="1.2"\n'
        '  xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">\n'
        "  <Triggers>\n"
        "    <TimeTrigger>\n"
        "      <Repetition>\n"
        f"        <Interval>PT{interval}M</Interval>\n"
        "        <StopAtDurationEnd>false</StopAtDurationEnd>\n"
        "      </Repetition>\n"
        "      <StartBoundary>2000-01-01T00:00:00</StartBoundary>\n"
        "      <Enabled>true</Enabled>\n"
        "    </TimeTrigger>\n"
        "  </Triggers>\n"
        "  <Actions>\n"
        "    <Exec>\n"
        f"      <Command>{pith_bin}</Command>\n"
        "      <Arguments>sync</Arguments>\n"
        "    </Exec>\n"
        "  </Actions>\n"
        "  <Settings>\n"
        "    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>\n"
        "    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>\n"
        "  </Settings>\n"
        "</Task>\n",
        encoding="utf-8",
    )

    output.info(t("init.scheduler_written", path=xml_path))
    output.info(t("init.scheduler_load_windows"))


def generate(config: PithConfig) -> None:
    """Detect the OS and write the appropriate scheduler files.

    Args:
        config: Validated PITH configuration (uses sync.interval_minutes).
    """
    pith_bin = _pith_executable()
    system = platform.system()

    if system == "Linux":
        _write_systemd(config, pith_bin)
    elif system == "Darwin":
        _write_launchd(config, pith_bin)
    elif system == "Windows":
        _write_task_scheduler(config, pith_bin)
    else:
        output.warning(t("init.scheduler_unsupported", os=system))
