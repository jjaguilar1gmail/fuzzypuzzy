---

description: "Task list for fixing v2/v3 solvers to solve canonical 5x5"
---

# Tasks: Fix v2/v3 solvers for 5x5 deterministic

**Input**: Design documents from `/specs/001-fix-v2-v3-solvers/`  
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

**Tests**: Included where valuable (regressions and perf checks).

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Ensure scaffolding and fixtures exist for independent testing

- [x] T001 Ensure feature branch is checked out (001-fix-v2-v3-solvers)
- [x] T002 [P] Add canonical 5x5 deterministic fixture in tests/integration/fixtures/canonical_5x5.json
- [x] T003 [P] Add test utility for timing/node metrics in tests/util/perf_utils.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core solver infrastructure needed by all stories

- [x] T004 Introduce logic fixpoint function signature in solve/solver.py (apply_logic_fixpoint(state) -> (progress, solved))
- [x] T005 [P] Ensure public solve() does not mutate caller Puzzle; confirm internal search uses copies in solve/solver.py
- [x] T006 [P] Add deterministic tie-breaking helpers (row,col; value asc) in util/ordering.py
- [x] T007 Wire trace recording interface for pruning reasons in solve/solver.py

**Checkpoint**: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Logic-only pruning improvements (Priority: P1) 🎯 MVP

**Goal**: logic_v2 reaches a fixpoint, performs at least one elimination (corridor/degree) on canonical 5x5, may stop with "no more logical moves".

**Independent Test**: Running logic_v2 on canonical 5x5 yields zero backtracking, ≥1 elimination by corridor or degree, fixpoint within ≤2 passes, runtime ≤250 ms.

### Tests for User Story 1 (targeted regressions)

- [x] T008 [P] [US1] Add unit test for degree pruning thresholds in tests/unit/test_degree_pruning.py
- [x] T009 [P] [US1] Add unit test for corridor distance-sum inequality in tests/unit/test_corridor_bfs.py
- [x] T010 [P] [US1] Add unit test for minimal region capacity in tests/unit/test_region_capacity.py
- [ ] T011 [US1] Add integration test for v2 fixpoint behavior on canonical 5x5 in tests/integration/test_v2_fixpoint.py

### Implementation for User Story 1

- [x] T012 [P] [US1] Create corridor helper (distance-sum, dual BFS) in solve/corridor.py
- [x] T013 [P] [US1] Implement corridor cache lifecycle (invalidate on placement; set clean after compute) in solve/corridor.py
- [x] T014 [P] [US1] Create degree helper (empty-neighbor count) in solve/degree.py
- [ ] T015 [P] [US1] Implement region capacity (coarse connected components) in solve/region.py
- [ ] T016 [US1] Integrate corridor pruning into logic_v2 fixpoint in solve/solver.py
- [ ] T017 [US1] Integrate degree pruning into logic_v2 fixpoint in solve/solver.py
- [ ] T018 [US1] Integrate region capacity pruning into logic_v2 fixpoint in solve/solver.py
- [ ] T019 [US1] Record pruning reasons (strategy, positions, counts) into trace in solve/solver.py
- [ ] T020 [US1] Ensure v2 returns "no more logical moves" status when fixpoint reached without contradiction in solve/solver.py

**Checkpoint**: US1 independently delivers: logic-only pruning active, ≥1 elimination on canonical 5x5, clear trace.

---

## Phase 4: User Story 2 - v3 bounded search completion (Priority: P1)

**Goal**: logic_v3 solves canonical 5x5 in ≤100 ms, nodes ≤2,000, depth ≤25; deterministic across runs.

**Independent Test**: Run v3 on canonical 5x5; assert solved=true, timing and node/depth limits, repeatable results across 5 runs.

### Tests for User Story 2 (integration + perf)

- [ ] T021 [P] [US2] Add integration test for v3 solve with strict limits in tests/integration/test_v3_solve_canonical.py
- [ ] T022 [P] [US2] Add repeatability test (5 runs same solution/metrics) in tests/integration/test_v3_repeatability.py

### Implementation for User Story 2

