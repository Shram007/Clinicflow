"""
Unit tests for the ClinicFlow MCP server JSON-RPC handler.
No network calls required — tests only the protocol layer.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parents[3]))

from clinicflow.backend.mcp_server import handle_request, TOOLS


def test_initialize_returns_server_info():
    resp = handle_request({"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}})
    assert resp["result"]["serverInfo"]["name"] == "clinicflow"
    assert resp["result"]["protocolVersion"] == "2024-11-05"
    print("[PASS] initialize handshake")


def test_tools_list_contains_all_tools():
    resp = handle_request({"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}})
    names = [t["name"] for t in resp["result"]["tools"]]
    for expected in ["generate_soap_note", "list_visits", "get_visit"]:
        assert expected in names, f"Missing tool: {expected}"
    print(f"[PASS] tools/list — {len(names)} tools registered: {names}")


def test_tools_have_valid_input_schemas():
    resp = handle_request({"jsonrpc": "2.0", "id": 3, "method": "tools/list", "params": {}})
    for tool in resp["result"]["tools"]:
        assert "inputSchema" in tool, f"Tool {tool['name']} missing inputSchema"
        assert tool["inputSchema"]["type"] == "object"
    print("[PASS] all tools have valid inputSchema")


def test_unknown_method_returns_error():
    resp = handle_request({"jsonrpc": "2.0", "id": 4, "method": "unknown/method", "params": {}})
    assert "error" in resp
    assert resp["error"]["code"] == -32601
    print("[PASS] unknown method returns JSON-RPC error -32601")


def test_unknown_tool_call_returns_is_error_true():
    resp = handle_request({
        "jsonrpc": "2.0",
        "id": 5,
        "method": "tools/call",
        "params": {"name": "nonexistent_tool", "arguments": {}},
    })
    assert resp["result"]["isError"] is True
    print("[PASS] unknown tool call returns isError=True")


if __name__ == "__main__":
    test_initialize_returns_server_info()
    test_tools_list_contains_all_tools()
    test_tools_have_valid_input_schemas()
    test_unknown_method_returns_error()
    test_unknown_tool_call_returns_is_error_true()
    print("\nAll MCP server tests passed.")
