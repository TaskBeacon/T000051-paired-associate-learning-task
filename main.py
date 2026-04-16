from contextlib import nullcontext
from pathlib import Path

import pandas as pd
from psychopy import core

from psyflow import (
    StimBank,
    StimUnit,
    SubInfo,
    TaskSettings,
    context_from_config,
    initialize_exp,
    initialize_triggers,
    load_config,
    parse_task_run_options,
    runtime_context,
    set_trial_context,
)

from src.run_trial import run_trial
from src.utils import build_session_plan, summarize_trials

MODES = ("human", "qa", "sim")
DEFAULT_CONFIG_BY_MODE = {
    "human": "config/config.yaml",
    "qa": "config/config_qa.yaml",
    "sim": "config/config_scripted_sim.yaml",
}


def _show_text(
    stim_bank: StimBank,
    win,
    kb,
    runtime,
    stim_name: str,
    *,
    phase: str,
    trial_id: str,
    block_id: str,
    condition_id: str,
    valid_keys: list[str],
    task_factors: dict | None = None,
    **fmt_kwargs,
) -> None:
    unit = StimUnit(stim_name, win, kb, runtime=runtime).add_stim(
        stim_bank.get_and_format(stim_name, **fmt_kwargs)
    )
    set_trial_context(
        unit,
        trial_id=trial_id,
        phase=phase,
        deadline_s=None,
        valid_keys=list(valid_keys),
        block_id=block_id,
        condition_id=condition_id,
        task_factors=task_factors or {},
        stim_id=stim_name,
    )
    unit.wait_and_continue(keys=list(valid_keys))


