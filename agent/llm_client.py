from dataclasses import dataclass
from typing import Optional, Any
from pydantic import BaseModel

@dataclass
class ToolCall:
    name: str
    input: dict
    id: Optional[str] = None
    

@dataclass
class ModelResponse:
    text: Optional[str] = None
    tool_call: Optional[ToolCall] = None
    parsed: Optional[Any] = None
    reasoning_content: Optional[str] = None
    
    @property
    def has_tool_call(self) -> bool:
        return self.tool_call is not None
        

    
class FakeLLMClient:
    
    def __init__(self, scripted_calls=None):
        self.call_count = 0
        self.scripted_calls = scripted_calls or []
        
    def chat(self, messages: list[dict], tools: list[dict]) -> ModelResponse:
        if self.call_count < len(self.scripted_calls):
            response = self.scripted_calls[self.call_count]
            self.call_count += 1
            return response
        
        self.call_count += 1
        return ModelResponse(text="Task finished.")