from pathlib import Path
from agent.tools.base import Tool, ToolResult, resolve_workspace_path, truncate_text

def list_files_executor(workspace: Path, path: str = ".") -> ToolResult:
    
    try:
        root = resolve_workspace_path(workspace, path)
        
        if not root.exists():
            return ToolResult(ok=False, error=f"Path not found: {path}")
        
        if not root.is_dir():
            return ToolResult(ok=False, error=f"Not a directory: {path}")
        
        ignored = {".git", "__pycache__", "node_modules", "venv", ".venv"}
        
        files = []
        for item in sorted(root.rglob("*")):
            if any(part in ignored for part in item.parts):
                continue
            
            rel = item.relative_to(workspace)
            files.append(str(rel) + ("/" if item.is_dir() else ""))
            
        output, truncated = truncate_text("\n".join(files), 12_000)
        
        return ToolResult(
            ok=True,
            output=output,
            metadata={"path": path, "count": len(files), "truncated": truncated}
        )
        
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
LIST_FILES_TOOL = Tool(
    name="list_files",
    description="List files recursively under a workspace directory",
    permission_level="read",
    executor=list_files_executor,
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string", "default": ""}
        },
        "required": []
    }
)