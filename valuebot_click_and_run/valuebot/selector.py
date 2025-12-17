from itertools import combinations
from typing import List, Optional
from .types import Candidate

def pick_daily_plays(
    candidates: List[Candidate],
    min_plays: int = 0,
    max_plays: int = 3,
    edge_min: float = 0.02,
    odds_sum_cap: float = 10.0,
) -> List[Candidate]:
    # Filter: must be valid probability, positive odds, and meet edge threshold
    filtered = [c for c in candidates if c.odds > 1.0 and 0.0 <= c.p_model <= 1.0 and c.ev >= edge_min]

    if not filtered:
        return [] if min_plays == 0 else []

    best_combo: Optional[List[Candidate]] = None
    best_score = float("-inf")

    for k in range(1, min(max_plays, len(filtered)) + 1):
        for combo in combinations(filtered, k):
            if sum(x.odds for x in combo) > odds_sum_cap:
                continue
            score = sum(x.ev for x in combo)  # simple and robust
            if score > best_score:
                best_score = score
                best_combo = list(combo)

    if not best_combo:
        return [] if min_plays == 0 else []

    return sorted(best_combo, key=lambda c: c.ev, reverse=True)
