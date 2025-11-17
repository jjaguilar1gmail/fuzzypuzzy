---

description: "Task list for implementing daily puzzle size options on the frontend"
---

# Tasks: Daily Puzzle Size Options

**Input**: Design documents from `/specs/001-daily-puzzle-sizes/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, quickstart.md

**Tests**: This feature will extend existing Vitest suites. We include explicit test tasks for each user story because the spec emphasizes deterministic behavior and sensible per-size progress.

**Organization**: Tasks are grouped by user story (US1, US2, US3) to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- All descriptions include concrete file paths under `frontend/`.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Confirm existing frontend infrastructure is ready for the daily size work (no new projects or frameworks).

- [ ] T001 Verify daily selection and persistence entry points in `frontend/src/lib/daily.ts` and `frontend/src/lib/persistence.ts`
- [ ] T002 Verify daily page structure and HUD components in `frontend/src/pages/index.tsx` and `frontend/src/components/HUD/`
- [ ] T003 [P] Verify existing daily puzzle integration tests in `frontend/tests/integration/daily-play.test.tsx` and identify where to extend for size-aware behavior

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core size-aware daily selection and persistence primitives that all user stories rely on.

- [ ] T004 Define `DailySizeOption` config (small/medium/large) and helper types in `frontend/src/lib/daily.ts` or a nearby module
- [ ] T005 [P] Extend `getDailyPuzzleKey` (or add new helper) in `frontend/src/lib/daily.ts` to support size-aware keys (e.g., `daily-YYYY-MM-DD-medium`)
- [ ] T006 Wire size-aware persistence keys into save/load helpers in `frontend/src/lib/persistence.ts` (ensure they accept/derive sizeId)
- [ ] T007 [P] Add or adjust utility to compute `(date, sizeId)` → deterministic index with wrap-around in `frontend/src/lib/daily.ts`
- [ ] T008 Ensure existing `useGameStore` and `useProgressStore` selectors in `frontend/src/state/gameStore.ts` and `frontend/src/state/progressStore.ts` can accept a size-aware key for daily puzzles

**Checkpoint**: After Phase 2, the codebase can deterministically select and persist a daily puzzle per `(date, size)` without any UI changes yet.

---

## Phase 3: User Story 1 - Select Daily Puzzle Size (Priority: P1) 🎯 MVP

**Goal**: On the daily puzzle page, show three size options (Small 5×5, Medium 6×6, Large 7×7). Selecting a size loads a puzzle of that size for today.

**Independent Test**: Load `/`, confirm three size pills/buttons are visible, click each and verify that the grid dimensions and puzzle size match 5×5, 6×6, or 7×7 respectively.

### Tests for User Story 1

- [ ] T009 [P] [US1] Add integration test to ensure size options render and are accessible in `frontend/tests/integration/daily-play.test.tsx`
- [ ] T010 [P] [US1] Add integration test to verify grid size changes when selecting Small/Medium/Large in `frontend/tests/integration/daily-play.test.tsx`

### Implementation for User Story 1

- [ ] T011 [P] [US1] Introduce a size selector UI (pill/button group) near the title and stats in `frontend/src/pages/index.tsx`
- [ ] T012 [P] [US1] Style the size selector pills/buttons to match existing HUD pills (e.g., SessionStats) in `frontend/src/components/HUD/` or a new shared style module
- [ ] T013 [US1] Wire the size selector to call a new `setDailySize(sizeId)` handler in `frontend/src/pages/index.tsx` that triggers loading the corresponding daily puzzle via `getDailyPuzzle` or a new size-aware function in `frontend/src/lib/daily.ts`
- [ ] T014 [US1] Ensure that selecting a size results in loading a puzzle whose `size` (rows/cols) matches the chosen option and that the grid renders correctly in `frontend/src/components/Grid/GuidedGrid.tsx` or related components

**Checkpoint**: US1 complete when a player can visually select Small/Medium/Large on `/` and see the correct grid size load for each.

---

## Phase 4: User Story 2 - Persistent Size Preference (Priority: P2)

**Goal**: Remember the player’s last chosen size and automatically load that size’s puzzle on subsequent visits; default to Medium 6×6 on first visit.

**Independent Test**: First visit: `/` auto-loads a Medium 6×6 puzzle. Change to Large, reload the page, and verify Large auto-loads with no extra clicks.

### Tests for User Story 2

- [ ] T015 [P] [US2] Add integration test verifying default Medium 6×6 auto-load on first visit in `frontend/tests/integration/daily-play.test.tsx`
- [ ] T016 [P] [US2] Add integration test verifying last-selected size (e.g., Large) is restored on reload in `frontend/tests/integration/daily-play.test.tsx`

### Implementation for User Story 2

- [ ] T017 [P] [US2] Implement `SizePreference` persistence (get/set last sizeId) in `frontend/src/lib/persistence.ts`
- [ ] T018 [US2] Integrate size preference reading/writing into the daily page bootstrapping logic in `frontend/src/pages/index.tsx` (default Medium 6×6 when no preference exists)
- [ ] T019 [US2] Ensure the size selector UI reflects the restored size (active pill) on load and that the corresponding puzzle is auto-loaded in `frontend/src/pages/index.tsx`

**Checkpoint**: US2 complete when first-time visitors see Medium 6×6 automatically and returning visitors see their last chosen size automatically loaded.

---

## Phase 5: User Story 3 - Different Puzzle per Size (Priority: P1)

**Goal**: Each size option loads a different puzzle for the same date, and daily puzzles per size rotate deterministically with wrap-around when we exhaust the pool. Progress and stats are tracked separately and remain sensible when switching sizes.

**Independent Test**: On a given day, play Small to completion, then switch to Medium and Large and confirm each size shows a different puzzle and maintains its own progress and completion stats.

### Tests for User Story 3

- [ ] T020 [P] [US3] Add unit tests for `(date, sizeId)` → puzzle selection with wrap-around in `frontend/tests/unit/lib/daily-selection.test.ts` (new file)
- [ ] T021 [P] [US3] Add integration test verifying that different sizes on the same date load different puzzles in `frontend/tests/integration/daily-play.test.tsx`
- [ ] T022 [P] [US3] Add integration test verifying per-size progress persistence when switching between sizes in `frontend/tests/integration/daily-play.test.tsx`

### Implementation for User Story 3

- [ ] T023 [P] [US3] Implement size-aware daily selection function in `frontend/src/lib/daily.ts` that accepts `(date, sizeId)` and returns `packId`/`puzzleId` with deterministic wrap-around
- [ ] T024 [US3] Update `getDailyPuzzle` (or add `getDailyPuzzleForSize`) in `frontend/src/lib/daily.ts` to use size-specific filtering and selection and to cooperate with existing pack loading
- [ ] T025 [P] [US3] Wire per-size storage keys (`daily-YYYY-MM-DD-small|medium|large`) into daily game state save/load in `frontend/src/lib/persistence.ts`
- [ ] T026 [US3] Ensure `useGameStore` and `useProgressStore` in `frontend/src/state/gameStore.ts` and `frontend/src/state/progressStore.ts` use size-aware keys so that time, moves, and completion are tracked separately per size
- [ ] T027 [US3] Update the daily page logic in `frontend/src/pages/index.tsx` so that switching sizes saves the current size’s state and restores or initializes the target size’s state without losing progress
- [ ] T028 [US3] Verify that UI stats components (e.g., `SessionStats` in `frontend/src/components/HUD/SessionStats.tsx`) display per-size stats correctly when switching sizes on the same date

**Checkpoint**: US3 complete when each size has its own deterministic daily puzzle and separate, sensible progress/stats, and switching sizes does not corrupt or mix states.

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: UI polish, performance, and consistency across the daily experience.

- [ ] T029 [P] Refine size selector styles and spacing in `frontend/src/pages/index.tsx` and related HUD components to ensure the UI remains clean and uncluttered with time/moves pills
- [ ] T030 [P] Add any missing ARIA roles/labels for size selector buttons in `frontend/src/pages/index.tsx` to keep accessibility strong
- [ ] T031 Review performance of daily selection and size switching (e.g., console timings) and optimize any obvious bottlenecks in `frontend/src/lib/daily.ts`
- [ ] T032 Run full frontend test suite (`pnpm vitest run` in `frontend/`) and fix any regressions related to daily selection or HUD layout

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies – can start immediately.
- **Foundational (Phase 2)**: Depends on Setup completion – blocks all user stories.
- **User Stories (Phases 3–5)**: Depend on Foundational phase completion.
  - US1 and US2 rely primarily on the presence of size-aware helpers and keys.
  - US3 relies on deterministic selection and persistence primitives being in place.
- **Polish (Phase 6)**: Depends on target user stories (US1–US3) being implemented.

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational – no dependency on other stories.
- **User Story 2 (P2)**: Can start after Foundational – integrates with US1’s UI but is independently testable.
- **User Story 3 (P1)**: Can start after Foundational – builds on size-aware selection and persistence but remains independently verifiable.

### Parallel Opportunities

- Tasks marked [P] in Phases 1–2 can run in parallel as they touch different modules.
- Within each user story, [P] tasks (tests, helpers, or styles) can run in parallel once dependencies are satisfied.
- Different user stories can be developed in parallel by different contributors after Phase 2 is complete.

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1 (Setup) and Phase 2 (Foundational).
2. Implement Phase 3 (US1) – size selector and per-size loading.
3. Run tests associated with US1 and validate that grid sizes match chosen options.
4. Optionally deploy/demo this as an early MVP of size selection.

### Incremental Delivery

1. Add US2 to remember and restore size preference across sessions.
2. Add US3 to ensure distinct puzzles and per-size progress/stats.
3. Apply Phase 6 polish tasks for a refined UX and performance.
