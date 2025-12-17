from dataclasses import dataclass
from typing import Optional

@dataclass(frozen=True)
class Event:
    event_id: str
    sport_key: str
    commence_time: str  # ISO string
    home_team: str
    away_team: str
    league: Optional[str] = None

@dataclass(frozen=True)
class MarketOdd:
    event_id: str
    market: str        # h2h, spreads, totals
    selection: str     # e.g. HOME, AWAY, OVER 145.5
    odds: float        # decimal odds
    bookmaker: str
    last_update: str   # ISO string

@dataclass(frozen=True)
class Candidate:
    event: Event
    market: str
    selection: str
    odds: float
    p_model: float

    @property
    def ev(self) -> float:
        return self.p_model * self.odds - 1.0
