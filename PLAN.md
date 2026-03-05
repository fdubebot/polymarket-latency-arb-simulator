# PLAN

## Project
**Polymarket Latency Arb Simulator** — a Python research harness that simulates latency-sensitive execution in prediction markets and uses a contextual-bandit policy to adapt execution aggressiveness.

## Why this is valuable
- Models realistic pain points in event-contract trading: stale signals, market microstructure noise, and inventory pressure.
- Gives a reusable baseline for future work (real Polymarket connectors, crypto hedge leg simulation, FPGA/offload experiments).
- Produces concrete metrics (PnL, fills, action mix) to compare strategy variants quickly.

## Scope for this run
1. Build modular simulation engine (market generator, policy, execution loop).
2. Add CLI for reproducible runs.
3. Add tests for deterministic behavior and policy learning updates.
4. Validate with pytest + one sample run.
5. Commit and push to a new GitHub repo.

## Near-term roadmap
- Add live adapters (Polymarket websocket + CLOB snapshots).
- Add explicit hedge-leg model for CEX perpetuals.
- Replace LinUCB with deep RL policy and compare regret.
- Add network-emulation profiles and packet-loss stress tests.
