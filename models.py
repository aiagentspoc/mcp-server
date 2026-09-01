"""Data models for the HSE Easy Mock MCP Server.

Defines two-tier Pydantic v2 schemas for regulatory updates,
deep legal documents, citation verification, and commercial service offerings.
"""

from typing import List, Literal, Optional
from pydantic import BaseModel, ConfigDict, Field


class RegulatoryUpdateSummary(BaseModel):
    """Tier 1 lightweight summary model for HSE regulatory updates."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    doc_id: str = Field(
        ...,
        description="Unique slug identifier (e.g. 'gu-2024-dl-preposti', 'eurlex-dir-2024-869')",
    )
    source: Literal["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"] = Field(
        ...,
        description="Authoritative regulatory source body",
    )
    doc_type: Literal["directive", "regulation", "decree", "circular", "guideline"] = Field(
        ...,
        description="Legal instrument category",
    )
    official_reference: str = Field(
        ...,
        description="Canonical legal reference (e.g. 'D.Lgs. 81/2008', 'Direttiva (UE) 2024/869')",
    )
    title: str = Field(
        ...,
        description="Official title of the regulatory act in Italian",
    )
    publication_date: str = Field(
        ...,
        description="Publication date formatted as ISO 8601 YYYY-MM-DD",
    )
    effective_date: Optional[str] = Field(
        default=None,
        description="Date when obligations enter into force (YYYY-MM-DD)",
    )
    impact_level: Literal["critical", "high", "medium", "low"] = Field(
        ...,
        description="Editorial urgency and operational impact rating for Scout triage",
    )
    topic_tags: List[str] = Field(
        default_factory=list,
        description="HSE domain tags (e.g. ['workplace_safety', 'training', 'chemical_risk'])",
    )
    summary: str = Field(
        ...,
        description="1-2 paragraph plain-language executive summary of the act and affected parties",
    )
    canonical_url: str = Field(
        ...,
        description="Official direct URL to the gazette or portal publication",
    )


class RegulatoryDocument(RegulatoryUpdateSummary):
    """Tier 2 comprehensive document model including deep legal obligations, sanctions, and text."""

    status: Literal["in_force", "amended", "repealed", "proposed"] = Field(
        ...,
        description="Current legal status of the document",
    )
    target_sectors: List[str] = Field(
        default_factory=list,
        description="Applicable industrial and commercial sectors (e.g. ['manufacturing', 'construction'])",
    )
    key_obligations: List[str] = Field(
        default_factory=list,
        description="Explicit compliance obligations for employers, HSE managers, and RSPPs",
    )
    penalties_summary: Optional[str] = Field(
        default=None,
        description="Summary of legal sanctions, administrative fines, or criminal liabilities",
    )
    related_citations: List[str] = Field(
        default_factory=list,
        description="Referenced national and European laws, standards, or articles",
    )
    content_markdown: str = Field(
        ...,
        description="Cleaned, structured full text or article breakdown in Markdown",
    )

    def to_summary(self) -> RegulatoryUpdateSummary:
        """Converts Tier 2 RegulatoryDocument into Tier 1 RegulatoryUpdateSummary."""
        exclude_fields = {
            "status",
            "target_sectors",
            "key_obligations",
            "penalties_summary",
            "related_citations",
            "content_markdown",
        }
        return RegulatoryUpdateSummary(**self.model_dump(exclude=exclude_fields))


class CitationVerificationResult(BaseModel):
    """Legal citation verification result returned by legal QA tools."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    citation_input: str = Field(
        ...,
        description="The raw citation text submitted for verification",
    )
    is_valid: bool = Field(
        ...,
        description="True if the reference exists, is legally sound, and verified",
    )
    status: Literal["in_force", "amended", "repealed", "unrecognized"] = Field(
        ...,
        description="Legal validity status of the cited provision",
    )
    canonical_citation: str = Field(
        ...,
        description="Standardized legal citation text (e.g. 'D.Lgs. 9 aprile 2008, n. 81, Art. 37')",
    )
    official_reference: Optional[str] = Field(
        default=None,
        description="Base parent law reference",
    )
    official_url: Optional[str] = Field(
        default=None,
        description="Direct link to the verified article on official portal (Normattiva/EUR-Lex)",
    )
    verified_against_doc_id: Optional[str] = Field(
        default=None,
        description="Matching document ID in the mock corpus if available",
    )
    notes: Optional[str] = Field(
        default=None,
        description="Legal nuances, recent amendment history, or transitional provisions",
    )


class TDIServiceOffering(BaseModel):
    """Commercial service offering and pre-approved CTA templates for lead conversion."""

    model_config = ConfigDict(extra="ignore", populate_by_name=True)

    service_id: str = Field(
        ...,
        description="Unique identifier for the TDI commercial service",
    )
    service_name: str = Field(
        ...,
        description="Official commercial title of the consulting or training service",
    )
    topic_category: str = Field(
        ...,
        description="Primary matching HSE topic category",
    )
    applicable_sectors: List[str] = Field(
        default_factory=list,
        description="Target industry sectors",
    )
    value_proposition: str = Field(
        ...,
        description="1-2 sentence value proposition explaining TDI's technical capability",
    )
    cta_headline: str = Field(
        ...,
        description="Conversion-focused headline for editorial Call-to-Action insertion",
    )
    cta_body: str = Field(
        ...,
        description="Persuasive body copy tailored to the regulatory risk and TDI solution",
    )
    landing_page_url: str = Field(
        ...,
        description="Canonical URL for lead capture and inquiry booking",
    )
