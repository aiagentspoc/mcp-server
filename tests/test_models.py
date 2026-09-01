"""Tests for Pydantic v2 data models in models.py.

Verifies field constraints, required/optional fields, literal enums,
JSON serialization/deserialization, schema generation, and Tier 2 projection.
"""

import json
import pytest
from pydantic import ValidationError

from models import (
    CitationVerificationResult,
    RegulatoryDocument,
    RegulatoryUpdateSummary,
    TDIServiceOffering,
)


class TestRegulatoryUpdateSummary:
    """Test suite for Tier 1 RegulatoryUpdateSummary model."""

    @pytest.fixture
    def valid_summary_payload(self):
        return {
            "doc_id": "eurlex-dir-2024-869",
            "source": "EUR_LEX",
            "doc_type": "directive",
            "official_reference": "Direttiva (UE) 2024/869",
            "title": "Direttiva sui valori limite di esposizione per piombo e diisocianati",
            "publication_date": "2024-03-19",
            "effective_date": "2026-04-09",
            "impact_level": "critical",
            "topic_tags": ["chemical_risk", "occupational_health"],
            "summary": "Aggiornamento dei valori limite biologici per il piombo e norme di prevenzione per i diisocianati.",
            "canonical_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024L0869",
        }

    def test_valid_instantiation_full(self, valid_summary_payload):
        summary = RegulatoryUpdateSummary(**valid_summary_payload)
        assert summary.doc_id == "eurlex-dir-2024-869"
        assert summary.source == "EUR_LEX"
        assert summary.doc_type == "directive"
        assert summary.official_reference == "Direttiva (UE) 2024/869"
        assert summary.title == "Direttiva sui valori limite di esposizione per piombo e diisocianati"
        assert summary.publication_date == "2024-03-19"
        assert summary.effective_date == "2026-04-09"
        assert summary.impact_level == "critical"
        assert summary.topic_tags == ["chemical_risk", "occupational_health"]
        assert "Aggiornamento" in summary.summary
        assert summary.canonical_url.startswith("https://")

    def test_valid_instantiation_minimal(self, valid_summary_payload):
        minimal_data = valid_summary_payload.copy()
        del minimal_data["effective_date"]
        del minimal_data["topic_tags"]

        summary = RegulatoryUpdateSummary(**minimal_data)
        assert summary.effective_date is None
        assert summary.topic_tags == []

    @pytest.mark.parametrize(
        "missing_field",
        [
            "doc_id",
            "source",
            "doc_type",
            "official_reference",
            "title",
            "publication_date",
            "impact_level",
            "summary",
            "canonical_url",
        ],
    )
    def test_missing_required_fields(self, valid_summary_payload, missing_field):
        invalid_data = valid_summary_payload.copy()
        del invalid_data[missing_field]

        with pytest.raises(ValidationError) as exc_info:
            RegulatoryUpdateSummary(**invalid_data)
        assert missing_field in str(exc_info.value)

    @pytest.mark.parametrize("valid_source", ["EUR_LEX", "GAZZETTA_UFFICIALE", "INAIL"])
    def test_valid_source_literal_enums(self, valid_summary_payload, valid_source):
        data = valid_summary_payload.copy()
        data["source"] = valid_source
        summary = RegulatoryUpdateSummary(**data)
        assert summary.source == valid_source

    @pytest.mark.parametrize("invalid_source", ["MINISTERO_SALUTE", "eur_lex", "OTHER", ""])
    def test_invalid_source_literal_enums(self, valid_summary_payload, invalid_source):
        data = valid_summary_payload.copy()
        data["source"] = invalid_source
        with pytest.raises(ValidationError) as exc_info:
            RegulatoryUpdateSummary(**data)
        assert "source" in str(exc_info.value)

    @pytest.mark.parametrize(
        "valid_doc_type", ["directive", "regulation", "decree", "circular", "guideline"]
    )
    def test_valid_doc_type_literal_enums(self, valid_summary_payload, valid_doc_type):
        data = valid_summary_payload.copy()
        data["doc_type"] = valid_doc_type
        summary = RegulatoryUpdateSummary(**data)
        assert summary.doc_type == valid_doc_type

    @pytest.mark.parametrize("invalid_doc_type", ["law", "standard", "statute", ""])
    def test_invalid_doc_type_literal_enums(self, valid_summary_payload, invalid_doc_type):
        data = valid_summary_payload.copy()
        data["doc_type"] = invalid_doc_type
        with pytest.raises(ValidationError) as exc_info:
            RegulatoryUpdateSummary(**data)
        assert "doc_type" in str(exc_info.value)

    @pytest.mark.parametrize("valid_impact", ["critical", "high", "medium", "low"])
    def test_valid_impact_level_literal_enums(self, valid_summary_payload, valid_impact):
        data = valid_summary_payload.copy()
        data["impact_level"] = valid_impact
        summary = RegulatoryUpdateSummary(**data)
        assert summary.impact_level == valid_impact

    @pytest.mark.parametrize("invalid_impact", ["extreme", "urgent", "none", "urgent_action"])
    def test_invalid_impact_level_literal_enums(self, valid_summary_payload, invalid_impact):
        data = valid_summary_payload.copy()
        data["impact_level"] = invalid_impact
        with pytest.raises(ValidationError) as exc_info:
            RegulatoryUpdateSummary(**data)
        assert "impact_level" in str(exc_info.value)

    def test_list_field_independence(self, valid_summary_payload):
        data1 = valid_summary_payload.copy()
        data2 = valid_summary_payload.copy()
        del data1["topic_tags"]
        del data2["topic_tags"]

        summary1 = RegulatoryUpdateSummary(**data1)
        summary2 = RegulatoryUpdateSummary(**data2)

        assert summary1.topic_tags == []
        assert summary2.topic_tags == []

        summary1.topic_tags.append("custom_tag")
        assert "custom_tag" in summary1.topic_tags
        assert "custom_tag" not in summary2.topic_tags

    def test_extra_fields_ignored(self, valid_summary_payload):
        data = valid_summary_payload.copy()
        data["unrecognized_extra_field"] = 12345
        summary = RegulatoryUpdateSummary(**data)
        assert not hasattr(summary, "unrecognized_extra_field")


