from __future__ import annotations

import argparse
import json
import logging

from .config import ConfigError, config_to_dict, load_app_config
from .engine import SimulationError, run_simulation
from .reporting import write_artifacts


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="latarb-sim",
        description="Polymarket latency arbitrage simulator (research-grade)",
    )
    p.add_argument("--config", type=str, default=None, help="Path to JSON config file")
    p.add_argument("--log-level", type=str, default="INFO", help="DEBUG|INFO|WARNING|ERROR")

    sub = p.add_subparsers(dest="command", required=True)

    run_p = sub.add_parser("run", help="Run a simulation and write artifacts")
    run_p.add_argument("--steps", type=int)
    run_p.add_argument("--latency-ms", type=int)
    run_p.add_argument("--fee-bps", type=float)
    run_p.add_argument("--seed", type=int)
    run_p.add_argument("--max-abs-inventory", type=float)
    run_p.add_argument("--drawdown-limit", type=float)
    run_p.add_argument("--risk-budget", type=float)
    run_p.add_argument("--liquidation-fraction", type=float)
    run_p.add_argument("--output-dir", type=str)
    run_p.add_argument("--run-name", type=str)
    run_p.add_argument("--no-csv", action="store_true")

    sub.add_parser("show-config", help="Print the resolved config and exit")

    return p


def _overrides_from_args(args: argparse.Namespace) -> dict:
    sim = {}
    risk = {}
    out = {}

    for k in ["steps", "latency_ms", "fee_bps", "seed"]:
        val = getattr(args, k, None)
        if val is not None:
            sim[k] = val

    risk_map = {
        "max_abs_inventory": "max_abs_inventory",
        "drawdown_limit": "drawdown_limit",
        "risk_budget": "risk_budget",
        "liquidation_fraction": "liquidation_fraction",
    }
    for arg_key, cfg_key in risk_map.items():
        val = getattr(args, arg_key, None)
        if val is not None:
            risk[cfg_key] = val

    for k in ["output_dir", "run_name"]:
        val = getattr(args, k, None)
        if val is not None:
            out[k] = val
    if getattr(args, "no_csv", False):
        out["write_csv"] = False

    return {"simulation": sim, "risk": risk, "output": out}


def main() -> None:
    parser = _build_parser()
    args = parser.parse_args()

    logging.basicConfig(level=getattr(logging, args.log_level.upper(), logging.INFO))

    try:
        cfg = load_app_config(config_path=args.config, overrides=_overrides_from_args(args))
        if args.command == "show-config":
            print(json.dumps(config_to_dict(cfg), indent=2))
            return

        result = run_simulation(cfg)
        paths = write_artifacts(result, cfg)
        print(json.dumps({
            "result": {
                k: v for k, v in result.items() if k not in {"fills_full", "equity_curve"}
            },
            "artifacts": paths,
        }, indent=2))
    except (ConfigError, SimulationError, ValueError) as exc:
        logging.error("Simulation failed: %s", exc)
        raise SystemExit(2) from exc


if __name__ == "__main__":
    main()
