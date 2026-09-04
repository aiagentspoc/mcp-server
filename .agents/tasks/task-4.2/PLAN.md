## 1. Context & Task Scope
Task 4.2 focuses on verifying the interactive functionality of the MCP tools and ensuring that the `stdio` transport is free from console noise. This is critical because standard output (`stdout`) is strictly reserved for JSON-RPC communication in the `stdio` transport, and any extraneous prints or logs will break protocol parsers.

## 2. Prerequisites
- Completion of Phase 1, 2, and 3 (Schemas, Fixtures, Tools).
- Completion of Task 4.1 (Automated Test Suite).
- `fastmcp` CLI installed and available via `uv`.

## 3. Objectives
- Verify that standard logging and any potential standard output noise are explicitly directed to `stderr` when running the server, preserving `stdout` for MCP protocol messages.
- Ensure that `uv run fastmcp dev server.py` functions correctly, exposing all 5 tools to the MCP Inspector.
- Mark Task 4.2 as complete in `ROADMAP.md`.

## 4. Proposed Changes & Specifications
1. **`server.py`**:
   - Add explicit logging configuration at the top of the file to direct all root logs to `sys.stderr`. Although `fastmcp` handles `stdio` transport routing, explicitly configuring `logging.basicConfig(stream=sys.stderr, level=logging.INFO)` guarantees zero `stdout` pollution from any imported modules or internal logs.
2. **`ROADMAP.md`**:
   - Update the task status for 4.2 from `[ ]` to `[x]`.

## 5. Verification Strategy
- **Stdio Noise Test**: Run `python server.py` programmatically in a subprocess, send a valid JSON-RPC initialization request to `stdin`, and verify that the `stdout` response contains *only* valid JSON-RPC, with all other logs appearing on `stderr`.
- **Inspector Readiness**: Start `uv run fastmcp dev server.py` in the background and verify it binds to its port without crashing, ensuring the interactive web inspector works.

## 6. Questions & Decisions for Human Approval

### a. Question
Should we introduce an explicit `logging` configuration in `server.py` to guarantee `stderr` redirection, or rely solely on `fastmcp`'s default stdio handling?

### b. Brief Background
The MCP protocol over `stdio` requires that `stdout` strictly contains JSON-RPC messages. Extraneous logs on `stdout` will break client parsers. `fastmcp` generally handles this, but third-party dependencies might accidentally print to `stdout` unless explicitly intercepted or configured.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Explicitly configure Python's `logging` module to use `sys.stderr` at the top of `server.py`. This is a defensive approach that guarantees no standard library logging pollutes `stdout`.
- **Option 2**: Do not change `server.py` and rely on `fastmcp`'s internal stdio transport handling, testing it purely via subprocess simulation.

### d. Justification of the Recommendation
Option 1 is recommended because it is a zero-cost defensive measure that prevents future regressions if new libraries with default logging are added.