class TestRegulatoryDocument:
    """Test suite for Tier 2 RegulatoryDocument model."""

    @pytest.fixture
    def valid_full_doc_payload(self):
        return {
            "doc_id": "eurlex-dir-2024-869",
            "source": "EUR_LEX",
            "doc_type": "directive",
            "official_reference": "Direttiva (UE) 2024/869",
            "title": "Direttiva sui valori limite di esposizione per piombo e diisocianati",
            "publication_date": "2024-03-19",
            "effective_date": "2026-04-09",
            "impact_level": "critical",
            "topic_tags": ["chemical_risk", "occupational_health"],
            "summary": "Aggiornamento dei valori limite biologici per il piombo.",
            "canonical_url": "https://eur-lex.europa.eu/legal-content/IT/TXT/?uri=CELEX:32024L0869",
            "status": "in_force",
            "target_sectors": ["manufacturing", "automotive", "construction"],
            "key_obligations": [
                "Revisione dei limiti biologici per il piombo a 30 µg Pb/100 ml di sangue",
                "Formazione specifica obbligatoria per tutti i lavoratori che manipolano diisocianati",
            ],
            "penalties_summary": "Sanzioni penali e ammende fino a 10.000 euro per mancato adeguamento.",
            "related_citations": ["Direttiva 2004/37/CE", "Direttiva 98/24/CE"],
            "content_markdown": "# Direttiva (UE) 2024/869\n\n## Articolo 1\nModifiche alla Direttiva 2004/37/CE...",
        }

    def test_valid_instantiation_full(self, valid_full_doc_payload):
        doc = RegulatoryDocument(**valid_full_doc_payload)
        assert doc.doc_id == "eurlex-dir-2024-869"
        assert doc.status == "in_force"
        assert len(doc.target_sectors) == 3
        assert len(doc.key_obligations) == 2
        assert doc.penalties_summary is not None
        assert len(doc.related_citations) == 2
        assert doc.content_markdown.startswith("# Direttiva")

    def test_valid_instantiation_minimal_tier2(self, valid_full_doc_payload):
        minimal_data = valid_full_doc_payload.copy()
        del minimal_data["target_sectors"]
        del minimal_data["key_obligations"]
        del minimal_data["penalties_summary"]
        del minimal_data["related_citations"]

        doc = RegulatoryDocument(**minimal_data)
        assert doc.status == "in_force"
        assert doc.target_sectors == []
        assert doc.key_obligations == []
        assert doc.penalties_summary is None
        assert doc.related_citations == []
        assert doc.content_markdown == valid_full_doc_payload["content_markdown"]

    @pytest.mark.parametrize("missing_tier2_field", ["status", "content_markdown"])
    def test_missing_required_tier2_fields(self, valid_full_doc_payload, missing_tier2_field):
        invalid_data = valid_full_doc_payload.copy()
        del invalid_data[missing_tier2_field]

        with pytest.raises(ValidationError) as exc_info:
            RegulatoryDocument(**invalid_data)
        assert missing_tier2_field in str(exc_info.value)

    @pytest.mark.parametrize("valid_status", ["in_force", "amended", "repealed", "proposed"])
    def test_valid_status_literal_enums(self, valid_full_doc_payload, valid_status):
        data = valid_full_doc_payload.copy()
        data["status"] = valid_status
        doc = RegulatoryDocument(**data)
        assert doc.status == valid_status

    @pytest.mark.parametrize("invalid_status", ["active", "deprecated", "archived", "valid", ""])
    def test_invalid_status_literal_enums(self, valid_full_doc_payload, invalid_status):
        data = valid_full_doc_payload.copy()
        data["status"] = invalid_status
        with pytest.raises(ValidationError) as exc_info:
            RegulatoryDocument(**data)
        assert "status" in str(exc_info.value)

    def test_to_summary_projection(self, valid_full_doc_payload):
        doc = RegulatoryDocument(**valid_full_doc_payload)
        summary = doc.to_summary()

        assert isinstance(summary, RegulatoryUpdateSummary)
        assert not isinstance(summary, RegulatoryDocument)

        # Verify shared fields match
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

        # Verify Tier 2 fields are stripped
        summary_dump = summary.model_dump()
        for tier2_field in [
            "status",
            "target_sectors",
            "key_obligations",
            "penalties_summary",
            "related_citations",
            "content_markdown",
        ]:
            assert tier2_field not in summary_dump
            assert not hasattr(summary, tier2_field)

    def test_to_summary_json_isolation(self, valid_full_doc_payload):
        doc = RegulatoryDocument(**valid_full_doc_payload)
        summary_json = doc.to_summary().model_dump_json()
        parsed = json.loads(summary_json)

        expected_keys = {
            "doc_id",
            "source",
            "doc_type",
            "official_reference",
            "title",
            "publication_date",
            "effective_date",
            "impact_level",
            "topic_tags",
            "summary",
            "canonical_url",
        }
        assert set(parsed.keys()) == expected_keys

    def test_list_field_independence_tier2(self, valid_full_doc_payload):
        data1 = valid_full_doc_payload.copy()
        data2 = valid_full_doc_payload.copy()
        del data1["target_sectors"]
        del data2["target_sectors"]

        doc1 = RegulatoryDocument(**data1)
        doc2 = RegulatoryDocument(**data2)

        doc1.target_sectors.append("sector_a")
        assert "sector_a" in doc1.target_sectors
        assert "sector_a" not in doc2.target_sectors


