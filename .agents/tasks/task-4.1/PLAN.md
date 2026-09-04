# Implementation Plan: Task 4.1 - Automated Test Suite (`tests/test_server.py`)

## 1. Context & Task Scope
This task is part of Phase 4: Verification, Quality Assurance & Security Audit. The scope involves creating an automated test suite for the FastMCP tool implementations in `server.py`. The goal is to ensure the deterministic mock fixture engine correctly exposes the data through the 5 core tools with accurate filtering, searching, exact lookup, legal validation, and commercial matching logic. 

## 2. Prerequisites
- Python 3.10+ and the `uv` environment configured (Phase 1).
- Pydantic v2 schemas defined in `models.py` (Phase 1).
- Mock fixtures seeded in `fixtures/` (Phase 2).
- The 5 core MCP tools fully implemented in `server.py` (Phase 3).
- `pytest` installed as a dependency.

## 3. Objectives
- Implement comprehensive unit tests for `list_regulatory_updates` focusing on date-window filtering and chronological ordering.
- Implement tests for `search_regulatory_docs` verifying keyword matching, topic filtering, and source isolation.
- Implement tests for `get_document_by_id` confirming exact retrieval and correct exception handling (e.g., raising `ValueError` on 404).
- Implement tests for `verify_legal_citation` validating against both in-force (e.g., `D.Lgs. 81/2008 Art. 37`) and repealed (e.g., `D.Lgs. 626/94 Art. 3`) citations.
- Implement tests for `get_tdi_service_offerings` verifying commercial CTA matching logic based on topic inputs (e.g., `chemical_risk` mapping to `tdi-srv-chemical-audit`).

## 4. Proposed Changes & Specifications

### `tests/test_server.py` (New File)
We will create a new test file containing standard `pytest` test cases to exercise the functions directly from `server.py`:

- **`test_list_regulatory_updates()`**:
  - Call `list_regulatory_updates(date_from="2024-01-01", date_to="2024-12-31")`.
  - Assert the result count and ensure chronological ordering (newest first).
  - Test `source` filtering.

- **`test_search_regulatory_docs()`**:
  - Call `search_regulatory_docs(query="preposti")`.
  - Assert the returned documents contain the keyword in titles/summaries/tags.
  - Test filtering by `topic` and `source`.

- **`test_get_document_by_id()`**:
  - Fetch an existing document ID (e.g., `eurlex-dir-2024-869`) and assert Tier 2 fields are present.
  - Fetch a non-existent document ID and assert `ValueError` is raised using `pytest.raises`.

- **`test_verify_legal_citation()`**:
  - Test valid case: `verify_legal_citation("D.Lgs. 81/2008 Art. 37")` -> assert `is_valid == True` and `status == "in_force"`.
  - Test invalid/repealed case: `verify_legal_citation("D.Lgs. 626/94 Art. 3")` -> assert `is_valid == False` and `status == "repealed"`.

- **`test_get_tdi_service_offerings()`**:
  - Test `get_tdi_service_offerings("chemical_risk")` -> assert first returned service has `service_id == "tdi-srv-chemical-audit"`.

## 5. Verification Strategy
- Run `pytest tests/test_server.py -v` to ensure all tests pass.
- Verify that tests correctly handle and mock out any dependencies if needed, though `server.py` is entirely in-memory and deterministic, so it can be tested as-is.

## 6. Questions & Decisions for Human Approval

### a. Question
Should we use `pytest-asyncio` for testing the server tools, or test the synchronous python functions directly?

### b. Brief Background
The tools in `server.py` are implemented as standard synchronous Python functions (e.g., `def list_regulatory_updates(...)`). While FastMCP can wrap these in an async context when running as an MCP server, the underlying Python implementation in `server.py` is fully synchronous. Testing the functions directly is simpler, but testing via an MCP client simulator might offer more integration-level confidence.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Test the synchronous Python functions directly by importing them from `server.py`.
- **Option 2 (Approved)**: Instantiate a mock FastMCP client and invoke the tools asynchronously to test the full MCP lifecycle.

### d. Justification of the Recommendation
Option 1 is highly recommended because the Acceptance Criteria specifically asks to "Test date-window filtering", "Test keyword matching", etc. in `tests/test_server.py`. Testing the core logic directly avoids the overhead of setting up async client/server harnesses, runs extremely fast, and precisely isolates the business logic of the 5 tools which are already purely synchronous.

**User Decision**: The user explicitly approved proceeding with **Option 2**. We will instantiate a mock FastMCP client (using FastMCP's built-in testing capabilities or an async client) and invoke the tools asynchronously in the tests.

