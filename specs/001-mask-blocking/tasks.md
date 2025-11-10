# Tasks: Mask-Driven Blocking & Ambiguity-Aware Repair

**Input**: Design documents from `specs/001-mask-blocking/`
**Prerequisites**: `plan.md`, `spec.md`, `research.md`, `data-model.md`, `contracts/`

## Phase 1: Setup (Shared Infrastructure)
**Purpose**: Establish directories, config flags, baseline scaffolding.

- [x] T001 Create feature directories `generate/mask/` and `generate/repair/` (empty `__init__.py` files)
- [x] T002 Add mask & repair config flags to `generate/models.py` (`GenerationConfig`): `mask_enabled`, `mask_mode`, `mask_template`, `mask_density`, `mask_max_attempts`, `structural_repair_enabled`, `structural_repair_max`, `structural_repair_timeout_ms`
- [x] T003 [P] Define placeholder error classes in `generate/mask/errors.py` (`InvalidMaskError`, `MaskDensityExceeded`)
- [x] T004 [P] Define placeholder error classes in `generate/repair/errors.py` (`StructuralRepairExhausted`)
- [x] T005 Add seed/logging extension points (no-op) in `generate/generator.py` for future mask metrics fields

---
## Phase 2: Foundational (Blocking Prerequisites)
**Purpose**: Core entities & validation utilities required before any story logic.

- [x] T006 Implement `BlockMask` & `MaskPattern` dataclasses in `generate/mask/models.py`
- [x] T007 [P] Implement `AmbiguityRegion` & `RepairAction` dataclasses in `generate/repair/models.py`
- [x] T008 Implement mask validation (connectivity + orphan pockets + density) in `generate/mask/validate.py`
- [x] T009 [P] Add reproducible RNG helper for mask generation in `generate/mask/rng.py`
- [x] T010 Integrate optional mask acceptance & application stub into `generate/generator.py` (pre-path build hook)
- [x] T011 Modify uniqueness staged transposition key to include mask signature in `generate/uniqueness_staged/__init__.py`
- [x] T012 [P] Add metrics structure extensions (`GenerationMetrics` fields) in `generate/mask/metrics.py`
- [x] T013 Add structural repair budget enforcement hook (stub) in `generate/pruning.py`
- [x] T014 Create initial test skeleton `tests/test_foundation_mask_config.py` verifying new config flags exist
- [x] T015 [P] Create initial test skeleton `tests/test_foundation_dataclasses.py` verifying core dataclasses instantiate

**Checkpoint**: Foundation complete; user stories can proceed.

---
## Phase 3: User Story 1 - Deterministic Mask Application (Priority: P1) 🎯 MVP
**Goal**: Deterministically generate & validate a small mask before path building to reduce branching and support fewer clues.
**Independent Test**: Compare generation with/without mask for 7x7 & 9x9 (branching factor ↓, clue count ↓, uniqueness preserved).

### Tests (US1)
- [x] T016 [P] [US1] Add mask pattern generation tests `tests/test_mask_patterns.py` (corridor, ring, spiral templates)
- [x] T017 [P] [US1] Add procedural mask sampling tests `tests/test_mask_procedural.py` (density bounds & reproducibility)
- [x] T018 [P] [US1] Add validation tests `tests/test_mask_validation.py` (connectivity, orphan pockets, start/end unblocked)
- [x] T019 [US1] Add integration test `tests/test_mask_integration_generation.py` (7x7 vs 9x9 baseline metrics)

### Implementation (US1)
- [x] T020 [P] [US1] Implement template pattern generators in `generate/mask/patterns.py` (corridor, ring, spiral, cross)
- [x] T021 [P] [US1] Implement procedural sampler in `generate/mask/procedural.py`
- [x] T022 [US1] Implement `build_mask` orchestrator in `generate/mask/__init__.py` (select template → fallback procedural → validate)
- [x] T023 [US1] Integrate mask application into `generate/generator.py` pre path with deterministic seed logic
- [x] T024 [P] [US1] Implement density heuristic & auto-disable logic in `generate/mask/density.py`
- [x] T025 [US1] Add mask metrics capture (pattern_id, cell_count, density, attempts) in `generate/mask/metrics.py`
- [x] T026 [US1] Update `GeneratedPuzzle` enrichment for mask metrics in `generate/models.py` (timings/solver_metrics extension)
- [x] T027 [P] [US1] Add branch factor measurement hook in `generate/path_builder.py`
- [ ] T028 [US1] Document usage in `specs/001-mask-blocking/quickstart.md` (already scaffolded; update with final flag names)

**Checkpoint**: US1 functional & testable independently (MVP deliverable).

---
## Phase 4: User Story 2 - Ambiguity-Aware Structural Repair (Priority: P2)
**Goal**: Detect multi-solution ambiguity and prefer a targeted structural block to restore uniqueness without increasing clues.
**Independent Test**: Force ambiguity; apply repair; uniqueness regained; clue count unchanged.

### Tests (US2)
- [ ] T029 [P] [US2] Add ambiguity region detection test `tests/test_ambiguity_detection.py`
- [ ] T030 [P] [US2] Add structural block candidate scoring test `tests/test_structural_block_scoring.py`
- [ ] T031 [US2] Add repair integration test `tests/test_structural_repair_integration.py` (block restores uniqueness)
- [ ] T032 [P] [US2] Add fallback clue repair test `tests/test_repair_fallback_clue.py`

