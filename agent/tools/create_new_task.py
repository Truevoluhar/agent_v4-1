from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def create_new_task_executor(workspace: Path, filename: str, content: str) -> ToolResult:
    path = f"./artifacts/{filename}.json"
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
    
    
CREATE_NEW_TASK_TOOL = Tool(
    name="create_new_task",
    description="Create a new test task.",
    permission_level="read",
    executor=create_new_task_executor,
    input_schema={
        "type": "object",
        "properties": {
            "filename": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["filename", "content"]
    }
)