# Sprint 5 — Launch

**Duration:** 1 week
**Goal:** PITH is live. First paying customers. Monitoring active. Feedback loop established.

## Exit Criteria

- [ ] Signed binaries published on GitHub Releases (Linux, macOS, Windows)
- [ ] pithhq.com/download live with working download links
- [ ] Lemon Squeezy store live — purchase and activation flow works
- [ ] First 10 real users have completed: download -> init -> ingest -> query
- [ ] Error monitoring in place (crash reports via opt-in, not telemetry)
- [ ] Feedback collection mechanism live (GitHub Issues template, hello@pithhq.com)
- [ ] `law-firm-sr` schema pack purchasable and installable
- [ ] Rollback procedure documented and tested

## Tasks

### Release — 1 day
1. **Tag v1.0.0** — create annotated git tag
2. **Trigger release pipeline** — CI builds, signs, and uploads binaries
3. **Verify downloads** — download each binary on a clean machine, run `pith version`
4. **Publish release notes** — changelog from Phase 1-4 + this sprint roadmap's fixes
5. **Enable Lemon Squeezy store** — take it out of test mode

### Monitoring Setup — 1 day
1. **Uptime check on `api.pithhq.com/version`** — simple ping monitor
2. **Lemon Squeezy webhook** — receive activation events, track conversion
3. **GitHub Issues template** — bug report template with version, OS, config (no secrets)
4. **Support email** — hello@pithhq.com with auto-responder pointing to docs
5. **Rollback procedure** — document how to revert to previous binary version

### Initial Acquisition — 3 days
1. **Announce on relevant channels** — legal tech forums, Serbian legal community, knowledge management communities
2. **Write launch blog post** — what PITH is, why it exists, privacy-first positioning
3. **Direct outreach** — contact 5-10 law firms in the target vertical
4. **Offer early-adopter pricing** — time-limited discount via Lemon Squeezy coupon
5. **Collect feedback** — structured form for first users: what worked, what didn't, what's missing

### Post-Launch Monitoring — ongoing
1. **Monitor GitHub Issues daily** — respond within 24 hours
2. **Track activation success rate** — Lemon Squeezy dashboard
3. **Track common errors** — review any crash reports or support emails
4. **Plan v1.1 backlog** — based on feedback + remaining P2 audit findings

## Risks

- First-user experience may reveal UX issues not caught in testing — be ready to hotfix
- Windows antivirus may flag unsigned or newly-signed binaries — document false positive resolution
- Lemon Squeezy payment flow on first real purchase may have issues — test with real card in sandbox first

## Agents

- **Launch Lead** — owns release execution, acquisition, communications
- **Tech Lead** — owns monitoring setup, hotfix readiness
- **Product Director** — owns feedback collection, v1.1 prioritization

## Definition of Done

A customer in Serbia can:
1. Download PITH for their OS
2. Run `pith init` and configure `law-firm-sr` schema
3. Ingest a legal document in Serbian
4. Query their wiki in Serbian using the local Ollama model
5. Export the wiki to PDF
6. Purchase and activate a license

All of this without any data leaving their machine (except the Claude API call for ingest, which they explicitly configured).
