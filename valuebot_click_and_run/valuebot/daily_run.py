import argparse
import datetime as dt
from typing import List, Dict

from .config import load_config
from .db import DB
from .types import Candidate, Event, MarketOdd
from .selector import pick_daily_plays
from .model.elo import EloModel
from .providers.demo import DemoProvider
from .providers.oddsapi import OddsApiProvider

def build_provider(name: str, cfg) :
    if name == "demo":
        return DemoProvider()
    if name == "oddsapi":
        p = cfg.providers.get("oddsapi", {})
        api_key = p.get("api_key")
        if not api_key or api_key == "PUT_YOUR_KEY_HERE":
            raise SystemExit("Missing Odds API key. Set it in config.json (providers.oddsapi.api_key).")
        return OddsApiProvider(
            api_key=api_key,
            regions=p.get("regions", "us,eu"),
            markets=p.get("markets", "h2h"),
            odds_format=p.get("odds_format", "decimal"),
        )
    raise SystemExit(f"Unknown provider: {name}")

def candidates_from_odds(events: List[Event], odds: List[MarketOdd], model: EloModel) -> List[Candidate]:
    ev_map = {e.event_id: e for e in events}
    # For v1: only h2h HOME/AWAY handled cleanly by Elo
    out: List[Candidate] = []
    for o in odds:
        e = ev_map.get(o.event_id)
        if not e:
            continue
        if o.market != "h2h":
            continue
        if o.selection not in ("HOME", "AWAY"):
            continue
        p_home = model.p_home_win(e)
        p = p_home if o.selection == "HOME" else (1.0 - p_home)
        out.append(Candidate(event=e, market=o.market, selection=o.selection, odds=o.odds, p_model=p))
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--date", required=True, help="YYYY-MM-DD (UTC date part used by odds feed)")
    ap.add_argument("--provider", default="demo", choices=["demo","oddsapi"])
    ap.add_argument("--sport_key", default="basketball_ncaab", help="Provider sport key (e.g., basketball_ncaab)")
    ap.add_argument("--max_plays", type=int, default=3)
    ap.add_argument("--min_plays", type=int, default=0)
    ap.add_argument("--edge_min", type=float, default=0.02)
    ap.add_argument("--odds_sum_cap", type=float, default=10.0)
    ap.add_argument("--config", default="config.json")
    args = ap.parse_args()

    cfg = load_config(args.config)
    db = DB(cfg.db_path)
    provider = build_provider(args.provider, cfg)

    events, odds = provider.fetch_upcoming(args.sport_key, args.date)
    db.upsert_events(events)
    db.insert_odds(odds)

    model = EloModel()
    ts = dt.datetime.utcnow().isoformat(timespec="seconds")+"Z"

    cands = candidates_from_odds(events, odds, model)
    db.insert_predictions(ts, cands)

    picks = pick_daily_plays(
        cands,
        min_plays=args.min_plays,
        max_plays=args.max_plays,
        edge_min=args.edge_min,
        odds_sum_cap=args.odds_sum_cap,
    )
    db.save_picks(args.date, ts, picks)

    # Print
    print(f"Date: {args.date} | sport_key={args.sport_key} | provider={args.provider}")
    print(f"Candidates: {len(cands)} | Picks: {len(picks)} | odds_sum_cap={args.odds_sum_cap}")
    print("-"*72)
    total_odds = 0.0
    for c in picks:
        total_odds += c.odds
        e = c.event
        print(f"{e.home_team} vs {e.away_team} | {c.market} {c.selection} | odds={c.odds:.2f} | p={c.p_model:.3f} | EV={c.ev:.3%}")
    print("-"*72)
    print(f"Sum odds: {total_odds:.2f}")

if __name__ == "__main__":
    main()
