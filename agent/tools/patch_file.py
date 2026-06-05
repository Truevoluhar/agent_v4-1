from pathlib import Path
from agent.tools.base import Tool, ToolResult, resolve_workspace_path


def patch_file_executor(
    workspace: Path,
    path: str,
    old_text: str,
    new_text: str
) -> ToolResult:
    try:
        target = resolve_workspace_path(workspace, path)
        
        if not target.exists():
            return ToolResult(ok=False, error=f"File not found: {path}")
        
        content = target.read_text(encoding="utf-8", errors="replace")
        
        if old_text not in content:
            return ToolResult(ok=False, error="old_text not found in file")

        updated = content.replace(old_text, new_text, 1)
        target.write_text(updated, encoding="utf-8")
        
        return ToolResult(
            ok=True,
            output=f"Patched file: {path}",
            metadata={
                "path": path,
                "old_length": len(old_text),
                "new_length": len(new_text)
            }
        )
    
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
PATCH_FILE_TOOL = Tool(
    name="patch_file",
    description="Patch a file by replacing one exact text block with another.",
    permission_level="write",
    executor=patch_file_executor,
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "old_text": {"type": "string"},
            "new_text": {"type": "string"}
        },
        "required": ["path", "old_text", "new_text"]
    }
)