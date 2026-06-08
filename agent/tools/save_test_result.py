import shutil
from pathlib import Path

from agent.tools.base import Tool, ToolResult, resolve_workspace_path

def save_test_result_executor(workspace: Path, filename: str, content: str) -> ToolResult:
    print("Model called save test result.")

    try:
        queue_relative_filepath = f"./artifacts/queue/{filename}"
        queue_path = resolve_workspace_path(workspace, queue_relative_filepath)

        final_relative_filepath = f"./artifacts/{filename}"
        final_path = resolve_workspace_path(workspace, final_relative_filepath)

        queue_path.parent.mkdir(parents=True, exist_ok=True)
        final_path.parent.mkdir(parents=True, exist_ok=True)

        with open(queue_path, "w", encoding="utf-8") as f:
            f.write(content)

        shutil.move(str(queue_path), str(final_path))

        return ToolResult(ok=True, output="File saved successfully.")

    except Exception as e:
        return ToolResult(ok=False, error=str(e))
    
    
SAVE_TEST_RESULT_TOOL = Tool(
    name="save_test_result",
    description="Save results of executed tests.",
    permission_level="read",
    executor=save_test_result_executor,
    input_schema={
        "type": "object",
        "properties": {
            "filename": {
                "type": "string",
                "description": "You must use the same filename you used to load a test case.",
            },
            "content": {
                "type": "string",
                "description": "Content of a test result.",
            },
        },
        "required": ["filename", "content"],
    },
)