# Implementation Plan - Task 2.2: Legal Citations Registry (`fixtures/citations.json`)

## 1. Context & Task Scope
According to [ROADMAP.md](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/ROADMAP.md#L68-L71), [SPECIFICATIONS.md § 3.3, § 4.4, § 5.2](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/SPECIFICATIONS.md#L87-L117), and [ARCHITECTURE.md § 2.1, § 4.2](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/.agents/docs/ARCHITECTURE.md#L103-L112), Task 2.2 establishes the **Legal Citations Registry** (`fixtures/citations.json`) for the HSE Easy Mock MCP Server.

This fixture dataset provides a 100% deterministic, high-accuracy legal citation verification database used primarily by the downstream MCP tool `verify_legal_citation`. It allows QA and editorial agents to check whether specific Italian and European legal references (articles, decrees, directives, regulations, and circulars) are valid, currently in force, amended, or repealed, and retrieves their canonical citation formats and authoritative URLs (Normattiva, EUR-Lex, INAIL, Gazzetta Ufficiale).

---

## 2. Prerequisites
- Completion of Phase 1 (Tasks 1.1, 1.2, 1.3) and Task 2.1 (`fixtures/regulatory_docs.json`).
- Validated Pydantic v2 schemas in [`models.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py), specifically [`CitationVerificationResult`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/models.py#L103-L140).
- Existing test suite in [`tests/test_fixtures.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_fixtures.py) and [`tests/test_models.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_models.py).

---

## 3. Objectives
1. **Author `fixtures/citations.json`** containing comprehensive active, amended, and repealed legal citations:
   - **Active & Amended HSE Citations**:
     - `D.Lgs. 81/2008 Art. 37` (Mandatory safety training & biennial preposti updates, verified against `gu-2024-dl-preposti`).
     - `D.Lgs. 81/2008 Art. 18` (Employer/manager obligations & formal preposto appointment, verified against `gu-2024-dl-preposti`).
     - `D.Lgs. 81/2008 Art. 19` (Preposto supervisory duties & power to halt non-compliant work, verified against `gu-2024-dl-preposti`).
     - `Direttiva 2004/37/CE` (Carcinogens, Mutagens, and Reprotoxic Substances Directive, amended by Dir 2024/869, verified against `eurlex-dir-2024-869`).
     - `Direttiva (UE) 2024/869` (Lead & diisocyanates biological limits and OELs, verified against `eurlex-dir-2024-869`).
     - `Direttiva 98/24/CE` (Chemical agents at work, amended by Dir 2024/869, verified against `eurlex-dir-2024-869`).
     - `Regolamento (UE) 2023/1230 Art. 10` (Machinery manufacturer obligations, CE marking, and AI safety, verified against `eurlex-reg-2023-1230`).
     - `Regolamento (UE) 2023/1230` (EU Machinery Regulation base act, verified against `eurlex-reg-2023-1230`).
     - `Circolare INAIL 28/2024` (Workplace heat stress guidelines and Worklimate protocol, verified against `inail-2024-circ-calore`).
     - `D.Lgs. 81/2008 Art. 28` (Risk assessment document / DVR inclusion, verified against `inail-2024-circ-calore`).
     - `D.Lgs. 81/2008 Art. 46` (Workplace fire prevention and emergency management, verified against `gu-2023-dm-antincendio`).
     - `D.M. 2 settembre 2021` (Workplace fire safety management & GSA emergency plans, verified against `gu-2023-dm-antincendio`).
     - `D.M. 3 settembre 2021` (Fire safety design and risk assessment criteria / Minispazi, verified against `gu-2023-dm-antincendio`).
   - **Invalid & Repealed Test Citations**:
     - `D.P.R. 547/55 Art. 10` (Historic accident prevention rules — *repealed* by Art. 304 D.Lgs. 81/2008).
     - `D.Lgs. 626/94 Art. 3` (Historic workplace safety act — *repealed* by Art. 304 D.Lgs. 81/2008).
     - `Direttiva 98/37/CE` (Historic EU Machinery Directive — *repealed* by Directive 2006/42/EC).
     - `D.P.R. 303/56 Art. 4` (Historic occupational hygiene regulation — *repealed* by Art. 304 D.Lgs. 81/2008).
     - `D.M. 10 marzo 1998` (Historical fire safety criteria — *repealed/superseded* by D.M. 1, 2, 3 Settembre 2021).
2. **Multi-Alias Normalization Index**:
   - Equip every citation entry with an extensive `aliases` array containing variations in casing (lowercase, uppercase, mixed), punctuation (`D.Lgs.`, `D.Lgs`, `DLgs`, `dlgs`), Italian spelled-out forms (`Decreto Legislativo`, `Articolo`), spacing, and shorthand years (`81/08` vs `81/2008`).
3. **Cross-Corpus Linkage**:
   - Link all relevant citations to their corresponding `doc_id` in `fixtures/regulatory_docs.json` via `verified_against_doc_id` for end-to-end relational consistency.
4. **Automated Test Validation**:
   - Extend [`tests/test_fixtures.py`](file:///C:/Users/Saksham/Git/poc/AIAgents/mcp-server/tests/test_fixtures.py) with comprehensive unit tests for `citations.json`: schema hydration, valid/invalid state checks, alias uniqueness, relational integrity with `regulatory_docs.json`, and lookup simulation.

---

## 4. Proposed Changes & Specifications

### 4.1 Fixture File: `fixtures/citations.json`
Create `fixtures/citations.json` formatted as a JSON array of citation objects adhering to `CitationVerificationResult` fields plus an `aliases` array for lookup resolution:

```json
[
  {
    "citation_input": "D.Lgs. 81/2008 Art. 37",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 37 (Formazione dei lavoratori e dei loro rappresentanti)",
    "official_reference": "D.Lgs. 9 aprile 2008, n. 81",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art37",
    "verified_against_doc_id": "gu-2024-dl-preposti",
    "notes": "Modificato da ultimo dal D.L. 19/2024 (conv. L. 56/2024). Introduce l'obbligo di aggiornamento formativo biennale in presenza per i Preposti (comma 7-ter).",
    "aliases": [
      "d.lgs. 81/2008 art. 37",
      "d.lgs 81/08 art 37",
      "dlgs 81/2008 art 37",
      "dlgs 81/08 art. 37",
      "d.lgs 81/2008 art 37",
      "d.lgs. 81/08 art. 37",
      "decreto legislativo 81/2008 articolo 37",
      "decreto legislativo 81/08 art 37",
      "art. 37 d.lgs. 81/2008",
      "art 37 dlgs 81/08",
      "art. 37 d.lgs. 81/08",
      "articolo 37 d.lgs. 81/2008"
    ]
  },
  {
    "citation_input": "D.Lgs. 81/2008 Art. 18",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 18 (Obblighi del datore di lavoro e del dirigente)",
    "official_reference": "D.Lgs. 9 aprile 2008, n. 81",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art18",
    "verified_against_doc_id": "gu-2024-dl-preposti",
    "notes": "Include la lettera b-bis introdotta dal D.L. 146/2021 e rafforzata dal D.L. 19/2024: obbligo di individuare espressamente e formalizzare per iscritto il preposto nelle attività in appalto e subappalto.",
    "aliases": [
      "d.lgs. 81/2008 art. 18",
      "d.lgs 81/08 art 18",
      "dlgs 81/2008 art 18",
      "dlgs 81/08 art. 18",
      "decreto legislativo 81/2008 articolo 18",
      "art. 18 d.lgs. 81/2008",
      "art 18 dlgs 81/08",
      "art. 18 d.lgs. 81/08",
      "articolo 18 d.lgs. 81/2008"
    ]
  },
  {
    "citation_input": "D.Lgs. 81/2008 Art. 19",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 19 (Obblighi del preposto)",
    "official_reference": "D.Lgs. 9 aprile 2008, n. 81",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art19",
    "verified_against_doc_id": "gu-2024-dl-preposti",
    "notes": "Riformulato dalla L. 215/2021: conferisce al preposto il dovere-potere di intervenire per interrompere tempestivamente l'attività in caso di mancato rispetto delle norme di sicurezza da parte dei lavoratori.",
    "aliases": [
      "d.lgs. 81/2008 art. 19",
      "d.lgs 81/08 art 19",
      "dlgs 81/2008 art 19",
      "dlgs 81/08 art. 19",
      "decreto legislativo 81/2008 articolo 19",
      "art. 19 d.lgs. 81/2008",
      "art 19 dlgs 81/08",
      "art. 19 d.lgs. 81/08",
      "articolo 19 d.lgs. 81/2008"
    ]
  },
  {
    "citation_input": "Direttiva 2004/37/CE",
    "is_valid": true,
    "status": "amended",
    "canonical_citation": "Direttiva 2004/37/CE del Parlamento europeo e del Consiglio, del 29 aprile 2004 (Protezione dei lavoratori contro i rischi derivanti da agenti cancerogeni, mutageni o sostanze tossiche per la riproduzione)",
    "official_reference": "Direttiva 2004/37/CE",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32004L0037",
    "verified_against_doc_id": "eurlex-dir-2024-869",
    "notes": "Modificata dalla Direttiva (UE) 2024/869 per quanto attiene all'abbassamento dei valori limite biologici per il piombo e l'inclusione delle sostanze reprotossiche (CMRD).",
    "aliases": [
      "direttiva 2004/37/ce",
      "direttiva 2004/37",
      "dir 2004/37/ce",
      "dir. 2004/37/ce",
      "direttiva cmr",
      "direttiva cmrd",
      "directive 2004/37/ec",
      "dir 2004/37"
    ]
  },
  {
    "citation_input": "Direttiva (UE) 2024/869",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Direttiva (UE) 2024/869 del Parlamento europeo e del Consiglio del 13 marzo 2024 (Valori limite per piombo e diisocianati)",
    "official_reference": "Direttiva (UE) 2024/869",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024L0869",
    "verified_against_doc_id": "eurlex-dir-2024-869",
    "notes": "Entrata in vigore l'8 aprile 2024. Fissa il valore limite biologico per il piombo a 15 µg Pb/100 ml di sangue e stabilisce limiti per i diisocianati (6 µg NCO/m³ 8h, 12 µg NCO/m³ breve termine).",
    "aliases": [
      "direttiva (ue) 2024/869",
      "direttiva ue 2024/869",
      "direttiva 2024/869",
      "direttiva 2024/869/ue",
      "dir 2024/869/ue",
      "dir (ue) 2024/869",
      "dir. 2024/869",
      "direttiva piombo e diisocianati"
    ]
  },
  {
    "citation_input": "Direttiva 98/24/CE",
    "is_valid": true,
    "status": "amended",
    "canonical_citation": "Direttiva 98/24/CE del Consiglio, del 7 aprile 1998 (Protezione della salute e della sicurezza dei lavoratori contro i rischi derivanti da agenti chimici)",
    "official_reference": "Direttiva 98/24/CE",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:31998L0024",
    "verified_against_doc_id": "eurlex-dir-2024-869",
    "notes": "Modificata dalla Direttiva (UE) 2024/869 per l'integrazione dei nuovi valori limite di esposizione professionale per i diisocianati e composti chimici pericolosi.",
    "aliases": [
      "direttiva 98/24/ce",
      "direttiva 98/24",
      "dir 98/24/ce",
      "dir. 98/24/ce",
      "direttiva agenti chimici",
      "directive 98/24/ec"
    ]
  },
  {
    "citation_input": "Regolamento (UE) 2023/1230 Art. 10",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Regolamento (UE) 2023/1230 del Parlamento europeo e del Consiglio, Articolo 10 (Obblighi dei fabbricanti di macchine)",
    "official_reference": "Regolamento (UE) 2023/1230",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32023R1230",
    "verified_against_doc_id": "eurlex-reg-2023-1230",
    "notes": "Definisce gli obblighi del fabbricante di macchine relative a progettazione sicura, marcatura CE, fornitura di istruzioni per l'uso (anche in formato digitale) e conformità AI/cybersecurity.",
    "aliases": [
      "regolamento (ue) 2023/1230 art. 10",
      "regolamento (ue) 2023/1230 art 10",
      "regolamento ue 2023/1230 art. 10",
      "regolamento 2023/1230 art 10",
      "reg (ue) 2023/1230 art 10",
      "reg. 2023/1230 art. 10",
      "art. 10 regolamento 2023/1230",
      "art 10 reg ue 2023/1230",
      "articolo 10 regolamento macchine"
    ]
  },
  {
    "citation_input": "Regolamento (UE) 2023/1230",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Regolamento (UE) 2023/1230 del Parlamento europeo e del Consiglio del 14 giugno 2023 relativo alle macchine",
    "official_reference": "Regolamento (UE) 2023/1230",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32023R1230",
    "verified_against_doc_id": "eurlex-reg-2023-1230",
    "notes": "Nuovo Regolamento Macchine europeo. Abroga integralmente la direttiva 2006/42/CE con applicazione generale a decorrere dal 20 gennaio 2027.",
    "aliases": [
      "regolamento (ue) 2023/1230",
      "regolamento ue 2023/1230",
      "regolamento 2023/1230",
      "regolamento macchine 2023",
      "nuovo regolamento macchine",
      "reg (ue) 2023/1230",
      "reg. 2023/1230/ue",
      "eu machinery regulation 2023/1230"
    ]
  },
  {
    "citation_input": "Circolare INAIL 28/2024",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Circolare INAIL n. 28 del 24 luglio 2024 (Linee guida prevenzione patologie da calore e stress termico nei luoghi di lavoro)",
    "official_reference": "Circolare INAIL n. 28/2024",
    "official_url": "https://www.inail.it/cs/internet/atti-e-documenti/circolari-e-linee-guida/circolari/circolare-inail-28-2024.html",
    "verified_against_doc_id": "inail-2024-circ-calore",
    "notes": "Fornisce istruzioni operative per la gestione del rischio da stress da calore in edilizia e agricoltura, basate sul progetto Worklimate e soglie CIGO sopra i 35°C.",
    "aliases": [
      "circolare inail 28/2024",
      "circolare inail n. 28/2024",
      "circ inail 28/2024",
      "circ. inail 28/2024",
      "inail circolare 28/2024",
      "circolare calore inail",
      "circolare 28 inail 2024",
      "circolare inail n 28 2024"
    ]
  },
  {
    "citation_input": "D.Lgs. 81/2008 Art. 28",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 28 (Oggetto della valutazione dei rischi)",
    "official_reference": "D.Lgs. 9 aprile 2008, n. 81",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art28",
    "verified_against_doc_id": "inail-2024-circ-calore",
    "notes": "Impone la valutazione di tutti i rischi per la sicurezza e la salute dei lavoratori, compresi i rischi da agenti fisici, microclima e stress termico.",
    "aliases": [
      "d.lgs. 81/2008 art. 28",
      "d.lgs 81/08 art 28",
      "dlgs 81/2008 art 28",
      "dlgs 81/08 art. 28",
      "decreto legislativo 81/2008 articolo 28",
      "art. 28 d.lgs. 81/2008",
      "art 28 dlgs 81/08",
      "articolo 28 dvr dlgs 81"
    ]
  },
  {
    "citation_input": "D.Lgs. 81/2008 Art. 46",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 46 (Prevenzione incendi)",
    "official_reference": "D.Lgs. 9 aprile 2008, n. 81",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81~art46",
    "verified_against_doc_id": "gu-2023-dm-antincendio",
    "notes": "Principio generale di prevenzione incendi nei luoghi di lavoro, attuato e dettagliato dai Decreti Ministeriali 1, 2 e 3 Settembre 2021.",
    "aliases": [
      "d.lgs. 81/2008 art. 46",
      "d.lgs 81/08 art 46",
      "dlgs 81/2008 art 46",
      "dlgs 81/08 art. 46",
      "decreto legislativo 81/2008 articolo 46",
      "art. 46 d.lgs. 81/2008",
      "art 46 dlgs 81/08",
      "antincendio art 46 dlgs 81"
    ]
  },
  {
    "citation_input": "D.M. 2 settembre 2021",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Decreto Ministeriale 2 settembre 2021 (Criteri per la gestione dei luoghi di lavoro in esercizio ed in emergenza e caratteristiche del servizio di prevenzione e protezione antincendio - c.d. Decreto GSA)",
    "official_reference": "D.M. 2 settembre 2021",
    "official_url": "https://www.gazzettaufficiale.it/eli/id/2021/10/04/21A05747/sg",
    "verified_against_doc_id": "gu-2023-dm-antincendio",
    "notes": "In vigore dal 4 ottobre 2022. Disciplina la gestione della sicurezza antincendio, i piani di emergenza e i requisiti/corsi di aggiornamento quinquennali degli addetti antincendio.",
    "aliases": [
      "d.m. 2 settembre 2021",
      "dm 2 settembre 2021",
      "dm 02/09/2021",
      "d.m. 2/9/2021",
      "decreto gsa",
      "decreto 2 settembre 2021 gsa",
      "dm gsa 2021"
    ]
  },
  {
    "citation_input": "D.M. 3 settembre 2021",
    "is_valid": true,
    "status": "in_force",
    "canonical_citation": "Decreto Ministeriale 3 settembre 2021 (Criteri generali di progettazione, realizzazione ed esercizio della sicurezza antincendio per luoghi di lavoro - c.d. Decreto Minispazi)",
    "official_reference": "D.M. 3 settembre 2021",
    "official_url": "https://www.gazzettaufficiale.it/eli/id/2021/10/29/21A06349/sg",
    "verified_against_doc_id": "gu-2023-dm-antincendio",
    "notes": "In vigore dal 29 ottobre 2022. Definisce la valutazione del rischio d'incendio per luoghi di lavoro a basso rischio d'incendio e introduce il metodo semplificato di conformità.",
    "aliases": [
      "d.m. 3 settembre 2021",
      "dm 3 settembre 2021",
      "dm 03/09/2021",
      "d.m. 3/9/2021",
      "decreto minispazi",
      "decreto 3 settembre 2021",
      "dm minispazi 2021"
    ]
  },
  {
    "citation_input": "D.P.R. 547/55 Art. 10",
    "is_valid": false,
    "status": "repealed",
    "canonical_citation": "D.P.R. 27 aprile 1955, n. 547, Art. 10 (Norme generali per la prevenzione degli infortuni sul lavoro) [ABROGATO]",
    "official_reference": "D.P.R. 27 aprile 1955, n. 547",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1955-04-27;547",
    "verified_against_doc_id": null,
    "notes": "DISPOSIZIONE ABROGATA. Il D.P.R. 547/1955 è stato integralmente abrogato dall'Articolo 304 del D.Lgs. 9 aprile 2008, n. 81. La materia è oggi disciplinata dal Titolo III del D.Lgs. 81/2008.",
    "aliases": [
      "d.p.r. 547/55 art. 10",
      "dpr 547/55 art 10",
      "dpr 547/1955 art 10",
      "d.p.r. 547/1955 art. 10",
      "dpr 547 art 10",
      "decreto presidente repubblica 547/55 articolo 10",
      "art 10 dpr 547/55",
      "art. 10 d.p.r. 547/55"
    ]
  },
  {
    "citation_input": "D.Lgs. 626/94 Art. 3",
    "is_valid": false,
    "status": "repealed",
    "canonical_citation": "D.Lgs. 19 settembre 1994, n. 626, Art. 3 (Misure generali di tutela) [ABROGATO]",
    "official_reference": "D.Lgs. 19 settembre 1994, n. 626",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:1994-09-19;626",
    "verified_against_doc_id": null,
    "notes": "DISPOSIZIONE ABROGATA. Il D.Lgs. 626/1994 è stato integralmente abrogato dall'Articolo 304 del D.Lgs. 9 aprile 2008, n. 81. Le misure generali di tutela sono confluite nell'Articolo 15 del D.Lgs. 81/2008.",
    "aliases": [
      "d.lgs. 626/94 art. 3",
      "d.lgs 626/94 art 3",
      "dlgs 626/94 art 3",
      "dlgs 626/1994 art 3",
      "d.lgs. 626/1994 art. 3",
      "decreto legislativo 626/94 articolo 3",
      "decreto 626 art 3",
      "art 3 dlgs 626/94",
      "art. 3 d.lgs. 626/94"
    ]
  },
  {
    "citation_input": "Direttiva 98/37/CE",
    "is_valid": false,
    "status": "repealed",
    "canonical_citation": "Direttiva 98/37/CE del Parlamento europeo e del Consiglio, del 22 giugno 1998 (Ravvicinamento delle legislazioni degli Stati membri relative alle macchine) [ABROGATA]",
    "official_reference": "Direttiva 98/37/CE",
    "official_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:31998L0037",
    "verified_against_doc_id": null,
    "notes": "DIRETTIVA ABROGATA. Abrogata dalla Direttiva Macchine 2006/42/CE a far data dal 29 dicembre 2009, a sua volta sostituita dal Regolamento (UE) 2023/1230.",
    "aliases": [
      "direttiva 98/37/ce",
      "direttiva 98/37",
      "dir 98/37/ce",
      "dir. 98/37/ce",
      "directive 98/37/ec",
      "direttiva macchine 98/37"
    ]
  },
  {
    "citation_input": "D.P.R. 303/56 Art. 4",
    "is_valid": false,
    "status": "repealed",
    "canonical_citation": "D.P.R. 19 marzo 1956, n. 303, Art. 4 (Norme generali per l'igiene del lavoro) [ABROGATO]",
    "official_reference": "D.P.R. 19 marzo 1956, n. 303",
    "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.del.presidente.della.repubblica:1956-03-19;303",
    "verified_against_doc_id": null,
    "notes": "DISPOSIZIONE ABROGATA. Il D.P.R. 303/1956 è stato abrogato dall'Articolo 304 del D.Lgs. 9 aprile 2008, n. 81. I requisiti igienico-sanitari e dei luoghi di lavoro sono disciplinati dall'Allegato IV e dal Titolo II del D.Lgs. 81/2008.",
    "aliases": [
      "d.p.r. 303/56 art. 4",
      "dpr 303/56 art 4",
      "dpr 303/1956 art 4",
      "d.p.r. 303/1956 art. 4",
      "decreto presidente repubblica 303/56 articolo 4",
      "art 4 dpr 303/56",
      "art. 4 d.p.r. 303/56"
    ]
  },
  {
    "citation_input": "D.M. 10 marzo 1998",
    "is_valid": false,
    "status": "repealed",
    "canonical_citation": "Decreto Ministeriale 10 marzo 1998 (Criteri generali di sicurezza antincendio e per la gestione dell'emergenza nei luoghi di lavoro) [ABROGATO/SUPERATO]",
    "official_reference": "D.M. 10 marzo 1998",
    "official_url": "https://www.gazzettaufficiale.it/eli/id/1998/04/07/098A3078/sg",
    "verified_against_doc_id": null,
    "notes": "DECRETO ABROGATO. Integralmente superato e sostituito dalla triade dei decreti ministeriali del settembre 2021 (D.M. 1 Settembre 2021 Controlli, D.M. 2 Settembre 2021 GSA, D.M. 3 Settembre 2021 Minispazi).",
    "aliases": [
      "d.m. 10 marzo 1998",
      "dm 10 marzo 1998",
      "dm 10/03/1998",
      "d.m. 10/3/1998",
      "decreto 10 marzo 1998 antincendio",
      "dm 10 marzo 98"
    ]
  }
]
```

### 4.2 Test Suite Updates: `tests/test_fixtures.py`
Extend `tests/test_fixtures.py` with comprehensive assertions covering `fixtures/citations.json`:
1. `test_citations_fixture_exists_and_is_valid_json()`: Ensures `fixtures/citations.json` exists, is valid JSON, and contains all expected seed citations.
2. `test_citations_pydantic_hydration()`: Verifies that every record cleanly instantiates as `CitationVerificationResult` without validation error.
3. `test_citations_required_fields_and_enums()`: Verifies that `citation_input`, `is_valid`, `status` (must be one of `"in_force"`, `"amended"`, `"repealed"`), `canonical_citation`, `official_reference`, and `official_url` are populated and valid.
4. `test_citations_mandatory_valid_and_repealed_cases()`: Specifically asserts the exact status and validity of roadmap-mandated citations:
   - `D.Lgs. 81/2008 Art. 37` $\rightarrow$ `is_valid: True`, `status: "in_force"`
   - `D.Lgs. 81/2008 Art. 18` $\rightarrow$ `is_valid: True`, `status: "in_force"`
   - `Direttiva 2004/37/CE` $\rightarrow$ `is_valid: True`, `status: "amended"`
   - `Regolamento (UE) 2023/1230 Art. 10` $\rightarrow$ `is_valid: True`, `status: "in_force"`
   - `Circolare INAIL 28/2024` $\rightarrow$ `is_valid: True`, `status: "in_force"`
   - `D.P.R. 547/55 Art. 10` $\rightarrow$ `is_valid: False`, `status: "repealed"`
   - `D.Lgs. 626/94 Art. 3` $\rightarrow$ `is_valid: False`, `status: "repealed"`
   - `Direttiva 98/37/CE` $\rightarrow$ `is_valid: False`, `status: "repealed"`
5. `test_citations_relational_integrity_with_regulatory_docs()`: Verifies that every non-null `verified_against_doc_id` points to a real `doc_id` present in `fixtures/regulatory_docs.json`.
6. `test_citations_alias_index_and_normalization_simulation()`: Tests in-memory lookup matching:
   - Verifies all aliases across all records are unique (no cross-citation collisions).
   - Simulates normalized lookup (`citation.strip().lower()`) across both `citation_input` and `aliases` for various messy query strings (e.g. `"dlgs 81/08 art 37"`, `"   D.LGS. 626/94 ART 3  "`, `"direttiva 98/37"`).

---

## 5. Verification Strategy
1. **JSON Formatting & Syntax Check**: Validate `fixtures/citations.json` conforms to valid JSON syntax with standard indentation.
2. **Automated Unit Testing**: Run `uv run pytest tests/test_fixtures.py -v` and `uv run pytest tests/ -v`.
3. **Cross-Corpus Referential Integrity**: Ensure 100% of referenced `verified_against_doc_id` entries match keys in `fixtures/regulatory_docs.json`.
4. **Lookup Simulation**: Verify that `server.py`'s lookup loop can resolve any alias in `O(1)` or fast list scan to return the canonical `CitationVerificationResult`.

---

## 6. Questions & Decisions for Human Approval

### a. Question
Should the citation registry store canonical citations with full formal title descriptions (e.g. `"D.Lgs. 9 aprile 2008, n. 81, Art. 37 (Formazione dei lavoratori e dei loro rappresentanti)"`) or purely formal numbering (e.g. `"D.Lgs. 9 aprile 2008, n. 81, Art. 37"`)?

### b. Brief Background
In Italian legal QA workflows, having the official article rubric/title helps automated editorial and QA agents immediately verify the topic and scope of the referenced norm without performing secondary lookups.

### c. Options with Recommendation
- **Option 1 (Recommended)**: Include the official article/law rubric title in parentheses within `canonical_citation` (e.g., `"D.Lgs. 9 aprile 2008, n. 81, Art. 37 (Formazione dei lavoratori e dei loro rappresentanti)"`) and provide the clean base law in `official_reference` (e.g., `"D.Lgs. 9 aprile 2008, n. 81"`).
- **Option 2**: Use strictly number-only strings in `canonical_citation` (e.g., `"D.Lgs. 9 aprile 2008, n. 81, Art. 37"`).

### d. Justification of the Recommendation
Option 1 provides richer context to downstream LLM agents (Scout, Writer, Legal-QA) and QA evaluation benchmarks while maintaining strict legal accuracy and full traceability via `official_reference` and `official_url`.
