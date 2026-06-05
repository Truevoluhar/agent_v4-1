import argparse

from agent.session import Session
from agent.llm_client import FakeLLMClient, ModelResponse, ToolCall
from agent.llm_openai import OpenAICompatibleLLMClient
from agent.loop import run_agent
from agent.agent import Agent
from agent.verifier import Verifier
from agent.db import AgentDatabase

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
RESOURCES_PATH = str(PROJECT_ROOT / "resources")
DATABASE_PATH = str(PROJECT_ROOT / "db" / "db_agent4-1.db")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("prompt", help="Task for the agent")
    
    parser.add_argument(
        "--workspace", 
        default=".", 
        help="Workspace directory the agent can access."
    )
    
    parser.add_argument(
        "--permission-mode",
        choices=["safe", "normal", "trusted", "yolo", "ci"],
        default="normal",
        help="Permission mode"
    )
    
    parser.add_argument(
        "--non-interactive",
        action="store_true",
        help="Deny action that requires user approval"
    )
    
    parser.add_argument(
        "--llm",
        choices=["fake", "openai"],
        default="openai",
        help="Which LLM client to use"
    )
    
    parser.add_argument(
        "--model",
        default=None,
        help="define which model to use"
    )
    
    args = parser.parse_args()


    agent_db = AgentDatabase(DATABASE_PATH)

    return

    verifier = Verifier(
        workspace=Path(args.workspace),
        artifacts_path="./artifacts"
    )


    planner_session = Session(
        user_prompt=args.prompt, 
        workspace=args.workspace,
        permission_mode=args.permission_mode,
        interactive=args.non_interactive
    )
    
        
    planner_agent = Agent(
        name="PLANNER", 
        model="unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:Q3_K_M",
        api_key="EMPTY",
        base_url="http://localhost:8080/v1",
        temperature=0.3,
        resources_path=RESOURCES_PATH
    )
    
    planner_response = run_agent(planner_session, planner_agent)
    print(planner_response)
    
    print(f"Session saved: ./myagent/sessions/{planner_session.id}.json")
    
    
    
    # Verification of a planner task
    is_planner_done = verifier.verify_planner_results()
    print(f"Verifier result: {is_planner_done}")



    # Executor run
    executor_session = Session(
        user_prompt=args.prompt, 
        workspace=args.workspace,
        permission_mode=args.permission_mode,
        interactive=args.non_interactive
    )
    
    executor_agent = Agent(
        name="EXECUTOR", 
        model="unsloth/Qwen3-Coder-30B-A3B-Instruct-GGUF:Q3_K_M",
        api_key="EMPTY",
        base_url="http://localhost:8080/v1",
        temperature=0.3,
        resources_path=RESOURCES_PATH
    )
    
    executor_response = run_agent(executor_session, executor_agent, max_steps=75)
    print(executor_response)
    
if __name__ == "__main__":
    main()
    
