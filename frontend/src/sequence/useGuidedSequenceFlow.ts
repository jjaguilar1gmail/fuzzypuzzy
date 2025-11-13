/**
 * Main React hook for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import { useState, useCallback, useMemo, useRef } from 'react';
import type {
  BoardCell,
  Position,
  SequenceState,
  GuidedSequenceFlowAPI,
  MistakeEvent,
} from './types';
import { UndoRedoStack } from './undoRedo';
import { computeChain } from './chain';
import { deriveNextTarget, computeLegalTargets } from './nextTarget';
import {
  selectAnchor as selectAnchorTransition,
  placeNext as placeNextTransition,
  removeCell as removeCellTransition,
  toggleGuide as toggleGuideTransition,
  applyUndo,
  applyRedo,
} from './transitions';

const MISTAKE_BUFFER_SIZE = 20;

/**
 * Initialize board from puzzle data
 */
function initializeBoard(
  rows: number,
  cols: number,
  givens: Map<string, number>
): BoardCell[][] {
  const board: BoardCell[][] = [];

  for (let row = 0; row < rows; row++) {
    const rowCells: BoardCell[] = [];
    for (let col = 0; col < cols; col++) {
      const key = `${row},${col}`;
      const value = givens.get(key) ?? null;
      const given = value !== null;

      rowCells.push({
        position: { row, col },
        value,
        given,
        blocked: false,
        highlighted: false,
        anchor: false,
        mistake: false,
      });
    }
    board.push(rowCells);
  }

  return board;
}

/**
 * Initialize sequence state
 */
function initializeSequenceState(): SequenceState {
  return {
    anchorValue: null,
    anchorPos: null,
    nextTarget: null,
    legalTargets: [],
    guideEnabled: true,
    chainEndValue: null,
    chainLength: 0,
    nextTargetChangeReason: 'neutral',
  };
}

/**
 * Main hook for guided sequence flow
 */
export function useGuidedSequenceFlow(
  rows: number,
  cols: number,
  givens: Map<string, number>,
  maxValue: number
): GuidedSequenceFlowAPI {
  // Initialize board and state
  const [board, setBoard] = useState(() => initializeBoard(rows, cols, givens));
  const [state, setState] = useState(() => {
    const initial = initializeSequenceState();
    const initialBoard = initializeBoard(rows, cols, givens);
    const chainInfo = computeChain(initialBoard, maxValue);
    return {
      ...initial,
      chainEndValue: chainInfo.chainEndValue,
      chainLength: chainInfo.chainLength,
    };
  });

  // Undo/redo stack
  const undoRedoRef = useRef(new UndoRedoStack());
  const [undoRedoVersion, setUndoRedoVersion] = useState(0);

  // Mistake buffer (ring buffer)
  const [mistakes, setMistakes] = useState<MistakeEvent[]>([]);

  // Select anchor
  const selectAnchor = useCallback(
    (pos: Position) => {
      const result = selectAnchorTransition(state, board, maxValue, pos);
      setState(result.state);
    },
    [state, board, maxValue]
  );

  // Place next value
  const placeNext = useCallback(
    (pos: Position) => {
      const result = placeNextTransition(state, board, maxValue, pos);
      
      if (result.undoAction) {
        undoRedoRef.current.push(result.undoAction);
        setUndoRedoVersion((v) => v + 1);
      }
      
      setState(result.state);
      setBoard(result.board);
    },
    [state, board, maxValue]
  );

  // Remove cell
  const removeCell = useCallback(
    (pos: Position) => {
      const result = removeCellTransition(state, board, maxValue, pos);
      
      if (result.undoAction) {
        undoRedoRef.current.push(result.undoAction);
        setUndoRedoVersion((v) => v + 1);
      }
      
      setState(result.state);
      setBoard(result.board);
    },
    [state, board, maxValue]
  );

  // Toggle guide
  const toggleGuide = useCallback(
    (enabled: boolean) => {
      const newState = toggleGuideTransition(state, enabled);
      setState(newState);
    },
    [state]
  );

  // Undo
  const undo = useCallback(() => {
    const action = undoRedoRef.current.undo();
    if (action) {
      const result = applyUndo(state, board, maxValue, action);
      setState(result.state);
      setBoard(result.board);
      setUndoRedoVersion((v) => v + 1);
    }
  }, [state, board, maxValue]);

  // Redo
  const redo = useCallback(() => {
    const action = undoRedoRef.current.redo();
    if (action) {
      const result = applyRedo(state, board, maxValue, action);
      setState(result.state);
      setBoard(result.board);
      setUndoRedoVersion((v) => v + 1);
    }
  }, [state, board, maxValue]);

  // Can undo/redo
  const canUndo = undoRedoRef.current.canUndo();
  const canRedo = undoRedoRef.current.canRedo();

  // Add mistake
  const addMistake = useCallback((mistake: MistakeEvent) => {
    setMistakes((prev) => {
      const updated = [...prev, mistake];
      // Trim to buffer size
      if (updated.length > MISTAKE_BUFFER_SIZE) {
        return updated.slice(-MISTAKE_BUFFER_SIZE);
      }
      return updated;
    });
  }, []);

  return {
    state,
    board,
    selectAnchor,
    placeNext,
    removeCell,
    toggleGuide,
    undo,
    redo,
    canUndo,
    canRedo,
    recentMistakes: mistakes,
  };
}
