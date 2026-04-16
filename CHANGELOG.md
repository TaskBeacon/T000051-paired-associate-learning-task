# CHANGELOG

All notable development changes for `T000051-paired-associate-learning-task` are documented here.

## [v0.1.0-dev] - 2026-04-17

### Added
- Paired-associate learning task flow with study-phase relation judgment, test-phase 4-choice recognition, practice feedback, block summaries, and final summary.
- Deterministic word-pair banks with disjoint slices across the practice and scored lists.
- Task-specific sampler simulation support for PAL study/test phases.
- Fresh evidence bundle, stimulus mapping, and task logic audit for the PAL workflow.

### Changed
- Replaced the matrix-reasoning scaffold with a verbal paired-associate learning runtime.
- Reworked the runtime around linked study/test phases per pair and block-level summaries.
- Updated the task metadata, README, assets README, and reference artifacts to match the PAL protocol.

### Fixed
- Removed the stale matrix-reasoning references, docs, and plot assumptions from the inherited scaffold.
- Aligned the practice feedback path, response timing, and simulation profile with the PAL workflow.
