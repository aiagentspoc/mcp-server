# Implementation Plan - Task 2.1: Regulatory Corpus (`fixtures/regulatory_docs.json`)

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md), [SPECIFICATIONS.md § 5.1](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md#L227-L254), and [ARCHITECTURE.md § 2.1](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md#L37-L49), Task 2.1 establishes the primary regulatory seed dataset for the HSE Easy Mock MCP Server in `fixtures/regulatory_docs.json`.

This fixture dataset provides 100% deterministic, high-fidelity mock data representing 5 critical Italian and European Health, Safety, and Environment (HSE) regulatory acts across three authoritative bodies: **EUR-Lex**, **Gazzetta Ufficiale**, and **INAIL**. The dataset serves as the underlying corpus for downstream FastMCP tools (`list_regulatory_updates`, `search_regulatory_docs`, and `get_document_by_id`).

---

## 2. Prerequisites
- Completion of Phase 1 (Tasks 1.1, 1.2, 1.3).
- Validated Pydantic v2 schemas in [`models.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py) (`RegulatoryDocument` and `RegulatoryUpdateSummary`).
- Virtual environment with `pytest` and `pydantic` installed.

---

## 3. Objectives
1. Create `fixtures/regulatory_docs.json` containing 5 comprehensive, legally authentic HSE scenarios:
   - `eurlex-dir-2024-869` (**EUR-Lex**): Directive (EU) 2024/869 on occupational exposure limit values and biological limit values for lead, inorganic lead compounds, and diisocyanates.
   - `eurlex-reg-2023-1230` (**EUR-Lex**): Regulation (EU) 2023/1230 on machinery safety, digital documentation, and AI/autonomous robot safety.
   - `gu-2024-dl-preposti` (**Gazzetta Ufficiale**): D.L. 19/2024 conv. L. 56/2024 amending D.Lgs. 81/2008 Art. 18, 19, 37 regarding mandatory appointment and biennial training of Preposti.
   - `gu-2023-dm-antincendio` (**Gazzetta Ufficiale**): Ministerial Decrees on workplace fire safety management (D.M. GSA 02/09/2021 & D.M. Minispazi 03/09/2021) in high-risk environments.
   - `inail-2024-circ-calore` (**INAIL**): Circolare INAIL n. 28/2024 guidelines on heat stress prevention, microclimate evaluation, and Worklimate protocols in construction and agriculture.
2. Ensure 100% schema conformance: every record in `fixtures/regulatory_docs.json` must strictly parse into `RegulatoryDocument` and support lossless projection into `RegulatoryUpdateSummary`.
3. Provide rich, domain-accurate Markdown content in `content_markdown` for each document, including legislative structure, specific article breakdowns, technical threshold tables, obligations for employers/RSPPs/preposti, and penalty summaries.
4. Implement automated validation tests in `tests/test_fixtures.py` ensuring JSON syntax integrity, complete schema validation, field non-emptiness, ISO 8601 date adherence, and unique document identifiers.

---

## 4. Proposed Changes & Specifications

### 4.1 Fixture File: `fixtures/regulatory_docs.json`
Create `fixtures/regulatory_docs.json` with an array of 5 JSON objects adhering strictly to `RegulatoryDocument`:

```json
[
  {
    "doc_id": "eurlex-dir-2024-869",
    "source": "EUR_LEX",
    "doc_type": "directive",
    "official_reference": "Direttiva (UE) 2024/869",
    "title": "Direttiva (UE) 2024/869 del Parlamento europeo e del Consiglio del 13 marzo 2024 che modifica la direttiva 2004/37/CE e la direttiva 98/24/CE per quanto riguarda i valori limite di esposizione professionale per piombo e diisocianati",
    "publication_date": "2024-03-19",
    "effective_date": "2024-04-08",
    "impact_level": "critical",
    "topic_tags": [
      "chemical_risk",
      "occupational_health",
      "cmrd_substances",
      "biological_limits",
      "lead",
      "diisocyanates"
    ],
    "summary": "La Direttiva (UE) 2024/869 riduce significativamente i valori limite di esposizione professionale (OEL) e i valori limite biologici (BLV) per il piombo e i suoi composti inorganici, introducendo contestualmente per la prima volta valori limite per i diisocianati a livello comunitario. Impone una revisione straordinaria della valutazione del rischio chimico e dei protocolli di sorveglianza sanitaria.",
    "canonical_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024L0869",
    "status": "in_force",
    "target_sectors": [
      "manufacturing",
      "chemical_industry",
      "construction",
      "automotive",
      "metallurgy",
      "plastics_and_polyurethanes"
    ],
    "key_obligations": [
      "Riduzione del valore limite biologico (BLV) per il piombo inorganico a 15 µg Pb/100 ml di sangue (rispetto ai precedenti 70 µg/100 ml con fase transitoria fino al 2028).",
      "Introduzione del valore limite di esposizione professionale per i diisocianati pari a 6 µg NCO/m³ (8 ore) e 12 µg NCO/m³ (breve termine).",
      "Obbligo di sorveglianza sanitaria rafforzata e monitoraggio biologico periodico per tutti i lavoratori esposti a composti di piombo e diisocianati.",
      "Obbligo di formazione specifica certificata per tutti i lavoratori e preposti addetti alla manipolazione o all'uso industriale di diisocianati."
    ],
    "penalties_summary": "In sede di recepimento nazionale (D.Lgs. 81/2008 Art. 262): arresto da 3 a 6 mesi o ammenda da €3.071,27 a €7.862,44 per omessa o inadeguata valutazione del rischio chimico e mancata sorveglianza sanitaria.",
    "related_citations": [
      "Direttiva 2004/37/CE",
      "Direttiva 98/24/CE",
      "D.Lgs. 81/2008 Titolo IX Capo I e II",
      "D.Lgs. 81/2008 Art. 223",
      "D.Lgs. 81/2008 Art. 242"
    ],
    "content_markdown": "# Direttiva (UE) 2024/869 del Parlamento europeo e del Consiglio\n\n## 1. Premessa e Ambito di Applicazione\n..."
  },
  {
    "doc_id": "eurlex-reg-2023-1230",
    "source": "EUR_LEX",
    "doc_type": "regulation",
    "official_reference": "Regolamento (UE) 2023/1230",
    "title": "Regolamento (UE) 2023/1230 del Parlamento europeo e del Consiglio del 14 giugno 2023 relativo alle macchine e che abroga la direttiva 2006/42/CE",
    "publication_date": "2023-06-29",
    "effective_date": "2027-01-20",
    "impact_level": "high",
    "topic_tags": [
      "machinery",
      "ce_marking",
      "industrial_safety",
      "ai_safety",
      "cybersecurity",
      "robotics"
    ],
    "summary": "Il Regolamento (UE) 2023/1230 sostituisce integralmente la Direttiva Macchine 2006/42/CE, stabilendo requisiti essenziali di sicurezza e di tutela della salute per le macchine, i componenti di sicurezza e i quasi-macchinari. Introduce disposizioni cogenti per i rischi derivanti da intelligenza artificiale, robot collaborativi autonomi (AMR) e minacce di cybersecurity ai sistemi di comando di sicurezza.",
    "canonical_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32023R1230",
    "status": "in_force",
    "target_sectors": [
      "manufacturing",
      "machinery_and_automation",
      "robotics",
      "construction_equipment",
      "agriculture_machinery"
    ],
    "key_obligations": [
      "Valutazione obbligatoria dei rischi legati all'integrazione di sistemi di intelligenza artificiale e comportamenti auto-evolutivi nei sistemi di sicurezza.",
      "Protezione obbligatoria del software di sicurezza contro alterazioni o attacchi cyber intenzionali e accidentali.",
      "Ammissibilità della documentazione d'uso e dichiarazione CE in formato digitale (con obbligo di fornitura cartacea gratuita su richiesta).",
      "Procedura di valutazione di conformità rafforzata con intervento obbligatorio di Organismo Notificato per le macchine ad alto rischio di cui all'Allegato I."
    ],
    "penalties_summary": "Sanzioni per immissione sul mercato di macchine non conformi e violazione della marcatura CE (fino a €150.000, ritiro obbligatorio dal mercato e blocco della commercializzazione ai sensi del D.Lgs. 17/2010 e del Regolamento UE 2019/1020).",
    "related_citations": [
      "Direttiva 2006/42/CE",
      "Regolamento (UE) 2019/1020",
      "D.Lgs. 17/2010",
      "D.Lgs. 81/2008 Art. 70",
      "D.Lgs. 81/2008 Art. 71"
    ],
    "content_markdown": "# Regolamento (UE) 2023/1230 del Parlamento europeo e del Consiglio\n\n## 1. Ambito e Finalità\n..."
  },
  {
    "doc_id": "gu-2024-dl-preposti",
    "source": "GAZZETTA_UFFICIALE",
    "doc_type": "decree",
    "official_reference": "D.L. 19/2024 conv. L. 56/2024 / D.Lgs. 81/2008",
    "title": "Decreto-Legge 2 marzo 2024, n. 19 convertito con modificazioni dalla L. 29 aprile 2024, n. 56: Nuovi obblighi di nomina e formazione per i Preposti (Modifiche agli Artt. 18, 19 e 37 D.Lgs. 81/2008)",
    "publication_date": "2024-04-30",
    "effective_date": "2024-05-01",
    "impact_level": "critical",
    "topic_tags": [
      "workplace_safety",
      "preposti_training",
      "dvr",
      "dlgs_81_08",
      "subcontracting",
      "surveillance"
    ],
    "summary": "Il D.L. 19/2024 (convertito in Legge 56/2024) introduce misure cogenti per il rafforzamento della vigilanza nei luoghi di lavoro e negli appalti. Rende obbligatoria la designazione formale del Preposto per tutte le attività in appalto/subappalto, conferisce al Preposto il potere-dovere di interrompere le lavorazioni non sicure e fissa l'aggiornamento formativo obbligatorio con cadenza biennale in presenza.",
    "canonical_url": "https://www.gazzettaufficiale.it/eli/id/2024/04/30/24A02246/sg",
    "status": "in_force",
    "target_sectors": [
      "construction",
      "manufacturing",
      "logistics",
      "facility_management",
      "all_industries"
    ],
    "key_obligations": [
      "Nomina formale obbligatoria del Preposto da parte del datore di lavoro/dirigente per ogni attività svolta in regime di appalto o subappalto (Art. 18 c. 1 lett. b-bis).",
      "Dovere di intervento diretto del Preposto con interruzione immediata dell'attività lavorativa in caso di rilevata inosservanza delle misure di sicurezza (Art. 19 c. 1 lett. a).",
      "Formazione di aggiornamento per i Preposti con cadenza obbligatoria biennale (ogni 2 anni) svolta interamente in presenza (Art. 37 c. 7-ter).",
      "Aggiornamento del Documento di Valutazione dei Rischi (DVR) con indicazione specifica delle figure preposte e delle modalità operative di vigilanza."
    ],
    "penalties_summary": "Arresto da 2 a 4 mesi o ammenda da €1.842,76 a €7.371,04 per il datore di lavoro in caso di omessa nomina del preposto o mancata formazione biennale. Sospensione dell'attività imprenditoriale in caso di gravi violazioni sulla sicurezza.",
    "related_citations": [
      "D.Lgs. 81/2008 Art. 18",
      "D.Lgs. 81/2008 Art. 19",
      "D.Lgs. 81/2008 Art. 37",
      "D.L. 146/2021 conv. L. 215/2021",
      "D.L. 19/2024 conv. L. 56/2024"
    ],
    "content_markdown": "# Modifiche al D.Lgs. 81/2008 introdotte dal D.L. 19/2024 (L. 56/2024)\n\n## 1. Quadro Normativo\n..."
  },
  {
    "doc_id": "gu-2023-dm-antincendio",
    "source": "GAZZETTA_UFFICIALE",
    "doc_type": "decree",
    "official_reference": "D.M. 2 settembre 2021 / D.M. 3 settembre 2021",
    "title": "Decreto Interministeriale 2 settembre 2021 (GSA) e 3 settembre 2021 (Minispazi): Criteri di gestione della sicurezza antincendio nei luoghi di lavoro e valutazione del rischio di incendio",
    "publication_date": "2023-10-04",
    "effective_date": "2023-10-04",
    "impact_level": "high",
    "topic_tags": [
      "fire_safety",
      "emergency_plans",
      "high_risk_plants",
      "risk_assessment",
      "gsa",
      "first_aid"
    ],
    "summary": "I decreti ministeriali antincendio (c.d. Decreto GSA e Decreto Minispazi) hanno superato definitivamente lo storico D.M. 10 marzo 1998, stabilendo i nuovi criteri per la valutazione del rischio d'incendio nei luoghi di lavoro, l'obbligo di redazione del Piano di Emergenza ed Evacuazione (PEE), la tenuta del registro antincendio e la formazione e attestazione di idoneità tecnica per gli addetti alle emergenze in attività ad alto rischio.",
    "canonical_url": "https://www.gazzettaufficiale.it/eli/id/2021/10/04/21A05747/sg",
    "status": "in_force",
    "target_sectors": [
      "manufacturing",
      "chemical_plants",
      "warehousing_and_logistics",
      "healthcare",
      "hospitality",
      "public_entertainment"
    ],
    "key_obligations": [
      "Aggiornamento della Valutazione del Rischio Incendio secondo i criteri dei Decreti 2 e 3 Settembre 2021 (classificazione dei luoghi di lavoro di livello 1, 2 e 3).",
      "Redazione obbligatoria del Piano di Emergenza ed Evacuazione (PEE) per tutti i luoghi di lavoro con oltre 10 lavoratori o soggetti a controllo VVF.",
      "Designazione e formazione specifica degli addetti antincendio con aggiornamento obbligatorio quinquennale (5 anni) ed esame di idoneità tecnica presso il Comando VVF per le attività ad alto rischio.",
      "Tenuta e costante aggiornamento del Registro dei Controlli Antincendio per la manutenzione presidi e impianti."
    ],
    "penalties_summary": "D.Lgs. 81/2008 Art. 68: arresto da 2 a 4 mesi o ammenda da €1.474,21 a €6.388,23 per omessa o insufficiente valutazione del rischio incendio, mancata redazione del piano di emergenza o omessa formazione degli addetti antincendio.",
    "related_citations": [
      "D.Lgs. 81/2008 Art. 46",
      "D.M. 10 marzo 1998",
      "D.M. 1 settembre 2021",
      "D.M. 2 settembre 2021",
      "D.M. 3 settembre 2021"
    ],
    "content_markdown": "# Decreti Ministeriali Antincendio (D.M. 2 e 3 Settembre 2021)\n\n## 1. Nuovo Assetto Normativo della Sicurezza Antincendio\n..."
  },
  {
    "doc_id": "inail-2024-circ-calore",
    "source": "INAIL",
    "doc_type": "circular",
    "official_reference": "Circolare INAIL n. 28/2024",
    "title": "Circolare INAIL n. 28 del 24 luglio 2024: Indicazioni operative e linee guida per la prevenzione delle patologie da calore nei luoghi di lavoro all'aperto, nell'edilizia e in agricoltura (Progetto Worklimate)",
    "publication_date": "2024-07-24",
    "effective_date": "2024-07-24",
    "impact_level": "high",
    "topic_tags": [
      "heat_stress",
      "microclimate",
      "construction_safety",
      "workplace_health",
      "worklimate",
      "agriculture"
    ],
    "summary": "La Circolare INAIL n. 28/2024 fornisce linee guida operative per la gestione e prevenzione del rischio da stress termico e colpi di calore nei cantieri edili, stradali e in agricoltura sulla base dei modelli previsionali del progetto Worklimate. Definisce misure di riorganizzazione dei turni, idratazione, aree di sosta ombreggiate e procedure di ricorso alla Cassa Integrazione Guadagni (CIGO) per meteo estremo.",
    "canonical_url": "https://www.inail.it/cs/internet/atti-e-documenti/circolari-e-linee-guida/circolari/circolare-inail-28-2024.html",
    "status": "in_force",
    "target_sectors": [
      "construction",
      "agriculture",
      "road_maintenance",
      "quarries_and_mining",
      "outdoor_logistics"
    ],
    "key_obligations": [
      "Integrazione del rischio microclima e stress termico nel DVR aziendale (Art. 28 D.Lgs. 81/2008) per tutte le lavorazioni all'aperto.",
      "Riorganizzazione degli orari di lavoro con anticipazione delle lavorazioni gravose alle prime ore del mattino e sospensione nelle fasce di picco termico (14:00-17:00 con temperature >35°C).",
      "Fornitura obbligatoria di aree di riposo ombreggiate e ventilate, acqua potabile fresca e integratori salini.",
      "Attivazione della CIGO (Cassa Integrazione Guadagni Ordinaria) con causale eventi meteo per temperature superiori a 35°C (o temperature percepite elevate)."
    ],
    "penalties_summary": "Violazione degli obblighi di valutazione dei rischi e adozione delle misure preventive (D.Lgs. 81/2008 Artt. 28, 180, 181): arresto da 3 a 6 mesi o ammenda da €3.071,27 a €7.862,44.",
    "related_citations": [
      "Circolare INAIL 28/2024",
      "D.Lgs. 81/2008 Art. 28",
      "D.Lgs. 81/2008 Titolo VIII Capo I",
      "D.Lgs. 81/2008 Art. 180",
      "D.Lgs. 81/2008 Art. 181",
      "D.L. 98/2023"
    ],
    "content_markdown": "# Circolare INAIL n. 28 del 24 Luglio 2024 - Prevenzione Rischio Calore\n\n## 1. Contesto e Finalità\n..."
  }
]
```

### 4.2 Test Suite: `tests/test_fixtures.py`
Create `tests/test_fixtures.py` to automate verification of the regulatory corpus fixture:
1. `test_regulatory_docs_json_exists_and_valid()`: Asserts that `fixtures/regulatory_docs.json` exists, contains valid JSON, and parses into a non-empty list of exactly 5 items.
2. `test_regulatory_docs_schema_validation()`: Instantiates each item as `RegulatoryDocument` and verifies that no `ValidationError` is raised.
3. `test_regulatory_docs_unique_identifiers()`: Asserts that all `doc_id` values are unique and non-empty.
4. `test_regulatory_docs_required_fields_content()`: Verifies that required fields (`title`, `official_reference`, `summary`, `canonical_url`, `content_markdown`, `target_sectors`, `key_obligations`, `related_citations`) are non-empty and well-formed.
5. `test_regulatory_docs_to_summary_projection()`: Verifies that each document cleanly projects to `RegulatoryUpdateSummary` via `doc.to_summary()`.
6. `test_regulatory_docs_date_formats()`: Asserts all `publication_date` and `effective_date` strings adhere strictly to ISO 8601 `YYYY-MM-DD`.

---

## 5. Verification Strategy
1. **JSON Syntax Validation**: Ensure `fixtures/regulatory_docs.json` is formatted with 2-space indentation and valid JSON syntax.
2. **Automated Unit Testing**: Run `uv run pytest tests/test_fixtures.py -v` and `uv run pytest tests/ -v`.
3. **Pydantic Model Hydration**: Validate all 5 objects parse directly into `RegulatoryDocument` instances.
4. **FastMCP Indexing Readiness**: Verify that `server.py` startup pattern `[RegulatoryDocument(**d) for d in json.load(f)]` executes cleanly against `fixtures/regulatory_docs.json`.

---

## 6. Questions & Decisions for Human Approval

### a. Question
Should we include exhaustive full-text article breakdowns in `content_markdown` for each document, or structured executive summaries with key articles?

### b. Brief Background
European directives and Italian decrees can span dozens of pages. In the mock MCP server, `content_markdown` is read by Writer and QA agents to extract specific requirements, threshold numbers (e.g. 15 µg/100 ml for lead, 6 µg/m³ for diisocyanates, 35°C for heat stress), and sanctions.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Provide highly detailed, structured Markdown breakdowns containing all critical articles, operational requirements, numeric safety thresholds, sanction references, and transitional timetables (approx. 100-250 lines per document).
- **Option 2**: Provide minimal skeleton summaries of 10-20 lines per document.

### d. Justification of the Recommendation
Option 1 provides the exact technical and legal depth needed for realistic downstream LLM agent reasoning, QA evaluation benchmarks (Phase 5), and legal citation verification while keeping fixture files deterministic and self-contained.
