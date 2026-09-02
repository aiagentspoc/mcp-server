# Walkthrough - Task 2.3: Commercial Services & CTAs (`fixtures/tdi_services.json`)

## 1. Overview
In Task 2.3, we established the **TDI Commercial Services & Call-to-Action Catalog** (`fixtures/tdi_services.json`) for the HSE Easy Mock MCP Server. This deterministic seed dataset powers the downstream MCP tool `get_tdi_service_offerings`, allowing automated Writer and Assembly agents to append tailored, high-converting Call-to-Action (CTA) blocks, value propositions, and direct booking URLs to synthesized regulatory articles and briefing memos.

---

## 2. Changes Summary

### 2.1 Commercial Service Catalog (`fixtures/tdi_services.json`)
- **Total Offerings**: 5 pre-seeded commercial consulting and training services adhering to [`TDIServiceOffering`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py#L142-L179):
  1. `tdi-srv-preposti-training`:
     - **Service Name**: Corso di Formazione e Aggiornamento Preposti (D.Lgs. 81/08)
     - **Topic Category**: `workplace_safety`
     - **Applicable Sectors**: `construction`, `manufacturing`, `logistics`, `services`, `plant_engineering`
     - **CTA Headline**: *"Adeguati ai nuovi obblighi formativi per i Preposti prima delle verifiche ispettive."*
     - **Landing Page**: `https://www.tdigroup.it/servizi/formazione-sicurezza-preposti`
  2. `tdi-srv-chemical-audit`:
     - **Service Name**: Audit di Conformità Rischio Chimico e Sostanze CMRD
     - **Topic Category**: `chemical_risk`
     - **Applicable Sectors**: `chemical`, `pharmaceutical`, `manufacturing`, `automotive`, `metalworking`, `waste_management`
     - **CTA Headline**: *"Aggiorna la valutazione rischio chimico e i valori limite biologici con i tecnici TDI."*
     - **Landing Page**: `https://www.tdigroup.it/servizi/audit-rischio-chimico-cmrd`
  3. `tdi-srv-machinery-ce`:
     - **Service Name**: Consulenza Nuovo Regolamento Macchine (UE) 2023/1230 e Marcatura CE
     - **Topic Category**: `machinery`
     - **Applicable Sectors**: `machinery_manufacturing`, `industrial_automation`, `robotics`, `metalworking`, `packaging`
     - **CTA Headline**: *"Verifica la conformità del tuo parco macchine al nuovo Regolamento UE 2023/1230."*
     - **Landing Page**: `https://www.tdigroup.it/servizi/consulenza-regolamento-macchine-ce`
  4. `tdi-srv-heat-stress`:
     - **Service Name**: Protocollo Valutazione Rischio Microclima e Stress da Calore
     - **Topic Category**: `heat_stress`
     - **Applicable Sectors**: `construction`, `agriculture`, `foundry`, `logistics`, `road_works`, `outdoor_activities`
     - **CTA Headline**: *"Proteggi i tuoi lavoratori all'aperto: richiedi il protocollo anti-calore personalizzato."*
     - **Landing Page**: `https://www.tdigroup.it/servizi/valutazione-microclima-stress-termico`
  5. `tdi-srv-fire-safety`:
     - **Service Name**: Consulenza Antincendio e Piani di Emergenza (D.M. GSA e Minispazi)
     - **Topic Category**: `fire_safety`
     - **Applicable Sectors**: `manufacturing`, `high_risk_plants`, `logistics`, `chemical`, `commercial_activities`, `all_sectors`
     - **CTA Headline**: *"Allinea la gestione antincendio aziendale ai Decreti Ministeriali 2021."*
     - **Landing Page**: `https://www.tdigroup.it/servizi/consulenza-antincendio-piani-emergenza`

### 2.2 Test Suite Expansion (`tests/test_fixtures.py`)
Added 7 dedicated automated unit test functions in `tests/test_fixtures.py`:
1. `test_tdi_services_fixture_exists_and_is_valid_json`: Validates file existence and JSON array integrity ($\ge 4$ offerings).
2. `test_tdi_services_pydantic_hydration`: Verifies 100% of records instantiate cleanly as `TDIServiceOffering`.
3. `test_tdi_services_expected_identifiers`: Confirms uniqueness and presence of all expected service IDs.
4. `test_tdi_services_mandatory_roadmap_cases`: Asserts presence of the 4 mandatory roadmap services.
5. `test_tdi_services_field_constraints_and_non_empty`: Enforces string length constraints, valid `https://` URLs, and minimum 2 target sectors per offering.
6. `test_tdi_services_topic_and_sector_matching_simulation`: Simulates downstream MCP tool matching logic across multiple topic domains and industry sectors.
7. `test_tdi_services_fallback_behavior_simulation`: Confirms deterministic single-offering fallback (`tdi-srv-preposti-training`) for unmatched queries.

### 2.3 Roadmap Synchronization (`ROADMAP.md`)
- Marked Task 2.3 and Phase 2 items as completed in both the Gantt chart and task list.

---

## 3. Verification Results

### 3.1 Automated Test Execution
```bash
uv run pytest -v
```
**Results**:
- `tests/test_fixtures.py`: 19 passed (6 regulatory docs, 6 legal citations, 7 TDI commercial services)
- `tests/test_models.py`: 88 passed
- **Total**: 107 passed in 0.43s with 0 failures and 0 warnings.

---

## 4. Next Steps
Proceeding directly to **Stage 3: Parallel Review** with `architect` and `qa` subagents.
