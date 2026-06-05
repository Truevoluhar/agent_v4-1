from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def save_test_results_executor(workspace: Path, content: str) -> ToolResult:
    relative_path = "./artifacts/test-results.json"
    path = resolve_workspace_path(workspace, relative_path)
    try:
        with open(path, "w") as f:
            f.write(content)
        return ToolResult(ok=True, output="File saved successfully.")
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
SAVE_TEST_RESULTS_TOOL = Tool(
    name="save_test_results",
    description="Save results of executed tests.",
    permission_level="read",
    executor=save_test_results_executor,
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string"}
        },
        "required": ["content"]
    }
)