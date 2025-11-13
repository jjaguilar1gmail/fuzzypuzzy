/**
 * Unit tests for chain detection logic
 */

import { describe, it, expect } from 'vitest';
import { computeChain, buildValuesMap } from '../chain';
import type { BoardCell } from '../types';

function createTestBoard(values: Map<string, number>): BoardCell[][] {
  const board: BoardCell[][] = [];
  for (let row = 0; row < 8; row++) {
    const rowCells: BoardCell[] = [];
    for (let col = 0; col < 8; col++) {
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

describe('chain detection', () => {
  describe('buildValuesMap', () => {
    it('builds map of values to positions', () => {
      const values = new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['1,0', 3],
      ]);
      const board = createTestBoard(values);
      const valuesMap = buildValuesMap(board);

      expect(valuesMap.size).toBe(3);
      expect(valuesMap.get(1)).toEqual({ row: 0, col: 0 });
      expect(valuesMap.get(2)).toEqual({ row: 0, col: 1 });
      expect(valuesMap.get(3)).toEqual({ row: 1, col: 0 });
    });
  });

  describe('computeChain', () => {
    it('returns empty chain for empty board', () => {
      const board = createTestBoard(new Map());
      const chainInfo = computeChain(board, 20);

      expect(chainInfo.chainEndValue).toBe(null);
      expect(chainInfo.chainLength).toBe(0);
      expect(chainInfo.nextCandidate).toBe(null);
    });

    it('detects contiguous chain starting at 1', () => {
      const values = new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]);
      const board = createTestBoard(values);
      const chainInfo = computeChain(board, 20);

      expect(chainInfo.chainEndValue).toBe(3);
      expect(chainInfo.chainLength).toBe(3);
      expect(chainInfo.nextCandidate).toBe(4);
    });

    it('stops chain at first gap', () => {
      const values = new Map([
        ['0,0', 1],
        ['0,1', 2],
        // Gap: no 3
        ['1,0', 4],
      ]);
      const board = createTestBoard(values);
      const chainInfo = computeChain(board, 20);

      expect(chainInfo.chainEndValue).toBe(2);
      expect(chainInfo.chainLength).toBe(2);
    });

    it('starts chain at minimum value if 1 not present', () => {
      const values = new Map([
        ['0,0', 5],
        ['0,1', 6],
        ['0,2', 7],
      ]);
      const board = createTestBoard(values);
      const chainInfo = computeChain(board, 20);

      expect(chainInfo.chainEndValue).toBe(7);
      expect(chainInfo.chainLength).toBe(3);
    });

    it('returns null nextCandidate when no legal adjacency', () => {
      // Chain end has no empty adjacent cells
      const values = new Map([
        ['0,0', 1],
        ['0,1', 5], // Block all adjacents of 1
        ['1,0', 6],
        ['1,1', 7],
      ]);
      const board = createTestBoard(values);
      const chainInfo = computeChain(board, 20);

      expect(chainInfo.chainEndValue).toBe(1);
      expect(chainInfo.nextCandidate).toBe(null);
    });

    it('returns null nextCandidate when chainEnd equals maxValue', () => {
      const values = new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]);
      const board = createTestBoard(values);
      const chainInfo = computeChain(board, 3); // maxValue = 3

      expect(chainInfo.chainEndValue).toBe(3);
      expect(chainInfo.nextCandidate).toBe(null);
    });
  });
});
