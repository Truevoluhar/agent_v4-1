from pathlib import Path
from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def write_file_executor(workspace: Path, path: str, content: str) -> ToolResult:
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
    
    
WRITE_FILE_TOOL = Tool(
    name="write_file",
    description="Write full content to a file in the workspace.",
    permission_level="write",
    executor=write_file_executor,
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "content": {"type": "string"}
        },
        "required": ["path", "content"]
    }
)