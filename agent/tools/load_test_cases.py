import os
import json
from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def load_test_cases_executor(workspace: Path) -> ToolResult:
    relative_path = "./artifacts/test-cases.json"
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
    
    
LOAD_TEST_CASES_TOOL = Tool(
    name="load_test_cases",
    description="Load test cases.",
    permission_level="read",
    executor=load_test_cases_executor,
    input_schema={
        "type": "object",
        "type": "object",
        "properties": {},
        "required": []
    }
)