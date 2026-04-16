from __future__ import annotations

import random as _py_random
from dataclasses import dataclass
from typing import Any

from psyflow.sim.contracts import Action, Feedback, Observation, SessionInfo


@dataclass
class TaskSamplerResponder:
    """Task-specific simulation responder for Paired-Associate Learning."""

    key: str | None = None
    study_hit_rate: float = 0.9
    test_hit_rate: float = 0.76
    study_timeout_rate: float = 0.05
    test_timeout_rate: float = 0.08
    study_rt_mean_s: float = 0.85
    test_rt_mean_s: float = 1.35
    rt_sd_s: float = 0.25
    rt_min_s: float = 0.18
    practice_bonus: float = 0.05
    related_bonus: float = 0.03
    unrelated_penalty: float = 0.02
    late_block_bonus: float = 0.03

    def __post_init__(self) -> None:
        self._rng: Any = None
        self.study_hit_rate = max(0.0, min(1.0, float(self.study_hit_rate)))
        self.test_hit_rate = max(0.0, min(1.0, float(self.test_hit_rate)))
        self.study_timeout_rate = max(0.0, min(1.0, float(self.study_timeout_rate)))
        self.test_timeout_rate = max(0.0, min(1.0, float(self.test_timeout_rate)))
        self.study_rt_mean_s = float(self.study_rt_mean_s)
        self.test_rt_mean_s = float(self.test_rt_mean_s)
        self.rt_sd_s = max(1e-6, float(self.rt_sd_s))
        self.rt_min_s = max(0.0, float(self.rt_min_s))
        self.practice_bonus = float(self.practice_bonus)
        self.related_bonus = float(self.related_bonus)
        self.unrelated_penalty = float(self.unrelated_penalty)
        self.late_block_bonus = float(self.late_block_bonus)

    def start_session(self, session: SessionInfo, rng: Any) -> None:
        self._rng = rng

    def on_feedback(self, fb: Feedback) -> None:
        return None

    def end_session(self) -> None:
        self._rng = None

    def _sample_normal(self, mean: float, sd: float) -> float:
        rng = self._rng
        if hasattr(rng, "normal"):
            return float(rng.normal(mean, sd))
        return float(rng.gauss(mean, sd))

    def _sample_random(self) -> float:
        rng = self._rng
        if hasattr(rng, "random"):
            return float(rng.random())
        return float(_py_random.random())

    def _pick_valid_key(self, valid_keys: list[str], correct_key: str | None) -> str | None:
        if correct_key and correct_key in valid_keys:
            return correct_key
        if self.key and self.key in valid_keys:
            return self.key
        return valid_keys[0] if valid_keys else None

    def _profile(self, obs: Observation) -> dict[str, Any]:
        task_factors = dict(getattr(obs, "task_factors", {}) or {})
        if not task_factors and isinstance(getattr(obs, "extras", None), dict):
            task_factors = dict(obs.extras.get("task_factors", {}) or {})

        stage = str(task_factors.get("stage", getattr(obs, "phase", ""))).strip().lower()
        practice = bool(task_factors.get("practice", False))
        pair_relation = str(task_factors.get("pair_relation", "")).strip().lower()
        block_idx = int(task_factors.get("block_idx", 0) or 0)

        if "study" in stage:
            hit_rate = self.study_hit_rate
            timeout_rate = self.study_timeout_rate
            rt_mean = self.study_rt_mean_s
        else:
            hit_rate = self.test_hit_rate
            timeout_rate = self.test_timeout_rate
            rt_mean = self.test_rt_mean_s

        if practice:
            hit_rate += self.practice_bonus
            timeout_rate = max(0.0, timeout_rate - 0.02)
            rt_mean = max(self.rt_min_s, rt_mean - 0.15)

        if pair_relation == "related":
            hit_rate += self.related_bonus
        elif pair_relation == "unrelated":
            hit_rate = max(0.0, hit_rate - self.unrelated_penalty)

        if block_idx >= 2 and "test" in stage:
            hit_rate += self.late_block_bonus

        return {
            "task_factors": task_factors,
            "stage": stage,
            "practice": practice,
            "pair_relation": pair_relation,
            "hit_rate": max(0.0, min(1.0, hit_rate)),
            "timeout_rate": max(0.0, min(1.0, timeout_rate)),
            "rt_mean_s": max(self.rt_min_s, rt_mean),
        }

    @staticmethod
    def _is_continue_phase(stage: str, phase: str) -> bool:
        label = f"{stage} {phase}".strip().lower()
        return any(
            token in label
            for token in (
                "instruction",
                "block_intro",
                "practice_break",
                "block_break",
                "good_bye",
                "continue",
            )
        )

    def act(self, obs: Observation) -> Action:
        valid_keys = [str(key) for key in list(obs.valid_keys or [])]
        if not valid_keys:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "no_valid_keys"})

        rng = self._rng
        if rng is None:
            return Action(key=None, rt_s=None, meta={"source": "task_sampler", "reason": "rng_missing"})

        profile = self._profile(obs)
        task_factors = profile["task_factors"]
        correct_key = task_factors.get("correct_key") or getattr(obs, "correct_key", None)
        correct_key = str(correct_key) if correct_key is not None else None

        if self._is_continue_phase(profile["stage"], str(getattr(obs, "phase", ""))):
            rt = max(self.rt_min_s, self._sample_normal(self.study_rt_mean_s, self.rt_sd_s))
            chosen_key = self._pick_valid_key(valid_keys, self.key)
            return Action(
                key=chosen_key,
                rt_s=rt,
                meta={
                    "source": "task_sampler",
                    "outcome": "continue",
                    "correct_key": correct_key,
                    "stage": profile["stage"],
                },
            )

        if self._sample_random() < profile["timeout_rate"]:
            return Action(
                key=None,
                rt_s=None,
                meta={
                    "source": "task_sampler",
                    "outcome": "timeout",
                    "correct_key": correct_key,
                    "stage": profile["stage"],
                },
            )

        rt = max(self.rt_min_s, self._sample_normal(profile["rt_mean_s"], self.rt_sd_s))

        if self._sample_random() > profile["hit_rate"]:
            wrong_keys = [key for key in valid_keys if key != correct_key]
            chosen_key = wrong_keys[0] if wrong_keys else self._pick_valid_key(valid_keys, correct_key)
            return Action(
                key=chosen_key,
                rt_s=rt,
                meta={
                    "source": "task_sampler",
                    "outcome": "miss",
                    "correct_key": correct_key,
                    "stage": profile["stage"],
                },
            )

        chosen_key = self._pick_valid_key(valid_keys, correct_key)
        return Action(
            key=chosen_key,
            rt_s=rt,
            meta={
                "source": "task_sampler",
                "outcome": "hit",
                "correct_key": correct_key,
                "stage": profile["stage"],
            },
        )
