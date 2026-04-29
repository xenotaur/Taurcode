from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class Prompt:
    id: str
    name: str
    description: str
    keyword: str
    body: str
    targets: Dict[str, Any] = field(default_factory=dict)
