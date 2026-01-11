from dataclasses import dataclass, field
from enum import Enum
from typing import List, Tuple
import random
import datetime

class BagStatus(Enum):
    CHECK_IN = "Check In"
    SECURITY = "Security"
    AT_GATE = "At Gate"
    IN_TRANSIT = "In Transit"
    LANDED = "Landed"
    BAGGAGE_CLAIM = "Baggage Claim"
    CLAIMED = "Claimed"
    LOST = "Lost"

@dataclass
class Airport:
    code: str
    name: str
    lat: float
    lon: float

@dataclass
class Bag:
    id: str
    owner: str
    origin: Airport
    destination: Airport
    current_lat: float
    current_lon: float
    status: BagStatus
    color: List[int] # RGBA
    history: List[Tuple[datetime.datetime, str]] = field(default_factory=list)
    progress: float = 0.0 # 0.0 to 1.0 for flight progress

    def update_history(self, message: str):
        self.history.append((datetime.datetime.now(), message))
