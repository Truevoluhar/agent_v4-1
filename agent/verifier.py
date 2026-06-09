import os
from pathlib import Path

from pydantic import BaseModel

from agent.tools.base import resolve_workspace_path
from agent.llm_openai import OpenAICompatibleLLMClient

from pydantic import BaseModel


class RequestResult(BaseModel):
    method: str
    url: str


class ResponseResult(BaseModel):
    status_code: int
    body_preview: str
    duration_seconds: float


class AssertionResult(BaseModel):
    passed: bool
    message: str


class WebserviceTestResult(BaseModel):
    request: RequestResult
    response: ResponseResult
    assertions: list[AssertionResult]
    errors: list[str]



class Verifier:

    def __init__(self, workspace: Path, artifacts_path: str):
        self.workspace = workspace
        self.artifacts_path = resolve_workspace_path(workspace=workspace, path=artifacts_path)

    def verify_planner_results(self) -> bool:
        filename_to_search = "test-cases.json"
        filename_path = Path(os.path.join(self.artifacts_path, filename_to_search))
        
        if filename_path.is_file:
            print(f"Planner end file found: {str(filename_path)}")
            return True
        else:
            print(f"Planner end file NOT found: {str(filename_path)}")
            return False


    def produce_final_response(self, model: OpenAICompatibleLLMClient, messages, path: str):
        
        files_path = resolve_workspace_path(self.workspace, path)
        try:
            results_files = os.listdir(files_path)
        except Exception as e:
            return f"ERROR in listing results_files: {e}"
        
        try:
            for file in results_files:
                file_str = str(file)
                
                model.chat_structured(
                    messages=messages,
                    response_model=WebserviceTestResult
                )        
        except Exception as e:
            return f"ERROR in producing final response: {e}"
        