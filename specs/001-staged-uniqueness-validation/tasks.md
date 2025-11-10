# Tasks: Staged Uniqueness Validation

## Phase 1: Setup

- [ ] T001 Ensure feature branch active (001-staged-uniqueness-validation)
- [ ] T002 Create package skeleton at src/generate/uniqueness_staged/__init__.py
- [ ] T003 Create config module at src/generate/uniqueness_staged/config.py
- [ ] T004 Create result dataclasses at src/generate/uniqueness_staged/result.py
- [ ] T005 Create registry at src/generate/uniqueness_staged/registry.py

## Phase 2: Foundational

- [ ] T006 Wire request/validation models in src/generate/uniqueness_staged/result.py
- [ ] T007 Add public entrypoint check_uniqueness in src/generate/uniqueness_staged/__init__.py
- [ ] T008 Add SAT hook interface in src/generate/uniqueness_staged/sat_hook.py
- [ ] T009 Integrate staged checker behind generate/pruning.py uniqueness call path
- [ ] T010 [P] Add metrics aggregation helper in src/generate/uniqueness_staged/result.py

## Phase 3: User Story 1 (P1) — Fast, bounded uniqueness checks

- [ ] T011 [US1] Implement early_exit stage orchestrator in src/generate/uniqueness_staged/early_exit.py
- [ ] T012 [P] [US1] Implement heuristic profiles (position/value orders) in src/generate/uniqueness_staged/registry.py
- [ ] T013 [US1] Reuse solver logic passes before branching in src/generate/uniqueness_staged/early_exit.py
- [ ] T014 [US1] Enforce solution_cap=2 and time cap per run in src/generate/uniqueness_staged/early_exit.py
- [ ] T015 [US1] Return Non-Unique immediately on second solution in src/generate/uniqueness_staged/early_exit.py
- [ ] T016 [US1] Respect total budget and record per-stage ms in src/generate/uniqueness_staged/__init__.py
- [ ] T017 [US1] Add independent test criteria doc in specs/001-staged-uniqueness-validation/quickstart.md

## Phase 4: User Story 2 (P2) — Configurable strategy & budgets

- [ ] T018 [US2] Implement config parsing (stage enable flags, budget split) in src/generate/uniqueness_staged/config.py
- [ ] T019 [P] [US2] Add programmatic API to enable/disable stages in src/generate/uniqueness_staged/__init__.py
- [ ] T020 [US2] Validate totals and defaults per difficulty in src/generate/uniqueness_staged/config.py
- [ ] T021 [US2] Ensure pruning uses tri-state decision and honors budgets in generate/pruning.py

## Phase 5: User Story 3 (P3) — Deterministic, seedable probes

- [ ] T022 [US3] Implement randomized probes orchestrator in src/generate/uniqueness_staged/probes.py
- [ ] T023 [P] [US3] Add seeded RNG and deterministic ordering in src/generate/uniqueness_staged/probes.py
- [ ] T024 [US3] Provide list_profiles() with stable ordering in src/generate/uniqueness_staged/registry.py

## Phase 6: Optional SAT/CP hook

- [ ] T025 Add SolverInterface and registration in src/generate/uniqueness_staged/sat_hook.py
- [ ] T026 Implement one-solution + blocking-clause flow (interface only) in src/generate/uniqueness_staged/sat_hook.py
- [ ] T027 Skip SAT stage silently if no solver registered in src/generate/uniqueness_staged/__init__.py

## Final Phase: Polish & Cross-Cutting

- [ ] T028 Add metrics logging (per-stage ms, nodes, probes) in src/generate/uniqueness_staged/__init__.py
- [ ] T029 Document configuration and defaults in specs/001-staged-uniqueness-validation/quickstart.md
- [ ] T030 Ensure no mutation of caller puzzles in all stages (audit) across src/generate/uniqueness_staged/*

## Dependencies

- US1 → US2 → US3 (in that order). SAT/CP hook independent of US3 but runs after US1 integration.

## Parallel Opportunities

- T012 and T013 can proceed in parallel (separate files).
- T018 and T020 can proceed in parallel.
- T022 and T024 can proceed in parallel.

## MVP Scope

- Complete Phase 3 (US1) to ship a fast Non-Unique detector under budget with tri-state output.
