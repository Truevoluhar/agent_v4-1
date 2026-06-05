from pathlib import Path
import subprocess

from agent.tools.base import Tool, ToolResult, truncate_text


def get_git_diff_executor(workspace: Path) -> ToolResult:
    
    try:
        
        completed = subprocess.run(
            "git diff -- .",
            cwd=workspace,
            shell=True,
            text=True,
            capture_output=True,
            timeout=20
        )
        
        output = completed.stdout or completed.stderr
        output, truncated = truncate_text(output, 12_000)
        
        return ToolResult(
            ok=completed.returncode == 0,
            output=output,
            error=None if completed.returncode == 0 else f"Exit code {completed.returncode}",
            metadata={"truncated": truncated}
        )
        
    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
GET_GIT_DIFF_TOOL = Tool(
    name="get_git_diff",
    description="Return the current git diff for the workspace.",
    permission_level="read",
    executor=get_git_diff_executor,
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)

