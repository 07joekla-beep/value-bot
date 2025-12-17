# ValueBot v1 (1–3 value-spel/dag, odds-summa ≤ 10)

Det här projektet bygger en *rekommendationsmotor* för value betting:
- hämtar odds från en **provider** (exempel: The Odds API),
- räknar modell-sannolikheter (baseline Elo),
- väljer 1–3 spel/dag med constraint **sum(odds) ≤ 10**,
- loggar allt i SQLite för uppföljning.

> Viktigt: Bet-placering via Unibet automatiskt ingår inte i v1. Använd officiella API:er och följ villkor.
> V1 ger förslag/rekar baserat på data du matar in.

## Snabbstart

### 1) Installera
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2) Konfigurera
Kopiera och fyll i API-nyckel om du använder The Odds API:
- `config.example.json` -> `config.json`

### 3) Kör dagens urval
```bash
python -m valuebot.daily_run --date 2025-12-17 --provider oddsapi --sport_key basketball_ncaab
```

Om du saknar API-nyckel kan du testa med demo-data:
```bash
python -m valuebot.daily_run --date 2025-12-17 --provider demo
```

## Viktiga flaggor
- `--max_plays` (default 3)
- `--odds_sum_cap` (default 10)
- `--edge_min` (default 0.02)

## Struktur
- `valuebot/providers/`  odds-källor (demo + oddsapi)
- `valuebot/model/`      baseline Elo-modell (per sport_key)
- `valuebot/selector.py` urvalslogik (kombinationer upp till 3 spel)
- `valuebot/db.py`       SQLite logg (odds, predictions, picks)
