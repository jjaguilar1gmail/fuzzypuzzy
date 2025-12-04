import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import { useGameStore } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';

// Mock Palette component for testing (actual implementation in T014)
const MockPalette = () => {
  const pencilMode = useGameStore((state) => state.pencilMode);
  const togglePencilMode = useGameStore((state) => state.togglePencilMode);
  const placeValue = useGameStore((state) => state.placeValue);
  const puzzle = useGameStore((state) => state.puzzle);

  if (!puzzle) return null;

  const maxValue = puzzle.size * puzzle.size;
  const numbers = Array.from({ length: maxValue }, (_, i) => i + 1);

  return (
    <div data-testid="palette">
      <button
        data-testid="pencil-toggle"
        onClick={togglePencilMode}
        aria-pressed={pencilMode}
      >
        {pencilMode ? 'Pencil: ON' : 'Pencil: OFF'}
      </button>
      <div>
        {numbers.map((num) => (
          <button
            key={num}
            data-testid={`number-${num}`}
            onClick={() => placeValue(num)}
          >
            {num}
          </button>
        ))}
      </div>
    </div>
  );
};

describe('Palette Component (Mock)', () => {
  beforeEach(() => {
    useGameStore.setState({
      puzzle: null,
      pencilMode: false,
      selectedCell: null,
      undoStack: [],
      redoStack: [],
    });
  });

  it('should render number buttons for puzzle size', () => {
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 5,
      difficulty: 'classic',
      seed: 1,
      clue_count: 2,
      givens: [
        { row: 0, col: 0, value: 1 },
        { row: 4, col: 4, value: 25 },
      ],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockPalette />);

    expect(screen.getByTestId('number-1')).toBeInTheDocument();
    expect(screen.getByTestId('number-25')).toBeInTheDocument();
    expect(screen.queryByTestId('number-26')).not.toBeInTheDocument();
  });

  it('should toggle pencil mode', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'classic',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    render(<MockPalette />);

    const toggle = screen.getByTestId('pencil-toggle');
    expect(toggle).toHaveTextContent('Pencil: OFF');
    expect(toggle).toHaveAttribute('aria-pressed', 'false');

    await user.click(toggle);

    expect(toggle).toHaveTextContent('Pencil: ON');
    expect(toggle).toHaveAttribute('aria-pressed', 'true');
  });

  it('should call placeValue when number clicked', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'classic',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    useGameStore.getState().selectCell(1, 1);
    render(<MockPalette />);

    const button = screen.getByTestId('number-5');
    await user.click(button);

    const grid = useGameStore.getState().grid;
    const cell = grid.cells[1][1];
    expect(cell.value).toBe(5);
  });

  it('should add candidate when pencil mode active', async () => {
    const user = userEvent.setup();
    const mockPuzzle: Puzzle = {
      id: 'test',
      size: 3,
      difficulty: 'classic',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    useGameStore.getState().selectCell(1, 1);
    useGameStore.getState().togglePencilMode();
    render(<MockPalette />);

    const button = screen.getByTestId('number-3');
    await user.click(button);

    const grid = useGameStore.getState().grid;
    const cell = grid.cells[1][1];
    expect(cell.candidates).toContain(3);
    expect(cell.value).toBeNull();
  });
});
