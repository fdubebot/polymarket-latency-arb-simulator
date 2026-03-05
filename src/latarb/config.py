from __future__ import annotations

import json
import os
from dataclasses import asdict, dataclass, fields
from pathlib import Path
from typing import Any, get_type_hints


class ConfigError(ValueError):
    """Raised when configuration cannot be loaded/validated."""


@dataclass(slots=True)
class SimulationConfig:
    steps: int = 1200
    latency_ms: int = 120
    fee_bps: float = 5.0
    seed: int = 7


@dataclass(slots=True)
class RiskConfig:
    max_abs_inventory: float = 180.0
    drawdown_limit: float = 18.0
    risk_budget: float = 250.0
    liquidation_fraction: float = 0.35


@dataclass(slots=True)
class OutputConfig:
    output_dir: str = "artifacts"
    run_name: str = "latest"
    write_csv: bool = True


@dataclass(slots=True)
class AppConfig:
    simulation: SimulationConfig
    risk: RiskConfig
    output: OutputConfig


def default_config() -> AppConfig:
    return AppConfig(simulation=SimulationConfig(), risk=RiskConfig(), output=OutputConfig())


def _coerce_value(value: str, target: type[Any]) -> Any:
    if target is bool:
        return value.lower() in {"1", "true", "yes", "on"}
    if target is int:
        return int(value)
    if target is float:
        return float(value)
    return value


def _update_dataclass(instance: Any, values: dict[str, Any]) -> Any:
    field_map = {f.name: f.type for f in fields(instance)}
    hints = get_type_hints(type(instance))
    for key, value in values.items():
        if key not in field_map:
            continue
        target_type = hints.get(key, field_map[key])
        if isinstance(value, str):
            setattr(instance, key, _coerce_value(value, target_type))
        else:
            setattr(instance, key, value)
    return instance


def _load_config_file(path: str | None) -> dict[str, Any]:
    if not path:
        return {}
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"Config file not found: {path}")
    try:
        return json.loads(p.read_text())
    except json.JSONDecodeError as exc:
        raise ConfigError(f"Invalid JSON in config file {path}: {exc}") from exc


def _apply_env(cfg: AppConfig) -> AppConfig:
    sim_updates: dict[str, str] = {}
    risk_updates: dict[str, str] = {}
    out_updates: dict[str, str] = {}

    for key, value in os.environ.items():
        if not key.startswith("LATARB_"):
            continue
        raw = key[len("LATARB_") :].lower()
        if raw.startswith("sim_"):
            sim_updates[raw[4:]] = value
        elif raw.startswith("risk_"):
            risk_updates[raw[5:]] = value
        elif raw.startswith("out_"):
            out_updates[raw[4:]] = value

    _update_dataclass(cfg.simulation, sim_updates)
    _update_dataclass(cfg.risk, risk_updates)
    _update_dataclass(cfg.output, out_updates)
    return cfg


def load_app_config(config_path: str | None = None, overrides: dict[str, Any] | None = None) -> AppConfig:
    cfg = default_config()
    file_cfg = _load_config_file(config_path)

    _update_dataclass(cfg.simulation, file_cfg.get("simulation", {}))
    _update_dataclass(cfg.risk, file_cfg.get("risk", {}))
    _update_dataclass(cfg.output, file_cfg.get("output", {}))

    cfg = _apply_env(cfg)

    if overrides:
        _update_dataclass(cfg.simulation, overrides.get("simulation", {}))
        _update_dataclass(cfg.risk, overrides.get("risk", {}))
        _update_dataclass(cfg.output, overrides.get("output", {}))

    validate_config(cfg)
    return cfg


def validate_config(cfg: AppConfig) -> None:
    if cfg.simulation.steps <= 0:
        raise ConfigError("simulation.steps must be > 0")
    if cfg.simulation.latency_ms < 0:
        raise ConfigError("simulation.latency_ms must be >= 0")
    if cfg.risk.max_abs_inventory <= 0:
        raise ConfigError("risk.max_abs_inventory must be > 0")
    if cfg.risk.drawdown_limit <= 0:
        raise ConfigError("risk.drawdown_limit must be > 0")
    if cfg.risk.risk_budget <= 0:
        raise ConfigError("risk.risk_budget must be > 0")
    if not (0.0 < cfg.risk.liquidation_fraction <= 1.0):
        raise ConfigError("risk.liquidation_fraction must be in (0, 1]")


def config_to_dict(cfg: AppConfig) -> dict[str, Any]:
    return asdict(cfg)
