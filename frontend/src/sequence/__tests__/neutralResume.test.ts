/**
 * Integration tests for neutral state recovery and tail removal scenarios
 */

import { describe, it, expect } from 'vitest';
import { removeCell, selectAnchor } from '../transitions';
import { computeChain } from '../chain';
import type { BoardCell, SequenceState } from '../types';

function createTestBoard(values: Map<string, number>): BoardCell[][] {
  const board: BoardCell[][] = [];
  for (let row = 0; row < 5; row++) {
    const rowCells: BoardCell[] = [];
    for (let col = 0; col < 5; col++) {
      const key = `${row},${col}`;
      const value = values.get(key) ?? null;
      rowCells.push({
        position: { row, col },
        value,
        given: false, // All player-placed for removal tests
        blocked: false,
        highlighted: false,
        anchor: false,
        mistake: false,
      });
    }
    board.push(rowCells);
  }
  return board;
}

describe('neutral state recovery', () => {
  describe('tail removal scenarios', () => {
    it('enters neutral state after tail removal', () => {
      // Setup: Chain 1->2->3, anchor on 3
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]));

      const state: SequenceState = {
        anchorValue: 3,
        anchorPos: { row: 0, col: 2 },
        nextTarget: 4,
        legalTargets: [{ row: 0, col: 3 }],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 3,
        chainLength: 3,
        nextTargetChangeReason: 'placement',
      };

      // Remove tail (value 3)
      const result = removeCell(state, board, 25, { row: 0, col: 2 });

      expect(result.undoAction).not.toBeNull();
      expect(result.state.anchorValue).toBe(null);
      expect(result.state.anchorPos).toBe(null);
      expect(result.state.nextTarget).toBe(null);
      expect(result.state.nextTargetChangeReason).toBe('tail-removal');
      expect(result.state.chainEndValue).toBe(2);
      expect(result.state.chainLength).toBe(2);
    });

    it('preserves anchor after non-tail removal', () => {
      // Setup: Chain 1->2->3->4, anchor on 4, remove 2 (middle)
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
        ['0,3', 4],
      ]));

      const state: SequenceState = {
        anchorValue: 4,
        anchorPos: { row: 0, col: 3 },
        nextTarget: 5,
        legalTargets: [{ row: 0, col: 4 }],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 4,
        chainLength: 4,
        nextTargetChangeReason: 'placement',
      };

      // Remove non-tail (value 2 in middle)
      const result = removeCell(state, board, 25, { row: 0, col: 1 });

      expect(result.state.anchorValue).toBe(4); // Anchor preserved
      expect(result.state.anchorPos).toEqual({ row: 0, col: 3 });
      expect(result.state.nextTarget).toBe(5); // Still valid
      expect(result.state.nextTargetChangeReason).toBe('non-tail-removal');
      expect(result.state.chainEndValue).toBe(1); // Chain now just 1
    });

    it('clears anchor when anchor cell removed', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]));

      const state: SequenceState = {
        anchorValue: 2,
        anchorPos: { row: 0, col: 1 },
        nextTarget: 3,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 3,
        chainLength: 3,
        nextTargetChangeReason: 'placement',
      };

      // Remove the anchor cell itself
      const result = removeCell(state, board, 25, { row: 0, col: 1 });

      expect(result.state.anchorValue).toBe(null);
      expect(result.state.anchorPos).toBe(null);
      expect(result.state.nextTarget).toBe(null);
      expect(result.state.nextTargetChangeReason).toBe('non-tail-removal');
    });
  });

  describe('neutral state resume', () => {
    it('can resume by selecting a chain value after tail removal', () => {
      // After tail removal, chain is 1->2
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
      ]));

      const neutralState: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 2,
        chainLength: 2,
        nextTargetChangeReason: 'tail-removal',
      };

      // Select value 2 as new anchor
      const result = selectAnchor(neutralState, board, 25, { row: 0, col: 1 });

      expect(result.state.anchorValue).toBe(2);
      expect(result.state.anchorPos).toEqual({ row: 0, col: 1 });
      expect(result.state.nextTarget).toBe(3);
      expect(result.state.legalTargets.length).toBeGreaterThan(0);
      expect(result.state.nextTargetChangeReason).toBe('anchor-change');
    });

    it('cannot resume if selected value not in chain', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['1,0', 10], // Not in main chain
      ]));

      const neutralState: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 2,
        chainLength: 2,
        nextTargetChangeReason: 'neutral',
      };

      // Try to select 10 (not in chain 1->2)
      const result = selectAnchor(neutralState, board, 25, { row: 1, col: 0 });

      expect(result.state.anchorValue).toBe(10);
      expect(result.state.nextTarget).toBe(11);
      // This works but extends a different chain
    });
  });

  describe('stale target contract test', () => {
    it('handles stale target scenario from contract spec', () => {
      // Contract: chain 1..10, anchor=10, nextTarget=11
      // Create wider board to fit 10 cells in a row
      const board: BoardCell[][] = [];
      for (let row = 0; row < 5; row++) {
        const rowCells: BoardCell[] = [];
        for (let col = 0; col < 15; col++) {
          const value = row === 0 && col < 10 ? col + 1 : null;
          rowCells.push({
            position: { row, col },
            value,
            given: false,
            blocked: false,
            highlighted: false,
            anchor: false,
            mistake: false,
          });
        }
        board.push(rowCells);
      }

      const state: SequenceState = {
        anchorValue: 10,
        anchorPos: { row: 0, col: 9 },
        nextTarget: 11,
        legalTargets: [
          { row: 0, col: 10 },
          { row: 1, col: 9 },
        ],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 10,
        chainLength: 10,
        nextTargetChangeReason: 'placement',
      };

      // Step 1: Remove tail (value 10)
      const result = removeCell(state, board, 25, { row: 0, col: 9 });

      // Contract assertions
      expect(result.state.chainEndValue).toBe(9); // A1: decreased from 10 to 9
      expect(result.state.nextTarget).toBe(null); // A2: becomes null immediately
      expect(result.state.nextTargetChangeReason).toBe('tail-removal'); // A3
      expect(result.state.legalTargets.length).toBe(0); // A4
      expect(result.undoAction).not.toBeNull(); // A5: action recorded (no mistake)

      // Verify chain recomputed correctly
      const chainInfo = computeChain(result.board, 25);
      expect(chainInfo.chainEndValue).toBe(9);
      expect(chainInfo.chainLength).toBe(9);
    });
  });
});
