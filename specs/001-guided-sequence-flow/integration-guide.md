# Developer Integration Guide: Guided Sequence Flow

Quick reference for integrating the guided sequence flow feature into your Hidato game UI.

---

## Quick Start

### 1. Install & Import

```typescript
import {
  useGuidedSequenceFlow,
  type BoardCell,
  type SequenceState,
} from '@/sequence';
import {
  NextNumberIndicator,
  HighlightLayer,
  MistakeBadge,
  CellMistakeHighlight,
} from '@/sequence/components';
```

### 2. Initialize Hook

```typescript
const GameBoard = ({ rows, cols, givens, maxValue }) => {
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
  } = useGuidedSequenceFlow(rows, cols, givens, maxValue);

  // ... render logic
};
```

### 3. Wire Up Click Handlers

```typescript
const handleCellClick = (row: number, col: number) => {
  const cell = board[row][col];
  const pos = { row, col };

  if (cell.value !== null) {
    // Click on existing number → select as anchor
    selectAnchor(pos);
  } else if (state.nextTarget !== null) {
    // Click on empty cell → attempt placement
    placeNext(pos);
  }
  // Invalid clicks are automatically validated and rejected
};

const handleCellRightClick = (row: number, col: number) => {
  const pos = { row, col };
  removeCell(pos); // Remove player-placed cells
};
```

---

## Component Integration

### NextNumberIndicator

Displays the next number to place with animated transitions.

```tsx
<NextNumberIndicator 
  nextTarget={state.nextTarget} 
  changeReason={state.nextTargetChangeReason}
/>
```

**Props:**
- `nextTarget`: `number | null` - Next value to place (null = neutral state)
- `changeReason`: `NextTargetChangeReason` - Triggers CSS animation

**Styling:**
Apply `getChangeReasonStyle(changeReason)` for animations:
- `placement` → pulse-success (green pulse)
- `anchor-change` → highlight-anchor (yellow glow)
- `tail-removal` → fade-neutral (gray fade)
- `neutral` → no animation

---

### HighlightLayer

Overlays legal target positions on the board.

```tsx
<HighlightLayer 
  legalTargets={state.legalTargets}
  anchorPos={state.anchorPos}
  enabled={state.guideEnabled}
/>
```

**Props:**
- `legalTargets`: `Position[]` - Valid placement positions
- `anchorPos`: `Position | null` - Current anchor (for pulse effect)
- `enabled`: `boolean` - Guide visibility toggle

**Rendering:**
- Render as overlay layer (absolute positioning)
- Apply semi-transparent highlight to legal cells
- Pulse anchor cell continuously

---

### MistakeBadge

Transient toast notification for mistakes.

```tsx
<MistakeBadge mistakes={recentMistakes} />
```

**Props:**
- `mistakes`: `MistakeEvent[]` - Ring buffer of last 20 mistakes

**Behavior:**
- Displays only the most recent mistake
- Auto-fades after 1.2 seconds
- Shows localized message: "Can't place there!" / "Cell occupied!" / "Must be adjacent!"

---

### CellMistakeHighlight

Red outline for mistake cells.

```tsx
{board.map((row, r) => 
  row.map((cell, c) => (
    <Cell key={`${r}-${c}`}>
      {cell.value}
      {cell.mistake && <CellMistakeHighlight />}
    </Cell>
  ))
)}
```

**Props:** None (self-contained)

**Styling:**
- Red 2px border with shake animation
- Clears automatically after mistake buffer expires

---

## State Management

### SequenceState Fields

```typescript
interface SequenceState {
  // Anchor tracking
  anchorValue: number | null;      // Current anchor value (null = neutral)
  anchorPos: Position | null;       // Anchor position

  // Next target
  nextTarget: number | null;        // Next value to place (null = can't extend)
  legalTargets: Position[];         // Valid placement positions

  // UI state
  guideEnabled: boolean;            // Highlight visibility
  nextTargetChangeReason: NextTargetChangeReason;  // Animation trigger

  // Chain info
  chainEndValue: number;            // Highest contiguous value from 1
  chainLength: number;              // Count of contiguous values
}
```

