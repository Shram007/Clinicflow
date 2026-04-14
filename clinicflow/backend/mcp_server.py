"""
MCP server for ClinicFlow.

Exposes clinical documentation tools as Model Context Protocol (MCP) callable tools
over stdio JSON-RPC 2.0 — no new dependencies required.

Tools exposed:
  - generate_soap_note   : Generate a SOAP note from a voice transcript
  - list_visits          : List recent visit summaries
  - get_visit            : Retrieve a single visit by ID

Run with:  python -m clinicflow.backend.mcp_server
  or:      python clinicflow/backend/mcp_server.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

# Add project root to sys.path so relative imports work when run directly
sys.path.insert(0, str(Path(__file__).parents[2]))

# ── Tool registry ─────────────────────────────────────────────────────────────

def _serialize(model) -> str:
    """Serialize a Pydantic model to a JSON string (supports v1 and v2)."""
    if hasattr(model, "model_dump_json"):
        return model.model_dump_json()
    return model.json()


TOOLS = {
    "generate_soap_note": {
        "name": "generate_soap_note",
        "description": (
            "Generate a structured SOAP note (Subjective, Objective, Assessment, Plan) "
            "from a doctor voice note transcript. Returns a VisitDetail object with title, "
            "summary, and all four SOAP sections."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "transcript": {
                    "type": "string",
                    "description": "The raw voice note transcript from the doctor.",
                },
                "visit_id": {
                    "type": "integer",
                    "description": "Numeric ID to assign to the generated visit (default 1).",
                    "default": 1,
                },
            },
            "required": ["transcript"],
        },
    },
    "list_visits": {
        "name": "list_visits",
        "description": "Return a list of all stored visit summaries.",
        "inputSchema": {
            "type": "object",
            "properties": {},
            "required": [],
        },
    },
    "get_visit": {
        "name": "get_visit",
        "description": "Retrieve the full detail of a single visit by its numeric ID.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "visit_id": {
                    "type": "integer",
                    "description": "The ID of the visit to retrieve.",
                },
            },
            "required": ["visit_id"],
        },
    },
}


# ── Tool dispatcher ───────────────────────────────────────────────────────────

def dispatch_tool(name: str, arguments: dict) -> str:
    """Call the underlying service/store and return a JSON string result."""

    if name == "generate_soap_note":
        from clinicflow.backend.services.agents_service import generate_visit_from_transcript
        transcript = arguments["transcript"]
        visit_id = int(arguments.get("visit_id", 1))
        result = generate_visit_from_transcript(transcript, visit_id=visit_id)
        return _serialize(result)

    elif name == "list_visits":
        # Import the in-memory store used by routes_visits
        try:
            from clinicflow.backend.api.routes_visits import VISITS_DB
            visits = [v.model_dump() if hasattr(v, "model_dump") else v.dict() for v in VISITS_DB]
        except Exception:
            visits = []
        return json.dumps(visits)

    elif name == "get_visit":
        try:
            from clinicflow.backend.api.routes_visits import VISITS_DB
            visit_id = int(arguments["visit_id"])
            visit = next((v for v in VISITS_DB if v.id == visit_id), None)
            if visit is None:
                return json.dumps({"error": f"Visit {visit_id} not found"})
            return _serialize(visit)
        except Exception as exc:
            return json.dumps({"error": str(exc)})

    else:
        raise ValueError(f"Unknown tool: {name}")


# ── JSON-RPC / MCP handler ────────────────────────────────────────────────────

def handle_request(request: dict) -> dict:
    method = request.get("method", "")
    req_id = request.get("id")
    params = request.get("params", {})

    # MCP initialize handshake
    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "clinicflow", "version": "1.0.0"},
            },
        }

    # List available tools
    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": list(TOOLS.values())},
        }

    # Call a tool
    if method == "tools/call":
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        try:
            content = dispatch_tool(tool_name, arguments)
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": content}],
                    "isError": False,
                },
            }
        except Exception as exc:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {
                    "content": [{"type": "text", "text": str(exc)}],
                    "isError": True,
                },
            }

    # Unknown method
    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method not found: {method}"},
    }


# ── stdio transport loop ──────────────────────────────────────────────────────

def run_stdio():
    """Read JSON-RPC requests line-by-line from stdin, write responses to stdout."""
    print("[mcp_server] ClinicFlow MCP server started (stdio)", file=sys.stderr, flush=True)
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
        except json.JSONDecodeError as exc:
            response = {
                "jsonrpc": "2.0",
                "id": None,
                "error": {"code": -32700, "message": f"Parse error: {exc}"},
            }
        else:
            response = handle_request(request)
        print(json.dumps(response), flush=True)


if __name__ == "__main__":
    run_stdio()
