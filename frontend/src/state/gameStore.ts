import { create } from 'zustand';
import { Grid, createEmptyGrid, getCell } from '@/domain/grid';
import { Puzzle } from '@/domain/puzzle';
import { positionKey } from '@/domain/position';
import type {
  SequenceState,
  BoardCell as SequenceBoardCell,
  MistakeEvent,
} from '@/sequence/types';

type CompletionStatus = 'success' | 'incorrect' | null;

function deriveCompletionStatusFromBoard(
  board: SequenceBoardCell[][] | null,
  puzzle: Puzzle | null
): CompletionStatus {
  if (!board || !puzzle) return null;
  if (board.length === 0 || board[0].length === 0) return null;

  // Ensure board is completely filled
  for (let row = 0; row < board.length; row++) {
    for (let col = 0; col < board[row].length; col++) {
      const cell = board[row][col];
      if (!cell || cell.value === null) {
        return null;
      }
    }
  }

  const solution = puzzle.solution;
  if (!solution || solution.length === 0) {
    return 'success';
  }

  const solutionMap = new Map<string, number>();
  solution.forEach(({ row, col, value }) => {
    solutionMap.set(positionKey({ row, col }), value);
  });

  for (let row = 0; row < board.length; row++) {
    for (let col = 0; col < board[row].length; col++) {
      const cell = board[row][col];
      const expected = solutionMap.get(positionKey(cell.position));
      if (typeof expected !== 'number' || cell.value !== expected) {
        return 'incorrect';
      }
    }
  }

  return 'success';
}

function countNewPlacements(
  previous: SequenceBoardCell[][] | null,
  next: SequenceBoardCell[][] | null
): number {
  if (!previous || !next) return 0;

  let placements = 0;

  for (let row = 0; row < next.length; row++) {
    const nextRow = next[row];
    const prevRow = previous[row];
    if (!nextRow || !prevRow) continue;

    for (let col = 0; col < nextRow.length; col++) {
      const nextCell = nextRow[col];
      const prevCell = prevRow[col];
      if (
        !nextCell ||
        !prevCell ||
        nextCell.given ||
        prevCell.value !== null ||
        typeof nextCell.value !== 'number'
      ) {
        continue;
      }

      placements += 1;
    }
  }

  return placements;
}

/**
 * Action representing a single game move for undo/redo.
 */
interface GameAction {
  type: 'place' | 'remove' | 'candidate_add' | 'candidate_remove';
  row: number;
  col: number;
  value?: number;
}

interface GameState {
  // Current puzzle
  puzzle: Puzzle | null;
  grid: Grid;
  completionStatus: CompletionStatus;
  puzzleInstance: number;
  moveCount: number;
  timerRunning: boolean;
  lastTick: number | null;
  
  // Guided sequence flow state (for integration)
  sequenceState: SequenceState | null;
  sequenceBoard: SequenceBoardCell[][] | null;
  recentMistakes: MistakeEvent[];
  
  // Interaction state
  selectedCell: { row: number; col: number } | null;
  pencilMode: boolean;
  
  // Undo/redo
  undoStack: GameAction[];
  redoStack: GameAction[];
  
  // Game status
  isComplete: boolean;
  elapsedMs: number;
  
  // Actions
  loadPuzzle: (puzzle: Puzzle) => void;
  selectCell: (row: number, col: number) => void;
  placeValue: (value: number) => void;
  removeValue: (row: number, col: number) => void;
  togglePencilMode: () => void;
  addCandidate: (row: number, col: number, value: number) => void;
  removeCandidate: (row: number, col: number, value: number) => void;
  undo: () => void;
  redo: () => void;
  resetPuzzle: () => void;
  checkCompletion: () => void;
  dismissCompletionStatus: () => void;
  startTimer: () => void;
  stopTimer: () => void;
  tickTimer: () => void;
  
  // Guided sequence flow actions
  updateSequenceState: (
    state: SequenceState,
    board: SequenceBoardCell[][],
    mistakes: MistakeEvent[]
  ) => void;
}

