import { describe, it, expect } from 'vitest';
import { deriveNextTarget } from '@/sequence/nextTarget';
import type { BoardCell } from '@/sequence/types';

type Layout = Array<Array<number | null>>;

function buildBoard(layout: Layout): BoardCell[][] {
  return layout.map((row, rowIndex) =>
    row.map((value, colIndex) => ({
      position: { row: rowIndex, col: colIndex },
      value,
      given: value !== null,
      blocked: false,
      highlighted: false,
      anchor: false,
      mistake: false,
    }))
  );
}

describe('deriveNextTarget', () => {
  it('skips contiguous placed values (even if they lack empty neighbors) until the first missing value', () => {
    const board = buildBoard([
      [13, 14, 15, null],
      [12, 11, 10, 9],
      [5, 6, 7, 8],
      [4, 3, 2, 1],
    ]);

    const result = deriveNextTarget(13, { row: 0, col: 0 }, board, 'forward');

    expect(result.nextTarget).toBe(16);
    expect(result.newAnchorValue).toBe(15);
    expect(result.newAnchorPos).toEqual({ row: 0, col: 2 });
  });

  it('returns null if the highest contiguous value has no legal placements', () => {
    const board = buildBoard([
      [4, 5, 1],
      [9, 7, 8],
      [3, 2, null],
    ]);

    const result = deriveNextTarget(4, { row: 0, col: 0 }, board, 'forward');

    expect(result.nextTarget).toBeNull();
    expect(result.newAnchorValue).toBe(5);
    expect(result.newAnchorPos).toEqual({ row: 0, col: 1 });
  });

  it('still reports null when stepping backward lands on a value with no empty neighbors', () => {
    const board = buildBoard([
      [7, 8, 9],
      [null, 6, 5],
      [null, 3, 2],
    ]);

    const result = deriveNextTarget(3, { row: 2, col: 1 }, board, 'backward');

    expect(result.nextTarget).toBeNull();
    expect(result.newAnchorValue).toBe(2);
    expect(result.newAnchorPos).toEqual({ row: 2, col: 2 });
  });
});
