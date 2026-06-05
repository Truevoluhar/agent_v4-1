from dataclasses import dataclass, asdict

from agent.session import Session
from agent.agent import Agent


@dataclass
class ContextData:
    system_prompt: str
    skills: str
    

def build_context(session: Session, agent: Agent) -> list[dict]:
    
    print("Starting to build context ...")
    ws_info = """
Base url to test is http://localhost:8001/, specifications are here: http://localhost:8001/openapi.json"""
    messages = [
        {
            "role": "system",
            "content": agent.system_message + agent.skills + ws_info
        },
        {
            "role": "user",
            "content": session.user_prompt + ws_info
        }
    ]
    
    for event in session.events:
         messages.append({
            "role": "event",
            "content": {
                "type": event.type,
                "data": event.data,
            }
        })
    
    print(str(messages))
    print("Context built successfully.")
    
    return messages