import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

@dataclass
class Config:
    db_path: str
    providers: Dict[str, Dict[str, Any]]

def load_config(path: str = "config.json") -> Config:
    with open(path, "r", encoding="utf-8") as f:
        obj = json.load(f)
    return Config(db_path=obj.get("db_path", "valuebot.sqlite"),
                  providers=obj.get("providers", {}))
