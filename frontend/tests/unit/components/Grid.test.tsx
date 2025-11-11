import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { useGameStore } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';

// Mock Grid component for testing (actual implementation in T013)
const MockGrid = () => {
  const grid = useGameStore((state) => state.grid);
  const selectedCell = useGameStore((state) => state.selectedCell);
  const selectCell = useGameStore((state) => state.selectCell);
  const placeValue = useGameStore((state) => state.placeValue);

  return (
    <div data-testid="grid">
      {grid.cells.map((row, r) =>
        row.map((cell, c) => (
          <button
            key={`${r}-${c}`}
            data-testid={`cell-${r}-${c}`}
            onClick={() => selectCell(r, c)}
            className={
              selectedCell?.row === r && selectedCell?.col === c
                ? 'selected'
                : ''
            }
          >
            {cell.value || ''}
          </button>
        ))
      )}
      <button
        data-testid="place-5"
        onClick={() => placeValue(5)}
      >
        Place 5
      </button>
    </div>
  );
};

describe('Grid Component (Mock)', () => {
  beforeEach(() => {
    // Reset store before each test
    useGameStore.setState({
      puzzle: null,
      grid: useGameStore.getState().grid,
      selectedCell: null,
      undoStack: [],
      redoStack: [],
      isComplete: false,
    });
  });

  it('should render grid cells', () => {
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'easy',
      seed: 1,
      clue_count: 2,
      givens: [
        { row: 0, col: 0, value: 1 },
        { row: 2, col: 2, value: 9 },
      ],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockGrid />);

    expect(screen.getByTestId('cell-0-0')).toHaveTextContent('1');
    expect(screen.getByTestId('cell-2-2')).toHaveTextContent('9');
  });

  it('should select cell on click', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'easy',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockGrid />);

    const cell = screen.getByTestId('cell-1-1');
    await user.click(cell);

    expect(cell).toHaveClass('selected');
  });

  it('should place value on selected cell', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'easy',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockGrid />);

    const cell = screen.getByTestId('cell-1-1');
    await user.click(cell);
    
    const placeButton = screen.getByTestId('place-5');
    await user.click(placeButton);

    expect(screen.getByTestId('cell-1-1')).toHaveTextContent('5');
  });

  it('should support undo action', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'easy',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockGrid />);

    const cell = screen.getByTestId('cell-1-1');
    await user.click(cell);
    await user.click(screen.getByTestId('place-5'));

    expect(screen.getByTestId('cell-1-1')).toHaveTextContent('5');

    // Undo
    useGameStore.getState().undo();
    expect(screen.getByTestId('cell-1-1')).toHaveTextContent('');
  });
});
