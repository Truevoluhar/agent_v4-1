import json
import subprocess
from pathlib import Path

from agent.session import Session
from agent.llm_client import FakeLLMClient, ModelResponse, ToolCall
from agent.loop import run_agent


def make_toy_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "toy-repo"
    repo.mkdir()

    (repo / "package.json").write_text(
        json.dumps({"scripts": {"test": "echo test-ok"}}),
        encoding="utf-8",
    )

    (repo / "src").mkdir()
    (repo / "src" / "index.js").write_text(
        "const message = 'hello';\nconsole.log(message);\n",
        encoding="utf-8",
    )

    subprocess.run("git init", cwd=repo, shell=True, check=True, capture_output=True)
    subprocess.run("git add .", cwd=repo, shell=True, check=True, capture_output=True)
    subprocess.run(
        'git commit -m "initial"',
        cwd=repo,
        shell=True,
        check=True,
        capture_output=True,
    )

    return repo


def get_tool_results(session):
    return [
        e.data["result"]
        for e in session.events
        if e.type == "tool_result"
    ]


def test_agent_reads_package_json(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="read_file",
            input={"path": "package.json"},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="read package.json", workspace=str(repo))
    run_agent(session, model)

    results = get_tool_results(session)

    assert results[0]["ok"] is True
    assert "scripts" in results[0]["output"]


def test_agent_finds_files_with_grep(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="grep",
            input={"pattern": "message", "path": "."},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="grep message", workspace=str(repo))
    run_agent(session, model)

    results = get_tool_results(session)

    assert results[0]["ok"] is True
    assert "src/index.js" in results[0]["output"]


def test_agent_edits_one_file(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="patch_file",
            input={
                "path": "src/index.js",
                "old_text": "hello",
                "new_text": "goodbye",
            },
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="edit one file", workspace=str(repo))
    run_agent(session, model)

    content = (repo / "src" / "index.js").read_text()

    assert "goodbye" in content
    assert "hello" not in content


def test_agent_produces_git_diff(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="patch_file",
            input={
                "path": "src/index.js",
                "old_text": "hello",
                "new_text": "goodbye",
            },
        )),
        ModelResponse(tool_call=ToolCall(
            name="get_git_diff",
            input={},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="edit and diff", workspace=str(repo))
    run_agent(session, model)

    results = get_tool_results(session)
    diff_result = results[-1]

    assert diff_result["ok"] is True
    assert "-const message = 'hello';" in diff_result["output"]
    assert "+const message = 'goodbye';" in diff_result["output"]


def test_tool_errors_are_returned_cleanly(tmp_path):
    repo = make_toy_repo(tmp_path)

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="read_file",
            input={"path": "missing.txt"},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="read missing file", workspace=str(repo))
    run_agent(session, model)

    results = get_tool_results(session)

    assert results[0]["ok"] is False
    assert "File not found" in results[0]["error"]


def test_huge_output_is_truncated_safely(tmp_path):
    repo = make_toy_repo(tmp_path)

    huge = "x" * 50_000
    (repo / "huge.txt").write_text(huge, encoding="utf-8")

    model = FakeLLMClient([
        ModelResponse(tool_call=ToolCall(
            name="read_file",
            input={"path": "huge.txt"},
        )),
        ModelResponse(text="Done."),
    ])

    session = Session(user_prompt="read huge file", workspace=str(repo))
    run_agent(session, model)

    results = get_tool_results(session)

    assert results[0]["ok"] is True
    assert len(results[0]["output"]) < 20_000
    assert results[0]["metadata"]["truncated"] is True
    assert "[TRUNCATED" in results[0]["output"]
