# Quickstart: Guided Sequence Flow Play

## Goal
Introduce a fluid sequential placement experience with optional guidance highlights and intuitive removal.

## Prerequisites
- Frontend React environment installed
- Puzzle board component existing baseline

## Enable Feature
1. Import new hooks: `useSequenceState`, `useUndoRedo`, `useGuideToggle`.
2. Wrap puzzle board in `<BoardContextProvider>`.
3. Add `<GuideToggle />` and `<NextNumberIndicator />` components.
4. Replace manual number picking UI with anchor selection + PLACE_NEXT flow.

## Core Hooks
- `useSequenceState()` returns { anchorValue, nextTarget, legalTargets, chainEndValue, chainLength, nextTargetChangeReason, selectAnchor, placeNext, removeCell }.
- `useUndoRedo()` returns { undo, redo, canUndo, canRedo }.
- `useGuideToggle()` returns { guideEnabled, toggleGuide }.

## Typical Flow
```
selectAnchor(cellPos)
if (nextTarget) highlight legalTargets (if guideEnabled)
placeNext(targetPos) -> updates anchorValue & nextTarget
removeCell(cellPos) -> clears anchor (if anchor removed) & neutral state
// After removal:
//   if tail removed => nextTargetChangeReason='tail-removal' and nextTarget cleared
//   else => nextTargetChangeReason='non-tail-removal' and may remain neutral until new anchor
```

## Styling
- `.anchor-cell`: subtle outline + background tint.
- `.legal-highlight`: low-opacity fill + thin outline.
- `.mistake-badge`: small red indicator near board edge.

## Testing
- Unit: adjacency.ts, chainDetection.ts, nextNumber.ts, highlightComputer.ts
- Integration: anchor select → placement → removal → undo/redo
- Contract: SELECT_ANCHOR then GET_SEQUENCE_STATE returns legalTargets

## Performance Tips
- Precompute adjacency offsets array once.
- Avoid deep cloning board; mutate cell objects and trigger React updates via shallow state wrapper.

## Accessibility
- Provide text label: "Next number: X" (aria-live polite)
- High-contrast mode increases outline thickness.

## Neutral State Guidance
When `nextTarget === null`, show placeholder text: "Select a number to continue sequence." No error styling.
Distinguish causes via `nextTargetChangeReason`:
| Reason | UI Treatment |
|--------|--------------|
| neutral | Placeholder only |
| tail-removal | Placeholder + optional subtle info tooltip "Chain tail removed" |
| non-tail-removal | Placeholder (no extra messaging) |
| anchor-change | Transient anchor highlight; compute nextTarget if legal |
| placement | Normal progression (indicator visible) |

## Undo/Redo Behavior
Each PLACE/REMOVE pushes an action. After REMOVE, user must explicitly select a new anchor to resume.

## Feature Toggle
Guide toggle persists using localStorage key `guidedFlow.showGuide`.

## Edge Cases
- No legalTargets: neutral state.
- Attempted PLACE_NEXT with stale nextTarget: revalidate; if invalid, clear and neutral.
- STALE_TARGET error: occurs when underlying chain changed (e.g., removal) but UI still shows outdated nextTarget; immediately recompute and emit neutral state.
- Removal of chain tail: clear anchor & nextTarget; require explicit new anchor selection.
- Removal of non-tail value: chainEndValue unchanged; stay neutral until user re-anchors.

## Debugging
Use snapshot utility `captureSequenceSnapshot(state)` to log {anchorValue, nextTarget, chainEndValue, chainLength, nextTargetChangeReason, legalTargets.length} for audits (dev only).

## Migration Notes
Remove old number picker component references; ensure no code attempts direct arbitrary number assignment.
