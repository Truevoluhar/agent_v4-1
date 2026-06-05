import requests
from pathlib import Path

from agent.tools.base import ToolResult, Tool


def webservice_definition_executor(workspace: Path, url: str) -> ToolResult:
    print("Model called webservice_analysis")
    try:
        #request_cert = "/home/Z66176/Public/key/server.crt"
        
        # ws_definition = requests.get(url)
        ws_definition = requests.request(
            method = "GET",
            url=url,
            timeout = None,
            #cert=request_cert,
            #verify=True
        )
        
        try:
            return ToolResult(
                ok=True,
                output=ws_definition.text,
                metadata={}
            )
        except Exception as e:
            return ToolResult(ok=False, error=str(e))
        
    except Exception as e:
        print(e)
        return ToolResult(ok=False, error=str(e))
    
    
WEBSERVICE_DEFINITION_TOOL = Tool(
    name="webservice_definition",
    description="Get definition of a webservice",
    permission_level="read",
    executor=webservice_definition_executor,
    input_schema={
        "type": "object",
        "properties": {
            "url": {"type": "string"}
        },
        "required": ["url"]
    }
)