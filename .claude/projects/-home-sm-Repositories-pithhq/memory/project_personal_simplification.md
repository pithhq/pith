---
name: Personal simplification
description: PITH simplified for personal use — no commercial launch, all LLM calls via claude -p subprocess, license system stubbed
type: project
---

PITH was simplified for personal use on 2026-04-09.

**What changed:**
- All model provider calls (Anthropic API httpx, Ollama httpx) replaced with `claude -p` subprocess calls via `pith/llm.py`
- License system (`pith/license/__init__.py`) stubbed to always return valid
- Config model simplified: no `providers`, `license`, `ModelProvider`, `AnthropicProvider`, `OllamaProvider` — models are plain strings
- `pith activate` CLI command removed
- `httpx` and `cryptography` dependencies removed from pyproject.toml

**Why:** User is using PITH for personal use only, no commercial launch planned. Routes everything through Claude Code Max subscription — no API key needed.

**How to apply:** Don't add API key handling, provider abstractions, or license enforcement. All LLM calls go through `pith.llm.call_claude()` / `call_claude_async()`.
