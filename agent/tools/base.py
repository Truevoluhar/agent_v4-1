from dataclasses import dataclass
from typing import Callable, Literal, Any, Optional
from pathlib import Path
import json

PermissionLevel = Literal["read", "write", "shell"]

@dataclass
class ToolResult:
    ok: bool
    output: Optional[str] = None
    error: Optional[str] = None
    metadata: Optional[dict] = None
    
@dataclass
class Tool:
    name: str
    description: str
    input_schema: str
    permission_level: PermissionLevel
    executor: Callable[..., ToolResult]
    max_output_chars: int = 12_000
    
    def schema(self) -> dict:
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema
        }
        

def truncate_text(text: str, max_chars: int) -> tuple[str, bool]:
    if len(text) <= max_chars:
        return text, False
    
    return (
        text[:max_chars] + "\n\n[TRUNCATED: output exceeded max size]",
        True
    )

    
def safe_json(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False)


def resolve_workspace_path(workspace: Path, path: str) -> Path:
    root = workspace.resolve()
    target = (root / path).resolve()
    
    try:
        target.relative_to(root)
    except ValueError:
        raise PermissionError(f"Path escapes workspace: {path}")
    
    return target    
    