export const useGameStore = create<GameState>((set, get) => ({
  puzzle: null,
  grid: createEmptyGrid(5),
  completionStatus: null,
  puzzleInstance: 0,
  moveCount: 0,
  timerRunning: false,
  lastTick: null,
  sequenceState: null,
  sequenceBoard: null,
  recentMistakes: [],
  selectedCell: null,
  pencilMode: false,
  undoStack: [],
  redoStack: [],
  isComplete: false,
  elapsedMs: 0,

  loadPuzzle: (puzzle: Puzzle) => {
    set((state) => {
      const grid = createEmptyGrid(puzzle.size);
      
      puzzle.givens.forEach(({ row, col, value }) => {
        const cell = getCell(grid, row, col);
        if (cell) {
          cell.value = value;
          cell.given = true;
        }
      });
      
      return {
        puzzle,
        grid,
      selectedCell: null,
      undoStack: [],
      redoStack: [],
      isComplete: false,
      elapsedMs: 0,
      moveCount: 0,
      timerRunning: true,
      lastTick: Date.now(),
      completionStatus: null,
      puzzleInstance: state.puzzleInstance + 1,
      };
    });
  },

  selectCell: (row: number, col: number) => {
    set({ selectedCell: { row, col } });
  },

  placeValue: (value: number) => {
    const { selectedCell, grid, undoStack, pencilMode } = get();
    if (!selectedCell) return;
    
    const cell = getCell(grid, selectedCell.row, selectedCell.col);
    if (!cell || cell.given) return;
    
    if (pencilMode) {
      // Add candidate
      get().addCandidate(selectedCell.row, selectedCell.col, value);
      return;
    }
    
    // Place value
    const action: GameAction = {
      type: 'place',
      row: selectedCell.row,
      col: selectedCell.col,
      value: cell.value ?? undefined,
    };
    
    cell.value = value;
    cell.candidates = [];
    
    set((state) => ({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: [],
      moveCount: state.moveCount + 1,
    }));
    
    get().checkCompletion();
  },

  removeValue: (row: number, col: number) => {
    const { grid, undoStack } = get();
    const cell = getCell(grid, row, col);
    if (!cell || cell.given || cell.value === null) return;
    
    const action: GameAction = {
      type: 'remove',
      row,
      col,
      value: cell.value,
    };
    
    cell.value = null;
    
    set({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: [],
      completionStatus: null,
      isComplete: false,
    });
  },

  togglePencilMode: () => {
    set((state) => ({ pencilMode: !state.pencilMode }));
  },

  addCandidate: (row: number, col: number, value: number) => {
    const { grid, undoStack } = get();
    const cell = getCell(grid, row, col);
    if (!cell || cell.given || cell.candidates.includes(value)) return;
    
    if (cell.candidates.length >= 4) return; // Max 4 candidates
    
    cell.candidates.push(value);
    
    const action: GameAction = { type: 'candidate_add', row, col, value };
    
    set({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: [],
    });
  },

  removeCandidate: (row: number, col: number, value: number) => {
    const { grid, undoStack } = get();
    const cell = getCell(grid, row, col);
    if (!cell || cell.given) return;
    
    const index = cell.candidates.indexOf(value);
    if (index === -1) return;
    
    cell.candidates.splice(index, 1);
    
    const action: GameAction = { type: 'candidate_remove', row, col, value };
    
    set({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: [],
    });
  },

  undo: () => {
    const { undoStack, redoStack, grid } = get();
    if (undoStack.length === 0) return;
    
    const action = undoStack[undoStack.length - 1];
    const cell = getCell(grid, action.row, action.col);
    if (!cell) return;
    
    // Reverse the action
    switch (action.type) {
      case 'place':
        cell.value = action.value ?? null;
        break;
      case 'remove':
        cell.value = action.value ?? null;
        break;
      case 'candidate_add':
        cell.candidates = cell.candidates.filter((v) => v !== action.value);
        break;
      case 'candidate_remove':
        if (action.value) cell.candidates.push(action.value);
        break;
    }
    
    set({
      grid: { ...grid },
      undoStack: undoStack.slice(0, -1),
      redoStack: [...redoStack, action],
    });
  },

  redo: () => {
    const { undoStack, redoStack, grid } = get();
    if (redoStack.length === 0) return;
    
    const action = redoStack[redoStack.length - 1];
    const cell = getCell(grid, action.row, action.col);
    if (!cell) return;
    
    // Replay the action
    switch (action.type) {
      case 'place':
        cell.value = action.value ?? null;
        break;
      case 'remove':
        cell.value = null;
        break;
      case 'candidate_add':
        if (action.value && !cell.candidates.includes(action.value)) {
          cell.candidates.push(action.value);
        }
        break;
      case 'candidate_remove':
        cell.candidates = cell.candidates.filter((v) => v !== action.value);
        break;
    }
    
    set({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: redoStack.slice(0, -1),
    });
  },

  resetPuzzle: () => {
    const { puzzle, loadPuzzle } = get();
    if (puzzle) {
      const puzzleClone: Puzzle = {
        ...puzzle,
        givens: puzzle.givens.map((given) => ({ ...given })),
        solution: puzzle.solution
          ? puzzle.solution.map((cell) => ({ ...cell }))
          : puzzle.solution ?? null,
      };
      loadPuzzle(puzzleClone);
    }
  },

  checkCompletion: () => {
    const { grid, puzzle } = get();
    if (!puzzle) return;

    const applySuccess = () => {
      set((state) => {
        const now = Date.now();
        const delta =
          state.timerRunning && state.lastTick !== null ? now - state.lastTick : 0;
        return {
          isComplete: true,
          completionStatus: 'success',
          timerRunning: false,
          lastTick: null,
          elapsedMs: state.elapsedMs + delta,
        };
      });
    };
    
    // Check if all cells filled
    for (let row = 0; row < grid.size; row++) {
      for (let col = 0; col < grid.size; col++) {
        const cell = getCell(grid, row, col);
        if (!cell || cell.value === null) {
          set({ isComplete: false, completionStatus: null });
          return;
        }
      }
    }
    
    const solution = puzzle.solution;
    if (!solution || solution.length === 0) {
      applySuccess();
      return;
    }

    const solutionMap = new Map<string, number>();
    solution.forEach(({ row, col, value }) => {
      solutionMap.set(positionKey({ row, col }), value);
    });

    let matchesSolution = true;
    for (let row = 0; row < grid.size && matchesSolution; row++) {
      for (let col = 0; col < grid.size; col++) {
        const cell = getCell(grid, row, col);
        const key = positionKey({ row, col });
        const expected = solutionMap.get(key);
        if (!cell || typeof expected !== 'number' || cell.value !== expected) {
          matchesSolution = false;
          break;
        }
      }
    }

    if (matchesSolution) {
      applySuccess();
    } else {
      set({ isComplete: false, completionStatus: 'incorrect' });
    }
  },

  dismissCompletionStatus: () => {
    set((state) =>
      state.completionStatus === 'success'
        ? { completionStatus: null }
        : { completionStatus: null, isComplete: false }
    );
  },

  startTimer: () => {
    set({ timerRunning: true, lastTick: Date.now() });
  },

  stopTimer: () => {
    set((state) => {
      if (!state.timerRunning) {
        return { timerRunning: false, lastTick: null };
      }
      const now = Date.now();
      const delta = state.lastTick !== null ? now - state.lastTick : 0;
      return {
        timerRunning: false,
        lastTick: null,
        elapsedMs: state.elapsedMs + delta,
      };
    });
  },

  tickTimer: () => {
    set((state) => {
      if (!state.timerRunning || state.lastTick === null) {
        return {};
      }
      const now = Date.now();
      return {
        elapsedMs: state.elapsedMs + (now - state.lastTick),
        lastTick: now,
      };
    });
  },
  
  updateSequenceState: (state: SequenceState, board: SequenceBoardCell[][], mistakes: MistakeEvent[]) => {
    set((current) => {
      const evaluatedStatus = deriveCompletionStatusFromBoard(board, current.puzzle);
      let completionStatus = current.completionStatus;
      let isComplete = current.isComplete;
      let elapsedMs = current.elapsedMs;
      let timerRunning = current.timerRunning;
      let lastTick = current.lastTick;
      let moveCount = current.moveCount;

      const alreadySolved =
        current.completionStatus === 'success' || current.isComplete;

      if (!alreadySolved) {
        const placementDelta = countNewPlacements(current.sequenceBoard, board);
        if (placementDelta > 0) {
          moveCount += placementDelta;
        }
      }

      if (evaluatedStatus === 'success') {
        completionStatus = 'success';
        isComplete = true;
        if (timerRunning && lastTick !== null) {
          const now = Date.now();
          elapsedMs += now - lastTick;
        }
        timerRunning = false;
        lastTick = null;
      } else if (evaluatedStatus === 'incorrect') {
        completionStatus = 'incorrect';
        isComplete = false;
      } else if (completionStatus !== null) {
        // Board is no longer complete - clear any stale status
        completionStatus = null;
        isComplete = false;
        if (!timerRunning) {
          timerRunning = true;
          lastTick = Date.now();
        }
      }

      return {
        sequenceState: state,
        sequenceBoard: board,
        recentMistakes: mistakes,
        completionStatus,
        isComplete,
        moveCount,
        elapsedMs,
        timerRunning,
        lastTick,
      };
    });
  },
}));
