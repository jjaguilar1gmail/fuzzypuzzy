---

description: "Task list for Advanced Solver Modes (Logic v1, v2, v3)"
---

# Tasks: Advanced Solver Modes (Logic v1, v2, v3)

**Input**: Design documents from `/specs/001-advanced-solvers/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Included where mandated by spec (FR-012). Additional tests optional.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Prepare fixtures and config knobs to support independent testing per story

- [ ] T001 [P] Create test fixture directories `tests/fixtures/puzzles/v1/`, `tests/fixtures/puzzles/v2/`, `tests/fixtures/puzzles/v3/`
- [ ] T002 [P] Add seed list file for reproducible sets `tests/fixtures/seeds_advanced.json`
- [ ] T003 [P] Document config knobs and modes in `specs/001-advanced-solvers/quickstart.md` (ensure examples include REPL `solve --mode` and `hint --mode`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure required by all stories (candidate model, regions, wiring)

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [ ] T004 Create CandidateModel with bidirectional maps in `solve/candidates.py` (value→positions, pos→values; init_from, assign, remove)
- [ ] T005 [P] Add Region segmentation with 4/8-way support and incremental cache in `solve/regions.py` (APIs: build_regions(puzzle), update_on_assign(...))
- [ ] T006 [P] Implement Corridor feasibility (segment bridging helpers) in `solve/corridors.py` (APIs: corridors_between(puzzle, a, b))
- [ ] T007 [P] Implement DegreeIndex in `solve/degree.py` (APIs: build_degree_index(puzzle), update_on_assign(...))
- [ ] T008 Wire new modes in `solve/solver.py`: add `logic_v1`, `logic_v2`, `logic_v3` dispatch in `Solver.solve(...)`; add config knobs and tie_break=row_col
- [ ] T009 Update REPL to accept and pass modes/config in `app/api.py` (commands: `solve --mode`, `hint --mode`)
- [ ] T010 Ensure profiling hooks are usable around solver calls in `util/profiling.py` consumers (no solver internal prints)

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Solve with Enhanced Pure Logic (Logic v1) (Priority: P1) 🎯 MVP

**Goal**: Deterministic solve using two-ended propagation + uniqueness + early contradictions; no guessing

**Independent Test**: On a curated v1 fixture unsolved by `logic_v0`, `solve --mode logic_v1` returns solved=True with only logical steps

### Tests for User Story 1 (Required by FR-012)

- [ ] T011 [P] [US1] Add v1 fixture puzzles and expected assertions in `tests/solvers/test_logic_v1.py`
- [ ] T012 [P] [US1] Test hint mode routing for v1 in `tests/solvers/test_hint_modes.py`

### Implementation for User Story 1

- [ ] T013 [US1] Implement two-ended propagation using `CandidateModel` in `solve/solver.py` (frontiers from k±1; forced placements)
- [ ] T014 [US1] Add global uniqueness checks (value has single position; cell has single candidate) in `solve/solver.py`
- [ ] T015 [US1] Implement early contradiction checks (k placed but neighbors can't host k±1) in `solve/solver.py`
- [ ] T016 [US1] Add config knobs: `max_logic_passes`, `tie_break` in `solve/solver.py`; ensure deterministic placement when ties
- [ ] T017 [US1] Update `Solver.get_hint` to accept `mode` and return one logical v1 step without mutating state in `solve/solver.py`

**Checkpoint**: User Story 1 independently functional and testable

---

## Phase 4: User Story 2 - Shape/Region Aware Logic (Logic v2) (Priority: P2)

**Goal**: Deterministic region/shape reasoning: island elimination, segment bridging corridors, degree pruning; optional edge nudges

**Independent Test**: On a curated v2 fixture, region/degree/corridor logic forces at least one placement that v1 cannot make

### Tests for User Story 2 (Required by FR-012)

- [ ] T018 [P] [US2] Add island elimination and corridor fixtures/tests in `tests/solvers/test_logic_v2.py`
- [ ] T019 [P] [US2] Add degree pruning and adjacency-4/8 cases in `tests/solvers/test_logic_v2.py`

### Implementation for User Story 2

- [ ] T020 [US2] Integrate island elimination via `solve/regions.py` into `solve/solver.py` (prune candidates outside viable regions)
- [ ] T021 [US2] Integrate segment bridging: filter candidates to `CorridorMap` cells in `solve/solver.py`
- [ ] T022 [US2] Integrate `DegreeIndex` pruning for mid-sequence cells in `solve/solver.py`
- [ ] T023 [US2] Add optional edge/turn nudges (only when logically forced) in `solve/solver.py`
- [ ] T024 [US2] Add config toggles: `enable_island_elim`, `enable_segment_bridging`, `enable_degree_prune` in `solve/solver.py` and `app/api.py`
- [ ] T025 [US2] Ensure trace reasons include structural explanations (e.g., island sizes, corridor evidence) in `solve/solver.py`

**Checkpoint**: User Stories 1 AND 2 work independently

---

## Phase 5: User Story 3 - Hybrid Logic + Bounded Smart Search (Logic v3) (Priority: P3)

**Goal**: Bounded MRV/LCV/frontier-biased backtracking with budgets/timeouts; logic fixpoint before/after guesses; telemetry

**Independent Test**: On a curated v3 fixture unsolved by v2, `logic_v3` finds solution within default budgets and reports stats

### Tests for User Story 3 (Required by FR-012)

- [ ] T026 [P] [US3] Add v3 fixtures and tests for budgets/timeouts/limits in `tests/solvers/test_logic_v3.py`
- [ ] T027 [P] [US3] Add reproducibility test (trace hash stable across runs) in `tests/solvers/test_logic_v3.py`

### Implementation for User Story 3

- [ ] T028 [US3] Implement MRV/LCV/frontier ordering and bounded search loop in `solve/search.py`; integrate with `Solver`
- [ ] T029 [US3] Add optional transposition table with Zobrist-like hashing in `solve/search.py`
- [ ] T030 [US3] Enforce budgets: `max_nodes`, `max_depth`, `timeout_ms` and graceful termination in `solve/search.py`
- [ ] T031 [US3] Ensure v0–v2 logic runs to fixpoint pre/post guess; integrate contradictions early in `solve/solver.py`
- [ ] T032 [US3] Emit telemetry/stats (nodes, max_depth, elapsed_ms, logic_steps) in `solve/solver.py` result message

**Checkpoint**: All user stories independently functional

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Docs, performance, and UX

- [ ] T033 [P] Update CLI/REPL help and README with new modes and examples in `README.md` and `app/api.py`
- [ ] T034 Code cleanup: deterministic iteration/tie-breaks; remove dead code in `solve/` modules
- [ ] T035 [P] Performance sampling records added to PR (measurements vs SC-001..SC-010) in `specs/001-advanced-solvers/quickstart.md`
- [ ] T036 [P] Add additional unit tests for edge cases (invalid modes, no logical moves) in `tests/solvers/test_edges.py`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies - can start immediately
- Foundational (Phase 2): Depends on Setup completion - BLOCKS all user stories
- User Stories (Phase 3+): All depend on Foundational completion
  - Stories can proceed in parallel (if staffed)
  - Or sequentially in priority order (P1 → P2 → P3)
- Polish (Phase 6): Depends on all desired user stories being complete

### User Story Dependencies

- User Story 1 (P1): Starts after Foundational; independent
- User Story 2 (P2): Starts after Foundational; independent of US1 for tests but integrates shared infra
- User Story 3 (P3): Starts after Foundational; independent test corpus

### Within Each User Story

- Tests (required by FR-012) should be authored and verified to fail before implementation
- Implement core logic, then integrate with REPL and telemetry
- Ensure deterministic ordering to satisfy constitution

### Parallel Opportunities

- Phase 1 tasks T001–T003 can run in parallel
- Phase 2 tasks T005–T007 can run in parallel
- Within stories: tests (marked [P]) can be developed in parallel; different helper modules can be implemented in parallel as marked [P]

---

## Parallel Example: User Story 1

```powershell
# Parallelizable tasks for US1
# Tests (in parallel)
#   - T011 Add v1 fixture tests
#   - T012 Test hint mode routing
# Implementation
#   - T013 Implement two-ended propagation
#   - T014 Add uniqueness checks
#   - T015 Add early contradictions
#   - T016 Add config knobs & tie-break
#   - T017 Update get_hint for mode
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL)
3. Complete Phase 3: User Story 1 (logic_v1)
4. STOP and VALIDATE: Run tests for US1 and measure basic performance
5. Demo/commit as MVP

### Incremental Delivery

1. Foundation ready → Deliver US1 (deterministic solves)
2. Deliver US2 (shape/region reasoning), test independently
3. Deliver US3 (bounded search), test independently with budgets

### Parallel Team Strategy

- Dev A: v1 implementation + tests
- Dev B: Regions/corridors/degree infra + v2 integration
- Dev C: v3 search + telemetry

---

## Validation

- All tasks adhere to required checklist format with IDs, [P] markers where parallel, and [US?] for user-story tasks
- Paths are absolute within repo structure (no ambiguous locations)
- Each user story has independent test criteria and can be demonstrated standalone
