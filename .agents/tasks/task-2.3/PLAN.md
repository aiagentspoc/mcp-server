# Implementation Plan - Task 2.3: Commercial Services & CTAs (`fixtures/tdi_services.json`)

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md#L72-L78), [SPECIFICATIONS.md § 3.4, § 4.5, § 5.3, § 6](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md#L118-L144), and [ARCHITECTURE.md § 2.1, § 4.1, § 4.2](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md#L114-L123), Task 2.3 establishes the **TDI Commercial Services & Call-to-Action Catalog** (`fixtures/tdi_services.json`) for the HSE Easy Mock MCP Server.

This fixture dataset serves as the commercial monetization and lead-conversion substrate for the downstream MCP tool `get_tdi_service_offerings`. It enables the Writer Agent (in POC A) and Assembly Step (in POC B) to seamlessly append relevant, high-converting Call-to-Action (CTA) blocks, value propositions, and direct booking URLs to synthesized regulatory articles and briefing memos.

---

## 2. Prerequisites
- Completion of Phase 1 (Tasks 1.1, 1.2, 1.3) and Phase 2 earlier tasks (Task 2.1: `fixtures/regulatory_docs.json`, Task 2.2: `fixtures/citations.json`).
- Validated Pydantic v2 data models in [`models.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py), specifically [`TDIServiceOffering`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py#L142-L179).
- Existing automated test suite in [`tests/test_fixtures.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_fixtures.py) and [`tests/test_models.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_models.py).

---

## 3. Objectives
1. **Author `fixtures/tdi_services.json`** containing deterministic, production-grade TDI commercial consulting and training offerings:
   - `tdi-srv-preposti-training` (Workplace safety, preposti training & biennial refresher per D.Lgs. 81/08 & L. 215/2021).
   - `tdi-srv-chemical-audit` (Chemical risk, carcinogens, reprotoxic CMRD audit & biological limit compliance per Dir (UE) 2024/869).
   - `tdi-srv-machinery-ce` (EU Machinery Regulation (UE) 2023/1230 compliance, CE marking, AI safety & digital manual transition).
   - `tdi-srv-heat-stress` (Microclimate assessment, thermal heat stress protocols & Worklimate adaptation per Circolare INAIL 28/2024).
   - *(Optional 5th Offering)* `tdi-srv-fire-safety` (Fire risk assessment, emergency management plans & firefighting team certifications per DM 1, 2, 3 Settembre 2021).
2. **Strict Pydantic v2 Schema Compliance**:
   - Ensure each service record strictly validates against [`TDIServiceOffering`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py#L142-L179) with all non-empty required fields: `service_id`, `service_name`, `topic_category`, `applicable_sectors`, `value_proposition`, `cta_headline`, `cta_body`, and `landing_page_url`.
3. **High-Conversion Copywriting**:
   - Craft persuasive, professionally tailored Italian headlines and body copy addressing specific legal liabilities, fines, and operational risks identified in the regulatory acts.
4. **Cross-Corpus Topic Alignment**:
   - Ensure the taxonomy of `topic_category` and `applicable_sectors` maps directly to the topic tags and target sectors across `fixtures/regulatory_docs.json` (`workplace_safety`, `preposti_training`, `chemical_risk`, `cmrd_substances`, `machinery`, `ce_marking`, `heat_stress`, `microclimate`, `fire_safety`).
5. **Comprehensive Test Suite**:
   - Extend [`tests/test_fixtures.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_fixtures.py) with unit tests validating JSON syntax, Pydantic hydration, field constraints, URL formats, topic/sector matching logic simulation, and deterministic fallback behavior.

---

## 4. Proposed Changes & Specifications

### 4.1 Fixture File: `fixtures/tdi_services.json`
Create `fixtures/tdi_services.json` containing the commercial service offerings:

