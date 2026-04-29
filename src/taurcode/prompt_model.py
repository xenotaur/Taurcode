from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class Prompt:
    id: str
    name: str
    description: str
    keyword: str
    body: str
    source: str = ""
    targets: Dict[str, Any] = field(default_factory=dict)
