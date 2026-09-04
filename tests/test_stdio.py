"""Test suite for stdio transport cleanliness, protocol lifecycle, and console script entrypoint."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_stdio_initialize_no_noise():
    """
    Test that running server.py in stdio mode produces no stdout noise
    before or during JSON-RPC initialization handshake.
    """
    server_path = Path(__file__).parent.parent / "server.py"

    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0",
            },
        },
    }

    process.stdin.write(json.dumps(init_msg) + "\n")
    process.stdin.flush()

    stdout_line = process.stdout.readline().strip()

    process.terminate()
    process.wait(timeout=2)

    try:
        response = json.loads(stdout_line)
        assert response.get("jsonrpc") == "2.0"
        assert response.get("id") == 1
        assert "result" in response
    except json.JSONDecodeError:
        assert False, f"Stdout contained non-JSON noise: {stdout_line}"


def test_stdio_full_protocol_lifecycle():
    """
    Verify complete MCP stdio lifecycle over persistent subprocess pipe:
    initialize -> notifications/initialized -> tools/list -> tools/call
    with zero non-JSON log noise on stdout.
    """
    server_path = Path(__file__).parent.parent / "server.py"

    process = subprocess.Popen(
        [sys.executable, str(server_path)],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        # Step 1: Initialize
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0",
                },
            },
        }
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()

        init_line = process.stdout.readline().strip()
        init_resp = json.loads(init_line)
        assert init_resp.get("jsonrpc") == "2.0"
        assert init_resp.get("id") == 1
        assert "result" in init_resp

        # Step 2: Initialized notification (no response expected)
        init_notif = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
        }
        process.stdin.write(json.dumps(init_notif) + "\n")
        process.stdin.flush()

        # Step 3: tools/list
        tools_req = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
        }
        process.stdin.write(json.dumps(tools_req) + "\n")
        process.stdin.flush()

        tools_line = process.stdout.readline().strip()
        tools_resp = json.loads(tools_line)
        assert tools_resp.get("jsonrpc") == "2.0"
        assert tools_resp.get("id") == 2
        assert "result" in tools_resp

        registered_tools = {t["name"] for t in tools_resp["result"].get("tools", [])}
        expected_tools = {
            "list_regulatory_updates",
            "search_regulatory_docs",
            "get_document_by_id",
            "verify_legal_citation",
            "get_tdi_service_offerings",
        }
        assert expected_tools == registered_tools

        # Step 4: tools/call (verify_legal_citation)
        call_req = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "verify_legal_citation",
                "arguments": {
                    "citation": "D.Lgs. 81/2008 Art. 37",
                },
            },
        }
        process.stdin.write(json.dumps(call_req) + "\n")
        process.stdin.flush()

        call_line = process.stdout.readline().strip()
        call_resp = json.loads(call_line)
        assert call_resp.get("jsonrpc") == "2.0"
        assert call_resp.get("id") == 3
        assert "result" in call_resp

        call_result = call_resp["result"]
        assert call_result.get("isError") is not True

        # Ensure content contains valid payload
        content = call_result.get("content", [])
        assert len(content) >= 1
        payload = json.loads(content[0]["text"])
        assert payload["is_valid"] is True
        assert payload["status"] == "in_force"
        assert payload["citation_input"] == "D.Lgs. 81/2008 Art. 37"

    finally:
        process.terminate()
        process.wait(timeout=2)


def test_console_script_entrypoint():
    """
    Verify console script `hse-easy-mock` entrypoint executes properly
    as a standalone executable or via `uv run hse-easy-mock`.
    """
    script_path = shutil.which("hse-easy-mock")
    if not script_path:
        candidate = Path(sys.executable).parent / (
            "hse-easy-mock.exe" if sys.platform == "win32" else "hse-easy-mock"
        )
        if candidate.exists():
            script_path = str(candidate)

    cmd = [script_path] if script_path else ["uv", "run", "hse-easy-mock"]

    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )

    try:
        init_req = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-script-client",
                    "version": "1.0.0",
                },
            },
        }
        process.stdin.write(json.dumps(init_req) + "\n")
        process.stdin.flush()

        stdout_line = process.stdout.readline().strip()
        resp = json.loads(stdout_line)
        assert resp.get("jsonrpc") == "2.0"
        assert resp.get("id") == 1
        assert "result" in resp
    finally:
        process.terminate()
        process.wait(timeout=2)
