from pathlib import Path
import re

from agent.tools.base import Tool, ToolResult, resolve_workspace_path, truncate_text

def grep_executor(workspace: Path, pattern: str, path: str = ".") -> ToolResult:
    try:
        
        root = resolve_workspace_path(workspace, path)
        regex = re.compile(pattern)
        
        ignored = {".git", "__pycache__", "node_modules", ".venv", "venv"}
        matches=[]
        
        files = [root] if root.is_file() else root.rglob("*")
        
        for file in files:
            if not file.is_file():
                continue
            if any(part in ignored for part in file.parts):
                continue
            
            try:
                lines = file.read_text(encoding="utf-8", errors="replace").splitlines()
            except Exception:
                continue
            
            for idx, line in enumerate(lines, start=1):
                if regex.search(line):
                    rel = file.relative_to(workspace)
                    matches.append(f"{rel}:{idx}: {line}")
                    
        output, truncated = truncate_text("\n".join(matches), 12_000)
        
        return ToolResult(
            ok=True,
            output=output,
            metadata={"matches": len(matches), "truncated": truncated}
        )
    except re.error as e:
        return ToolResult(ok=False, error=f"Invalid regex: {e}")
                
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
GREP_TOOL = Tool(
    name="grep",
    description="Search worskpace files using a regular expression.",
    permission_level="read",
    executor=grep_executor,
    input_schema={
        "type": "object",
        "properties": {
            "pattern": {"type": "string"},
            "path": {"type": "string", "default": "."}
        },
        "required": ["pattern"]
    }
)