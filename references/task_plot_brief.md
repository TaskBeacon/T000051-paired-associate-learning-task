# Task Plot Brief

- Task: Paired-Associate Learning Task
- Figure title: Paired-Associate Learning Task
- Subtitle: Construct: verbal associative memory / paired-word learning
- Source priority: `README.md`, `config/config.yaml`, `src/run_trial.py`, `references/task_logic_audit.md`.

## Timeline Rows

1. Practice list
2. Scored list 1
3. Scored list 2

## List Structure

- Each list has 10 word pairs.
- Each list runs a study phase for all pairs, then a 4-choice test phase.
- Practice list includes study feedback and test feedback.
- Scored lists do not include corrective feedback.

## Study Trial Flow

1. Study fixation, 500 ms.
2. Study pair, 1500 ms: cue word plus associate word.
3. Participant presses `R` for related or `U` for unrelated.
4. Practice study feedback, 800 ms, practice only.
5. Study ITI, 400 ms.

## Test Trial Flow

1. Test fixation, 500 ms.
2. Test choice, 6000 ms: cue word plus four response options in a 2x2 grid.
3. Participant presses `1`, `2`, `3`, or `4`.
4. Practice test feedback, 800 ms, practice only.
5. Test ITI, 400 ms.

## Conditions

- Blocks: practice, scored_1, scored_2.
- Study relation: related versus unrelated.
- Test options: one correct associate and three lures.
