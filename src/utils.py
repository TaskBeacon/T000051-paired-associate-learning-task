from __future__ import annotations

import random
from typing import Any, Iterable


STUDY_RELATION_ORDER = ("related", "unrelated")
STUDY_KEY_MAP = {
    "related": "r",
    "unrelated": "u",
}
TEST_KEY_ORDER = ("1", "2", "3", "4")
TEST_OPTION_POSITIONS = ("top_left", "top_right", "bottom_left", "bottom_right")

RELATED_PAIR_BANK: list[tuple[str, str]] = [
    ("doctor", "nurse"),
    ("sun", "moon"),
    ("bread", "butter"),
    ("ship", "anchor"),
    ("pencil", "paper"),
    ("king", "queen"),
    ("rain", "umbrella"),
    ("cat", "kitten"),
    ("train", "track"),
    ("picture", "frame"),
    ("guitar", "music"),
    ("forest", "tree"),
    ("coffee", "cup"),
    ("river", "bridge"),
    ("candle", "flame"),
]

UNRELATED_PAIR_BANK: list[tuple[str, str]] = [
    ("cloud", "hammer"),
    ("apple", "ladder"),
    ("mirror", "rabbit"),
    ("window", "spoon"),
    ("towel", "bicycle"),
    ("orange", "pillow"),
    ("bucket", "violin"),
    ("suitcase", "tomato"),
    ("chalk", "engine"),
    ("blanket", "oyster"),
    ("shadow", "pebble"),
    ("rocket", "compass"),
    ("shirt", "lemon"),
    ("feather", "marble"),
    ("lantern", "gallon"),
]


def _trial_rng(seed: int, block_idx: int, salt: int = 0) -> random.Random:
    mixed = (int(seed) * 1_000_003) + ((int(block_idx) + 1) * 1_009) + (int(salt) * 97)
    return random.Random(mixed % (2**32))


def _coerce_int(value: Any, default: int) -> int:
    try:
        return int(value)
    except Exception:
        return int(default)


def _coerce_positive_int(value: Any, default: int) -> int:
    result = max(1, _coerce_int(value, default))
    return result


def _coerce_sequence(value: Any, default: Iterable[Any]) -> list[Any]:
    if isinstance(value, (list, tuple)):
        items = list(value)
        if items:
            return items
    return list(default)


def _select_block_slice(
    bank: list[tuple[str, str]],
    *,
    block_idx: int,
    pairs_per_block: int,
) -> list[tuple[str, str]]:
    start = block_idx * pairs_per_block
    end = start + pairs_per_block
    if end > len(bank):
        raise ValueError(
            f"Not enough pair-bank entries for block {block_idx}: "
            f"need {end}, have {len(bank)}"
        )
    return list(bank[start:end])


def _shuffle_no_long_runs(items: list[dict[str, Any]], *, key_name: str, rng: random.Random, max_run: int = 2) -> list[dict[str, Any]]:
    if len(items) <= 1:
        return list(items)

    candidate = list(items)

    def ok(seq: list[dict[str, Any]]) -> bool:
        run = 1
        for idx in range(1, len(seq)):
            if seq[idx][key_name] == seq[idx - 1][key_name]:
                run += 1
                if run > max_run:
                    return False
            else:
                run = 1
        return True

    for _ in range(512):
        rng.shuffle(candidate)
        if ok(candidate):
            return list(candidate)
    return list(candidate)


def _pair_spec(
    *,
    pair_id: str,
    cue_word: str,
    associate_word: str,
    relation: str,
    practice: bool,
    block_kind: str,
    block_idx: int,
    pair_index: int,
) -> dict[str, Any]:
    return {
        "pair_id": pair_id,
        "cue_word": cue_word,
        "associate_word": associate_word,
        "pair_relation": relation,
        "study_correct_key": STUDY_KEY_MAP[relation],
        "practice": bool(practice),
        "block_kind": block_kind,
        "block_idx": int(block_idx),
        "pair_index": int(pair_index),
    }


