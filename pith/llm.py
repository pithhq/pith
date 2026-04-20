"""LLM interface — all calls route through Claude Code CLI (`claude -p`)."""

from __future__ import annotations

import asyncio
import subprocess


class LLMError(Exception):
    """Raised when a Claude Code CLI call fails."""

    def __init__(self, detail: str) -> None:
        self.detail = detail
        super().__init__(detail)


def call_claude(
    prompt: str,
    *,
    system: str | None = None,
    model: str = "claude-sonnet-4-6",
) -> str:
    """Call Claude Code CLI and return the response text.

    Args:
        prompt:  The user prompt to send.
        system:  Optional system prompt (prepended to the prompt).
        model:   Model identifier passed to ``--model``.

    Returns:
        The model's response text, stripped of leading/trailing whitespace.

    Raises:
        LLMError: If the subprocess exits non-zero or times out.
    """
    full_prompt = f"{system}\n\n{prompt}" if system else prompt

    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model],
            input=full_prompt,
            capture_output=True,
            text=True,
            timeout=300,
        )
    except FileNotFoundError:
        raise LLMError(
            "claude CLI not found. Install Claude Code: "
            "https://docs.anthropic.com/en/docs/claude-code"
        )
    except subprocess.TimeoutExpired:
        raise LLMError("claude -p timed out after 300 seconds")

    if result.returncode != 0:
        raise LLMError(f"claude -p failed (exit {result.returncode}): {result.stderr}")

    return result.stdout.strip()


async def call_claude_async(
    prompt: str,
    *,
    system: str | None = None,
    model: str = "claude-sonnet-4-6",
) -> str:
    """Async wrapper around :func:`call_claude` using ``asyncio.to_thread``."""
    return await asyncio.to_thread(
        call_claude,
        prompt,
        system=system,
        model=model,
    )
