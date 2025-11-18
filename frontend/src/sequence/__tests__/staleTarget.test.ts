/**
 * Unit tests for stale target detection and recovery
 */

import { describe, it, expect } from 'vitest';
import {
  detectStaleTarget,
  recoverFromStaleState,
  isNeutralState,
  canResumeFromNeutral,
} from '../staleTarget';
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
        given: value !== null && value <= 3,
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

describe('stale target detection', () => {
  describe('detectStaleTarget', () => {
    it('returns not stale when nextTarget is null', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const state: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 1,
        chainLength: 1,
        nextTargetChangeReason: 'neutral',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(false);
    });

    it('detects stale when anchor is null but nextTarget exists', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const state: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: 2, // Stale!
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 1,
        chainLength: 1,
        nextTargetChangeReason: 'placement',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(true);
      expect(result.reason).toBe('anchor-invalid');
      expect(result.recoveredState?.nextTarget).toBe(null);
    });

    it('detects stale when anchor cell value changed', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
      ]));
      const state: SequenceState = {
        anchorValue: 5, // Board has 2, not 5!
        anchorPos: { row: 0, col: 1 },
        nextTarget: 6,
        legalTargets: [{ row: 0, col: 2 }],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 2,
        chainLength: 2,
        nextTargetChangeReason: 'placement',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(true);
      expect(result.reason).toBe('anchor-invalid');
    });

    it('detects stale when computed nextTarget differs', () => {
      // Board has 1,2,3 but state thinks nextTarget is 5
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]));
      const state: SequenceState = {
        anchorValue: 3,
        anchorPos: { row: 0, col: 2 },
        nextTarget: 5, // Should be 4!
        legalTargets: [{ row: 0, col: 3 }],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 3,
        chainLength: 3,
        nextTargetChangeReason: 'placement',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(true);
      expect(result.reason).toBe('chain-mutated');
      expect(result.recoveredState?.nextTarget).toBe(4);
    });

    it('detects stale when nextTarget should be null', () => {
      // Anchor surrounded by filled cells, no legal targets
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 5],
        ['0,2', 6],
        ['1,0', 2],
        ['1,1', 3], // Anchor
        ['1,2', 7],
        ['2,0', 8],
        ['2,1', 9],
        ['2,2', 10],
      ]));
      const state: SequenceState = {
        anchorValue: 3,
        anchorPos: { row: 1, col: 1 },
        nextTarget: 4, // Should be null (no legal targets)
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 3,
        chainLength: 3,
        nextTargetChangeReason: 'placement',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(true);
      expect(result.reason).toBe('target-unreachable');
      expect(result.recoveredState?.nextTarget).toBe(null);
    });

    it('returns not stale for valid state', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
      ]));
      const state: SequenceState = {
        anchorValue: 2,
        anchorPos: { row: 0, col: 1 },
        nextTarget: 3,
        legalTargets: [
          { row: 0, col: 2 },
          { row: 1, col: 0 },
          { row: 1, col: 1 },
          { row: 1, col: 2 },
        ],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 2,
        chainLength: 2,
        nextTargetChangeReason: 'placement',
      };

      const result = detectStaleTarget(state, board, 25);
      expect(result.isStale).toBe(false);
    });
  });

  describe('recoverFromStaleState', () => {
    it('returns recovered state when stale', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const staleState: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: 2, // Stale
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 1,
        chainLength: 1,
        nextTargetChangeReason: 'placement',
      };

      const recovered = recoverFromStaleState(staleState, board, 25);
      expect(recovered.nextTarget).toBe(null);
      expect(recovered.nextTargetChangeReason).toBe('neutral');
    });

    it('returns same state when not stale', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const validState: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 1,
        chainLength: 1,
        nextTargetChangeReason: 'neutral',
      };

      const result = recoverFromStaleState(validState, board, 25);
      expect(result).toEqual(validState);
    });
  });

  describe('isNeutralState', () => {
    it('returns true for neutral state', () => {
      const state: SequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 5,
        chainLength: 5,
        nextTargetChangeReason: 'neutral',
      };

      expect(isNeutralState(state)).toBe(true);
    });

    it('returns false when anchor exists', () => {
      const state: SequenceState = {
        anchorValue: 5,
        anchorPos: { row: 0, col: 0 },
        nextTarget: 6,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 5,
        chainLength: 5,
        nextTargetChangeReason: 'placement',
      };

      expect(isNeutralState(state)).toBe(false);
    });
  });

  describe('canResumeFromNeutral', () => {
    it('returns true when chain exists and can extend', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]));

      expect(canResumeFromNeutral(board, 25)).toBe(true);
    });

    it('returns false for empty board', () => {
      const board = createTestBoard(new Map());
      expect(canResumeFromNeutral(board, 25)).toBe(false);
    });

    it('returns false when chain cannot extend', () => {
      // Chain 1-3 but all adjacents of 3 are blocked
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
        ['0,3', 10],
        ['1,1', 11],
        ['1,2', 12],
        ['1,3', 13],
      ]));

      expect(canResumeFromNeutral(board, 25)).toBe(false);
    });
  });
});