- [ ] T023 [P] [US2] Apply v2 fixpoint in-place at each node (without deep-copying away progress) in solve/solver.py
- [ ] T024 [P] [US2] Switch MRV to operate on values (min |value_to_positions|) in solve/solver.py
- [ ] T025 [P] [US2] Implement LCV/frontier ordering for positions of chosen value in solve/solver.py
- [ ] T026 [US2] Add optional tiny transposition table with deterministic key in solve/transposition.py
- [ ] T027 [US2] Integrate transposition lookup/store into search loop in solve/solver.py
- [ ] T028 [US2] Ensure deterministic tie-breaking on equal candidates (row,col; value asc) in solve/solver.py
- [ ] T029 [US2] Record search decisions in trace (value choice, ordering, node count) in solve/solver.py

**Checkpoint**: US2 independently delivers: fast, deterministic v3 solve with metrics and trace.

---

## Phase 5: User Story 3 - Transparent trace and validation (Priority: P2)

**Goal**: concise step-by-step trace and final validator PASS output.

**Independent Test**: Enabling trace prints strategy labels and counts; final validator reports PASS (givens preserved, contiguous 1..25).

### Tests for User Story 3

- [ ] T030 [P] [US3] Add trace formatting test for pruning and search steps in tests/unit/test_trace_format.py
- [ ] T031 [P] [US3] Add final validator report test in tests/integration/test_validator_report.py

### Implementation for User Story 3

- [ ] T032 [P] [US3] Add concise trace formatting utilities in util/trace.py
- [ ] T033 [US3] Wire final validation summary (givens preserved, 1..N contiguous) into solve/solver.py
- [ ] T034 [US3] Add CLI/demo flag to enable tracing (limit 200 lines) in app/hidato.py

**Checkpoint**: US3 independently delivers: actionable tracing and validator PASS.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [ ] T035 [P] Documentation updates for README.md and specs/001-fix-v2-v3-solvers/quickstart.md
- [ ] T036 Code cleanup and small refactors in solve/ and util/
- [ ] T037 [P] Add additional unit tests for edge cases in tests/unit/
- [ ] T038 Performance tuning if needed (guardrails maintained) across solve/solver.py
- [ ] T039 [P] Run quickstart.md validation

---

## Dependencies & Execution Order

### Phase Dependencies
- Setup (Phase 1): No deps
- Foundational (Phase 2): Depends on Setup; BLOCKS US1–US3
- US1 (Phase 3): Depends on Foundational
- US2 (Phase 4): Depends on Foundational and US1 pruning helpers integrated (T012–T019)
- US3 (Phase 5): Depends on Foundational; can run in parallel with late US2 once trace hooks exist
- Polish (Phase 6): After desired stories complete

### User Story Dependencies
- US1 (P1): Independent after Foundational
- US2 (P1): Depends on US1 (uses v2 fixpoint and pruning at each node)
- US3 (P2): Independent after Foundational (tracing builds on hooks from Foundational)

### Parallel Opportunities
- Setup: T002, T003 in parallel
- Foundational: T005, T006 in parallel
- US1: T012–T015 in parallel; tests T008–T010 in parallel
- US2: T023–T025 in parallel; tests T021–T022 in parallel
- US3: T030, T031, T032 in parallel
- Polish: T035, T037, T039 in parallel

---

## Parallel Example: User Story 1

```bash
# Parallelizable tasks for US1
Task: T012 Create corridor helper (solve/corridor.py)
Task: T014 Create degree helper (solve/degree.py)
Task: T015 Implement region capacity (solve/region.py)
# In parallel, write tests:
Task: T008 Unit test degree pruning (tests/unit/test_degree_pruning.py)
Task: T009 Unit test corridor inequality (tests/unit/test_corridor_bfs.py)
Task: T010 Unit test region capacity (tests/unit/test_region_capacity.py)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)
1. Complete Setup (Phase 1)
2. Complete Foundational (Phase 2)
3. Complete US1 (Phase 3)
4. STOP and VALIDATE: v2 shows ≥1 elimination and clear fixpoint status on canonical 5x5

### Incremental Delivery
1. Setup + Foundational → US1 (MVP)
2. Add US2 → deterministic fast solve
3. Add US3 → tracing and validator report polish

---

## Format Validation
- All tasks use checklist format: `- [ ] T### [P?] [US?] Description with file path`
- Story labels only present for user story phases (US1/US2/US3)
- Parallelizable tasks correctly marked [P]
- File paths point to actual repository structure (core/, solve/, util/, tests/, app/)