class TestCitationVerificationResult:
    """Test suite for CitationVerificationResult model."""

    @pytest.fixture
    def valid_citation_payload(self):
        return {
            "citation_input": "D.Lgs. 81/2008 Art. 37",
            "is_valid": True,
            "status": "in_force",
            "canonical_citation": "D.Lgs. 9 aprile 2008, n. 81, Art. 37",
            "official_reference": "D.Lgs. 81/2008",
            "official_url": "https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81!art37",
            "verified_against_doc_id": "gu-2024-dl-preposti",
            "notes": "Articolo recentemente integrato con nuovi obblighi per i preposti.",
        }

    def test_valid_instantiation_verified(self, valid_citation_payload):
        res = CitationVerificationResult(**valid_citation_payload)
        assert res.citation_input == "D.Lgs. 81/2008 Art. 37"
        assert res.is_valid is True
        assert res.status == "in_force"
        assert res.canonical_citation == "D.Lgs. 9 aprile 2008, n. 81, Art. 37"
        assert res.official_reference == "D.Lgs. 81/2008"
        assert res.official_url.startswith("https://www.normattiva.it")
        assert res.verified_against_doc_id == "gu-2024-dl-preposti"
        assert res.notes is not None

    def test_valid_instantiation_unrecognized(self):
        data = {
            "citation_input": "Legge Inesistente 999/2099",
            "is_valid": False,
            "status": "unrecognized",
            "canonical_citation": "Legge Inesistente 999/2099",
        }
        res = CitationVerificationResult(**data)
        assert res.citation_input == "Legge Inesistente 999/2099"
        assert res.is_valid is False
        assert res.status == "unrecognized"
        assert res.canonical_citation == "Legge Inesistente 999/2099"
        assert res.official_reference is None
        assert res.official_url is None
        assert res.verified_against_doc_id is None
        assert res.notes is None

    @pytest.mark.parametrize(
        "missing_field",
        ["citation_input", "is_valid", "status", "canonical_citation"],
    )
    def test_missing_required_fields(self, valid_citation_payload, missing_field):
        invalid_data = valid_citation_payload.copy()
        del invalid_data[missing_field]

        with pytest.raises(ValidationError) as exc_info:
            CitationVerificationResult(**invalid_data)
        assert missing_field in str(exc_info.value)

    @pytest.mark.parametrize("valid_status", ["in_force", "amended", "repealed", "unrecognized"])
    def test_valid_status_literal_enums(self, valid_citation_payload, valid_status):
        data = valid_citation_payload.copy()
        data["status"] = valid_status
        res = CitationVerificationResult(**data)
        assert res.status == valid_status

    @pytest.mark.parametrize("invalid_status", ["valid", "invalid", "deprecated", "active", ""])
    def test_invalid_status_literal_enums(self, valid_citation_payload, invalid_status):
        data = valid_citation_payload.copy()
        data["status"] = invalid_status
        with pytest.raises(ValidationError) as exc_info:
            CitationVerificationResult(**data)
        assert "status" in str(exc_info.value)

    def test_boolean_type_validation(self, valid_citation_payload):
        data = valid_citation_payload.copy()
        data["is_valid"] = True
        assert CitationVerificationResult(**data).is_valid is True

        data["is_valid"] = False
        assert CitationVerificationResult(**data).is_valid is False

    def test_extra_aliases_field_ignored(self, valid_citation_payload):
        data = valid_citation_payload.copy()
        data["aliases"] = ["art 37 81/08", "81/08 art 37", "art. 37 d.lgs 81"]
        res = CitationVerificationResult(**data)
        assert res.is_valid is True
        assert not hasattr(res, "aliases")