```json
[
  {
    "service_id": "tdi-srv-preposti-training",
    "service_name": "Corso di Formazione e Aggiornamento Preposti (D.Lgs. 81/08)",
    "topic_category": "workplace_safety",
    "applicable_sectors": [
      "construction",
      "manufacturing",
      "logistics",
      "services",
      "plant_engineering"
    ],
    "value_proposition": "Percorsi formativi certificati in presenza e blended per adempiere all'obbligo di aggiornamento biennale dei preposti introdotto dalla Legge 215/2021 e rafforzare le competenze di vigilanza operativa.",
    "cta_headline": "Adeguati ai nuovi obblighi formativi per i Preposti prima delle verifiche ispettive.",
    "cta_body": "La mancata formazione o l'omesso aggiornamento biennale dei preposti comporta sanzioni penali dirette con arresto o ammenda fino a 5.000€ per datori di lavoro e dirigenti. Pianifica il piano formativo certificato con TDI.",
    "landing_page_url": "https://www.tdigroup.it/servizi/formazione-sicurezza-preposti"
  },
  {
    "service_id": "tdi-srv-chemical-audit",
    "service_name": "Audit di Conformità Rischio Chimico e Sostanze CMRD",
    "topic_category": "chemical_risk",
    "applicable_sectors": [
      "chemical",
      "pharmaceutical",
      "manufacturing",
      "automotive",
      "metalworking",
      "waste_management"
    ],
    "value_proposition": "Valutazione specialistica dell'esposizione professionale ad agenti chimici pericolosi, cancerogeni, mutageni e reprotossici con monitoraggio biologico e campionamento ambientale conforme alla Direttiva (UE) 2024/869.",
    "cta_headline": "Aggiorna la valutazione rischio chimico e i valori limite biologici con i tecnici TDI.",
    "cta_body": "Con l'entrata in vigore dei nuovi limiti europei per piombo e diisocianati, è obbligatorio adeguare il DVR chimico e i protocolli di sorveglianza sanitaria. Richiedi un audit tecnico preliminare con i nostri igienisti industriali.",
    "landing_page_url": "https://www.tdigroup.it/servizi/audit-rischio-chimico-cmrd"
  },
  {
    "service_id": "tdi-srv-machinery-ce",
    "service_name": "Consulenza Nuovo Regolamento Macchine (UE) 2023/1230 e Marcatura CE",
    "topic_category": "machinery",
    "applicable_sectors": [
      "machinery_manufacturing",
      "industrial_automation",
      "robotics",
      "metalworking",
      "packaging"
    ],
    "value_proposition": "Supporto ingegneristico per la transizione dalla Direttiva 2006/42/CE al Regolamento (UE) 2023/1230: gap analysis tecnica, valutazione rischi cybersecurity/AI applicata alla sicurezza macchine e fascicolo tecnico CE.",
    "cta_headline": "Verifica la conformità del tuo parco macchine al nuovo Regolamento UE 2023/1230.",
    "cta_body": "Il nuovo Regolamento Macchine impone requisiti stringenti per software di sicurezza, intelligenza artificiale e istruzioni digitali. Affidati agli esperti TDI per aggiornare la marcatura CE ed evitare blocchi commerciali.",
    "landing_page_url": "https://www.tdigroup.it/servizi/consulenza-regolamento-macchine-ce"
  },
  {
    "service_id": "tdi-srv-heat-stress",
    "service_name": "Protocollo Valutazione Rischio Microclima e Stress da Calore",
    "topic_category": "heat_stress",
    "applicable_sectors": [
      "construction",
      "agriculture",
      "foundry",
      "logistics",
      "road_works",
      "outdoor_activities"
    ],
    "value_proposition": "Integrazione del Documento di Valutazione dei Rischi (DVR) con indici microclimatici avanzati (WBGT, PHS, Worklimate) e protocolli operativi di emergenza caldo conformi alle linee guida INAIL 2024.",
    "cta_headline": "Proteggi i tuoi lavoratori all'aperto: richiedi il protocollo anti-calore personalizzato.",
    "cta_body": "Temperature elevate e ondate di calore sopra i 35°C richiedono misure organizzative immediate, pause designate e accesso alla CIGO caldo. Richiedi il protocollo operativo TDI per tutelare i lavoratori ed evitare sanzioni.",
    "landing_page_url": "https://www.tdigroup.it/servizi/valutazione-microclima-stress-termico"
  },
  {
    "service_id": "tdi-srv-fire-safety",
    "service_name": "Consulenza Antincendio e Piani di Emergenza (D.M. GSA e Minispazi)",
    "topic_category": "fire_safety",
    "applicable_sectors": [
      "manufacturing",
      "high_risk_plants",
      "logistics",
      "chemical",
      "commercial_activities",
      "all_sectors"
    ],
    "value_proposition": "Valutazione del rischio incendio, redazione e aggiornamento dei Piani di Emergenza ed Evacuazione (PEE) e percorsi di formazione/aggiornamento per addetti antincendio ai sensi dei D.M. 1, 2 e 3 Settembre 2021.",
    "cta_headline": "Allinea la gestione antincendio aziendale ai Decreti Ministeriali 2021.",
    "cta_body": "La mancata adozione o il mancato aggiornamento del piano di emergenza nei luoghi di lavoro comporta l'arresto da 2 a 4 mesi o ammenda fino a 6.000€. Prenota una verifica tecnica dello stato di conformità antincendio con TDI.",
    "landing_page_url": "https://www.tdigroup.it/servizi/consulenza-antincendio-piani-emergenza"
  }
]
```

