import os
import json
from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def load_test_executor(workspace: Path, filename: str) -> ToolResult:
    
    print("Model called load test.")
    
    relative_path = f"./artifacts/queue/{filename}"
    path = resolve_workspace_path(workspace, relative_path)
    try:
        with open(path, "r") as f:
            return ToolResult(
                ok=True,
                output=f.read(),
                metadata={"size": os.path.getsize(path)}
            )
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
LOAD_TEST_TOOL = Tool(
    name="load_test",
    description="Load test cases.",
    permission_level="read",
    executor=load_test_executor,
    input_schema={
        "type": "object",
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "Valid Filename of a test case to load."
            }
        },
        "required": []
    }
)