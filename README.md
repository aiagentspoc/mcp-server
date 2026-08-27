# HSE Easy Mock MCP Server

A deterministic, protocol-compliant [Model Context Protocol (MCP)](https://modelcontextprotocol.io/) server providing regulatory data fixtures, legal citation validation, and TDI service catalog mappings for HSE Easy AI Agent workflows (POC A & POC B).

---

## Features & Tools

- **`list_regulatory_updates`**: Query and filter regulatory updates from EUR-Lex, Gazzetta Ufficiale, and INAIL by source, impact level, topic, or date.
- **`get_regulatory_doc`**: Retrieve full regulatory text, structured key provisions, affected sectors, and sanctions.
- **`verify_citation`**: Validate official legal citations, canonical references, and authoritative URLs.
- **`get_service_catalog`**: Map regulatory topics to TDI commercial service offerings and Call-to-Action (CTA) templates.

---

## Quick Start

### Prerequisites
- Python 3.10+
- [`uv`](https://docs.astral.sh/uv/) package manager

### Setup & Installation
```bash
# Install dependencies
uv sync
```

### Running the Server
```bash
# Run interactive MCP Inspector for development
uv run fastmcp dev server.py

# Run standard stdio transport server
uv run python server.py
```

---

## Documentation

- [ARCHITECTURE.md](.agents/docs/ARCHITECTURE.md): System topology, lifecycles, and component boundaries.
- [SPECIFICATIONS.md](.agents/docs/SPECIFICATIONS.md): Pydantic schemas, tool contracts, and fixture requirements.
- [ROADMAP.md](ROADMAP.md): Project roadmap and implementation milestones.
