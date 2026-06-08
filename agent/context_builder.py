from dataclasses import dataclass, asdict

from agent.session import Session
from agent.agent import Agent
from agent.db import AgentDatabase

class ContextBuilder:
    
    system_prompt: str
    skills: str
    
    def __init__(self, agent_db: AgentDatabase):
        self.agent_db = agent_db


    def build_context(self, session: Session, agent: Agent) -> list[dict]:
        
        print("Starting to build context ...")
        ws_info = self.get_webservice_data()
        messages = [
            {
                "role": "system",
                "content": agent.system_message + "\n\n" + agent.skills
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


    def get_webservice_data(self):
        try:
            webservices = self.agent_db.select("SELECT * FROM services")

            output_string = ""
            for ws in webservices:
                output_string += f"Webservice name: {ws["service_name"]}, "
                output_string += f"Base url: {ws["base_url"]}, "
                output_string += f"Specifications url: {ws["spec_url"]}\n\n"
            return output_string
        except Exception as e:
            print(f"[ContextData] ERROR in get_webservice_data: {e}")
