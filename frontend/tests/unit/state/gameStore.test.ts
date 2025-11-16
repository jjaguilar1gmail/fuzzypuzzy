import { beforeEach, describe, expect, it } from 'vitest';
import { useGameStore } from '@/state/gameStore';
import type { BoardCell, SequenceState } from '@/sequence/types';

function createCell(row: number, col: number, value: number | null): BoardCell {
  return {
    position: { row, col },
    value,
    given: false,
    blocked: false,
    highlighted: false,
    anchor: false,
    mistake: false,
  };
}

function cloneBoard(board: BoardCell[][]): BoardCell[][] {
  return board.map((row) => row.map((cell) => ({ ...cell, position: { ...cell.position } })));
}

describe('gameStore move count tracking', () => {
  beforeEach(() => {
    useGameStore.setState({
      puzzle: null,
      grid: useGameStore.getState().grid,
      sequenceState: null,
      sequenceBoard: null,
      moveCount: 0,
      completionStatus: null,
      isComplete: false,
      timerRunning: true,
      lastTick: Date.now(),
    });
  });

  it('increments for each guided placement detected from board changes', () => {
    const initialBoard: BoardCell[][] = [
      [createCell(0, 0, null), createCell(0, 1, null)],
      [createCell(1, 0, null), createCell(1, 1, null)],
    ];

    const baseSequenceState: SequenceState = {
      anchorValue: null,
      anchorPos: null,
      nextTarget: null,
      legalTargets: [],
      guideEnabled: true,
      chainEndValue: null,
      chainLength: 0,
      nextTargetChangeReason: 'neutral',
    };

    useGameStore.getState().updateSequenceState(baseSequenceState, initialBoard, []);
    expect(useGameStore.getState().moveCount).toBe(0);

    const boardAfterFirst = cloneBoard(initialBoard);
    boardAfterFirst[0][0] = { ...boardAfterFirst[0][0], value: 1 };

    const placementState: SequenceState = {
      ...baseSequenceState,
      anchorValue: 1,
      anchorPos: { row: 0, col: 0 },
      nextTarget: 2,
      nextTargetChangeReason: 'placement',
    };

    useGameStore.getState().updateSequenceState(placementState, boardAfterFirst, []);
    expect(useGameStore.getState().moveCount).toBe(1);

    const boardAfterSecond = cloneBoard(boardAfterFirst);
    boardAfterSecond[0][1] = { ...boardAfterSecond[0][1], value: 2 };

    useGameStore.getState().updateSequenceState(placementState, boardAfterSecond, []);
    expect(useGameStore.getState().moveCount).toBe(2);
  });

  it('counts placements even if the guided board is mutated in place', () => {
    const sharedBoard: BoardCell[][] = [
      [createCell(0, 0, null), createCell(0, 1, null)],
      [createCell(1, 0, null), createCell(1, 1, null)],
    ];

    // The production sequence engine mutates this shared structure between
    // updates, so the store must diff against an immutable snapshot to detect
    // each new placement. This regression test locks in that behavior.
    const baseSequenceState: SequenceState = {
      anchorValue: null,
      anchorPos: null,
      nextTarget: null,
      legalTargets: [],
      guideEnabled: true,
      chainEndValue: null,
      chainLength: 0,
      nextTargetChangeReason: 'neutral',
    };

    useGameStore.getState().updateSequenceState(baseSequenceState, sharedBoard, []);
    expect(useGameStore.getState().moveCount).toBe(0);

    sharedBoard[0][0] = { ...sharedBoard[0][0], value: 1 };

    useGameStore.getState().updateSequenceState(
      { ...baseSequenceState, nextTargetChangeReason: 'placement' },
      sharedBoard,
      []
    );
    expect(useGameStore.getState().moveCount).toBe(1);

    sharedBoard[1][1] = { ...sharedBoard[1][1], value: 2 };

    useGameStore.getState().updateSequenceState(
      { ...baseSequenceState, nextTargetChangeReason: 'placement' },
      sharedBoard,
      []
    );
    expect(useGameStore.getState().moveCount).toBe(2);
  });
});
