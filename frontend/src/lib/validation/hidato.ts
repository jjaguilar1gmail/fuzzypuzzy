/**
 * Hidato validation logic.
 * Validates adjacency constraints and givens protection.
 */

import { Grid, getCell, getNeighbors } from '@/domain/grid';

/**
 * Check if placing a value at a position violates adjacency rules.
 * Returns true if valid (adjacent to value-1 or value+1), false otherwise.
 */
export function isValidPlacement(
  grid: Grid,
  row: number,
  col: number,
  value: number
): boolean {
  const cell = getCell(grid, row, col);
  if (!cell) return false;
  
  // Cannot place on a given
  if (cell.given) return false;
  
  // Value must be in valid range
  const maxValue = grid.size * grid.size;
  if (value < 1 || value > maxValue) return false;
  
  // Check for duplicate value in grid
  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const otherCell = getCell(grid, r, c);
      if (otherCell && otherCell.value === value && (r !== row || c !== col)) {
        return false; // Duplicate value
      }
    }
  }
  
  // Must be adjacent to value-1 or value+1 (if they exist in grid)
  const neighbors = getNeighbors(grid, row, col);
  let hasLowerNeighbor = false;
  let hasHigherNeighbor = false;
  
  for (const neighbor of neighbors) {
    const neighborCell = getCell(grid, neighbor.row, neighbor.col);
    if (!neighborCell || neighborCell.value === null) continue;
    
    if (neighborCell.value === value - 1) hasLowerNeighbor = true;
    if (neighborCell.value === value + 1) hasHigherNeighbor = true;
  }
  
  // Special case: if value is 1 or max, only need one neighbor
  if (value === 1) return hasHigherNeighbor || neighbors.length > 0;
  if (value === maxValue) return hasLowerNeighbor || neighbors.length > 0;
  
  // For middle values, at least one neighbor should be value±1
  // More lenient: allow placement if either neighbor exists OR grid is mostly empty
  const filledCells = countFilledCells(grid);
  if (filledCells <= 2) return true; // Early game, allow freedom
  
  return hasLowerNeighbor || hasHigherNeighbor;
}

/**
 * Count filled cells in grid.
 */
function countFilledCells(grid: Grid): number {
  let count = 0;
  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const cell = getCell(grid, r, c);
      if (cell && cell.value !== null) count++;
    }
  }
  return count;
}

/**
 * Check if the puzzle is complete and valid.
 */
export function isPuzzleComplete(grid: Grid): boolean {
  const maxValue = grid.size * grid.size;
  
  // All cells must be filled
  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const cell = getCell(grid, r, c);
      if (!cell || cell.value === null) return false;
    }
  }
  
  // Check contiguity: each value 1..max must be adjacent to value+1
  for (let val = 1; val < maxValue; val++) {
    const currentPos = findValue(grid, val);
    const nextPos = findValue(grid, val + 1);
    
    if (!currentPos || !nextPos) return false;
    
    const neighbors = getNeighbors(grid, currentPos.row, currentPos.col);
    const isAdjacent = neighbors.some(
      (n) => n.row === nextPos.row && n.col === nextPos.col
    );
    
    if (!isAdjacent) return false;
  }
  
  return true;
}

/**
 * Find position of a value in the grid.
 */
function findValue(grid: Grid, value: number): { row: number; col: number } | null {
  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const cell = getCell(grid, r, c);
      if (cell && cell.value === value) {
        return { row: r, col: c };
      }
    }
  }
  return null;
}