### 4.2 Test Suite Updates: `tests/test_fixtures.py`
Add comprehensive test functions in `tests/test_fixtures.py`:
1. `test_tdi_services_fixture_exists_and_is_valid_json()`:
   - Verifies `fixtures/tdi_services.json` exists, is valid JSON, and contains the required offerings.
2. `test_tdi_services_pydantic_hydration()`:
   - Verifies every item cleanly instantiates as `TDIServiceOffering` without validation errors.
3. `test_tdi_services_expected_identifiers()`:
   - Verifies that `tdi-srv-preposti-training`, `tdi-srv-chemical-audit`, `tdi-srv-machinery-ce`, `tdi-srv-heat-stress` (and `tdi-srv-fire-safety`) are uniquely present.
4. `test_tdi_services_field_constraints_and_non_empty()`:
   - Verifies non-empty string lengths across `service_name`, `topic_category`, `value_proposition`, `cta_headline`, `cta_body`, valid `landing_page_url` (must start with `https://`), and at least 2 target sectors in `applicable_sectors`.
5. `test_tdi_services_topic_and_sector_matching_simulation()`:
   - Simulates `get_tdi_service_offerings(topic, sector)` matching logic:
     - `topic="chemical_risk"` $\rightarrow$ matches `tdi-srv-chemical-audit`.
     - `topic="machinery"` $\rightarrow$ matches `tdi-srv-machinery-ce`.
     - `topic="heat_stress"` $\rightarrow$ matches `tdi-srv-heat-stress`.
     - `topic="workplace_safety"` $\rightarrow$ matches `tdi-srv-preposti-training`.
     - `sector="construction"` $\rightarrow$ matches services applicable to construction (`preposti-training`, `heat-stress`).
6. `test_tdi_services_fallback_behavior_simulation()`:
   - Simulates querying with an unknown topic (e.g. `topic="unknown_nonexistent_topic"`) ensuring the deterministic fallback returns the primary general safety service (`tdi-srv-preposti-training`).

---

## 5. Verification Strategy
1. **JSON Syntax & Model Validation**:
   - Run `pytest` to verify 100% of fixture objects parse into `TDIServiceOffering`.
2. **Automated Unit Testing**:
   - Run `uv run pytest tests/test_fixtures.py -v`
   - Run `uv run pytest tests/ -v`
3. **Cross-Corpus Referential Consistency**:
   - Ensure the topics and sectors directly match the corresponding tags in `fixtures/regulatory_docs.json`.
4. **Latency & Zero External Dependencies**:
   - Verify fixture reading and parsing is instantaneous (<5ms) with zero network or database dependencies.

---

## 6. Questions & Decisions for Human Approval

### a. Question
Should `fixtures/tdi_services.json` include 5 commercial offerings (adding `tdi-srv-fire-safety` for complete 1:1 coverage with all 5 regulatory documents, including `gu-2023-dm-antincendio`) or strictly the 4 offerings explicitly enumerated in ROADMAP.md?

### b. Brief Background
The regulatory corpus (`fixtures/regulatory_docs.json`) contains 5 documents: Lead/Diisocyanates, Machinery, Preposti Training, Fire Safety (`gu-2023-dm-antincendio`), and Heat Stress (`inail-2024-circ-calore`). ROADMAP.md specifically names 4 TDI offerings (Preposti, Chemical Audit, Machinery CE, Heat Stress). Adding `tdi-srv-fire-safety` ensures that every single regulatory scenario has a dedicated, direct commercial CTA counterpart when agents generate articles.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Seed all 5 offerings (the 4 mandatory ones from ROADMAP.md plus `tdi-srv-fire-safety`), providing 1:1 commercial CTA coverage for every regulatory document in the seed corpus.
- **Option 2**: Seed strictly the 4 offerings listed in ROADMAP.md (Preposti, Chemical Audit, Machinery CE, Heat Stress), with fire safety articles relying on the general safety fallback offering.

### d. Justification of the Recommendation
Option 1 creates a complete, realistic demonstration for both POC A (Content Factory) and POC B (Research Analyst) without breaking any schema rules or test constraints. All 4 mandatory roadmap services are fully satisfied, and fire safety articles receive tailored CTAs rather than generic fallbacks.
