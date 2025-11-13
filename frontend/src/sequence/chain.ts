/**
 * Chain detection logic for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { BoardCell, ChainInfo, Position } from './types';
import { getLegalAdjacents } from './adjacency';

/**
 * Build a map of values to their positions on the board
 */
export function buildValuesMap(board: BoardCell[][]): Map<number, Position> {
  const valuesMap = new Map<number, Position>();

  for (let row = 0; row < board.length; row++) {
    for (let col = 0; col < board[row].length; col++) {
      const cell = board[row][col];
      if (cell.value !== null) {
        valuesMap.set(cell.value, cell.position);
      }
    }
  }

  return valuesMap;
}

/**
 * Compute chain information from board state
 * @param board - 2D board grid
 * @param maxValue - Maximum value in puzzle
 * @returns Chain info (chainEndValue, chainLength, nextCandidate)
 */
export function computeChain(
  board: BoardCell[][],
  maxValue: number
): ChainInfo {
  const valuesMap = buildValuesMap(board);

  // Empty board
  if (valuesMap.size === 0) {
    return {
      chainEndValue: null,
      chainLength: 0,
      nextCandidate: null,
    };
  }

  // Determine chain start: 1 if exists, else minimum value
  const start = valuesMap.has(1) ? 1 : Math.min(...valuesMap.keys());

  // Find contiguous chain
  let current = start;
  while (valuesMap.has(current + 1)) {
    current++;
  }

  const chainEndValue = current;
  const chainLength = current - start + 1;

  // Determine next candidate
  let nextCandidate: number | null = null;
  if (chainEndValue < maxValue) {
    const candidateValue = chainEndValue + 1;
    const chainEndPos = valuesMap.get(chainEndValue);

    if (chainEndPos) {
      // Check if next candidate has at least one legal adjacency
      const legalAdjacents = getLegalAdjacents(chainEndPos, board);
      if (legalAdjacents.length > 0) {
        nextCandidate = candidateValue;
      }
    }
  }

  return {
    chainEndValue,
    chainLength,
    nextCandidate,
  };
}
