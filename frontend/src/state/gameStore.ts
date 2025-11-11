import { create } from 'zustand';
import { Grid, createEmptyGrid, getCell } from '@/domain/grid';
import { Puzzle } from '@/domain/puzzle';
import { positionKey } from '@/domain/position';

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
  
  // Interaction state
  selectedCell: { row: number; col: number } | null;
  pencilMode: boolean;
  
  // Undo/redo
  undoStack: GameAction[];
  redoStack: GameAction[];
  
  // Game status
  isComplete: boolean;
  elapsedMs: number;
  mistakes: number;
  
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
}

export const useGameStore = create<GameState>((set, get) => ({
  puzzle: null,
  grid: createEmptyGrid(5),
  selectedCell: null,
  pencilMode: false,
  undoStack: [],
  redoStack: [],
  isComplete: false,
  elapsedMs: 0,
  mistakes: 0,

  loadPuzzle: (puzzle: Puzzle) => {
    const grid = createEmptyGrid(puzzle.size);
    
    // Place givens
    puzzle.givens.forEach(({ row, col, value }) => {
      const cell = getCell(grid, row, col);
      if (cell) {
        cell.value = value;
        cell.given = true;
      }
    });
    
    set({
      puzzle,
      grid,
      selectedCell: null,
      undoStack: [],
      redoStack: [],
      isComplete: false,
      elapsedMs: 0,
      mistakes: 0,
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
    
    set({
      grid: { ...grid },
      undoStack: [...undoStack, action],
      redoStack: [],
    });
    
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
    const { puzzle } = get();
    if (puzzle) get().loadPuzzle(puzzle);
  },

  checkCompletion: () => {
    const { grid, puzzle } = get();
    if (!puzzle) return;
    
    // Check if all cells filled
    for (let row = 0; row < grid.size; row++) {
      for (let col = 0; col < grid.size; col++) {
        const cell = getCell(grid, row, col);
        if (!cell || cell.value === null) {
          set({ isComplete: false });
          return;
        }
      }
    }
    
    // TODO: Full validation (adjacency, contiguity)
    set({ isComplete: true });
  },
}));