### NextTargetChangeReason Values

| Reason | Trigger | Visual Effect |
|--------|---------|---------------|
| `initial` | Hook initialization | None |
| `placement` | Successful `placeNext` | Green pulse |
| `anchor-change` | New anchor selected | Yellow glow |
| `tail-removal` | Removed chain tail | Gray fade |
| `non-tail-removal` | Removed middle cell | None |
| `undo` | Undo action | None |
| `redo` | Redo action | None |
| `neutral` | No anchor/target | None |

---

## Validation & Mistakes

### Automatic Validation

**Pre-placement checks** (no invalid mutations):
1. **no-target**: `nextTarget` is null
2. **occupied-cell**: Target cell already has a value
3. **not-adjacent**: Target cell not adjacent to anchor

**On validation failure:**
- State unchanged (no mutation)
- `MistakeEvent` added to `recentMistakes`
- Mistake cell flagged with `mistake: true`

### Manual Validation

```typescript
import { validatePlacement, isInvalidEmptyCellClick } from '@/sequence';

// Check before custom logic
const mistake = validatePlacement(pos, state.nextTarget, state.anchorPos, board);
if (mistake) {
  console.warn('Invalid placement:', mistake.reason);
  return;
}
```

---

## Undo/Redo

### Basic Usage

```tsx
<button onClick={undo} disabled={!canUndo}>Undo</button>
<button onClick={redo} disabled={!canRedo}>Redo</button>
```

### What's Recorded

**Recorded actions:**
- `placeNext` (valid placements only)
- `removeCell` (non-given cells only)

**NOT recorded:**
- `selectAnchor` (non-mutating)
- `toggleGuide` (UI-only)
- Invalid placement attempts (mistakes)

### Stack Limits

- Max 50 actions (configurable via `MAX_UNDO_STACK`)
- LIFO stack (most recent action undone first)

---

## Stale State Recovery

### Automatic Recovery

The hook automatically detects and recovers from stale states via `useEffect`:

```typescript
useEffect(() => {
  checkAndRecoverStale();
}, [board, state.anchorValue, state.anchorPos, state.nextTarget]);
```

**Stale detection reasons:**
1. **anchor-invalid**: Anchor cell value changed or cleared
2. **chain-mutated**: Next target no longer follows chain end
3. **target-unreachable**: No legal targets available

**Recovery process:**
- Recompute chain from current board
- Update `nextTarget` and `legalTargets`
- Log warning to console (debug mode)

### Manual Recovery

```typescript
import { detectStaleTarget, recoverFromStaleState } from '@/sequence';

const check = detectStaleTarget(state, board, maxValue);
if (check.isStale) {
  console.log('Stale reason:', check.reason);
  const recovered = recoverFromStaleState(state, board, maxValue);
  setState(recovered);
}
```

---

## Neutral State Handling

### What is Neutral State?

State where no anchor exists (`anchorValue === null` && `nextTarget === null`).

**Entry conditions:**
- Tail removal (removed highest chain value)
- Anchor cell removed
- Initial state (before first anchor selected)

### Resume from Neutral

```typescript
// User clicks any chain value
if (isNeutralState(state) && canResumeFromNeutral(board, maxValue)) {
  selectAnchor(pos); // Re-establish anchor
}
```

**Resume requirements:**
- Board has contiguous chain from 1
- Chain can be extended (legal targets exist)

---

## CSS Integration

### Required Styles

Add `CHANGE_REASON_CSS` to your global stylesheet:

```typescript
import { CHANGE_REASON_CSS } from '@/sequence';

// In your CSS-in-JS or global.css
const styles = `
  ${CHANGE_REASON_CSS}
`;
```

### Keyframes Provided

- `pulse-success`: Green scale pulse (0.5s)
- `highlight-anchor`: Yellow glow pulse (1s loop)
- `fade-neutral`: Opacity fade to gray (0.3s)
- `mistakePulse`: Red shake + scale (0.4s)
- `mistakeFadeOut`: Opacity fade (1.2s)

---

## Performance Tips

### Optimization Strategies

