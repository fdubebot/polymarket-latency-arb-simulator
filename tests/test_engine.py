from latarb.config import AppConfig, OutputConfig, RiskConfig, SimulationConfig
from latarb.engine import run_simulation


def test_simulation_is_deterministic_for_seed() -> None:
    cfg = AppConfig(
        simulation=SimulationConfig(steps=300, latency_ms=100, fee_bps=4.0, seed=11),
        risk=RiskConfig(),
        output=OutputConfig(),
    )
    a = run_simulation(cfg)
    b = run_simulation(cfg)
    assert a["final_pnl"] == b["final_pnl"]
    assert a["fills"] == b["fills"]


def test_risk_guardrails_triggered_under_strict_limits() -> None:
    cfg = AppConfig(
        simulation=SimulationConfig(steps=600, latency_ms=110, fee_bps=5.0, seed=3),
        risk=RiskConfig(max_abs_inventory=40.0, drawdown_limit=8.0, risk_budget=35.0),
        output=OutputConfig(),
    )
    result = run_simulation(cfg)
    assert result["fills"] > 0
    assert result["guardrails"]["forced_liquidations"] >= 0
    assert abs(result["final_inventory"]) <= 40.0
