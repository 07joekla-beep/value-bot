from abc import ABC, abstractmethod
from typing import List, Tuple
from ..types import Event, MarketOdd

class OddsProvider(ABC):
    @abstractmethod
    def fetch_upcoming(self, sport_key: str, date_iso: str) -> Tuple[List[Event], List[MarketOdd]]:
        """Return events and odds for a given sport_key and date (YYYY-MM-DD)."""
        raise NotImplementedError
