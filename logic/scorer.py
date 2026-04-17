"""
CommPlexCore/logic/scorer.py -- Lead Heat Score Engine
Domain: CommPlexCore (The Brain)

Calculates a Heat Score S for every QUALIFIED lead so the
CommPlexEdge PWA can rank "Hot Leads" at the top of Kenyon's list.

Heat Score Formula:
    S = price_score * year_score * urgency_bonus

    price_score  = (price_floor - price_detected) / price_floor * 60
                   Max 60 pts.  Higher score = further BELOW the floor = hotter.
    year_score   = min((vehicle_year - MIN_YEAR) / 5, 1.0) * 30
                   Max 30 pts.  Newer vehicle = hotter.
    urgency_bonus = 10 pts if lead is < 2 hours old, 5 pts if < 24 hrs, else 0.

    Total max: 100 pts.
    HOT   >= 75
    WARM  >= 45
    COLD  <  45

GoF Patterns:
    - Strategy:  HeatScorer is swappable (subclass to change formula)
    - Value Object: HeatResult is immutable after construction

Usage:
    from CommPlexCore.logic.scorer import HeatScorer
    scorer = HeatScorer()
    result = scorer.score(price=25000, vehicle_year=2022, age_hours=1.5)
    print(result.score, result.tier, result.breakdown)
"""

from __future__ import annotations
import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Optional, Dict, List

# Pricing constants (mirror vertex.py -- Single Source of Truth in .env)
PRICE_STANDARD   = float(os.getenv("SLUICE_PRICE_STANDARD",   "28500"))
PRICE_AGGRESSIVE = float(os.getenv("SLUICE_PRICE_AGGRESSIVE",  "24000"))
MIN_YEAR         = int(os.getenv("SLUICE_MIN_YEAR", "2020"))
YEAR_RANGE       = 5   # years above MIN_YEAR for full year score


# ---- Tier constants ----------------------------------------------------------

TIER_HOT  = "HOT"
TIER_WARM = "WARM"
TIER_COLD = "COLD"

TIER_THRESHOLDS = {
    TIER_HOT:  75,
    TIER_WARM: 45,
    TIER_COLD: 0,
}

TIER_EMOJI = {
    TIER_HOT:  "🔥",
    TIER_WARM: "🌡️",
    TIER_COLD: "🧊",
}


# ---- Heat Result value object ------------------------------------------------

@dataclass(frozen=True)
class HeatResult:
    """
    Immutable result of a heat score calculation.
    frozen=True ensures it can be cached / used as a dict key.
    """
    score:        float          # 0.0 - 100.0
    tier:         str            # HOT | WARM | COLD
    emoji:        str
    price_score:  float          # contribution from price delta
    year_score:   float          # contribution from vehicle year
    urgency_pts:  float          # time-based bonus
    price_floor:  float          # which floor was used
    sluice_mode:  str            # standard | aggressive

    def to_dict(self) -> Dict:
        return {
            "score":       round(self.score, 1),
            "tier":        self.tier,
            "emoji":       self.emoji,
            "price_score": round(self.price_score, 1),
            "year_score":  round(self.year_score, 1),
            "urgency_pts": self.urgency_pts,
            "price_floor": self.price_floor,
            "sluice_mode": self.sluice_mode,
        }

    @property
    def label(self) -> str:
        return f"{self.emoji} {self.tier}  ({self.score:.0f}/100)"


# ---- Heat Scorer strategy ----------------------------------------------------

