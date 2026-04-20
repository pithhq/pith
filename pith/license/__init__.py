"""License stub — always valid for personal use."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class LicenseInfo:
    """Result of license validation."""

    key: str
    machine_id: str
    tier: str
    activated_at: str
    valid: bool


def activate(key: str) -> LicenseInfo:
    """Stub — always returns a valid personal license."""
    return LicenseInfo(
        key=key,
        machine_id="personal",
        tier="personal",
        activated_at="",
        valid=True,
    )


def validate_license() -> LicenseInfo:
    """Stub — always returns a valid personal license."""
    return LicenseInfo(
        key="personal",
        machine_id="personal",
        tier="personal",
        activated_at="",
        valid=True,
    )
