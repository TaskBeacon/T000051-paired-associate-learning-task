from __future__ import annotations

from functools import partial
from typing import Any

from psyflow import StimUnit, next_trial_id, set_trial_context


def _duration(settings: Any, name: str, fallback: float) -> float:
    timing = dict(getattr(settings, "timing", {}) or {})
    value = timing.get(name, fallback)
    try:
        return float(value)
    except Exception:
        return float(fallback)


def _parse_response_key(response: Any) -> str:
    if response is None:
        return ""
    return str(response).strip().lower()


def _selected_test_word(options: list[str], response_key: str) -> str:
    try:
        idx = int(str(response_key)) - 1
    except Exception:
        return ""
    if idx < 0 or idx >= len(options):
        return ""
    return str(options[idx])


def _feedback_stim_name(*, phase_kind: str, practice: bool, timed_out: bool, response_correct: bool) -> str:
    prefix = "practice_" if practice else ""
    phase = "study" if phase_kind == "study" else "test"
    if timed_out:
        return f"{prefix}{phase}_feedback_timeout"
    if response_correct:
        return f"{prefix}{phase}_feedback_correct"
    return f"{prefix}{phase}_feedback_incorrect"


def run_trial(
    win,
    kb,
    settings,
    condition,
    stim_bank,
    trigger_runtime,
    block_id=None,
    block_idx=None,
):
    """Run one paired-associate learning trial."""
    trial_id = int(next_trial_id())
    trial_spec = condition if isinstance(condition, dict) else {}
    phase_kind = str(trial_spec.get("trial_phase", "study")).strip().lower()
    block_id_val = str(block_id) if block_id is not None else str(trial_spec.get("block_id", "block_0"))
    block_idx_val = int(block_idx) if block_idx is not None else int(trial_spec.get("block_idx", 0))
    practice = bool(trial_spec.get("practice", False))

    pair_id = str(trial_spec.get("pair_id", f"{block_id_val}_{trial_id}"))
    pair_relation = str(trial_spec.get("pair_relation", "related")).strip().lower()
    cue_word = str(trial_spec.get("cue_word", "")).strip()
    associate_word = str(trial_spec.get("associate_word", "")).strip()
    study_correct_key = str(trial_spec.get("study_correct_key", "r")).strip().lower()
    test_options = [str(item).strip() for item in list(trial_spec.get("test_options", [])) if str(item).strip()]
    correct_key = str(trial_spec.get("correct_key", study_correct_key)).strip().lower()

    fixation_duration = _duration(settings, "fixation_duration", 0.5)
    study_duration = _duration(settings, "study_duration", 1.5)
    study_iti_duration = _duration(settings, "study_iti_duration", 0.4)
    test_duration = _duration(settings, "test_duration", 6.0)
    test_iti_duration = _duration(settings, "test_iti_duration", 0.4)
    practice_feedback_duration = _duration(settings, "practice_feedback_duration", 0.8)

    study_keys = [str(key) for key in list(getattr(settings, "study_response_keys", ["r", "u"]))]
    if not study_keys:
        study_keys = ["r", "u"]
    test_keys = [str(key) for key in list(getattr(settings, "test_response_keys", ["1", "2", "3", "4"]))]
    if not test_keys:
        test_keys = ["1", "2", "3", "4"]

    make_unit = partial(StimUnit, win=win, kb=kb, runtime=trigger_runtime)

    trial_data: dict[str, Any] = {
        "trial_id": trial_id,
        "block_id": block_id_val,
        "block_idx": block_idx_val,
        "block_kind": str(trial_spec.get("block_kind", "practice" if practice else "scored")),
        "pair_id": pair_id,
        "pair_relation": pair_relation,
        "practice": practice,
        "trial_phase": phase_kind,
        "cue_word": cue_word,
        "associate_word": associate_word,
        "study_correct_key": study_correct_key,
        "correct_key": correct_key,
        "test_options": "|".join(test_options),
        "trial_index_in_block": int(trial_spec.get("trial_index_in_block", 0)),
        "stimulus_summary": str(trial_spec.get("stimulus_summary", "")),
    }

    # Study phase
    if phase_kind == "study":
        study_fixation = make_unit(unit_label="study_fixation").add_stim(stim_bank.get("fixation"))
        set_trial_context(
            study_fixation,
            trial_id=trial_id,
            phase="study_fixation",
            deadline_s=fixation_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "study_fixation",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "block_idx": block_idx_val,
            },
            stim_id="fixation",
        )
        study_fixation.show(
            duration=fixation_duration,
            onset_trigger=settings.triggers.get("study_fixation_onset"),
        ).to_dict(trial_data)

        study_unit = make_unit(unit_label="study_pair")
        study_unit.add_stim(stim_bank.get_and_format("study_cue_word", word=cue_word))
        study_unit.add_stim(stim_bank.get_and_format("study_associate_word", word=associate_word))
        study_unit.add_stim(stim_bank.get("study_prompt"))
        set_trial_context(
            study_unit,
            trial_id=trial_id,
            phase="study_pair",
            deadline_s=study_duration,
            valid_keys=study_keys,
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "study_pair",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "cue_word": cue_word,
                "associate_word": associate_word,
                "study_correct_key": study_correct_key,
                "block_idx": block_idx_val,
            },
            stim_id="study_pair",
        )
        study_unit.capture_response(
            keys=study_keys,
            correct_keys=[study_correct_key],
            duration=study_duration,
            onset_trigger=settings.triggers.get("study_onset"),
            response_trigger={key: settings.triggers.get(f"response_{key}") for key in study_keys},
            timeout_trigger=settings.triggers.get("study_timeout"),
        ).to_dict(trial_data)

        response_key = _parse_response_key(study_unit.get_state("response", None))
        response_rt = study_unit.get_state("rt", None)
        response_correct = bool(response_key and response_key == study_correct_key)
        timed_out = response_key == ""

        trial_data.update(
            {
                "responded": bool(response_key),
                "response_key": response_key,
                "response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
                "response_correct": response_correct,
                "timed_out": timed_out,
                "selected_word": "",
                "study_response_key": response_key,
                "study_response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
                "study_response_correct": response_correct,
                "study_timed_out": timed_out,
            }
        )

        if practice:
            feedback_name = _feedback_stim_name(
                phase_kind="study",
                practice=True,
                timed_out=timed_out,
                response_correct=response_correct,
            )
            feedback_kwargs = {
                "cue_word": cue_word,
                "associate_word": associate_word,
                "correct_relation": pair_relation,
                "response_key": response_key,
            }
            if timed_out:
                feedback_kwargs["correct_relation"] = pair_relation
            feedback_unit = make_unit(unit_label="practice_study_feedback").add_stim(
                stim_bank.get_and_format(feedback_name, **feedback_kwargs)
            )
            set_trial_context(
                feedback_unit,
                trial_id=trial_id,
                phase="practice_study_feedback",
                deadline_s=practice_feedback_duration,
                valid_keys=[],
                block_id=block_id_val,
                condition_id=pair_id,
                task_factors={
                    "stage": "practice_study_feedback",
                    "block_kind": trial_data["block_kind"],
                    "pair_relation": pair_relation,
                    "practice": True,
                    "pair_id": pair_id,
                    "block_idx": block_idx_val,
                },
                stim_id=feedback_name,
            )
            feedback_unit.show(
                duration=practice_feedback_duration,
                onset_trigger=settings.triggers.get("practice_study_feedback_onset"),
            ).to_dict(trial_data)

        study_iti = make_unit(unit_label="study_iti").add_stim(stim_bank.get("fixation"))
        set_trial_context(
            study_iti,
            trial_id=trial_id,
            phase="study_iti",
            deadline_s=study_iti_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "study_iti",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "block_idx": block_idx_val,
            },
            stim_id="fixation",
        )
        study_iti.show(
            duration=study_iti_duration,
            onset_trigger=settings.triggers.get("study_iti_onset"),
        ).to_dict(trial_data)

        return trial_data

    # Test phase
    if phase_kind == "test":
        test_fixation = make_unit(unit_label="test_fixation").add_stim(stim_bank.get("fixation"))
        set_trial_context(
            test_fixation,
            trial_id=trial_id,
            phase="test_fixation",
            deadline_s=fixation_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "test_fixation",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "block_idx": block_idx_val,
            },
            stim_id="fixation",
        )
        test_fixation.show(
            duration=fixation_duration,
            onset_trigger=settings.triggers.get("test_fixation_onset"),
        ).to_dict(trial_data)

        test_unit = make_unit(unit_label="test_choice")
        test_unit.add_stim(stim_bank.get_and_format("test_cue_word", word=cue_word))
        for option_idx, option_word in enumerate(test_options, start=1):
            test_unit.add_stim(stim_bank.get_and_format(f"test_option_{option_idx}", option_word=option_word))
        test_unit.add_stim(stim_bank.get("test_prompt"))
        set_trial_context(
            test_unit,
            trial_id=trial_id,
            phase="test_choice",
            deadline_s=test_duration,
            valid_keys=test_keys,
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "test_choice",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "cue_word": cue_word,
                "associate_word": associate_word,
                "correct_key": correct_key,
                "test_options": "|".join(test_options),
                "block_idx": block_idx_val,
            },
            stim_id="test_choice",
        )
        test_unit.capture_response(
            keys=test_keys,
            correct_keys=[correct_key],
            duration=test_duration,
            onset_trigger=settings.triggers.get("test_onset"),
            response_trigger={key: settings.triggers.get(f"response_{key}") for key in test_keys},
            timeout_trigger=settings.triggers.get("response_timeout"),
        ).to_dict(trial_data)

        response_key = _parse_response_key(test_unit.get_state("response", None))
        response_rt = test_unit.get_state("rt", None)
        selected_word = _selected_test_word(test_options, response_key)
        response_correct = bool(response_key and response_key == correct_key)
        timed_out = response_key == ""

        trial_data.update(
            {
                "responded": bool(response_key),
                "response_key": response_key,
                "response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
                "response_correct": response_correct,
                "timed_out": timed_out,
                "selected_word": selected_word,
                "study_response_key": "",
                "study_response_rt": None,
                "study_response_correct": None,
                "study_timed_out": None,
                "test_response_key": response_key,
                "test_response_rt": float(response_rt) if isinstance(response_rt, (int, float)) else None,
                "test_response_correct": response_correct,
                "test_timed_out": timed_out,
            }
        )

        if practice:
            feedback_name = _feedback_stim_name(
                phase_kind="test",
                practice=True,
                timed_out=timed_out,
                response_correct=response_correct,
            )
            feedback_kwargs = {
                "cue_word": cue_word,
                "associate_word": associate_word,
                "correct_word": associate_word,
                "selected_word": selected_word,
                "response_key": response_key,
            }
            feedback_unit = make_unit(unit_label="practice_test_feedback").add_stim(
                stim_bank.get_and_format(feedback_name, **feedback_kwargs)
            )
            set_trial_context(
                feedback_unit,
                trial_id=trial_id,
                phase="practice_test_feedback",
                deadline_s=practice_feedback_duration,
                valid_keys=[],
                block_id=block_id_val,
                condition_id=pair_id,
                task_factors={
                    "stage": "practice_test_feedback",
                    "block_kind": trial_data["block_kind"],
                    "pair_relation": pair_relation,
                    "practice": True,
                    "pair_id": pair_id,
                    "correct_key": correct_key,
                    "block_idx": block_idx_val,
                },
                stim_id=feedback_name,
            )
            feedback_unit.show(
                duration=practice_feedback_duration,
                onset_trigger=settings.triggers.get("practice_test_feedback_onset"),
            ).to_dict(trial_data)

        test_iti = make_unit(unit_label="test_iti").add_stim(stim_bank.get("fixation"))
        set_trial_context(
            test_iti,
            trial_id=trial_id,
            phase="test_iti",
            deadline_s=test_iti_duration,
            valid_keys=[],
            block_id=block_id_val,
            condition_id=pair_id,
            task_factors={
                "stage": "test_iti",
                "block_kind": trial_data["block_kind"],
                "pair_relation": pair_relation,
                "practice": practice,
                "pair_id": pair_id,
                "block_idx": block_idx_val,
            },
            stim_id="fixation",
        )
        test_iti.show(
            duration=test_iti_duration,
            onset_trigger=settings.triggers.get("test_iti_onset"),
        ).to_dict(trial_data)

        return trial_data

    raise ValueError(f"Unknown trial phase {phase_kind!r} for pair {pair_id!r}")
