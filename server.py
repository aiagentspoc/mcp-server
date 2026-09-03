import json
from operator import attrgetter
from pathlib import Path
from typing import List, Literal, Optional, Annotated

from fastmcp import FastMCP
from pydantic import Field

from models import (
    CitationVerificationResult,
    RegulatoryDocument,
    RegulatoryUpdateSummary,
    TDIServiceOffering,
)

mcp = FastMCP("HSE-Easy-Mock-Server")
FIXTURES_DIR = Path(__file__).parent / "fixtures"

# 1. Load regulatory documents and validate via Pydantic model
with open(FIXTURES_DIR / "regulatory_docs.json", encoding="utf-8") as f:
    REGULATORY_DOCS = [RegulatoryDocument(**d) for d in json.load(f)]

# 2. Load citations as raw dicts (preserves aliases for lookup logic)
with open(FIXTURES_DIR / "citations.json", encoding="utf-8") as f:
    CITATIONS_RAW = json.load(f)

# 3. Load TDI services and validate via Pydantic model
with open(FIXTURES_DIR / "tdi_services.json", encoding="utf-8") as f:
    TDI_SERVICES = [TDIServiceOffering(**s) for s in json.load(f)]

# Summary exclusions used to downcast Tier 2 to Tier 1 schema
SUMMARY_EXCLUDE = {
    "status", "target_sectors", "key_obligations", "penalties_summary",
    "related_citations", "content_markdown",
}

def to_summary(doc: RegulatoryDocument) -> RegulatoryUpdateSummary:
    """Helper to convert Tier 2 doc to Tier 1 summary."""
    return RegulatoryUpdateSummary(**doc.model_dump(exclude=SUMMARY_EXCLUDE))

@mcp.tool(
    description=(
        "Lists recent HSE regulatory updates, decrees, and circulars across EUR-Lex, "
        "Gazzetta Ufficiale, and INAIL within an optional date window. Returns lightweight "
        "metadata summaries for feed monitoring and newsworthiness triage."
    )
)
def list_regulatory_updates(
    source: Annotated[Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]], Field(
        default=None, description="Authoritative regulatory source body to filter by."
    )] = None,
    date_from: Annotated[Optional[str], Field(
        default=None, description="Start of publication date window (ISO 8601 YYYY-MM-DD)."
    )] = None,
    date_to: Annotated[Optional[str], Field(
        default=None, description="End of publication date window (ISO 8601 YYYY-MM-DD)."
    )] = None,
    limit: Annotated[int, Field(
        default=10, description="Maximum number of updates to return."
    )] = 10,
) -> List[RegulatoryUpdateSummary]:
    """
    List recent HSE regulatory updates across sources.
    
    This tool allows monitoring of new regulatory entries to triage what is newsworthy.
    It returns lightweight metadata summaries.
    """
    results = REGULATORY_DOCS
    if source:
        results = [d for d in results if d.source == source]
    if date_from:
        results = [d for d in results if d.publication_date >= date_from]
    if date_to:
        results = [d for d in results if d.publication_date <= date_to]
    return [to_summary(d) for d in sorted(
        results, key=attrgetter("publication_date"), reverse=True
    )[:limit]]


@mcp.tool(
    description=(
        "Searches the regulatory database by keyword, topic category, or source authority. "
        "Returns matching document summaries and unique IDs for discovery."
    )
)
def search_regulatory_docs(
    query: Annotated[str, Field(
        description="Keyword to search in titles, summaries, references, and topics."
    )],
    source: Annotated[Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]], Field(
        default=None, description="Authoritative regulatory source body to filter by."
    )] = None,
    topic: Annotated[Optional[str], Field(
        default=None, description="HSE topic category to filter by (e.g. workplace_safety)."
    )] = None,
) -> List[RegulatoryUpdateSummary]:
    """
    Search the regulatory database by keyword, topic, or authority.
    
    This tool enables agents to search regulations across the available mock dataset.
    """
    q = query.lower()
    matches = []
    for doc in REGULATORY_DOCS:
        if source and doc.source != source:
            continue
        if topic and topic.lower() not in [t.lower() for t in doc.topic_tags]:
            continue
        if (q in doc.title.lower() or q in doc.summary.lower()
                or q in doc.official_reference.lower()
                or any(q in t.lower() for t in doc.topic_tags)):
            matches.append(doc)
    return [to_summary(d) for d in matches]


@mcp.tool(
    description=(
        "Retrieves the full structured text, article breakdown, legal obligations, "
        "and official metadata for a specific regulatory document by its ID."
    )
)
def get_document_by_id(
    doc_id: Annotated[str, Field(
        description="Unique slug identifier of the regulatory document to retrieve."
    )]
) -> RegulatoryDocument:
    """
    Retrieve full text and compliance obligations by document ID.
    
    Raises:
        ValueError: If a document with the provided `doc_id` is not found.
    """
    for doc in REGULATORY_DOCS:
        if doc.doc_id == doc_id:
            return doc
    raise ValueError(f"Document with ID '{doc_id}' not found.")


@mcp.tool(
    description=(
        "Verifies whether a specific legal reference or article citation "
        "(e.g., 'D.Lgs. 81/2008 Art. 37') exists and is currently in force. "
        "Returns canonical citation text and official source URLs for legal QA."
    )
)
def verify_legal_citation(
    citation: Annotated[str, Field(
        description="The raw legal reference or article citation text to verify."
    )],
    source: Annotated[Optional[Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"]], Field(
        default=None, description="Optional authoritative regulatory source body."
    )] = None,
) -> CitationVerificationResult:
    """
    Verify legal citation validity, status, and canonical URL.
    
    This tool checks if a given reference is legally sound and currently in force,
    returning official metadata and URLs.
    """
    normalized = citation.strip().lower()
    for entry in CITATIONS_RAW:
        aliases = [a.lower() for a in entry.get("aliases", [])]
        aliases.append(entry["citation_input"].lower())
        if normalized in aliases:
            return CitationVerificationResult(**entry)
    return CitationVerificationResult(
        citation_input=citation,
        is_valid=False,
        status="unrecognized",
        canonical_citation=citation,
        notes="Citation not recognized in authoritative legal registry.",
    )


@mcp.tool(
    description=(
        "Retrieves relevant TDI consulting services, compliance audit offerings, "
        "and pre-approved Call-to-Action (CTA) templates matching a specific HSE "
        "regulatory topic or industry sector for commercial lead generation."
    )
)
def get_tdi_service_offerings(
    topic: Annotated[str, Field(
        description="HSE regulatory topic category to match services for."
    )],
    sector: Annotated[Optional[str], Field(
        default=None, description="Optional target industry sector to filter by."
    )] = None,
) -> List[TDIServiceOffering]:
    """
    Retrieve relevant TDI services and pre-approved calls to action.
    
    This tool helps attach matching commercial services and conversion CTAs
    to regulatory content.
    """
    value = topic.lower()
    matches = [
        service for service in TDI_SERVICES
        if value in service.topic_category.lower()
        or any(value in item.lower() for item in service.applicable_sectors)
    ]
    return matches or TDI_SERVICES[:1]

if __name__ == "__main__":
    mcp.run()

