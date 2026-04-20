"""Tests for the schema pack loader."""

from __future__ import annotations

from pathlib import Path

import pytest

from pith.schema import (
    EntityDef,
    LegislationConfig,
    SchemaLintConfig,
    SchemaNotFoundError,
    SchemaPack,
    SchemaValidationError,
    load_schema,
)

# The submodule at schemas/ contains schemas/law-firm-sr/.
_SCHEMAS_ROOT = Path(__file__).parent.parent / "schemas"


class TestLoadSchemaLawFirmSr:
    """Test against the real law-firm-sr schema in the submodule."""

    @pytest.fixture()
    def pack(self) -> SchemaPack:
        return load_schema("law-firm-sr", _SCHEMAS_ROOT)

    def test_metadata(self, pack: SchemaPack) -> None:
        assert pack.name == "law-firm-sr"
        assert pack.version == "0.1.0"
        assert pack.language == "sr"
        assert pack.mixed_script is True

    def test_entities(self, pack: SchemaPack) -> None:
        assert set(pack.entities) == {"client", "matter", "precedent", "doctrine"}
        assert isinstance(pack.entities["client"], EntityDef)
        assert "title" in pack.entities["client"].required_fields
        assert "client_id" in pack.entities["client"].required_fields

    def test_matter_links(self, pack: SchemaPack) -> None:
        matter = pack.entities["matter"]
        assert "client" in matter.links_to
        assert "precedent" in matter.links_to

    def test_legislation_config(self, pack: SchemaPack) -> None:
        assert pack.legislation is not None
        assert isinstance(pack.legislation, LegislationConfig)
        ref = pack.legislation.references_legislation
        assert ref.enabled is True
        assert ref.staleness_tracking is True
        assert ref.slug_format == "{law-name}-{year}"

    def test_lint_config(self, pack: SchemaPack) -> None:
        assert pack.lint is not None
        assert isinstance(pack.lint, SchemaLintConfig)
        assert "client" in pack.lint.orphan_exempt_entities
        assert "client" in pack.lint.required_cross_references.get("matter", [])
        assert pack.lint.stale_check.field_name == "references_legislation"

    def test_agent_instructions(self, pack: SchemaPack) -> None:
        assert "entity_type" in pack.agent_instructions
        assert "Serbian" in pack.agent_instructions
        assert len(pack.agent_instructions) > 0

    def test_seeds_dir(self, pack: SchemaPack) -> None:
        assert pack.seeds_dir.is_dir()
        seed_files = list(pack.seeds_dir.glob("*.md"))
        assert len(seed_files) >= 3


class TestLoadSchemaErrors:
    def test_not_found(self, tmp_path: Path) -> None:
        with pytest.raises(SchemaNotFoundError) as exc_info:
            load_schema("nonexistent", tmp_path)
        assert "nonexistent" in str(exc_info.value)

    def test_missing_yaml(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "bad-schema"
        schema_dir.mkdir()
        with pytest.raises(SchemaValidationError):
            load_schema("bad-schema", tmp_path)

    def test_invalid_yaml(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "broken"
        schema_dir.mkdir()
        (schema_dir / "schema.yaml").write_text(
            "not: [valid: yaml: {{",
            encoding="utf-8",
        )
        with pytest.raises(SchemaValidationError):
            load_schema("broken", tmp_path)

    def test_missing_required_fields(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "incomplete"
        schema_dir.mkdir()
        (schema_dir / "schema.yaml").write_text(
            "schema:\n  name: test\n",
            encoding="utf-8",
        )
        with pytest.raises(SchemaValidationError):
            load_schema("incomplete", tmp_path)


class TestLoadSchemaMinimal:
    def test_minimal_valid_schema(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "minimal"
        schema_dir.mkdir()
        (schema_dir / "schema.yaml").write_text(
            "schema:\n"
            "  name: minimal\n"
            "  version: '1.0'\n"
            "  language: en\n"
            "entities:\n"
            "  note:\n"
            "    description: A simple note\n",
            encoding="utf-8",
        )

        pack = load_schema("minimal", tmp_path)

        assert pack.name == "minimal"
        assert pack.version == "1.0"
        assert pack.language == "en"
        assert pack.mixed_script is False
        assert "note" in pack.entities
        assert pack.legislation is None
        assert pack.lint is None
        assert pack.agent_instructions == ""
        assert pack.seeds_dir == schema_dir / "seeds"

    def test_with_agent_md(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "with-agent"
        schema_dir.mkdir()
        (schema_dir / "schema.yaml").write_text(
            "schema:\n"
            "  name: with-agent\n"
            "  version: '1.0'\n"
            "  language: en\n"
            "entities:\n"
            "  item:\n"
            "    description: An item\n",
            encoding="utf-8",
        )
        (schema_dir / "AGENT.md").write_text(
            "You are an agent.\n",
            encoding="utf-8",
        )

        pack = load_schema("with-agent", tmp_path)

        assert pack.agent_instructions == "You are an agent.\n"


class TestSchemaPathTraversal:
    """S6 — schema name must not escape schemas directory."""

    def test_dotdot_in_name_rejected(self, tmp_path: Path) -> None:
        with pytest.raises(SchemaValidationError, match="escapes"):
            load_schema("../etc/passwd", tmp_path)

    def test_normal_name_allowed(self, tmp_path: Path) -> None:
        schema_dir = tmp_path / "safe-schema"
        schema_dir.mkdir()
        (schema_dir / "schema.yaml").write_text(
            "schema:\n"
            "  name: safe-schema\n"
            "  version: '1.0'\n"
            "  language: en\n"
            "entities:\n"
            "  note:\n"
            "    description: A note\n",
            encoding="utf-8",
        )
        pack = load_schema("safe-schema", tmp_path)
        assert pack.name == "safe-schema"
