# Task Logic Audit

## 1. Paradigm Intent

- Task: Paired-Associate Learning Task
- Primary construct: verbal associative memory / paired-word learning
- Manipulated factors:
  - block: practice list versus scored list 1 versus scored list 2
  - phase: study versus test
  - pair relation at study: related versus unrelated
  - response outcome: correct / incorrect / timeout
- Dependent measures:
  - study-judgment accuracy and RT
  - test recognition accuracy and RT
  - timeout rate
  - block-to-block learning change
- Key citations:
  - W2106602535, word paired-associate memory task with new-learning and proactive-interference manipulations
  - W2040178194, verbal paired-associate learning in older adults with fMRI evidence for verbal PAL
  - W2120104877, paired-associate learning as a verbal learning construct with open-access behavioral evidence
  - W2024910015, high-impact associative-learning paper used as broad mechanistic support

## 2. Block/Trial Workflow

### Block Structure

- Total blocks: 3
- Trials per block: 20 visible trials
  - 10 study trials
  - 10 test trials
- Randomization/counterbalancing:
  - each block uses 10 word pairs
  - within each block, 5 pairs are semantically related and 5 are semantically unrelated
  - blocks draw disjoint slices from the related/unrelated banks so practice and scored lists do not repeat the same pairs
  - study order is randomized with a seed and constrained to avoid long runs of the same relation type
  - test order is randomized separately from study order while preserving cue-target pairing
  - each test item has 4 options, with one correct associate and three lures drawn from the current block plus a small filler pool
  - correct option positions are counterbalanced across the 4 response keys
- Condition weight policy:
  - `task.condition_weights` remains null
  - block balance is handled by a custom session-plan generator, not by weighted labels
- Condition generation method:
  - custom generator
  - simple labels are insufficient because each block must produce linked study/test trial pairs, relation labels, cue-target mappings, and lure sets
  - generated data shape: list of dicts with `phase_kind`, `block_idx`, `block_id`, `pair_id`, `pair_relation`, `cue_word`, `associate_word`, `test_options`, `correct_key`, `practice`, and `trial_index_in_block`
- Runtime-generated trial values:
  - pair selection is deterministic from a common-noun bank and the overall seed
  - lure construction is deterministic from the block seed and pair index
  - option order is deterministic per test trial
  - practice uses the same logic but enables corrective feedback

### Trial State Machine

1. State name: instruction screen
   - Onset trigger: `exp_onset`
   - Stimuli shown: task instructions, pair-learning rule, study/test key mappings
   - Valid keys: `space`
   - Timeout behavior: wait for `space`
   - Next state: block intro

2. State name: block intro
   - Onset trigger: `block_onset`
   - Stimuli shown: practice list or scored list introduction
   - Valid keys: `space`
   - Timeout behavior: wait for `space`
   - Next state: study fixation

3. State name: study fixation
   - Onset trigger: `study_fixation_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: fixed short duration
   - Next state: study pair

4. State name: study pair
   - Onset trigger: `study_onset`
   - Stimuli shown: cue word and associate word side-by-side, plus study prompt
   - Valid keys: `r`, `u`
   - Timeout behavior: fixed study deadline or early response
   - Next state: practice study feedback or study ITI

5. State name: practice study feedback
   - Onset trigger: `practice_study_feedback_onset`
   - Stimuli shown: correctness feedback for the study relation judgment
   - Valid keys: none
   - Timeout behavior: short fixed duration
   - Next state: study ITI

6. State name: study ITI
   - Onset trigger: `study_iti_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: fixed short duration
   - Next state: next study pair or test fixation

7. State name: test fixation
   - Onset trigger: `test_fixation_onset`
   - Stimuli shown: fixation cross
   - Valid keys: none
   - Timeout behavior: fixed short duration
   - Next state: test choice

8. State name: test choice
   - Onset trigger: `test_onset`
   - Stimuli shown: cue word and four response options in a 2x2 grid
   - Valid keys: `1`, `2`, `3`, `4`
   - Timeout behavior: fixed recognition deadline or early response
   - Next state: practice test feedback or test ITI

9. State name: practice test feedback
   - Onset trigger: `practice_test_feedback_onset`
   - Stimuli shown: correctness feedback and, if incorrect, the correct associate word
   - Valid keys: none
   - Timeout behavior: short fixed duration
   - Next state: test ITI

