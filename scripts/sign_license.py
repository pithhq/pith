"""Offline license signing for PITH.

Signs a license.json payload with the Ed25519 private key.
For developer use when provisioning early customers.

Usage:
    python scripts/sign_license.py <license.json> [--key ~/.pithhq-signing/private.pem]

The script reads the license payload, signs it, and writes the
signature back into the file.
"""

from __future__ import annotations

import argparse
import base64
import json
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def _load_private_key(key_path: Path) -> Ed25519PrivateKey:
    """Load an Ed25519 private key from a PEM file."""
    raw = key_path.read_bytes()
    key = serialization.load_pem_private_key(raw, password=None)
    if not isinstance(key, Ed25519PrivateKey):
        raise TypeError(f"expected Ed25519 private key, got {type(key).__name__}")
    return key


def sign_license(license_path: Path, key_path: Path) -> None:
    """Sign a license.json file in place."""
    data = json.loads(license_path.read_text(encoding="utf-8"))

    required = ("key", "machine_id", "tier", "activated_at")
    for field in required:
        if field not in data:
            raise KeyError(f"missing required field: {field}")

    message = (
        f"{data['key']}:{data['machine_id']}"
        f":{data['tier']}:{data['activated_at']}"
    )

    private_key = _load_private_key(key_path)
    signature = private_key.sign(message.encode())
    data["signature"] = base64.b64encode(signature).decode()
    data["version"] = 2

    license_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print(f"signed: {license_path}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Sign a PITH license file.")
    parser.add_argument("license", type=Path, help="Path to license.json")
    parser.add_argument(
        "--key",
        type=Path,
        default=Path.home() / ".pithhq-signing" / "private.pem",
        help="Path to Ed25519 private key PEM",
    )
    args = parser.parse_args()
    sign_license(args.license, args.key)


if __name__ == "__main__":
    main()
