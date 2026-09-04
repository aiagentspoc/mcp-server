"""Test suite for validating JSON fixture datasets against Pydantic models."""

import json
from pathlib import Path
import re
import pytest
from pydantic import ValidationError

from models import (
    CitationVerificationResult,
    RegulatoryDocument,
    RegulatoryUpdateSummary,
    TDIServiceOffering,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"
REGULATORY_DOCS_PATH = FIXTURES_DIR / "regulatory_docs.json"
CITATIONS_PATH = FIXTURES_DIR / "citations.json"
TDI_SERVICES_PATH = FIXTURES_DIR / "tdi_services.json"
ISO_DATE_REGEX = re.compile(r"^\d{4}-\d{2}-\d{2}$")

EXPECTED_DOC_IDS = {
    "eurlex-dir-2024-869",
    "eurlex-reg-2023-1230",
    "gu-2024-dl-preposti",
    "gu-2023-dm-antincendio",
    "inail-2024-circ-calore",
}

MANDATORY_ROADMAP_CITATIONS = {
    "D.Lgs. 81/2008 Art. 37": {"is_valid": True, "status": "in_force"},
    "D.Lgs. 81/2008 Art. 18": {"is_valid": True, "status": "in_force"},
    "Direttiva 2004/37/CE": {"is_valid": True, "status": "amended"},
    "Regolamento (UE) 2023/1230 Art. 10": {"is_valid": True, "status": "in_force"},
    "Circolare INAIL 28/2024": {"is_valid": True, "status": "in_force"},
    "D.P.R. 547/55 Art. 10": {"is_valid": False, "status": "repealed"},
    "D.Lgs. 626/94 Art. 3": {"is_valid": False, "status": "repealed"},
    "Direttiva 98/37/CE": {"is_valid": False, "status": "repealed"},
}

EXPECTED_SERVICE_IDS = {
    "tdi-srv-preposti-training",
    "tdi-srv-chemical-audit",
    "tdi-srv-machinery-ce",
    "tdi-srv-heat-stress",
    "tdi-srv-fire-safety",
}

MANDATORY_ROADMAP_SERVICES = {
    "tdi-srv-preposti-training",
    "tdi-srv-chemical-audit",
    "tdi-srv-machinery-ce",
    "tdi-srv-heat-stress",
}


# ==========================================
# Regulatory Corpus Fixture Tests (Task 2.1)
# ==========================================


def test_regulatory_docs_fixture_exists_and_is_valid_json():
    """Verify that fixtures/regulatory_docs.json exists, parses as valid JSON, and contains 5 items."""
    assert REGULATORY_DOCS_PATH.exists(), f"Missing fixture file at {REGULATORY_DOCS_PATH}"
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) == 5, f"Expected exactly 5 documents, found {len(data)}"


def test_regulatory_docs_pydantic_hydration():
    """Verify that all items in regulatory_docs.json instantiate cleanly as RegulatoryDocument."""
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    docs = []
    for item in data:
        try:
            doc = RegulatoryDocument(**item)
            docs.append(doc)
        except ValidationError as e:
            pytest.fail(f"Failed to instantiate RegulatoryDocument for {item.get('doc_id')}: {e}")

    assert len(docs) == 5


def test_regulatory_docs_expected_identifiers():
    """Verify that all expected document IDs are present and unique."""
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    found_ids = [d["doc_id"] for d in data]
    assert len(found_ids) == len(set(found_ids)), "Duplicate doc_id detected in fixtures!"
    assert set(found_ids) == EXPECTED_DOC_IDS, f"Mismatch in expected doc_ids. Found: {set(found_ids)}"


