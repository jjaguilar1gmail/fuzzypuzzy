# Quickstart: Guided Sequence Flow Play

## Goal
Introduce a fluid sequential placement experience with optional guidance highlights and intuitive removal.

## Prerequisites
- Frontend React environment installed
- Puzzle board component existing baseline

## Enable Feature
1. Import main hook from `@/sequence`: `useGuidedSequenceFlow`.
2. Import components: `NextNumberIndicator`, `HighlightLayer`.
3. Initialize hook with board dimensions, givens map, and maxValue.
4. Replace manual number picking UI with anchor selection + PLACE_NEXT flow.

## Core Hook API
The main hook `useGuidedSequenceFlow(rows, cols, givens, maxValue)` returns:
```typescript
interface GuidedSequenceFlowAPI {
  state: SequenceState;            // Current sequence state
  board: BoardCell[][];            // 2D board grid
  selectAnchor: (pos: Position) => void;
  placeNext: (pos: Position) => void;
  removeCell: (pos: Position) => void;
  toggleGuide: (enabled: boolean) => void;
  undo: () => void;
  redo: () => void;
  canUndo: boolean;
  canRedo: boolean;
  recentMistakes: MistakeEvent[];
}
```

Types are exported from `@/sequence/types`.

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
Unit tests in `frontend/src/sequence/__tests__/`:
- `adjacency.test.ts`: getAdjacents, filterEmptyAdjacents, getLegalAdjacents
- `chain.test.ts`: computeChain, buildValuesMap
- `undoRedo.test.ts`: UndoRedoStack, snapshot utilities

Run tests: `npm test -- src/sequence/__tests__`

Integration tests (to be implemented):
- Anchor select → placement → removal → undo/redo flows
- Neutral state recovery after tail removal
- STALE_TARGET detection and recovery

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
Use snapshot utility from `@/sequence/stateSnapshot`:
```typescript
import { captureSequenceSnapshot, formatSnapshot } from '@/sequence/stateSnapshot';

const snapshot = captureSequenceSnapshot(state, board);
console.log(formatSnapshot(snapshot));
```

Example output:
```
=== Sequence Snapshot (2025-11-13T09:30:00.000Z) ===

Anchor: 5 at (2,3)
Next Target: 6
Legal Targets: 3 positions
Guide Enabled: true

Chain: 1..5 (length 5)
Change Reason: placement

Board: 8 filled (3 given), 56 empty
```

## Migration Notes
Remove old number picker component references; ensure no code attempts direct arbitrary number assignment.
