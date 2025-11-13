/**
 * Stale target detection and recovery utilities
 * Handles cases where displayed nextTarget becomes invalid due to board changes
 */

import type { SequenceState, BoardCell, Position } from './types';
import { computeChain } from './chain';
import { deriveNextTarget, computeLegalTargets } from './nextTarget';
import { positionsEqual } from './adjacency';

export interface StaleTargetCheck {
  /** Whether the current state is stale */
  isStale: boolean;
  /** Reason for staleness (if stale) */
  reason?: 'chain-mutated' | 'anchor-invalid' | 'target-unreachable';
  /** Recovered state (if stale) */
  recoveredState?: SequenceState;
}

/**
 * Detect if current sequence state is stale (nextTarget no longer valid)
 * @param state - Current sequence state
 * @param board - Current board state
 * @param maxValue - Maximum value in puzzle
 * @returns Check result with recovery state if stale
 */
export function detectStaleTarget(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number
): StaleTargetCheck {
  // If no next target, nothing can be stale
  if (state.nextTarget === null) {
    return { isStale: false };
  }

  // If no anchor, nextTarget should be null (stale)
  if (state.anchorPos === null || state.anchorValue === null) {
    const chainInfo = computeChain(board, maxValue);
    return {
      isStale: true,
      reason: 'anchor-invalid',
      recoveredState: {
        ...state,
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
        nextTargetChangeReason: 'neutral',
      },
    };
  }

  // Check if anchor cell still has the expected value
  const anchorCell = board[state.anchorPos.row][state.anchorPos.col];
  if (anchorCell.value !== state.anchorValue) {
    const chainInfo = computeChain(board, maxValue);
    return {
      isStale: true,
      reason: 'anchor-invalid',
      recoveredState: {
        ...state,
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
        nextTargetChangeReason: 'neutral',
      },
    };
  }

  // Recompute what the next target should be
  const targetResult = deriveNextTarget(
    state.anchorValue,
    state.anchorPos,
    board
  );

  // If computed target differs from state, we're stale
  if (targetResult.nextTarget !== state.nextTarget) {
    const chainInfo = computeChain(board, maxValue);
    const finalAnchorValue = targetResult.newAnchorValue ?? state.anchorValue;
    const finalAnchorPos = targetResult.newAnchorPos ?? state.anchorPos;
    const legalTargets = targetResult.nextTarget !== null
      ? computeLegalTargets(finalAnchorPos, board)
      : [];

    return {
      isStale: true,
      reason: targetResult.nextTarget === null ? 'target-unreachable' : 'chain-mutated',
      recoveredState: {
        ...state,
        anchorValue: finalAnchorValue,
        anchorPos: finalAnchorPos,
        nextTarget: targetResult.nextTarget,
        legalTargets,
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
        nextTargetChangeReason: 'neutral',
      },
    };
  }

  // Check if legal targets have changed
  const actualLegalTargets = computeLegalTargets(state.anchorPos, board);
  const legalTargetsChanged =
    actualLegalTargets.length !== state.legalTargets.length ||
    !actualLegalTargets.every((target) =>
      state.legalTargets.some((stateTarget) =>
        positionsEqual(target, stateTarget)
      )
    );

  if (legalTargetsChanged) {
    const chainInfo = computeChain(board, maxValue);
    return {
      isStale: true,
      reason: 'target-unreachable',
      recoveredState: {
        ...state,
        legalTargets: actualLegalTargets,
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      },
    };
  }

  // State is valid
  return { isStale: false };
}

/**
 * Automatically recover from stale state
 * @param state - Current (potentially stale) state
 * @param board - Current board
 * @param maxValue - Maximum value in puzzle
 * @returns Recovered state
 */
export function recoverFromStaleState(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number
): SequenceState {
  const check = detectStaleTarget(state, board, maxValue);
  return check.isStale && check.recoveredState ? check.recoveredState : state;
}

/**
 * Check if a state represents neutral (no anchor, no next target)
 */
export function isNeutralState(state: SequenceState): boolean {
  return (
    state.anchorValue === null &&
    state.anchorPos === null &&
    state.nextTarget === null
  );
}

/**
 * Check if user can resume from neutral state by selecting a chain value
 */
export function canResumeFromNeutral(
  board: BoardCell[][],
  maxValue: number
): boolean {
  const chainInfo = computeChain(board, maxValue);
  return chainInfo.chainEndValue !== null && chainInfo.nextCandidate !== null;
}
