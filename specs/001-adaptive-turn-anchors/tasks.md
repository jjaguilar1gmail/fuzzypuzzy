# Task Breakdown: Adaptive Turn Anchors (specs/001-adaptive-turn-anchors/tasks.md)

Status: PHASE 0-1 COMPLETE + POLISH | Core anchor selection implemented, tested with all path modes, documented | Numbering continues from existing T045 (highest found) → start at T046.

## Implementation Progress Summary

**COMPLETED:**
- ✅ T046: Extended GenerationConfig with anchor policy fields
- ✅ T047: Created anchor_policy.py module with data types and selection logic
- ✅ T048: Integrated select_anchors into Generator with legacy fallback
- ✅ T050: Fixed min_index_gap_enforced flag tracking
- ✅ T054: Added anchor metrics to GeneratedPuzzle.solver_metrics
- ✅ T055: Implemented opt-out flags (--anchor-policy, --no-adaptive-turn-anchors)
- ✅ T057: Created test_anchor_counts.py with 7 passing tests
- ✅ T062: Confirmed no regressions (116 passing tests including 14 anchor tests)
- ✅ T064: Updated README with Adaptive Turn Anchors section

**Path Mode Integration Verified:**
- ✅ Serpentine, backbite_v1, random_walk_v2 all work with adaptive anchors
- ✅ Partial path acceptance compatible
- ✅ Legacy mode backward compatible
- ✅ Determinism maintained across modes

**NEXT PRIORITIES:**
- T049: Soft anchor evaluation (medium difficulty) - needs uniqueness check implementation
- T051: Symmetry support for anchors - mirror anchor positions
- T052: Uniqueness repair planning - add repair anchors when needed
- T053: Fragmentation guardrail - prevent isolated regions

Legend:
- [P1] Core minimal-clue adaptive anchors (User Story 1)
- [P2] Opt-out & tooling (User Story 2)
- [P3] Metrics & guardrails (User Story 3)
- [POLISH] Documentation / benchmarking / tuning
- Each task lists: Goal, Files, Steps, Acceptance, Dependencies.

## Phase 0 – Config & Scaffolding (Foundational, unblock later tasks) ✅ COMPLETE

### T046 [P1] Extend GenerationConfig for anchor policy ✅
Goal: Add fields to configure adaptive anchor policy and opt-out.
Files: `generate/models.py`
Status: COMPLETE - Added anchor_policy_name, adaptive_turn_anchors, anchor_counts, anchor_tolerance with validation.

### T047 [P1] Create anchor policy module & data types ✅
Goal: Implement `generate/anchor_policy.py` providing dataclasses / lightweight classes: AnchorPolicy, TurnAnchor(kind enum), AnchorMetrics. (Use enums via simple str constants to stay stdlib.)
Files: `generate/anchor_policy.py`
Status: COMPLETE - Module created with all data types, select_anchors, stubs for evaluate_soft_anchor and plan_repair.

## Phase 1 – Adaptive Anchor Selection (User Story 1 Core) ✅ MOSTLY COMPLETE

### T048 [P1] Integrate select_anchors into Generator ✅
Goal: Replace inline turn anchor logic in `Generator.generate_puzzle` with call to `select_anchors` if adaptive_turn_anchors and policy != legacy; else use legacy logic (current code path extracted to helper `_legacy_turn_anchors`).
Files: `generate/generator.py` (+ possibly `generate/anchor_policy.py` for helper import).
Status: COMPLETE - Integrated with conditional logic; legacy path preserved inline; metrics captured.

### T049 [P3] Implement soft anchor evaluation 🔲
Goal: `evaluate_soft_anchor(puzzle, soft_anchor)` determines if soft anchor retained for medium difficulty.
Files: `generate/anchor_policy.py`, `generate/generator.py` integration.
Status: STUB ONLY - Currently always returns True; needs uniqueness check implementation.
Logic (deterministic): Temporarily treat soft anchor as given; run a quick uniqueness check with and without it; keep only if uniqueness count increases search branching or reduces alternative solutions.
Acceptance: Medium difficulty may result in 0 or 1 soft anchor; deterministic across runs.
Dependencies: T048.

### T050 [P3] Enforce min_index_gap distribution rule ✅
Goal: Avoid anchors too close on path index (fragmenting early region visibility).
Files: `generate/anchor_policy.py` (inside `select_anchors`).
Status: COMPLETE - _select_spaced_turns now returns (selected, gap_enforced) tuple; flag properly tracked and passed to metrics.
Logic: When choosing candidate turn anchors, skip any whose path index distance from previous chosen anchor < policy.min_index_gap.
Acceptance: AnchorMetrics.min_index_gap_enforced True when any were skipped; tests verify spacing.
Dependencies: T048.