def test_regulatory_docs_field_constraints_and_non_empty():
    """Verify that all required fields contain meaningful non-empty content."""
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        doc = RegulatoryDocument(**item)
        assert len(doc.doc_id.strip()) > 0
        assert doc.source in {"EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"}
        assert doc.doc_type in {"directive", "regulation", "decree", "circular", "guideline"}
        assert len(doc.official_reference.strip()) > 0
        assert len(doc.title.strip()) > 0
        assert ISO_DATE_REGEX.match(doc.publication_date)
        if doc.effective_date:
            assert ISO_DATE_REGEX.match(doc.effective_date)
        assert doc.impact_level in {"critical", "high", "medium", "low"}
        assert len(doc.topic_tags) >= 3, f"Document {doc.doc_id} should have at least 3 topic tags"
        assert len(doc.summary.strip()) > 50
        assert doc.canonical_url.startswith("http")
        assert doc.status in {"in_force", "amended", "repealed", "proposed"}
        assert len(doc.target_sectors) >= 2, f"Document {doc.doc_id} should target at least 2 sectors"
        assert len(doc.key_obligations) >= 3, f"Document {doc.doc_id} should specify at least 3 obligations"
        assert doc.penalties_summary is not None and len(doc.penalties_summary.strip()) > 20
        assert len(doc.related_citations) >= 2, f"Document {doc.doc_id} should reference at least 2 citations"
        assert len(doc.content_markdown.strip()) > 200, f"Document {doc.doc_id} content_markdown is too short"


def test_regulatory_docs_to_summary_projection():
    """Verify that every RegulatoryDocument can be projected down to RegulatoryUpdateSummary."""
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        doc = RegulatoryDocument(**item)
        summary = doc.to_summary()
        assert isinstance(summary, RegulatoryUpdateSummary)
        assert summary.doc_id == doc.doc_id
        assert summary.source == doc.source
        assert summary.doc_type == doc.doc_type
        assert summary.official_reference == doc.official_reference
        assert summary.title == doc.title
        assert summary.publication_date == doc.publication_date
        assert summary.effective_date == doc.effective_date
        assert summary.impact_level == doc.impact_level
        assert summary.topic_tags == doc.topic_tags
        assert summary.summary == doc.summary
        assert summary.canonical_url == doc.canonical_url



# ==========================================
# Legal Citations Fixture Tests (Task 2.2)
# ==========================================


def test_citations_fixture_exists_and_is_valid_json():
    """Verify that fixtures/citations.json exists, parses as valid JSON, and contains entries."""
    assert CITATIONS_PATH.exists(), f"Missing fixture file at {CITATIONS_PATH}"
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 15, f"Expected at least 15 citations, found {len(data)}"


def test_citations_pydantic_hydration():
    """Verify that all items in citations.json instantiate cleanly as CitationVerificationResult."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    results = []
    for item in data:
        try:
            res = CitationVerificationResult(**item)
            results.append(res)
        except ValidationError as e:
            pytest.fail(f"Failed to instantiate CitationVerificationResult for {item.get('citation_input')}: {e}")

    assert len(results) == len(data)


def test_citations_required_fields_and_enums():
    """Verify that every citation entry adheres to schema constraints, valid enums, and non-empty URLs."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        res = CitationVerificationResult(**item)
        assert len(res.citation_input.strip()) > 0
        assert isinstance(res.is_valid, bool)
        assert res.status in {"in_force", "amended", "repealed", "unrecognized"}
        assert len(res.canonical_citation.strip()) > 0
        assert res.official_reference is not None and len(res.official_reference.strip()) > 0
        assert res.official_url is not None and res.official_url.startswith("http")
        assert res.notes is not None and len(res.notes.strip()) > 10

        # Verify aliases list
        aliases = item.get("aliases", [])
        assert isinstance(aliases, list)
        assert len(aliases) >= 2, f"Citation '{res.citation_input}' should have at least 2 aliases"
        for alias in aliases:
            assert isinstance(alias, str)
            assert len(alias.strip()) > 0


