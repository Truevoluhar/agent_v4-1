from pathlib import Path
from typing import Optional, Any
import requests

from agent.tools.base import Tool, ToolResult

def test_endpoint_executor(
    workspace: Path,
    method: str,
    url: str,
    body: Optional[dict] = None,
    headers: Optional[dict] = None,
    params: Optional[dict] = None,
    timeout: int = 10,
) -> ToolResult:

    print(f"Model called test_endpoint with params method: {method}, url: {url}, body: {body}, headers: {headers}, params: {params}, timeout: {timeout}")
    
    try:
        
        #request_cert = "/home/Z66176/Public/key/server.crt"
        #request_key = "/home/Z66176/Public/key/server.key"
        
        response = requests.request(
            method=method.upper(),
            url=url,
            json=body,
            headers=headers,
            params=params,
            timeout=timeout,
            #cert=request_cert,
            #verify=True
        )

        result = {
            "status_code": response.status_code,
            "headers": dict(response.headers),
        }

        try:
            result["body"] = response.json()
        except Exception:
            result["body"] = response.text

        return ToolResult(
            ok=True,
            output=str(result["body"]),
            metadata={"status_code": result["status_code"], "headers": result["headers"] }
        )

    except requests.exceptions.RequestException as e:
        return ToolResult(
            ok=False,
            error=str(e)
        )

    except Exception as e:
        return ToolResult(
            ok=False,
            error=str(e)
        )
    

    
        
TEST_ENDPOINT_TOOL = Tool(
    name="test_endpoint",
    description=(
        "Send an HTTP request to a webservice endpoint and return the response. "
        "When a loaded test case contains a `body` field, pass that exact value as this tool's `body` argument. "
        "For JSON requests, `body` is sent using requests.request(..., json=body). "
        "Do not put JSON body fields in `params`. `params` is only for URL query parameters."
    ),
    permission_level="read",
    executor=test_endpoint_executor,
    input_schema={
        "type": "object",
        "properties": {
            "method": {
                "type": "string",
                "description": "HTTP method, for example GET, POST, PUT, PATCH, or DELETE."
            },
            "url": {
                "type": "string",
                "description": "Full URL to request."
            },
            "body": {
                "type": "object",
                "description": (
                    "JSON request body to send with the request. "
                    "Use this for test-case fields named `body`, such as login credentials "
                    "or token payloads. This is sent using requests.request(..., json=body)."
                ),
            },
            "headers": {
                "type": ["object", "null"],
                "description": "HTTP headers, for example Content-Type or Authorization."
            },
            "params": {
                "type": ["object", "null"],
                "description": (
                    "URL query parameters only. Do not put JSON request body fields here."
                ),
            },
            "timeout": {
                "type": "integer",
                "description": "Request timeout in seconds."
            },
        },
        "required": ["method", "url"]
    }
)