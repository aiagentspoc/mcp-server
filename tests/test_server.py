"""Comprehensive test suite for HSE Easy Mock MCP Server tools and schema."""

import json
import pytest
from server import mcp
from models import RegulatoryDocument, RegulatoryUpdateSummary


def extract_json(result):
    assert not result.is_error
    if not result.content:
        if getattr(result, "structured_content", None) and "result" in result.structured_content:
            return result.structured_content["result"]
        return []
    text = result.content[0].text
    return json.loads(text)


@pytest.mark.asyncio
async def test_tools_list_schema_inspection():
    """Introspect mcp.list_tools() to assert all 5 tools are exposed with valid schemas."""
    tools = await mcp.list_tools()
    tool_map = {t.name: t for t in tools}
    expected_tools = {
        "list_regulatory_updates",
        "search_regulatory_docs",
        "get_document_by_id",
        "verify_legal_citation",
        "get_tdi_service_offerings",
    }
    assert expected_tools == set(tool_map.keys())

    for tool_name, tool in tool_map.items():
        assert tool.description is not None
        assert len(tool.description.strip()) > 20, f"Tool {tool_name} description too short"
        assert tool.parameters is not None
        assert "properties" in tool.parameters

    # Assert parameter property schemas
    assert "source" in tool_map["list_regulatory_updates"].parameters["properties"]
    assert "date_from" in tool_map["list_regulatory_updates"].parameters["properties"]
    assert "date_to" in tool_map["list_regulatory_updates"].parameters["properties"]
    assert "limit" in tool_map["list_regulatory_updates"].parameters["properties"]

    assert "query" in tool_map["search_regulatory_docs"].parameters["properties"]
    assert "source" in tool_map["search_regulatory_docs"].parameters["properties"]
    assert "topic" in tool_map["search_regulatory_docs"].parameters["properties"]

    assert "doc_id" in tool_map["get_document_by_id"].parameters["properties"]

    assert "citation" in tool_map["verify_legal_citation"].parameters["properties"]
    assert "source" in tool_map["verify_legal_citation"].parameters["properties"]

    assert "topic" in tool_map["get_tdi_service_offerings"].parameters["properties"]
    assert "sector" in tool_map["get_tdi_service_offerings"].parameters["properties"]


@pytest.mark.asyncio
async def test_list_regulatory_updates_matrix():
    """Verify limit boundaries, date windows, source filtering, and Tier 1 projections."""
    # Default call returns up to 10 items in descending order of publication_date
    res_default = await mcp.call_tool("list_regulatory_updates", {})
    updates = extract_json(res_default)
    assert isinstance(updates, list)
    assert 1 <= len(updates) <= 10
    for i in range(len(updates) - 1):
        assert updates[i]["publication_date"] >= updates[i + 1]["publication_date"]

    # Limit boundaries: limit=1
    res_1 = await mcp.call_tool("list_regulatory_updates", {"limit": 1})
    updates_1 = extract_json(res_1)
    assert len(updates_1) == 1

    # limit=100 clamped to 50 (fixture has 5 docs, so returns all 5)
    res_100 = await mcp.call_tool("list_regulatory_updates", {"limit": 100})
    updates_100 = extract_json(res_100)
    assert len(updates_100) == 5

    # limit=0 clamped to 1
    res_0 = await mcp.call_tool("list_regulatory_updates", {"limit": 0})
    updates_0 = extract_json(res_0)
    assert len(updates_0) == 1

    # Date filtering: valid date window
    res_date = await mcp.call_tool(
        "list_regulatory_updates",
        {"date_from": "2024-01-01", "date_to": "2024-04-01"},
    )
    updates_date = extract_json(res_date)
    assert len(updates_date) > 0
    for u in updates_date:
        assert "2024-01-01" <= u["publication_date"] <= "2024-04-01"

    # Source filtering
    res_inail = await mcp.call_tool("list_regulatory_updates", {"source": "INAIL"})
    updates_inail = extract_json(res_inail)
    assert len(updates_inail) > 0
    for u in updates_inail:
        assert u["source"] == "INAIL"

    # Tier 1 projection: assert keys in return objects match RegulatoryUpdateSummary and exclude Tier 2 fields
    tier2_exclusive_fields = {
        "status",
        "target_sectors",
        "key_obligations",
        "penalties_summary",
        "related_citations",
        "content_markdown",
    }
    for u in updates:
        for t2_key in tier2_exclusive_fields:
            assert t2_key not in u, f"Tier 2 field '{t2_key}' should not be present in Tier 1 summary"
        assert "doc_id" in u
        assert "title" in u
        assert "official_reference" in u
        assert "publication_date" in u
        # Model verification
        RegulatoryUpdateSummary(**u)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "invalid_kwargs",
    [
        {"date_from": "20240101"},
        {"date_from": "2024-99-99"},
        {"date_from": "2024-02-31"},
        {"date_from": "2024-1-1"},
        {"date_to": "20240101"},
        {"date_to": "2024-99-99"},
        {"date_to": "2024-02-31"},
        {"date_to": "2024-1-1"},
        {"date_from": "2024-12-31", "date_to": "2024-01-01"},
    ],
)
async def test_list_regulatory_updates_strict_date_validation(invalid_kwargs):
    """Verify that compact dates, non-calendar dates, and inverted ranges are strictly rejected."""
    from server import list_regulatory_updates

    with pytest.raises(ValueError):
        list_regulatory_updates(**invalid_kwargs)

    with pytest.raises(Exception):
        await mcp.call_tool("list_regulatory_updates", invalid_kwargs)


