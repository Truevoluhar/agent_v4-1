import os
from pathlib import Path
from agent.tools.base import resolve_workspace_path

class Verifier:

    def __init__(self, workspace: Path, artifacts_path: str):

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

