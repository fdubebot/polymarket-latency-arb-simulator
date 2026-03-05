# polymarket-latency-arb-simulator

Research-focused simulator for **latency-sensitive execution** on Polymarket-like binary markets, with production-like risk controls and reproducible experiment outputs.

## What this project is
This package simulates a signal-driven execution policy under latency, microstructure noise, fees, and inventory pressure. It is intended for strategy research and guardrail validation.

## What this project is not
- Not a live trading bot.
- Not connected to Polymarket APIs by default.
- Not investment advice.

## Features
- Latency-aware synthetic market stream with regime shifts
- Contextual-bandit action selection (LinUCB)
- Risk controls:
  - inventory caps
  - drawdown guardrails
  - risk-budget controls
  - forced liquidation / de-risk modes
- Deterministic reproducibility via explicit seed
- Config layering: **JSON config file + environment variables + CLI overrides**
- Artifact outputs:
  - `summary.json`
  - `fills.csv`
  - `equity_curve.csv`
- Logging and robust CLI error handling

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .[dev]

# show resolved config
latarb-sim show-config

# run with defaults
latarb-sim run

# run with overrides
latarb-sim run --steps 2000 --latency-ms 140 --seed 17 --run-name exp-17
```

## Configuration
### 1) JSON config file
```json
{
  "simulation": {"steps": 1500, "latency_ms": 120, "fee_bps": 5.0, "seed": 7},
  "risk": {
    "max_abs_inventory": 180.0,
    "drawdown_limit": 18.0,
    "risk_budget": 250.0,
    "liquidation_fraction": 0.35
  },
  "output": {"output_dir": "artifacts", "run_name": "baseline", "write_csv": true}
}
```

Use with:
```bash
latarb-sim --config config.json run
```

### 2) Environment variables
Prefix with `LATARB_`:
- `LATARB_SIM_STEPS=1800`
- `LATARB_RISK_MAX_ABS_INVENTORY=120`
- `LATARB_OUT_RUN_NAME=my-run`

### 3) CLI overrides (highest precedence)
```bash
latarb-sim --config config.json run --steps 2200 --run-name final
```

## Output artifacts
Runs are saved to `<output_dir>/<run_name>/`:
- `summary.json`: top-level metrics + resolved config
- `fills.csv`: all fills (reason-tagged)
- `equity_curve.csv`: stepwise equity + inventory

## Architecture
- `latarb.market` — synthetic market generator
- `latarb.policy` — LinUCB policy
- `latarb.engine` — core simulation + risk guardrails
- `latarb.config` — config loading/validation
- `latarb.reporting` — artifact writing
- `latarb.cli` — command-line UX

## Development
```bash
pip install -e .[dev]
pytest
ruff check .
mypy src
python -m build
```

## Limitations
- Market model is synthetic and simplified.
- No explicit cross-venue hedge leg model.
- No live exchange adapters.

## Roadmap
- Real Polymarket market-data adapters
- Explicit hedge-leg and slippage model
- Multi-market portfolio allocation and stress scenarios
- Rich dashboard/report generation
