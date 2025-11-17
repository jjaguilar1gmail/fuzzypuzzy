# Implementation Plan: Daily Puzzle Size Options

**Branch**: `001-daily-puzzle-sizes` | **Date**: 2025-11-16 | **Spec**: `specs/001-daily-puzzle-sizes/spec.md`
**Input**: Feature specification from `/specs/001-daily-puzzle-sizes/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Add support for three daily puzzle sizes (Small 5×5, Medium 6×6, Large 7×7) on the frontend, with Medium 6×6 auto-loaded by default, separate daily puzzle selection and progress tracking per size, and a clean, unobtrusive size-selection UI that fits into the existing daily puzzle layout (stats, time, moves) without adding clutter.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript + React (Next.js frontend), following project’s existing frontend stack  
**Primary Dependencies**: Next.js pages, React, Zustand stores (`useGameStore`, `useProgressStore`), existing daily loader (`frontend/src/lib/daily.ts`), and UI components (Grid, GuidedGrid, SessionStats, CompletionModal)  
**Storage**: Browser localStorage via existing persistence utilities (`frontend/src/lib/persistence.ts`), plus deterministic daily puzzle selection from JSON packs  
**Testing**: Vitest + React Testing Library, following existing frontend test patterns under `frontend/tests/integration` and `frontend/tests/unit`  
**Target Platform**: Web browser (desktop + mobile) via Next.js frontend
**Project Type**: Web application with `frontend/` app and shared core/solver modules  
**Performance Goals**: Daily puzzle (any size) should load and render within ~2 seconds on typical devices and connections; switching sizes should feel instantaneous (no full-page reload)  
**Constraints**: Respect existing UX for guided sequence flow; avoid cluttering the main play area; keep size selector discoverable but unobtrusive (top of page near title/stats)  
**Scale/Scope**: Single daily puzzle route (`/`) with three size variants per day; puzzle pool size bounded by existing packs; user base scale handled by static assets + client-side logic

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Clarity & separation of concerns: Plan keeps daily-size logic confined to daily loader (`daily.ts`), frontend state, and UI components; core solver/generator code and domain models are not mutated, satisfying “core domain has no I/O” and single-responsibility guidance.
- Determinism & reproducibility: Daily puzzle selection remains deterministic; we will extend it to be deterministic per (date, size) while still using seeds and pack data, in line with the constitution’s determinism rules.
- Safety & validation: No changes to solver validity rules; we will ensure givens are never overwritten and daily state keys remain distinct per size.
- Testing discipline: New behavior (per-size daily selection, per-size progress) will be covered by additional unit/integration tests, following the “every bug gets a test” and existing Vitest patterns.

**Gate Status**: PASS – Proposed frontend-only changes and daily-selection adjustments align with the constitution; no violations or special complexity justifications required at this stage.

## Project Structure

### Documentation (this feature)

```text
specs/[###-feature]/
├── plan.md              # This file (/speckit.plan command output)
├── research.md          # Phase 0 output (/speckit.plan command)
├── data-model.md        # Phase 1 output (/speckit.plan command)
├── quickstart.md        # Phase 1 output (/speckit.plan command)
├── contracts/           # Phase 1 output (/speckit.plan command)
└── tasks.md             # Phase 2 output (/speckit.tasks command - NOT created by /speckit.plan)
```

### Source Code (repository root)

```text
frontend/
├── src/
│   ├── pages/
│   │   ├── index.tsx                 # Daily puzzle page (US1)
│   │   └── packs/                    # Pack browsing & puzzle routes
│   ├── components/
│   │   ├── Grid/                     # Grid & guided grid components
│   │   ├── Palette/                  # Number input & bottom sheet
│   │   └── HUD/                      # Session stats, completion modal, settings
│   ├── lib/
│   │   ├── daily.ts                  # Daily puzzle selection logic
│   │   ├── loaders/                  # Pack & puzzle loaders
│   │   └── persistence.ts            # Local storage utilities
│   ├── state/
│   │   ├── gameStore.ts              # Game state (grid, sequence, completion)
│   │   └── progressStore.ts          # Per-puzzle/pack completion tracking
│   └── domain/                       # Puzzle, pack, and related models
└── tests/
    ├── integration/
    │   ├── daily-play.test.tsx       # Daily puzzle integration tests
    │   ├── packs-index.test.tsx      # Packs index flow
    │   └── pack-puzzle-route.test.tsx
    └── unit/
        ├── components/               # Grid, Palette, HUD unit tests
        └── lib/                      # Validation, helpers, loaders tests
```

**Structure Decision**: Web application with a single frontend project (`frontend/`) that already implements the daily puzzle page, grid, and HUD. This feature will extend the daily puzzle page, daily loader, and progress tracking while keeping the existing structure and responsibilities intact.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |
