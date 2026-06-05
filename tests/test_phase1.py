from pathlib import Path
import json

from agent.session import Session
from agent.llm_client import FakeLLMClient
from agent.loop import run_agent

def test_user_can_submit_prompt():
    session = Session(user_prompt="fix the failing tests")
    
    assert session.user_prompt == "fix the failing tests"
    

def test_agent_can_call_fake_tool():
    session = Session(user_prompt="use the fake tool")
    model = FakeLLMClient()
    
    run_agent(session, model)
    
    tool_calls = [
        e for e in session.events
        if e.type == "model_tool_call"
    ]
    
    assert len(tool_calls) == 1
    assert tool_calls[0].data["name"] == "fake_tool"
    

def test_tool_result_is_returned_to_session():
    session = Session(user_prompt="use the fake tool")
    model = FakeLLMClient()
    
    run_agent(session, model)
    
    tool_results = [
        e for e in session.events
        if e.type == "tool_result"
    ]
    
    assert len(tool_results) == 1
    assert tool_results[0].data["result"]["ok"] is True
    
    
def test_agent_stops_with_final_text():
    session = Session(user_prompt="finish")
    model = FakeLLMClient()
    
    final = run_agent(session, model)
    
    assert final == "Task finished. The fake tool result was processed."
    assert session.final == final
    
def test_session_transcript_is_saved(tmp_path):
    session = Session(user_prompt="save transcript")
    model = FakeLLMClient()
    
    run_agent(session, model)
    
    path = session.save(path=str(tmp_path))
    
    assert path.exists()
    
    data = json.loads(path.read_text())
    
    assert data["user_prompt"] == "save transcript"
    assert data["final"] is not None
    assert len(data["events"]) > 0