@pytest.mark.asyncio
async def test_search_regulatory_docs_matrix():
    """Verify search across keyword, topics, combined filters, and empty/unmatched inputs."""
    # Keyword matching title, summary, official_reference, or topic_tags
    res_kw = await mcp.call_tool("search_regulatory_docs", {"query": "preposti"})
    docs_kw = extract_json(res_kw)
    assert len(docs_kw) > 0
    assert any(d["doc_id"] == "gu-2024-dl-preposti" for d in docs_kw)

    # Combined filters: query="calore", source="INAIL", topic="construction_safety"
    res_comb = await mcp.call_tool(
        "search_regulatory_docs",
        {"query": "calore", "source": "INAIL", "topic": "construction_safety"},
    )
    docs_comb = extract_json(res_comb)
    assert len(docs_comb) == 1
    assert docs_comb[0]["doc_id"] == "inail-2024-circ-calore"

    # Case insensitivity: "PREPOSTI" vs "preposti"
    res_upper = await mcp.call_tool("search_regulatory_docs", {"query": "PREPOSTI"})
    res_lower = await mcp.call_tool("search_regulatory_docs", {"query": "preposti"})
    assert extract_json(res_upper) == extract_json(res_lower)

    # Empty query: "" and "   " return []
    res_empty1 = await mcp.call_tool("search_regulatory_docs", {"query": ""})
    assert extract_json(res_empty1) == []
    res_empty2 = await mcp.call_tool("search_regulatory_docs", {"query": "   "})
    assert extract_json(res_empty2) == []

    # Unmatched query returns []
    res_none = await mcp.call_tool("search_regulatory_docs", {"query": "non_existent_term_xyz_12345"})
    assert extract_json(res_none) == []


@pytest.mark.asyncio
async def test_get_document_by_id_success():
    """Verify document retrieval across all fixture IDs and whitespace slug trimming."""
    expected_ids = [
        "eurlex-dir-2024-869",
        "eurlex-reg-2023-1230",
        "gu-2024-dl-preposti",
        "gu-2023-dm-antincendio",
        "inail-2024-circ-calore",
    ]
    for doc_id in expected_ids:
        res = await mcp.call_tool("get_document_by_id", {"doc_id": doc_id})
        doc = extract_json(res)
        assert doc["doc_id"] == doc_id
        assert "content_markdown" in doc
        assert "key_obligations" in doc
        assert RegulatoryDocument(**doc)

    # Whitespace slug resolves correctly
    res_ws = await mcp.call_tool("get_document_by_id", {"doc_id": "  gu-2024-dl-preposti  "})
    doc_ws = extract_json(res_ws)
    assert doc_ws["doc_id"] == "gu-2024-dl-preposti"


def test_get_document_by_id_error_direct_function():
    """Verify direct Python function invocation raises ValueError on unknown ID."""
    from server import get_document_by_id

    with pytest.raises(ValueError, match="Document with ID 'non-existent-id' not found."):
        get_document_by_id("non-existent-id")


@pytest.mark.asyncio
async def test_get_document_by_id_error_mcp_boundary():
    """Verify MCP protocol boundary properly flags error on unknown ID."""
    try:
        res = await mcp.call_tool("get_document_by_id", {"doc_id": "non-existent-id"})
        assert hasattr(res, "is_error") and res.is_error
        assert "Document with ID 'non-existent-id' not found." in res.content[0].text
    except Exception as e:
        assert "Document with ID 'non-existent-id' not found." in str(e)


