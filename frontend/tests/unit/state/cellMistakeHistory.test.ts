import { describe, it, expect } from 'vitest';
import {
  markHistoryFromSnapshots,
  markHistoryFromSequenceBoard,
  markHistoryFromGrid,
} from '@/state/cellMistakeHistory';
import type { Puzzle } from '@/domain/puzzle';
import type { SequenceBoardCell } from '@/sequence/types';
import { createEmptyGrid } from '@/domain/grid';

const samplePuzzle: Puzzle = {
  id: 'demo',
  pack_id: 'pack',
  size: 2,
  difficulty: 'easy',
  seed: 1,
  clue_count: 2,
  givens: [{ row: 0, col: 0, value: 1 }],
  solution: [
    { row: 0, col: 0, value: 1 },
    { row: 0, col: 1, value: 2 },
    { row: 1, col: 0, value: 3 },
    { row: 1, col: 1, value: 4 },
  ],
};

const baseBoardCell = {
  blocked: false,
  highlighted: false,
  anchor: false,
  mistake: false,
};

describe('cell mistake history helpers', () => {
  it('marks incorrect snapshots and ignores correct placements', () => {
    const initial = markHistoryFromSnapshots(samplePuzzle, {}, [
      { row: 0, col: 1, value: 99, given: false },
    ]);
    expect(initial['0,1']).toBe(true);

    // Correct placements should not mutate history reference
    const next = markHistoryFromSnapshots(samplePuzzle, initial, [
      { row: 0, col: 1, value: 2, given: false },
    ]);
    expect(next).toBe(initial);
  });

  it('detects mistakes from a guided sequence board snapshot', () => {
    const board: SequenceBoardCell[][] = [
      [
        {
          ...baseBoardCell,
          position: { row: 0, col: 0 },
          value: 1,
          given: true,
        },
        {
          ...baseBoardCell,
          position: { row: 0, col: 1 },
          value: 5,
          given: false,
        },
      ],
      [
        {
          ...baseBoardCell,
          position: { row: 1, col: 0 },
          value: 3,
          given: false,
        },
        {
          ...baseBoardCell,
          position: { row: 1, col: 1 },
          value: null,
          given: false,
        },
      ],
    ];

    const history = markHistoryFromSequenceBoard(samplePuzzle, {}, board);
    expect(history['0,1']).toBe(true);
    expect(history['1,0']).toBeUndefined();
  });

  it('derives mistakes from the classic grid representation', () => {
    const grid = createEmptyGrid(2);
    grid.cells[0][0].given = true;
    grid.cells[0][0].value = 1;
    grid.cells[0][1].value = 9;
    grid.cells[1][0].value = 3;

    const history = markHistoryFromGrid(samplePuzzle, {}, grid);
    expect(history['0,1']).toBe(true);
    expect(history['1,0']).toBeUndefined();
  });
});
