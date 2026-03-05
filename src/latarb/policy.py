from __future__ import annotations

from dataclasses import dataclass

from .models import Action


@dataclass
class ArmState:
    a00: float = 1.0
    a01: float = 0.0
    a11: float = 1.0
    b0: float = 0.0
    b1: float = 0.0


class LinUCBPolicy:
    """Tiny contextual bandit to pick aggressiveness under uncertainty."""

    def __init__(self, actions: list[Action], alpha: float = 0.4) -> None:
        self.actions = actions
        self.alpha = alpha
        self.state = {a.name: ArmState() for a in actions}

    @staticmethod
    def _inv(a: ArmState) -> tuple[float, float, float]:
        det = a.a00 * a.a11 - a.a01 * a.a01
        return (a.a11 / det, -a.a01 / det, a.a00 / det)

    def choose(self, signal: float, volatility: float) -> Action:
        x0, x1 = signal, volatility
        best_score = float("-inf")
        best = self.actions[0]
        for action in self.actions:
            s = self.state[action.name]
            i00, i01, i11 = self._inv(s)
            theta0 = i00 * s.b0 + i01 * s.b1
            theta1 = i01 * s.b0 + i11 * s.b1
            mean = theta0 * x0 + theta1 * x1
            conf_sq = x0 * (i00 * x0 + i01 * x1) + x1 * (i01 * x0 + i11 * x1)
            score = mean + self.alpha * (conf_sq ** 0.5)
            if score > best_score:
                best_score = score
                best = action
        return best

    def update(self, action_name: str, signal: float, volatility: float, reward: float) -> None:
        s = self.state[action_name]
        x0, x1 = signal, volatility
        s.a00 += x0 * x0
        s.a01 += x0 * x1
        s.a11 += x1 * x1
        s.b0 += reward * x0
        s.b1 += reward * x1
