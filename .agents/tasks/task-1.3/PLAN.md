# Implementation Plan - Task 1.3: Schema Validation & Serialization Tests

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md), [SPECIFICATIONS.md § 3](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md#L24-L144), and [ARCHITECTURE.md § 4.1](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md#L72-L123), Task 1.3 establishes comprehensive test coverage and schema validation assertions for the Pydantic v2 data models implemented in Task 1.2 (`models.py`).

The HSE Easy Mock MCP Server relies on strict two-tier data contracts:
1. **Tier 1 (`RegulatoryUpdateSummary`)**: Lightweight metadata model for fast feed polling and search queries.
2. **Tier 2 (`RegulatoryDocument`)**: Rich model containing deep legal obligations, sanctions, citations, and full markdown content.
3. **Legal QA (`CitationVerificationResult`)**: Structured response for legal citation validation and canonical reference lookup.
4. **Commercial Conversion (`TDIServiceOffering`)**: CTA templates and service catalog entries for lead generation.

Task 1.3 hardens and expands the test suite in `tests/test_models.py` to ensure complete coverage of:
- Required vs. optional field validation and missing field rejection.
- All valid and invalid `Literal` enum values across all models.
- Default values and factory isolation (e.g. empty lists not shared across instances).
- JSON serialization (`model_dump_json`), deserialization (`model_validate_json`), and dictionary conversion (`model_dump(mode="json")`).
- Unicode / Italian character fidelity (e.g. `à, è, é, ì, ò, ù, €, §`).
- Tier 2 to Tier 1 projection (`to_summary()`) integrity without field leakage.
- FastMCP / OpenAPI JSON Schema generation (`model_json_schema()`) conformance.

---

## 2. Prerequisites
- **Task 1.1 Completed**: `pyproject.toml` with `fastmcp>=0.1.0`, `pydantic>=2.0.0`, `pytest`, `pytest-asyncio`.
- **Task 1.2 Completed**: `models.py` containing the four Pydantic v2 models and `to_summary()` helper.
- Active Python 3.10+ virtual environment (`uv sync`).

---

## 3. Objectives
1. **Exhaustive Literal Enum Testing**:
   - Parametrize all valid enum values for `source` (`EUR_LEX`, `GAZZETTA_UFFICIALE`, `INAIL`).
   - Parametrize all valid enum values for `doc_type` (`directive`, `regulation`, `decree`, `circular`, `guideline`).
   - Parametrize all valid enum values for `impact_level` (`critical`, `high`, `medium`, `low`).
   - Parametrize all valid enum values for `status` in `RegulatoryDocument` (`in_force`, `amended`, `repealed`, `proposed`).
   - Parametrize all valid enum values for `status` in `CitationVerificationResult` (`in_force`, `amended`, `repealed`, `unrecognized`).
   - Verify that invalid literal values strictly raise `pydantic.ValidationError`.

2. **Field Constraint & Requirement Assertions**:
   - Systematically verify that omitting any required field (e.g., `doc_id`, `title`, `source`, `summary`, `citation_input`, `is_valid`, `service_id`, `cta_headline`) raises a `ValidationError`.
   - Verify that optional fields (`effective_date`, `penalties_summary`, `official_reference`, `official_url`, `verified_against_doc_id`, `notes`) default to `None`.
   - Verify that list fields (`topic_tags`, `target_sectors`, `key_obligations`, `related_citations`, `applicable_sectors`) default to independent empty lists `[]`.

3. **Serialization, Deserialization & Round-Trip Fidelity**:
   - Validate `model_dump_json()` and `model_validate_json()` round-trip serialization for all 4 models.
   - Verify correct serialization of `None` fields (serializes to JSON `null`).
   - Verify preservation of UTF-8 Italian characters (accents, legal section markers, quotes).

4. **Tier 2 to Tier 1 Projection Verification**:
   - Verify `RegulatoryDocument.to_summary()` produces a valid `RegulatoryUpdateSummary` instance with matching field values.
   - Ensure none of the Tier 2 specific attributes (`status`, `target_sectors`, `key_obligations`, `penalties_summary`, `related_citations`, `content_markdown`) leak into the summary object or its exported JSON/dict.

5. **MCP Schema Conformance**:
   - Verify `model_json_schema()` output structure for all 4 models to ensure full compatibility with FastMCP tool registration.

---

## 4. Proposed Changes & Specifications

### 4.1 File: `tests/test_models.py`
Refactor and expand `tests/test_models.py` to organize tests into distinct, descriptive test classes:

```python
"""Tests for Pydantic v2 data models in models.py.

Verifies field constraints, optional fields, literal enums,
JSON serialization/deserialization, schema generation, and Tier 2 projection.
"""

import json
import pytest
from pydantic import ValidationError

from models import (
    CitationVerificationResult,
    RegulatoryDocument,
    RegulatoryUpdateSummary,
    TDIServiceOffering,
)
```

#### Test Structure Breakdown:
1. **`TestRegulatoryUpdateSummary`**:
   - `test_valid_instantiation_full`: Instantiation with all fields populated.
   - `test_valid_instantiation_minimal`: Instantiation with only required fields.
   - `test_missing_required_fields`: Parametrized test asserting `ValidationError` when required fields are missing.
   - `test_source_literal_enums`: Parametrized test for valid sources (`EUR_LEX`, `GAZZETTA_UFFICIALE`, `INAIL`) and invalid source rejection.
   - `test_doc_type_literal_enums`: Parametrized test for valid doc types (`directive`, `regulation`, `decree`, `circular`, `guideline`) and invalid doc type rejection.
   - `test_impact_level_literal_enums`: Parametrized test for valid impact levels (`critical`, `high`, `medium`, `low`) and invalid impact level rejection.
   - `test_list_field_independence`: Verifies mutating one instance's `topic_tags` list does not affect another instance.
   - `test_extra_fields_ignored`: Verifies `extra="ignore"` config behavior.

2. **`TestRegulatoryDocument`**:
   - `test_valid_instantiation_full`: Instantiation with all Tier 1 + Tier 2 fields.
   - `test_valid_instantiation_minimal_tier2`: Instantiation with default lists and `penalties_summary=None`.
   - `test_missing_required_tier2_fields`: Missing `status` or `content_markdown` raises `ValidationError`.
   - `test_status_literal_enums`: Parametrized test for valid statuses (`in_force`, `amended`, `repealed`, `proposed`) and invalid status rejection.
   - `test_to_summary_projection`: Validates field equality and complete absence of Tier 2 fields in `to_summary()` output.
   - `test_to_summary_json_isolation`: Validates that `to_summary().model_dump_json()` contains only Tier 1 keys.

3. **`TestCitationVerificationResult`**:
   - `test_valid_instantiation_verified`: Verified citation with full metadata.
   - `test_valid_instantiation_unrecognized`: Unrecognized citation with minimal fields.
   - `test_missing_required_fields`: Missing `citation_input`, `is_valid`, `status`, or `canonical_citation` raises `ValidationError`.
   - `test_status_literal_enums`: Parametrized test for valid statuses (`in_force`, `amended`, `repealed`, `unrecognized`) and invalid rejection.
   - `test_boolean_type_coercion_and_validation`: Validates `is_valid` boolean handling.

4. **`TestTDIServiceOffering`**:
   - `test_valid_instantiation`: Instantiation of commercial service offering with full CTA copy.
   - `test_missing_required_fields`: Missing required fields raises `ValidationError`.
   - `test_applicable_sectors_default`: Defaults to empty list when omitted.

5. **`TestSerializationAndJsonSchema`**:
   - `test_json_roundtrip_all_models`: Serializes each model with `model_dump_json()` and restores with `model_validate_json()`, verifying field equality.
   - `test_model_dump_modes`: Verifies `model_dump(mode="python")` and `model_dump(mode="json")`.
   - `test_unicode_and_special_characters_preservation`: Tests Italian legal texts containing accents (`è, é, à, ò, ù`), currency symbols (`€`), and section symbols (`§`).
   - `test_model_json_schema_validity`: Validates that `model_json_schema()` produces standard OpenAPI/JSON Schema compatible structures with `title`, `type`, `properties`, and `required` definitions for FastMCP.

---

## 5. Verification Strategy
1. **Automated Unit Testing**:
   - Run `uv run pytest tests/test_models.py -v` to ensure 100% test pass rate across all new parametrized assertions.
2. **Schema Introspection Validation**:
   - Ensure all 4 models pass JSON schema generation without runtime errors.
3. **Execution Cleanliness**:
   - Verify zero warnings, zero regressions, and fast execution (<200ms for full test suite).

---

## 6. Questions & Decisions for Human Approval

### a. Question
Should we consolidate all schema and serialization tests into `tests/test_models.py` or split serialization and schema tests into a separate `tests/test_serialization.py` module?

### b. Brief Background
Task 1.3 focuses on validating the four Pydantic models defined in `models.py`. Currently, `tests/test_models.py` contains initial basic tests. As we expand to comprehensive field validation, literal enum parametrization, round-trip serialization, and JSON schema introspection, we can either keep all model-level tests in `tests/test_models.py` or separate them into multiple files.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Consolidate all model validation, enum coverage, Tier 2 projection, and serialization tests into `tests/test_models.py` structured with distinct, clean test classes (`TestRegulatoryUpdateSummary`, `TestRegulatoryDocument`, `TestCitationVerificationResult`, `TestTDIServiceOffering`, `TestSerializationAndJsonSchema`).
- **Option 2**: Split into `tests/test_models.py` (for validation & constraints) and `tests/test_serialization.py` (for JSON round-trip and schema generation).

### d. Justification of the Recommendation
Option 1 keeps the test architecture cohesive and aligned with the single `models.py` source module in Phase 1, making it easy to run all model contract verifications in one command (`pytest tests/test_models.py`) and maintaining simplicity before Phase 2 fixture and Phase 3 server tests are introduced.
