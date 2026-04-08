---
description: Privacy enforcement rules for PITH. Non-negotiable constraints that define the product's identity.
globs: "**/*.py,**/*.rs,**/*.json"
---

# Privacy Rules — PITH

These are non-negotiable. They are the reason privacy-first clients pay a premium.

## Zero Telemetry
- No analytics calls
- No error reporting to external services
- No usage tracking of any kind
- No logging that writes to network endpoints

If you see any network call that isn't:
1. Claude API for ingest
2. Ollama local endpoint for query
3. `api.pithhq.com/version` for update check (no user identifier)
4. Lemon Squeezy for license activation (one-time only)

Flag it. It doesn't belong.

## Secrets in Environment Variables Only
```python
# ❌ NEVER
config = {"api_key": "sk-ant-..."}

# ✅ ALWAYS
import os
api_key = os.environ.get("ANTHROPIC_API_KEY")
if not api_key:
    raise PithConfigError(
        "ANTHROPIC_API_KEY not set. "
        "Add it to your environment variables."
    )
```

Never write API keys to any file. Not config.json. Not a .env file PITH creates. Environment variables only.

## Update Check — No User Identifier
```python
# ✅ Correct update check
async def check_for_update(current_version: str) -> str | None:
    async with httpx.AsyncClient() as client:
        # No user ID, no machine ID, no license key in request
        response = await client.get(
            "https://api.pithhq.com/version",
            timeout=3.0
        )
    data = response.json()
    latest = data["version"]
    return latest if latest != current_version else None
```

## License Validation — Offline After First Activation
The license check after initial activation must work without network access. Machine fingerprint is hashed locally, never sent after activation.

```python
def validate_license_offline(license_key: str, stored_hash: str) -> bool:
    machine_id = generate_machine_fingerprint()  # local only
    expected = hash_license_and_machine(license_key, machine_id)
    return hmac.compare_digest(expected, stored_hash)
```

## Data Handling Levels (writing-agency schema)
When implementing features that touch client data, respect the privacy_level field:

- `privacy_level: 1` → NO cloud API calls with content. Local model only. Hard block.
- `privacy_level: 2` → Cloud API allowed for processing. No external storage.
- `privacy_level: 3` → Full cloud allowed. User has explicitly consented.

The privacy_level enforcement is at the engine level, not the application level. It cannot be overridden by user action.