class TestTDIServiceOffering:
    """Test suite for TDIServiceOffering model."""

    @pytest.fixture
    def valid_service_payload(self):
        return {
            "service_id": "tdi-srv-chemical-audit",
            "service_name": "Audit di Conformità Rischio Chimico e Sostanze CMR",
            "topic_category": "chemical_risk",
            "applicable_sectors": ["manufacturing", "chemical", "automotive"],
            "value_proposition": "Valutazione specialistica dei rischi chimici e aggiornamento DVR.",
            "cta_headline": "Aggiorna la valutazione rischio chimico con i tecnici TDI.",
            "cta_body": "Richiedi un audit sul campo per adeguarti ai nuovi limiti biologici.",
            "landing_page_url": "https://www.tdigroup.it/servizi/audit-rischio-chimico",
        }

    def test_valid_instantiation(self, valid_service_payload):
        srv = TDIServiceOffering(**valid_service_payload)
        assert srv.service_id == "tdi-srv-chemical-audit"
        assert srv.service_name == "Audit di Conformità Rischio Chimico e Sostanze CMR"
        assert srv.topic_category == "chemical_risk"
        assert len(srv.applicable_sectors) == 3
        assert srv.value_proposition.startswith("Valutazione")
        assert srv.cta_headline.startswith("Aggiorna")
        assert srv.cta_body.startswith("Richiedi")
        assert srv.landing_page_url == "https://www.tdigroup.it/servizi/audit-rischio-chimico"

    def test_applicable_sectors_default(self, valid_service_payload):
        data = valid_service_payload.copy()
        del data["applicable_sectors"]
        srv = TDIServiceOffering(**data)
        assert srv.applicable_sectors == []

    @pytest.mark.parametrize(
        "missing_field",
        [
            "service_id",
            "service_name",
            "topic_category",
            "value_proposition",
            "cta_headline",
            "cta_body",
            "landing_page_url",
        ],
    )
    def test_missing_required_fields(self, valid_service_payload, missing_field):
        invalid_data = valid_service_payload.copy()
        del invalid_data[missing_field]

        with pytest.raises(ValidationError) as exc_info:
            TDIServiceOffering(**invalid_data)
        assert missing_field in str(exc_info.value)

    def test_extra_fields_ignored(self, valid_service_payload):
        data = valid_service_payload.copy()
        data["internal_crm_code"] = "CRM-12345"
        srv = TDIServiceOffering(**data)
        assert not hasattr(srv, "internal_crm_code")


