import os
from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path


def get_tasks_executor(workspace: Path) -> ToolResult:

    print("Model called get tasks.")

    relative_path = "./artifacts/queue"
    try:
        queue_path = resolve_workspace_path(workspace=workspace, path=relative_path)
        queue_files = os.listdir(queue_path)
        return ToolResult(
            ok=True,
            output=str(queue_files),
            metadata={"num_files_in_queue": len(queue_files)}
        )
    except Exception as e:
        return ToolResult(
            ok=False,
            error=str(e)
        )
    
GET_TASKS_TOOL = Tool(
    name="get_tasks",
    description="Get tasks in queue. These tasks are waiting to get executed.",
    executor=get_tasks_executor,
    permission_level="read",
    input_schema={
        "type": "object",
        "properties": {},
        "required": []
    }
)