---
name: pith-schema-design
description: How to design PITH schema packs — schema.yaml structure, AGENT.md instruction layers, frontmatter conventions, staleness rules, and seed page standards.
globs: "schemas/**,**/schema.yaml,**/AGENT.md"
---

# PITH Schema Design

## Schema Pack Structure
```
schemas/[vertical-name]/
  schema.yaml    — entity definitions, fields, cross-references, staleness, lint rules
  AGENT.md       — LLM instruction layer for ingest pipeline
  seeds/         — 3-5 example wiki pages (what good looks like)
  README.md      — human-readable guide for this vertical
```

## schema.yaml Format
```yaml
version: "1.0"
vertical: [name]
language: [en | sr | mixed]
description: [one sentence]

entities:
  [entity-name]:
    description: [what this entity represents]
    required_fields:
      - [field-name]: [type]  # [description]
    optional_fields:
      - [field-name]: [type]  # [description]
    staleness_days: [integer | null]  # null = evergreen
    vaulted_fields:  # never visible to contributors
      - [field-name]

cross_references:
  - from: [entity-type]
    field: [field-name]
    to: [entity-type]
    cardinality: one | many

staleness_rules:
  - entity: [entity-type]
    field: [field-name]
    condition: [condition description]
    action: flag | block | notify
    window_days: [integer]

lint_rules:
  - name: [rule-name]
    description: [what this catches]
    entity: [entity-type]
    check: [condition]
    severity: warning | error

privacy:
  level_1_exclude:  # fields excluded from cloud and cross-client for level-1 clients
    - [entity-type].[field-name]
  global_graph_exclude:  # entities excluded from cross-client query
    - [entity-type] where privacy_level == 1
```

## AGENT.md Format
The AGENT.md is the LLM instruction layer. It tells the ingest model how to behave when compiling raw sources into wiki pages.

```markdown
# [Vertical] — Agent Instructions

## Your Role
[What the ingest agent does for this vertical]

## Entity Recognition
When ingesting a source, identify which entities are present and create/update:
[List entity types and what source signals indicate each]

## Required Field Validation
Before writing any entity, verify:
[Specific validation rules per entity]

## Quality Gates
REJECT and surface for human review if:
[Specific rejection conditions]

## Cross-Reference Rules
[How entities link to each other]

## Verbatim Preservation Rules
[What content must never be paraphrased]

## Staleness Enforcement
[What triggers a staleness flag and what to do]
```

## Frontmatter Conventions
```yaml
---
entity: [entity-type]
id: [kebab-case-unique-id]
client_ref: [client-id | global]  # global = cross-client
privacy_level: 1 | 2 | 3
tags: [list of global tags]
staleness_days: [integer | null]
created: [YYYY-MM-DD]
updated: [YYYY-MM-DD]
vaulted: true | false
verbatim: true | false  # true = preserve exact language, never paraphrase
---
```

## Seed Page Standards
5 seed pages shipped with each schema pack:
1. One complete, populated entity per major entity type
2. Show vaulted fields (with VAULTED comment) so users understand the access model
3. Demonstrate cross-references working (not just standalone entities)
4. Include at least one example of the staleness mechanism
5. Named `example-[descriptor].md` — not `entity-1.md`

## Staleness Implementation
```yaml
# In frontmatter of any wiki page
staleness_check:
  last_verified: 2026-01-15
  window_days: 90
  status: current  # current | stale | pending-verification
```

PITH's lint command reads these fields and surfaces stale pages.

## Privacy Level Enforcement
At the engine level in `pith/privacy.py`:
```python
def can_include_in_global_query(entity: WikiEntity, client: Client) -> bool:
    if client.privacy_level == 1:
        return False  # Hard block — no exceptions
    return True

def can_send_to_cloud_model(content: str, client: Client) -> bool:
    if client.privacy_level == 1:
        raise PrivacyViolationError(
            f"Client {client.id} is Level 1 (local-only). "
            "Cannot send content to cloud model."
        )
    return True
```
