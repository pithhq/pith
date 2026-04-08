"""Offline license validation for PITH.

License files are written by ``pith activate`` and stored at
~/.pithhq/license.json.  Validation is offline after first
activation — no network calls required.

# TODO: replace HMAC with asymmetric signing before launch.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import platform
import socket
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import httpx

from pith.i18n import t

# TODO: replace with asymmetric signing before launch
_LICENSE_SALT = b"pithhq-license-salt-v1"
_KEY_PREFIX = "pithhq_"


@dataclass
class LicenseInfo:
    """Result of license activation or validation."""

    key: str
    machine_id: str
    tier: str
    activated_at: str
    valid: bool


def get_license_path() -> Path:
    """Return the path to the license file."""
    return Path.home() / ".pithhq" / "license.json"


def _generate_machine_id() -> str:
    """Generate a SHA-256 fingerprint of the current machine, truncated to 32 chars."""
    raw = f"{socket.gethostname()}{platform.platform()}{platform.processor()}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


def _compute_signature(key: str, machine_id: str, tier: str, activated_at: str) -> str:
    """Compute HMAC-SHA256 signature over the license payload."""
    message = f"{key}:{machine_id}:{tier}:{activated_at}"
    return hmac.new(_LICENSE_SALT, message.encode(), hashlib.sha256).hexdigest()


def activate(key: str) -> LicenseInfo:
    """Activate a license key on this machine.

    Validates key format, contacts Lemon Squeezy, writes
    ~/.pithhq/license.json, and returns a LicenseInfo.

    Args:
        key: A license key starting with ``pithhq_``.

    Returns:
        LicenseInfo with valid=True on success.

    Raises:
        ValueError: If the key format is invalid.
        httpx.HTTPError: If the remote validation call fails.
    """
    if not key.startswith(_KEY_PREFIX):
        raise ValueError(t("license.invalid_key"))

    machine_id = _generate_machine_id()
    activated_at = datetime.now(timezone.utc).isoformat()

    # TODO: add Lemon Squeezy API key header (Authorization: Bearer ...)
    response = httpx.post(
        "https://api.lemonsqueezy.com/v1/licenses/validate",
        json={"license_key": key},
        timeout=30,
    )
    response.raise_for_status()

    # Default tier — real response will include tier info.
    tier = "personal"
    body: dict[str, Any] = response.json()
    if "tier" in body:
        tier = body["tier"]

    signature = _compute_signature(key, machine_id, tier, activated_at)

    license_data = {
        "key": key,
        "machine_id": machine_id,
        "tier": tier,
        "activated_at": activated_at,
        "signature": signature,
    }

    license_path = get_license_path()
    license_path.parent.mkdir(parents=True, exist_ok=True)
    license_path.write_text(json.dumps(license_data, indent=2), encoding="utf-8")

    return LicenseInfo(
        key=key,
        machine_id=machine_id,
        tier=tier,
        activated_at=activated_at,
        valid=True,
    )


def validate_license() -> LicenseInfo:
    """Validate the locally stored license file.

    Reads ~/.pithhq/license.json, checks that the machine ID
    matches and the HMAC signature is correct.

    Never raises — returns LicenseInfo with valid=False on any error.
    """
    _invalid = LicenseInfo(key="", machine_id="", tier="", activated_at="", valid=False)

    try:
        license_path = get_license_path()
        data: dict[str, str] = json.loads(
            license_path.read_text(encoding="utf-8"),
        )

        key = data["key"]
        machine_id = data["machine_id"]
        tier = data["tier"]
        activated_at = data["activated_at"]
        signature = data["signature"]
    except Exception:  # noqa: BLE001
        return _invalid

    # Machine mismatch.
    if machine_id != _generate_machine_id():
        return _invalid

    # Signature verification.
    expected = _compute_signature(key, machine_id, tier, activated_at)
    if not hmac.compare_digest(signature, expected):
        return _invalid

    return LicenseInfo(
        key=key,
        machine_id=machine_id,
        tier=tier,
        activated_at=activated_at,
        valid=True,
    )
