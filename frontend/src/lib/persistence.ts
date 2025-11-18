import { useGameStore, getPuzzleIdentity } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';
import { getCell } from '@/domain/grid';
import type { DailySizeId } from '@/lib/daily';

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
  // v1.1 fields
  completion_status?: 'success' | 'incorrect' | null;
  is_complete?: boolean;
  move_count?: number;
  timer_running?: boolean;
  // Guided sequence board (for guided mode)
  sequence_board?: Array<Array<{value: number | null; given: boolean}>> | null;
}

const SCHEMA_VERSION = '1.1';

function getStorageKey(puzzleId: string, sizeId?: DailySizeId): string {
  // For daily puzzles, sizeId is already included in the puzzleId (e.g., "daily-2025-11-17-small")
  // For pack puzzles, we add the sizeId suffix if provided
  return sizeId && !puzzleId.startsWith('daily-') 
    ? `hpz:v1:state:${puzzleId}:${sizeId}` 
    : `hpz:v1:state:${puzzleId}`;
}

/**
 * Save current game state to localStorage.
 * @param puzzleId - The puzzle identifier (use daily key for daily puzzles)
 * @param sizeId - Optional size identifier (for non-daily puzzles only)
 */
export function saveGameState(puzzleId: string, sizeId?: DailySizeId): void {
  const state = useGameStore.getState();
  const { grid, elapsedMs, undoStack, completionStatus, isComplete, moveCount, timerRunning } = state;

  const cellEntries: Record<string, number> = {};
  const candidates: Record<string, number[]> = {};

  for (let r = 0; r < grid.size; r++) {
    for (let c = 0; c < grid.size; c++) {
      const cell = getCell(grid, r, c);
      if (!cell) continue;
      
      if (cell.given) continue;

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
    completion_status: completionStatus,
    is_complete: isComplete,
    move_count: moveCount,
    timer_running: timerRunning,
    // Save sequenceBoard for guided mode
    sequence_board: state.sequenceBoard ? state.sequenceBoard.map(row => 
      row.map(cell => ({ value: cell.value, given: cell.given }))
    ) : null,
  };

  try {
    localStorage.setItem(getStorageKey(puzzleId, sizeId), JSON.stringify(persistedState));
  } catch (err) {
    console.error('Failed to save game state:', err);
  }
}

/**
 * Load game state from localStorage and apply to store.
 * @param puzzle - The puzzle to restore state for
 * @param sizeId - Optional size identifier (for non-daily puzzles only)
 * @param overridePuzzleId - Optional puzzle ID to use for storage key (for daily puzzles)
 */
export function loadGameState(
  puzzle: Puzzle, 
  sizeId?: DailySizeId,
  overridePuzzleId?: string
): boolean {
  const puzzleId = overridePuzzleId || puzzle.id;
  const key = getStorageKey(puzzleId, sizeId);
  const data = localStorage.getItem(key);
  
  if (!data) {
    return false;
  }

  try {
    const persistedState: PersistedState = JSON.parse(data);

    // Handle schema migration from v1.0 to v1.1
    const isOldSchema = persistedState.schema_version === '1.0';
    if (!isOldSchema && persistedState.schema_version !== SCHEMA_VERSION) {
      console.warn('Saved state schema mismatch, skipping restore');
      return false;
    }

    // Load puzzle first (resets all state)
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
    
    // Restore sequenceBoard if it exists (for guided mode)
    let restoredSequenceBoard: any = null;
    if (persistedState.sequence_board) {
      // SAFETY CHECK: Ensure restored board size matches current puzzle size
      if (persistedState.sequence_board.length !== puzzle.size) {
        return false; // Don't restore incompatible board
      }
      
      // Convert saved format back to full BoardCell format
      restoredSequenceBoard = persistedState.sequence_board.map((row, r) =>
        row.map((savedCell, c) => ({
          position: { row: r, col: c },
          value: savedCell.value,
          given: savedCell.given,
          blocked: false,
          highlighted: false,
          anchor: false,
          mistake: false,
        }))
      );
    }
    
    useGameStore.setState({
      grid: { ...grid },
      elapsedMs: persistedState.elapsed_ms,
      // Restore v1.1 fields (will be undefined for old v1.0 saves)
      completionStatus: persistedState.completion_status ?? null,
      isComplete: persistedState.is_complete ?? false,
      moveCount: persistedState.move_count ?? 0,
      timerRunning: persistedState.timer_running ?? true, // Default to true for old saves
      sequenceBoard: restoredSequenceBoard,
      sequenceBoardKey: restoredSequenceBoard ? getPuzzleIdentity(puzzle) : null,
    });
    
    // If we restored a sequenceBoard, derive completion status from it
    if (restoredSequenceBoard) {
      const store = useGameStore.getState();
      // Call updateSequenceState to derive completion from restored board
      // This ensures completion status, timer state, etc. are correctly set
      const emptySequenceState = {
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward' as const,
        chainEndValue: null,
        chainLength: 0,
        nextTargetChangeReason: 'neutral' as const,
      };
      store.updateSequenceState(emptySequenceState, restoredSequenceBoard, []);
    }

    // Re-check completion status for old saves that don't have it
    if (isOldSchema) {
      useGameStore.getState().checkCompletion();
    }

    return true;
  } catch (err) {
    console.error('Failed to load game state:', err);
    return false;
  }
}

/**
 * Clear saved state for a puzzle.
 * @param puzzleId - The puzzle identifier
 * @param sizeId - Optional size identifier for daily puzzles
 */
export function clearGameState(puzzleId: string, sizeId?: DailySizeId): void {
  const key = getStorageKey(puzzleId, sizeId);
  localStorage.removeItem(key);
}
