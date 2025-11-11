---

description: "Generated task list for Hidato Web Game & Puzzle Pack Generator"
---

# Tasks: Hidato Web Game & Puzzle Pack Generator

**Input**: Design documents from `/specs/001-hidato-web-game/`
**Prerequisites**: plan.md (required), spec.md (required), research.md, data-model.md, contracts/

Tests are OPTIONAL and not explicitly requested in the spec; this plan focuses on implementation tasks. Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- [P]: Can run in parallel (different files, no dependencies)
- [Story]: Which user story this task belongs to (US1, US2, US3, ...)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

Purpose: Initialize the frontend project and baseline structure per the implementation plan

- [x] T001 Create frontend project structure at `frontend/`
- [x] T002 Initialize Next.js + TypeScript app with dependencies at `frontend/package.json`
- [x] T003 [P] Add TailwindCSS setup at `frontend/tailwind.config.js`, `frontend/postcss.config.js`, `frontend/src/styles/globals.css`
- [x] T004 [P] Add linting/formatting configs at `frontend/.eslintrc.cjs`, `frontend/.prettierignore`
- [x] T005 [P] Create packs directory and placeholder at `frontend/public/packs/.gitkeep` and `frontend/public/packs/sample-pack/`

---

## Phase 2: Foundational (Blocking Prerequisites)

Purpose: Core infrastructure that MUST be complete before any user story

- [x] T006 Create domain types at `frontend/src/domain/puzzle.ts`, `frontend/src/domain/grid.ts`, `frontend/src/domain/position.ts`
- [x] T007 [P] Create Zod schemas from contracts at `frontend/src/lib/schemas/puzzle.ts`, `frontend/src/lib/schemas/pack.ts`
- [x] T008 Implement pack/puzzle loaders with validation at `frontend/src/lib/loaders/packs.ts`
- [x] T009 Create base Zustand stores at `frontend/src/state/gameStore.ts`, `frontend/src/state/settingsStore.ts`
- [x] T010 Scaffold route pages at `frontend/src/pages/index.tsx`, `frontend/src/pages/packs/index.tsx`, `frontend/src/pages/packs/[packId]/index.tsx`, `frontend/src/pages/packs/[packId]/puzzles/[puzzleId].tsx`
- [x] T011 [P] Add base theme and accessibility styles at `frontend/src/styles/theme.css`
- [x] T012 Implement deterministic daily selection util at `frontend/src/lib/daily.ts`

Checkpoint: Foundation ready — user story implementation can now begin

---

## Phase 3: User Story 1 - Play a Daily Hidato Puzzle (Priority: P1) 🎯 MVP

Goal: Player can load and play a daily puzzle with placement, validation, undo, pencil marks, completion modal, and basic animations.

Independent Test: Launch `/` to load the daily puzzle; interact with grid; place numbers; undo; use pencil mode; complete puzzle and see results modal.

### Tests for User Story 1 (write before implementation)

- [ ] T044 [P] [US1] Unit test Hidato adjacency validation at `frontend/tests/unit/lib/validation/hidato.test.ts`
- [ ] T045 [P] [US1] Component test SVG Grid interactions (select/place/undo) at `frontend/tests/unit/components/Grid.test.tsx`
- [ ] T046 [P] [US1] Component test Number Palette and pencil toggle at `frontend/tests/unit/components/Palette.test.tsx`
- [ ] T047 [US1] Integration test daily flow (load → play → complete → modal) at `frontend/tests/integration/daily-play.test.tsx`
- [ ] T048 [US1] Persistence round-trip test (hydrate/snapshot) at `frontend/tests/integration/persistence.test.ts`

### Implementation for User Story 1

