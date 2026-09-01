# Implementation Plan - Task 1.2: Two-Tier Data Schemas (`models.py`)

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md), [SPECIFICATIONS.md § 3](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md#L24-L144), and [ARCHITECTURE.md § 4.1](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md#L72-L123), Task 1.2 implements the core data contracts for the HSE Easy Mock MCP Server in `models.py`.

The server enforces a two-tier schema strategy:
1. **Tier 1 (Lightweight Feed Summary)**: Optimizes token efficiency for agent feed monitoring and search discovery.
2. **Tier 2 (Comprehensive Regulatory Act)**: Encapsulates deep legal obligations, sanction structures, related citations, and full Markdown content for detailed downstream analysis.
3. **Legal QA & Citation Verification**: Exposes normalized citation verification results.
4. **Commercial Conversion**: Structures TDI consulting and training service offerings with ready-to-insert CTA templates.

---

## 2. Prerequisites
- Completion of Task 1.1 (`pyproject.toml`, `pydantic>=2.0.0` installed in virtual environment).
- Python 3.10+ execution environment (`uv sync` active).

---

## 3. Objectives
1. Implement Pydantic v2 models in `models.py` matching all specifications in [SPECIFICATIONS.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md):
   - `RegulatoryUpdateSummary` (Tier 1)
   - `RegulatoryDocument` (Tier 2, inheriting from `RegulatoryUpdateSummary`)
   - `CitationVerificationResult` (Legal Citation Verification)
   - `TDIServiceOffering` (Commercial Conversion & CTA Catalog)
2. Add full field-level metadata using Pydantic `Field(description=...)` for downstream MCP schema generation and LLM tool introspection.
3. Implement a clean conversion helper method `to_summary()` on `RegulatoryDocument` to easily project Tier 2 documents down to Tier 1 summaries.
4. Create test suite in `tests/test_models.py` validating instantiation, field constraints, type validation, serialization/deserialization, and schema introspection.

---

## 4. Proposed Changes & Specifications

### 4.1 File: `models.py`
Create `models.py` with the following four primary Pydantic v2 models and conversion utility:

```python
from typing import List, Literal, Optional
from pydantic import BaseModel, Field, ConfigDict


class RegulatoryUpdateSummary(BaseModel):
    """Tier 1 lightweight summary model for HSE regulatory updates."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    doc_id: str = Field(
        ...,
        description="Unique slug identifier (e.g. 'gu-2024-dl-preposti', 'eurlex-dir-2024-869')"
    )
    source: Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"] = Field(
        ...,
        description="Authoritative regulatory source body"
    )
    doc_type: Literal["directive", "regulation", "decree", "circular", "guideline"] = Field(
        ...,
        description="Legal instrument category"
    )
    official_reference: str = Field(
        ...,
        description="Canonical legal reference (e.g. 'D.Lgs. 81/2008', 'Direttiva (UE) 2024/869')"
    )
    title: str = Field(
        ...,
        description="Official title of the regulatory act in Italian"
    )
    publication_date: str = Field(
        ...,
        description="Publication date formatted as ISO 8601 YYYY-MM-DD"
    )
    effective_date: Optional[str] = Field(
        default=None,
        description="Date when obligations enter into force (YYYY-MM-DD)"
    )
    impact_level: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Editorial urgency and operational impact rating for Scout triage"
    )
    topic_tags: List[str] = Field(
        default_factory=list,
        description="HSE domain tags (e.g. ['workplace_safety', 'training', 'chemical_risk'])"
    )
    summary: str = Field(
        ...,
        description="1-2 paragraph plain-language executive summary of the act and affected parties"
    )
    canonical_url: str = Field(
        ...,
        description="Official direct URL to the gazette or portal publication"
    )


class RegulatoryDocument(RegulatoryUpdateSummary):
    """Tier 2 comprehensive document model including deep legal obligations, sanctions, and text."""
    status: Literal["in_force", "amended", "repealed", "proposed"] = Field(
        ...,
        description="Current legal status of the document"
    )
    target_sectors: List[str] = Field(
        default_factory=list,
        description="Applicable industrial and commercial sectors (e.g. ['manufacturing', 'construction'])"
    )
    key_obligations: List[str] = Field(
        default_factory=list,
        description="Explicit compliance obligations for employers, HSE managers, and RSPPs"
    )
    penalties_summary: Optional[str] = Field(
        default=None,
        description="Summary of legal sanctions, administrative fines, or criminal liabilities"
    )
    related_citations: List[str] = Field(
        default_factory=list,
        description="Referenced national and European laws, standards, or articles"
    )
    content_markdown: str = Field(
        ...,
        description="Cleaned, structured full text or article breakdown in Markdown"
    )

    def to_summary(self) -> RegulatoryUpdateSummary:
        """Converts Tier 2 RegulatoryDocument into Tier 1 RegulatoryUpdateSummary."""
        exclude_fields = {
            "status",
            "target_sectors",
            "key_obligations",
            "penalties_summary",
            "related_citations",
            "content_markdown",
        }
        return RegulatoryUpdateSummary(**self.model_dump(exclude=exclude_fields))


class CitationVerificationResult(BaseModel):
    """Legal citation verification result returned by legal QA tools."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    citation_input: str = Field(
        ...,
        description="The raw citation text submitted for verification"
    )
    is_valid: bool = Field(
        ...,
        description="True if the reference exists, is legally sound, and verified"
    )
    status: Literal["in_force", "amended", "repealed", "unrecognized"] = Field(
        ...,
        description="Legal validity status of the cited provision"
    )
    canonical_citation: str = Field(
        ...,
        description="Standardized legal citation text (e.g. 'D.Lgs. 9 aprile 2008, n. 81, Art. 37')"
    )
    official_reference: Optional[str] = Field(
        default=None,
        description="Base parent law reference"
    )
    official_url: Optional[str] = Field(
        default=None,
        description="Direct link to the verified article on official portal (Normattiva/EUR-Lex)"
    )
    verified_against_doc_id: Optional[str] = Field(
        default=None,
        description="Matching document ID in the mock corpus if available"
    )
    notes: Optional[str] = Field(
        default=None,
        description="Legal nuances, recent amendment history, or transitional provisions"
    )


class TDIServiceOffering(BaseModel):
    """Commercial service offering and pre-approved CTA templates for lead conversion."""
    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    service_id: str = Field(
        ...,
        description="Unique identifier for the TDI commercial service"
    )
    service_name: str = Field(
        ...,
        description="Official commercial title of the consulting or training service"
    )
    topic_category: str = Field(
        ...,
        description="Primary matching HSE topic category"
    )
    applicable_sectors: List[str] = Field(
        default_factory=list,
        description="Target industry sectors"
    )
    value_proposition: str = Field(
        ...,
        description="1-2 sentence value proposition explaining TDI's technical capability"
    )
    cta_headline: str = Field(
        ...,
        description="Conversion-focused headline for editorial Call-to-Action insertion"
    )
    cta_body: str = Field(
        ...,
        description="Persuasive body copy tailored to the regulatory risk and TDI solution"
    )
    landing_page_url: str = Field(
        ...,
        description="Canonical URL for lead capture and inquiry booking"
    )
```

### 4.2 File: `tests/test_models.py`
Create unit test suite covering:
1. Valid instantiation of all 4 models with complete and minimal payloads.
2. Literal validation (e.g. Invalid `source`, `doc_type`, `impact_level`, `status` raises `ValidationError`).
3. Tier 2 `RegulatoryDocument.to_summary()` projection.
4. JSON serialization and schema generation (`model_json_schema()`).
5. Optional field handling (defaulting to `None` or empty lists).

---

## 5. Verification Strategy
1. **Static Syntax and Type Check**: Run `uv run python -m py_compile models.py`.
2. **Automated Unit Testing**: Execute `uv run pytest tests/test_models.py -v`.
3. **Pydantic Schema Introspection**: Verify generated JSON schemas for MCP compatibility.

---

## 6. Questions & Decisions for Human Approval

### a. Question
Should we configure `model_config = ConfigDict(extra="ignore", populate_by_name=True)` across all models or enforce `extra="forbid"`?

### b. Brief Background
The mock MCP server reads JSON fixtures (`regulatory_docs.json`, `citations.json`, `tdi_services.json`). In fixture datasets, `citations.json` contains an auxiliary `aliases: List[str]` field used by the in-memory lookup index that is not exposed directly in `CitationVerificationResult`. 

### c. Options with Recommendation
- **Option 1 (Recommended)**: Use `extra="ignore"`. This allows seamless hydration of Pydantic models directly from JSON fixtures without erroring on internal indexing fields like `aliases`, while preserving strict validation of required model fields.
- **Option 2**: Use `extra="forbid"` and strip non-model fields during fixture loading before model instantiation.

### d. Justification of the Recommendation
Option 1 avoids redundant dictionary manipulation and filtering code during fixture ingestion while maintaining strict type checking for all defined model attributes and clean serialization for tool output.
