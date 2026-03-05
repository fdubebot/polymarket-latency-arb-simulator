from __future__ import annotations

from dataclasses import asdict
from statistics import pstdev

from .config import AppConfig
from .market import SyntheticPolymarket
from .models import Action, EquityPoint, Fill
from .policy import LinUCBPolicy


class SimulationError(RuntimeError):
    """Raised for simulation runtime failures."""


def _mark_to_market(inventory: float, fair: float) -> float:
    return inventory * fair


def _liquidation_side(inventory: float) -> str:
    return "sell_yes" if inventory > 0 else "buy_yes"


def run_simulation(cfg: AppConfig) -> dict:
    sim = cfg.simulation
    risk = cfg.risk

    market = SyntheticPolymarket(seed=sim.seed)
    ticks = market.generate(sim.steps)
    if not ticks:
        raise SimulationError("Generated tick stream is empty")

    actions = [
        Action("passive", edge_threshold=0.025, size=4.0),
        Action("balanced", edge_threshold=0.015, size=8.0),
        Action("aggressive", edge_threshold=0.008, size=14.0),
    ]
    policy = LinUCBPolicy(actions)

    cash = 0.0
    inventory = 0.0
    fills: list[Fill] = []
    equity_curve: list[EquityPoint] = []

    max_equity = 0.0
    max_drawdown = 0.0
    risk_spent = 0.0
    guardrail_hits = {
        "inventory_cap_hits": 0,
        "drawdown_de_risk_events": 0,
        "risk_budget_de_risk_events": 0,
        "forced_liquidations": 0,
    }

    lag = max(1, sim.latency_ms // 20)
    for i in range(lag, len(ticks)):
        delayed = ticks[i - lag]
        now = ticks[i]
        vol = pstdev([t.observed_prob for t in ticks[max(0, i - 25) : i + 1]]) if i > 3 else 0.01
        act = policy.choose(delayed.signal, vol)

        edge = delayed.signal * 0.03 + (now.fair_prob - now.observed_prob)
        reward = 0.0

        # Decide normal trade candidate
        side = "buy_yes" if edge > 0 else "sell_yes"
        size = act.size
        reason = "signal_trade"

        abs_inventory = abs(inventory)
        remaining_budget = risk.risk_budget - risk_spent

        # De-risk mode if near drawdown limit or budget exhaustion
        in_drawdown_mode = max_drawdown >= 0.85 * risk.drawdown_limit
        in_budget_mode = remaining_budget <= 0.15 * risk.risk_budget

        if in_drawdown_mode or in_budget_mode:
            size = min(size, max(2.0, abs_inventory * risk.liquidation_fraction))
            if abs_inventory > 0:
                side = _liquidation_side(inventory)
                reason = "de_risk"
            if in_drawdown_mode:
                guardrail_hits["drawdown_de_risk_events"] += 1
            if in_budget_mode:
                guardrail_hits["risk_budget_de_risk_events"] += 1

        # Hard forced liquidation conditions
        force_liquidate = (
            abs_inventory > risk.max_abs_inventory
            or max_drawdown >= risk.drawdown_limit
            or remaining_budget <= 0
        )
        if force_liquidate and abs_inventory > 0:
            side = _liquidation_side(inventory)
            size = min(abs_inventory, max(2.0, abs_inventory * risk.liquidation_fraction))
            reason = "forced_liquidation"
            guardrail_hits["forced_liquidations"] += 1

        # Enforce inventory cap pre-trade for signal trades
        if reason == "signal_trade":
            projected = inventory + size if side == "buy_yes" else inventory - size
            if abs(projected) > risk.max_abs_inventory:
                guardrail_hits["inventory_cap_hits"] += 1
                side = _liquidation_side(inventory) if abs_inventory > 0 else side
                size = min(size, abs_inventory if abs_inventory > 0 else size)
                reason = "inventory_cap_block"

        should_trade = abs(edge) > act.edge_threshold or reason in {
            "de_risk",
            "forced_liquidation",
            "inventory_cap_block",
        }

        if should_trade and size > 0:
            price = now.observed_prob
            fee = (sim.fee_bps / 10000.0) * size
            if side == "buy_yes":
                inventory += size
                cash -= price * size
                cash -= fee
            else:
                inventory -= size
                cash += price * size
                cash -= fee

            reward = (abs(edge) - act.edge_threshold) * size - fee
            risk_spent += fee + (abs(inventory) * 0.001)
            fills.append(
                Fill(
                    t=now.t,
                    action=act.name,
                    side=side,
                    price=price,
                    size=size,
                    edge=edge,
                    reason=reason,
                )
            )

        reward -= abs(inventory) * 0.0003
        policy.update(act.name, delayed.signal, vol, reward)

        equity = cash + _mark_to_market(inventory, now.fair_prob)
        max_equity = max(max_equity, equity)
        drawdown = max_equity - equity
        max_drawdown = max(max_drawdown, drawdown)
        equity_curve.append(EquityPoint(t=now.t, equity=equity, inventory=inventory))

    pnl = equity_curve[-1].equity if equity_curve else 0.0
    return {
        "steps": sim.steps,
        "latency_ms": sim.latency_ms,
        "seed": sim.seed,
        "fills": len(fills),
        "final_inventory": round(inventory, 4),
        "final_pnl": round(pnl, 6),
        "max_drawdown": round(max_drawdown, 6),
        "risk_spent": round(risk_spent, 6),
        "actions_used": sorted({f.action for f in fills}),
        "guardrails": guardrail_hits,
        "sample_fills": [asdict(f) for f in fills[:10]],
        "equity_curve": [asdict(p) for p in equity_curve],
        "fills_full": [asdict(f) for f in fills],
    }
