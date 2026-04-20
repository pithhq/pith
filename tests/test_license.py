"""Tests for pith.license — personal-use stub."""

from __future__ import annotations

from pith.license import activate, validate_license


def test_activate_returns_valid():
    """activate() always returns valid for personal use."""
    result = activate("any_key")
    assert result.valid
    assert result.tier == "personal"


def test_validate_returns_valid():
    """validate_license() always returns valid for personal use."""
    result = validate_license()
    assert result.valid
    assert result.tier == "personal"