def run(options):
    """Run the paired-associate learning task in human/qa/sim mode."""
    task_root = Path(__file__).resolve().parent
    cfg = load_config(str(options.config_path))

    output_dir: Path | None = None
    runtime_scope = nullcontext()
    runtime_ctx = None
    if options.mode in ("qa", "sim"):
        runtime_ctx = context_from_config(task_dir=task_root, config=cfg, mode=options.mode)
        output_dir = runtime_ctx.output_dir
        runtime_scope = runtime_context(runtime_ctx)

    with runtime_scope:
        if options.mode == "qa":
            subject_data = {"subject_id": "qa"}
        elif options.mode == "sim":
            participant_id = "sim"
            if runtime_ctx is not None and runtime_ctx.session is not None:
                participant_id = str(runtime_ctx.session.participant_id or "sim")
            subject_data = {"subject_id": participant_id}
        else:
            subform = SubInfo(cfg["subform_config"])
            subject_data = subform.collect()

        settings = TaskSettings.from_dict(cfg["task_config"])
        if options.mode in ("qa", "sim") and output_dir is not None:
            settings.save_path = str(output_dir)
        settings.add_subinfo(subject_data)

        if options.mode == "qa" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "qa_trace.csv")
            settings.log_file = str(output_dir / "qa_psychopy.log")
            settings.json_file = str(output_dir / "qa_settings.json")
        elif options.mode == "sim" and output_dir is not None:
            output_dir.mkdir(parents=True, exist_ok=True)
            settings.res_file = str(output_dir / "sim_trace.csv")
            settings.log_file = str(output_dir / "sim_psychopy.log")
            settings.json_file = str(output_dir / "sim_settings.json")

        settings.triggers = cfg["trigger_config"]
        trigger_runtime = initialize_triggers(mock=True) if options.mode in ("qa", "sim") else initialize_triggers(cfg)

        win, kb = initialize_exp(settings)
        stim_bank = StimBank(win, cfg["stim_config"]).preload_all()

        settings.save_to_json()

        trigger_runtime.send(settings.triggers.get("exp_onset"))

        continue_key = [str(getattr(settings, "continue_key", "space")).strip().lower()]
        _show_text(
            stim_bank,
            win,
            kb,
            trigger_runtime,
            "instruction_text",
            phase="instruction",
            trial_id="instruction",
            block_id="instruction",
            condition_id="instruction",
            valid_keys=continue_key,
            task_factors={
                "stage": "instruction",
                "practice_pairs": int(getattr(settings, "practice_pairs", 10)),
                "scored_pairs_per_block": int(getattr(settings, "scored_pairs_per_block", 10)),
                "study_key": str(getattr(settings, "related_key", "r")).upper(),
                "test_keys": "1/2/3/4",
            },
            practice_pairs=int(getattr(settings, "practice_pairs", 10)),
            scored_pairs_per_block=int(getattr(settings, "scored_pairs_per_block", 10)),
            study_key=str(getattr(settings, "related_key", "r")).upper(),
            test_keys="1/2/3/4",
        )

        session_plan = build_session_plan(settings)
        all_data: list[dict] = []
        scored_block_counter = 0

        for block_num, block_plan in enumerate(session_plan, start=1):
            block_kind = str(block_plan["block_kind"])
            block_id = str(block_plan["block_id"])
            block_idx = int(block_plan["block_idx"])
            block_trials = []

            trigger_runtime.send(settings.triggers.get("block_onset"))
            _show_text(
                stim_bank,
                win,
                kb,
                trigger_runtime,
                "block_intro_text",
                phase="block_intro",
                trial_id=f"block_intro_{block_num}",
                block_id=block_id,
                condition_id=block_id,
                valid_keys=continue_key,
                task_factors={
                    "stage": "block_intro",
                    "block_kind": block_kind,
                    "block_num": block_num,
                    "total_blocks": len(session_plan),
                    "pair_count": int(block_plan["pair_count"]),
                },
                block_label=str(block_plan["block_label"]),
                block_num=block_num,
                total_blocks=len(session_plan),
                pair_count=int(block_plan["pair_count"]),
                study_key=str(getattr(settings, "related_key", "r")).upper(),
                unrelated_key=str(getattr(settings, "unrelated_key", "u")).upper(),
                test_keys="1, 2, 3, 4",
            )

            for trial_spec in block_plan["trials"]:
                trial_data = run_trial(
                    win,
                    kb,
                    settings,
                    condition=trial_spec,
                    stim_bank=stim_bank,
                    trigger_runtime=trigger_runtime,
                    block_id=block_id,
                    block_idx=block_idx,
                )
                block_trials.append(trial_data)
                all_data.append(trial_data)

            summary = summarize_trials(block_trials)
            trigger_runtime.send(settings.triggers.get("block_end"))

            if block_kind == "practice":
                trigger_runtime.send(settings.triggers.get("block_break_onset"))
                _show_text(
                    stim_bank,
                    win,
                    kb,
                    trigger_runtime,
                    "practice_break_text",
                    phase="practice_break",
                    trial_id="practice_break",
                    block_id=block_id,
                    condition_id=block_id,
                    valid_keys=continue_key,
                    task_factors={
                        "stage": "practice_break",
                        "study_accuracy": summary["study_accuracy"],
                        "test_accuracy": summary["test_accuracy"],
                        "mean_test_rt_ms": summary["test_mean_correct_rt_ms"],
                        "timeout_count": summary["timeout_count"],
                    },
                    study_accuracy=summary["study_accuracy"],
                    test_accuracy=summary["test_accuracy"],
                    mean_test_rt_ms=summary["test_mean_correct_rt_ms"],
                    timeout_count=summary["timeout_count"],
                )
            else:
                scored_block_counter += 1
                trigger_runtime.send(settings.triggers.get("block_break_onset"))
                _show_text(
                    stim_bank,
                    win,
                    kb,
                    trigger_runtime,
                    "block_break_text",
                    phase="block_break",
                    trial_id=f"block_break_{scored_block_counter}",
                    block_id=block_id,
                    condition_id=block_id,
                    valid_keys=continue_key,
                    task_factors={
                        "stage": "block_break",
                        "block_num": scored_block_counter,
                        "total_blocks": sum(1 for b in session_plan if b["block_kind"] == "scored"),
                        "study_accuracy": summary["study_accuracy"],
                        "test_accuracy": summary["test_accuracy"],
                        "mean_test_rt_ms": summary["test_mean_correct_rt_ms"],
                        "timeout_count": summary["timeout_count"],
                    },
                    block_num=scored_block_counter,
                    total_blocks=sum(1 for b in session_plan if b["block_kind"] == "scored"),
                    study_accuracy=summary["study_accuracy"],
                    test_accuracy=summary["test_accuracy"],
                    mean_test_rt_ms=summary["test_mean_correct_rt_ms"],
                    timeout_count=summary["timeout_count"],
                )

        total_summary = summarize_trials(all_data)
        trigger_runtime.send(settings.triggers.get("good_bye_onset"))
        _show_text(
            stim_bank,
            win,
            kb,
            trigger_runtime,
            "good_bye_text",
            phase="good_bye",
            trial_id="good_bye",
            block_id="good_bye",
            condition_id="good_bye",
            valid_keys=continue_key,
            task_factors={
                "stage": "good_bye",
                "study_accuracy": total_summary["study_accuracy"],
                "test_accuracy": total_summary["test_accuracy"],
                "mean_test_rt_ms": total_summary["test_mean_correct_rt_ms"],
                "timeout_count": total_summary["timeout_count"],
            },
            study_accuracy=total_summary["study_accuracy"],
            test_accuracy=total_summary["test_accuracy"],
            mean_test_rt_ms=total_summary["test_mean_correct_rt_ms"],
            timeout_count=total_summary["timeout_count"],
        )

        trigger_runtime.send(settings.triggers.get("exp_end"))
        pd.DataFrame(all_data).to_csv(settings.res_file, index=False)

        trigger_runtime.close()
        core.quit()


def main() -> None:
    task_root = Path(__file__).resolve().parent
    options = parse_task_run_options(
        task_root=task_root,
        description="Run task in human/qa/sim mode.",
        default_config_by_mode=DEFAULT_CONFIG_BY_MODE,
        modes=MODES,
    )
    run(options)


if __name__ == "__main__":
    main()