1. **Memoize heavy computations:**
```typescript
const chainInfo = useMemo(() => computeChain(board, maxValue), [board, maxValue]);
```

2. **Throttle state updates:**
```typescript
const throttledSetState = useCallback(
  throttle((newState) => setState(newState), 16), // ~60fps
  []
);
```

3. **Virtualize large boards:**
- Use `react-window` for 15x15+ grids
- Render only visible cells

---

## Accessibility

### Screen Reader Support

```tsx
<div
  role="status"
  aria-live="polite"
  aria-atomic="true"
>
  {state.nextTarget 
    ? `Next number is ${state.nextTarget}. ${state.legalTargets.length} legal positions.`
    : 'Select a number to continue.'
  }
</div>
```

### Keyboard Navigation

```tsx
const handleKeyDown = (e: KeyboardEvent) => {
  if (e.key === 'Tab') {
    // Cycle through legalTargets
    const nextIndex = (currentLegalIndex + 1) % state.legalTargets.length;
    setFocusedCell(state.legalTargets[nextIndex]);
  } else if (e.key === 'Enter') {
    // Place at focused cell
    placeNext(focusedCell);
  } else if (e.key === 'Escape') {
    // Clear anchor
    selectAnchor(null);
  }
};
```

### High Contrast Mode

```css
@media (prefers-contrast: high) {
  .legal-target-highlight {
    border: 3px solid #000;
    background: #ff0;
  }
  
  .anchor-cell {
    outline: 4px solid #00f;
  }
}
```

---

## Testing

### Unit Test Example

```typescript
import { renderHook, act } from '@testing-library/react';
import { useGuidedSequenceFlow } from '@/sequence';

it('places next value and updates anchor', () => {
  const { result } = renderHook(() =>
    useGuidedSequenceFlow(5, 5, new Map([['0,0', 1]]), 25)
  );

  act(() => {
    result.current.selectAnchor({ row: 0, col: 0 });
  });

  expect(result.current.state.anchorValue).toBe(1);
  expect(result.current.state.nextTarget).toBe(2);

  act(() => {
    result.current.placeNext({ row: 0, col: 1 });
  });

  expect(result.current.state.anchorValue).toBe(2);
  expect(result.current.state.nextTarget).toBe(3);
});
```

---

## Common Pitfalls

### 1. Forgetting to Check `nextTarget`

❌ **Wrong:**
```typescript
const handleClick = (pos) => {
  placeNext(pos); // Will fail if nextTarget is null
};
```

✅ **Correct:**
```typescript
const handleClick = (pos) => {
  if (state.nextTarget !== null) {
    placeNext(pos);
  }
};
```

### 2. Mutating Board State

❌ **Wrong:**
```typescript
board[row][col].value = 5; // Direct mutation breaks React
```

✅ **Correct:**
```typescript
placeNext({ row, col }); // Use hook API
```

### 3. Ignoring Stale State

❌ **Wrong:**
```typescript
// Display nextTarget without checking validity
<div>{state.nextTarget}</div>
```

✅ **Correct:**
```typescript
// Hook auto-recovers, but you can still detect:
{detectStaleTarget(state, board, maxValue).isStale && <Warning />}
```

---

## FAQ

**Q: Can I have multiple anchors?**  
A: No. Single anchor per spec. To support multi-chain, extend logic in Phase 6.

**Q: What if user places wrong number?**  
A: Validation prevents non-sequential placements. Mistakes are logged but board unchanged.

**Q: How to disable guidance UI?**  
A: `toggleGuide(false)` hides highlights. State tracking continues.

**Q: Can I customize animations?**  
A: Yes. Override CSS keyframes or provide custom `getChangeReasonStyle` mapping.

**Q: What happens at chain end?**  
A: `nextTarget → null`, `legalTargets → []`. User must select new anchor or complete puzzle.

---

## Support

- **Bugs:** Open issue with test case
- **Questions:** Refer to `specs/001-guided-sequence-flow/data-model.md`
- **Feature requests:** Submit via RFC process

---

**Last Updated:** 2025-01-XX  
**Version:** Phase 3 Complete (v0.3.0)
