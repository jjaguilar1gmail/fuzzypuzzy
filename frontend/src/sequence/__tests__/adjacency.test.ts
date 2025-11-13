/**
 * Unit tests for adjacency utilities
 */

import { describe, it, expect } from 'vitest';
import {
  getAdjacents,
  filterEmptyAdjacents,
  getLegalAdjacents,
  positionsEqual,
  areAdjacent,
} from '../adjacency';
import type { BoardCell, Position } from '../types';

describe('adjacency utilities', () => {
  describe('getAdjacents', () => {
    it('returns 8 adjacents for center cell', () => {
      const pos: Position = { row: 4, col: 4 };
      const adjacents = getAdjacents(pos, 8, 8);
      expect(adjacents).toHaveLength(8);
    });

    it('returns 3 adjacents for corner cell', () => {
      const pos: Position = { row: 0, col: 0 };
      const adjacents = getAdjacents(pos, 8, 8);
      expect(adjacents).toHaveLength(3);
      expect(adjacents).toContainEqual({ row: 0, col: 1 });
      expect(adjacents).toContainEqual({ row: 1, col: 0 });
      expect(adjacents).toContainEqual({ row: 1, col: 1 });
    });

    it('returns 5 adjacents for edge cell', () => {
      const pos: Position = { row: 0, col: 4 };
      const adjacents = getAdjacents(pos, 8, 8);
      expect(adjacents).toHaveLength(5);
    });

    it('excludes self from adjacents', () => {
      const pos: Position = { row: 2, col: 2 };
      const adjacents = getAdjacents(pos, 8, 8);
      expect(adjacents).not.toContainEqual(pos);
    });
  });

  describe('filterEmptyAdjacents', () => {
    it('filters out occupied cells', () => {
      const board: BoardCell[][] = Array(3)
        .fill(null)
        .map((_, row) =>
          Array(3)
            .fill(null)
            .map((_, col) => ({
              position: { row, col },
              value: row === 1 && col === 1 ? 5 : null,
              given: false,
              blocked: false,
              highlighted: false,
              anchor: false,
              mistake: false,
            }))
        );

      const adjacents: Position[] = [
        { row: 0, col: 1 },
        { row: 1, col: 1 }, // Occupied
        { row: 2, col: 1 },
      ];

      const filtered = filterEmptyAdjacents(adjacents, board);
      expect(filtered).toHaveLength(2);
      expect(filtered).not.toContainEqual({ row: 1, col: 1 });
    });

    it('filters out blocked cells', () => {
      const board: BoardCell[][] = Array(3)
        .fill(null)
        .map((_, row) =>
          Array(3)
            .fill(null)
            .map((_, col) => ({
              position: { row, col },
              value: null,
              given: false,
              blocked: row === 1 && col === 1,
              highlighted: false,
              anchor: false,
              mistake: false,
            }))
        );

      const adjacents: Position[] = [
        { row: 0, col: 1 },
        { row: 1, col: 1 }, // Blocked
        { row: 2, col: 1 },
      ];

      const filtered = filterEmptyAdjacents(adjacents, board);
      expect(filtered).toHaveLength(2);
      expect(filtered).not.toContainEqual({ row: 1, col: 1 });
    });
  });

  describe('positionsEqual', () => {
    it('returns true for equal positions', () => {
      const a: Position = { row: 2, col: 3 };
      const b: Position = { row: 2, col: 3 };
      expect(positionsEqual(a, b)).toBe(true);
    });

    it('returns false for different positions', () => {
      const a: Position = { row: 2, col: 3 };
      const b: Position = { row: 2, col: 4 };
      expect(positionsEqual(a, b)).toBe(false);
    });
  });

  describe('areAdjacent', () => {
    it('returns true for horizontally adjacent', () => {
      const a: Position = { row: 2, col: 3 };
      const b: Position = { row: 2, col: 4 };
      expect(areAdjacent(a, b)).toBe(true);
    });

    it('returns true for diagonally adjacent', () => {
      const a: Position = { row: 2, col: 3 };
      const b: Position = { row: 3, col: 4 };
      expect(areAdjacent(a, b)).toBe(true);
    });

    it('returns false for non-adjacent', () => {
      const a: Position = { row: 2, col: 3 };
      const b: Position = { row: 2, col: 5 };
      expect(areAdjacent(a, b)).toBe(false);
    });

    it('returns false for self', () => {
      const a: Position = { row: 2, col: 3 };
      expect(areAdjacent(a, a)).toBe(false);
    });
  });
});
