# Integration Guide: Guided Sequence Flow

## Current Status

✅ **Feature Implementation:** 100% complete (69/69 tests passing)  
❌ **UI Integration:** Not yet integrated into main game UI

## Problem

The guided sequence flow feature is fully implemented in `src/sequence/` but the main game UI (`src/pages/index.tsx`, `src/components/Grid/Grid.tsx`) still uses the old `useGameStore` approach. The new UI components and hook are not connected to the game.

## Solution: Integration Steps

### Step 1: Update Grid Component

Replace `src/components/Grid/Grid.tsx` to use `useGuidedSequenceFlow`:

```tsx
import { useGuidedSequenceFlow } from '@/sequence';
import { SequenceAnnouncer } from '@/sequence/components';
import type { Position } from '@/sequence/types';

export default function Grid() {
  const puzzle = useGameStore((state) => state.puzzle);
  
  // Initialize guided sequence flow
  const {
    state,
    board,
    selectAnchor,
    placeNext,
    removeCell,
    undo,
    redo,
    canUndo,
    canRedo,
    recentMistakes,
  } = useGuidedSequenceFlow(
    puzzle.size,
    puzzle.size,
    puzzle.givens, // Map of given cell positions & values
    puzzle.maxValue
  );

  const handleCellClick = (row: number, col: number) => {
    const pos: Position = { row, col };
    const cell = board[row][col];
    
    // If cell has a value, select it as anchor
    if (cell.value !== null) {
      selectAnchor(pos);
    }
    // If cell is empty and is a legal target, place next value
    else if (state.legalTargets.some(t => t.row === row && t.col === col)) {
      placeNext(pos);
    }
  };

  // Render board cells with highlights...
  // Apply cell.anchor, cell.highlighted, cell.mistake flags to styling
}
```

### Step 2: Add UI Components

Import and use the guided sequence UI components:

```tsx
// In your main page or Grid component
import {
  NextNumberIndicator,
  HighlightLayer,
  MistakeBadge,
  SequenceAnnouncer,
} from '@/sequence/components';

// Render alongside Grid:
<>
  <NextNumberIndicator
    nextTarget={state.nextTarget}
    changeReason={state.nextTargetChangeReason}
  />
  
  <div className="relative">
    <Grid />
    <HighlightLayer
      legalTargets={state.legalTargets}
      anchorPos={state.anchorPos}
      board={board}
    />
  </div>
  
  <MistakeBadge
    mistakes={recentMistakes}
    onDismiss={() => {/* handle dismiss */}}
  />
  
  <SequenceAnnouncer
    state={state}
    board={board}
    recentMistakes={recentMistakes}
  />
</>
```

### Step 3: Update Game Store (Optional)

Either:

**Option A:** Keep both stores separate
- `useGameStore` for puzzle loading/persistence
- `useGuidedSequenceFlow` for gameplay state

**Option B:** Integrate into gameStore
- Add guided sequence state to Zustand store
- Wrap `useGuidedSequenceFlow` actions in store actions

### Step 4: Add Keyboard Navigation (Accessibility)

```tsx
import { useKeyboardNavigation } from '@/sequence';

const {
  focusedTarget,
  focusedIndex,
  handleKeyDown,
} = useKeyboardNavigation(state.legalTargets, placeNext);

// Add to your component:
<div onKeyDown={handleKeyDown} tabIndex={0}>
  <Grid />
</div>
```

### Step 5: Style the Board Cells

Apply the board cell flags to your cell rendering:

```tsx
// In your cell rendering loop
const cell = board[row][col];

<rect
  fill={
    cell.anchor ? 'yellow' :
    cell.highlighted ? 'lightblue' :
    cell.mistake ? 'pink' :
    cell.given ? 'lightgray' : 'white'
  }
  stroke={
    cell.anchor ? 'gold' :
    cell.mistake ? 'red' :
    'gray'
  }
  onClick={() => handleCellClick(row, col)}
/>
```

### Step 6: Test the Integration

1. Run `npm run dev`
2. Click a given number (should become anchor - yellow highlight)
3. Adjacent empty cells should be highlighted (legal targets)
4. Click a legal target (should place next number)
5. Press Ctrl+Z to undo
6. Try removing a value (should enter neutral state)

## Quick Integration Example

Here's a minimal working example for `src/pages/index.tsx`:

```tsx
import { useGuidedSequenceFlow } from '@/sequence';
import { SequenceAnnouncer, NextNumberIndicator } from '@/sequence/components';

export default function HomePage() {
  const puzzle = useGameStore((state) => state.puzzle);
  
  const {
    state,
    board,
    selectAnchor,
    placeNext,
    removeCell,
    undo,
    redo,
    canUndo,
    canRedo,
  } = useGuidedSequenceFlow(
    puzzle.size,
    puzzle.size,
    puzzle.givens,
    puzzle.maxValue
  );

  return (
    <main>
      <NextNumberIndicator
        nextTarget={state.nextTarget}
        changeReason={state.nextTargetChangeReason}
      />
      
      {/* Use board state from guided flow instead of gameStore.grid */}
      <Grid
        board={board}
        onCellClick={(row, col) => {
          const cell = board[row][col];
          if (cell.value !== null) {
            selectAnchor({ row, col });
          } else if (state.legalTargets.some(t => t.row === row && t.col === col)) {
            placeNext({ row, col });
          }
        }}
      />
      
      <div className="flex gap-2">
        <button onClick={undo} disabled={!canUndo}>Undo</button>
        <button onClick={redo} disabled={!canRedo}>Redo</button>
      </div>
      
      <SequenceAnnouncer
        state={state}
        board={board}
        recentMistakes={[]}
      />
    </main>
  );
}
```

## Data Format Conversion

The hook expects givens in a specific format:

```typescript
// Convert puzzle.givens (however they're stored) to Map<string, number>
const givensMap = new Map<string, number>();
puzzle.cells.forEach((row, r) => {
  row.forEach((cell, c) => {
    if (cell.given && cell.value !== null) {
      givensMap.set(`${r},${c}`, cell.value);
    }
  });
});

// Pass to hook:
useGuidedSequenceFlow(rows, cols, givensMap, maxValue);
```

## Checklist

- [ ] Update Grid component to use `useGuidedSequenceFlow`
- [ ] Add NextNumberIndicator to show current target
- [ ] Add HighlightLayer for legal target hints
- [ ] Add MistakeBadge for error feedback
- [ ] Add SequenceAnnouncer for accessibility
- [ ] Update cell click handlers (anchor select vs place next)
- [ ] Add keyboard navigation support
- [ ] Style cells based on `board[r][c]` flags (anchor, highlighted, mistake)
- [ ] Test full flow: select anchor → place values → undo/redo
- [ ] Test neutral state: remove tail → select new anchor

## Next Steps After Integration

1. **Test the UI** with real puzzles
2. **Adjust styling** to match your design system
3. **Add user preferences** (toggle guide on/off)
4. **Performance profiling** on large boards (15x15)
5. **Cross-browser testing**

## Need Help?

Refer to:
- `src/sequence/__tests__/integration.test.ts` - Full flow examples
- `docs/specs/001-guided-sequence-flow/quickstart.md` - API reference
- `docs/specs/001-guided-sequence-flow/api-reference.md` - Complete TypeScript API docs