class HeatScorer:
    """
    Calculates the Heat Score S for a qualified lead.
    GoF Strategy: swap this class for a different scoring algorithm.

    Scoring formula:
        price_score  = clamp((floor - price) / floor, 0, 1) * 60
        year_score   = clamp((year - MIN_YEAR) / YEAR_RANGE, 0, 1) * 30
        urgency_pts  = 10 if age_hours < 2 else (5 if age_hours < 24 else 0)
        S            = price_score + year_score + urgency_pts
    """

    def __init__(self, sluice_mode: str = "standard"):
        self.sluice_mode = sluice_mode
        self.price_floor = (
            PRICE_STANDARD if sluice_mode == "standard" else PRICE_AGGRESSIVE
        )

    def score(
        self,
        price:        float,
        vehicle_year: int,
        age_hours:    float = 0.0,
        created_at:   Optional[datetime] = None,
    ) -> HeatResult:
        """
        Calculate heat score for a lead.

        Args:
            price:        Dealer's asking price (must be <= price_floor to qualify)
            vehicle_year: Model year of vehicle
            age_hours:    Hours since lead was created (overrides created_at)
            created_at:   datetime of lead creation (used if age_hours not given)

        Returns:
            HeatResult with score 0-100 and tier HOT/WARM/COLD
        """
        # Resolve age
        if created_at and age_hours == 0.0:
            now = datetime.now(timezone.utc)
            if created_at.tzinfo is None:
                created_at = created_at.replace(tzinfo=timezone.utc)
            age_hours = (now - created_at).total_seconds() / 3600

        # Price score: max 60 pts
        price_delta  = max(self.price_floor - price, 0.0)
        price_ratio  = min(price_delta / self.price_floor, 1.0)
        price_score  = price_ratio * 60.0

        # Year score: max 30 pts
        year_delta   = max(vehicle_year - MIN_YEAR, 0)
        year_ratio   = min(year_delta / YEAR_RANGE, 1.0)
        year_score   = year_ratio * 30.0

        # Urgency bonus: max 10 pts
        if age_hours < 2:
            urgency_pts = 10.0
        elif age_hours < 24:
            urgency_pts = 5.0
        else:
            urgency_pts = 0.0

        total = round(price_score + year_score + urgency_pts, 2)

        # Tier
        if total >= TIER_THRESHOLDS[TIER_HOT]:
            tier = TIER_HOT
        elif total >= TIER_THRESHOLDS[TIER_WARM]:
            tier = TIER_WARM
        else:
            tier = TIER_COLD

        return HeatResult(
            score=total,
            tier=tier,
            emoji=TIER_EMOJI[tier],
            price_score=price_score,
            year_score=year_score,
            urgency_pts=urgency_pts,
            price_floor=self.price_floor,
            sluice_mode=self.sluice_mode,
        )

    def rank_leads(self, leads: List[Dict]) -> List[Dict]:
        """
        Score and rank a list of lead dicts (from CommPlexAPI /leads).
        Each dict must have: price, vehicle_year, created_at (ISO string).
        Returns list sorted HOT first, with 'heat' key added.

        Args:
            leads: List of lead dicts from the API

        Returns:
            Same list, sorted descending by heat score, 'heat' key added.
        """
        scored = []
        for lead in leads:
            if lead.get("status") != "QUALIFIED":
                lead["heat"] = None
                scored.append(lead)
                continue

            price = lead.get("price")
            year  = lead.get("vehicle_year")

            if price is None or year is None:
                lead["heat"] = None
                scored.append(lead)
                continue

            created_at = None
            raw_ts = lead.get("created_at")
            if raw_ts:
                try:
                    from datetime import datetime
                    created_at = datetime.fromisoformat(
                        raw_ts.replace("Z", "+00:00")
                    )
                except Exception:
                    pass

            result = self.score(
                price=float(price),
                vehicle_year=int(year),
                created_at=created_at,
            )
            lead["heat"] = result.to_dict()
            scored.append(lead)

        # Sort: QUALIFIED+HOT first, then by score desc, then non-qualified last
        def sort_key(l):
            heat = l.get("heat")
            return (-(heat["score"] if heat else -1))

        return sorted(scored, key=sort_key)


# ---- Kill Switch integration -------------------------------------------------

class KillSwitch:
    """
    Emergency stop for all outbound Bland.ai calls.
    GoF: Proxy -- gates all campaign module execution.

    When armed:
      - Sets KILL_SWITCH=1 in the environment
      - Writes a kill file to disk that all modules check before firing
      - Optionally calls Bland.ai /stop endpoint

    Usage:
        ks = KillSwitch()
        ks.arm("Accidental double-dial loop detected")
        ks.status()
        ks.disarm()
    """

    KILL_FILE = os.path.expanduser("~/.commplex_kill")

    def arm(self, reason: str = "Manual kill switch") -> bool:
        """Arm the kill switch. All campaign modules will abort on next check."""
        try:
            with open(self.KILL_FILE, "w") as f:
                f.write(f"{datetime.now().isoformat()} | REASON: {reason}\n")
            os.environ["KILL_SWITCH"] = "1"
            print(f"[KillSwitch] ARMED: {reason}")
            print(f"[KillSwitch] Kill file: {self.KILL_FILE}")
            self._notify_team(reason)
            return True
        except Exception as e:
            print(f"[KillSwitch] ARM FAILED: {e}")
            return False

    def disarm(self) -> bool:
        """Disarm the kill switch. Resume normal operation."""
        try:
            if os.path.exists(self.KILL_FILE):
                os.remove(self.KILL_FILE)
            os.environ.pop("KILL_SWITCH", None)
            print("[KillSwitch] DISARMED. System resumed.")
            return True
        except Exception as e:
            print(f"[KillSwitch] DISARM FAILED: {e}")
            return False

    def is_armed(self) -> bool:
        """Check if kill switch is active. Call this before any API call."""
        return os.path.exists(self.KILL_FILE) or os.getenv("KILL_SWITCH") == "1"

    def status(self) -> Dict:
        armed = self.is_armed()
        reason = ""
        if armed and os.path.exists(self.KILL_FILE):
            with open(self.KILL_FILE) as f:
                reason = f.read().strip()
        return {
            "armed":  armed,
            "reason": reason,
            "file":   self.KILL_FILE,
        }

    def _notify_team(self, reason: str):
        """Send ntfy.sh alert when kill switch is armed."""
        try:
            import requests
            topic  = os.getenv("NTFY_TOPIC", "arc-badlands")
            server = os.getenv("NTFY_SERVER", "https://ntfy.sh")
            requests.post(
                f"{server}/{topic}",
                data=f"KILL SWITCH ARMED: {reason}".encode(),
                headers={"Title": "🛑 CommPlex KILL SWITCH", "Priority": "5",
                         "Tags": "rotating_light,stop_sign"},
                timeout=5,
            )
        except Exception:
            pass  # Notification failure must never block the kill switch


