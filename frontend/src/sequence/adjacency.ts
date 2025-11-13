/**
 * Adjacency utilities for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { Position, BoardCell } from './types';

/**
 * Get all adjacent positions (8-way connectivity, excluding self)
 * @param pos - Current position
 * @param rows - Number of rows in grid
 * @param cols - Number of columns in grid
 * @returns Array of valid adjacent positions
 */
export function getAdjacents(
  pos: Position,
  rows: number,
  cols: number
): Position[] {
  const adjacents: Position[] = [];

  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      // Skip self
      if (dr === 0 && dc === 0) continue;

      const r = pos.row + dr;
      const c = pos.col + dc;

      // Check bounds
      if (r >= 0 && r < rows && c >= 0 && c < cols) {
        adjacents.push({ row: r, col: c });
      }
    }
  }

  return adjacents;
}

/**
 * Filter adjacent positions to only empty, non-blocked cells
 * @param adjacents - Array of adjacent positions
 * @param board - 2D board grid
 * @returns Filtered array of legal empty positions
 */
export function filterEmptyAdjacents(
  adjacents: Position[],
  board: BoardCell[][]
): Position[] {
  return adjacents.filter((pos) => {
    const cell = board[pos.row][pos.col];
    return cell.value === null && !cell.blocked;
  });
}

/**
 * Get legal empty adjacent cells for a position
 * @param pos - Current position
 * @param board - 2D board grid
 * @returns Array of legal empty adjacent positions
 */
export function getLegalAdjacents(
  pos: Position,
  board: BoardCell[][]
): Position[] {
  const rows = board.length;
  const cols = board[0]?.length ?? 0;
  const adjacents = getAdjacents(pos, rows, cols);
  return filterEmptyAdjacents(adjacents, board);
}

/**
 * Check if two positions are equal
 */
export function positionsEqual(a: Position, b: Position): boolean {
  return a.row === b.row && a.col === b.col;
}

/**
 * Check if two positions are adjacent (8-way)
 */
export function areAdjacent(a: Position, b: Position): boolean {
  const dr = Math.abs(a.row - b.row);
  const dc = Math.abs(a.col - b.col);
  return (dr <= 1 && dc <= 1) && !(dr === 0 && dc === 0);
}
