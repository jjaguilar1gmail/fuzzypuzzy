/**
 * Next target derivation logic for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { BoardCell, Position } from './types';
import { getLegalAdjacents } from './adjacency';

/**
 * Derive next target value from anchor value
 * @param anchorValue - Current anchor value (or null)
 * @param anchorPos - Current anchor position (or null)
 * @param board - 2D board grid
 * @returns Next target value or null if no valid extension
 */
export function deriveNextTarget(
  anchorValue: number | null,
  anchorPos: Position | null,
  board: BoardCell[][]
): number | null {
  // No anchor selected
  if (anchorValue === null || anchorPos === null) {
    return null;
  }

  const nextValue = anchorValue + 1;

  // Check if next value has legal adjacency from anchor
  const legalAdjacents = getLegalAdjacents(anchorPos, board);

  // If no legal adjacent cells, cannot extend
  if (legalAdjacents.length === 0) {
    return null;
  }

  return nextValue;
}

/**
 * Compute legal target positions for the next value
 * @param anchorPos - Current anchor position (or null)
 * @param board - 2D board grid
 * @returns Array of legal target positions
 */
export function computeLegalTargets(
  anchorPos: Position | null,
  board: BoardCell[][]
): Position[] {
  if (anchorPos === null) {
    return [];
  }

  return getLegalAdjacents(anchorPos, board);
}