- [ ] T013 [P] [US1] Implement SVG Grid component at `frontend/src/components/Grid/Grid.tsx`
- [ ] T014 [P] [US1] Implement Number Palette with pencil toggle at `frontend/src/components/Palette/Palette.tsx`
- [ ] T015 [US1] Implement daily game page at `frontend/src/pages/index.tsx` (load daily puzzle via `lib/daily.ts` + `lib/loaders/packs.ts`)
- [ ] T016 [US1] Implement Hidato validation (adjacency, givens protection) at `frontend/src/lib/validation/hidato.ts`
- [ ] T017 [US1] Add undo/redo stack in game store at `frontend/src/state/gameStore.ts`
- [ ] T018 [US1] Add pencil candidates data model/UI at `frontend/src/state/gameStore.ts` and `frontend/src/components/Grid/Grid.tsx`
- [ ] T019 [US1] Implement completion modal at `frontend/src/components/HUD/CompletionModal.tsx`
- [ ] T020 [US1] Implement settings (sound, theme toggles) at `frontend/src/components/HUD/SettingsMenu.tsx` and `frontend/src/state/settingsStore.ts`
- [ ] T021 [US1] Implement local persistence hydration/snapshot at `frontend/src/lib/persistence.ts` and integrate in `frontend/src/pages/index.tsx`
- [ ] T022 [US1] Add subtle animations (≤150ms) in Grid/Palette using Framer Motion at `frontend/src/components/**`

Checkpoint: US1 independently functional and demoable (MVP)

---

## Phase 4: User Story 2 - Browse & Select Puzzle Packs (Priority: P2)

Goal: Player can browse packs, filter, view metadata, and play puzzles in sequence with progress tracking.

Independent Test: Navigate to `/packs`, filter by difficulty, open a pack, start puzzle #1, and navigate through the pack.

### Tests for User Story 2 (write before implementation)

- [ ] T049 [P] [US2] Integration test packs index filtering by difficulty at `frontend/tests/integration/packs-index.test.tsx`
- [ ] T050 [P] [US2] Integration test pack detail loads metadata at `frontend/tests/integration/pack-detail.test.tsx`
- [ ] T051 [US2] Route test loads puzzle and records progress at `frontend/tests/integration/pack-puzzle-route.test.tsx`

### Implementation for User Story 2

- [ ] T023 [P] [US2] Implement packs index loader/util at `frontend/src/lib/loaders/packsIndex.ts`
- [ ] T024 [P] [US2] Implement packs list page with filters at `frontend/src/pages/packs/index.tsx`
- [ ] T025 [US2] Implement pack detail page at `frontend/src/pages/packs/[packId]/index.tsx`
- [ ] T026 [US2] Implement pack puzzle route reusing game components at `frontend/src/pages/packs/[packId]/puzzles/[puzzleId].tsx`
- [ ] T027 [US2] Implement pack progress store (last puzzle index, completion) at `frontend/src/state/progressStore.ts`

Checkpoint: US1 and US2 are independently functional

---

## Phase 5: User Story 3 - Generate Puzzle Packs via CLI (Priority: P3)

Goal: Maintainer can generate validated unique puzzles into pack structure under frontend/public.

Independent Test: Run CLI with sizes/difficulties/count and verify output manifests and puzzles under `frontend/public/packs/{packId}`.

### Tests for User Story 3 (write before implementation)

- [ ] T052 [P] [US3] Pytest CLI invocation test (args parse, exit codes) at `tests/packgen/test_cli.py`
- [ ] T053 [P] [US3] Validate exported metadata.json and puzzles shape at `tests/packgen/test_export.py`
- [ ] T054 [US3] Generation summary report contents test at `tests/packgen/test_report.py`

### Implementation for User Story 3

- [ ] T028 [US3] Create CLI entrypoint at `app/packgen/cli.py`
- [ ] T029 [P] [US3] Implement generator wrapper using engine at `app/packgen/generate_pack.py`
- [ ] T030 [P] [US3] Implement JSON exporters (metadata + puzzles) at `app/packgen/export.py`
- [ ] T031 [US3] Implement summary report writer at `app/packgen/report.py`
- [ ] T032 [US3] Add example configuration at `app/packgen/config.example.json`
- [ ] T033 [US3] Ensure unique timestamped output directories at `frontend/public/packs/{packId}-{timestamp}/`
- [ ] T034 [US3] Add argparse options (sizes, difficulties, count, outdir, seed, retries) in `app/packgen/cli.py`
- [ ] T035 [US3] Validate outputs against constraints before write at `app/packgen/generate_pack.py`