def _build_pair_bank() -> list[dict[str, Any]]:
    pairs: list[dict[str, Any]] = []
    for idx, (cue_word, associate_word) in enumerate(RELATED_PAIR_BANK, start=1):
        pairs.append(
            _pair_spec(
                pair_id=f"related_{idx:02d}",
                cue_word=cue_word,
                associate_word=associate_word,
                relation="related",
                practice=False,
                block_kind="bank",
                block_idx=0,
                pair_index=idx,
            )
        )
    for idx, (cue_word, associate_word) in enumerate(UNRELATED_PAIR_BANK, start=1):
        pairs.append(
            _pair_spec(
                pair_id=f"unrelated_{idx:02d}",
                cue_word=cue_word,
                associate_word=associate_word,
                relation="unrelated",
                practice=False,
                block_kind="bank",
                block_idx=0,
                pair_index=idx,
            )
        )
    return pairs


def _build_block_pairs(
    *,
    block_kind: str,
    block_idx: int,
    pairs_per_block: int,
    seed: int,
) -> list[dict[str, Any]]:
    if pairs_per_block % 2 != 0:
        raise ValueError("pairs_per_block must be even so related/unrelated pairs can be balanced.")

    half = pairs_per_block // 2
    # Use disjoint word-pair slices across the three blocks so practice does not
    # reuse the same material as the scored lists.
    block_slice_idx = block_idx

    related_slice = _select_block_slice(RELATED_PAIR_BANK, block_idx=block_slice_idx, pairs_per_block=half)
    unrelated_slice = _select_block_slice(UNRELATED_PAIR_BANK, block_idx=block_slice_idx, pairs_per_block=half)

    pair_specs: list[dict[str, Any]] = []
    for idx, (cue_word, associate_word) in enumerate(related_slice, start=1):
        pair_specs.append(
            _pair_spec(
                pair_id=f"{block_kind}_{block_idx}_related_{idx:02d}",
                cue_word=cue_word,
                associate_word=associate_word,
                relation="related",
                practice=block_kind == "practice",
                block_kind=block_kind,
                block_idx=block_idx,
                pair_index=idx,
            )
        )
    for idx, (cue_word, associate_word) in enumerate(unrelated_slice, start=1):
        pair_specs.append(
            _pair_spec(
                pair_id=f"{block_kind}_{block_idx}_unrelated_{idx:02d}",
                cue_word=cue_word,
                associate_word=associate_word,
                relation="unrelated",
                practice=block_kind == "practice",
                block_kind=block_kind,
                block_idx=block_idx,
                pair_index=half + idx,
            )
        )

    rng = _trial_rng(seed, block_idx, salt=21 if block_kind == "practice" else 31)
    return _shuffle_no_long_runs(pair_specs, key_name="pair_relation", rng=rng, max_run=2)


def _build_test_options(
    *,
    block_pairs: list[dict[str, Any]],
    pair_spec: dict[str, Any],
    seed: int,
    block_idx: int,
    pair_index: int,
) -> list[str]:
    correct = str(pair_spec["associate_word"])
    lures = [str(spec["associate_word"]) for spec in block_pairs if spec["associate_word"] != correct]
    rng = _trial_rng(seed, block_idx, salt=91 + pair_index)
    rng.shuffle(lures)
    chosen = [correct] + lures[:3]
    rng.shuffle(chosen)
    return chosen


