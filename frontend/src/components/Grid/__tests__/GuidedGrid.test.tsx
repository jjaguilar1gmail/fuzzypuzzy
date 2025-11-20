import { describe, beforeEach, it, expect, vi } from 'vitest';
import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import React from 'react';
import type { Puzzle } from '@/domain/puzzle';
import type { BoardCell, SequenceState } from '@/sequence/types';
import GuidedGrid from '@/components/Grid/GuidedGrid';

// Minimal motion mock so SVG/DOM nodes render without framer-motion
vi.mock('framer-motion', () => {
  const createMotionComponent =
    (tag: keyof JSX.IntrinsicElements) =>
    ({ children, ...props }: Record<string, unknown>) =>
      React.createElement(tag, props, children);

  const motion = new Proxy(
    {},
    {
      get: (_target, key: string) =>
        createMotionComponent(key as keyof JSX.IntrinsicElements),
    }
  );

  return { motion };
});

// Mock Zustand store hook so we can control the slices the component consumes
const mockGameState: Record<string, any> = {};

const resetGameState = (overrides: Record<string, unknown> = {}) => {
  Object.keys(mockGameState).forEach((key) => delete mockGameState[key]);
  Object.assign(
    mockGameState,
    {
      puzzle: createPuzzle(),
      puzzleInstance: 1,
      updateSequenceState: vi.fn(),
      incrementMoveCount: vi.fn(),
      sequenceBoard: null,
      sequenceBoardKey: 'mock-key',
      boardClearSignal: 0,
      clearBoardEntries: vi.fn(),
      sequenceState: null,
      completionStatus: null,
      isComplete: false,
      reopenCompletionSummary: vi.fn(),
    },
    overrides
  );
};

vi.mock('@/state/gameStore', () => ({
  useGameStore: (selector: (state: typeof mockGameState) => unknown) =>
    selector(mockGameState),
  getPuzzleIdentity: () => 'mock-identity',
}));

// Mock guided sequence hook to avoid the full puzzle runtime
let mockSequenceResult = createSequenceApi();

vi.mock('@/sequence', () => ({
  useGuidedSequenceFlow: () => mockSequenceResult,
}));

function createPuzzle(): Puzzle {
  return {
    id: 'puzzle-1',
    pack_id: 'pack-1',
    size: 2,
    difficulty: 'easy',
    seed: 0,
    clue_count: 1,
    givens: [{ row: 0, col: 0, value: 1 }],
    solution: null,
  };
}

function createCell(row: number, col: number, value: number | null, given: boolean): BoardCell {
  return {
    position: { row, col },
    value,
    given,
    blocked: false,
    highlighted: false,
    anchor: false,
    mistake: false,
  };
}

function createBoard(): BoardCell[][] {
  return [
    [createCell(0, 0, 1, true), createCell(0, 1, null, false)],
    [createCell(1, 0, null, false), createCell(1, 1, null, false)],
  ];
}

function createSequenceState(overrides: Partial<SequenceState> = {}): SequenceState {
  return {
    anchorValue: 1,
    anchorPos: { row: 0, col: 0 },
    nextTarget: 5,
    legalTargets: [],
    guideEnabled: true,
    stepDirection: 'forward',
    chainEndValue: 1,
    chainLength: 1,
    nextTargetChangeReason: 'neutral',
    ...overrides,
  };
}

function createSequenceApi() {
  return {
    state: createSequenceState(),
    board: createBoard(),
    selectAnchor: vi.fn(),
    placeNext: vi.fn(),
    removeCell: vi.fn(),
    toggleGuide: vi.fn(),
    setStepDirection: vi.fn(),
    undo: vi.fn(),
    redo: vi.fn(),
    canUndo: false,
    canRedo: false,
    clearBoard: vi.fn(),
    recentMistakes: [],
  };
}

describe('GuidedGrid next-number pill', () => {
  beforeEach(() => {
    resetGameState();
    mockSequenceResult = createSequenceApi();
  });

  it('renders the completion pill as a button and reopens the summary', async () => {
    const user = userEvent.setup();
    resetGameState({
      isComplete: true,
      completionStatus: 'success',
    });

    render(<GuidedGrid />);

    const completionButton = screen.getByRole('button', {
      name: 'View puzzle completion details',
    });
    expect(completionButton).toBeInTheDocument();
    expect(completionButton).toHaveTextContent('Puzzle complete!');

    await user.click(completionButton);

    expect(mockGameState.reopenCompletionSummary).toHaveBeenCalledTimes(1);
  });

  it('keeps the pill as static text when the puzzle is still in progress', () => {
    mockSequenceResult = createSequenceApi();
    mockSequenceResult.state = createSequenceState({ nextTarget: 12 });
    resetGameState({
      isComplete: false,
      completionStatus: null,
    });

    render(<GuidedGrid />);

    const pillText = screen.getByText('Next: 12');
    expect(pillText).toBeInTheDocument();
    expect(pillText.closest('button')).toBeNull();
  });
});
