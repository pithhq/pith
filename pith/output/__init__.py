"""Terminal output — all CLI printing routes through this module.

Colours follow the PITH spec:
  Copper  #B07858  — warnings, flagged items
  Sage    #5C8A5A  — success, clean states
  Red                — errors only
  Default            — progress, informational

No emoji. No exclamation marks. No hardcoded strings.
"""

from __future__ import annotations

import sys

# ANSI escape codes — copper, sage, red, reset.
# Disabled automatically when stdout is not a TTY.
_COPPER = "\033[38;2;176;120;88m"
_SAGE   = "\033[38;2;92;138;90m"
_RED    = "\033[38;2;200;60;60m"
_RESET  = "\033[0m"


def _supports_color() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _colorize(text: str, code: str) -> str:
    if _supports_color():
        return f"{code}{text}{_RESET}"
    return text


def info(message: str) -> None:
    """Print an informational or progress message — no color."""
    print(message)


def success(message: str) -> None:
    """Print a success message in sage."""
    print(_colorize(message, _SAGE))


def warning(message: str) -> None:
    """Print a warning in copper."""
    print(_colorize(message, _COPPER))


def error(message: str) -> None:
    """Print an error in red and write to stderr."""
    print(_colorize(message, _RED), file=sys.stderr)


def summary(*, updated: int, created: int, conflicts: int) -> None:
    """Print the standard ingest/sync summary line.

    Format: "N pages updated · N created · N conflicts"
    Colour: sage if conflicts == 0, copper if conflicts > 0.
    """
    line = f"{updated} pages updated · {created} created · {conflicts} conflicts"
    if conflicts > 0:
        warning(line)
    else:
        success(line)