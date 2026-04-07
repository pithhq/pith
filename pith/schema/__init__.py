"""Schema pack loader — reads and validates vertical schema packs.

A schema pack lives at ``schemas/{name}/`` and contains:
  schema.yaml  — entity definitions, legislation config, lint rules
  AGENT.md     — raw LLM instructions for the ingest pipeline
  seeds/       — example wiki pages (listed, not parsed at load time)

Public interface:
    pack = load_schema("law-firm-sr", schemas_root)
"""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import yaml
from pydantic import BaseModel, Field, ValidationError

from pith.i18n import t

_DEFAULT_SCHEMAS_ROOT = Path(__file__).parent.parent.parent / "schemas" / "schemas"


# --- Pydantic validation models for schema.yaml ---


class SchemaMetadata(BaseModel):
    """Top-level ``schema:`` block in schema.yaml."""

    name: str
    version: str
    language: str
    mixed_script: bool = False


class EntityDef(BaseModel):
    """Definition of a single entity type."""

    description: str
    required_fields: list[str] = Field(default_factory=list)
    optional_fields: list[str] = Field(default_factory=list)
    links_to: list[str] = Field(default_factory=list)


class LegislationRef(BaseModel):
    """Configuration for the ``references_legislation`` feature."""

    enabled: bool = False
    slug_format: str = ""
    example: str = ""
    staleness_tracking: bool = False


class LegislationConfig(BaseModel):
    """Top-level ``legislation:`` block."""

    references_legislation: LegislationRef = Field(
        default_factory=LegislationRef,
    )


class StaleCheck(BaseModel):
    """Staleness check configuration inside lint rules."""

    field: str = ""
    source_file: str = ""


class SchemaLintConfig(BaseModel):
    """Top-level ``lint:`` block in schema.yaml."""

    orphan_exempt_entities: list[str] = Field(default_factory=list)
    required_cross_references: dict[str, list[str]] = Field(
        default_factory=dict,
    )
    stale_check: StaleCheck = Field(default_factory=StaleCheck)


class IngestHints(BaseModel):
    """Top-level ``ingest:`` block in schema.yaml."""

    chunk_strategy: str = "by_section"
    frontmatter_fields: list[str] = Field(default_factory=list)


class SchemaYaml(BaseModel):
    """Root model for the entire schema.yaml file."""

    schema_: SchemaMetadata = Field(alias="schema")
    entities: dict[str, EntityDef]
    legislation: LegislationConfig | None = None
    lint: SchemaLintConfig | None = None
    ingest: IngestHints | None = None


# --- Public dataclass ---


@dataclass(frozen=True)
class SchemaPack:
    """Loaded and validated schema pack.

    Attributes:
        name:                Schema name (e.g. ``law-firm-sr``).
        version:             Schema version string.
        language:            Language code (e.g. ``sr``).
        mixed_script:        Whether the schema uses mixed scripts.
        entities:            Entity type definitions keyed by name.
        legislation:         Legislation tracking config, or ``None``.
        lint:                Schema-specific lint rules, or ``None``.
        agent_instructions:  Raw contents of ``AGENT.md``.
        seeds_dir:           Path to the ``seeds/`` directory.
    """

    name: str
    version: str
    language: str
    mixed_script: bool
    entities: dict[str, EntityDef]
    legislation: LegislationConfig | None
    lint: SchemaLintConfig | None
    agent_instructions: str
    seeds_dir: Path


# --- Exceptions ---


class SchemaNotFoundError(Exception):
    """Raised when a schema pack directory does not exist."""

    def __init__(self, name: str) -> None:
        self.name = name
        super().__init__(t("schema.not_found", name=name))


class SchemaValidationError(Exception):
    """Raised when schema.yaml fails validation."""

    def __init__(self, name: str, detail: str) -> None:
        self.name = name
        self.detail = detail
        super().__init__(t("schema.validation_error", name=name, detail=detail))


# --- Loader ---


def load_schema(
    name: str,
    schemas_root: Path = _DEFAULT_SCHEMAS_ROOT,
) -> SchemaPack:
    """Load and validate a schema pack from disk.

    Args:
        name:         Schema name (directory name under *schemas_root*).
        schemas_root: Root directory containing schema pack directories.

    Returns:
        A validated ``SchemaPack`` ready for use by the ingest pipeline.

    Raises:
        SchemaNotFoundError:    If the schema directory does not exist.
        SchemaValidationError:  If ``schema.yaml`` is missing or invalid.
    """
    schema_dir = schemas_root / name

    if not schema_dir.is_dir():
        raise SchemaNotFoundError(name)

    yaml_path = schema_dir / "schema.yaml"
    if not yaml_path.exists():
        raise SchemaValidationError(
            name,
            t("schema.missing_yaml", path=str(yaml_path)),
        )

    try:
        raw = yaml.safe_load(yaml_path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise SchemaValidationError(name, str(exc)) from exc

    try:
        parsed = SchemaYaml.model_validate(raw)
    except ValidationError as exc:
        raise SchemaValidationError(name, str(exc)) from exc

    agent_path = schema_dir / "AGENT.md"
    agent_instructions = (
        agent_path.read_text(encoding="utf-8") if agent_path.exists() else ""
    )

    seeds_dir = schema_dir / "seeds"

    return SchemaPack(
        name=parsed.schema_.name,
        version=parsed.schema_.version,
        language=parsed.schema_.language,
        mixed_script=parsed.schema_.mixed_script,
        entities=parsed.entities,
        legislation=parsed.legislation,
        lint=parsed.lint,
        agent_instructions=agent_instructions,
        seeds_dir=seeds_dir,
    )


__all__ = [
    "EntityDef",
    "IngestHints",
    "LegislationConfig",
    "LegislationRef",
    "SchemaLintConfig",
    "SchemaNotFoundError",
    "SchemaPack",
    "SchemaValidationError",
    "SchemaYaml",
    "StaleCheck",
    "load_schema",
]
