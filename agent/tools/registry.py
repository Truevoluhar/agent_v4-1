from pathlib import Path
from dataclasses import asdict

from agent.tools.read_file import READ_FILE_TOOL
from agent.tools.write_file import WRITE_FILE_TOOL
from agent.tools.patch_file import PATCH_FILE_TOOL
from agent.tools.list_files import LIST_FILES_TOOL
from agent.tools.grep import GREP_TOOL
from agent.tools.shell import RUN_SHELL_TOOL
from agent.tools.git_diff import GET_GIT_DIFF_TOOL
from agent.tools.webservice_definition import WEBSERVICE_DEFINITION_TOOL
from agent.tools.save_test_cases import SAVE_TEST_CASES_TOOL
from agent.tools.test_endpoint import TEST_ENDPOINT_TOOL
from agent.tools.load_test_cases import LOAD_TEST_CASES_TOOL
from agent.tools.save_test_results import SAVE_TEST_RESULTS_TOOL
from agent.tools.create_new_task import CREATE_NEW_TASK_TOOL
from agent.tools.get_tasks import GET_TASKS_TOOL
from agent.tools.load_test import LOAD_TEST_TOOL
from agent.tools.save_test_result import SAVE_TEST_RESULT_TOOL


# Glavni register orodij
#
# Vsako orodje mora biti registrirano tukaj, ker tu not gleda funkcija
# za izvajanje orodij
TOOLS = {
    tool.name: tool for tool in [
        READ_FILE_TOOL, WRITE_FILE_TOOL, PATCH_FILE_TOOL,
        LIST_FILES_TOOL, GREP_TOOL, RUN_SHELL_TOOL, GET_GIT_DIFF_TOOL,
        WEBSERVICE_DEFINITION_TOOL, SAVE_TEST_CASES_TOOL, TEST_ENDPOINT_TOOL,
        LOAD_TEST_CASES_TOOL, SAVE_TEST_RESULTS_TOOL,

        CREATE_NEW_TASK_TOOL, GET_TASKS_TOOL, LOAD_TEST_TOOL, SAVE_TEST_RESULT_TOOL
        ]
}



# Orodja za agente
PLANNER_TOOLS = {
    tool.name: tool for tool in [
        CREATE_NEW_TASK_TOOL, WEBSERVICE_DEFINITION_TOOL
    ]
}

EXECUTOR_TOOLS = {
    tool.name: tool for tool in [
        TEST_ENDPOINT_TOOL,
        GET_TASKS_TOOL, LOAD_TEST_TOOL, SAVE_TEST_RESULT_TOOL
    ]
}


# Funkcija za pridobivanje shem za orodja
def get_tool_schemas(agent_name: str) -> list[dict]:
    if (agent_name == "PLANNER"):
        return [tool.schema() for tool in PLANNER_TOOLS.values()]
    if (agent_name == "EXECUTOR"):
        return [tool.schema() for tool in EXECUTOR_TOOLS.values()]


# Funkcija za izvajanje orodij
def execute_registered_tool(
    workspace: Path,
    tool_name: str,
    tool_input: dict
) -> dict:
    tool = TOOLS.get(tool_name)
    
    if tool is None:
        return {
            "ok": False,
            "error": f"Unknown tool: {tool_name}",
            "output": None,
            "metadata": None
        }
    
    try:
        result = tool.executor(workspace=workspace, **tool_input)

        return {
            "ok": result.ok,
            "output": result.output,
            "error": result.error,
            "metadata": result.metadata or {}
        }
        
    except TypeError as e:
        return {
            "ok": False,
            "output": None,
            "error": f"Invalid tool input: {e}",
            "metadata": {}
        }
        
    except Exception as e:
        return {
            "ok": False,
            "output": None,
            "error": str(e),
            "metadata": {}
        }