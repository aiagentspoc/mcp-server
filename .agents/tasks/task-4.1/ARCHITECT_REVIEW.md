# Architect Review: Task 4.1 (`tests/test_server.py`)

## 1. System Boundaries
**Status:** Pass.
The tests correctly treat the MCP server as a bounded system. By importing the `mcp` instance from `server.py` and calling tools directly via `mcp.call_tool()`, the tests accurately simulate client interactions over the MCP protocol without relying on internal function calls.

## 2. FastMCP Lifecycle
**Status:** Pass.
Test cases correctly utilize `pytest.mark.asyncio` to execute async operations, and cleanly `await mcp.call_tool(...)` simulating the request-response lifecycle of FastMCP tools.

## 3. Pydantic v2 Schemas
**Status:** Pass.
The tests fetch the output as raw JSON via the `extract_json` helper and perform assertions on the serialized dictionaries. This correctly validates that the underlying Pydantic v2 schemas serialize into the expected JSON shape required by the MCP protocol.

## 4. Clean Architecture
**Status:** Pass.
The test code avoids directly importing `REGULATORY_DOCS` or other internal state fixtures, keeping a decoupled architectural boundary. Assertions are based strictly on what is returned through the interface.

## 5. Coding Conventions
**Status:** Pass.
Code is clean, concise, and uses standard Python/pytest practices. Edge cases such as non-existent documents are covered, and `pytest.raises` is used cleanly with a check for FastMCP's `is_error` wrapper logic.

## Conclusion
The implementation is approved. No architectural fixes are necessary.
