# polymarket-latency-arb-simulator

A substantial Python prototype for **AI-driven latency arbitrage research** across prediction-market style order flow.

## Included modules
- `market.py`: synthetic Polymarket-like stream with regime shifts and microstructure noise
- `policy.py`: lightweight contextual bandit (LinUCB) choosing execution aggressiveness
- `engine.py`: latency-aware execution loop with fees and inventory penalty
- `cli.py`: command-line entrypoint for experiments

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e . pytest
python -m latarb.cli --steps 1500 --latency-ms 140 --fee-bps 5
pytest
```

## Example output
```json
{
  "steps": 1200,
  "latency_ms": 120,
  "fills": 1004,
  "final_inventory": 196.0,
  "final_pnl": 8.4296,
  "actions_used": ["aggressive", "balanced", "passive"]
}
```

## Notes
This is a simulation framework (not live trading code). It is intended as a foundation for deeper modules: real data adapters, hedge leg modeling, and hardware/network acceleration experiments.
