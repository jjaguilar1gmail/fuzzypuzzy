# Tasks: Anti-Branch Uniqueness & Size-Aware Clue Distribution

## Phase 1: Setup

- [x] T001 Create feature scaffolding directories per plan in specs/001-anti-branch-uniqueness/
- [x] T002 Add new Python modules stubs solve/uniqueness_probe.py, generate/spacing.py, generate/anchors_policy.py, util/logging_uniqueness.py
- [x] T003 Wire CLI flags for anti-branch probe in app/packgen/cli.py (--enable-anti-branch flag added)

## Phase 2: Foundational

- [x] T004 Implement SizeTierPolicy config defaults and loader in util/logging_uniqueness.py
- [x] T005 Implement line-delimited JSON logger (UniquenessLogger class) in util/logging_uniqueness.py
- [x] T006 Define data classes for ProbeOutcome, RemovalAttemptLog, UniquenessProbeConfig in solve/uniqueness_probe.py
- [x] T007 Add spacing metrics helpers (avg_manhattan_distance, quadrant_variance, detect_clusters, spacing_score) in generate/spacing.py

## Phase 3: [US1] Prevent False Uniqueness (P1)

- [x] T008 [US1] Integrate logic fixpoint pre-check entry in solve/uniqueness_probe.py
- [x] T009 [US1] Implement anti-branch DFS with early-exit at 2 solutions in solve/uniqueness_probe.py (leverages existing Solver.count_solutions)
- [x] T010 [P] [US1] Implement tie-break shuffling (MRV/LCV/frontier) and permutation tracking in solve/uniqueness_probe.py
- [x] T011 [US1] Run 2–3 probes based on size tier; aggregate outcomes and classification in solve/uniqueness_probe.py
- [x] T012 [US1] Add extended attempt (+50% budgets) for UNKNOWN/TIMEOUT when fallback disabled in solve/uniqueness_probe.py
- [x] T013 [US1] Emit per-probe and summary telemetry records via optional logger parameter in solve/uniqueness_probe.py
- [x] T014 [US1] Enforce removal acceptance policy in generate/generator.py (accept only if all probes EXHAUST)
- [x] T015 [US1] Restrict metrics collection to path modes {backbite_v1, random_v2} per spec FR-010 in generate/generator.py (retain general compatibility)

## Phase 4: [US2] Reduce Clue Clustering (P2)

- [ ] T016 [US2] Implement size/difficulty anchor policy in generate/anchors_policy.py (endpoints always; Easy spaced turns; Medium at most one soft turn; Hard endpoints only + repair)
- [ ] T017 [US2] Implement dynamic density floors by size & difficulty in generate/generator.py
- [ ] T018 [US2] Add spacing score term to removal candidate scorer in generate/spacing.py and integrate in generate/generator.py
- [ ] T019 [US2] Implement de-chunk pass post-target-density with uniqueness probe re-check in generate/generator.py

## Phase 5: [US3] Actionable Logging & Metrics (P3)

- [ ] T020 [US3] Record per (mode,size,difficulty) rollup: accepted/reverted removals, probe outcomes, final density, spacing metrics, solve stats in util/logging_uniqueness.py
- [ ] T021 [US3] Emit final summary JSON block at end of generation in util/logging_uniqueness.py

## Final Phase: Polish & Cross-Cutting

- [ ] T022 Add configuration docs updates in specs/001-anti-branch-uniqueness/quickstart.md
- [ ] T023 Add property/contract tests for probe classification and spacing metrics in tests/ (placeholders if test suite exists)
- [ ] T024 Add seeds/examples to benchmarks/ for before/after comparison
- [ ] T025 Update README.md with brief feature summary and flags

## Dependencies

- US1 → US2 → US3 (US1 must be done first; US2 depends on probe; US3 aggregates telemetry across both)

## Parallel Execution Examples

- [P] T010 (tie-break shuffle) can be built in parallel with T009 (DFS core) if contracts agreed.
- [P] T007 (spacing helpers) can proceed in parallel with T006 (dataclasses) and T004 (config defaults).
- [P] T020 (summary rollup) can proceed after T013 emits telemetry schema.

## Implementation Strategy

- MVP = Phase 3 (US1) only: anti-branch uniqueness probes integrated with acceptance policy. Then layer US2 spacing/de-chunk and US3 telemetry rollups.