10. State name: test ITI
    - Onset trigger: `test_iti_onset`
    - Stimuli shown: fixation cross
    - Valid keys: none
    - Timeout behavior: fixed short duration
    - Next state: next test pair or block summary

11. State name: block summary
    - Onset trigger: `block_break_onset`
    - Stimuli shown: block accuracy summary, study accuracy, mean test RT, timeout count
    - Valid keys: `space`
    - Timeout behavior: wait for `space`
    - Next state: next block or final summary

12. State name: final summary
    - Onset trigger: `exp_end`
    - Stimuli shown: overall accuracy summary and exit prompt
    - Valid keys: `space`
    - Timeout behavior: wait for `space`
    - Next state: quit

## 3. Condition Semantics

For each condition token in `task.conditions`:

- Condition ID: `practice`
  - Participant-facing meaning: practice learning list
  - Concrete stimulus realization: 10 word pairs, 5 related and 5 unrelated, with practice-only corrective feedback
  - Outcome rules: study relation judgments and test recognition are scored; feedback is shown only in practice

- Condition ID: `scored_1`
  - Participant-facing meaning: scored learning list 1
  - Concrete stimulus realization: 10 new word pairs, balanced by relation type, followed by a 4-option recognition test
  - Outcome rules: responses are recorded without corrective feedback

- Condition ID: `scored_2`
  - Participant-facing meaning: scored learning list 2
  - Concrete stimulus realization: 10 new word pairs, balanced by relation type, followed by a 4-option recognition test
  - Outcome rules: responses are recorded without corrective feedback

Participant-facing text and stimuli are defined as follows:

- Participant-facing text source: `config/config*.yaml` for instructions, prompts, and feedback; code constants for the deterministic word-pair bank
- Why this source is appropriate for auditability: instructions and prompts remain localization-friendly in config, while the stimulus bank is a small, fixed set of concrete word pairs that can be traced in code and the audit
- Localization strategy: English defaults live in config; translating the task later only requires swapping prompt text and the word-pair bank, not changing the trial engine

## 4. Response and Scoring Rules

- Response mapping:
  - study judgment: `r` = related, `u` = unrelated
  - test recognition: `1` through `4` select the four response options
- Response key source: config-defined response key lists
- If code-defined, why config-driven mapping is not sufficient:
  - the test phase needs a distinct 4-choice grid and the study phase needs a binary relation judgment, so the runtime uses two config-driven key sets rather than a single global mapping
- Missing-response policy:
  - study timeout is recorded if no relation judgment is made before deadline
  - test timeout is recorded if no recognition choice is made before deadline
  - practice trials show timeout feedback
  - scored trials advance without corrective feedback
- Correctness logic:
  - study is correct when the judgment key matches the pair relation
  - test is correct when the chosen option matches the learned associate word
- Reward/penalty updates:
  - none
  - this is a pure learning and memory task
- Running metrics:
  - study accuracy
  - test recognition accuracy
  - mean correct study RT
  - mean correct test RT
  - timeout count
  - block-to-block change in test accuracy

## 5. Stimulus Layout Plan

For every screen with multiple simultaneous options/stimuli:

- Screen name: instruction screen
  - Stimulus IDs shown together: `instruction_text`
  - Layout anchors (`pos`): centered multi-line text block
  - Size/spacing (`height`, width, wrap): large readable block with wrap width around 1000 px
  - Readability/overlap checks: single text block only
  - Rationale: explains the learning rule and key mapping before the task starts

- Screen name: block intro
  - Stimulus IDs shown together: `block_intro_text`
  - Layout anchors (`pos`): centered multi-line text block
  - Size/spacing (`height`, width, wrap): large readable block with wrap width around 1000 px
  - Readability/overlap checks: single text block only
  - Rationale: tells the participant whether this is practice or a scored list

- Screen name: study pair
  - Stimulus IDs shown together: cue word, associate word, study prompt
  - Layout anchors (`pos`): cue word left of center, associate word right of center, prompt near bottom
  - Size/spacing (`height`, width, wrap): large word height with enough horizontal separation to prevent overlap
  - Readability/overlap checks: the two words must remain readable at 1280x720 without crowding the prompt
  - Rationale: displays the pair the participant must learn

