/**
 * Grid domain model for Hidato puzzle state.
 */

export interface Cell {
  row: number;
  col: number;
  given: boolean;
  value: number | null;
  candidates: number[];
}

export interface Grid {
  size: number;
  cells: Cell[][];
}

/**
 * Create an empty grid of given size.
 */
export function createEmptyGrid(size: number): Grid {
  const cells: Cell[][] = [];
  for (let row = 0; row < size; row++) {
    cells[row] = [];
    for (let col = 0; col < size; col++) {
      cells[row][col] = {
        row,
        col,
        given: false,
        value: null,
        candidates: [],
      };
    }
  }
  return { size, cells };
}

/**
 * Get a cell from the grid safely.
 */
export function getCell(grid: Grid, row: number, col: number): Cell | null {
  if (row < 0 || row >= grid.size || col < 0 || col >= grid.size) {
    return null;
  }
  return grid.cells[row][col];
}

/**
 * Check if a position is within grid bounds.
 */
export function isInBounds(grid: Grid, row: number, col: number): boolean {
  return row >= 0 && row < grid.size && col >= 0 && col < grid.size;
}

/**
 * Get all 8-neighbor positions for a cell.
 */
export function getNeighbors(
  grid: Grid,
  row: number,
  col: number
): Array<{ row: number; col: number }> {
  const neighbors: Array<{ row: number; col: number }> = [];
  for (let dr = -1; dr <= 1; dr++) {
    for (let dc = -1; dc <= 1; dc++) {
      if (dr === 0 && dc === 0) continue;
      const nr = row + dr;
      const nc = col + dc;
      if (isInBounds(grid, nr, nc)) {
        neighbors.push({ row: nr, col: nc });
      }
    }
  }
  return neighbors;
}
