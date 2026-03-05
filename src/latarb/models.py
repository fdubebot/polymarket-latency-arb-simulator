from __future__ import annotations

from dataclasses import dataclass


@dataclass(slots=True)
class Tick:
    t: int
    signal: float
    fair_prob: float
    observed_prob: float


@dataclass(slots=True)
class Action:
    name: str
    edge_threshold: float
    size: float


@dataclass(slots=True)
class Fill:
    t: int
    action: str
    side: str
    price: float
    size: float
    edge: float


@dataclass(slots=True)
class StepResult:
    pnl_delta: float
    inventory_delta: float
    fills: list[Fill]
