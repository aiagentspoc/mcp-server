# HSE Easy Mock MCP Server — Specifications
Document Version: 1.0.0
Project: HSE Easy Proof-of-Concept (POC A & POC B)
Target Audience: Antigravity Engineering & AI Agent Development Teams
Protocol: Model Context Protocol (MCP) via stdio Transport
Implementation Stack: Python 3.10+, FastMCP, Pydantic v2
## 1. Executive Summary & Objective
The HSE Easy Mock MCP Server provides a deterministic, protocol-compliant regulatory data substrate and commercial service mapping layer for the HSE Easy Proof-of-Concept. It acts as the single data interface for Strands AI agents across two distinct architectural implementations:
POC A (Content Factory): AWS Step Functions code-orchestrated pipeline turning regulatory updates into articles at scale.
POC B (Research Analyst): Agent-orchestrated supervisor investigating complex regulatory topics with autonomous loop revisions.
### Primary Goals
Authoritative Regulatory Emulation: Standardize heterogeneous legal updates from EUR-Lex, Gazzetta Ufficiale, and INAIL into unified, token-efficient Pydantic schemas.
Citation Verification: Expose deterministic legal lookup to validate articles, decrees, and official reference URLs for the QA-Legal agent.
Commercial Conversion: Map regulatory domains to pre-approved TDI service offerings and Call-to-Action (CTA) templates to fulfill lead-generation metrics.
Zero-Friction Local Execution: Run over stdio without external database, network, or cloud dependencies.
## 2. Technical Stack & Protocol Specifications
### Execution Commands
# Install dependencies
uv sync
# Run development server with interactive MCP Inspector
uv run fastmcp dev server.py
# Run standard stdio server for Strands agents / MCP clients
uv run python server.py
## 3. Data Schemas (Pydantic Models)
The server enforces a Two-Tier Schema strategy: Tier 1 models are lightweight summaries designed to conserve token context during feed polling and searches, while Tier 2 models provide deep legal content when a specific document is fetched.
### 3.1. Tier 1: RegulatoryUpdateSummary
Returned by list_regulatory_updates and search_regulatory_docs.
from typing import List, Literal, Optional
from pydantic import BaseModel, Field
class RegulatoryUpdateSummary(BaseModel):
doc_id: str = Field(
description="Unique slug identifier (e.g. 'gu-2024-dl-preposti', 'eurlex-dir-2024-869')"
)
source: Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"] = Field(
description="Authoritative regulatory source body"
)
doc_type: Literal["directive", "regulation", "decree", "circular", "guideline"] = Field(
description="Legal instrument category"
)
official_reference: str = Field(
description="Canonical legal reference (e.g. 'D.Lgs. 81/2008', 'Direttiva (UE) 2024/869')"
)
title: str = Field(
description="Official title of the regulatory act in Italian"
)
publication_date: str = Field(
description="Publication date formatted as ISO 8601 YYYY-MM-DD"
)
effective_date: Optional[str] = Field(
default=None,
description="Date when obligations enter into force (YYYY-MM-DD)"
)
impact_level: Literal["critical", "high", "medium", "low"] = Field(
description="Editorial urgency and operational impact rating for Scout triage"
)
topic_tags: List[str] = Field(
description="HSE domain tags (e.g. ['workplace_safety', 'training', 'chemical_risk'])"
)
summary: str = Field(
description="1-2 paragraph plain-language executive summary of the act and affected parties"
)
canonical_url: str = Field(
description="Official direct URL to the gazette or portal publication"
)
### 3.2. Tier 2: RegulatoryDocument
Returned by get_document_by_id. Contains all summary fields plus deep legal content and obligations.
class RegulatoryDocument(RegulatoryUpdateSummary):
status: Literal["in_force", "amended", "repealed", "proposed"] = Field(
description="Current legal status of the document"
)
target_sectors: List[str] = Field(
description="Applicable industrial and commercial sectors (e.g. ['manufacturing', 'construction'])"
)
key_obligations: List[str] = Field(
description="Explicit compliance obligations for employers, HSE managers, and RSPPs"
)
penalties_summary: Optional[str] = Field(
default=None,
description="Summary of legal sanctions, administrative fines, or criminal liabilities"
)
related_citations: List[str] = Field(
description="Referenced national and European laws, standards, or articles"
)
content_markdown: str = Field(
description="Cleaned, structured full text or article breakdown in Markdown"
)
### 3.3. Legal Citation: CitationVerificationResult
Returned by verify_legal_citation.
class CitationVerificationResult(BaseModel):
citation_input: str = Field(
description="The raw citation text submitted for verification"
)
is_valid: bool = Field(
description="True if the reference exists, is legally sound, and verified"
)
status: Literal["in_force", "amended", "repealed", "unrecognized"] = Field(
description="Legal validity status of the cited provision"
)
canonical_citation: str = Field(
description="Standardized legal citation text (e.g. 'D.Lgs. 9 aprile 2008, n. 81, Art. 37')"
)
official_reference: Optional[str] = Field(
default=None,
description="Base parent law reference"
)
official_url: Optional[str] = Field(
default=None,
description="Direct link to the verified article on official portal (Normattiva/EUR-Lex)"
)
verified_against_doc_id: Optional[str] = Field(
default=None,
description="Matching document ID in the mock corpus if available"
)
notes: Optional[str] = Field(
default=None,
description="Legal nuances, recent amendment history, or transitional provisions"
)
### 3.4. Commercial Conversion: TDIServiceOffering
Returned by get_tdi_service_offerings.
class TDIServiceOffering(BaseModel):
service_id: str = Field(
description="Unique identifier for the TDI commercial service"
)
service_name: str = Field(
description="Official commercial title of the consulting or training service"
)
topic_category: str = Field(
description="Primary matching HSE topic category"
)
applicable_sectors: List[str] = Field(
description="Target industry sectors"
)
value_proposition: str = Field(
description="1-2 sentence value proposition explaining TDI's technical capability"
)
cta_headline: str = Field(
description="Conversion-focused headline for editorial Call-to-Action insertion"
)
cta_body: str = Field(
description="Persuasive body copy tailored to the regulatory risk and TDI solution"
)
landing_page_url: str = Field(
description="Canonical URL for lead capture and inquiry booking"
)
## 4. Tool Interface Definitions & Signatures
from typing import List, Optional
from fastmcp import FastMCP
mcp = FastMCP("HSE-Easy-Mock-Server")
### 4.1. list_regulatory_updates
Purpose: Enables the Scout Agent to monitor new regulatory entries and triage what is newsworthy.
Signature:
@mcp.tool(
description=(
"Lists recent HSE regulatory updates, decrees, and circulars across EUR-Lex, "
"Gazzetta Ufficiale, and INAIL within an optional date window. Returns lightweight "
"metadata summaries for feed monitoring and newsworthiness triage."
)
)
def list_regulatory_updates(
source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None,
date_from: Optional[str] = None,
date_to: Optional[str] = None,
limit: int = 10
) -> List[RegulatoryUpdateSummary]:
...
### 4.2. search_regulatory_docs
Purpose: Enables the Scout and Writer Agents to search regulations by keyword, topic tags, or authority.
Signature:
@mcp.tool(
description=(
"Searches the regulatory database by keyword, topic category, or source authority. "
"Returns matching document summaries and unique IDs for discovery."
)
)
def search_regulatory_docs(
query: str,
source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None,
topic: Optional[str] = None
) -> List[RegulatoryUpdateSummary]:
...
### 4.3. get_document_by_id
Purpose: Enables the Writer and QA-Legal Agents to fetch full legal text, compliance obligations, and sanctions.
Signature:
@mcp.tool(
description=(
"Retrieves the full structured text, article breakdown, legal obligations, "
"and official metadata for a specific regulatory document by its ID."
)
)
def get_document_by_id(
doc_id: str
) -> RegulatoryDocument:
...
Error Behavior: Raises ValueError("Document with ID '{doc_id}' not found.") if not matched.
### 4.4. verify_legal_citation
Purpose: Enables the QA-Legal Agent to verify that any legal reference in a generated draft is legally valid, currently in force, and backed by an official URL.
Signature:
@mcp.tool(
description=(
"Verifies whether a specific legal reference or article citation "
"(e.g., 'D.Lgs. 81/2008 Art. 37') exists and is currently in force. "
"Returns canonical citation text and official source URLs for legal QA."
)
)
def verify_legal_citation(
citation: str,
source: Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]] = None
) -> CitationVerificationResult:
...
### 4.5. get_tdi_service_offerings
Purpose: Enables the Writer Agent and Assembly Step to attach matching commercial services and conversion CTAs.
Signature:
@mcp.tool(
description=(
"Retrieves relevant TDI consulting services, compliance audit offerings, "
"and pre-approved Call-to-Action (CTA) templates matching a specific HSE "
"regulatory topic or industry sector for commercial lead generation."
)
)
def get_tdi_service_offerings(
topic: str,
sector: Optional[str] = None
) -> List[TDIServiceOffering]:
...
## 5. Mock Fixture Datasets (Pre-Seeded Scenarios)
The server loads three JSON fixture files from fixtures/:
### 5.1. Regulatory Documents (fixtures/regulatory_docs.json)
Contains 5 comprehensive HSE legal scenarios across all authorities:
eurlex-dir-2024-869 (EUR-Lex):
Title: Direttiva (UE) 2024/869 sui valori limite di esposizione professionale per piombo e diisocianati.
Doc Type: directive | Impact: critical | Status: in_force
Topic Tags: ["chemical_risk", "occupational_health", "cmrd_substances"]
Key Obligations: Revision of biological limit values for inorganic lead; mandatory training for workers handling diisocyanates.
eurlex-reg-2023-1230 (EUR-Lex):
Title: Regolamento (UE) 2023/1230 relativo alle macchine e che abroga la direttiva 2006/42/CE.
Doc Type: regulation | Impact: high | Status: in_force
Topic Tags: ["machinery", "ce_marking", "industrial_safety", "ai_safety"]
Key Obligations: Digital user manuals allowed; mandatory risk assessment for autonomous mobile robots and AI-driven safety software.
gu-2024-dl-preposti (Gazzetta Ufficiale):
Title: Aggiornamento D.Lgs. 81/2008: Nuovi obblighi formativi e nomina obbligatoria dei Preposti.
Doc Type: decree | Impact: critical | Status: in_force
Topic Tags: ["workplace_safety", "preposti_training", "dvr", "dlgs_81_08"]
Key Obligations: Mandatory written appointment of preposti in all contracting environments; biennial refresher training; power to halt non-compliant operations.
gu-2023-dm-antincendio (Gazzetta Ufficiale):
Title: Decreto Interministeriale sulla gestione della sicurezza antincendio nei luoghi di lavoro ad alto rischio.
Doc Type: decree | Impact: high | Status: in_force
Topic Tags: ["fire_safety", "emergency_plans", "high_risk_plants"]
Key Obligations: Updated fire risk assessments according to Ministerial Decree criteria; specific certification for emergency response team members.
inail-2024-circ-calore (INAIL):
Title: Circolare INAIL n. 28/2024: Linee guida per la prevenzione del rischio da stress termico e colpi di calore nei cantieri e in agricoltura.
Doc Type: circular | Impact: high | Status: in_force
Topic Tags: ["heat_stress", "microclimate", "construction_safety", "workplace_health"]
Key Obligations: Reorganization of shift hours during extreme heat alerts (>35°C); provision of shaded rest areas and hydration points; integration into the DVR.
### 5.2. Citations Index (fixtures/citations.json)
Pre-indexed legal citations for rapid QA testing:
Valid citations: D.Lgs. 81/2008 Art. 37, D.Lgs. 81/2008 Art. 18, Direttiva 2004/37/CE, Regolamento (UE) 2023/1230 Art. 10, Circolare INAIL 28/2024.
Invalid / Outdated test citations: D.P.R. 547/55 Art. 10 (repealed), D.Lgs. 626/94 Art. 3 (repealed by D.Lgs. 81/08), Direttiva 98/37/CE (repealed).
### 5.3. TDI Commercial Services (fixtures/tdi_services.json)
tdi-srv-preposti-training:
Service: Corso di Formazione e Aggiornamento Preposti (D.Lgs. 81/08).
Topic: workplace_safety / preposti_training
CTA Headline: "Adeguati ai nuovi obblighi formativi per i Preposti prima delle verifiche ispettive."
tdi-srv-chemical-audit:
Service: Audit di Conformità Rischio Chimico e Sostanze CMR.
Topic: chemical_risk / cmrd_substances
CTA Headline: "Aggiorna la valutazione rischio chimico e i valori limite biologici con i tecnici TDI."
tdi-srv-machinery-ce:
Service: Consulenza Nuovo Regolamento Macchine (UE) 2023/1230 e Marcatura CE.
Topic: machinery / ce_marking
CTA Headline: "Verifica la conformità del tuo parco macchine al nuovo Regolamento UE 2023/1230."
tdi-srv-heat-stress:
Service: Protocollo Valutazione Rischio Microclima e Stress da Calore.
Topic: heat_stress / microclimate
CTA Headline: "Proteggi i tuoi lavoratori all'aperto: richiedi il protocollo anti-calore personalizzato."
## 6. Acceptance & Verification Criteria
To certify completion of the Mock MCP server implementation:
FastMCP Inspector Verification: All 5 tools appear with full parameter descriptions in fastmcp dev server.py.
Deterministic Response Time: All tool invocations execute in under 15ms over stdio.
Pydantic Validation: Return payloads strictly validate against their respective schemas without missing required fields.
QA-Legal Test Case: Calling verify_legal_citation("D.Lgs. 81/2008 Art. 37") returns is_valid: true, and calling verify_legal_citation("D.Lgs. 626/94 Art. 3") returns is_valid: false with status repealed.
Commercial CTA Test Case: Calling get_tdi_service_offerings("chemical_risk") returns tdi-srv-chemical-audit with full CTA fields.

| Component | Specification |
| --- | --- |
| Language & Runtime | Python 3.10+ |
| MCP Framework | fastmcp>=0.1.0 |
| Data Validation | pydantic>=2.0.0 |
| Transport | Standard Input/Output (stdio) |
| Data Store | In-memory JSON fixtures loaded on server initialization |
| Package Management | uv / pip (pyproject.toml) |
| Client Support | Strands Agent SDK, AWS Bedrock AgentCore, MCP Inspector |
