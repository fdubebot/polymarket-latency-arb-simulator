from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import pstdev

from .market import SyntheticPolymarket
from .models import Action, Fill
from .policy import LinUCBPolicy


@dataclass(slots=True)
class SimulationConfig:
    steps: int = 1200
    latency_ms: int = 120
    fee_bps: float = 5.0
    seed: int = 7


def _mark_to_market(inventory: float, fair: float) -> float:
    # inventory is YES shares, payoff tracks fair probability
    return inventory * fair


def run_simulation(config: SimulationConfig) -> dict:
    market = SyntheticPolymarket(seed=config.seed)
    ticks = market.generate(config.steps)
    actions = [
        Action("passive", edge_threshold=0.025, size=4.0),
        Action("balanced", edge_threshold=0.015, size=8.0),
        Action("aggressive", edge_threshold=0.008, size=14.0),
    ]
    policy = LinUCBPolicy(actions)

    cash = 0.0
    inventory = 0.0
    fills: list[Fill] = []
    mtm_series: list[float] = []

    lag = max(1, config.latency_ms // 20)
    for i in range(lag, len(ticks)):
        delayed = ticks[i - lag]
        now = ticks[i]
        vol = pstdev([t.observed_prob for t in ticks[max(0, i - 25): i + 1]]) if i > 3 else 0.01
        act = policy.choose(delayed.signal, vol)

        edge = delayed.signal * 0.03 + (now.fair_prob - now.observed_prob)
        traded = False
        reward = 0.0

        if abs(edge) > act.edge_threshold:
            side = "buy_yes" if edge > 0 else "sell_yes"
            price = now.observed_prob
            size = act.size
            fee = (config.fee_bps / 10000.0) * size
            if side == "buy_yes":
                inventory += size
                cash -= price * size
                cash -= fee
            else:
                inventory -= size
                cash += price * size
                cash -= fee
            reward = (abs(edge) - act.edge_threshold) * size - fee
            traded = True
            fills.append(
                Fill(
                    t=now.t,
                    action=act.name,
                    side=side,
                    price=price,
                    size=size,
                    edge=edge,
                )
            )

        # Penalize inventory build-up to mimic hedge pressure on crypto venues
        reward -= abs(inventory) * 0.0003
        policy.update(act.name, delayed.signal, vol, reward)

        mtm = cash + _mark_to_market(inventory, now.fair_prob)
        mtm_series.append(mtm)

        if not traded:
            continue

    pnl = mtm_series[-1] if mtm_series else 0.0
    return {
        "steps": config.steps,
        "latency_ms": config.latency_ms,
        "fills": len(fills),
        "final_inventory": round(inventory, 3),
        "final_pnl": round(pnl, 4),
        "actions_used": sorted({f.action for f in fills}),
        "sample_fills": [asdict(f) for f in fills[:5]],
    }