def _build_trial_specs_for_block(
    *,
    block_kind: str,
    block_idx: int,
    pairs_per_block: int,
    seed: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    block_pairs = _build_block_pairs(
        block_kind=block_kind,
        block_idx=block_idx,
        pairs_per_block=pairs_per_block,
        seed=seed,
    )

    study_trials: list[dict[str, Any]] = []
    test_trials: list[dict[str, Any]] = []

    for pair_index, pair_spec in enumerate(block_pairs, start=1):
        study_trials.append(
            {
                **pair_spec,
                "trial_phase": "study",
                "trial_index_in_block": pair_index,
                "stimulus_summary": "cue-associate pair",
                "correct_key": pair_spec["study_correct_key"],
            }
        )

    for pair_index, pair_spec in enumerate(block_pairs, start=1):
        options = _build_test_options(
            block_pairs=block_pairs,
            pair_spec=pair_spec,
            seed=seed,
            block_idx=block_idx,
            pair_index=pair_index,
        )
        correct_word = str(pair_spec["associate_word"])
        correct_position = options.index(correct_word) + 1
        test_trials.append(
            {
                **pair_spec,
                "trial_phase": "test",
                "trial_index_in_block": pairs_per_block + pair_index,
                "stimulus_summary": "cue-plus-four-option-recognition",
                "test_options": options,
                "correct_key": str(correct_position),
            }
        )

    return study_trials, test_trials


def build_session_plan(settings: Any) -> list[dict[str, Any]]:
    """Return the ordered practice + scored block schedule for runtime use."""
    seed = _coerce_int(getattr(settings, "overall_seed", 2026), 2026)
    pairs_per_block = _coerce_positive_int(getattr(settings, "pairs_per_block", 10), 10)
    practice_pairs = _coerce_positive_int(getattr(settings, "practice_pairs", pairs_per_block), pairs_per_block)
    scored_pairs_per_block = _coerce_positive_int(
        getattr(settings, "scored_pairs_per_block", pairs_per_block),
        pairs_per_block,
    )

    block_plan: list[dict[str, Any]] = []

    for block_kind, block_idx, pair_count in (
        ("practice", 0, practice_pairs),
        ("scored", 1, scored_pairs_per_block),
        ("scored", 2, scored_pairs_per_block),
    ):
        study_trials, test_trials = _build_trial_specs_for_block(
            block_kind=block_kind,
            block_idx=block_idx,
            pairs_per_block=pair_count,
            seed=seed,
        )
        block_plan.append(
            {
                "block_kind": block_kind,
                "block_id": "practice" if block_idx == 0 else f"block_{block_idx}",
                "block_idx": block_idx,
                "pair_count": pair_count,
                "study_trials": study_trials,
                "test_trials": test_trials,
                "trials": study_trials + test_trials,
                "block_label": "Practice List" if block_idx == 0 else f"Scored List {block_idx}",
                "show_feedback": block_kind == "practice",
            }
        )

    return block_plan


def summarize_trials(trials: list[dict[str, Any]]) -> dict[str, float | int]:
    study_trials = [trial for trial in trials if str(trial.get("trial_phase", "")) == "study"]
    test_trials = [trial for trial in trials if str(trial.get("trial_phase", "")) == "test"]

    def _summarize(items: list[dict[str, Any]]) -> tuple[int, int, float, float]:
        responded = [t for t in items if bool(t.get("responded"))]
        correct = [t for t in items if bool(t.get("response_correct"))]
        rts = [
            float(t["response_rt"])
            for t in items
            if bool(t.get("response_correct")) and isinstance(t.get("response_rt"), (int, float))
        ]
        accuracy = (len(correct) / len(items)) if items else 0.0
        mean_rt_ms = (sum(rts) / len(rts) * 1000.0) if rts else 0.0
        return len(responded), len(correct), accuracy, mean_rt_ms

    study_responded, study_correct, study_accuracy, study_mean_rt_ms = _summarize(study_trials)
    test_responded, test_correct, test_accuracy, test_mean_rt_ms = _summarize(test_trials)

    return {
        "n_trials": len(trials),
        "study_n": len(study_trials),
        "test_n": len(test_trials),
        "study_n_responded": study_responded,
        "test_n_responded": test_responded,
        "study_n_correct": study_correct,
        "test_n_correct": test_correct,
        "study_accuracy": study_accuracy,
        "test_accuracy": test_accuracy,
        "study_mean_correct_rt_ms": study_mean_rt_ms,
        "test_mean_correct_rt_ms": test_mean_rt_ms,
        "accuracy": test_accuracy,
        "mean_correct_rt_ms": test_mean_rt_ms,
        "timeout_count": sum(1 for t in trials if bool(t.get("timed_out"))),
    }
