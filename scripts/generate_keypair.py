"""One-time Ed25519 keypair generation for PITH license signing.

Usage:
    python scripts/generate_keypair.py

Outputs:
    - Private key PEM (save to ~/.pithhq-signing/private.pem — NEVER commit)
    - Public key hex (embed in pith/license/__init__.py)
    - Private key hex (set as PITH_SIGNING_KEY env var for development)
"""

from __future__ import annotations

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


def main() -> None:
    private_key = Ed25519PrivateKey.generate()
    public_key = private_key.public_key()

    # Private key PEM
    private_pem = private_key.private_bytes(
        serialization.Encoding.PEM,
        serialization.PrivateFormat.PKCS8,
        serialization.NoEncryption(),
    )

    # Raw bytes for embedding
    public_bytes = public_key.public_bytes(
        serialization.Encoding.Raw,
        serialization.PublicFormat.Raw,
    )
    private_bytes = private_key.private_bytes(
        serialization.Encoding.Raw,
        serialization.PrivateFormat.Raw,
        serialization.NoEncryption(),
    )

    print("=== PRIVATE KEY PEM (save to ~/.pithhq-signing/private.pem) ===")
    print(private_pem.decode())

    print("=== PUBLIC KEY HEX (embed in pith/license/__init__.py) ===")
    print(public_bytes.hex())
    print()

    print("=== PRIVATE KEY HEX (set as PITH_SIGNING_KEY env var) ===")
    print(private_bytes.hex())


if __name__ == "__main__":
    main()
