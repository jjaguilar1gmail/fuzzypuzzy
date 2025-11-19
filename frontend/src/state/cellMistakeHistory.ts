import { Puzzle } from '@/domain/puzzle';
import { Grid } from '@/domain/grid';
import { positionKey } from '@/domain/position';
import type { SequenceBoardCell } from '@/sequence/types';

export type CellMistakeHistory = Record<string, true>;

interface CellSnapshot {
  row: number;
  col: number;
  value: number | null;
  given?: boolean;
}

const solutionMapCache = new WeakMap<Puzzle, Map<string, number>>();

function getSolutionMap(puzzle: Puzzle | null): Map<string, number> | null {
  if (!puzzle || !Array.isArray(puzzle.solution)) {
    return null;
  }

  const cached = solutionMapCache.get(puzzle);
  if (cached) return cached;

  const map = new Map<string, number>();
  puzzle.solution.forEach(({ row, col, value }) => {
    map.set(positionKey({ row, col }), value);
  });
  solutionMapCache.set(puzzle, map);
  return map;
}

function applySnapshots(
  puzzle: Puzzle | null,
  history: CellMistakeHistory,
  snapshots: CellSnapshot[]
): CellMistakeHistory {
  if (!snapshots.length) return history;
  const solutionMap = getSolutionMap(puzzle);
  if (!solutionMap) return history;

  let mutated = false;
  let nextHistory = history;

  for (const snapshot of snapshots) {
    if (snapshot.given || snapshot.value === null) continue;
    const key = positionKey({ row: snapshot.row, col: snapshot.col });
    const expected = solutionMap.get(key);
    if (typeof expected !== 'number') continue;
    if (snapshot.value === expected || nextHistory[key]) continue;
    if (!mutated) {
      nextHistory = { ...history };
      mutated = true;
    }
    nextHistory[key] = true;
  }

  return nextHistory;
}

export function markHistoryFromSnapshots(
  puzzle: Puzzle | null,
  history: CellMistakeHistory,
  snapshots: CellSnapshot[]
): CellMistakeHistory {
  return applySnapshots(puzzle, history, snapshots);
}

export function markHistoryFromSequenceBoard(
  puzzle: Puzzle | null,
  history: CellMistakeHistory,
  board: SequenceBoardCell[][] | null
): CellMistakeHistory {
  if (!board) return history;
  const snapshots: CellSnapshot[] = [];
  for (const row of board) {
    for (const cell of row) {
      snapshots.push({
        row: cell.position.row,
        col: cell.position.col,
        value: cell.value,
        given: cell.given,
      });
    }
  }
  return applySnapshots(puzzle, history, snapshots);
}

export function markHistoryFromGrid(
  puzzle: Puzzle | null,
  history: CellMistakeHistory,
  grid: Grid | null
): CellMistakeHistory {
  if (!grid) return history;
  const snapshots: CellSnapshot[] = [];
  for (let row = 0; row < grid.size; row++) {
    for (let col = 0; col < grid.size; col++) {
      const cell = grid.cells[row][col];
      snapshots.push({
        row,
        col,
        value: cell.value,
        given: cell.given,
      });
    }
  }
  return applySnapshots(puzzle, history, snapshots);
}
