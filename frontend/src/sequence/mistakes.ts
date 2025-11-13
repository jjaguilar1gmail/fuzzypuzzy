/**
 * Mistake detection and classification logic
 * Based on specs/001-guided-sequence-flow/spec.md (US2)
 */

import type { Position, BoardCell, MistakeEvent, MistakeReason } from './types';
import { positionsEqual, areAdjacent } from './adjacency';

/**
 * Validate a placement attempt and classify any mistake
 * @param pos - Position where user attempted to place
 * @param expectedValue - The nextTarget value expected
 * @param anchorPos - Current anchor position
 * @param board - 2D board grid
 * @returns MistakeEvent if invalid, null if valid
 */
export function validatePlacement(
  pos: Position,
  expectedValue: number | null,
  anchorPos: Position | null,
  board: BoardCell[][]
): MistakeEvent | null {
  // No target available
  if (expectedValue === null) {
    return {
      position: pos,
      attemptedValue: 0, // No valid value available
      reason: 'no-target',
      timestamp: Date.now(),
    };
  }

  const cell = board[pos.row][pos.col];

  // Cell already occupied
  if (cell.value !== null) {
    return {
      position: pos,
      attemptedValue: expectedValue,
      reason: 'occupied',
      timestamp: Date.now(),
    };
  }

  // Cell blocked
  if (cell.blocked) {
    return {
      position: pos,
      attemptedValue: expectedValue,
      reason: 'occupied', // Blocked cells treated as occupied
      timestamp: Date.now(),
    };
  }

  // Not adjacent to anchor
  if (anchorPos === null || !areAdjacent(anchorPos, pos)) {
    return {
      position: pos,
      attemptedValue: expectedValue,
      reason: 'not-adjacent',
      timestamp: Date.now(),
    };
  }

  // Valid placement
  return null;
}

/**
 * Validate a removal attempt
 * @param pos - Position where user attempted to remove
 * @param board - 2D board grid
 * @returns Error message if invalid, null if valid
 */
export function validateRemoval(
  pos: Position,
  board: BoardCell[][]
): string | null {
  const cell = board[pos.row][pos.col];

  // Cannot remove from empty cell
  if (cell.value === null) {
    return 'Cannot remove from empty cell';
  }

  // Cannot remove given values
  if (cell.given) {
    return 'Cannot remove given values';
  }

  // Valid removal
  return null;
}

/**
 * Check if a click on an empty cell is a mistake (not in legal targets)
 * @param pos - Clicked position
 * @param legalTargets - Array of legal target positions
 * @param nextTarget - Current next target value
 * @returns True if click was a mistake
 */
export function isInvalidEmptyCellClick(
  pos: Position,
  legalTargets: Position[],
  nextTarget: number | null
): boolean {
  // If no next target, any empty cell click is invalid
  if (nextTarget === null) {
    return true;
  }

  // Check if position is in legal targets
  return !legalTargets.some((target) => positionsEqual(target, pos));
}