class TestSerializationAndJsonSchema:
    """Test suite for JSON serialization, deserialization, and schema introspection."""

    def test_json_roundtrip_all_models(self):
        summary = RegulatoryUpdateSummary(
            doc_id="gu-2024-dl-preposti",
            source="GAZZETTA_UFFICIALE",
            doc_type="decree",
            official_reference="D.Lgs. 81/2008",
            title="Nuovi obblighi formativi e nomina preposti",
            publication_date="2024-01-15",
            effective_date="2024-02-01",
            impact_level="critical",
            topic_tags=["workplace_safety", "preposti_training"],
            summary="Obbligo nomina preposti nei contratti di appalto.",
            canonical_url="https://www.gazzettaufficiale.it/eli/id/2024/01/15/24G00010/sg",
        )
        summary_json = summary.model_dump_json()
        restored_summary = RegulatoryUpdateSummary.model_validate_json(summary_json)
        assert summary == restored_summary

        doc = RegulatoryDocument(
            doc_id="gu-2024-dl-preposti",
            source="GAZZETTA_UFFICIALE",
            doc_type="decree",
            official_reference="D.Lgs. 81/2008",
            title="Nuovi obblighi formativi e nomina preposti",
            publication_date="2024-01-15",
            effective_date="2024-02-01",
            impact_level="critical",
            topic_tags=["workplace_safety", "preposti_training"],
            summary="Obbligo nomina preposti nei contratti di appalto.",
            canonical_url="https://www.gazzettaufficiale.it/eli/id/2024/01/15/24G00010/sg",
            status="in_force",
            target_sectors=["construction", "manufacturing"],
            key_obligations=["Nomina espressa del preposto per iscritto"],
            penalties_summary="Arresto da 2 a 4 mesi o ammenda da 1.500 a 6.000 euro.",
            related_citations=["D.Lgs. 81/2008 Art. 37", "D.Lgs. 81/2008 Art. 18"],
            content_markdown="# D.Lgs. 81/2008 Aggiornamento Preposti\n\nTesto normativo...",
        )
        doc_json = doc.model_dump_json()
        restored_doc = RegulatoryDocument.model_validate_json(doc_json)
        assert doc == restored_doc

        citation = CitationVerificationResult(
            citation_input="D.Lgs. 81/2008 Art. 37",
            is_valid=True,
            status="in_force",
            canonical_citation="D.Lgs. 9 aprile 2008, n. 81, Art. 37",
            official_reference="D.Lgs. 81/2008",
            official_url="https://www.normattiva.it/uri-res/N2Ls?urn:nir:stato:decreto.legislativo:2008-04-09;81!art37",
            verified_against_doc_id="gu-2024-dl-preposti",
            notes="Formazione preposti ogni due anni.",
        )
        citation_json = citation.model_dump_json()
        restored_citation = CitationVerificationResult.model_validate_json(citation_json)
        assert citation == restored_citation

        service = TDIServiceOffering(
            service_id="tdi-srv-preposti-training",
            service_name="Corso di Formazione e Aggiornamento Preposti (D.Lgs. 81/08)",
            topic_category="workplace_safety",
            applicable_sectors=["construction", "logistics", "manufacturing"],
            value_proposition="Formazione certificata biennale per preposti in conformità all'art. 37 D.Lgs. 81/08.",
            cta_headline="Adeguati ai nuovi obblighi formativi per i Preposti prima delle verifiche ispettive.",
            cta_body="Iscrivi subito i tuoi preposti al corso di aggiornamento conforme alle novità normative.",
            landing_page_url="https://www.tdigroup.it/corsi/aggiornamento-preposti",
        )
        service_json = service.model_dump_json()
        restored_service = TDIServiceOffering.model_validate_json(service_json)
        assert service == restored_service

    def test_model_dump_modes(self):
        summary = RegulatoryUpdateSummary(
            doc_id="inail-2024-circ-calore",
            source="INAIL",
            doc_type="circular",
            official_reference="Circolare INAIL 28/2024",
            title="Linee guida rischio stress termico",
            publication_date="2024-07-02",
            effective_date=None,
            impact_level="high",
            topic_tags=["heat_stress", "microclimate"],
            summary="Misure per prevenire i colpi di calore nei cantieri estivi.",
            canonical_url="https://www.inail.it/atti/circolare-28-2024",
        )

        python_dict = summary.model_dump(mode="python")
        json_dict = summary.model_dump(mode="json")

        assert isinstance(python_dict, dict)
        assert isinstance(json_dict, dict)
        assert python_dict["doc_id"] == "inail-2024-circ-calore"
        assert json_dict["effective_date"] is None
        assert json_dict["source"] == "INAIL"

    def test_unicode_and_special_characters_preservation(self):
        italian_title = (
            "Decreto Ministeriale concernente l'attività antincendio: "
            "obblighi di sicurezza, sanzioni fino a € 10.000 e applicazione § 12"
        )
        doc = RegulatoryDocument(
            doc_id="gu-2023-dm-antincendio",
            source="GAZZETTA_UFFICIALE",
            doc_type="decree",
            official_reference="D.M. 3 settembre 2021",
            title=italian_title,
            publication_date="2023-09-03",
            effective_date="2023-10-01",
            impact_level="high",
            topic_tags=["fire_safety", "emergency_plans"],
            summary="Nuovi criteri generali di sicurezza antincendio e gestione delle emergenze.",
            canonical_url="https://www.gazzettaufficiale.it/eli/id/2021/10/29/21A06354/sg",
            status="in_force",
            target_sectors=["high_risk_plants"],
            key_obligations=["Valutazione del rischio incendio secondo i nuovi criteri"],
            penalties_summary="Sanzioni penali ai sensi dell'art. 68 D.Lgs. 81/08 (ammenda da € 1.500 a € 6.000).",
            related_citations=["D.Lgs. 81/2008 Art. 46"],
            content_markdown="# Sicurezza Antincendio\n\nTesto con caratteri accentati: à, è, é, ì, ò, ù, €, §.",
        )

        doc_json = doc.model_dump_json()
        restored = RegulatoryDocument.model_validate_json(doc_json)

        assert restored.title == italian_title
        assert "€ 10.000" in restored.title
        assert "§ 12" in restored.title
        assert "à, è, é, ì, ò, ù, €, §" in restored.content_markdown

    def test_none_fields_serialize_to_json_null(self):
        citation = CitationVerificationResult(
            citation_input="D.P.R. 547/55 Art. 10",
            is_valid=False,
            status="repealed",
            canonical_citation="D.P.R. 27 aprile 1955, n. 547, Art. 10",
            official_reference=None,
            official_url=None,
            verified_against_doc_id=None,
            notes=None,
        )

        citation_json = citation.model_dump_json()
        parsed = json.loads(citation_json)

        assert parsed["official_reference"] is None
        assert parsed["official_url"] is None
        assert parsed["verified_against_doc_id"] is None
        assert parsed["notes"] is None

        restored = CitationVerificationResult.model_validate_json(citation_json)
        assert restored.official_reference is None
        assert restored.official_url is None

    @pytest.mark.parametrize(
        "model_cls",
        [
            RegulatoryUpdateSummary,
            RegulatoryDocument,
            CitationVerificationResult,
            TDIServiceOffering,
        ],
    )
    def test_model_json_schema_validity(self, model_cls):
        schema = model_cls.model_json_schema()

        assert isinstance(schema, dict)
        assert schema.get("type") == "object"
        assert "properties" in schema
        assert "required" in schema
        assert isinstance(schema["properties"], dict)
        assert isinstance(schema["required"], list)

        # Verify all properties have descriptions
        for prop_name, prop_meta in schema["properties"].items():
            # In Pydantic v2 schemas, description might be on property or anyOf/allOf
            has_desc = "description" in prop_meta or (
                "anyOf" in prop_meta
                and any("description" in item for item in prop_meta["anyOf"])
            )
            assert has_desc, f"Property '{prop_name}' in {model_cls.__name__} missing description"