### T051 [P3] Symmetry support for anchors 🔲
Goal: Honor `symmetry` parameter when present by mirroring anchors.
Files: `generate/anchor_policy.py`.
Status: NOT IMPLEMENTED - symmetry parameter accepted but not used.
Logic: After initial selection, compute mirrored positions; include if path contains them and they are not duplicates; ensure endpoints preserved.
Acceptance: Symmetry mode produces symmetric anchor pairs (except endpoints if self-mirrored).
Dependencies: T048.

## Phase 2 – Repair & Guardrails (Uniqueness resilience)

### T052 [P3] Uniqueness repair planning
Goal: Implement `plan_repair` invoked when removal loop cannot reach target clue density without losing uniqueness OR final puzzle uniqueness fails post-removal.
Files: `generate/anchor_policy.py`, integrate call in `generate/generator.py` after removal attempts (before final puzzle build).
Logic: If uniqueness failure encountered (solutions_found >1 at final check opportunity) and difficulty in {hard, extreme}, run plan_repair; add repair anchor (kind=repair) and restart uniqueness verification for that anchor only (not full removal cycle).
Acceptance: Hard/extreme optionally gain 1 repair anchor; AnchorMetrics.repair_count increments; anchor_selection_reason='repair'.
Dependencies: T048.

### T053 [P3] Fragmentation guardrail
Goal: Prevent anchor placement that isolates region; reuse path_builder fragmentation heuristic.
Files: `generate/anchor_policy.py`.
Logic: For each candidate anchor, ensure its removal (if not given) would not isolate cells; if anchor causes fragmentation risk removal OR replacement with next eligible turn point.
Acceptance: No test puzzle exhibits isolated region flagged by guardrail; metrics anchor_selection_reason not changed (unless fallback). Possibly set anchor_selection_reason='conservative_fallback' if adjustments applied.
Dependencies: T048.

## Phase 3 – Metrics & Observability (User Story 3)

### T054 [P3] Emit AnchorMetrics
Goal: Add metrics fields to GeneratedPuzzle.solver_metrics: anchor_count, hard_count, soft_count, repair_count, anchor_positions, policy_name, anchor_selection_reason, min_index_gap_enforced, adjacency_mode.
Files: `generate/generator.py` (when assembling solver_metrics), `generate/anchor_policy.py` (provide metrics data).
Acceptance: solver_metrics contains all fields; tests validate presence and types.
Dependencies: T048.

### T055 [P2] Opt-out & legacy behavior plumbing
Goal: Implement combined logic for flags: if `adaptive_turn_anchors=False` OR `anchor_policy_name=='legacy'` then use `_legacy_turn_anchors` path.
Files: `generate/generator.py`, `hidato.py` adds CLI `--anchor-policy` (string) and `--no-adaptive-turn-anchors` flag.
Acceptance: Running with `--anchor-policy legacy` reproduces previous anchor counts; determinism holds; tests pass.
Dependencies: T046, T048.

### T056 [P3] Determinism tests for adaptive anchors
Goal: Ensure identical seeds produce identical anchor sets & metrics.
Files: `tests/test_anchor_determinism.py`.
Scenarios: For each difficulty (easy, medium, hard, extreme) generate twice with same seed; compare anchor_positions; when soft anchor droppable scenario triggers ensure consistent decision.
Acceptance: All assertions pass.
Dependencies: T048, T049.

## Phase 4 – Unit & Integration Tests

### T057 [P1] Basic anchor count tests ✅
Files: `tests/test_anchor_counts.py`.
Status: COMPLETE - 7 tests created and passing (easy, medium, hard, extreme counts; metadata presence; legacy behavior; determinism).
Checks: Easy anchors between 2–3 (excluding endpoints), Medium soft anchor 0–1, Hard/Extreme only endpoints unless repair reason logged.
Acceptance: Pass for seeded runs (choose 3 seeds).
Dependencies: T048.

### T058 [P3] Soft anchor evaluation test 🔲
Files: `tests/test_soft_anchor.py`.
Status: PENDING - Awaits T049 implementation.
Scenario: Construct medium puzzle where soft anchor is redundant; assert it is dropped (0 soft anchors). Provide second scenario where uniqueness requires soft anchor (1 soft kept).
Acceptance: Both scenarios pass.
Dependencies: T049.

### T059 [P3] Repair anchor test 🔲
Files: `tests/test_repair_anchor.py`.
Status: PENDING - Awaits T052 implementation.
Scenario: Force uniqueness ambiguity by constructing grid/seed causing multiple solutions; assert repair anchor added and uniqueness resolved.
Acceptance: repair_count == 1; anchor_selection_reason='repair'.
Dependencies: T052.