@pytest.mark.asyncio
async def test_verify_legal_citation_identity_and_aliases():
    """Verify alias resolution, preservation of citation_input, and status handling."""
    # Alias query: asserts citation_input reflects submitted citation
    res_alias = await mcp.call_tool("verify_legal_citation", {"citation": "dlgs 81/08 art 37"})
    c_alias = extract_json(res_alias)
    assert c_alias["citation_input"] == "dlgs 81/08 art 37"
    assert c_alias["is_valid"] is True
    assert c_alias["status"] == "in_force"
    assert c_alias["canonical_citation"] == "D.Lgs. 9 aprile 2008, n. 81, Art. 37 (Formazione dei lavoratori e dei loro rappresentanti)"

    # Canonical query
    canonical_input = "D.Lgs. 81/2008 Art. 37"
    res_canon = await mcp.call_tool("verify_legal_citation", {"citation": canonical_input})
    c_canon = extract_json(res_canon)
    assert c_canon["citation_input"] == canonical_input
    assert c_canon["is_valid"] is True
    assert c_canon["status"] == "in_force"

    # Repealed citation
    res_rep = await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 626/94 Art. 3"})
    c_rep = extract_json(res_rep)
    assert c_rep["citation_input"] == "D.Lgs. 626/94 Art. 3"
    assert c_rep["is_valid"] is False
    assert c_rep["status"] == "repealed"

    # Unknown citation
    unknown_input = "Legge Fantasma 99/2099"
    res_unk = await mcp.call_tool("verify_legal_citation", {"citation": unknown_input})
    c_unk = extract_json(res_unk)
    assert c_unk["citation_input"] == unknown_input
    assert c_unk["is_valid"] is False
    assert c_unk["status"] == "unrecognized"
    assert c_unk["canonical_citation"] == unknown_input

    # Empty citation
    res_emp = await mcp.call_tool("verify_legal_citation", {"citation": ""})
    c_emp = extract_json(res_emp)
    assert c_emp["is_valid"] is False
    assert c_emp["status"] == "unrecognized"
    assert c_emp["canonical_citation"] == ""

    # Whitespace citation
    res_ws = await mcp.call_tool("verify_legal_citation", {"citation": "   "})
    c_ws = extract_json(res_ws)
    assert c_ws["is_valid"] is False
    assert c_ws["status"] == "unrecognized"


@pytest.mark.asyncio
async def test_verify_legal_citation_source_noop():
    """Verify source argument acts as a backward-compatible no-op."""
    res_none = await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 81/2008 Art. 37", "source": None})
    res_gu = await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 81/2008 Art. 37", "source": "GAZZETTA_UFFICIALE"})
    res_eur = await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 81/2008 Art. 37", "source": "EUR_LEX"})

    data_none = extract_json(res_none)
    data_gu = extract_json(res_gu)
    data_eur = extract_json(res_eur)

    assert data_none == data_gu == data_eur
    assert data_gu["is_valid"] is True


@pytest.mark.asyncio
async def test_get_tdi_service_offerings_matrix():
    """Verify scored-union matching across topic, sector, combined filters, and fallbacks."""
    # Topic-only: topic="chemical_risk", sector=None
    res_chem = await mcp.call_tool("get_tdi_service_offerings", {"topic": "chemical_risk"})
    data_chem = extract_json(res_chem)
    assert len(data_chem) > 0
    assert data_chem[0]["service_id"] == "tdi-srv-chemical-audit"

    # Sector-only: topic="", sector="construction"
    res_sec = await mcp.call_tool("get_tdi_service_offerings", {"topic": "", "sector": "construction"})
    data_sec = extract_json(res_sec)
    sec_ids = [s["service_id"] for s in data_sec]
    assert "tdi-srv-preposti-training" in sec_ids
    assert "tdi-srv-heat-stress" in sec_ids

    # Topic + sector combined: topic="workplace_safety", sector="construction"
    res_comb = await mcp.call_tool(
        "get_tdi_service_offerings",
        {"topic": "workplace_safety", "sector": "construction"},
    )
    data_comb = extract_json(res_comb)
    assert data_comb[0]["service_id"] == "tdi-srv-preposti-training"

    # Fallback: unknown topic and sector=None returns [tdi-srv-preposti-training]
    res_fb = await mcp.call_tool("get_tdi_service_offerings", {"topic": "unknown_xyz"})
    data_fb = extract_json(res_fb)
    assert len(data_fb) == 1
    assert data_fb[0]["service_id"] == "tdi-srv-preposti-training"

    # Empty inputs fallback: topic="", sector=None
    res_emp = await mcp.call_tool("get_tdi_service_offerings", {"topic": ""})
    data_emp = extract_json(res_emp)
    assert len(data_emp) == 1
    assert data_emp[0]["service_id"] == "tdi-srv-preposti-training"
