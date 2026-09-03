## 1. Context & Task Scope
The HSE Easy Mock MCP Server currently successfully loads regulatory documents, legal citations, and TDI service offerings into memory on startup and validates them via Pydantic v2 schemas. However, it does not yet expose the 5 core MCP tools required by the Strands AI agents (`list_regulatory_updates`, `search_regulatory_docs`, `get_document_by_id`, `verify_legal_citation`, `get_tdi_service_offerings`) nor their tool docstrings or JSON Schema annotations. This task focuses on implementing these tools.

## 2. Prerequisites
- Phase 1 (Data Schemas) and Phase 2 (Fixtures) are completed.
- FastMCP startup and memory indexing are in place in `server.py` (Task 3.1).

## 3. Objectives
- Implement `list_regulatory_updates` with `date_from`, `date_to`, source filtering, and descending date sort.
- Implement `search_regulatory_docs` with keyword, source, and topic matching.
- Implement `get_document_by_id` and raise a clear `ValueError` on 404.
- Implement `verify_legal_citation` matching aliases and returning validity.
- Implement `get_tdi_service_offerings` for topic and sector matching with deterministic fallback.
- Ensure every tool has rich docstrings, parameter descriptions, and type annotations as outlined in `SPECIFICATIONS.md`.

## 4. Proposed Changes & Specifications

### `server.py`
- [MODIFY] `server.py`
  - Define `list_regulatory_updates` wrapped with `@mcp.tool()` and rich descriptions.
  - Define `search_regulatory_docs` wrapped with `@mcp.tool()`.
  - Define `get_document_by_id` wrapped with `@mcp.tool()`.
  - Define `verify_legal_citation` wrapped with `@mcp.tool()`.
  - Define `get_tdi_service_offerings` wrapped with `@mcp.tool()`.
  - Ensure type annotations for `List[RegulatoryUpdateSummary]`, `RegulatoryDocument`, `CitationVerificationResult`, and `List[TDIServiceOffering]` are maintained for accurate JSON schema generation.

### Details of Tool Implementation
- The logic will mirror the provided reference architecture in `ARCHITECTURE.md`.
- `list_regulatory_updates`: Will filter the `REGULATORY_DOCS` list by source, `date_from`, `date_to` and return up to `limit` summaries.
- `search_regulatory_docs`: Will perform a case-insensitive search across title, summary, official_reference, and topic tags.
- `get_document_by_id`: Loops through docs and raises `ValueError(f"Document with ID '{doc_id}' not found.")` if absent.
- `verify_legal_citation`: Normalizes input to lowercase and matches against the citations list and `aliases`. If unmatched, returns `status="unrecognized"` and `is_valid=False`.
- `get_tdi_service_offerings`: Searches TDI services for topic or sector matches. Falls back to `TDI_SERVICES[:1]` if no matches exist.

## 5. Verification Strategy
- **Manual Verification**: Run `uv run fastmcp dev server.py` and interact with each tool via the MCP Inspector.
- **Automated Tests**: Later verified in Phase 4.1 (`pytest` and determinism tests).

## 6. Questions & Decisions for Human Approval

### a. Question
Are the fallback logic for `get_tdi_service_offerings` and the case-insensitive alias matching for `verify_legal_citation` fully aligned with the expected deterministic behavior?

### b. Brief Background
The specification states we need a "deterministic fallback offering" for `get_tdi_service_offerings` if no topics or sectors match. The reference architecture suggests returning the first offering in the list (`TDI_SERVICES[:1]`). For `verify_legal_citation`, the list contains exact "citation_input" and multiple "aliases" (like "d.lgs. 81/2008 art. 37") which must be matched case-insensitively.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Use `TDI_SERVICES[:1]` as the deterministic fallback for services, and enforce exact case-insensitive matching on the predefined aliases list for citations (as per `ARCHITECTURE.md`).
- **Option 2**: Enhance the fallback logic to look for a generic "all_sectors" service, and use fuzzy matching instead of strict alias matching for citations.
- **Option 3**: Raise an exception if no TDI service matches, enforcing strict taxonomy alignment.

### d. Justification of the Recommendation
Option 1 is strongly recommended because the mock server must remain strictly deterministic, predictable, and simple. It perfectly aligns with the blueprint provided in `ARCHITECTURE.md` and guarantees reproducible QA test executions without introducing non-deterministic fuzzy logic.