def test_citations_mandatory_roadmap_cases():
    """Verify that all mandatory valid and repealed test cases from ROADMAP.md are present with expected status."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    citations_by_input = {item["citation_input"]: item for item in data}

    for mandatory_input, expected in MANDATORY_ROADMAP_CITATIONS.items():
        assert mandatory_input in citations_by_input, f"Mandatory citation '{mandatory_input}' not found in registry"
        actual = citations_by_input[mandatory_input]
        assert actual["is_valid"] == expected["is_valid"], (
            f"Citation '{mandatory_input}' expected is_valid={expected['is_valid']}, got {actual['is_valid']}"
        )
        assert actual["status"] == expected["status"], (
            f"Citation '{mandatory_input}' expected status={expected['status']}, got {actual['status']}"
        )


def test_citations_relational_integrity_with_regulatory_docs():
    """Verify that all non-null verified_against_doc_id references resolve to valid documents in regulatory_docs.json."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        citations = json.load(f)

    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        docs = json.load(f)
    valid_doc_ids = {d["doc_id"] for d in docs}

    for item in citations:
        doc_ref = item.get("verified_against_doc_id")
        if doc_ref is not None:
            assert doc_ref in valid_doc_ids, (
                f"Citation '{item['citation_input']}' references unknown doc_id '{doc_ref}'"
            )


def test_citations_fixture_alias_collision_free():
    """Verify that across all fixture records, no normalized alias belongs to more than one canonical citation record."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        citations = json.load(f)

    alias_map: dict[str, str] = {}
    for entry in citations:
        canonical = entry["canonical_citation"]
        all_keys = [entry["citation_input"]] + entry.get("aliases", [])
        for raw_key in all_keys:
            norm_key = raw_key.strip().lower()
            if norm_key in alias_map:
                assert alias_map[norm_key] == canonical, (
                    f"Collision in fixtures: key '{norm_key}' maps to both '{alias_map[norm_key]}' and '{canonical}'"
                )
            alias_map[norm_key] = canonical


# ==========================================
# TDI Commercial Services Fixture Tests (Task 2.3)
# ==========================================


def test_tdi_services_fixture_exists_and_is_valid_json():
    """Verify that fixtures/tdi_services.json exists, parses as valid JSON, and contains entries."""
    assert TDI_SERVICES_PATH.exists(), f"Missing fixture file at {TDI_SERVICES_PATH}"
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    assert isinstance(data, list)
    assert len(data) >= 4, f"Expected at least 4 TDI service offerings, found {len(data)}"


def test_tdi_services_pydantic_hydration():
    """Verify that all items in tdi_services.json instantiate cleanly as TDIServiceOffering."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    services = []
    for item in data:
        try:
            srv = TDIServiceOffering(**item)
            services.append(srv)
        except ValidationError as e:
            pytest.fail(f"Failed to instantiate TDIServiceOffering for {item.get('service_id')}: {e}")

    assert len(services) == len(data)


def test_tdi_services_expected_identifiers():
    """Verify that all expected TDI service IDs are present and unique."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    found_ids = [s["service_id"] for s in data]
    assert len(found_ids) == len(set(found_ids)), "Duplicate service_id detected in fixtures!"
    assert EXPECTED_SERVICE_IDS.issubset(set(found_ids)), f"Missing expected service_ids: {EXPECTED_SERVICE_IDS - set(found_ids)}"


def test_tdi_services_mandatory_roadmap_cases():
    """Verify that all 4 mandatory service offerings from ROADMAP.md are present."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    services_by_id = {s["service_id"]: s for s in data}
    for mandatory_id in MANDATORY_ROADMAP_SERVICES:
        assert mandatory_id in services_by_id, f"Mandatory service '{mandatory_id}' not found in catalog"


def test_tdi_services_field_constraints_and_non_empty():
    """Verify that all required fields in each TDI service offering contain meaningful non-empty content."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)

    for item in data:
        srv = TDIServiceOffering(**item)
        assert len(srv.service_id.strip()) > 0
        assert len(srv.service_name.strip()) > 10
        assert len(srv.topic_category.strip()) > 0
        assert len(srv.applicable_sectors) >= 2, f"Service {srv.service_id} should specify at least 2 sectors"
        for sector in srv.applicable_sectors:
            assert len(sector.strip()) > 0
        assert len(srv.value_proposition.strip()) > 30, f"Service {srv.service_id} value_proposition too short"
        assert len(srv.cta_headline.strip()) > 20, f"Service {srv.service_id} cta_headline too short"
        assert len(srv.cta_body.strip()) > 50, f"Service {srv.service_id} cta_body too short"
        assert srv.landing_page_url.startswith("https://"), f"Service {srv.service_id} invalid URL {srv.landing_page_url}"