### Implementation (US2)
- [ ] T033 [P] [US2] Implement solution diff & divergence clustering in `generate/repair/ambiguity.py`
- [ ] T034 [P] [US2] Implement block candidate scoring (frequency × corridor width × distance) in `generate/repair/structural_block.py`
- [ ] T035 [US2] Implement repair orchestrator (attempt ≤2 blocks then clue fallback) in `generate/repair/__init__.py`
- [ ] T036 [US2] Integrate repair flow into uniqueness failure path in `generate/pruning.py`
- [ ] T037 [P] [US2] Add solvability re-check hook in `generate/validator.py` for post-block insertion
- [ ] T038 [US2] Extend transposition table logic to account for repair attempts in `generate/uniqueness_staged/__init__.py`
- [ ] T039 [US2] Update metrics capture for repair actions in `generate/repair/metrics.py`

**Checkpoint**: US2 functional & independently testable (works whether or not US1 enabled).

---
## Phase 5: User Story 3 - Mask & Repair Metrics Observability (Priority: P3)
**Goal**: Provide structured metrics enabling performance/clue count/uniqueness impact analysis.
**Independent Test**: Batch generate 50 puzzles; aggregate metrics; verify required fields & sane ranges.

### Tests (US3)
- [ ] T040 [P] [US3] Add metrics emission test `tests/test_metrics_mask_fields.py`
- [ ] T041 [P] [US3] Add metrics emission test `tests/test_metrics_repair_fields.py`
- [ ] T042 [US3] Add batch benchmark harness `tests/test_benchmark_observability.py` (aggregate + assertions)

### Implementation (US3)
- [ ] T043 [P] [US3] Extend generation metrics aggregator `generate/generator.py` (branching_factor_before/after, ambiguity stats)
- [ ] T044 [US3] Implement metrics summary utility `generate/mask/summary.py` (aggregate across runs)
- [ ] T045 [P] [US3] Implement ambiguity repair summary utility `generate/repair/summary.py`
- [ ] T046 [US3] Add README metrics section in `README.md` (document new fields & usage example)
- [ ] T047 [US3] Update `specs/001-mask-blocking/UNIQUENESS-VERIFICATION.md` with metrics interpretation addendum

**Checkpoint**: US3 metrics independently verifiable; tuning possible.

---
## Phase 6: Polish & Cross-Cutting Concerns
**Purpose**: Cleanup, optimization, documentation, regression safety.

- [ ] T048 [P] Add performance micro-bench script `tests/test_perf_density_sweep.py`
- [ ] T049 Refactor duplicated connectivity code (mask vs repair) into `generate/mask/connectivity_shared.py`
- [ ] T050 [P] Add additional edge case tests `tests/test_edge_cases_masks.py` (small sizes, over-density auto-disable)
- [ ] T051 [P] Add additional edge case tests `tests/test_edge_cases_repair.py` (oscillation prevention, unsolvable rejection)
- [ ] T052 Optimize scoring hot path (precompute corridor widths) in `generate/repair/structural_block.py`
- [ ] T053 Security/readability audit heuristics in `generate/mask/readability.py`
- [ ] T054 [P] Update quickstart with final examples `specs/001-mask-blocking/quickstart.md`
- [ ] T055 Documentation polish in `docs/validation/PROOF_OF_PERFORMANCE.md` (add mask/repair impact section)
- [ ] T056 Final constitution compliance review notes in `specs/001-mask-blocking/plan.md` (append section)

---
## Dependencies & Execution Order

### Phase Dependencies
- Phase 1 → Phase 2 → (Phases 3,4,5 in priority order; 4 & 5 can start after 3 if independence maintained) → Phase 6
- US2 (ambiguity repair) depends on foundational + ability to generate puzzles (but can run without mask logic active).
- US3 (metrics) depends on metrics fields created in Foundational + story outputs from US1/US2.

### User Story Dependencies
- US1 independent after foundational (MVP)
- US2 independent after foundational (can parallel US1; integrates optionally with mask)
- US3 depends on data emitted by US1 and US2 (starts after their metric hooks in place)

### Parallel Opportunities
- Pattern vs procedural modules (T020, T021)
- Validation vs density heuristics (T018, T024)
- Ambiguity detection vs structural scoring (T033, T034)
- Metrics mask vs repair summaries (T044, T045)
- Edge case tests (T050, T051) in parallel

---
## Parallel Example: User Story 1
```
# Parallel implementation batch:
T020 generate/mask/patterns.py
T021 generate/mask/procedural.py
T024 generate/mask/density.py
T018 tests/test_mask_validation.py (can run after patterns/procedural outputs exist)
```

## Implementation Strategy
**MVP**: Complete US1 (mask generation & integration + tests) after foundational; deliver measurable branching + clue reduction.
**Incremental**: Add US2 (repair) to reduce clue regression; then US3 for observability & tuning; finalize with Polish phase.

## Task Counts Summary
- Setup: 5
- Foundational: 10
- US1: 13 (Tests 4, Impl 9)
- US2: 13 (Tests 4, Impl 9)
- US3: 11 (Tests 3, Impl 8)
- Polish: 9
- Total: 61

## MVP Scope
- Complete through T028 (US1 implementation & tests) for initial measurable value.

## Format Validation
All tasks follow required format: `- [ ] TaskID [P?] [USx?] Description with file path`. Story phases include `[US1]`, `[US2]`, `[US3]`; Setup/Foundational/Polish omit story label. Parallelizable tasks marked `[P]` where independent.

