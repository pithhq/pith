# Sprint 1 — Performance

**Duration:** 1 week
**Goal:** Ingest pipeline is fast. A 20-chunk document completes in seconds, not minutes. Fix all critical performance findings.

## Exit Criteria

- [ ] httpx client reused across all chunks in a single ingest (audit P1)
- [ ] Chunks processed concurrently with configurable concurrency limit (audit P2)
- [ ] `_ocr_page` double-render bug fixed (audit P3)
- [ ] Config not re-loaded per OCR page (audit P4)
- [ ] pandas removed from CSV export — replaced with stdlib `csv` (audit P9)
- [ ] Lint contradiction check uses async concurrency (audit P8)
- [ ] Ingest of a 20-chunk document completes in <30s (was: ~60s sequential)
- [ ] All tests passing, new performance-relevant tests added

## Tasks

### Ingest Pipeline Refactor (P1 + P2) — 3 days
1. **Refactor `_call_anthropic` and `_call_ollama`** — accept `client: httpx.AsyncClient` parameter instead of creating their own
2. **Create shared client in `ingest_file()`** — single `async with httpx.AsyncClient()` wrapping the entire chunk loop
3. **Add concurrent chunk processing** — `asyncio.Semaphore(5)` + `asyncio.gather()` for parallel API calls
4. **Add `ingest.max_concurrency` config field** — defaults to 5, user-configurable
5. **Preserve chunk ordering** — results must be assembled in original chunk order despite concurrent execution
6. **Update progress reporting** — `info()` calls must be thread-safe and show completion count
7. **Tests** — mock httpx to verify single client creation, verify chunk ordering, verify semaphore bounds

### OCR Bug Fixes (P3 + P4) — 1 day
1. **Remove line 71 in `pdf.py`** — delete the premature `page.to_image().original` call
2. **Move `_set_tessdata_prefix()` below the docstring** in `_ocr_page`
3. **Refactor `_ocr_language()`** — accept `language: str | None` parameter instead of calling `load_config()`
4. **Pass language from `parse_pdf()` caller** — the ingest pipeline already has the config
5. **Tests** — verify OCR page only renders once (mock `to_image`)

### CSV Export Cleanup (P9) — 0.5 day
1. **Replace `import pandas as pd` with `import csv`** in `_export_csv`
2. **Use `csv.DictWriter`** for output
3. **Remove `pandas` from `pyproject.toml` dependencies** (keep in `parsers/csv.py` which still needs it for reading)
4. **Verify mypy passes** — pandas-stubs issue in `export/` should disappear
5. **Tests** — verify CSV output matches expected format

### Lint Concurrency (P8) — 0.5 day
1. **Add `asyncio.gather` to `_check_contradictions`** — fan out page pair checks with semaphore
2. **Add max pairs limit** — cap at 50 pairs per lint run, warn if exceeded
3. **Tests** — verify concurrent execution, verify pair limit

## Risks

- Anthropic API rate limits may throttle concurrent requests — the semaphore bounds this, but need to handle 429 responses with retry
- Reordering chunks after `asyncio.gather` requires tracking original indices — use `enumerate` and sort results

## Agents

- **Performance Engineer** — validates all changes with before/after measurements
- **Tech Lead** — reviews async patterns for correctness
