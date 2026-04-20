# Sprint 4 — Pre-Launch

**Duration:** 1 week
**Goal:** Everything needed to accept money and distribute the product. License activation works. Packaging complete. Legal in place.

## Exit Criteria

- [ ] Lemon Squeezy integration complete — activation flow works end-to-end (audit S3)
- [ ] License tiers enforced: Personal (1 machine), Team (5), Enterprise (unlimited)
- [ ] Update check endpoint implemented (`api.pithhq.com/version`)
- [ ] PyInstaller binaries signed (macOS: Sectigo, Windows: code signing)
- [ ] pithhq.com has download page with platform-specific binaries
- [ ] Apache 2.0 LICENSE file in repo root
- [ ] Privacy policy at pithhq.com/privacy
- [ ] README.md has install instructions, quick start, and schema pack docs
- [ ] `pith.config.example.json` is accurate and well-commented
- [ ] Re-run `/audit` — all P0 and P1 findings resolved

## Tasks

### Lemon Squeezy Integration (S3) — 2 days
1. **Add Authorization header to `activate()`** — `Bearer {LEMONSQUEEZY_API_KEY}`
2. **Parse Lemon Squeezy response** — extract tier, license ID, customer email
3. **Implement tier enforcement** — check machine count against tier limit
4. **Handle API errors gracefully** — network failure, invalid key, expired license
5. **Build-time embedding** — embed the Lemon Squeezy store ID in the binary (not the API key — that's server-side)
6. **Tests** — mock Lemon Squeezy API, verify all response scenarios

### Update Check — 1 day
1. **Implement `check_for_update()`** — GET `https://api.pithhq.com/version`, no user identifier
2. **Call on `pith version`** — display "Update available: X.Y.Z" if newer version exists
3. **Respect `privacy.update_check: false`** — skip entirely if disabled
4. **Timeout: 3 seconds** — never block the CLI for a slow network
5. **Tests** — verify no user identifier sent, verify opt-out works

### Code Signing — 1 day
1. **macOS** — sign with Sectigo certificate, notarize with `xcrun notarytool`
2. **Windows** — sign `.exe` with code signing certificate
3. **Linux** — AppImage doesn't require signing, but add GPG signature file
4. **Add signing to CI/CD** — automated signing in release pipeline

### Distribution Setup — 1 day
1. **Create GitHub Releases workflow** — tag-triggered, builds all platforms, uploads signed binaries
2. **Set up pithhq.com/download** — platform detection, download links
3. **Schema pack distribution** — `pip install pith-schemas-law-firm-sr` or private git submodule instruction
4. **Write install docs** — per-platform instructions in README

### Legal — 0.5 day
1. **Verify Apache 2.0 LICENSE** in repo root
2. **Draft privacy policy** — matches the zero-telemetry commitment in code
3. **Draft terms of service** — covers license terms, data handling, no warranty
4. **Dependency license audit** — verify all dependencies are compatible with Apache 2.0

### Final Audit — 0.5 day
1. **Re-run `/audit`** — verify all P0 and P1 findings from 2026-04-08 are resolved
2. **Document any accepted risks** — P2 findings that ship as-is with justification
3. **Security review of the release binary** — verify no secrets embedded

## Risks

- Code signing certificates take days to provision — start the application process early
- Lemon Squeezy API has quirks with license validation — test against their sandbox
- macOS notarization can be slow and fail intermittently — build in retry logic

## Agents

- **Security Lead** — reviews final audit, code signing setup
- **Launch Lead** — owns distribution, legal, pithhq.com updates
- **DevOps Lead** — owns release pipeline, signing automation
