/**
 * Next target derivation logic for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { BoardCell, Position, SequenceDirection } from './types';
import { getLegalAdjacents } from './adjacency';

/**
 * Result of deriving next target, including updated anchor position
 */
export interface NextTargetResult {
  nextTarget: number | null;
  newAnchorValue: number | null;
  newAnchorPos: Position | null;
}

/**
 * Derive next target value from anchor value
 * Skips values that already exist on the board (given or player-placed)
 * When skipping, moves anchor to the position of the highest skipped value
 * that still has legal adjacent cells
 * @param anchorValue - Current anchor value (or null)
 * @param anchorPos - Current anchor position (or null)
 * @param board - 2D board grid
 * @returns Result with next target and potentially updated anchor position
 */
export function deriveNextTarget(
  anchorValue: number | null,
  anchorPos: Position | null,
  board: BoardCell[][],
  direction: SequenceDirection
): NextTargetResult {
  // No anchor selected
  if (anchorValue === null || anchorPos === null) {
    return { nextTarget: null, newAnchorValue: null, newAnchorPos: null };
  }

  // Build a map of all values currently on the board to their positions
  const valuePositions = new Map<number, Position>();
  for (const row of board) {
    for (const cell of row) {
      if (cell.value !== null) {
        valuePositions.set(cell.value, cell.position);
      }
    }
  }

  const maxValue = board.length * board[0].length;
  const minValue = 1;

  let currentValue = anchorValue;
  let currentPos = anchorPos;

  if (direction === 'forward') {
    let nextValue = currentValue + 1;

    while (nextValue <= maxValue && valuePositions.has(nextValue)) {
      const candidatePos = valuePositions.get(nextValue)!;
      const candidateLegalAdjacents = getLegalAdjacents(candidatePos, board);

      if (candidateLegalAdjacents.length === 0) {
        return {
          nextTarget: null,
          newAnchorValue: currentValue,
          newAnchorPos: currentPos,
        };
      }

      currentValue = nextValue;
      currentPos = candidatePos;

      nextValue++;
    }

    if (nextValue > maxValue) {
      return {
        nextTarget: null,
        newAnchorValue: currentValue,
        newAnchorPos: currentPos,
      };
    }

    const legalAdjacents = getLegalAdjacents(currentPos, board);
    if (legalAdjacents.length === 0) {
      return {
        nextTarget: null,
        newAnchorValue: currentValue,
        newAnchorPos: currentPos,
      };
    }

    return {
      nextTarget: nextValue,
      newAnchorValue: currentValue,
      newAnchorPos: currentPos,
    };
  }

  // Backward direction
  let nextValue = currentValue - 1;
  while (nextValue >= minValue && valuePositions.has(nextValue)) {
    const candidatePos = valuePositions.get(nextValue)!;
    const candidateLegalAdjacents = getLegalAdjacents(candidatePos, board);

    if (candidateLegalAdjacents.length === 0) {
      return {
        nextTarget: null,
        newAnchorValue: currentValue,
        newAnchorPos: currentPos,
      };
    }

    currentValue = nextValue;
    currentPos = candidatePos;

    nextValue--;
  }

  if (nextValue < minValue) {
    return {
      nextTarget: null,
      newAnchorValue: currentValue,
      newAnchorPos: currentPos,
    };
  }

  const legalAdjacents = getLegalAdjacents(currentPos, board);
  if (legalAdjacents.length === 0) {
    return {
      nextTarget: null,
      newAnchorValue: currentValue,
      newAnchorPos: currentPos,
    };
  }

  return {
    nextTarget: nextValue,
    newAnchorValue: currentValue,
    newAnchorPos: currentPos,
  };
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
