"""
Render MCP Stdio Server
Exposes Render deployment management tools over Model Context Protocol (MCP) JSON-RPC.
"""

import sys
import json
import os
import urllib.request
import urllib.error

RENDER_API_KEY = os.getenv("RENDER_API_KEY", "rnd_vsNd9zqRTgLh8Jd13NDyPJQsiDNW")
RENDER_SERVICE_ID = os.getenv("RENDER_SERVICE_ID", "srv-daro718jo6nc738p9a1g")

def render_api_request(endpoint: str, method: str = "GET", payload: dict = None):
    url = f"https://api.render.com/v1/{endpoint.lstrip('/')}"
    headers = {
        "Authorization": f"Bearer {RENDER_API_KEY}",
        "Content-Type": "application/json",
        "Accept": "application/json"
    }
    data = json.dumps(payload).encode('utf-8') if payload else None
    req = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            content = resp.read().decode('utf-8')
            return json.loads(content) if content else {}
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP Error {e.code}: {e.read().decode('utf-8')}"}
    except Exception as e:
        return {"error": str(e)}

TOOLS = [
    {
        "name": "render_get_service_status",
        "description": "Get real-time operational status, URL, and metadata of the deployed Render web service.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_id": {"type": "string", "description": "Optional Render service ID (defaults to project service)"}
            }
        }
    },
    {
        "name": "render_trigger_deploy",
        "description": "Trigger a new build and deployment on Render.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_id": {"type": "string", "description": "Optional Render service ID (defaults to project service)"},
                "clear_cache": {"type": "boolean", "description": "Clear build cache before building"}
            }
        }
    },
    {
        "name": "render_get_deploy_history",
        "description": "Retrieve recent deployment logs and build status history on Render.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "service_id": {"type": "string", "description": "Optional Render service ID"}
            }
        }
    }
]

def handle_request(request):
    method = request.get("method")
    req_id = request.get("id")

    if method == "initialize":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "render-mcp-server", "version": "1.0.0"}
            }
        }

    if method == "tools/list":
        return {
            "jsonrpc": "2.0",
            "id": req_id,
            "result": {"tools": TOOLS}
        }

    if method == "tools/call":
        params = request.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})

        sid = args.get("service_id") or RENDER_SERVICE_ID

        if tool_name == "render_get_service_status":
            res = render_api_request(f"services/{sid}")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }

        elif tool_name == "render_trigger_deploy":
            clear_cache = "do_not_clear" if not args.get("clear_cache") else "clear"
            res = render_api_request(f"services/{sid}/deploys", method="POST", payload={"clearCache": clear_cache})
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }

        elif tool_name == "render_get_deploy_history":
            res = render_api_request(f"services/{sid}/deploys")
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "result": {"content": [{"type": "text", "text": json.dumps(res, indent=2)}]}
            }

        else:
            return {
                "jsonrpc": "2.0",
                "id": req_id,
                "error": {"code": -32601, "message": f"Tool '{tool_name}' not found"}
            }

    return {
        "jsonrpc": "2.0",
        "id": req_id,
        "error": {"code": -32601, "message": f"Method '{method}' not supported"}
    }

def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            req = json.loads(line)
            resp = handle_request(req)
            sys.stdout.write(json.dumps(resp) + "\n")
            sys.stdout.flush()
        except Exception as e:
            sys.stderr.write(f"Error handling request: {e}\n")

if __name__ == "__main__":
    main()
