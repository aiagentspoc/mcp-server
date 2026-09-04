"""Performance benchmark suite for HSE Easy Mock MCP Server.

Isolates:
1. Startup index construction (<50ms threshold, target <15ms).
2. In-process tool direct call latency (<15ms threshold, target <2ms).
3. In-process FastMCP tool latency (<15ms threshold).
4. Full stdio roundtrip latency over an open pipe (strictly <15ms threshold on every platform).
"""

import json
import subprocess
import sys
import time
from operator import attrgetter
from pathlib import Path

import pytest

from models import (
    CitationVerificationResult,
    RegulatoryDocument,
    TDIServiceOffering,
)
from server import (
    DOCS_BY_ID,
    PreprocessedService,
    get_document_by_id,
    get_tdi_service_offerings,
    list_regulatory_updates,
    load_fixtures_and_indexes,
    mcp,
    search_regulatory_docs,
    verify_legal_citation,
)

FIXTURES_DIR = Path(__file__).parent.parent / "fixtures"


def test_benchmark_startup_indexing():
    """
    Benchmark the actual production startup indexing path via load_fixtures_and_indexes:
    Opening the 3 JSON files, parsing JSON, hydrating Pydantic models,
    and constructing DOCS_BY_ID, CITATIONS_BY_ALIAS (with collision safety),
    and INDEXED_TDI_SERVICES using the exact production callable.
    Threshold: < 50ms.
    """
    durations = []

    for _ in range(10):
        t0 = time.perf_counter()
        (
            docs,
            docs_by_id,
            docs_ordered,
            citations_by_alias,
            tdi_services,
            indexed_services,
            fallback,
        ) = load_fixtures_and_indexes(FIXTURES_DIR)
        t1 = time.perf_counter()
        durations.append(t1 - t0)

        assert len(docs_by_id) == 5
        assert len(docs_ordered) == 5
        assert len(citations_by_alias) >= 18
        assert len(indexed_services) == 5
        assert len(fallback) == 1

    mean_duration_ms = (sum(durations) / len(durations)) * 1000.0
    print(f"\n[Startup Indexing] Mean: {mean_duration_ms:.2f} ms")
    assert mean_duration_ms < 50.0, f"Startup indexing exceeded 50ms: {mean_duration_ms:.2f}ms"


def test_benchmark_in_process_tool_latency():
    """
    Benchmark in-process direct invocations of all 5 tools over 100 warm iterations.
    Threshold: < 15ms per call (target: < 2ms).
    """
    # Warmup
    for _ in range(10):
        list_regulatory_updates()
        search_regulatory_docs("preposti")
        get_document_by_id("gu-2024-dl-preposti")
        verify_legal_citation("D.Lgs. 81/2008 Art. 37")
        get_tdi_service_offerings("chemical_risk")

    tools = [
        ("list_regulatory_updates", lambda: list_regulatory_updates()),
        ("search_regulatory_docs", lambda: search_regulatory_docs("preposti")),
        ("get_document_by_id", lambda: get_document_by_id("gu-2024-dl-preposti")),
        ("verify_legal_citation", lambda: verify_legal_citation("D.Lgs. 81/2008 Art. 37")),
        ("get_tdi_service_offerings", lambda: get_tdi_service_offerings("chemical_risk")),
    ]

    iterations = 100
    for tool_name, tool_fn in tools:
        t0 = time.perf_counter()
        for _ in range(iterations):
            tool_fn()
        t1 = time.perf_counter()

        mean_ms = ((t1 - t0) / iterations) * 1000.0
        print(f"\n[In-Process Tool: {tool_name}] Mean: {mean_ms:.4f} ms")
        assert mean_ms < 15.0, f"Tool {tool_name} latency exceeded 15ms: {mean_ms:.4f}ms"


@pytest.mark.asyncio
async def test_benchmark_mcp_protocol_tool_latency():
    """
    Benchmark FastMCP middleware & routing tool execution in-process over 50 iterations.
    Threshold: < 15ms per call.
    """
    # Warmup
    for _ in range(5):
        await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 81/2008 Art. 37"})

    iterations = 50
    times = []
    for _ in range(iterations):
        t0 = time.perf_counter()
        await mcp.call_tool("verify_legal_citation", {"citation": "D.Lgs. 81/2008 Art. 37"})
        t1 = time.perf_counter()
        times.append(t1 - t0)

    mean_ms = (sum(times) / iterations) * 1000.0
    print(f"\n[FastMCP in-process call_tool] Mean: {mean_ms:.3f} ms")
    assert mean_ms < 15.0, f"FastMCP call_tool exceeded 15ms: {mean_ms:.3f}ms"


def test_benchmark_stdio_roundtrip_latency():
    """
    Benchmark JSON-RPC roundtrip latency over an open stdio pipe across 20 sequential calls.
    Excludes subprocess boot time.
    Threshold: strictly < 15ms across all platforms per architecture specification.
    """
    import os

    server_path = Path(__file__).parent.parent / "server.py"

    process = subprocess.Popen(
        [sys.executable, "-u", str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )

    try:
        # Handshake
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {"name": "bench-client", "version": "1.0"},
            },
        }
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()
        process.stdout.readline()

        process.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
        process.stdin.flush()

        # Warmup calls over pipe
        for i in range(5):
            call = {
                "jsonrpc": "2.0",
                "id": 100 + i,
                "method": "tools/call",
                "params": {"name": "verify_legal_citation", "arguments": {"citation": "D.Lgs. 81/2008 Art. 37"}},
            }
            process.stdin.write(json.dumps(call) + "\n")
            process.stdin.flush()
            process.stdout.readline()

        # 20 sequential measured calls
        times = []
        for i in range(20):
            call = {
                "jsonrpc": "2.0",
                "id": 200 + i,
                "method": "tools/call",
                "params": {"name": "verify_legal_citation", "arguments": {"citation": "D.Lgs. 81/2008 Art. 37"}},
            }
            t0 = time.perf_counter()
            process.stdin.write(json.dumps(call) + "\n")
            process.stdin.flush()
            line = process.stdout.readline()
            t1 = time.perf_counter()
            times.append(t1 - t0)

            # Sanity assert that result returned
            resp = json.loads(line)
            assert "result" in resp

        mean_ms = (sum(times) / len(times)) * 1000.0
        min_ms = min(times) * 1000.0
        print(f"\n[stdio Roundtrip Latency] Mean: {mean_ms:.2f} ms (min: {min_ms:.2f} ms)")

        # Architecture & Specification requirement: < 15ms strictly
        assert mean_ms < 15.0, f"stdio roundtrip exceeded 15ms: {mean_ms:.2f}ms"

    finally:
        process.terminate()
        process.wait(timeout=2)
