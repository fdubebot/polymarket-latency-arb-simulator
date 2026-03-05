from __future__ import annotations

import csv
import json
from pathlib import Path

from .config import AppConfig, config_to_dict


def write_artifacts(result: dict, cfg: AppConfig) -> dict[str, str]:
    outdir = Path(cfg.output.output_dir) / cfg.output.run_name
    outdir.mkdir(parents=True, exist_ok=True)

    summary = {
        k: v
        for k, v in result.items()
        if k not in {"fills_full", "equity_curve"}
    }
    summary["config"] = config_to_dict(cfg)

    summary_path = outdir / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2))

    paths = {"summary_json": str(summary_path)}

    if cfg.output.write_csv:
        fills_path = outdir / "fills.csv"
        with fills_path.open("w", newline="") as f:
            writer = csv.DictWriter(
                f,
                fieldnames=["t", "action", "side", "price", "size", "edge", "reason"],
            )
            writer.writeheader()
            for row in result["fills_full"]:
                writer.writerow(row)

        equity_path = outdir / "equity_curve.csv"
        with equity_path.open("w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=["t", "equity", "inventory"])
            writer.writeheader()
            for row in result["equity_curve"]:
                writer.writerow(row)

        paths["fills_csv"] = str(fills_path)
        paths["equity_curve_csv"] = str(equity_path)

    return paths
