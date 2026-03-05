from __future__ import annotations

import math
import random

from .models import Tick


def clamp(v: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, v))


class SyntheticPolymarket:
    """Generate synthetic market and signal streams with microstructure noise."""

    def __init__(self, seed: int = 7) -> None:
        self.rng = random.Random(seed)

    def generate(self, steps: int) -> list[Tick]:
        fair = 0.5
        out: list[Tick] = []
        for t in range(steps):
            regime = 1.0 if (t // 200) % 2 == 0 else -1.0
            drift = regime * 0.0015
            shock = self.rng.gauss(0.0, 0.01)
            fair = clamp(fair + drift + shock, 0.02, 0.98)

            # "networked alpha" as an upstream crypto signal with lagged relevance
            signal_noise = self.rng.gauss(0.0, 0.05)
            signal = clamp((fair - 0.5) * 2.0 + signal_noise, -1.0, 1.0)

            micro_noise = self.rng.gauss(0.0, 0.015) + 0.01 * math.sin(t / 15)
            observed = clamp(fair + micro_noise, 0.01, 0.99)
            out.append(Tick(t=t, signal=signal, fair_prob=fair, observed_prob=observed))
        return out