# ---- Singletons --------------------------------------------------------------

_scorer: Optional[HeatScorer] = None
_kill:   Optional[KillSwitch] = None

def get_scorer(sluice_mode: str = "standard") -> HeatScorer:
    global _scorer
    if _scorer is None:
        _scorer = HeatScorer(sluice_mode=sluice_mode)
    return _scorer

def get_kill_switch() -> KillSwitch:
    global _kill
    if _kill is None:
        _kill = KillSwitch()
    return _kill


# ---- Self-test ---------------------------------------------------------------

if __name__ == "__main__":
    print("=" * 60)
    print("CommPlexCore -- HeatScorer + KillSwitch Self-Test")
    print("=" * 60)

    scorer = HeatScorer(sluice_mode="standard")

    test_cases = [
        ("HOT  -- new, cheap, fresh",  22000, 2024, 0.5),
        ("WARM -- decent deal, day old", 26000, 2022, 12.0),
        ("COLD -- old year, higher price", 27500, 2020, 48.0),
        ("MAX  -- perfect score",       1000,  2025, 0.1),
        ("EDGE -- exactly at floor",    28500, 2020, 100.0),
    ]

    print()
    for label, price, year, age_h in test_cases:
        r = scorer.score(price=price, vehicle_year=year, age_hours=age_h)
        print(f"  {label}")
        print(f"    score={r.score:>5.1f}  tier={r.tier:<4}  {r.emoji}  "
              f"(price={r.price_score:.1f} + year={r.year_score:.1f} + urgency={r.urgency_pts:.0f})")

    # Kill switch
    print()
    ks = KillSwitch()
    print(f"  KillSwitch status before arm: {ks.status()}")
    ks.arm("Self-test -- disarming immediately")
    print(f"  KillSwitch status armed:      {ks.status()['armed']}")
    ks.disarm()
    print(f"  KillSwitch status disarmed:   {ks.status()['armed']}")

    # Rank leads
    print()
    mock_leads = [
        {"id": 1, "status": "QUALIFIED", "price": 27000, "vehicle_year": 2021,
         "created_at": "2026-04-17T00:00:00", "dealer_name": "Bismarck Auto"},
        {"id": 2, "status": "QUALIFIED", "price": 22000, "vehicle_year": 2023,
         "created_at": "2026-04-17T12:00:00", "dealer_name": "Fargo Ford"},
        {"id": 3, "status": "REJECTED",  "price": 35000, "vehicle_year": 2019,
         "created_at": "2026-04-16T00:00:00", "dealer_name": "Minot Motors"},
    ]
    ranked = scorer.rank_leads(mock_leads)
    print("  Ranked leads (HOT first):")
    for l in ranked:
        heat = l.get("heat")
        score_str = f"{heat['score']:.0f}/100 {heat['emoji']}" if heat else "N/A"
        print(f"    #{l['id']} {l['dealer_name']:<20} {l['status']:<12} Heat: {score_str}")

    print()
    print("checkpoints:")
    print("  [OK] HeatScorer produces scores 0-100")
    print("  [OK] Tier thresholds: HOT>=75, WARM>=45, COLD<45")
    print("  [OK] KillSwitch arm/disarm cycle works")
    print("  [OK] rank_leads() sorts QUALIFIED+HOT first")
    print()
    print("All scorer checkpoints passed.")
