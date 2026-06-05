import json
import subprocess
from pathlib import Path

from agent.session import Session
from agent.llm_client import FakeLLMClient, ModelResponse, ToolCall
from agent.loop import run_agent
from agent.permissions import permission_gate


def make_toy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "toy-repo"
    repo.mkdir()

    (repo / "package.json").write_text(
        json.dumps({"scripts": {"test": "echo test-ok"}}),
        encoding="utf-8",
    )

    (repo / "src").mkdir()
    (repo / "src" / "index.js").write_text(
        "console.log('hello');\n",
        encoding="utf-8",
    )

    subprocess.run("git init", cwd=repo, shell=True, check=True, capture_output=True)
    subprocess.run('git config user.email "test@example.com"', cwd=repo, shell=True, check=True)
    subprocess.run('git config user.name "Test User"', cwd=repo, shell=True, check=True)
    subprocess.run("git add .", cwd=repo, shell=True, check=True, capture_output=True)
    subprocess.run('git commit -m "initial"', cwd=repo, shell=True, check=True, capture_output=True)

    return repo


def get_tool_results(session):
    return [
        e.data["result"]
        for e in session.events
        if e.type == "tool_result"
    ]


def get_permission_decisions(session):
    return [
        e.data
        for e in session.events
        if e.type == "permission_decision"
    ]
    
    
    

def test_agent_cannot_read_ssh_private_key(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="read_file",
            input={"path": "~/.ssh/id_rsa"},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="read private key",
        workspace=str(repo),
        permission_mode="yolo",
    )

    run_agent(session, model)

    results = get_tool_results(session)

    assert results[0]["ok"] is False
    assert "Permission denied" in results[0]["error"]

    decisions = get_permission_decisions(session)

    assert decisions[0]["resolved_action"] == "deny"
    assert decisions[0]["matched_rule"] == "deny_home_path"
    

    
    
def test_agent_cannot_modify_files_outside_workspace(tmp_path):
    repo = make_toy_repo(tmp_path)
    outside_file = tmp_path / "outside.txt"
    outside_file.write_text("do not edit", encoding="utf-8")

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="write_file",
            input={
                "path": "../outside.txt",
                "content": "edited",
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="modify outside file",
        workspace=str(repo),
        permission_mode="yolo",
    )

    run_agent(session, model)

    assert outside_file.read_text(encoding="utf-8") == "do not edit"

    results = get_tool_results(session)

    assert results[0]["ok"] is False
    assert "Permission denied" in results[0]["error"]

    decisions = get_permission_decisions(session)

    assert decisions[0]["resolved_action"] == "deny"
    assert decisions[0]["matched_rule"] == "deny_path_escape"


def test_agent_must_ask_before_shell_command_in_normal_mode(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="run_shell",
            input={
                "command": "echo hello",
                "cwd": ".",
                "timeout": 5,
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="run shell",
        workspace=str(repo),
        permission_mode="normal",
        interactive=True,
    )

    run_agent(session, model, input_func=lambda prompt: "n")

    decisions = get_permission_decisions(session)
    results = get_tool_results(session)

    assert decisions[0]["decision"] == "ask"
    assert decisions[0]["resolved_action"] == "deny"
    assert results[0]["ok"] is False


def test_shell_command_runs_when_user_approves(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="run_shell",
            input={
                "command": "echo hello",
                "cwd": ".",
                "timeout": 5,
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="run shell",
        workspace=str(repo),
        permission_mode="normal",
        interactive=True,
    )

    run_agent(session, model, input_func=lambda prompt: "y")

    decisions = get_permission_decisions(session)
    results = get_tool_results(session)

    assert decisions[0]["decision"] == "ask"
    assert decisions[0]["resolved_action"] == "allow"
    assert results[0]["ok"] is True
    assert "hello" in results[0]["output"]


def test_deny_rule_overrides_yolo_mode(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="run_shell",
            input={
                "command": "rm -rf *",
                "cwd": ".",
                "timeout": 5,
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="delete everything",
        workspace=str(repo),
        permission_mode="yolo",
        interactive=True,
    )

    run_agent(session, model)

    decisions = get_permission_decisions(session)
    results = get_tool_results(session)

    assert decisions[0]["decision"] == "deny"
    assert decisions[0]["resolved_action"] == "deny"
    assert results[0]["ok"] is False
    assert "Permission denied" in results[0]["error"]


def test_permission_decisions_are_logged(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="read_file",
            input={"path": "package.json"},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="read package json",
        workspace=str(repo),
        permission_mode="normal",
    )

    run_agent(session, model)

    decisions = get_permission_decisions(session)

    assert len(decisions) == 1
    assert decisions[0]["tool"] == "read_file"
    assert decisions[0]["decision"] == "allow"
    assert decisions[0]["resolved_action"] == "allow"
    assert "reason" in decisions[0]


def test_non_interactive_mode_fails_closed_for_shell(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="run_shell",
            input={
                "command": "echo should-not-run",
                "cwd": ".",
                "timeout": 5,
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="run shell noninteractive",
        workspace=str(repo),
        permission_mode="normal",
        interactive=False,
    )

    run_agent(session, model)

    decisions = get_permission_decisions(session)
    results = get_tool_results(session)

    assert decisions[0]["decision"] == "deny"
    assert decisions[0]["resolved_action"] == "deny"
    assert results[0]["ok"] is False


def test_safe_mode_denies_write(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="write_file",
            input={
                "path": "src/index.js",
                "content": "console.log('changed');\n",
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(
        user_prompt="write file in safe mode",
        workspace=str(repo),
        permission_mode="safe",
    )

    run_agent(session, model)

    content = (repo / "src" / "index.js").read_text(encoding="utf-8")

    assert "changed" not in content

    decisions = get_permission_decisions(session)

    assert decisions[0]["resolved_action"] == "deny"


def test_trusted_mode_allows_write_but_asks_shell(tmp_path):
    repo = make_toy_repo(tmp_path)

    write_decision = permission_gate(
        tool_name="write_file",
        tool_input={"path": "src/index.js", "content": "x"},
        workspace=repo,
        mode="trusted",
        interactive=True,
    )

    shell_decision = permission_gate(
        tool_name="run_shell",
        tool_input={"command": "echo hello", "cwd": "."},
        workspace=repo,
        mode="trusted",
        interactive=True,
    )

    assert write_decision.action == "allow"
    assert shell_decision.action == "ask"


def test_ci_mode_denies_write_and_shell(tmp_path):
    repo = make_toy_repo(tmp_path)

    write_decision = permission_gate(
        tool_name="write_file",
        tool_input={"path": "src/index.js", "content": "x"},
        workspace=repo,
        mode="ci",
        interactive=False,
    )

    shell_decision = permission_gate(
        tool_name="run_shell",
        tool_input={"command": "echo hello", "cwd": "."},
        workspace=repo,
        mode="ci",
        interactive=False,
    )

    read_decision = permission_gate(
        tool_name="read_file",
        tool_input={"path": "package.json"},
        workspace=repo,
        mode="ci",
        interactive=False,
    )

    assert write_decision.action == "deny"
    assert shell_decision.action == "deny"
    assert read_decision.action == "allow"