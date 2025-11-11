import { useGameStore } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';
import { getCell } from '@/domain/grid';

/**
 * Local persistence utilities for saving/restoring game state.
 */

export interface PersistedState {
  schema_version: string;
  puzzle_id: string;
  pack_id?: string;
  cell_entries: Record<string, number>;
  candidates: Record<string, number[]>;
  elapsed_ms: number;
  undo_count: number;
}

const SCHEMA_VERSION = '1.0';

function getStorageKey(puzzleId: string): string {
  return `hpz:v1:state:${puzzleId}`;
}

/**
 * Save current game state to localStorage.
 */
export function saveGameState(puzzleId: string): void {
  const state = useGameStore.getState();
  const { grid, elapsedMs, undoStack } = state;

  const cellEntries: Record<string, number> = {};
  const candidates: Record<string, number[]> = {};

  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const cell = getCell(grid, r, c);
      if (!cell || cell.given) continue;

      const key = `${r},${c}`;
      if (cell.value !== null) {
        cellEntries[key] = cell.value;
      }
      if (cell.candidates.length > 0) {
        candidates[key] = [...cell.candidates];
      }
    }
  }

  const persistedState: PersistedState = {
    schema_version: SCHEMA_VERSION,
    puzzle_id: puzzleId,
    pack_id: state.puzzle?.pack_id,
    cell_entries: cellEntries,
    candidates,
    elapsed_ms: elapsedMs,
    undo_count: undoStack.length,
  };

  try {
    localStorage.setItem(getStorageKey(puzzleId), JSON.stringify(persistedState));
  } catch (err) {
    console.error('Failed to save game state:', err);
  }
}

/**
 * Load game state from localStorage and apply to store.
 */
export function loadGameState(puzzle: Puzzle): boolean {
  const key = getStorageKey(puzzle.id);
  const data = localStorage.getItem(key);
  if (!data) return false;

  try {
    const persistedState: PersistedState = JSON.parse(data);

    // Verify schema version
    if (persistedState.schema_version !== SCHEMA_VERSION) {
      console.warn('Saved state schema mismatch, skipping restore');
      return false;
    }

    // Load puzzle first
    useGameStore.getState().loadPuzzle(puzzle);

    // Apply cell values
    const grid = useGameStore.getState().grid;
    Object.entries(persistedState.cell_entries).forEach(([key, value]) => {
      const [r, c] = key.split(',').map(Number);
      const cell = getCell(grid, r, c);
      if (cell && !cell.given) {
        cell.value = value;
      }
    });

    // Apply candidates
    Object.entries(persistedState.candidates).forEach(([key, cands]) => {
      const [r, c] = key.split(',').map(Number);
      const cell = getCell(grid, r, c);
      if (cell && !cell.given) {
        cell.candidates = [...cands];
      }
    });

    // Apply time (undo stack not persisted for simplicity)
    useGameStore.setState({
      grid: { ...grid },
      elapsedMs: persistedState.elapsed_ms,
    });

    return true;
  } catch (err) {
    console.error('Failed to load game state:', err);
    return false;
  }
}

/**
 * Clear saved state for a puzzle.
 */
export function clearGameState(puzzleId: string): void {
  const key = getStorageKey(puzzleId);
  localStorage.removeItem(key);
}
