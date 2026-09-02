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


def test_server_indexing_loader_simulation():
    """Simulate server.py startup loading pattern to ensure zero-friction in-memory indexing."""
    with open(REGULATORY_DOCS_PATH, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    docs = [RegulatoryDocument(**d) for d in raw_data]
    docs_by_id = {doc.doc_id: doc for doc in docs}

    for expected_id in EXPECTED_DOC_IDS:
        assert expected_id in docs_by_id
        retrieved = docs_by_id[expected_id]
        assert retrieved.doc_id == expected_id


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


def test_citations_alias_uniqueness_and_normalization_simulation():
    """Simulate server.py lookup normalization across aliases, ensuring no collisions and 100% resolution."""
    with open(CITATIONS_PATH, "r", encoding="utf-8") as f:
        citations = json.load(f)

    alias_map = {}
    for entry in citations:
        canonical_input = entry["citation_input"]
        all_keys = [canonical_input] + entry.get("aliases", [])
        for key in all_keys:
            normalized_key = key.strip().lower()
            assert normalized_key not in alias_map or alias_map[normalized_key] == canonical_input, (
                f"Alias collision detected for '{normalized_key}' between '{alias_map.get(normalized_key)}' and '{canonical_input}'"
            )
            alias_map[normalized_key] = canonical_input

    # Test sample noisy queries matching against registry
    test_queries = [
        ("  D.LGS. 81/2008 Art. 37  ", "D.Lgs. 81/2008 Art. 37", True, "in_force"),
        ("dlgs 81/08 art 37", "D.Lgs. 81/2008 Art. 37", True, "in_force"),
        ("DECRETO LEGISLATIVO 81/08 ART 37", "D.Lgs. 81/2008 Art. 37", True, "in_force"),
        ("d.lgs. 626/94 art. 3", "D.Lgs. 626/94 Art. 3", False, "repealed"),
        ("dlgs 626/94 art 3", "D.Lgs. 626/94 Art. 3", False, "repealed"),
        ("direttiva 98/37/ce", "Direttiva 98/37/CE", False, "repealed"),
        ("direttiva macchine 98/37", "Direttiva 98/37/CE", False, "repealed"),
        ("circolare inail 28/2024", "Circolare INAIL 28/2024", True, "in_force"),
        ("regolamento (ue) 2023/1230 art 10", "Regolamento (UE) 2023/1230 Art. 10", True, "in_force"),
    ]

    for raw_query, expected_input, expected_valid, expected_status in test_queries:
        norm = raw_query.strip().lower()
        assert norm in alias_map, f"Failed to match query '{raw_query}' (normalized: '{norm}') in alias index"
        matched_input = alias_map[norm]
        assert matched_input == expected_input

        # Lookup entry
        entry = next(c for c in citations if c["citation_input"] == matched_input)
        result = CitationVerificationResult(**entry)
        assert result.is_valid == expected_valid
        assert result.status == expected_status


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


def test_tdi_services_topic_and_sector_matching_simulation():
    """Simulate server.py get_tdi_service_offerings matching logic across topics and sectors."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        raw_services = json.load(f)

    services = [TDIServiceOffering(**s) for s in raw_services]

    # 1. Match by topic_category: "chemical_risk"
    chemical_matches = [
        s for s in services
        if "chemical_risk" in s.topic_category.lower()
        or any("chemical_risk" in sec.lower() for sec in s.applicable_sectors)
    ]
    assert len(chemical_matches) >= 1
    assert chemical_matches[0].service_id == "tdi-srv-chemical-audit"

    # 2. Match by topic_category: "machinery"
    machinery_matches = [
        s for s in services
        if "machinery" in s.topic_category.lower()
        or any("machinery" in sec.lower() for sec in s.applicable_sectors)
    ]
    assert len(machinery_matches) >= 1
    assert machinery_matches[0].service_id == "tdi-srv-machinery-ce"

    # 3. Match by topic_category: "heat_stress"
    heat_matches = [
        s for s in services
        if "heat_stress" in s.topic_category.lower()
        or any("heat_stress" in sec.lower() for sec in s.applicable_sectors)
    ]
    assert len(heat_matches) >= 1
    assert heat_matches[0].service_id == "tdi-srv-heat-stress"

    # 4. Match by topic_category: "workplace_safety"
    safety_matches = [
        s for s in services
        if "workplace_safety" in s.topic_category.lower()
        or any("workplace_safety" in sec.lower() for sec in s.applicable_sectors)
    ]
    assert len(safety_matches) >= 1
    assert safety_matches[0].service_id == "tdi-srv-preposti-training"

    # 5. Match by sector: "construction"
    construction_matches = [
        s for s in services
        if "construction" in s.topic_category.lower()
        or any("construction" in sec.lower() for sec in s.applicable_sectors)
    ]
    assert len(construction_matches) >= 2
    matched_ids = {s.service_id for s in construction_matches}
    assert "tdi-srv-preposti-training" in matched_ids
    assert "tdi-srv-heat-stress" in matched_ids


def test_tdi_services_fallback_behavior_simulation():
    """Simulate server.py deterministic fallback behavior when no topic or sector matches."""
    with open(TDI_SERVICES_PATH, "r", encoding="utf-8") as f:
        raw_services = json.load(f)

    services = [TDIServiceOffering(**s) for s in raw_services]

    def mock_get_tdi_service_offerings(topic: str, sector: str = None):
        val = topic.lower()
        sec = sector.lower() if sector else None
        matches = [
            s for s in services
            if val in s.topic_category.lower()
            or any(val in item.lower() for item in s.applicable_sectors)
            or (sec and any(sec in item.lower() for item in s.applicable_sectors))
        ]
        return matches or services[:1]

    fallback_result = mock_get_tdi_service_offerings("unknown_arbitrary_topic_999")
    assert len(fallback_result) == 1
    assert fallback_result[0].service_id == "tdi-srv-preposti-training"
    assert fallback_result[0].topic_category == "workplace_safety"

