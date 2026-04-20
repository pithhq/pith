# Sprint 2 — Polish

**Duration:** 1 week
**Goal:** Clean up every remaining P2 audit finding. Improve error handling, config safety, and developer experience.

## Exit Criteria

- [ ] Frontmatter parsing standardized across all modules (audit S11)
- [ ] `pith init` confirms before overwriting existing config (audit S12)
- [ ] Suppressed exceptions logged at debug level (audit S13)
- [ ] File size limits enforced before parsing (audit S9)
- [ ] `pith sync` command fully implemented (currently empty)
- [ ] i18n string coverage complete — no untranslated strings
- [ ] `pith --help` and all subcommands produce clean, useful output

## Tasks

### Frontmatter Standardization (S11) — 1 day
1. **Create `pith/frontmatter.py`** — shared utility with `parse_frontmatter(text) -> (dict, str)` using `yaml.safe_load`
2. **Replace hand-rolled parser in `export/__init__.py:39-60`** with shared utility
3. **Replace parser in `lint/__init__.py:44-53`** with shared utility
4. **Replace regex stripping in `query/__init__.py:24-25`** with shared utility
5. **Tests** — verify identical output across all three former implementations

### Config Safety (S12) — 0.5 day
1. **Add overwrite check in `_write_config()`** — if `pith.config.json` exists, prompt `typer.confirm()`
2. **Add `--force` flag to `pith init`** to skip confirmation
3. **Tests** — verify prompt appears, verify `--force` skips it

### Exception Logging (S13) — 0.5 day
1. **Add `logging` module** to `pith/license/__init__.py` — log caught exceptions at `DEBUG` level before returning invalid
2. **Same for `pith/cli/__init__.py:137`** — log the activation exception
3. **Add `--verbose` / `-v` global flag** that sets log level to DEBUG
4. **Tests** — verify debug output contains exception info when `-v` is passed

### File Size Limits (S9) — 0.5 day
1. **Add `ingest.max_file_size_mb` config field** — defaults to 100
2. **Check file size in `pith/parsers/__init__.py:parse()`** before dispatching to format-specific parser
3. **Raise `ParseError`** with clear message if file exceeds limit
4. **Tests** — verify oversized files are rejected

### Sync Command Implementation — 2 days
1. **Implement `pith sync`** — `git add .`, `git commit -m "pith sync: {timestamp}"`, `git push` if remote configured
2. **Use gitpython** (already a dependency) for all git operations
3. **Respect `sync.active_hours`** — skip if outside configured window
4. **Respect `sync.remote`** — skip push if no remote configured
5. **Handle common errors** — no git repo, dirty index, merge conflicts, auth failure
6. **Tests** — use temp git repos, verify commit message format, verify active hours gating

### i18n Audit — 0.5 day
1. **Grep for raw strings in user-facing output** — any `print()`, `typer.echo()`, or `output.*()` call with a literal string instead of `t()`
2. **Add missing i18n keys** to the string table
3. **Verify all `t()` calls have corresponding entries**

## Risks

- `pith sync` touching git operations needs careful error handling — network failures, SSH key issues, merge conflicts
- Frontmatter standardization could change parsing behavior for edge cases — run full test suite after each module migration

## Agents

- **Tech Lead** — reviews sync implementation, frontmatter refactor
- **QA Lead** — verifies i18n coverage, reviews error handling
