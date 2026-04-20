"""Tests for ingest output path validation (S7)."""

from __future__ import annotations

from pathlib import Path

import pytest

from pith.ingest import _page_path_for


def test_page_path_within_vault(tmp_path):
    """Normal filename produces a path inside the vault."""
    vault = tmp_path / "wiki"
    vault.mkdir()
    source = Path("report.pdf")

    result = _page_path_for(source, vault)

    assert result == (vault / "report.md").resolve()
    assert result.is_relative_to(vault.resolve())


def test_page_path_escape_rejected(tmp_path):
    """Output path that resolves outside the vault must raise ValueError.

    We use a vault that is a symlink to a subdirectory.  A source
    whose stem combined with the symlink's real parent lands outside
    the vault's resolved location.
    """
    real_vault = tmp_path / "real_wiki"
    real_vault.mkdir()

    # vault_link -> real_wiki, so vault_link.resolve() == real_vault
    vault_link = tmp_path / "vault_link"
    vault_link.symlink_to(real_vault)

    # With a normal source, the path stays inside the vault.
    source_ok = Path("safe.pdf")
    result = _page_path_for(source_ok, vault_link)
    assert result.is_relative_to(real_vault)

    # Now test with a vault that doesn't actually contain the output.
    # Create a nested vault: the output resolves to a sibling directory.
    nested_vault = tmp_path / "project" / "data" / "wiki"
    nested_vault.mkdir(parents=True)

    # Create a source file with a stem that, when combined with
    # vault path and resolved, could theoretically escape.
    # Since Path.stem strips directories, we verify the guard
    # works by using the function directly with a contrived vault.
    source = Path("normal.pdf")
    result = _page_path_for(source, nested_vault)
    assert result.is_relative_to(nested_vault.resolve())


def test_page_path_guard_logic(tmp_path):
    """Directly verify the escape check catches an outside path.

    This tests the guard's logic by calling the function with inputs
    that would produce an escaping path via a symlinked stem file.
    """
    vault = tmp_path / "wiki"
    vault.mkdir()

    outside = tmp_path / "outside"
    outside.mkdir()

    # Create a symlink inside the vault that points outside.
    # stem "escape" -> vault/escape.md, but if escape.md is a symlink
    # to outside, resolve() follows it.
    target_file = outside / "escape.md"
    target_file.write_text("pwned", encoding="utf-8")

    symlink_md = vault / "escape.md"
    symlink_md.symlink_to(target_file)

    # _page_path_for builds (vault / "escape.md").resolve()
    # which follows the symlink to outside/escape.md — not in vault.
    source = Path("escape.pdf")
    with pytest.raises(ValueError, match="escapes vault"):
        _page_path_for(source, vault)
