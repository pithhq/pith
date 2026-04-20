# Sprint 3 — Integration Testing

**Duration:** 1 week
**Goal:** Prove that PITH works end-to-end on all target platforms. Test with real documents and real schema packs. Reach 80% coverage.

## Exit Criteria

- [ ] End-to-end test: `pith init` -> `pith ingest` -> `pith query` -> `pith lint` -> `pith export` (full lifecycle)
- [ ] Cross-platform PyInstaller builds verified: Linux, macOS, Windows
- [ ] `law-firm-sr` schema pack tested with real Serbian legal documents
- [ ] `writing-agency` schema pack tested with sample client briefs
- [ ] Test coverage >= 80% (currently untested: ingest pipeline, query, lint, export, sync, license, init)
- [ ] All builds produce working binaries that run without Python installed
- [ ] CI runs integration tests in addition to unit tests

## Tasks

### End-to-End Test Suite — 2 days
1. **Create `tests/test_e2e.py`** — full lifecycle test using a temp directory as vault
2. **Test with mock Ollama** — httpx mock returning canned responses for query and lint
3. **Test with mock Anthropic** — httpx mock returning canned responses for ingest
4. **Test export formats** — verify PDF, DOCX, CSV output files are valid
5. **Test config validation** — invalid configs produce clear error messages and correct exit codes
6. **Test license flow** — mock Lemon Squeezy, verify activation and offline validation

### Cross-Platform Build Testing — 2 days
1. **Linux build** — `build.sh` produces working binary, test on clean Ubuntu container
2. **macOS build** — `build.sh` produces working `.app`, test on macOS runner
3. **Windows build** — `build.ps1` produces working `.exe`, test on Windows runner
4. **AppImage** — `make-appimage.sh` produces working AppImage
5. **Add build verification to CI** — build step on each platform, smoke test the binary
6. **Verify bundled git** — PyInstaller binary includes git or documents requirement

### Schema Pack Integration — 1.5 days
1. **Test `law-firm-sr`** — load schema, ingest a sample Serbian legal document, verify frontmatter fields, verify `references_legislation` tracking
2. **Test `writing-agency`** — load schema, ingest sample client brief, verify entity types
3. **Test schema seeds** — verify seed pages are valid markdown with correct frontmatter
4. **Test schema validation** — invalid schema.yaml files produce `SchemaValidationError` with helpful messages
5. **Test mixed-script OCR** — Serbian Latin + Cyrillic in same document

### Coverage Gap Analysis — 0.5 day
1. **Run `pytest --cov=pith --cov-report=html`** — identify untested modules
2. **Add unit tests for untested functions** — prioritize business logic over plumbing
3. **Target: 80% line coverage**

## Risks

- PyInstaller builds may fail on CI runners due to missing system dependencies (Tesseract, poppler)
- Schema pack tests require the `pith-schemas` submodule — CI needs access to the private repo
- Real document tests may be flaky due to OCR non-determinism — use known-good fixtures

## Agents

- **QA Lead** — owns test strategy, reviews coverage report
- **DevOps Lead** — owns CI pipeline, cross-platform build matrix
- **Tech Lead** — reviews integration test design
