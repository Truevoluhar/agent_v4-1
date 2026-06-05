from pathlib import Path
from agent.tools.base import Tool, ToolResult, resolve_workspace_path, truncate_text

def read_file_executor(workspace: Path, path: str) -> ToolResult:
    try:
        target = resolve_workspace_path(workspace, path)
        
        if not target.exists():
            return ToolResult(ok=False, error=f"File not found: {path}")
        
        if not target.is_file():
            return ToolResult(ok=False, error=f"Not a file: {path}")
        
        text = target.read_text(encoding="utf-8", errors="replace")
        text, truncated = truncate_text(text, 12_000)
        
        return ToolResult(
            ok=True,
            output=text,
            metadata={"path": path, "truncated": truncated}
        )
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
READ_FILE_TOOL = Tool(
    name="read_file",
    description="Read a UTF-8 text file from the workspace.",
    permission_level="read",
    executor=read_file_executor,
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string"}
        },
        "required": ["path"]
    }
)