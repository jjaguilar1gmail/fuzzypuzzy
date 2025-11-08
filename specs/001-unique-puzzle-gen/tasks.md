---

description: "Task list for feature implementation"
---

# Tasks: Uniqueness-Preserving Puzzle Generator

**Input**: Design documents from `/specs/001-unique-puzzle-gen/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

**Tests**: Tests are OPTIONAL per spec. This plan focuses on implementation tasks; independent test criteria are listed for each user story.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- Single project layout with top-level packages: `core/`, `solve/`, `generate/`, `io/`, `util/`, CLI script `hidato.py` at repo root

---

## Phase 1: Setup (Shared Infrastructure)

Purpose: Ensure minimal scaffolding to start implementation without blocking.

- [ ] T001 Create new module for uniqueness checks in generate/uniqueness.py
- [ ] T002 Create new module for difficulty metrics and band mapping in generate/difficulty.py
- [ ] T003 [P] Add CLI flag stubs for generator options in hidato.py (--generate, --size, --difficulty, --seed, --allow-diagonal, --blocked, --percent-fill, --symmetry, --trace)

---

## Phase 2: Foundational (Blocking Prerequisites)

Purpose: Core structures and scaffolds that MUST be complete before user stories.

- [ ] T004 Create dataclasses for GeneratedPuzzle, GenerationConfig, UniquenessCheckResult, DifficultyProfile in generate/models.py
- [ ] T005 [P] Extend generate/path_builder.py to support mode="random_walk" (seeded) and honor blocked cells
- [ ] T006 [P] Extend generate/clue_placer.py to support anchor-based seeding (values 1, N, turn-anchors) and symmetry hooks (rotational|horizontal|none)
- [ ] T007 Create removal scoring helper with contract score_candidates(givens, path, anchors, grid) in generate/removal.py
- [ ] T008 Define difficulty profiles (bands) constants in generate/difficulty.py (easy, medium, hard, extreme)
- [ ] T009 Update generate/generator.py public API to generate_puzzle(size, difficulty=None, percent_fill=None, seed=None, allow_diagonal=True, blocked=None, path_mode='serpentine', clue_mode='anchor_removal_v1', symmetry=None, turn_anchors=True, timeout_ms=5000, max_attempts=5)

Checkpoint: Foundation ready — user story implementation can now begin in parallel.

---

## Phase 3: User Story 1 - Generate Valid Unique Puzzle (Priority: P1) 🎯 MVP

Goal: Generate a puzzle that is solvable by the existing solver and has exactly one solution; return metadata.

Independent Test: Call generator with parameters; verify solver solves (solved=True) and uniqueness check finds exactly one solution.

### Implementation for User Story 1

- [ ] T010 [US1] Implement count_solutions(cap=2, node_cap, timeout_ms) using solve/solver.py in generate/uniqueness.py (early-abort on second solution)
- [ ] T011 [P] [US1] Implement removal loop in generate/generator.py using generate/removal.py scoring; preserve anchors; enforce clue lower bound per band
- [ ] T012 [P] [US1] Wire blocked cell handling end-to-end in generate/generator.py and generate/path_builder.py; ensure uniqueness checks skip blocked
- [ ] T013 [US1] Finalize metadata assembly (seed, path_mode, clue_mode, attempts_used, timings_ms, solver_metrics) in generate/generator.py per data-model
- [ ] T014 [US1] Implement CLI flow in hidato.py invoking Generator with parsed args; print structured summary (size, difficulty, clue_count, uniqueness_verified)
- [ ] T015 [US1] Parse --blocked as list of r,c pairs in hidato.py and thread into generator.generate_puzzle()
- [ ] T016 [US1] Add final validation step to re-solve returned puzzle via solve/solver.py and assert solved before returning

Checkpoint: US1 complete — unique and solvable puzzles can be generated deterministically by seed.

---

## Phase 4: User Story 2 - Difficulty Tuning & Bands (Priority: P2)

Goal: Allow requests for difficulty bands and enforce band criteria; report assessed difficulty.

Independent Test: Generate N puzzles per band; validate each puzzle meets defined band constraints (clue density, max search depth, node caps).

### Implementation for User Story 2

- [ ] T017 [US2] Compute metrics from solver trace (clue_density, logic_ratio, nodes, depth, strategy_hits) in generate/difficulty.py
- [ ] T018 [P] [US2] Map metrics to band label and difficulty_score in generate/difficulty.py
- [ ] T019 [US2] Integrate difficulty enforcement into removal loop/post-check in generate/generator.py (retry or adjust removals to hit band)
- [ ] T020 [US2] Implement clear error for unsupported difficulty in generate/generator.py (enumerate valid labels)
- [ ] T021 [US2] Update CLI output in hidato.py to include assessed difficulty and key metrics

Checkpoint: US2 complete — band targeting works and assessments are reported.

---

## Phase 5: User Story 3 - Deterministic Reproducibility (Priority: P3)

Goal: Identical inputs (including seed) produce identical outputs (clue layout and values) and metadata logs capture reproducibility context.

Independent Test: Generate twice with same parameters and seed; assert serialized puzzle states (givens set and metadata) are identical; different seeds differ.

### Implementation for User Story 3

- [ ] T022 [US3] Ensure single util/rng.RNG instance is passed through generate/generator.py, generate/path_builder.py, generate/clue_placer.py, generate/removal.py
- [ ] T023 [P] [US3] Implement deterministic serialization of givens (sorted by row,col then value) in generate/models.py (helper to_json())
- [ ] T024 [US3] Record reproducibility metadata (seed, path_mode, clue_mode, symmetry) in consistent key order in generate/generator.py
- [ ] T025 [US3] Update hidato.py to echo final seed and params; add --print-seed option

Checkpoint: US3 complete — reproducible by seed; stable serialization for fixtures.

---

## Phase N: Polish & Cross-Cutting Concerns

Purpose: Documentation and non-functional improvements.

- [ ] T026 [P] Update specs/001-unique-puzzle-gen/quickstart.md examples to match final CLI flags and outputs
- [ ] T027 Update README.md with generator usage section and examples
- [ ] T028 Add optional generation benchmark helper at scripts/bench_generate.py (measure P95 by band; standard library only)
- [ ] T029 [P] Add --trace flag handling in hidato.py and summarized trace logging in generate/generator.py
- [ ] T030 Run ruff and basic pytest to validate no regressions across existing modules

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies — can start immediately
- Foundational (Phase 2): Depends on Setup completion — BLOCKS all user stories
- User Stories (Phase 3+): Depend on Foundational; then proceed in priority order (P1 → P2 → P3) or in parallel if staffed
- Polish (Final Phase): Depends on desired user stories being complete

### User Story Dependencies

- User Story 1 (P1): Starts after Foundational — no dependency on other stories
- User Story 2 (P2): Starts after US1 core if enforcing bands uses US1 metrics; otherwise can begin in parallel after foundational
- User Story 3 (P3): Can start after Foundational; may integrate with US1/US2 but remains independently testable

### Within Each User Story

- Models/helpers before pipeline orchestration
- Orchestration before CLI integration
- Validation before reporting
- Story complete before moving to next priority

### Parallel Opportunities

- Setup: T003
- Foundational: T005, T006, T007, T008 in parallel (different files)
- US1: T011 and T012 can proceed in parallel; T014 and T015 can proceed in parallel
- US2: T018 can proceed in parallel with T017; T021 independent once T019 is wired
- US3: T023 can proceed in parallel with T022
- Polish: T026 and T029 can run in parallel

---

## Parallel Example: User Story 1

Tasks that can start together:

- T011 [P] [US1] Implement removal loop in generate/generator.py
- T012 [P] [US1] Wire blocked cell handling in generate/generator.py and generate/path_builder.py
- T014 [US1] Implement CLI flow in hidato.py
- T015 [US1] Parse --blocked in hidato.py

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. STOP and VALIDATE: Manually verify US1 independent test criteria via CLI
5. Demo/ship MVP

### Incremental Delivery

1. Setup + Foundational → foundation ready
2. Add User Story 1 → validate independently → demo
3. Add User Story 2 → validate independently → demo
4. Add User Story 3 → validate independently → demo

---

## Story Test Criteria (independent)

- US1: Solver returns solved=True; uniqueness count_solutions returns exactly 1; anchors (1 and N) present; blocked cells (if provided) respected.
- US2: Puzzle metrics fall within requested band thresholds (clue density, nodes, depth); unsupported difficulty yields clear error list.
- US3: Same seed + params → identical serialized givens and metadata; different seeds → differ in at least one clue position; reported seed logged.

---

## Format Validation

All tasks follow required checklist format: "- [ ] T### [P?] [US#?] Description with file path". Setup and Foundational phases contain no story labels; User Story phases include [US#] labels where required.
