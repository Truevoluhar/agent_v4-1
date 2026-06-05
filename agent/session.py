from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import json
import uuid
from typing import Optional

@dataclass
class Event:
    type: str
    data: dict
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    
@dataclass
class Session:
    user_prompt: str
    workspace: str = "."
    permission_mode: str = "normal"
    interactive: bool = True
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    events: list[Event] = field(default_factory=list)
    final: Optional[str] = None
    
    def add_event(self, event_type: str, data: dict):
        self.events.append(Event(type=event_type, data=data))
        
    def workspace_path(self) -> Path:
        return Path(self.workspace).resolve()
    
    def save(self, path: str = ".myagent/sessions"):
        folder = Path(path)
        folder.mkdir(parents=True, exist_ok=True)
        
        file_path = folder / f"{self.id}.json"
        
        payload = {
            "id": self.id,
            "user_prompt": self.user_prompt,
            "workspace": self.workspace,
            "permission_mode": self.permission_mode,
            "interactive": self.interactive,
            "final": self.final,
            "events": [asdict(e) for e in self.events]
        }
        
        file_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return file_path