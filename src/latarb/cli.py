from __future__ import annotations

import argparse
import json

from .engine import SimulationConfig, run_simulation


def main() -> None:
    p = argparse.ArgumentParser(description="Run polymarket latency arbitrage simulation")
    p.add_argument("--steps", type=int, default=1200)
    p.add_argument("--latency-ms", type=int, default=120)
    p.add_argument("--fee-bps", type=float, default=5.0)
    p.add_argument("--seed", type=int, default=7)
    args = p.parse_args()

    result = run_simulation(
        SimulationConfig(
            steps=args.steps,
            latency_ms=args.latency_ms,
            fee_bps=args.fee_bps,
            seed=args.seed,
        )
    )
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
