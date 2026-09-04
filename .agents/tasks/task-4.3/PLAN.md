# Implementation Plan: Task 4.3 (Code Quality & Security Audit)

## 1. Context & Task Scope
Task 4.3 requires conducting a code quality and security audit on the FastMCP server (`server.py`) according to the `code-reviewer` guidelines. This involves enforcing strict typing, input sanitization, and error resilience to ensure the server handles edge cases securely and deterministically without crashing.

## 2. Prerequisites
- Tasks 1.1 through 4.2 must be complete.
- The `server.py` file must be fully functional with the 5 core MCP tools implemented.

## 3. Objectives
- Improve input validation and sanitization for all exposed MCP tool endpoints.
- Ensure strict typing for all tool arguments.
- Handle edge cases gracefully to provide error resilience.
- Fix any identified logical bugs (e.g., `sector` filtering in `get_tdi_service_offerings`).

## 4. Proposed Changes & Specifications

### `server.py`
We will apply the following enhancements to the tool functions:

1. **`list_regulatory_updates`**:
   - Add input sanitization for `limit`: `limit = max(1, min(limit, 50))` to prevent memory exhaustion or large payload overhead.
   - Add regex-based format validation for `date_from` and `date_to` to ensure they strictly follow the ISO 8601 `YYYY-MM-DD` format. Raise a clear `ValueError` if the format is invalid.

2. **`search_regulatory_docs`**:
   - Sanitize the `query` input: `query = query.strip()`.
   - If the `query` is empty after stripping, return an empty list immediately to prevent matching all documents unintentionally.

3. **`get_document_by_id`**:
   - Sanitize the `doc_id` input: `doc_id = doc_id.strip()`.
   - Ensure the function robustly raises `ValueError` when not found (already implemented, but we will ensure the error message is clean).

4. **`verify_legal_citation`**:
   - Sanitize the `citation` input: `citation = citation.strip()`.
   - If the `citation` is empty, return an "unrecognized" `CitationVerificationResult` immediately.

5. **`get_tdi_service_offerings`**:
   - Sanitize the `topic` input: `topic = topic.strip()`.
   - **Bug Fix**: The current implementation for `sector` matching is flawed. It checks `if value in item.lower()` where `value` is the `topic`. We will correct this to match `sector.lower()` against the items in `service.applicable_sectors` if a `sector` argument is provided.

## 5. Verification Strategy
- **Unit Testing**: Run `uv run pytest` to ensure that existing assertions (e.g., in `tests/test_server.py`) remain green.
- **Static Analysis**: Run `uv run mypy server.py` (if installed) or rely on IDE-level static type checking to verify strict typing compliance.
- **Edge Case Validation**: Ensure deterministic responses by testing edge cases (e.g., negative limits, malformed dates, empty strings) interactively or via test scripts to confirm they do not cause unhandled exceptions or latency spikes (>15ms).

## 6. Questions & Decisions for Human Approval

### a. Question
How should we handle invalid date formats in `list_regulatory_updates`?

### b. Brief Background
Currently, `date_from` and `date_to` are strings. The specification requires `YYYY-MM-DD`. If a client passes an invalid format (e.g., `DD/MM/YYYY` or random text), we need a resilient way to handle it.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Raise a descriptive `ValueError` (e.g., "Invalid date format. Expected YYYY-MM-DD.") allowing the MCP client to surface the error clearly to the agent.
- **Option 2**: Ignore invalid date filters silently and return unfiltered results.
- **Option 3**: Attempt to parse and auto-correct common date formats.

### d. Justification of the Recommendation
Option 1 is recommended because it adheres to "fail fast" and "error resilience" principles. Silently ignoring filters (Option 2) could lead to incorrect agent assumptions, and auto-correcting (Option 3) adds unnecessary complexity and potential non-determinism, violating the strict requirements.

