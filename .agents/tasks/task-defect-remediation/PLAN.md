# Implementation Plan: Defect Remediation & Technical Debt Resolution

## 1. Context & Task Scope

The **HSE Easy Mock MCP Server** is a deterministic, protocol-compliant local data service designed to provide regulatory data emulation, citation verification, and commercial service conversion for Strands AI agents across two core pipelines: POC A (Content Factory) and POC B (Research Analyst).

A rigorous inspection of the codebase, design specifications ([`ARCHITECTURE.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md), [`SPECIFICATIONS.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md), [`ROADMAP.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md)), and test suites revealed concrete technical defects, missing boundary handling, and test-isolation issues:

1. **Citation Result Identity Defect**:
   - `SPECIFICATIONS.md` § 3.3 defines `CitationVerificationResult.citation_input` as *"The raw citation text submitted for verification"*.
   - When an alias or normalized query matches an index entry, returning the indexed fixture instance directly overwrites the user's submitted input with the fixture's canonical `citation_input`. The server must return a shallow copy updating `citation_input` to the raw/trimmed input submitted by the caller via `matched.model_copy(update={"citation_input": citation})`.
2. **Citation Alias Collision Safety**:
   - The startup alias indexing must not silently overwrite duplicate keys across different citations.
   - Startup indexing must normalize canonical inputs and aliases using `strip().lower()` and perform fail-fast validation: raising an explicit startup `ValueError` if an alias key collides with a different canonical citation.
3. **Citation `source` Parameter Inconsistency**:
   - `verify_legal_citation` exposes `source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None` in its public signature, but `server.py` never uses it.
   - The baseline recommended approach documents this parameter as an intentional backward-compatible no-op. All source-mapping and fixture-source metadata work is strictly conditional upon human approval of Decision 1 Option 2. In all options, the public `CitationVerificationResult` response schema remains unchanged.
4. **TDI Commercial Service Matching Divergence**:
   - `get_tdi_service_offerings` currently enforces `if t_lower not in service.topic_category.lower(): continue`, preventing sector matching unless `topic` also matches `topic_category`.
   - The public signature requires `topic: str`. Sector-only requests must be precisely specified as `topic="", sector="<sector>"`.
   - The matching logic must implement deterministic scored-union semantics with fixture-order tie-breaking and fallback.
5. **In-Memory Indexing & Structural Debt**:
   - `ARCHITECTURE.md` § 2.2 mandates in-memory dictionaries and lookup tables. Currently, `server.py` performs linear scans and per-request lowercasing loops.
   - Indexes must be directly consumed by real lookup algorithms; unused structures (such as `SERVICES_BY_ID`) will not be introduced.
6. **Broken Package Entry Point**:
   - `pyproject.toml` declares `hse-easy-mock = "server:main"`, but `server.py` lacks a `main` function.
7. **Strict Hyphenated ISO Date Validation**:
   - Date filtering currently uses a regex that admits invalid calendar dates (e.g. `2024-99-99`) and does not prevent inverted ranges (`date_from > date_to`).
   - Using `date.fromisoformat()` alone accepts unhyphenated compact strings (e.g. `"20240101"`). The validation must strictly enforce canonical hyphenated ISO dates by requiring both successful parsing and `date_str == parsed.isoformat()`.
8. **Test Gaps, Protocol Flow & Simulation Smells**:
   - `tests/test_server.py` does not test combined filters, boundaries, invalid dates, alias variations, or MCP error results.
   - MCP error handling must distinguish between a direct-function `ValueError` and an MCP protocol error result (`is_error=True`).
   - `tests/test_fixtures.py` duplicates production search and fallback logic via local mocks instead of asserting against registered MCP tools.
   - Console-script execution must be tested via live subprocess communication.
   - The live stdio protocol test must cover the complete lifecycle: `initialize` $\rightarrow$ `notifications/initialized` $\rightarrow$ `tools/list` (asserting all 5 tools) $\rightarrow$ `tools/call` (asserting result payload and stdout cleanliness).
   - Latency benchmarks must isolate index construction ($<50\text{ ms}$) from Python interpreter startup, and in-process tool latency ($<15\text{ ms}$) from stdio transport latency.

### Factual Inventory of Seed Fixtures
Inspection of the actual fixture files in `fixtures/` establishes the verified ground truth:
- **`fixtures/regulatory_docs.json`**: Exactly **5** documents (`eurlex-dir-2024-869`, `eurlex-reg-2023-1230`, `gu-2024-dl-preposti`, `gu-2023-dm-antincendio`, `inail-2024-circ-calore`).
- **`fixtures/citations.json`**: Exactly **18** citation records (including valid, amended, and repealed provisions with comprehensive alias arrays).
- **`fixtures/tdi_services.json`**: Exactly **5** commercial service offerings:
  1. `tdi-srv-preposti-training` (Mandatory baseline)
  2. `tdi-srv-chemical-audit` (Mandatory baseline)
  3. `tdi-srv-machinery-ce` (Mandatory baseline)
  4. `tdi-srv-heat-stress` (Mandatory baseline)
  5. `tdi-srv-fire-safety` (Seeded for fire safety decree compliance)

**Scope & Fixture Immutability Boundary**:
Fixture datasets in `fixtures/` remain unchanged unless human approval explicitly selects Decision 1 Option 2, which authorizes adding internal, non-public source metadata to `fixtures/citations.json`. No source code, tests, or documentation outside this plan will be modified in this task.

---

## 2. Prerequisites

1. **Tooling & Environment**: Python 3.10+ managed via `uv`. Dependencies declared in `pyproject.toml`: `fastmcp>=0.1.0`, `pydantic>=2.0.0`, `pytest>=8.0.0`, `pytest-asyncio>=0.23.0`, and `pytest-benchmark>=4.0.0`.
2. **Design Specifications**:
   - [`ARCHITECTURE.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md) (v1.0.0)
   - [`SPECIFICATIONS.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md) (v1.0.0)
   - [`ROADMAP.md`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md) (Phases 1–5)
3. **Fixture Baseline**: The 5 regulatory documents, 18 citations, and 5 TDI services in `fixtures/` remain authoritative and unchanged, unless Decision 1 Option 2 is approved.
4. **Approval**: Section 6 human decision on the citation `source` parameter must be confirmed before Stage 2 implementation.

---

## 3. Objectives

1. **Correct Citation Verification Return Value**: Return `matched.model_copy(update={"citation_input": citation})` on matched queries, preserving the caller's exact raw/trimmed input in `citation_input` while retaining all verified canonical metadata from the matched fixture record.
2. **Implement Fail-Fast Citation Alias Indexing**: Build an in-memory O(1) hash map `CITATIONS_BY_ALIAS` that normalizes keys with `strip().lower()` and raises an explicit `ValueError` at server startup if any alias collides with a different canonical citation.
3. **Implement Scored-Union TDI Matching**: Support topic-only, sector-only (`topic=""`, `sector="<sector>"`), and combined queries with a deterministic scoring algorithm, fixture-order tie-breaking, and fallback to `tdi-srv-preposti-training`.
4. **Deploy Consumed In-Memory Indexes**: Build O(1) hash maps for documents and citations and preprocessed search structures for services at startup. Eliminate unused structures (such as `SERVICES_BY_ID`). Ensure index construction takes $<50\text{ ms}$ and in-process tool calls take $<15\text{ ms}$.
5. **Fix Console Script Entry Point**: Add `def main(): mcp.run()` in `server.py` while ensuring all server logs write strictly to `sys.stderr` to keep `sys.stdout` clean for JSON-RPC stdio transport.
6. **Implement Strict Hyphenated ISO Calendar Validation**: Validate dates using `date.fromisoformat()` and assert `date_str == parsed.isoformat()`, strictly rejecting compact forms (e.g. `"20240101"`), invalid calendars (e.g. `"2024-99-99"`), and inverted ranges (`date_from > date_to`).
7. **Resolve the Citation `source` Parameter**: Baseline recommended implementation treats `source` as an explicit, documented backward-compatible no-op. Conditional source-mapping and fixture metadata are reserved exclusively for Decision 1 Option 2. Preserve `CitationVerificationResult` schema in all options.
8. **Complete & Deduplicate the Test Suite**:
   - Eliminate mock simulations from `tests/test_fixtures.py`.
   - Separate direct function `ValueError` tests from MCP-boundary error result tests.
   - Add a live subprocess test for `hse-easy-mock`.
   - Implement full stdio protocol sequence testing (`initialize` $\rightarrow$ `notifications/initialized` $\rightarrow$ `tools/list` $\rightarrow$ `tools/call`).
   - Add dedicated benchmarks isolating in-process tool latency from stdio transport latency and startup index construction from interpreter boot.

---

## 4. Proposed Changes & Specifications

### 4.1. Core Server & Indexing (`server.py`)

#### A. Entry Point & stdio Preservation
- **File**: [`server.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/server.py)
- **Changes**:
  Expose a top-level `main()` callable required by `pyproject.toml` (`hse-easy-mock = "server:main"`):
  ```python
  def main() -> None:
      """Entry point for the hse-easy-mock console script and stdio transport execution."""
      mcp.run()

  if __name__ == "__main__":
      main()
  ```
  Ensure `logging.basicConfig(stream=sys.stderr, level=logging.INFO, force=True)` directs all server logs to stderr, preserving stdout strictly for JSON-RPC.

#### B. Strict Hyphenated ISO Date Validation
- **File**: [`server.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/server.py)
- **Specification**:
  Reject compact ISO dates (`"20240101"`), non-calendar dates (`"2024-99-99"`, `"2024-02-31"`), and non-canonical forms by verifying `date_str == parsed.isoformat()`:
  ```python
  from datetime import date

  def validate_strict_iso_date(date_str: str, param_name: str) -> date:
      """
      Validate that date_str is a strict canonical hyphenated ISO 8601 date (YYYY-MM-DD).
      Rejects compact forms (e.g. '20240101'), non-padded components, and invalid calendar dates.
      """
      try:
          parsed = date.fromisoformat(date_str)
      except (ValueError, TypeError):
          raise ValueError(
              f"Invalid {param_name} date format: '{date_str}'. Expected valid calendar date in YYYY-MM-DD format."
          )
      if date_str != parsed.isoformat():
          raise ValueError(
              f"Invalid {param_name} date format: '{date_str}'. Expected strict hyphenated YYYY-MM-DD format."
          )
      return parsed
  ```
  In `list_regulatory_updates`:
  ```python
  d_from = validate_strict_iso_date(date_from, "date_from") if date_from else None
  d_to = validate_strict_iso_date(date_to, "date_to") if date_to else None

  if d_from and d_to and d_from > d_to:
      raise ValueError(f"date_from ({date_from}) cannot be after date_to ({date_to}).")
  ```

#### C. In-Memory Indexes (Startup Lifecycle & Alias Collision Safety)
- **File**: [`server.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/server.py)
- **Specification**:
  Hydrate models and build consumed lookup tables during server initialization. Enforce fail-fast alias collision checks:
  ```python
  # 1. Documents: Hydrate Pydantic models
  with open(FIXTURES_DIR / "regulatory_docs.json", encoding="utf-8") as f:
      REGULATORY_DOCS: list[RegulatoryDocument] = [RegulatoryDocument(**d) for d in json.load(f)]

  # O(1) direct lookup by document slug
  DOCS_BY_ID: dict[str, RegulatoryDocument] = {doc.doc_id: doc for doc in REGULATORY_DOCS}

  # Pre-sorted list by publication date descending for deterministic list_regulatory_updates
  DOCS_ORDERED_BY_DATE: list[RegulatoryDocument] = sorted(
      REGULATORY_DOCS, key=attrgetter("publication_date"), reverse=True
  )

  # 2. Citations: Hydrate Pydantic models & build fail-fast collision-safe O(1) alias index
  with open(FIXTURES_DIR / "citations.json", encoding="utf-8") as f:
      CITATIONS_DATA = json.load(f)

  CITATIONS_BY_ALIAS: dict[str, CitationVerificationResult] = {}

  for entry in CITATIONS_DATA:
      res = CitationVerificationResult(
          citation_input=entry["citation_input"],
          is_valid=entry["is_valid"],
          status=entry["status"],
          canonical_citation=entry["canonical_citation"],
          official_reference=entry.get("official_reference"),
          official_url=entry.get("official_url"),
          verified_against_doc_id=entry.get("verified_against_doc_id"),
          notes=entry.get("notes"),
      )
      
      all_keys = [entry["citation_input"]] + entry.get("aliases", [])
      for raw_key in all_keys:
          norm_key = raw_key.strip().lower()
          if norm_key in CITATIONS_BY_ALIAS:
              existing = CITATIONS_BY_ALIAS[norm_key]
              if existing.canonical_citation != res.canonical_citation:
                  raise ValueError(
                      f"Startup citation alias collision: key '{norm_key}' maps to both "
                      f"'{existing.canonical_citation}' and '{res.canonical_citation}'."
                  )
          CITATIONS_BY_ALIAS[norm_key] = res

  # Note: CITATIONS_SOURCE_MAP is omitted from baseline. It is constructed ONLY if Decision 1 Option 2 is selected.

  # 3. TDI Services: Preprocessed structure consumed by search algorithm
  with open(FIXTURES_DIR / "tdi_services.json", encoding="utf-8") as f:
      TDI_SERVICES: list[TDIServiceOffering] = [TDIServiceOffering(**s) for s in json.load(f)]

  class PreprocessedService:
      __slots__ = ("service", "index", "topic_category_lower", "sectors_lower")
      def __init__(self, service: TDIServiceOffering, index: int):
          self.service = service
          self.index = index
          self.topic_category_lower = service.topic_category.lower()
          self.sectors_lower = [sec.lower() for sec in service.applicable_sectors]

  INDEXED_TDI_SERVICES: list[PreprocessedService] = [
      PreprocessedService(s, i) for i, s in enumerate(TDI_SERVICES)
  ]
  FALLBACK_TDI_SERVICE: list[TDIServiceOffering] = [TDI_SERVICES[0]]
  ```
  *(Note: `SERVICES_BY_ID` is omitted as no tool performs lookup by service ID).*

#### D. Tool Remediations

1. **`list_regulatory_updates`**:
   - Validate date strings with `validate_strict_iso_date`.
   - Clamp `limit = max(1, min(limit, 50))`.
   - Filter over `DOCS_ORDERED_BY_DATE` using date string comparison (strict canonical format allows lexicographical comparison).
   - Downcast and return summaries projected via `to_summary()`.

2. **`search_regulatory_docs`**:
   - Clean query: `q = query.strip().lower()`. If empty, return `[]`.
   - Clean topic: `t = topic.strip().lower() if topic else None`.
   - Match across `title`, `summary`, `official_reference`, and `topic_tags`.
   - Return summaries projected via `to_summary()`.

3. **`get_document_by_id`**:
   - Strip input: `clean_id = doc_id.strip()`.
   - Direct lookup in `DOCS_BY_ID`.
   - If not found, raise `ValueError(f"Document with ID '{doc_id}' not found.")`.

4. **`verify_legal_citation`**:
   - Clean input: `normalized = citation.strip().lower()`.
   - If `not normalized`:
     Return `CitationVerificationResult(citation_input=citation, is_valid=False, status="unrecognized", canonical_citation="", notes="Empty citation provided.")`.
   - Lookup in `CITATIONS_BY_ALIAS`.
   - If found:
     Return a shallow copy updating `citation_input` to the user's submitted string:
     ```python
     matched = CITATIONS_BY_ALIAS[normalized]
     return matched.model_copy(update={"citation_input": citation})
     ```
   - If not found:
     Return `CitationVerificationResult(citation_input=citation, is_valid=False, status="unrecognized", canonical_citation=citation, notes="Citation not recognized in authoritative legal registry.")`.
   - Baseline behavior treats `source` as a documented backward-compatible no-op. (Conditional exact-equality filtering is applied only if Decision 1 Option 2 is chosen).

5. **`get_tdi_service_offerings`**:
   - Signature: `topic: str`, `sector: Optional[str] = None`.
   - Normalize: `t_query = topic.strip().lower()`, `s_query = sector.strip().lower() if sector else ""`.
   - Sector-only request: Caller supplies `topic=""` and non-empty `sector`.
   - Matching & Scoring Algorithm:
     ```python
     if not t_query and not s_query:
         return FALLBACK_TDI_SERVICE

     scored_candidates: list[tuple[int, int, TDIServiceOffering]] = []

     for item in INDEXED_TDI_SERVICES:
         score = 0
         # Topic evaluation (category or applicable sectors)
         if t_query:
             if t_query in item.topic_category_lower:
                 score += 2
             elif any(t_query in sec for sec in item.sectors_lower):
                 score += 1

         # Sector evaluation
         if s_query and any(s_query in sec for sec in item.sectors_lower):
             score += 1

         if score > 0:
             scored_candidates.append((score, item.index, item.service))

     if not scored_candidates:
         return FALLBACK_TDI_SERVICE

     # Sort: primary key = -score (descending), tie-breaker = index (ascending fixture order)
     scored_candidates.sort(key=lambda c: (-c[0], c[1]))
     return [c[2] for c in scored_candidates]
     ```

---

### 4.2. Configuration & Packaging (`pyproject.toml`)

- **File**: [`pyproject.toml`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/pyproject.toml)
- Verify console script definition:
  ```toml
  [project.scripts]
  hse-easy-mock = "server:main"
  ```
- Verify hatchling wheel build targets explicitly include `server.py`, `models.py`, and `fixtures`.

---

### 4.3. Test Suite Remediation & Expansion

#### A. Tool Unit & Integration Tests (`tests/test_server.py`)
- **File**: [`tests/test_server.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_server.py)
- **New & Remediated Tests**:
  1. `test_tools_list_schema_inspection`:
     - Introspect `mcp.list_tools()`. Assert all 5 tools are exposed.
     - Assert descriptions are non-empty strings (>20 chars).
     - Assert input schemas define expected property names and types.
  2. `test_list_regulatory_updates_matrix`:
     - Default call returns up to 10 items in descending order of `publication_date`.
     - Limit boundaries: `limit=1` returns 1 item; `limit=100` clamped to 50; `limit=0` clamped to 1.
     - Date filtering: valid date window returns expected subset.
     - Tier 1 projection: assert keys in return objects match `RegulatoryUpdateSummary` and exclude Tier 2 fields (`content_markdown`, `key_obligations`, etc.).
  3. `test_list_regulatory_updates_strict_date_validation`:
     - Compact ISO dates: `"20240101"` raises `ValueError`.
     - Non-calendar dates: `"2024-99-99"`, `"2024-02-31"` raise `ValueError`.
     - Non-padded dates: `"2024-1-1"` raises `ValueError`.
     - Inverted date range: `date_from="2024-12-31", date_to="2024-01-01"` raises `ValueError`.
  4. `test_search_regulatory_docs_matrix`:
     - Keyword query matching `title`, `summary`, `official_reference`, and `topic_tags`.
     - Combined filters: `query="calore", source="INAIL", topic="construction_safety"`.
     - Case insensitivity: `"PREPOSTI"` vs `"preposti"`.
     - Empty query: `query=""` and `query="   "` return `[]`.
     - Unmatched query returns `[]`.
  5. `test_get_document_by_id_success`:
     - Query each of the 5 valid IDs (`eurlex-dir-2024-869`, etc.) and assert returned fields validate as `RegulatoryDocument`.
     - Whitespace handling: `"  gu-2024-dl-preposti  "` successfully resolves.
  6. `test_get_document_by_id_error_direct_function`:
     - Directly call underlying function:
       ```python
       with pytest.raises(ValueError, match="Document with ID 'non-existent-id' not found."):
           get_document_by_id("non-existent-id")
       ```
  7. `test_get_document_by_id_error_mcp_boundary`:
     - Call via `mcp.call_tool("get_document_by_id", {"doc_id": "non-existent-id"})`.
     - Assert result exhibits MCP error behavior (`result.is_error is True` and error message contains `"Document with ID 'non-existent-id' not found."`).
  8. `test_verify_legal_citation_identity_and_aliases`:
     - Query alias `"dlgs 81/08 art 37"`: assert `result.citation_input == "dlgs 81/08 art 37"`, `result.is_valid is True`, `result.canonical_citation == "D.Lgs. 9 aprile 2008, n. 81, Art. 37 (Formazione dei lavoratori e dei loro rappresentanti)"`.
     - Query canonical `"D.Lgs. 81/2008 Art. 37"`: assert `result.citation_input == "D.Lgs. 81/2008 Art. 37"`.
     - Query repealed citation `"D.Lgs. 626/94 Art. 3"`: assert `result.is_valid is False` and `result.status == "repealed"`.
     - Query unknown citation `"Legge Fantasma 99/2099"`: assert `result.is_valid is False`, `result.status == "unrecognized"`, `result.canonical_citation == "Legge Fantasma 99/2099"`.
     - Query empty citation `""`: assert `result.is_valid is False`, `result.status == "unrecognized"`.
  9. `test_get_tdi_service_offerings_matrix`:
     - Topic-only: `topic="chemical_risk", sector=None` returns `tdi-srv-chemical-audit`.
     - Sector-only: `topic="", sector="construction"` returns matching services (`tdi-srv-preposti-training` and `tdi-srv-heat-stress`).
     - Topic and sector combined: `topic="workplace_safety", sector="construction"` scores `tdi-srv-preposti-training` first (score 3).
     - Fallback: `topic="unknown_xyz", sector=None` returns `[tdi-srv-preposti-training]`.
     - Both empty: `topic="", sector=None` returns `[tdi-srv-preposti-training]`.

#### B. Fixture Test Deduplication & Collision Integrity (`tests/test_fixtures.py`)
- **File**: [`tests/test_fixtures.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_fixtures.py)
- **Remediations**:
  - Delete `test_server_indexing_loader_simulation` (lines 146–158).
  - Delete `test_citations_alias_uniqueness_and_normalization_simulation` (lines 249–290). Replace with `test_citations_fixture_alias_collision_free` which verifies that across all fixture records, no normalized alias belongs to more than one canonical citation record.
  - Delete `test_tdi_services_topic_and_sector_matching_simulation` (lines 360–413).
  - Delete `test_tdi_services_fallback_behavior_simulation` (lines 415–437).
  - Retain pure fixture integrity tests (JSON validity, Pydantic hydration, field constraints, relational links to documents).

#### C. stdio Protocol Lifecycle & Console Script (`tests/test_stdio.py`)
- **File**: [`tests/test_stdio.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_stdio.py)
- **Remediations**:
  1. `test_stdio_initialize_no_noise`: Retain test verifying initialize handshake produces zero non-JSON noise on stdout.
  2. `test_stdio_full_protocol_lifecycle`:
     - Subprocess runs `sys.executable server.py`.
     - Step 1: Send `initialize` request, read and assert valid JSON-RPC response.
     - Step 2: Send `notifications/initialized` notification.
     - Step 3: Send `tools/list` request, read response, and assert `tools` list contains all 5 registered tools (`list_regulatory_updates`, `search_regulatory_docs`, `get_document_by_id`, `verify_legal_citation`, `get_tdi_service_offerings`).
     - Step 4: Send `tools/call` for `verify_legal_citation` (`citation: "D.Lgs. 81/2008 Art. 37"`), read response, and assert valid result payload.
     - Assert that every line received on stdout across all steps is valid JSON-RPC with zero non-JSON log noise.
     - Clean shutdown via `process.terminate()`.
  3. `test_console_script_entrypoint`:
     - Spawn subprocess running `hse-easy-mock` (or `uv run hse-easy-mock`).
     - Send JSON-RPC `initialize` request.
     - Verify valid JSON-RPC response on stdout.
     - Safely terminate process within 2 seconds.

#### D. Performance & Latency Benchmarks (`tests/test_performance.py`)
- **File**: Create [`tests/test_performance.py`](file:///c:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_performance.py)
- **Specification**:
  Isolate in-memory indexing and tool logic from process startup:
  1. `test_benchmark_startup_indexing`:
     - Benchmark the timing boundary: opening the 3 JSON files, parsing JSON, hydrating Pydantic models, and building `DOCS_BY_ID`, `CITATIONS_BY_ALIAS` (with collision checks), and `INDEXED_TDI_SERVICES`.
     - Assert total duration $< 50\text{ ms}$ (target: typically $< 15\text{ ms}$).
  2. `test_benchmark_in_process_tool_latency`:
     - Benchmark in-process direct invocations of:
       - `list_regulatory_updates`
       - `search_regulatory_docs`
       - `get_document_by_id`
       - `verify_legal_citation`
       - `get_tdi_service_offerings`
     - Over 100 warm iterations, assert mean execution time $< 15\text{ ms}$ per call (target: $< 2\text{ ms}$).
  3. `test_benchmark_stdio_roundtrip_latency`:
     - Start a running `server.py` subprocess.
     - Send 20 sequential JSON-RPC `tools/call` requests over the existing open stdio pipe.
     - Measure mean roundtrip latency per call (excluding subprocess boot). Assert mean roundtrip $< 15\text{ ms}$.

---

## 5. Verification Strategy

### 5.1. Automated Test Pipeline
Execute the following verification sequence:
```powershell
# 1. Syntax & type safety check
uv run python -m py_compile server.py models.py

# 2. Complete unit, integration, and deduplicated fixture test suite
uv run pytest tests/test_server.py tests/test_fixtures.py tests/test_models.py -v

# 3. stdio full protocol lifecycle and console script verification
uv run pytest tests/test_stdio.py -v

# 4. Latency and startup benchmarks
uv run pytest tests/test_performance.py -v --benchmark-columns=min,mean,max
```

### 5.2. Acceptance Criteria Matrix

| Requirement | Acceptance Target | Verification Method |
| :--- | :--- | :--- |
| **Startup Indexing** | $< 50\text{ ms}$ (fixture load to index ready) | `tests/test_performance.py::test_benchmark_startup_indexing` |
| **Tool Response Latency** | $< 15\text{ ms}$ per in-process call | `tests/test_performance.py::test_benchmark_in_process_tool_latency` |
| **Transport Latency** | $< 15\text{ ms}$ over open stdio pipe | `tests/test_performance.py::test_benchmark_stdio_roundtrip_latency` |
| **Citation Return Identity**| `citation_input` preserves raw input | `tests/test_server.py::test_verify_legal_citation_identity_and_aliases` |
| **Alias Collision Safety** | Startup fail-fast `ValueError` | Code inspection & fixture collision test |
| **TDI Sector Matching** | Topic-only, sector-only (`topic=""`), union | `tests/test_server.py::test_get_tdi_service_offerings_matrix` |
| **Strict Date Validation** | Rejects unhyphenated, invalid calendars | `tests/test_server.py::test_list_regulatory_updates_strict_date_validation` |
| **MCP Error Handling** | Direct `ValueError` + MCP error result | `tests/test_server.py::test_get_document_by_id_error_*` |
| **Console Script** | `hse-easy-mock` responds to JSON-RPC | `tests/test_stdio.py::test_console_script_entrypoint` |
| **stdio Lifecycle** | `init` $\rightarrow$ `tools/list` $\rightarrow$ `tools/call` clean | `tests/test_stdio.py::test_stdio_full_protocol_lifecycle` |

---

## 6. Questions & Decisions for Human Approval

### Decision 1: Resolution of the Citation `source` Parameter in `verify_legal_citation`

### a. Question
How should the `source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None` parameter in `verify_legal_citation` be handled in server logic?

### b. Brief Background
The documented tool signature in `SPECIFICATIONS.md` § 4.4 and `ARCHITECTURE.md` § 4.2 defines an optional `source` argument. However:
- `server.py` accepts but ignores `source`.
- `CitationVerificationResult` does not include a `source` field.
- `fixtures/citations.json` entries do not contain source metadata.
- Italian and European legal citations (e.g. *"D.Lgs. 81/2008 Art. 37"*, *"Regolamento (UE) 2023/1230"*, *"Circolare INAIL 28/2024"*) are unambiguous, globally unique identifiers that inherently identify their issuing authority.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Retain `source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None` in the public signature for 100% backward compatibility, but explicitly document in the tool docstring that it is a backward-compatible no-op because legal citations in the registry are globally unique.
  - *Implementation Details*: Baseline implementation builds no source maps. Fixtures remain untouched.
  - *Corresponding Test*: `test_verify_legal_citation_source_noop`: Verifies that passing `source="GAZZETTA_UFFICIALE"`, `source="EUR_LEX"`, or `source=None` for `"D.Lgs. 81/2008 Art. 37"` returns the identical valid citation result.
- **Option 2**: Authorize updating `fixtures/citations.json` to add an internal, fixture-only `source` field to all 18 citation records (without adding `source` to `CitationVerificationResult`, preserving the public response model).
  - *Implementation Details*: At startup, build an internal `CITATIONS_SOURCE_MAP: dict[str, str]` mapping normalized aliases to their internal source. If a caller supplies `source`, enforce exact equality: if the matched citation's source does not match the argument, return `is_valid=False, status="unrecognized", notes="Citation belongs to {record_source}, not {source}."`.
  - *Corresponding Test*: `test_verify_legal_citation_source_filter`: Verifies that passing `source="GAZZETTA_UFFICIALE"` for `"D.Lgs. 81/2008 Art. 37"` succeeds, while passing `source="EUR_LEX"` returns `is_valid=False, status="unrecognized"`.

### d. Justification of the Recommendation
Option 1 preserves the exact documented MCP tool contract and response schema without modifying the baseline `citations.json` fixture dataset. Because legal citations are universally distinct, authority filtering is technically redundant in legal QA workflows.

---

### Decision 2: Sector-Only TDI Matching Invocation Semantics

### a. Question
Should sector-only TDI requests use `topic="", sector="<sector>"` under the existing documented signature `topic: str`, or should `topic` be made optional (`topic: Optional[str] = None`)?

### b. Brief Background
`SPECIFICATIONS.md` § 4.5 defines the signature as:
`get_tdi_service_offerings(topic: str, sector: Optional[str] = None) -> List[TDIServiceOffering]`
Because `topic` is a required string without a default, an agent attempting to match exclusively by industrial sector must provide an empty string for `topic` if the documented signature is strictly preserved.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Retain `topic: str` as documented. Define sector-only requests precisely as `topic="", sector="<sector>"`. The scoring algorithm evaluates `topic` only when `topic.strip()` is non-empty, allowing pure sector queries to score and rank services matching the sector.
  - *Corresponding Test*: `test_get_tdi_services_sector_only`: Calls `get_tdi_service_offerings(topic="", sector="construction")` and asserts that `tdi-srv-preposti-training` and `tdi-srv-heat-stress` are returned.
- **Option 2**: Update the tool signature to `topic: Optional[str] = None, sector: Optional[str] = None`, allowing `get_tdi_service_offerings(sector="construction")`. This requires updating `SPECIFICATIONS.md` § 4.5 and `ARCHITECTURE.md` § 4.2.

### d. Justification of the Recommendation
Option 1 avoids breaking the established MCP tool signature contract expected by existing Strands agent prompt templates and schema validators, while cleanly enabling sector-driven matching via standard empty-string conventions.
