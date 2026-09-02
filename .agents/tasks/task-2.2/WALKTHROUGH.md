# Walkthrough - Task 2.2: Legal Citations Registry (`fixtures/citations.json`)

## 1. Overview
In Task 2.2, we established the **Legal Citations Registry** (`fixtures/citations.json`) for the HSE Easy Mock MCP Server. This deterministic seed dataset provides authoritative legal reference verification, canonical citations, official portal URLs (Normattiva, EUR-Lex, INAIL, Gazzetta Ufficiale), and comprehensive multi-alias lookup indexes for the downstream MCP tool `verify_legal_citation`.

---

## 2. Changes Summary

### 2.1 Legal Citation Registry (`fixtures/citations.json`)
- **Total Citations**: 18 pre-seeded legal entries covering EU directives/regulations, Italian legislative decrees, ministerial decrees, and historical repealed safety norms.
- **Active & Amended HSE Provisions**:
  - `D.Lgs. 81/2008 Art. 37`: Preposti biennial training update under D.L. 19/2024 (`is_valid: true`, `status: "in_force"`, linked to `gu-2024-dl-preposti`).
  - `D.Lgs. 81/2008 Art. 18`: Formal written appointment of preposti in contracting (`is_valid: true`, `status: "in_force"`, linked to `gu-2024-dl-preposti`).
  - `D.Lgs. 81/2008 Art. 19`: Preposti power to halt non-compliant operations (`is_valid: true`, `status: "in_force"`, linked to `gu-2024-dl-preposti`).
  - `Direttiva 2004/37/CE`: Protection against carcinogens, mutagens, and reprotoxic substances (`is_valid: true`, `status: "amended"`, linked to `eurlex-dir-2024-869`).
  - `Direttiva (UE) 2024/869`: Biological limits for lead & diisocyanates (`is_valid: true`, `status: "in_force"`, linked to `eurlex-dir-2024-869`).
  - `Direttiva 98/24/CE`: Chemical agents at work (`is_valid: true`, `status: "amended"`, linked to `eurlex-dir-2024-869`).
  - `Regolamento (UE) 2023/1230 Art. 10`: Manufacturer obligations, digital user manuals, CE marking (`is_valid: true`, `status: "in_force"`, linked to `eurlex-reg-2023-1230`).
  - `Regolamento (UE) 2023/1230`: Base EU Machinery Regulation (`is_valid: true`, `status: "in_force"`, linked to `eurlex-reg-2023-1230`).
  - `Circolare INAIL 28/2024`: Worklimate heat stress protocols (`is_valid: true`, `status: "in_force"`, linked to `inail-2024-circ-calore`).
  - `D.Lgs. 81/2008 Art. 28`: Risk assessment document (DVR) scope (`is_valid: true`, `status: "in_force"`, linked to `inail-2024-circ-calore`).
  - `D.Lgs. 81/2008 Art. 46`: Workplace fire prevention general mandate (`is_valid: true`, `status: "in_force"`, linked to `gu-2023-dm-antincendio`).
  - `D.M. 2 settembre 2021`: Fire safety management (GSA) and emergency plans (`is_valid: true`, `status: "in_force"`, linked to `gu-2023-dm-antincendio`).
  - `D.M. 3 settembre 2021`: Fire safety design criteria / Minispazi (`is_valid: true`, `status: "in_force"`, linked to `gu-2023-dm-antincendio`).
- **Invalid & Repealed Norms**:
  - `D.P.R. 547/55 Art. 10`: Historic accident prevention regulation (`is_valid: false`, `status: "repealed"` by Art. 304 D.Lgs. 81/08).
  - `D.Lgs. 626/94 Art. 3`: Historic workplace safety framework (`is_valid: false`, `status: "repealed"` by Art. 304 D.Lgs. 81/08).
  - `Direttiva 98/37/CE`: Historic machinery directive (`is_valid: false`, `status: "repealed"` by Directive 2006/42/EC).
  - `D.P.R. 303/56 Art. 4`: Historic occupational hygiene rule (`is_valid: false`, `status: "repealed"` by Art. 304 D.Lgs. 81/08).
  - `D.M. 10 marzo 1998`: Historic fire safety criteria (`is_valid: false`, `status: "repealed"` by DM 1, 2, 3 Settembre 2021).
- **Multi-Alias Normalization Index**: Each entry contains an array of normalized variants (spacing variations, punctuation variants like `dlgs` vs `d.lgs.`, `art` vs `art.`, `decreto legislativo`, and Roman/Arabic numerals) preventing citation lookup misses.

### 2.2 Test Suite Expansion (`tests/test_fixtures.py`)
Added 6 dedicated automated test functions to `tests/test_fixtures.py`:
1. `test_citations_fixture_exists_and_is_valid_json`: Validates file existence and JSON array integrity ($\ge 15$ items).
2. `test_citations_pydantic_hydration`: Ensures 100% of records instantiate into `CitationVerificationResult` with zero schema errors.
3. `test_citations_required_fields_and_enums`: Validates field constraints, enum literals (`"in_force"`, `"amended"`, `"repealed"`), official URLs, and minimum alias counts.
4. `test_citations_mandatory_roadmap_cases`: Verifies exact expected status and boolean validity for all 8 mandatory roadmap test cases.
5. `test_citations_relational_integrity_with_regulatory_docs`: Confirms that all `verified_against_doc_id` references map to existing `doc_id` values in `fixtures/regulatory_docs.json`.
6. `test_citations_alias_uniqueness_and_normalization_simulation`: Asserts that alias mappings across entries are unique (no collisions) and proves simulated lookup normalization matches messy queries.

---

## 3. Verification Results

### 3.1 Automated Test Execution
```bash
uv run pytest -v
```
**Results**:
- `tests/test_fixtures.py`: 12 passed
- `tests/test_models.py`: 88 passed
- **Total**: 100 passed in 0.54s with 0 failures and 0 warnings.

---

## 4. Next Steps
Automatically transitioning to **Stage 3: Parallel Review** with `architect` and `qa` subagents.
