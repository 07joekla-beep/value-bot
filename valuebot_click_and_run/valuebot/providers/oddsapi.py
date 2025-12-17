import datetime as dt
from typing import List, Tuple, Dict, Any
import requests
from .base import OddsProvider
from ..types import Event, MarketOdd

class OddsApiProvider(OddsProvider):
    """Provider for The Odds API v4.

    Requires api_key in config.json.
    """
    def __init__(self, api_key: str, regions: str = "us,eu", markets: str = "h2h", odds_format: str = "decimal"):
        self.api_key = api_key
        self.regions = regions
        self.markets = markets
        self.odds_format = odds_format

    def fetch_upcoming(self, sport_key: str, date_iso: str) -> Tuple[List[Event], List[MarketOdd]]:
        # NOTE: The Odds API doesn't filter by date directly in one call;
        # we fetch upcoming and then filter to the requested UTC date.
        url = f"https://api.the-odds-api.com/v4/sports/{sport_key}/odds"
        params = {
            "apiKey": self.api_key,
            "regions": self.regions,
            "markets": self.markets,
            "oddsFormat": self.odds_format,
        }
        r = requests.get(url, params=params, timeout=30)
        r.raise_for_status()
        data = r.json()

        events: Dict[str, Event] = {}
        odds: List[MarketOdd] = []

        for item in data:
            commence = item.get("commence_time")
            if not commence:
                continue
            # Filter by requested date (UTC date part)
            if commence[:10] != date_iso:
                continue

            eid = item["id"]
            e = Event(
                event_id=eid,
                sport_key=sport_key,
                commence_time=commence,
                home_team=item.get("home_team","HOME"),
                away_team=item.get("away_team","AWAY"),
                league=item.get("sport_title"),
            )
            events[eid] = e

            for bk in item.get("bookmakers", []):
                bname = bk.get("title", "bookmaker")
                last_update = bk.get("last_update", dt.datetime.utcnow().isoformat(timespec="seconds")+"Z")
                for m in bk.get("markets", []):
                    mkey = m.get("key")
                    for out in m.get("outcomes", []):
                        name = out.get("name")
                        price = out.get("price")
                        if price is None:
                            continue
                        # Normalize selection
                        if mkey == "h2h":
                            if name == e.home_team:
                                sel = "HOME"
                            elif name == e.away_team:
                                sel = "AWAY"
                            else:
                                sel = str(name)
                        else:
                            # spreads/totals include point field
                            pt = out.get("point")
                            sel = f"{name} {pt}" if pt is not None else str(name)

                        odds.append(MarketOdd(
                            event_id=eid,
                            market=mkey,
                            selection=sel,
                            odds=float(price),
                            bookmaker=bname,
                            last_update=last_update,
                        ))

        return list(events.values()), odds
