from dataclasses import dataclass, field
from typing import Dict

@dataclass
class Chat:
    req_offers: Dict[str, float] = field(default_factory=dict)
    rsp_offers: Dict[str, float] = field(default_factory=dict)
    req_bids: Dict[str, float] = field(default_factory=dict)
    rsp_bids: Dict[str, float] = field(default_factory=dict)
