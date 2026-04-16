# Paired-Associate Learning Task

| Field | Value |
|---|---|
| Name | Paired-Associate Learning Task |
| Version | v0.1.0-dev |
| URL / Repository | `E:\Taskbeacon\T000051-paired-associate-learning-task` |
| Short Description | Verbal paired-associate learning with study-phase relation judgment and 4-choice recognition |
| Created By | TaskBeacon build pipeline |
| Date Updated | 2026-04-17 |
| PsyFlow Version | 0.1.12 |
| PsychoPy Version | 2025.2.4 |
| Modality | Behavior |
| Language | English |

## 1. Task Overview

This task implements a verbal paired-associate learning paradigm in PsychoPy/PsyFlow. Participants learn word pairs across three lists: one practice list and two scored lists. Each list contains a deterministic set of cue/associate word pairs drawn from the local word banks.

The runtime follows two phases per pair. During study, participants judge whether the pair is related or unrelated by meaning using `R` and `U`. During test, they choose the associate word that was paired with the cue word from a 4-choice grid using keys `1`-`4`.

The task is designed for auditable, repeatable execution. Word-pair selection, lure construction, and option ordering are deterministic from the task seed and block index. Practice lists include corrective feedback; scored lists do not.

## 2. Task Flow

![Task Flow](task_flow.png)

### Block-Level Flow

| Step | Description |
|---|---|
| Load Config | Read the mode-specific config and task metadata. |
| Collect Subject Info | Collect subject ID in human mode or inject deterministic IDs in QA/sim. |
| Initialize Runtime | Create the PsychoPy window, keyboard, triggers, and stimulus bank. |
| Show Instructions | Present the paired-associate learning instructions and key mappings. |
| Run Practice List | Present the practice block with study judgments, test choices, and corrective feedback. |
| Show Practice Break | Display study accuracy, test accuracy, mean test RT, and timeout count. |
| Run Scored List 1 | Present the first scored block without corrective feedback. |
| Show Block Break | Display block-level performance summary after scored list 1. |
| Run Scored List 2 | Present the second scored block without corrective feedback. |
| Show Block Break | Display block-level performance summary after scored list 2. |
| Save Outputs | Write the CSV data and settings JSON to the mode output folder. |
| Finish | Present the goodbye screen, send the end trigger, and quit PsychoPy. |

### Trial-Level Flow

| Step | Description |
|---|---|
| Study Fixation | Show a centered fixation cross for a short pre-pair interval. |
| Study Pair | Show the cue word and associate word side-by-side, plus the R/U prompt. |
| Study Response | Collect `R` for related or `U` for unrelated within the study window. |
| Practice Study Feedback | Show corrective feedback only during the practice list. |
| Study ITI | Show the fixation cross again before the next pair. |
| Test Fixation | Show a centered fixation cross before the recognition screen. |
| Test Choice | Show the cue word and four candidate associates in a 2x2 grid. |
| Test Response | Collect `1`, `2`, `3`, or `4` for the recognition choice. |
| Practice Test Feedback | Show corrective feedback only during the practice list. |
| Test ITI | Show the fixation cross again before the next pair. |

### Controller Logic

| Feature | Description |
|---|---|
| Condition Scheduling | `build_session_plan(...)` creates one practice block and two scored blocks with disjoint word-pair slices. |
| Determinism | The cue/associate bank, lure selection, and option order are all deterministic from the overall seed and block index. |
| Trial Context | Every participant-visible phase in `src/run_trial.py` calls `set_trial_context(...)` before display or response capture. |
| Scoring | Study correctness is based on the related/unrelated judgment key; test correctness is based on the selected associate word. |
| Simulation | The scripted responder exercises the response path, and the sampler responder varies accuracy, RT, and timeout behavior. |

## 3. Configuration Summary

### a. Subject Info

| Field | Meaning |
|---|---|
| `subject_id` | Three-digit participant identifier. |

### b. Window Settings

| Parameter | Value |
|---|---|
| `window.size` | `[1280, 720]` |
| `window.units` | `pix` |
| `window.bg_color` | `black` |
| `window.fullscreen` | `false` |
| `window.screen` | `0` |

### c. Stimuli

| Stimulus ID | Purpose |
|---|---|
| `instruction_text` | Intro screen explaining the task, the study/test phases, and the response keys. |
| `block_intro_text` | Block intro screen that labels the current list and reminds the participant of the keys. |
| `fixation` | Center fixation cross used before study and test screens and during ITIs. |
| `study_cue_word` | Cue word on the left side of the study screen. |
| `study_associate_word` | Associate word on the right side of the study screen. |
| `study_prompt` | Relation-judgment prompt shown below the study pair. |
| `test_cue_word` | Cue word shown above the 4-choice test grid. |
| `test_option_1` / `test_option_2` / `test_option_3` / `test_option_4` | Four candidate associate words laid out in a 2x2 grid. |
| `test_prompt` | Recognition prompt shown below the test grid. |
| `practice_study_feedback_*` | Practice-only study feedback screens for correct, incorrect, and timeout outcomes. |
| `practice_test_feedback_*` | Practice-only test feedback screens for correct, incorrect, and timeout outcomes. |
| `practice_break_text` | Practice summary with study and test accuracy plus RT/timeout summary. |
| `block_break_text` | Scored-list summary with study and test accuracy plus RT/timeout summary. |
| `good_bye_text` | Final task summary and exit prompt. |

### d. Timing

| Parameter | Value |
|---|---|
| `timing.fixation_duration` | `0.5` s |
| `timing.study_duration` | `1.5` s |
| `timing.study_iti_duration` | `0.4` s |
| `timing.test_duration` | `6.0` s |
| `timing.test_iti_duration` | `0.4` s |
| `timing.practice_feedback_duration` | `0.8` s |

### e. Triggers

| Trigger | Code |
|---|---|
| `exp_onset` / `exp_end` | `1` / `2` |
| `block_onset` / `block_end` | `10` / `11` |
| `instruction_onset` | `12` |
| `study_fixation_onset` | `20` |
| `study_onset` | `21` |
| `response_r` / `response_u` | `31` / `32` |
| `study_timeout` | `33` |
| `practice_study_feedback_onset` | `34` |
| `study_iti_onset` | `35` |
| `test_fixation_onset` | `40` |
| `test_onset` | `41` |
| `response_1` / `response_2` / `response_3` / `response_4` | `51` / `52` / `53` / `54` |
| `response_timeout` | `55` |
| `practice_test_feedback_onset` | `56` |
| `test_iti_onset` | `57` |
| `block_break_onset` | `60` |
| `good_bye_onset` | `61` |

### f. Adaptive Controller

| Parameter | Value |
|---|---|
| Adaptive controller | None |

## 4. Methods (for academic publication)

Participants completed a verbal paired-associate learning task implemented in PsychoPy/PsyFlow. Across three lists, they viewed cue/associate word pairs, made a related/unrelated judgment during study, and then chose the learned associate from four alternatives during test.

The implementation uses deterministic word-bank sampling so the order of pairs, the lure set, and the response-option layout are reproducible for auditing and simulation. Practice feedback is enabled only in the practice list; scored lists are feedback-free.

The retrieval screen is implemented as a 4-choice recognition adaptation to fit the key-based framework used in this repository. That adaptation is documented in the task logic audit and stimulus mapping files.
