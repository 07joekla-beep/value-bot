import datetime as dt
import streamlit as st

from valuebot.config import load_config
from valuebot.db import DB
from valuebot.model.elo import EloModel
from valuebot.providers.demo import DemoProvider
from valuebot.providers.oddsapi import OddsApiProvider
from valuebot.daily_run import candidates_from_odds
from valuebot.selector import pick_daily_plays

st.set_page_config(page_title="ValueBot v1", layout="wide")

st.title("ValueBot v1 – 1–3 value-spel/dag (odds-summa ≤ 10)")
st.caption("Det här är en rekommendationsmotor. Den lägger inga spel åt dig.")

def build_provider(provider_name, cfg):
    if provider_name == "demo":
        return DemoProvider()
    if provider_name == "oddsapi":
        p = cfg.providers.get("oddsapi", {})
        api_key = p.get("api_key")
        if not api_key or api_key == "PUT_YOUR_KEY_HERE":
            st.error("Saknar Odds API-nyckel. Fyll i config.json (providers.oddsapi.api_key).")
            st.stop()
        return OddsApiProvider(
            api_key=api_key,
            regions=p.get("regions", "us,eu"),
            markets=p.get("markets", "h2h"),
            odds_format=p.get("odds_format", "decimal"),
        )
    st.error(f"Okänd provider: {provider_name}")
    st.stop()

with st.sidebar:
    st.header("Inställningar")
    cfg_path = st.text_input("config.json path", value="config.json")
    provider = st.selectbox("Odds-källa", ["demo", "oddsapi"], index=0)
    sport_key = st.text_input("sport_key", value="basketball_ncaab")
    date_iso = st.date_input("Datum (UTC)", value=dt.date.today()).isoformat()

    st.subheader("Urval")
    max_plays = st.slider("Max antal spel", 1, 3, 3)
    odds_sum_cap = st.number_input("Max summa odds", min_value=1.0, max_value=100.0, value=10.0, step=0.5)
    edge_min = st.number_input("Min edge (EV)", min_value=0.0, max_value=0.5, value=0.02, step=0.01, format="%.2f")

    run = st.button("Kör")

if run:
    cfg = load_config(cfg_path)
    db = DB(cfg.db_path)
    prov = build_provider(provider, cfg)

    events, odds = prov.fetch_upcoming(sport_key, date_iso)
    db.upsert_events(events)
    db.insert_odds(odds)

    model = EloModel()
    ts = dt.datetime.utcnow().isoformat(timespec="seconds")+"Z"

    cands = candidates_from_odds(events, odds, model)
    db.insert_predictions(ts, cands)

    picks = pick_daily_plays(
        cands,
        min_plays=0,
        max_plays=max_plays,
        edge_min=edge_min,
        odds_sum_cap=odds_sum_cap,
    )
    db.save_picks(date_iso, ts, picks)

    st.subheader("Dagens picks")
    if not picks:
        st.info("Inga spel hittades som klarade din edge och odds-summa-regeln.")
    else:
        rows = []
        for c in picks:
            e = c.event
            rows.append({
                "Match": f"{e.home_team} vs {e.away_team}",
                "Marknad": c.market,
                "Val": c.selection,
                "Odds": round(c.odds, 2),
                "p_model": round(c.p_model, 3),
                "EV": f"{c.ev*100:.2f}%"
            })
        st.dataframe(rows, use_container_width=True)
        st.metric("Summa odds", round(sum(c.odds for c in picks), 2))

    st.subheader("Kandidater (h2h)")
    rows2 = []
    for c in sorted(cands, key=lambda x: x.ev, reverse=True)[:50]:
        e = c.event
        rows2.append({
            "Match": f"{e.home_team} vs {e.away_team}",
            "Val": c.selection,
            "Odds": round(c.odds, 2),
            "p_model": round(c.p_model, 3),
            "EV": f"{c.ev*100:.2f}%"
        })
    st.dataframe(rows2, use_container_width=True)
