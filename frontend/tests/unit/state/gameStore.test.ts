import { describe, it, expect, beforeEach } from 'vitest';
import { useGameStore, getPuzzleIdentity } from '@/state/gameStore';
import type { Puzzle } from '@/domain/puzzle';
import type { SequenceBoardCell, SequenceState } from '@/sequence/types';

const baseSequenceState: SequenceState = {
  anchorValue: null,
  anchorPos: null,
  nextTarget: null,
  legalTargets: [],
  guideEnabled: true,
  stepDirection: 'forward',
  chainEndValue: null,
  chainLength: 0,
  nextTargetChangeReason: 'neutral',
};

function createPuzzle(overrides: Partial<Puzzle> = {}): Puzzle {
  return {
    id: 'puzzle-1',
    pack_id: 'pack-a',
    size: 2,
    difficulty: 'classic',
    seed: 1,
    clue_count: 0,
    givens: [],
    ...overrides,
  };
}

function createSequenceCell(
  row: number,
  col: number,
  value: number
): SequenceBoardCell {
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

function createBoard(size: number): SequenceBoardCell[][] {
  return Array.from({ length: size }, (_, row) =>
    Array.from({ length: size }, (_, col) =>
      createSequenceCell(row, col, row * size + col + 1)
    )
  );
}

describe('gameStore sequence board handling', () => {
  beforeEach(() => {
    const state = useGameStore.getState();
    useGameStore.setState({
      ...state,
      puzzle: null,
      sequenceBoard: null,
      sequenceBoardKey: null,
      sequenceState: null,
      recentMistakes: [],
    });
  });

  it('clears stale sequence boards when loading a new puzzle', () => {
    const puzzleA = createPuzzle({ id: 'puzzle-a', pack_id: 'pack-a' });
    const puzzleB = createPuzzle({ id: 'puzzle-b', pack_id: 'pack-b' });

    useGameStore.setState({
      sequenceBoard: createBoard(2),
      sequenceBoardKey: getPuzzleIdentity(puzzleA),
    });

    useGameStore.getState().loadPuzzle(puzzleB);

    const state = useGameStore.getState();
    expect(state.sequenceBoard).toBeNull();
    expect(state.sequenceBoardKey).toBeNull();
  });

  it('tags stored sequence boards with the active puzzle identity', () => {
    const puzzle = createPuzzle({ id: 'puzzle-c', pack_id: 'pack-c' });
    useGameStore.getState().loadPuzzle(puzzle);

    const board = createBoard(puzzle.size);
    useGameStore.getState().updateSequenceState(baseSequenceState, board, []);

    const state = useGameStore.getState();
    expect(state.sequenceBoard).toBe(board);
    expect(state.sequenceBoardKey).toBe(getPuzzleIdentity(puzzle));
  });
});
