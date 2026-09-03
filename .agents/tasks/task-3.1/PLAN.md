## 1. Context & Task Scope
This task (3.1) represents the foundational step for Phase 3 of the HSE Easy Mock MCP Server roadmap. The goal is to establish the `server.py` file, configure the FastMCP instance, load the pre-seeded mock JSON fixtures from the `fixtures/` directory on startup, validate them against our Pydantic v2 schemas (`models.py`), and build efficient in-memory hash maps/indexes to enable sub-15ms lookups for the MCP tools that will be implemented in subsequent tasks.

## 2. Prerequisites
- `pyproject.toml` environment is configured with `fastmcp>=0.1.0` and `pydantic>=2.0.0` (completed in Phase 1).
- `models.py` with Tier 1 and Tier 2 schemas (completed in Phase 1).
- Fixture datasets (`regulatory_docs.json`, `citations.json`, `tdi_services.json`) exist in `fixtures/` (completed in Phase 2).

## 3. Objectives
- Create the core `server.py` entrypoint.
- Instantiate a `FastMCP` server named `"HSE-Easy-Mock-Server"`.
- Read and parse `regulatory_docs.json`, `citations.json`, and `tdi_services.json` at startup.
- Validate all loaded JSON records into their respective Pydantic models (`RegulatoryDocument`, `CitationVerificationResult` for citations, and `TDIServiceOffering`).
- Construct in-memory data structures (lists or dictionaries) to ensure instant lookup capabilities.
- Maintain a startup time of `<50ms` and ensure zero external database or cloud dependencies.

## 4. Proposed Changes & Specifications

### `server.py` [NEW]
- **Imports**: `json`, `Path` from `pathlib`, `FastMCP` from `fastmcp`, and Pydantic models from `models.py`.
- **Server Initialization**: Initialize `mcp = FastMCP("HSE-Easy-Mock-Server")`.
- **Fixture Loading & Validation**:
  - Resolve the `fixtures/` directory path relative to `server.py`.
  - Read `regulatory_docs.json` and instantiate a list of `RegulatoryDocument` objects.
  - Read `citations.json` and store it in an easily searchable format (raw dict or parsed models). For optimal tool performance later (tool `verify_legal_citation`), we can keep it as a raw list of dicts or parse it. The architecture blueprint uses a raw list of dicts for `citations.json` because the schema `CitationVerificationResult` matches the output of the tool, not directly the raw input which contains `aliases`. However, validating the structure is good. I will stick to the blueprint `CITATIONS_RAW = json.load(f)`.
  - Read `tdi_services.json` and instantiate a list of `TDIServiceOffering` objects.
- **Indexing**: 
  - Create global variables `REGULATORY_DOCS`, `CITATIONS_RAW`, and `TDI_SERVICES`.
  - Provide a `SUMMARY_EXCLUDE` set and a `to_summary()` helper function as specified in the blueprint in `ARCHITECTURE.md` to map Tier 2 (`RegulatoryDocument`) down to Tier 1 (`RegulatoryUpdateSummary`).
- **Main Block**: Add the `if __name__ == "__main__": mcp.run()` execution block.

*Note: The actual MCP tools (`@mcp.tool()`) will be implemented in task 3.2. This task focuses solely on the server foundation and fixture indexing.*

## 5. Verification Strategy
- **Syntax & Execution**: Run `python server.py` to ensure it starts without errors and parses the JSON files correctly.
- **Static Analysis**: Run `uv run pyright server.py` or similar type-checking to ensure types align.
- **Performance Profiling**: The startup logic should be trivial (reading 3 small JSON files). A simple timing check or profiler can verify it meets the `<50ms` criteria.

## 6. Questions & Decisions for Human Approval

### a. Question
Should we parse `citations.json` into a Pydantic model at startup, or keep it as raw JSON dictionaries as outlined in `ARCHITECTURE.md`?

### b. Brief Background
The architecture blueprint currently reads `citations.json` into a raw dictionary `CITATIONS_RAW = json.load(f)` because the JSON contains `aliases` which are used during the lookup tool but aren't part of the final `CitationVerificationResult` output schema. Validating them into an internal model at startup would be cleaner and safer, but slightly deviates from the provided code blueprint.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Follow the `ARCHITECTURE.md` blueprint exactly (keep as raw dictionaries). It satisfies the fast startup requirement and maps perfectly to the planned tool implementation in 3.2.
- **Option 2**: Create an internal `CitationFixture` Pydantic model in `server.py` to strictly validate `citations.json` on startup.

### d. Justification of the Recommendation
Following Option 1 aligns directly with the established `ARCHITECTURE.md` blueprint. It avoids polluting `models.py` with server-internal structures and minimizes startup overhead.

