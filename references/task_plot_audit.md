# Task Plot Audit

- generated_at: 2026-04-17T01:07:33
- mode: existing
- task_path: E:\Taskbeacon\T000051-paired-associate-learning-task

## 1. Inputs and provenance

- E:\Taskbeacon\T000051-paired-associate-learning-task\README.md
- E:\Taskbeacon\T000051-paired-associate-learning-task\config\config.yaml
- E:\Taskbeacon\T000051-paired-associate-learning-task\src\run_trial.py

## 2. Evidence extracted from README

- | Step | Description |
- |---|---|
- | Study Fixation | Show a centered fixation cross for a short pre-pair interval. |
- | Study Pair | Show the cue word and associate word side-by-side, plus the R/U prompt. |
- | Study Response | Collect `R` for related or `U` for unrelated within the study window. |
- | Practice Study Feedback | Show corrective feedback only during the practice list. |
- | Study ITI | Show the fixation cross again before the next pair. |
- | Test Fixation | Show a centered fixation cross before the recognition screen. |
- | Test Choice | Show the cue word and four candidate associates in a 2x2 grid. |
- | Test Response | Collect `1`, `2`, `3`, or `4` for the recognition choice. |
- | Practice Test Feedback | Show corrective feedback only during the practice list. |
- | Test ITI | Show the fixation cross again before the next pair. |

## 3. Evidence extracted from config/source

- practice: phase=study fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- practice: phase=study pair, deadline_expr=study_duration, response_expr=n/a, stim_expr='study_pair'
- practice: phase=practice study feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- practice: phase=study iti, deadline_expr=study_iti_duration, response_expr=n/a, stim_expr='fixation'
- practice: phase=test fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- practice: phase=test choice, deadline_expr=test_duration, response_expr=n/a, stim_expr='test_choice'
- practice: phase=practice test feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- practice: phase=test iti, deadline_expr=test_iti_duration, response_expr=n/a, stim_expr='fixation'
- scored_1: phase=study fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- scored_1: phase=study pair, deadline_expr=study_duration, response_expr=n/a, stim_expr='study_pair'
- scored_1: phase=practice study feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- scored_1: phase=study iti, deadline_expr=study_iti_duration, response_expr=n/a, stim_expr='fixation'
- scored_1: phase=test fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- scored_1: phase=test choice, deadline_expr=test_duration, response_expr=n/a, stim_expr='test_choice'
- scored_1: phase=practice test feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- scored_1: phase=test iti, deadline_expr=test_iti_duration, response_expr=n/a, stim_expr='fixation'
- scored_2: phase=study fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- scored_2: phase=study pair, deadline_expr=study_duration, response_expr=n/a, stim_expr='study_pair'
- scored_2: phase=practice study feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- scored_2: phase=study iti, deadline_expr=study_iti_duration, response_expr=n/a, stim_expr='fixation'
- scored_2: phase=test fixation, deadline_expr=fixation_duration, response_expr=n/a, stim_expr='fixation'
- scored_2: phase=test choice, deadline_expr=test_duration, response_expr=n/a, stim_expr='test_choice'
- scored_2: phase=practice test feedback, deadline_expr=practice_feedback_duration, response_expr=n/a, stim_expr=feedback_name
- scored_2: phase=test iti, deadline_expr=test_iti_duration, response_expr=n/a, stim_expr='fixation'

## 4. Mapping to task_plot_spec

- timeline collection: one representative timeline per unique trial logic
- phase flow inferred from run_trial set_trial_context order and branch predicates
- participant-visible show() phases without set_trial_context are inferred where possible and warned
- duration/response inferred from deadline/capture expressions
- stimulus examples inferred from stim_id + config stimuli
- conditions with equivalent phase/timing logic collapsed and annotated as variants
- root_key: task_plot_spec
- spec_version: 0.2

## 5. Style decision and rationale

- Single timeline-collection view selected by policy: one representative condition per unique timeline logic.

## 6. Rendering parameters and constraints

