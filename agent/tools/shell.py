from pathlib import Path
import subprocess

from agent.tools.base import Tool, ToolResult, resolve_workspace_path, truncate_text


def run_shell_executor(
    workspace: Path,
    command: str,
    cwd: str = ".",
    timeout: int = 20
) -> ToolResult:
    
    try:
        
        working_dir = resolve_workspace_path(workspace, cwd)
        
        if not working_dir.is_dir():
            return ToolResult(ok=False, error=f"cwd is not a directory: {cwd}")
        
        completed = subprocess.run(
            command,
            cwd=working_dir,
            shell=True,
            text=True,
            capture_output=True,
            timeout=timeout
        )
        
        output = ""
        if completed.stdout:
            output += completed.stdout
        if completed.stderr:
            output += "\n[stderr]\n" + completed.stderr
            
        output, truncated = truncate_text(output, 12_000)
        
        return ToolResult(
            ok=completed.returncode == 0,
            output=output,
            error=None if completed.returncode == 0 else f"Exit code {completed.returncode}",
            metadata={
                "command": command,
                "cwd": cwd,
                "exit_code": completed.returncode,
                "truncated": truncated
            }
        )
    
    except subprocess.TimeoutExpired:
        return ToolResult(ok=False, error=str(e))
    
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
RUN_SHELL_TOOL = Tool(
    name="run_shell",
    description="Run a shell command inside the workspace.",
    permission_level="shell",
    executor=run_shell_executor,
    input_schema={
        "type": "object",
        "properties": {
            "command": {"type": "string"},
            "cwd": {"type": "string", "default": ""},
            "timeout": {"type": "integer", "default": 20}
        },
        "required": ["command"]
    }
)