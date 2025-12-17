import math
from dataclasses import dataclass
from typing import Dict, Tuple
from ..types import Event

def logistic(x: float) -> float:
    return 1.0 / (1.0 + math.exp(-x))

@dataclass
class EloModel:
    # Simple Elo per (sport_key, team)
    ratings: Dict[Tuple[str,str], float]
    k: float = 20.0
    home_adv: float = 60.0  # elo points

    def __init__(self, k: float = 20.0, home_adv: float = 60.0):
        self.ratings = {}
        self.k = k
        self.home_adv = home_adv

    def get_rating(self, sport_key: str, team: str) -> float:
        return self.ratings.get((sport_key, team), 1500.0)

    def p_home_win(self, e: Event) -> float:
        rh = self.get_rating(e.sport_key, e.home_team) + self.home_adv
        ra = self.get_rating(e.sport_key, e.away_team)
        # Convert Elo diff to win prob
        return 1.0 / (1.0 + 10 ** (-(rh - ra) / 400.0))

    def update_from_result(self, e: Event, home_result: float) -> None:
        # home_result: 1.0 home win, 0.0 away win, 0.5 draw
        ph = self.p_home_win(e)
        rh = self.get_rating(e.sport_key, e.home_team)
        ra = self.get_rating(e.sport_key, e.away_team)
        self.ratings[(e.sport_key, e.home_team)] = rh + self.k * (home_result - ph)
        self.ratings[(e.sport_key, e.away_team)] = ra + self.k * ((1.0 - home_result) - (1.0 - ph))
