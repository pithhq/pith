# Sprint 0 — Hardening

**Duration:** 1 week
**Goal:** Resolve all P0 and P1 audit findings. Establish CI pipeline. The engine becomes trustworthy.

This is not a foundation sprint (the foundation exists). This is the sprint where we fix everything that would embarrass us if a security researcher looked at the code on launch day.

## Exit Criteria

- [ ] License system uses Ed25519 asymmetric signing (audit S1)
- [ ] Machine fingerprint includes hardware-unique identifiers (audit S2)
- [ ] License file and scheduler files written with `0o600` permissions (audit S4, S5)
- [ ] Schema name validated against path traversal (audit S6)
- [ ] Ingest output path validated against vault boundary (audit S7)
- [ ] Ollama base_url restricted to localhost/private ranges by default (audit S8)
- [ ] CI pipeline running: ruff + mypy + pytest on every push
- [ ] All 66 existing tests still passing
- [ ] New tests for every security fix

## Tasks

### License System Overhaul (S1 + S2) — 3 days
1. **Generate Ed25519 keypair** — private key stays on server (never in repo), public key embedded in `pith/license/`
2. **Rewrite `_compute_signature`** — replace HMAC with Ed25519 verify using the public key
3. **Rewrite `activate()`** — server returns a signed license blob; client stores and verifies it
4. **Harden `_generate_machine_id()`** — add `uuid.getnode()` (MAC), `/etc/machine-id` (Linux), `IOPlatformUUID` (macOS), `MachineGuid` registry (Windows)
5. **Update tests** — test signature verification, test machine ID stability, test rejection of forged licenses
6. **Remove `_LICENSE_SALT`** — the hardcoded salt must not exist in any form

### File Permission Fixes (S4 + S5) — 0.5 day
1. Add `license_path.chmod(0o600)` after writing license file
2. Add `license_path.parent.chmod(0o700)` when creating `~/.pithhq/`
3. Add `.chmod(0o600)` after writing systemd units, launchd plist, Task Scheduler XML
4. Tests: verify file permissions on Linux (skip on Windows if needed)

### Path Traversal Fixes (S6 + S7) — 0.5 day
1. `load_schema()` — resolve and validate `schema_dir.is_relative_to(schemas_root)`
2. `_page_path_for()` — resolve and validate `page_path.is_relative_to(vault_path)`
3. Tests: confirm `../` in schema name raises `SchemaValidationError`
4. Tests: confirm adversarial filenames don't escape vault

### SSRF Protection (S8) — 0.5 day
1. Add validator to `OllamaProvider.base_url` that rejects non-private IPs by default
2. Add `allow_remote_ollama: bool = False` config flag to override
3. Test: non-local URL rejected unless flag set

### CI Pipeline — 0.5 day
1. Create `.github/workflows/ci.yml` — runs on push and PR to `main`
2. Steps: checkout, setup Python 3.12, install deps, `ruff check`, `mypy pith/`, `pytest`
3. Add badge to README

## Risks

- Ed25519 signing changes the license file format — existing test licenses will break (acceptable, no production licenses exist yet)
- Machine ID on macOS requires `ioreg` subprocess call — needs error handling for sandboxed environments
- File permissions are not enforceable on Windows (NTFS ACLs are different) — document limitation

## Agents

- **Security Lead** — reviews all crypto and permission changes
- **QA Lead** — verifies test coverage for every security fix
- **Tech Lead** — reviews CI pipeline, approves merge