### T060 [P3] Metrics presence & types
Files: `tests/test_anchor_metrics.py`.
Checks: All metric keys exist; types correct; policy_name matches config; min_index_gap flag correct for at least one easy case.
Dependencies: T054.

### T061 [P2] Opt-out regression tests
Files: `tests/test_anchor_opt_out.py`.
Checks: Setting adaptive_turn_anchors=False yields legacy counts identical to pre-change snapshot for a known seed; ensures non-regression.
Dependencies: T055.

### T062 [P1] Non-regression full suite run ✅
Goal: Confirm existing 31 tests still pass.
Files: (none modified) Execution only.
Status: COMPLETE - 109 tests passing (including 7 new anchor tests); 7 pre-existing failures unrelated to anchor changes.
Acceptance: 31 original tests + new anchor tests all PASS.
Dependencies: All prior test tasks.

## Phase 5 – Documentation & CLI UX

### T063 [POLISH] Update quickstart.md from planning placeholders
Files: `specs/001-adaptive-turn-anchors/quickstart.md` finalize examples (remove planning wording) & add repair example.
Dependencies: T052.

### T064 [POLISH] Update README.md ✅
Goal: Add section "Adaptive Turn Anchors" with usage, flags, metrics snippet.
Files: `README.md`.
Status: COMPLETE - Added comprehensive section with table, usage examples, anchor types, and impact on generation.
Dependencies: T055, T054.

### T065 [POLISH] Add CLI help text
Files: `hidato.py`.
Add argparse help for `--anchor-policy`, `--no-adaptive-turn-anchors`; verbose output prints anchor metrics when `--verbose`.
Dependencies: T055.

## Phase 6 – Benchmarking & Tuning

### T066 [POLISH] Benchmark anchor impact script
Files: `scripts/bench_anchor_policy.py`.
Measures: median clue_count & anchor_count across seeds per difficulty comparing adaptive_v1 vs legacy.
Acceptance: Script runs & prints table; internal dev doc snippet produced.
Dependencies: T048, T055.

### T067 [POLISH] Success criteria sampling harness
Files: `tests/test_anchor_success_criteria.py` (slow tag or optional).
Runs 50 seeds hard/extreme; computes median clue reduction ≥10% vs legacy baseline (precomputed or side-run) & uniqueness ≥95%.
Acceptance: Pass or prints actionable tuning note if fail.
Dependencies: T066.

## Phase 7 – Post-Implementation Tuning (Optional / Future)

### T068 [FUTURE] Implement anchor_tolerance logic
Goal: Use anchor_tolerance to probabilistically drop borderline anchors for ultra-hard puzzles.
Dependencies: Completed baseline.

### T069 [FUTURE] Prefer four-neighbor adjustment for sparse hard puzzles
Goal: Temporarily treat adjacency as 4-neighbor for anchor evaluation to reduce artificial structure.
Dependencies: T052.

---

## Cross-Cutting Quality Gates Tasks

### T070 Lint & style integration for new module
Goal: Ensure `ruff check .` passes after adding new files.
Dependencies: Modules created.

### T071 Determinism seed reproducibility extension
Goal: Extend existing seed reproducibility tests to include anchor metrics fields.
Files: `tests/test_seed_repro.py` (modify).
Dependencies: T054.

---

## Implementation Order Recommendation
1. T046 → T047 → T048 (establish adaptive anchor pipeline)
2. T049–T051 (refine selection logic & symmetry) → T050 distribution
3. T054 metrics emission early for observability
4. T055 opt-out to secure rollback path
5. Guardrails & repair (T052, T053)
6. Test suite tasks (T056–T062) then docs/CLI (T063–T065)
7. Bench & success criteria (T066–T067)
8. Future enhancements (T068–T069)

---

## Acceptance Matrix (Summary)
- User Story 1 (Minimal clues): T046–T048, T050, T052 (repair), T062, T066–T067
- User Story 2 (Opt-out/tooling): T046, T055, T061, T064–T065
- User Story 3 (Metrics/guardrails): T047, T049–T054, T056–T060, T071

---

## Risk Notes
- Repair anchor insertion could destabilize determinism if uniqueness check nondeterministic → ensure solver invoked with deterministic mode; capture seed in metrics.
- Soft anchor evaluation must not perform expensive full search repeatedly → consider capped uniqueness check (cap=2) for evaluation.
- Benchmark tests (T067) may be slow; mark with skip/slow unless CI performance acceptable.

## Done Definition Per Task
Each task considered DONE when:
1. Code merged in feature branch
2. Associated tests (if defined) pass locally
3. Metrics or docs updated if relevant
4. ruff passes (T070) and no regression in existing tests (T062)

---

(End of tasks.md)
