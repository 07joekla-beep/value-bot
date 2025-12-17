import sqlite3
from typing import Iterable, Optional, Tuple
from .types import Event, MarketOdd, Candidate

SCHEMA = '''
PRAGMA journal_mode=WAL;

CREATE TABLE IF NOT EXISTS events(
  event_id TEXT PRIMARY KEY,
  sport_key TEXT NOT NULL,
  commence_time TEXT NOT NULL,
  home_team TEXT NOT NULL,
  away_team TEXT NOT NULL,
  league TEXT
);

CREATE TABLE IF NOT EXISTS odds(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  ts TEXT NOT NULL,
  bookmaker TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  odds REAL NOT NULL,
  UNIQUE(event_id, ts, bookmaker, market, selection)
);

CREATE TABLE IF NOT EXISTS predictions(
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  event_id TEXT NOT NULL,
  ts TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  p_model REAL NOT NULL,
  ev REAL NOT NULL,
  UNIQUE(event_id, ts, market, selection)
);

CREATE TABLE IF NOT EXISTS picks(
  run_date TEXT NOT NULL,
  ts TEXT NOT NULL,
  event_id TEXT NOT NULL,
  market TEXT NOT NULL,
  selection TEXT NOT NULL,
  odds REAL NOT NULL,
  p_model REAL NOT NULL,
  ev REAL NOT NULL,
  PRIMARY KEY(run_date, event_id, market, selection)
);
'''

class DB:
    def __init__(self, path: str):
        self.path = path
        self.conn = sqlite3.connect(path)
        self.conn.execute("PRAGMA foreign_keys=ON;")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def upsert_events(self, events: Iterable[Event]) -> None:
        q = '''INSERT INTO events(event_id, sport_key, commence_time, home_team, away_team, league)
               VALUES(?,?,?,?,?,?)
               ON CONFLICT(event_id) DO UPDATE SET
                 sport_key=excluded.sport_key,
                 commence_time=excluded.commence_time,
                 home_team=excluded.home_team,
                 away_team=excluded.away_team,
                 league=excluded.league;'''
        self.conn.executemany(q, [(e.event_id, e.sport_key, e.commence_time, e.home_team, e.away_team, e.league) for e in events])
        self.conn.commit()

    def insert_odds(self, odds: Iterable[MarketOdd]) -> None:
        q = '''INSERT OR IGNORE INTO odds(event_id, ts, bookmaker, market, selection, odds)
               VALUES(?,?,?,?,?,?);'''
        self.conn.executemany(q, [(o.event_id, o.last_update, o.bookmaker, o.market, o.selection, o.odds) for o in odds])
        self.conn.commit()

    def insert_predictions(self, ts: str, preds: Iterable[Candidate]) -> None:
        q = '''INSERT OR IGNORE INTO predictions(event_id, ts, market, selection, p_model, ev)
               VALUES(?,?,?,?,?,?);'''
        self.conn.executemany(q, [(c.event.event_id, ts, c.market, c.selection, c.p_model, c.ev) for c in preds])
        self.conn.commit()

    def save_picks(self, run_date: str, ts: str, picks: Iterable[Candidate]) -> None:
        q = '''INSERT OR REPLACE INTO picks(run_date, ts, event_id, market, selection, odds, p_model, ev)
               VALUES(?,?,?,?,?,?,?,?);'''
        self.conn.executemany(q, [(run_date, ts, c.event.event_id, c.market, c.selection, c.odds, c.p_model, c.ev) for c in picks])
        self.conn.commit()
