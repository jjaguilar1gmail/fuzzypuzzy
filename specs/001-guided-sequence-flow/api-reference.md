# Guided Sequence Flow - API Reference

Complete TypeScript API documentation for the guided sequence flow feature.

---

## Table of Contents

- [Main Hook](#main-hook)
- [Types](#types)
- [Core Utilities](#core-utilities)
- [Validation](#validation)
- [State Management](#state-management)
- [Components](#components)
- [Keyboard Navigation](#keyboard-navigation)
- [Visual Effects](#visual-effects)

---

## Main Hook

### `useGuidedSequenceFlow`

Main React hook for intelligent placement guidance.

```typescript
function useGuidedSequenceFlow(
  rows: number,
  cols: number,
  givens: Map<string, number>,
  maxValue: number
): GuidedSequenceFlowAPI
```

**Parameters:**
- `rows`: Board height
- `cols`: Board width
- `givens`: Map of given cell values (key format: `"row,col"`)
- `maxValue`: Maximum value in puzzle (typically `rows * cols`)

**Returns:** `GuidedSequenceFlowAPI` object

**Example:**
```typescript
const {
  state,
  board,
  selectAnchor,
  placeNext,
  removeCell,
  toggleGuide,
  undo,
  redo,
  canUndo,
  canRedo,
  recentMistakes,
} = useGuidedSequenceFlow(5, 5, givensMap, 25);
```

---

### `GuidedSequenceFlowAPI`

Return type of `useGuidedSequenceFlow` hook.

```typescript
interface GuidedSequenceFlowAPI {
  /** Current sequence state */
  state: SequenceState;
  
  /** Current board with highlighting flags */
  board: BoardCell[][];
  
  /** Select a cell value as anchor */
  selectAnchor: (pos: Position) => void;
  
  /** Place next sequential value */
  placeNext: (pos: Position) => void;
  
  /** Remove a player-placed cell */
  removeCell: (pos: Position) => void;
  
  /** Toggle visual guidance */
  toggleGuide: (enabled: boolean) => void;
  
  /** Undo last action */
  undo: () => void;
  
  /** Redo last undone action */
  redo: () => void;
  
  /** Whether undo is available */
  canUndo: boolean;
  
  /** Whether redo is available */
  canRedo: boolean;
  
  /** Recent validation errors (ring buffer, max 20) */
  recentMistakes: MistakeEvent[];
}
```

---

## Types

### `Position`

```typescript
interface Position {
  row: number;
  col: number;
}
```

### `BoardCell`

```typescript
interface BoardCell {
  /** Cell position */
  position: Position;
  
  /** Cell value (null if empty) */
  value: number | null;
  
  /** Whether this is a given (immutable) value */
  given: boolean;
  
  /** Whether cell is blocked from placement */
  blocked: boolean;
  
  /** Whether cell should be visually highlighted */
  highlighted: boolean;
  
  /** Whether this is the current anchor cell */
  anchor: boolean;
  
  /** Whether cell has a recent mistake */
  mistake: boolean;
}
```

### `SequenceState`

```typescript
interface SequenceState {
  /** Current anchor value (null if no anchor) */
  anchorValue: number | null;
  
  /** Current anchor position */
  anchorPos: Position | null;
  
  /** Next value to place (null if can't extend) */
  nextTarget: number | null;
  
  /** Valid positions for next placement */
  legalTargets: Position[];
  
  /** Whether visual guidance is enabled */
  guideEnabled: boolean;
  
  /** Highest contiguous value from 1 */
  chainEndValue: number | null;
  
  /** Count of contiguous values in chain */
  chainLength: number;
  
  /** Reason for last nextTarget change */
  nextTargetChangeReason: NextTargetChangeReason;
}
```

### `NextTargetChangeReason`

```typescript
type NextTargetChangeReason =
  | 'initial'           // Hook initialization
  | 'placement'         // Successful placeNext
  | 'anchor-change'     // New anchor selected
  | 'tail-removal'      // Removed chain tail
  | 'non-tail-removal'  // Removed non-tail cell
  | 'neutral';          // No anchor/target
```

### `MistakeEvent`

```typescript
interface MistakeEvent {
  /** Position where mistake occurred */
  position: Position;
  
  /** Type of validation error */
  reason: MistakeReason;
  
  /** Timestamp of mistake */
  timestamp: number;
}

type MistakeReason =
  | 'no-target'       // nextTarget is null
  | 'occupied-cell'   // Target cell already has value
  | 'not-adjacent';   // Target cell not adjacent to anchor
```

### `UndoAction`

```typescript
interface UndoAction {
  /** Type of action */
  type: UndoActionType;
  
  /** State snapshot before action */
  before: SequenceSnapshot;
  
  /** State snapshot after action */
  after: SequenceSnapshot;
}

type UndoActionType = 'placement' | 'removal';

interface SequenceSnapshot {
  board: BoardCell[][];
  state: SequenceState;
}
```

### `ChainInfo`

```typescript
interface ChainInfo {
  /** Highest contiguous value from 1 */
  chainEndValue: number | null;
  
  /** Count of contiguous values */
  chainLength: number;
  
  /** Next value that could extend chain (null if N/A) */
  nextCandidate: number | null;
}
```

---

## Core Utilities

### Chain Computation

#### `computeChain`

Compute longest consecutive chain starting from 1.

```typescript
function computeChain(
  board: BoardCell[][],
  maxValue: number
): ChainInfo
```

**Example:**
```typescript
const chainInfo = computeChain(board, 25);
// { chainEndValue: 10, chainLength: 10, nextCandidate: 11 }
```

#### `buildValuesMap`

Build map of values to positions for fast lookup.

```typescript
function buildValuesMap(
  board: BoardCell[][]
): Map<number, Position>
```

---

### Next Target Derivation

#### `deriveNextTarget`

Compute next target value based on chain end.

```typescript
function deriveNextTarget(
  chainEndValue: number | null,
  maxValue: number
): number | null
```

**Returns:** Next sequential value, or `null` if chain is complete.

#### `computeLegalTargets`

Find all valid positions for next placement.

```typescript
function computeLegalTargets(
  anchorPos: Position | null,
  nextTarget: number | null,
  board: BoardCell[][]
): Position[]
```

**Returns:** Array of positions adjacent to anchor with empty cells.

---

### Adjacency Helpers

#### `areAdjacent`

Check if two positions are adjacent (4-directional + diagonal).

```typescript
function areAdjacent(a: Position, b: Position): boolean
```

#### `getAdjacents`

Get all adjacent positions (max 8, excludes out-of-bounds).

```typescript
function getAdjacents(
  pos: Position,
  rows: number,
  cols: number,
  includeDiagonal?: boolean
): Position[]
```

**Default:** `includeDiagonal = true`

#### `getLegalAdjacents`

Filter adjacents to only empty, non-blocked cells.

```typescript
function getLegalAdjacents(
  pos: Position,
  board: BoardCell[][],
  includeDiagonal?: boolean
): Position[]
```

#### `positionsEqual`

Check if two positions are equal.

```typescript
function positionsEqual(a: Position, b: Position): boolean
```

---

## Validation

### `validatePlacement`

Pre-validate placement attempt before mutation.

```typescript
function validatePlacement(
  pos: Position,
  nextTarget: number | null,
  anchorPos: Position | null,
  board: BoardCell[][]
): MistakeEvent | null
```

**Returns:** `MistakeEvent` if invalid, `null` if valid.

**Checks:**
1. `nextTarget` is not null
2. Target cell is empty
3. Target cell is adjacent to anchor

**Example:**
```typescript
const mistake = validatePlacement(pos, state.nextTarget, state.anchorPos, board);
if (mistake) {
  console.warn('Invalid placement:', mistake.reason);
  return;
}
// Proceed with placement
```

---

### `validateRemoval`

Validate removal attempt.

```typescript
function validateRemoval(
  pos: Position,
  board: BoardCell[][]
): MistakeEvent | null
```

**Returns:** `MistakeEvent` if invalid, `null` if valid.

**Checks:**
1. Cell is not empty
2. Cell is not a given value

---

### `isInvalidEmptyCellClick`

Check if empty cell click is invalid (no target or not in legal targets).

```typescript
function isInvalidEmptyCellClick(
  pos: Position,
  nextTarget: number | null,
  legalTargets: Position[]
): boolean
```

---

## State Management

### Stale Target Detection

#### `detectStaleTarget`

Detect if displayed `nextTarget` is stale due to board changes.

```typescript
function detectStaleTarget(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number
): {
  isStale: boolean;
  reason?: 'anchor-invalid' | 'chain-mutated' | 'target-unreachable';
  recoveredState?: SequenceState;
}
```

**Stale Reasons:**
- `anchor-invalid`: Anchor cell value changed or anchor is null but nextTarget exists
- `chain-mutated`: Computed nextTarget differs from displayed nextTarget
- `target-unreachable`: No legal targets available (should be null)

---

#### `recoverFromStaleState`

Auto-recover from stale state by recomputing chain.

```typescript
function recoverFromStaleState(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number
): SequenceState
```

**Returns:** Recovered state with correct `nextTarget` and `legalTargets`.

---

### Neutral State

#### `isNeutralState`

Check if state is neutral (no anchor or target).

```typescript
function isNeutralState(state: SequenceState): boolean
```

#### `canResumeFromNeutral`

Check if chain can be extended from neutral state.

```typescript
function canResumeFromNeutral(
  board: BoardCell[][],
  maxValue: number
): boolean
```

**Returns:** `true` if chain exists and has legal targets.

---

### Undo/Redo Stack

#### `UndoRedoStack`

Stack manager for undo/redo actions.

```typescript
class UndoRedoStack {
  constructor(maxSize?: number); // Default: 50
  
  push(action: UndoAction): void;
  undo(): UndoAction | null;
  redo(): UndoAction | null;
  canUndo(): boolean;
  canRedo(): boolean;
  clear(): void;
}
```

#### `createSequenceSnapshot`

Create state snapshot for undo/redo.

```typescript
function createSequenceSnapshot(
  board: BoardCell[][],
  state: SequenceState
): SequenceSnapshot
```

#### `restoreSequenceSnapshot`

Restore state from snapshot.

```typescript
function restoreSequenceSnapshot(
  snapshot: SequenceSnapshot
): { board: BoardCell[][], state: SequenceState }
```

---

## Components

### `NextNumberIndicator`

Displays next target with animated transitions.

```typescript
interface NextNumberIndicatorProps {
  nextTarget: number | null;
  changeReason: NextTargetChangeReason;
}
```

**Usage:**
```tsx
<NextNumberIndicator 
  nextTarget={state.nextTarget}
  changeReason={state.nextTargetChangeReason}
/>
```

---

### `HighlightLayer`

Overlays legal target positions.

```typescript
interface HighlightLayerProps {
  legalTargets: Position[];
  anchorPos: Position | null;
  enabled: boolean;
}
```

**Usage:**
```tsx
<HighlightLayer
  legalTargets={state.legalTargets}
  anchorPos={state.anchorPos}
  enabled={state.guideEnabled}
/>
```

---

### `MistakeBadge`

Toast notification for mistakes (auto-fades after 1.2s).

```typescript
interface MistakeBadgeProps {
  mistakes: MistakeEvent[];
}
```

**Usage:**
```tsx
<MistakeBadge mistakes={recentMistakes} />
```

---

### `CellMistakeHighlight`

Red outline for mistake cells.

```typescript
// No props - self-contained
```

**Usage:**
```tsx
{cell.mistake && <CellMistakeHighlight />}
```

---

### `SequenceAnnouncer`

Invisible aria-live region for screen readers.

```typescript
interface SequenceAnnouncerProps {
  state: SequenceState;
  recentMistakes?: MistakeEvent[];
}
```

**Usage:**
```tsx
<SequenceAnnouncer 
  state={state}
  recentMistakes={recentMistakes}
/>
```

**Announcements:**
- Anchor selection: "Anchor set to 5. Next number is 6. 3 legal positions available."
- Placement: "Placed 5. Next number is 6. 2 legal positions."
- Mistakes: "Invalid placement. Cell is already occupied."
- Neutral state: "Tail removed. Chain now ends at 9. Select a chain value to continue."

---

## Keyboard Navigation

### `useKeyboardNavigation`

Hook for keyboard-only interaction with legal targets.

```typescript
interface KeyboardNavigationProps {
  legalTargets: Position[];
  enabled: boolean;
  onSelectTarget: (pos: Position) => void;
  onClearFocus?: () => void;
}

interface KeyboardNavigationResult {
  focusedTarget: Position | null;
  focusedIndex: number;
  focusNext: () => void;
  focusPrev: () => void;
  clearFocus: () => void;
  handleKeyDown: (e: React.KeyboardEvent) => void;
}

function useKeyboardNavigation(
  props: KeyboardNavigationProps
): KeyboardNavigationResult
```

**Keyboard Shortcuts:**
- `Tab` / `Shift+Tab`: Cycle through legal targets
- `ArrowRight` / `ArrowDown`: Next target
- `ArrowLeft` / `ArrowUp`: Previous target
- `Enter` / `Space`: Place at focused target
- `Escape`: Clear focus

**Example:**
```tsx
const { focusedTarget, handleKeyDown } = useKeyboardNavigation({
  legalTargets: state.legalTargets,
  enabled: state.guideEnabled,
  onSelectTarget: placeNext,
});

return (
  <div onKeyDown={handleKeyDown} tabIndex={0}>
    {board.map((row, r) => 
      row.map((cell, c) => (
        <Cell
          focused={focusedTarget?.row === r && focusedTarget?.col === c}
          {...cell}
        />
      ))
    )}
  </div>
);
```

---

### `isFocusedPosition`

Check if position is currently focused.

```typescript
function isFocusedPosition(
  pos: Position,
  focusedTarget: Position | null
): boolean
```

---

## Visual Effects

### `CHANGE_REASON_CSS`

String containing all keyframe definitions for state transitions.

```typescript
const CHANGE_REASON_CSS: string;
```

**Keyframes:**
- `pulse-success`: Green scale pulse (0.5s)
- `highlight-anchor`: Yellow glow pulse (1s loop)
- `fade-neutral`: Opacity fade to gray (0.3s)
- `mistakePulse`: Red shake + scale (0.4s)
- `mistakeFadeOut`: Opacity fade (1.2s)

**Usage:**
```tsx
import { CHANGE_REASON_CSS } from '@/sequence';

// Inject into global styles
<style>{CHANGE_REASON_CSS}</style>
```

---

### `getChangeReasonStyle`

Map change reason to CSS class name.

```typescript
function getChangeReasonStyle(
  reason: NextTargetChangeReason
): string
```

**Mapping:**
- `placement` → `'sequence-pulse-success'`
- `anchor-change` → `'sequence-highlight-anchor'`
- `tail-removal` → `'sequence-fade-neutral'`
- `neutral` → `''`
- Others → `''`

**Example:**
```tsx
<div className={getChangeReasonStyle(state.nextTargetChangeReason)}>
  Next: {state.nextTarget}
</div>
```

---

## Constants

```typescript
const MISTAKE_BUFFER_SIZE = 20;  // Max mistakes in ring buffer
const MAX_UNDO_STACK = 50;       // Max undo actions
```

---

## Complete Example

```tsx
import {
  useGuidedSequenceFlow,
  useKeyboardNavigation,
  NextNumberIndicator,
  HighlightLayer,
  MistakeBadge,
  SequenceAnnouncer,
  CHANGE_REASON_CSS,
} from '@/sequence';

function HidatoGame() {
  const {
    state,
    board,
    selectAnchor,
    placeNext,
    removeCell,
    toggleGuide,
    undo,
    redo,
    canUndo,
    canRedo,
    recentMistakes,
  } = useGuidedSequenceFlow(5, 5, givensMap, 25);

  const { focusedTarget, handleKeyDown } = useKeyboardNavigation({
    legalTargets: state.legalTargets,
    enabled: state.guideEnabled,
    onSelectTarget: placeNext,
  });

  return (
    <>
      <style>{CHANGE_REASON_CSS}</style>
      
      <SequenceAnnouncer state={state} recentMistakes={recentMistakes} />
      
      <div onKeyDown={handleKeyDown} tabIndex={0}>
        <HighlightLayer
          legalTargets={state.legalTargets}
          anchorPos={state.anchorPos}
          enabled={state.guideEnabled}
        />
        
        {board.map((row, r) => (
          <div key={r}>
            {row.map((cell, c) => (
              <Cell
                key={c}
                {...cell}
                focused={focusedTarget?.row === r && focusedTarget?.col === c}
                onClick={() => handleCellClick(r, c)}
                onContextMenu={() => removeCell({ row: r, col: c })}
              />
            ))}
          </div>
        ))}
      </div>
      
      <NextNumberIndicator
        nextTarget={state.nextTarget}
        changeReason={state.nextTargetChangeReason}
      />
      
      <MistakeBadge mistakes={recentMistakes} />
      
      <button onClick={undo} disabled={!canUndo}>Undo</button>
      <button onClick={redo} disabled={!canRedo}>Redo</button>
      <button onClick={() => toggleGuide(!state.guideEnabled)}>
        Toggle Guide
      </button>
    </>
  );
}
```

---

**Last Updated:** 2025-01-XX  
**Version:** Phase 4 Complete (v0.4.0)
