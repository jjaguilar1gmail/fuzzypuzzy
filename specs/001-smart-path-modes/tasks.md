# Tasks: Smart Path Modes

## Dependency Overview
- User Stories priority order: US1 (fast non-hanging generation) → US2 (variety via smart modes) → US3 (partial coverage acceptance)
- Foundational tasks must precede all story phases.

## Phase 1: Setup
- [ ] T001 Establish feature branch context (already created) reference only
- [ ] T002 Add new config flags placeholders in generate/generator.py (allow_partial_paths, min_cover_ratio, path_time_ms)
- [ ] T003 Insert PathBuildResult and PathBuildSettings dataclass stubs in generate/path_builder.py
- [ ] T004 Add new metrics placeholders (path_build_ms, path_coverage) in GeneratedPuzzle construction (generate/generator.py)

## Phase 2: Foundational
- [ ] T005 Refactor PathBuilder.build to route through internal _build_mode dispatcher (generate/path_builder.py)
- [ ] T006 Introduce structured return object PathBuildResult for serpentine legacy mode wrapper (generate/path_builder.py)
- [ ] T007 Add CLI argument parsing for --allow-partial-paths, --min-cover, --path-time-ms, update hidato.py
- [ ] T008 Update GenerationConfig with new fields (generate/models.py)
- [ ] T009 Add validation for min_cover_ratio and path_time_ms (generate/models.py)
- [ ] T010 Integrate PathBuildResult handling into Generator.generate_puzzle (generate/generator.py)
- [ ] T011 Adjust constraints.max_value when partial path accepted (generate/generator.py)
- [ ] T012 Ensure determinism by threading RNG through new path settings (generate/generator.py)

## Phase 3: US1 Fast, non-hanging generation
Goal: Guarantee bounded path building for large sizes without hangs or silent fallback.
Independent Test: Generate 9x9 across seeds {11,13,17,19,23} under 6000ms with no fallback reason.

- [ ] T013 [US1] Implement backbite_v1 initial path builder (generate/path_builder.py)
- [ ] T014 [P] [US1] Implement backbite end-reversal move logic & convergence checks (generate/path_builder.py)
- [ ] T015 [US1] Add timing budget enforcement (path_time_ms) in backbite loop (generate/path_builder.py)
- [ ] T016 [US1] Add structured reasons (success, timeout) to backbite PathBuildResult (generate/path_builder.py)
- [ ] T017 [US1] Integrate path_build_ms timing capture (generate/generator.py)
- [ ] T018 [US1] Add unit test: backbite_v1 completes within budget (tests/test_backbite_speed.py)
- [ ] T019 [P] [US1] Add unit test: determinism same seed same path (tests/test_backbite_determinism.py)
- [ ] T020 [US1] Add performance harness script for manual benchmarking (scripts/bench_path_build.py)

## Phase 4: US2 Smarter path modes with variety
Goal: Provide varied path shapes with heuristics and controlled retries.
Independent Test: Generate 5 puzzles same size different seeds; assert ≥3 distinct turn-count profiles.

- [ ] T021 [US2] Refactor random_walk to random_walk_v2 entry point (generate/path_builder.py)
- [ ] T022 [P] [US2] Add Warnsdorff neighbor ordering (generate/path_builder.py)
- [ ] T023 [US2] Add fragmentation pocket heuristic (generate/path_builder.py)
- [ ] T024 [US2] Implement restart loop with max_restarts (generate/path_builder.py)
- [ ] T025 [US2] Enforce max_nodes and max_time_ms limits (generate/path_builder.py)
- [ ] T026 [US2] Structured reasons (exhausted_restarts, timeout) for random_walk_v2 (generate/path_builder.py)
- [ ] T027 [US2] Diversity metric: compute turn count & segment length stats (generate/path_builder.py)
- [ ] T028 [US2] Unit test: random_walk_v2 respects max_restarts (tests/test_random_walk_limits.py)
- [ ] T029 [P] [US2] Unit test: variety across seeds (tests/test_path_variety.py)
- [ ] T030 [US2] Integrate diversity metrics into result.metrics (generate/path_builder.py)

## Phase 5: US3 Partial-coverage acceptance with guarantees
Goal: Accept high coverage partial paths cleanly; reject low coverage.
Independent Test: Force low time budget to trigger partial acceptance with coverage ≥ threshold.

- [ ] T031 [US3] Implement partial coverage acceptance path (Generator logic) (generate/generator.py)
- [ ] T032 [P] [US3] Block remainder cells when partial accepted (generate/generator.py)
- [ ] T033 [US3] Adjust Constraints.max_value after blocking (generate/generator.py)
- [ ] T034 [US3] Structured reason partial_accepted vs coverage_below_threshold (generate/path_builder.py)
- [ ] T035 [US3] Emit warnings on coverage below threshold (hidato.py)
- [ ] T036 [US3] Unit test: partial acceptance modifies constraint max_value (tests/test_partial_acceptance.py)
- [ ] T037 [US3] Unit test: rejection when coverage < min_cover_ratio (tests/test_partial_threshold.py)
- [ ] T038 [US3] Add CLI help text updates for new flags (hidato.py)

## Phase 6: Polish & Cross-Cutting
- [ ] T039 Add doc section to README.md summarizing smart path modes & partial coverage
- [ ] T040 Add quickstart examples integration (quickstart.md already created) ensure link in README.md
- [ ] T041 Add generation metrics printing (path_coverage, path_build_ms) in hidato.py
- [ ] T042 Add property test for seed reproducibility across modes (tests/test_seed_repro.py)
- [ ] T043 Benchmark script improvements: aggregate p90 timing (scripts/bench_path_build.py)
- [ ] T044 Add deprecation warning if old 'random_walk' invoked (generate/path_builder.py)
- [ ] T045 Final pass for lint/line length (ruff/flake) across modified files

## Parallel Execution Opportunities
- Backbite core (T013-T016) can run in parallel with initial tests (T018-T019) after stubs (T003-T006) land.
- Random_walk_v2 heuristics (T022, T023) parallelizable once entry function exists (T021).
- Partial acceptance generator logic (T031-T033) can proceed after structured reasons (T034).
- Documentation tasks (T039-T041) parallel with later test tasks (T042-T043).

## Independent Test Criteria Summary
- US1: 9x9 generation speed & no fallback.
- US2: Path diversity across seeds.
- US3: Partial acceptance threshold behavior.

## Suggested MVP Scope
Implement US1 only (T001–T020) to achieve fast, deterministic path generation.

