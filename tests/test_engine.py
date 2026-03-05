from latarb.engine import SimulationConfig, run_simulation


def test_simulation_is_deterministic_for_seed() -> None:
    cfg = SimulationConfig(steps=300, latency_ms=100, fee_bps=4.0, seed=11)
    a = run_simulation(cfg)
    b = run_simulation(cfg)
    assert a["final_pnl"] == b["final_pnl"]
    assert a["fills"] == b["fills"]


def test_simulation_trades_and_reports_fields() -> None:
    result = run_simulation(SimulationConfig(steps=400, latency_ms=140, fee_bps=5.0, seed=3))
    assert result["steps"] == 400
    assert result["latency_ms"] == 140
    assert result["fills"] > 0
    assert isinstance(result["actions_used"], list)