Checkpoint: US3 independently functional with CLI-only verification

---

## Phase 6: User Story 4 - Mobile Responsive Interaction (Priority: P3)

Goal: Comfortable mobile play with adaptive layout, bottom sheet palette, and no horizontal scroll.

Independent Test: Emulate mobile viewport (<480px), verify grid scales, bottom sheet palette interaction, and tappable targets ≥40px.

### Tests for User Story 4 (write before implementation)

- [ ] T055 [P] [US4] Component test bottom sheet palette expand/collapse at `frontend/tests/unit/components/Palette/BottomSheet.test.tsx`
- [ ] T056 [US4] Integration test mobile viewport layout (no horizontal scroll, 40px targets) at `frontend/tests/integration/mobile-layout.test.tsx`

### Implementation for User Story 4

- [ ] T036 [P] [US4] Implement responsive styles and breakpoints in `frontend/src/styles/globals.css` and components
- [ ] T037 [P] [US4] Implement bottom sheet palette at `frontend/src/components/Palette/BottomSheet.tsx`
- [ ] T038 [US4] Ensure 40px min tap targets and no horizontal scroll across pages at `frontend/src/components/**`
- [ ] T039 [US4] Handle orientation changes and layout reflow without data loss at `frontend/src/pages/**`

Checkpoint: US4 independently functional

---

## Phase N: Polish & Cross-Cutting Concerns

Purpose: Improvements that affect multiple user stories

- [ ] T040 [P] Documentation updates and quickstart verification at `specs/001-hidato-web-game/quickstart.md` and `frontend/README.md`
- [ ] T041 Accessibility audit adjustments (WCAG AA) across `frontend/src/components/**`
- [ ] T042 Performance optimization (memoization, render trimming) across `frontend/src/components/**`
- [ ] T043 [P] Add additional unit/integration tests if requested later at `frontend/tests/**`

---

## Dependencies & Execution Order

### Phase Dependencies

- Setup (Phase 1): No dependencies — can start immediately
- Foundational (Phase 2): Depends on Setup completion — BLOCKS all user stories
- User Stories (Phase 3+): Depend on Foundational — can proceed in parallel or in priority order (P1 → P2 → P3)
- Polish (Final Phase): Depends on stories being complete as desired

### User Story Dependencies

- User Story 1 (P1): Starts after Foundational; no dependency on other stories
- User Story 2 (P2): Starts after Foundational; independent but reuses components from US1
- User Story 3 (P3): Starts after Foundational; independent of frontend stories
- User Story 4 (P3): Starts after Foundational; independent; may share styles/components

### Parallel Opportunities

- Setup: T003, T004, T005
- Foundational: T007, T011
- US1: T013, T014 can proceed in parallel; T017–T022 follow core wiring
- US2: T023, T024 in parallel
- US3: T029, T030 in parallel
- US4: T036, T037 in parallel

### Parallel Example: User Story 1

- Launch parallel tasks:
  - T013 [P] [US1] Implement SVG Grid component at `frontend/src/components/Grid/Grid.tsx`
  - T014 [P] [US1] Implement Number Palette with pencil toggle at `frontend/src/components/Palette/Palette.tsx`

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. Stop and validate; demo MVP

### Incremental Delivery

1. Foundation ready → Add US1 → Validate → Demo
2. Add US2 → Validate → Demo
3. Add US3 → Validate → Demo
4. Add US4 → Validate → Demo

## Format validation

- All tasks follow: `- [ ] T### [P?] [US?] Description with file path`
- Each user story phase is independently testable based on stated Independent Tests
- Tasks include clear file paths and can be executed by an LLM without additional context