- Screen name: test choice
  - Stimulus IDs shown together: cue word, four response option words, test prompt
  - Layout anchors (`pos`): cue word top-center; options in a 2x2 grid
  - Size/spacing (`height`, width, wrap): option words large enough to read without overlap
  - Readability/overlap checks: all four options must fit cleanly in the grid with equal spacing
  - Rationale: supports 4-choice recognition using the configured number keys

- Screen name: practice feedback
  - Stimulus IDs shown together: practice feedback text only
  - Layout anchors (`pos`): centered text block
  - Size/spacing (`height`, width, wrap): moderate readable block
  - Readability/overlap checks: single text block only
  - Rationale: gives corrective feedback only during practice

- Screen name: block summary
  - Stimulus IDs shown together: `block_break`
  - Layout anchors (`pos`): centered text block
  - Size/spacing (`height`, width, wrap): summary text with enough vertical spacing for two accuracy metrics
  - Readability/overlap checks: summary should fit on one screen without truncation
  - Rationale: provides block-level performance summary and a pause before the next list

- Screen name: final summary
  - Stimulus IDs shown together: `good_bye`
  - Layout anchors (`pos`): centered text block
  - Size/spacing (`height`, width, wrap): summary text with clear exit prompt
  - Readability/overlap checks: final screen should not crowd the metric lines
  - Rationale: closes the task cleanly

## 6. Trigger Plan

- `exp_onset`: experiment start
- `exp_end`: experiment end
- `block_onset`: block intro onset
- `block_end`: block completion after the test phase
- `study_fixation_onset`: study fixation onset
- `study_onset`: study pair onset
- `response_r`: related study judgment
- `response_u`: unrelated study judgment
- `study_timeout`: study deadline reached
- `practice_study_feedback_onset`: practice study feedback onset
- `study_iti_onset`: study inter-trial interval
- `test_fixation_onset`: test fixation onset
- `test_onset`: test choice onset
- `response_1` / `response_2` / `response_3` / `response_4`: recognition choice responses
- `response_timeout`: test deadline reached
- `practice_test_feedback_onset`: practice test feedback onset
- `test_iti_onset`: test inter-trial interval
- `block_break_onset`: block summary onset

## 7. Architecture Decisions (Auditability)

- `main.py` runtime flow style: simple single-flow runtime with a custom session plan that explicitly runs study and test phases per block
- `utils.py` used? yes
- If yes, exact purpose:
  - deterministic word-pair bank selection
  - block/session planning
  - lure and option construction for the recognition test
  - summary aggregation across study and test phases
- Custom controller used? yes
- If yes, why PsyFlow-native path is insufficient:
  - the task needs linked study/test pair phases, pair-specific relation labels, and test-option construction that cannot be represented cleanly as a flat condition list
- Legacy/backward-compatibility fallback logic required? no

## 8. Inference Log

- Decision: use a short-form 10-pair practice list and two 10-pair scored lists
  - Why inference was required: the accessible papers describe paired-associate learning paradigms, but the exact short-form block size needed for this repository is not specified
  - Citation-supported rationale: the protocol papers support repeated pair learning and cued retrieval, but they do not mandate this repository's short validation length

- Decision: retain study-phase related/unrelated judgments but use a 4-option recognition test instead of free recall
  - Why inference was required: the framework in this workspace is key-based and does not provide a standard free-text recall response path
  - Citation-supported rationale: the primary paper uses word-pair study with relatedness judgments and later retrieval of learned pairs; the recognition test is a framework-compatible adaptation of the retrieval phase

- Decision: derive a deterministic common-noun bank in code instead of reproducing a single published stimulus list verbatim
  - Why inference was required: the accessible text describes the task structure but does not enumerate a canonical full word bank
  - Citation-supported rationale: the selected papers establish the use of verbal paired associates and word-pair learning, which supports a matched, reproducible noun-pair bank

- Decision: treat the Nature Neuroscience associative-learning paper as background support rather than the direct stimulus source
  - Why inference was required: it supports associative learning mechanistically but does not specify the exact PAL stimuli
  - Citation-supported rationale: it is a high-impact open-access associative-learning paper that satisfies the build filter and strengthens the learning-paradigm rationale

## Contract Note

- Participant-facing labels/instructions/options should be config-defined whenever possible.
- `src/run_trial.py` should not hardcode participant-facing text that would require code edits for localization.