- output_file: task_flow.png
- dpi: 300
- max_conditions: 3
- screens_per_timeline: 7
- screen_overlap_ratio: 0.1
- screen_slope: 0.08
- screen_slope_deg: 25.0
- screen_aspect_ratio: 1.4545454545454546
- qa_mode: local
- auto_layout_feedback:
  - layout pass 1: crop-only; left=0.030, right=0.031, blank=0.115
- auto_layout_feedback_records:
  - pass: 1
    metrics: {'left_ratio': 0.0304, 'right_ratio': 0.0312, 'blank_ratio': 0.1147}

## 7. Output files and checksums

- E:\Taskbeacon\T000051-paired-associate-learning-task\references\task_plot_spec.yaml: sha256=9125560179c7ca1228c9f619b865a469fb61613e995869c62ab16f630d4b9e1c
- E:\Taskbeacon\T000051-paired-associate-learning-task\references\task_plot_spec.json: sha256=52630470452e26df9ba3709ff6b0cb0499ca8adca97139d0dc75b6a5e8b130c7
- E:\Taskbeacon\T000051-paired-associate-learning-task\references\task_plot_source_excerpt.md: sha256=1f33053e1e5f1436ec8d06d38a54281be29e1c037fd79d4b2b8ebeb0ac8fb919
- E:\Taskbeacon\T000051-paired-associate-learning-task\task_flow.png: sha256=d410ab30f6a8356d288d5c876d276e71a92127ac07d4b67dc6c35e6886f3b364

## 8. Inferred/uncertain items

- practice:study fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- practice:study pair:heuristic numeric parse from '_duration(settings, 'study_duration', 1.5)'
- practice:practice study feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- practice:practice study feedback:stimulus unresolved, used textual fallback
- practice:study iti:heuristic numeric parse from '_duration(settings, 'study_iti_duration', 0.4)'
- practice:test fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- practice:test choice:heuristic numeric parse from '_duration(settings, 'test_duration', 6.0)'
- practice:practice test feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- practice:practice test feedback:stimulus unresolved, used textual fallback
- practice:test iti:heuristic numeric parse from '_duration(settings, 'test_iti_duration', 0.4)'
- practice: phases truncated to screens_per_timeline=6
- scored_1:study fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- scored_1:study pair:heuristic numeric parse from '_duration(settings, 'study_duration', 1.5)'
- scored_1:practice study feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- scored_1:practice study feedback:stimulus unresolved, used textual fallback
- scored_1:study iti:heuristic numeric parse from '_duration(settings, 'study_iti_duration', 0.4)'
- scored_1:test fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- scored_1:test choice:heuristic numeric parse from '_duration(settings, 'test_duration', 6.0)'
- scored_1:practice test feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- scored_1:practice test feedback:stimulus unresolved, used textual fallback
- scored_1:test iti:heuristic numeric parse from '_duration(settings, 'test_iti_duration', 0.4)'
- scored_1: phases truncated to screens_per_timeline=6
- scored_2:study fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- scored_2:study pair:heuristic numeric parse from '_duration(settings, 'study_duration', 1.5)'
- scored_2:practice study feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- scored_2:practice study feedback:stimulus unresolved, used textual fallback
- scored_2:study iti:heuristic numeric parse from '_duration(settings, 'study_iti_duration', 0.4)'
- scored_2:test fixation:heuristic numeric parse from '_duration(settings, 'fixation_duration', 0.5)'
- scored_2:test choice:heuristic numeric parse from '_duration(settings, 'test_duration', 6.0)'
- scored_2:practice test feedback:heuristic numeric parse from '_duration(settings, 'practice_feedback_duration', 0.8)'
- scored_2:practice test feedback:stimulus unresolved, used textual fallback
- scored_2:test iti:heuristic numeric parse from '_duration(settings, 'test_iti_duration', 0.4)'
- scored_2: phases truncated to screens_per_timeline=6
- collapsed equivalent condition logic into representative timeline: practice, scored_1, scored_2
- unparsed if-tests defaulted to condition-agnostic applicability: not study_keys; not test_keys; phase_kind == 'study'; phase_kind == 'test'; practice; timed_out
