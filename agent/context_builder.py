from dataclasses import dataclass, asdict


@dataclass
class ContextData:
    system_prompt: str
    skills: str
    