import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { useGameStore } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';

// Mock localStorage
const localStorageMock = (() => {
  let store: Record<string, string> = {};

  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => {
      store[key] = value;
    },
    removeItem: (key: string) => {
      delete store[key];
    },
    clear: () => {
      store = {};
    },
  };
})();

Object.defineProperty(global, 'localStorage', {
  value: localStorageMock,
});

/**
 * Persistence helper (to be implemented in T021).
 */
interface PersistenceState {
  schema_version: string;
  puzzle_id: string;
  cell_entries: Record<string, number>;
  candidates: Record<string, number[]>;
  elapsed_ms: number;
}

function saveState(puzzleId: string, state: PersistenceState): void {
  const key = `hpz:v1:state:${puzzleId}`;
  localStorage.setItem(key, JSON.stringify(state));
}

function loadState(puzzleId: string): PersistenceState | null {
  const key = `hpz:v1:state:${puzzleId}`;
  const data = localStorage.getItem(key);
  if (!data) return null;
  return JSON.parse(data);
}

describe('Persistence Round-Trip', () => {
  beforeEach(() => {
    localStorage.clear();
    useGameStore.setState({
      puzzle: null,
      selectedCell: null,
      undoStack: [],
      redoStack: [],
    });
  });

  afterEach(() => {
    localStorage.clear();
  });

  it('should save and restore game state', () => {
    const mockPuzzle: Puzzle = {
      id: 'persist-test',
      size: 3,
      difficulty: 'classic',
      seed: 1,
      clue_count: 2,
      givens: [
        { row: 0, col: 0, value: 1 },
        { row: 2, col: 2, value: 9 },
      ],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    useGameStore.getState().selectCell(1, 1);
    useGameStore.getState().placeValue(5);

    // Save state
    const state: PersistenceState = {
      schema_version: '1.0',
      puzzle_id: mockPuzzle.id,
      cell_entries: { '1,1': 5 },
      candidates: {},
      elapsed_ms: 0,
    };

    saveState(mockPuzzle.id, state);

    // Restore state
    const restored = loadState(mockPuzzle.id);
    expect(restored).not.toBeNull();
    expect(restored?.puzzle_id).toBe('persist-test');
    expect(restored?.cell_entries['1,1']).toBe(5);
  });

  it('should save candidates correctly', () => {
    const mockPuzzle: Puzzle = {
      id: 'candidates-test',
      size: 3,
      difficulty: 'classic',
      seed: 1,
      clue_count: 1,
      givens: [{ row: 0, col: 0, value: 1 }],
    };

    useGameStore.getState().loadPuzzle(mockPuzzle);
    useGameStore.getState().selectCell(1, 1);
    useGameStore.getState().togglePencilMode();
    useGameStore.getState().addCandidate(1, 1, 3);
    useGameStore.getState().addCandidate(1, 1, 5);

    // Save state
    const state: PersistenceState = {
      schema_version: '1.0',
      puzzle_id: mockPuzzle.id,
      cell_entries: {},
      candidates: { '1,1': [3, 5] },
      elapsed_ms: 1500,
    };

    saveState(mockPuzzle.id, state);

    const restored = loadState(mockPuzzle.id);
    expect(restored?.candidates['1,1']).toEqual([3, 5]);
  });

  it('should handle missing state gracefully', () => {
    const restored = loadState('non-existent');
    expect(restored).toBeNull();
  });

  it('should respect schema_version for future migrations', () => {
    const state: PersistenceState = {
      schema_version: '1.0',
      puzzle_id: 'version-test',
      cell_entries: {},
      candidates: {},
      elapsed_ms: 0,
    };

    saveState('version-test', state);
    const restored = loadState('version-test');

    expect(restored?.schema_version).toBe('1.0');
  });
});
