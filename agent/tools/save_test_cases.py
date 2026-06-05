from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def save_test_cases_executor(workspace: Path, content: str) -> ToolResult:
    path = "./artifacts/test-cases.json"
    try:
        target = resolve_workspace_path(workspace, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
        
        return ToolResult(
            ok=True,
            output=f"Wrote file: {path}",
            metadata={"path": path, "bytes": len(content.encode("utf-8"))}
        )
        
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
SAVE_TEST_CASES_TOOL = Tool(
    name="save_test_cases",
    description="Save test cases to a file.",
    permission_level="read",
    executor=save_test_cases_executor,
    input_schema={
        "type": "object",
        "properties": {
            "content": {"type": "string"}
        },
        "required": ["content"]
    }
)