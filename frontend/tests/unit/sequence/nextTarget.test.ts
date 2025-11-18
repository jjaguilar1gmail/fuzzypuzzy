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
  it('returns null when the next contiguous value exists but has no legal moves (forward)', () => {
    const board = buildBoard([
      [1, null, 6],
      [7, 8, 9],
      [4, 5, 2],
    ]);

    const result = deriveNextTarget(1, { row: 0, col: 0 }, board, 'forward');

    expect(result.nextTarget).toBeNull();
    expect(result.newAnchorValue).toBe(1);
    expect(result.newAnchorPos).toEqual({ row: 0, col: 0 });
  });

  it('returns null when stepping backward into a landlocked value', () => {
    const board = buildBoard([
      [7, 8, 9],
      [null, 6, 5],
      [null, 3, 2],
    ]);

    const result = deriveNextTarget(3, { row: 2, col: 1 }, board, 'backward');

    expect(result.nextTarget).toBeNull();
    expect(result.newAnchorValue).toBe(3);
    expect(result.newAnchorPos).toEqual({ row: 2, col: 1 });
  });
});
