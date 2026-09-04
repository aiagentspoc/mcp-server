"""HSE Easy Mock MCP Server implementation."""

import json
import logging
import sys
from datetime import date
from operator import attrgetter
from pathlib import Path
from typing import Annotated, List, Literal, Optional

# Explicitly direct all root logging to stderr to preserve stdout for JSON-RPC
logging.basicConfig(stream=sys.stderr, level=logging.INFO, force=True)

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


class PreprocessedService:
    __slots__ = ("service", "index", "topic_category_lower", "sectors_lower")

    def __init__(self, service: TDIServiceOffering, index: int):
        self.service = service
        self.index = index
        self.topic_category_lower = service.topic_category.lower()
        self.sectors_lower = [sec.lower() for sec in service.applicable_sectors]


def load_fixtures_and_indexes(fixtures_dir: Optional[Path] = None) -> tuple[
    list[RegulatoryDocument],
    dict[str, RegulatoryDocument],
    list[RegulatoryDocument],
    dict[str, CitationVerificationResult],
    list[TDIServiceOffering],
    list[PreprocessedService],
    list[TDIServiceOffering],
]:
    """
    Loads and validates all JSON fixtures against Pydantic models, builds in-memory
    indexes with fail-fast collision checks, and returns the initialized data structures.
    """
    target_dir = fixtures_dir or FIXTURES_DIR

    # 1. Documents: Hydrate Pydantic models & in-memory indexes
    with open(target_dir / "regulatory_docs.json", encoding="utf-8") as f:
        docs = [RegulatoryDocument(**d) for d in json.load(f)]
    docs_by_id = {doc.doc_id: doc for doc in docs}
    docs_ordered_by_date = sorted(docs, key=attrgetter("publication_date"), reverse=True)

    # 2. Citations: Hydrate Pydantic models & build fail-fast collision-safe O(1) alias index
    with open(target_dir / "citations.json", encoding="utf-8") as f:
        citations_data = json.load(f)

    citations_by_alias: dict[str, CitationVerificationResult] = {}
    for entry in citations_data:
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
            if norm_key in citations_by_alias:
                existing = citations_by_alias[norm_key]
                if existing.canonical_citation != res.canonical_citation:
                    raise ValueError(
                        f"Startup citation alias collision: key '{norm_key}' maps to both "
                        f"'{existing.canonical_citation}' and '{res.canonical_citation}'."
                    )
            citations_by_alias[norm_key] = res

    # 3. TDI Services: Preprocessed structure consumed by search algorithm
    with open(target_dir / "tdi_services.json", encoding="utf-8") as f:
        tdi_services = [TDIServiceOffering(**s) for s in json.load(f)]

    indexed_tdi_services = [PreprocessedService(s, i) for i, s in enumerate(tdi_services)]
    fallback_tdi_service = [tdi_services[0]]

    return (
        docs,
        docs_by_id,
        docs_ordered_by_date,
        citations_by_alias,
        tdi_services,
        indexed_tdi_services,
        fallback_tdi_service,
    )


# Hydrate module-level production data structures upon startup
(
    REGULATORY_DOCS,
    DOCS_BY_ID,
    DOCS_ORDERED_BY_DATE,
    CITATIONS_BY_ALIAS,
    TDI_SERVICES,
    INDEXED_TDI_SERVICES,
    FALLBACK_TDI_SERVICE,
) = load_fixtures_and_indexes()

# Summary exclusions used to downcast Tier 2 to Tier 1 schema
SUMMARY_EXCLUDE = {
    "status",
    "target_sectors",
    "key_obligations",
    "penalties_summary",
    "related_citations",
    "content_markdown",
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
    limit = max(1, min(limit, 50))

    d_from = validate_strict_iso_date(date_from, "date_from") if date_from else None
    d_to = validate_strict_iso_date(date_to, "date_to") if date_to else None

    if d_from and d_to and d_from > d_to:
        raise ValueError(f"date_from ({date_from}) cannot be after date_to ({date_to}).")

    results = DOCS_ORDERED_BY_DATE
    if source:
        results = [d for d in results if d.source == source]
    if date_from:
        results = [d for d in results if d.publication_date >= date_from]
    if date_to:
        results = [d for d in results if d.publication_date <= date_to]

    return [to_summary(d) for d in results[:limit]]


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
    clean_query = query.strip()
    if not clean_query:
        return []
    q = clean_query.lower()
    clean_topic = topic.strip().lower() if topic else None

    matches = []
    for doc in DOCS_ORDERED_BY_DATE:
        if source and doc.source != source:
            continue
        if clean_topic and clean_topic not in [t.lower() for t in doc.topic_tags]:
            continue
        if (
            q in doc.title.lower()
            or q in doc.summary.lower()
            or q in doc.official_reference.lower()
            or any(q in t.lower() for t in doc.topic_tags)
        ):
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
    clean_id = doc_id.strip()
    doc = DOCS_BY_ID.get(clean_id)
    if doc is not None:
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
        default=None, description="Optional authoritative regulatory source body (backward-compatible no-op)."
    )] = None,
) -> CitationVerificationResult:
    """
    Verify legal citation validity, status, and canonical URL.

    This tool checks if a given reference is legally sound and currently in force,
    returning official metadata and URLs.

    Note: The `source` parameter is retained for backward compatibility as a no-op
    because legal citations in the registry are globally unique authoritative references.
    """
    citation_clean = citation.strip()
    if not citation_clean:
        return CitationVerificationResult(
            citation_input=citation,
            is_valid=False,
            status="unrecognized",
            canonical_citation="",
            notes="Empty citation provided.",
        )
    normalized = citation_clean.lower()
    if normalized in CITATIONS_BY_ALIAS:
        matched = CITATIONS_BY_ALIAS[normalized]
        return matched.model_copy(update={"citation_input": citation})

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
        description="HSE regulatory topic category to match services for (pass empty string for sector-only matching)."
    )],
    sector: Annotated[Optional[str], Field(
        default=None, description="Optional target industry sector to filter by."
    )] = None,
) -> List[TDIServiceOffering]:
    """
    Retrieve relevant TDI services and pre-approved calls to action.

    This tool helps attach matching commercial services and conversion CTAs
    to regulatory content. Sector-only matching can be performed by passing
    topic="" along with the desired sector.
    """
    t_query = topic.strip().lower() if topic else ""
    s_query = sector.strip().lower() if sector else ""

    if not t_query and not s_query:
        return FALLBACK_TDI_SERVICE

    scored_candidates: list[tuple[int, int, TDIServiceOffering]] = []

    for item in INDEXED_TDI_SERVICES:
        score = 0
        # Topic evaluation (category +2, sector +1)
        if t_query:
            if t_query in item.topic_category_lower:
                score += 2
            elif any(t_query in sec for sec in item.sectors_lower):
                score += 1

        # Sector evaluation (+1)
        if s_query and any(s_query in sec for sec in item.sectors_lower):
            score += 1

        if score > 0:
            scored_candidates.append((score, item.index, item.service))

    if not scored_candidates:
        return FALLBACK_TDI_SERVICE

    # Sort: primary key = -score (descending), tie-breaker = index (ascending fixture order)
    scored_candidates.sort(key=lambda c: (-c[0], c[1]))
    return [c[2] for c in scored_candidates]


def main() -> None:
    """Entry point for the hse-easy-mock console script and stdio transport execution."""
    mcp.run()


if __name__ == "__main__":
    main()
