# Task Breakdown: Guided Sequence Flow (Feature 001)

Legend:
- Priority: P1 (must), P2 (secondary)
- Status: TODO / IN-PROGRESS / DONE
- Tags: [logic], [ui], [state], [test], [perf], [accessibility], [docs]
- Parallelizable groups separated by blank lines.

## Phase 0: Foundations (Pre-US1)
T001 (P1) [logic][state] Define TypeScript types (`SequenceState`, `BoardCell`, `UndoAction`, `MistakeEvent`, `PlayerSettings`) per data-model.md.
Acceptance: Types compile; no lint errors; exported from `app/sequence/types.ts`.

T002 (P1) [logic] Implement adjacency utility `getAdjacents(pos, rows, cols)` and empties filter.
Acceptance: Unit tests cover corners & center cells; returns 3 for corner in 8x8; no out-of-bounds.

T003 (P1) [logic] Implement chain detection `computeChain(valuesMap, maxValue)` returning `{chainEndValue, chainLength, nextCandidate}`.
Acceptance: Tests for gaps (1,2,4) -> chainEnd=2; map without 1 starts at min value.

T004 (P1) [logic] Implement next target computation `deriveNextTarget(anchorValue, chainInfo, board)` applying adjacency availability check.
Acceptance: Returns null when no legal adjacency; happy path returns anchor+1.

T005 (P1) [state] Implement removal impact function `classifyRemoval(prevChainEnd, removedValue)` -> 'tail-removal' | 'non-tail-removal'.
Acceptance: Unit test removing chainEnd vs inside chain.

T006 (P1) [state] Implement undo/redo stack manager with cap=50, atomic PLACE/REMOVE actions.
Acceptance: Test push beyond 50 trims oldest; undo restores prior anchor & nextTarget snapshot.

T007 (P1) [state] Implement core reducer or hook internal state machine (pure functions) for transitions (SELECT_ANCHOR, PLACE_NEXT, REMOVE_CELL, TOGGLE_GUIDE, UNDO, REDO) returning updated `SequenceState` + side effects (stacks).
Acceptance: Transition tests reflecting table in data-model; tail removal clears anchor.

## Phase 1: US1 Guided Placement (MVP)
T008 (P1) [state][ui] Create hook `useGuidedSequenceFlow(boardInit)` exposing: state, selectAnchor, placeNext, removeCell, toggleGuide, undo, redo.
Acceptance: Storybook or test harness demonstrates placing sequential numbers correctly.

T009 (P1) [ui] Render anchor and legal target highlights (faint & accessible) via `HighlightLayer`.
Acceptance: DOM includes data-test attributes for anchor & legal targets; contrast check passes.

T010 (P1) [ui] Implement `NextNumberIndicator` showing nextTarget or neutral state placeholder.
Acceptance: Shows value when available; hides when null.

T011 (P1) [test] Integration tests: select anchor -> place sequence (1..n) validating visual/DOM states & state invariants.
Acceptance: Jest + React Testing Library; passes CI; covers at least one neutral state.

T012 (P1) [docs] Update `quickstart.md` with hook usage snippet; cross-link new types file.
Acceptance: Markdown builds; no broken relative links.

## Phase 2: US2 Mistake Feedback
T013 (P2) [logic][state] Implement mistake attempt classification (not-adjacent, occupied, no-target) returning `MistakeEvent`.
Acceptance: Unit tests for each classification.

T014 (P2) [ui] Display transient mistake feedback (MistakeBadge + cell outline) timed 1.2s fade.
Acceptance: Mistake badge appears only after invalid attempt; automatic removal after timeout.

T015 (P2) [state] Add mistake logging ring buffer size 20.
Acceptance: Oldest dropped when >20; test verifies length constraint.

T016 (P2) [test] Tests for mistake scenarios & no state corruption (anchor preserved).
Acceptance: All new tests green; coverage for classification ≥90% lines of mistake module.

## Phase 3: US3 Resume Anchor / Neutral Recovery
T017 (P2) [state] Implement neutral resume logic: after tail removal anchor cleared; selecting any chain value re-establishes correct nextTarget.
Acceptance: Test tail removal -> neutral -> new anchor -> correct nextTarget.

T018 (P2) [logic][state] Detect STALE_TARGET when board mutation invalidates previously computed nextTarget without user action (e.g., concurrent removal) and emit recovery event.
Acceptance: Simulate stale scenario; nextTarget recalculated; event flagged.

T019 (P2) [ui] Visual treatment for nextTargetChangeReason (placement pulse, removal fade, anchor-change highlight).
Acceptance: Distinct CSS class applied per reason; snapshot test.

T020 (P2) [test] Integration tests for resume anchor & stale target recovery.
Acceptance: All pass; ensures no phantom highlights remain.

## Phase 4: Performance & Accessibility Polish
T021 (P1) [perf] Add profiling helper measuring highlight & placement compute times; log warning if > thresholds.
Acceptance: Manual run shows times under target; threshold exceed triggers console warn.

T022 (P2) [accessibility] Implement highlight intensity + high contrast toggles; store `PlayerSettings` in localStorage.
Acceptance: Toggling updates DOM classes; persists across reload (test with jsdom).

T023 (P2) [test][perf] Add performance budget test (mock large board) ensuring under configured ms using synthetic timing.
Acceptance: Fails if functions exceed budget; currently passes.

## Phase 5: Documentation & Final QA
T024 (P1) [docs] Add README section summarizing Guided Sequence Flow feature & API surface.
Acceptance: Links to spec + tasks; lint passes.

T025 (P1) [docs][dev-tools] Document `stateSnapshot` utility usage in README and developer notes.
Acceptance: Example output snippet included.

T026 (P1) [test] Full regression test run & flake audit; ensure deterministic results.
Acceptance: Two consecutive runs identical; no skipped tests.

T027 (P1) [release] Prepare changelog entry & finalize success criteria checklist (SC-001–SC-004) with PASS/FAIL status.
Acceptance: Changelog committed; all success criteria PASS.

## Risks & Mitigations Quick Reference
- Complex state transitions: Mitigate with pure function tests (T007, T011).
- Performance regression: Profiling helper & budget tests (T021, T023).
- Visual accessibility: Intensity & contrast toggles (T022) early before polish complete.
- Stale target edge cases: Dedicated tests (T018, T020).

## Dependency Ordering (Simplified)
T001 -> T002 -> T003 -> T004 -> T005 -> T006 -> T007 -> T008 -> (T009,T010 in parallel) -> T011 -> T012 -> (T013 -> T014 -> T015 -> T016) -> (T017 -> T018 -> T019 -> T020) -> (T021,T022) -> T023 -> (T024,T025) -> T026 -> T027
