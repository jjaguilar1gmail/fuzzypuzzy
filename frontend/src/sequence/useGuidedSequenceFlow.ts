/**
 * Main React hook for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import { useState, useCallback, useMemo, useRef, useEffect } from 'react';
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
import { validatePlacement, isInvalidEmptyCellClick } from './mistakes';
import { detectStaleTarget, recoverFromStaleState } from './staleTarget';

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
 * Main hook for guided sequence flow with intelligent placement assistance
 * 
 * @param rows - Board height
 * @param cols - Board width
 * @param givens - Map of given cell values (key: "row,col", value: number)
 * @param maxValue - Maximum value in the puzzle (typically rows * cols)
 * @returns API object with state, board, and action methods
 * 
 * @example
 * ```tsx
 * const {
 *   state,
 *   board,
 *   selectAnchor,
 *   placeNext,
 *   removeCell,
 *   undo,
 *   redo,
 *   canUndo,
 *   canRedo,
 *   recentMistakes
 * } = useGuidedSequenceFlow(5, 5, givensMap, 25);
 * ```
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

  // Memoize chain computation to avoid redundant calculations
  // Only recompute when board actually changes
  const chainInfo = useMemo(() => {
    return computeChain(board, maxValue);
  }, [board, maxValue]);

  /**
   * Select a cell value as the anchor for guided placement
   * Recomputes legal targets based on the new anchor
   */
  const selectAnchor = useCallback(
    (pos: Position) => {
      const result = selectAnchorTransition(state, board, maxValue, pos);
      setState(result.state);
    },
    [state, board, maxValue]
  );

  /**
   * Place the next sequential value at the specified position
   * Validates placement before mutation; records mistakes if invalid
   * Automatically advances anchor to newly placed value
   */
  const placeNext = useCallback(
    (pos: Position) => {
      // Validate placement first
      const mistake = validatePlacement(pos, state.nextTarget, state.anchorPos, board);
      
      if (mistake) {
        // Record mistake but don't change board
        addMistake(mistake);
        return;
      }

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

  /**
   * Remove a player-placed cell value
   * Handles tail removal (enters neutral state) vs non-tail removal
   * Cannot remove given values or empty cells
   */
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

  /**
   * Toggle visual guidance highlights
   * @param enabled - Whether to show legal target highlights
   */
  const toggleGuide = useCallback(
    (enabled: boolean) => {
      const newState = toggleGuideTransition(state, enabled);
      setState(newState);
    },
    [state]
  );

  /**
   * Undo the last placement or removal action
   * Restores full state snapshot from undo stack
   */
  const undo = useCallback(() => {
    const action = undoRedoRef.current.undo();
    if (action) {
      const result = applyUndo(state, board, maxValue, action);
      setState(result.state);
      setBoard(result.board);
      setUndoRedoVersion((v) => v + 1);
    }
  }, [state, board, maxValue]);

  /**
   * Redo the last undone action
   * Replays action from redo stack
   */
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

  /**
   * Detect and recover from stale target states
   * Stale states occur when board changes invalidate displayed nextTarget
   * @internal Auto-invoked by useEffect on state changes
   */
  const checkAndRecoverStale = useCallback(() => {
    const check = detectStaleTarget(state, board, maxValue);
    if (check.isStale && check.recoveredState) {
      console.warn(
        `[GuidedSequenceFlow] Detected stale target: ${check.reason}. Recovering...`
      );
      setState(check.recoveredState);
      return true;
    }
    return false;
  }, [state, board, maxValue]);

  /**
   * Add a mistake event to the ring buffer
   * Maintains last 20 mistakes for UI feedback
   * @internal Called automatically by placeNext validation
   */
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

  // Auto-recover from stale state after board/state changes
  useEffect(() => {
    checkAndRecoverStale();
  }, [board, state.anchorValue, state.anchorPos, state.nextTarget]);

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
