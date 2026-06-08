from typing import Any
from agent.llm_openai import OpenAICompatibleLLMClient
from agent.tools.base import resolve_workspace_path

class Agent:
    
    name: str
    system_message: str
    skills: str
    client: Any
    
    def __init__(self, name, model, api_key, base_url, temperature, resources_path):
        
        self.name = name
        self.resources_path = resources_path
        
        self.system_message = self.load_system_message(self.name)
        self.skills = self.load_skills(self.name)
        
        self.client = OpenAICompatibleLLMClient(model, api_key, base_url, temperature)
       
        
    def load_system_message(self, name):
        print(f"[]Loading system message ...")
        path = self.resources_path + "/" + self.name + "/AGENT.md"
        with open(path, "r") as f:
            content = f.read()
            return content
    
    def load_skills(self, name):
        print("Loading skills ...")
        path = self.resources_path + "/" + self.name + "/SKILLS.md"
        with open(path, "r") as f:
            content = f.read()
            return content