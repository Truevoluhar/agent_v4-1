from dataclasses import dataclass
from pathlib import Path
from typing import Literal, Optional
import re

from agent.tools.registry import TOOLS

PermissionAction = Literal["allow", "ask", "deny"]
PermissionMode = Literal["safe", "normal", "trusted", "yolo", "ci"]

# 
# 
# Nastavitve in podatkovni razredi
#

@dataclass
class PermissionDecision:
    action: PermissionAction
    reason: str
    matched_rule: Optional[str] = None
    
    
DANGEROUS_SHELL_PATTERNS = [
    r"\brm\s+-rf\s+(/|\*|\.|\$HOME|~)",
    r"\bcurl\b.*\|\s*(sh|bash|zsh)",
    r"\bwget\b.*\|\s*(sh|bash|zsh)",
    r"\bsudo\b",
    r"\bmkfs\b",
    r"\bdd\s+.*\bof=",
    r":\s*\(\)\s*\{\s*:\s*\|\s*:\s*&\s*\}\s*;",
]


PATH_KEYS_BY_TOOL = {
    "read_file": ["path"],
    "write_file": ["path"],
    "patch_file": ["path"],
    "list_files": ["path"],
    "grep": ["path"],
    "run_shell": ["cwd"],
}


#
# Pomozne funkcije
#

def _is_inside_workspace(workspace: Path, target: Path) -> bool:
    workspace = workspace.resolve()
    target = target.resolve()
    
    try:
        target.relative_to(workspace)
        return True
    except ValueError:
        return False
    
def _check_path_safety(
    workspace: Path,
    tool_name: str,
    tool_input: dict
) -> Optional[PermissionDecision]:
    keys = PATH_KEYS_BY_TOOL.get(tool_name, [])
    
    for key in keys:
        
        raw_path = tool_input.get(key)
        if raw_path is None:
            continue

        if not isinstance(raw_path, str):
            return PermissionDecision(
                action="deny",
                reason=f"Invalid path value for {key}",
                matched_rule="invalid_path_type"
            )
        
        if raw_path.startswith("~"):
            return PermissionDecision(
                action="deny",
                reason=f"Home-directory paths are not allowed: {raw_path}",
                matched_rule="deny_home_path"
            )
        
        candidate = Path(raw_path)
        
        if candidate.is_absolute():
            target = candidate
        else:
            target = workspace / candidate
        
        if not _is_inside_workspace(workspace, target):
            return PermissionDecision(
                action="deny",
                reason=f"Path escapes workspace: {raw_path}",
                matched_rule="deny_path_escape" 
            )
    
    return None


def _check_shell_safety(tool_name: str, tool_input: dict) -> Optional[PermissionDecision]:
    if tool_name != "run_shell":
        return None
    
    command = tool_input.get("command", "")
    
    if not isinstance(command, str):
        return PermissionDecision(
            action="deny",
            reason="Invalid shell command",
            matched_rule="invalid_shell_command"
        )
    
    normalized = " ".join(command.strip().split())
    
    for pattern in DANGEROUS_SHELL_PATTERNS:
        if re.search(pattern, normalized, flags=re.IGNORECASE):
            return PermissionDecision(
                action="deny",
                reason=f"Shell command matched hard-deny rule: {pattern}",
                matched_rule=pattern
            )
            
    return None
            
            
            
            

def permission_gate(
    tool_name: str,
    tool_input: dict,
    workspace: Path,
    mode: PermissionMode = "normal",
    interactive: bool = True
) -> PermissionDecision:
    
    tool = TOOLS.get(tool_name)
    
    if tool is None:
        return PermissionDecision(
            action="deny",
            reason=f"Unknown tool: {tool_name}",
            matched_rule="unknown_tool"
        )
        
    # Najprej se preveri hard-deny pot
    path_decision = _check_path_safety(workspace, tool_name, tool_input)
    if path_decision is not None:
        return path_decision
    
    # Potem preverimo hard-deny shell komande
    shell_decision = _check_shell_safety(tool_name, tool_input)
    if shell_decision is not None:
        return shell_decision
    

    # Logika preverjanja na podlagi vrednosti LEVEL in MODE
    level = tool.permission_level
    
    if mode == "safe":
        if level == "read":
            return PermissionDecision("allow", "Safe mode allows read-only tools.")
        return PermissionDecision("deny", "Safe mode denies write and shell tools.")

    if mode == "normal":
        if level == "read":
            return PermissionDecision("allow", "Normal mode allows read-only tools.")
        if interactive:
            return PermissionDecision("ask", f"Normal mode requires approval for {level} tools.")
        return PermissionDecision("deny", "Normal mode is non-interactive, so approval is unavailable.")

    if mode == "trusted":
        if level in {"read", "write"}:
            return PermissionDecision("allow", "Trusted mode allows read and write tools.")
        if level == "shell":
            if interactive:
                return PermissionDecision("ask", "Trusted mode requires approval for shell tools.")
            return PermissionDecision("deny", "Trusted mode is non-interactive, so shell approval is unavailable.")

    if mode == "yolo":
        return PermissionDecision("allow", "YOLO mode allows all tools except hard-deny rules.")

    if mode == "ci":
        if level == "read":
            return PermissionDecision("allow", "CI mode allows read-only tools.")
        return PermissionDecision("deny", "CI mode denies tools that require approval.")