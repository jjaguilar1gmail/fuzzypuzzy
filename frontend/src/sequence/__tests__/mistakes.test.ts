/**
 * Unit tests for mistake detection and classification
 */

import { describe, it, expect } from 'vitest';
import { validatePlacement, validateRemoval, isInvalidEmptyCellClick } from '../mistakes';
import type { BoardCell, Position } from '../types';

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
        given: value !== null,
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

describe('mistake detection', () => {
  describe('validatePlacement', () => {
    it('returns null for valid placement', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const pos: Position = { row: 0, col: 1 };
      const anchorPos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, 2, anchorPos, board);
      expect(result).toBeNull();
    });

    it('detects no-target mistake', () => {
      const board = createTestBoard(new Map());
      const pos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, null, null, board);
      expect(result).not.toBeNull();
      expect(result?.reason).toBe('no-target');
    });

    it('detects occupied cell mistake', () => {
      const board = createTestBoard(new Map([['0,0', 1], ['0,1', 2]]));
      const pos: Position = { row: 0, col: 1 }; // Already occupied
      const anchorPos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, 3, anchorPos, board);
      expect(result).not.toBeNull();
      expect(result?.reason).toBe('occupied');
    });

    it('detects not-adjacent mistake', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const pos: Position = { row: 3, col: 3 }; // Far from anchor
      const anchorPos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, 2, anchorPos, board);
      expect(result).not.toBeNull();
      expect(result?.reason).toBe('not-adjacent');
    });

    it('accepts diagonal adjacency', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const pos: Position = { row: 1, col: 1 }; // Diagonal
      const anchorPos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, 2, anchorPos, board);
      expect(result).toBeNull();
    });

    it('rejects blocked cells', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      board[0][1].blocked = true;
      const pos: Position = { row: 0, col: 1 };
      const anchorPos: Position = { row: 0, col: 0 };

      const result = validatePlacement(pos, 2, anchorPos, board);
      expect(result).not.toBeNull();
      expect(result?.reason).toBe('occupied');
    });
  });

  describe('validateRemoval', () => {
    it('returns null for valid removal', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      board[0][0].given = false; // Make it player-placed
      const pos: Position = { row: 0, col: 0 };

      const result = validateRemoval(pos, board);
      expect(result).toBeNull();
    });

    it('rejects removal of given values', () => {
      const board = createTestBoard(new Map([['0,0', 1]]));
      const pos: Position = { row: 0, col: 0 };

      const result = validateRemoval(pos, board);
      expect(result).not.toBeNull();
      expect(result).toContain('given');
    });

    it('rejects removal from empty cell', () => {
      const board = createTestBoard(new Map());
      const pos: Position = { row: 0, col: 0 };

      const result = validateRemoval(pos, board);
      expect(result).not.toBeNull();
      expect(result).toContain('empty');
    });
  });

  describe('isInvalidEmptyCellClick', () => {
    it('returns true when no next target', () => {
      const pos: Position = { row: 0, col: 0 };
      const result = isInvalidEmptyCellClick(pos, [], null);
      expect(result).toBe(true);
    });

    it('returns true when position not in legal targets', () => {
      const pos: Position = { row: 0, col: 0 };
      const legalTargets: Position[] = [{ row: 1, col: 1 }];
      const result = isInvalidEmptyCellClick(pos, legalTargets, 2);
      expect(result).toBe(true);
    });

    it('returns false when position is in legal targets', () => {
      const pos: Position = { row: 0, col: 0 };
      const legalTargets: Position[] = [{ row: 0, col: 0 }];
      const result = isInvalidEmptyCellClick(pos, legalTargets, 2);
      expect(result).toBe(false);
    });
  });
});
