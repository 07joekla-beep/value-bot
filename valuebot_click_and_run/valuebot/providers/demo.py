import datetime as dt
import random
from typing import List, Tuple
from .base import OddsProvider
from ..types import Event, MarketOdd

class DemoProvider(OddsProvider):
    def fetch_upcoming(self, sport_key: str, date_iso: str) -> Tuple[List[Event], List[MarketOdd]]:
        rng = random.Random(hash((sport_key, date_iso)) & 0xffffffff)
        day = dt.datetime.fromisoformat(date_iso)
        events: List[Event] = []
        odds: List[MarketOdd] = []

        teams = [f"Uni Team {i}" for i in range(1, 21)]
        rng.shuffle(teams)

        for i in range(0, 10, 2):  # 5 events
            home, away = teams[i], teams[i+1]
            eid = f"demo_{sport_key}_{date_iso}_{i//2}"
            commence = (day + dt.timedelta(hours=18+i)).isoformat(timespec="seconds")
            e = Event(event_id=eid, sport_key=sport_key, commence_time=commence, home_team=home, away_team=away, league="DEMO")
            events.append(e)

            # Create plausible decimal odds around 1.5-3.5
            p_home = rng.uniform(0.40, 0.70)
            home_odds = max(1.2, min(4.0, 1.0/p_home * rng.uniform(1.02, 1.08)))
            away_odds = max(1.2, min(4.5, 1.0/(1.0-p_home) * rng.uniform(1.02, 1.08)))

            ts = (day + dt.timedelta(hours=9)).isoformat(timespec="seconds")
            odds.append(MarketOdd(eid, "h2h", "HOME", float(f"{home_odds:.2f}"), "demo", ts))
            odds.append(MarketOdd(eid, "h2h", "AWAY", float(f"{away_odds:.2f}"), "demo", ts))

        return events, odds
