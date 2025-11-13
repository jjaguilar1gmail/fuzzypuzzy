# Implementation Plan: Guided Sequence Flow Play

**Branch**: `001-guided-sequence-flow` | **Date**: 2025-11-13 | **Spec**: ../spec.md
**Input**: Feature specification from `/specs/001-guided-sequence-flow/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace manual number selection with a guided sequential placement flow anchored by a selected cell. When an anchor is chosen the UI derives next target (v+1), optionally highlights all legal adjacent empty cells (8‑neighbor), and places on single click. If no legal extension exists the interface becomes neutral (clears next target) rather than signaling an error, allowing non‑linear exploration. Players can remove previously placed numbers via direct click; removal recomputes the longest contiguous chain and adjusts or clears the next target. A Show Guide toggle controls visual highlights; logic always validates moves silently. Undo/redo treats placement/removal as atomic actions. Styling emphasizes subtle guidance, clarity, and accessibility.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: TypeScript (React frontend) + Python 3.11 (existing puzzle generation only, unchanged).  
**Primary Dependencies**: React, existing internal hooks/context; no new global state lib (decision: no Redux/Recoil).  
**Storage**: In-memory board state only (no persistence added).  
**Testing**: Jest + React Testing Library (UI logic); optional Cypress for E2E (stretch); pytest unchanged backend.  
**Target Platform**: Web (desktop + mobile browsers).  
**Project Type**: Web application frontend enhancement.  
**Performance Goals**: Anchor select → highlight compute < 2ms (8x8); 95% valid actions commit < 100ms; removal recompute chain < 3ms.  
**Constraints**: No heavy new deps; WCAG AA contrast for guide/anchor; undo stack capped at 50 actions; deterministic adjacency logic.  
**Scale/Scope**: Single-player session; board sizes 5x5–10x10; complexity O(n) per recompute (n ≤ 100 typical).

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Gates:
1. Minimal dependencies (no extra global state library) → PASS
2. Deterministic algorithms (adjacency, chain detection) → PASS
3. Bounded resource usage (undo stack <= 50) → PASS
4. Accessibility (non-color cues) commitment → PASS
5. No backend schema changes → PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-guided-sequence-flow/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md (future)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
frontend/
  src/
    components/
      PuzzleBoard/
        BoardGrid.tsx
        Cell.tsx
        AnchorOverlay.tsx
        NextNumberIndicator.tsx
        GuideToggle.tsx
        RemovalHint.tsx
      Feedback/
        MistakeBadge.tsx
        Toast.tsx
        HighlightLayer.tsx
    hooks/
      useSequenceState.ts
      useUndoRedo.ts
      useGuideToggle.ts
    logic/
      adjacency.ts
      chainDetection.ts
      nextNumber.ts
      highlightComputer.ts
      validation.ts
    state/
      boardContext.tsx
    styles/
      guided-flow.css
    tests/
      unit/
      integration/
      contract/
```

**Structure Decision**: Enhance existing frontend with new PuzzleBoard module and supporting logic/contexts; no backend changes required.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| (none) | Feature fits existing structure | N/A |
