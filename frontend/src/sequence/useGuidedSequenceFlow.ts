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
  SequenceDirection,
} from './types';
import { UndoRedoStack } from './undoRedo';
import { computeChain } from './chain';
import { deriveNextTarget, computeLegalTargets } from './nextTarget';
import {
  selectAnchor as selectAnchorTransition,
  placeNext as placeNextTransition,
  removeCell as removeCellTransition,
  toggleGuide as toggleGuideTransition,
  setStepDirection as setStepDirectionTransition,
  applyUndo,
  applyRedo,
} from './transitions';
import { validatePlacement, isInvalidEmptyCellClick } from './mistakes';
import { detectStaleTarget, recoverFromStaleState } from './staleTarget';
import { loadSequenceSettings, saveSequenceSettings } from './playerSettings';

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
function initializeSequenceState(
  stepDirection: SequenceDirection = 'forward'
): SequenceState {
  return {
    anchorValue: null,
    anchorPos: null,
    nextTarget: null,
    legalTargets: [],
    guideEnabled: true,
    stepDirection,
    chainEndValue: null,
    chainLength: 0,
    nextTargetChangeReason: 'neutral',
  };
}

/**
 * Find the lowest-value anchor that can immediately expose legal targets.
 * Considers contiguous chain skipping logic by reusing next-target derivation.
 */
function findAnchorWithCandidates(
  board: BoardCell[][],
  direction: SequenceDirection
): Position | null {
  let bestCandidate:
    | { pos: Position; value: number; legalCount: number; sourceValue: number }
    | null = null;

  for (const row of board) {
    for (const cell of row) {
      const cellValue = cell.value;
      if (cellValue === null) continue;

      const targetResult = deriveNextTarget(
        cellValue,
        cell.position,
        board,
        direction
      );
      const anchorValue = targetResult.newAnchorValue ?? cellValue;
      const anchorPos = targetResult.newAnchorPos ?? cell.position;

      if (targetResult.nextTarget === null || anchorPos === null) {
        continue;
      }

      const legalTargets = computeLegalTargets(anchorPos, board);
      if (legalTargets.length === 0) {
        continue;
      }

      const shouldReplace =
        bestCandidate === null ||
        (direction === 'forward'
          ? anchorValue < bestCandidate.value
          : anchorValue > bestCandidate.value) ||
        (anchorValue === bestCandidate.value &&
          legalTargets.length > bestCandidate.legalCount) ||
        (anchorValue === bestCandidate.value &&
          legalTargets.length === bestCandidate.legalCount &&
          (direction === 'forward'
            ? cellValue < bestCandidate.sourceValue
            : cellValue > bestCandidate.sourceValue));

      if (shouldReplace) {
        bestCandidate = {
          pos: { ...anchorPos },
          value: anchorValue,
          legalCount: legalTargets.length,
          sourceValue: cellValue,
        };
      }
    }
  }

  return bestCandidate ? bestCandidate.pos : null;
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
  maxValue: number,
  resetKey = 0,
  callbacks?: { onPlacement?: () => void },
  initialBoard?: BoardCell[][] | null
): GuidedSequenceFlowAPI {
  // Initialize board and state - use initialBoard if provided (for restoration)
  const [board, setBoard] = useState(() => 
    initialBoard || initializeBoard(rows, cols, givens)
  );
  const [state, setState] = useState(() => {
    const storedDirection = loadSequenceSettings()?.stepDirection ?? 'forward';
    const initial = initializeSequenceState(storedDirection);
    const boardForChain = initialBoard || initializeBoard(rows, cols, givens);
    const chainInfo = computeChain(boardForChain, maxValue);
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
  const placementCallback = callbacks?.onPlacement;
  const settingsLoadedRef = useRef(false);

  // Reset board/state whenever puzzle inputs or reset key change
  // BUT: don't reset if we're being initialized with a restored board
  useEffect(() => {
    // Skip reset if we have an initial board (restoration scenario)
    if (initialBoard) {
      return;
    }
    
    const newBoard = initializeBoard(rows, cols, givens);
    const preferredDirection =
      loadSequenceSettings()?.stepDirection ?? 'forward';
    const baseState = initializeSequenceState(preferredDirection);
    const chainInfo = computeChain(newBoard, maxValue);

    setBoard(newBoard);
    setState({
      ...baseState,
      chainEndValue: chainInfo.chainEndValue,
      chainLength: chainInfo.chainLength,
    });

    undoRedoRef.current = new UndoRedoStack();
    setUndoRedoVersion(0);
    setMistakes([]);
    settingsLoadedRef.current = false;
  }, [rows, cols, maxValue, givens, resetKey]); // Note: initialBoard NOT in deps

  // Memoize chain computation to avoid redundant calculations
  // Only recompute when board actually changes
  const chainInfo = useMemo(() => {
    return computeChain(board, maxValue);
  }, [board, maxValue]);

  // Update board cell visual states (highlighted, anchor) based on current state
  useEffect(() => {
    setBoard((currentBoard) => {
      const updatedBoard = currentBoard.map((row) =>
        row.map((cell) => {
          const isAnchor =
            state.anchorPos !== null &&
            cell.position.row === state.anchorPos.row &&
            cell.position.col === state.anchorPos.col;

          const isHighlighted = state.legalTargets.some(
            (target) =>
              target.row === cell.position.row && target.col === cell.position.col
          );

          // Only create new object if something changed
          if (cell.anchor !== isAnchor || cell.highlighted !== isHighlighted) {
            const updated = {
              ...cell,
              anchor: isAnchor,
              highlighted: isHighlighted,
            };
            // Debug: Check if value is preserved
            if (cell.value !== null && updated.value !== cell.value) {
              console.error(`Value lost for cell [${cell.position.row},${cell.position.col}]:`, cell.value, '→', updated.value);
            }
            return updated;
          }
          return cell;
        })
      );

      return updatedBoard;
    });
  }, [state.anchorPos, state.legalTargets]);

  // Automatically pick the lowest-value anchor with legal targets on load
  useEffect(() => {
    if (state.anchorPos !== null) {
      return;
    }

    const autoAnchorPos = findAnchorWithCandidates(board, state.stepDirection);
    if (!autoAnchorPos) {
      return;
    }

    const result = selectAnchorTransition(state, board, maxValue, autoAnchorPos);
    setState(result.state);
  }, [board, maxValue, state]);

  useEffect(() => {
    if (settingsLoadedRef.current) {
      return;
    }

    const stored = loadSequenceSettings();
    if (stored && stored.stepDirection !== state.stepDirection) {
      setState((current) =>
        setStepDirectionTransition(current, board, stored.stepDirection)
      );
    }

    settingsLoadedRef.current = true;
  }, [board, state.stepDirection]);

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
        placementCallback?.();
      }
      
      setState(result.state);
      setBoard(result.board);
    },
    [state, board, maxValue, placementCallback]
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
   * Switch between forward/backward stepping directions
   */
  const setStepDirection = useCallback(
    (direction: SequenceDirection) => {
      setState((current) =>
        setStepDirectionTransition(current, board, direction)
      );
      saveSequenceSettings({ stepDirection: direction });
    },
    [board]
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
    setStepDirection,
    undo,
    redo,
    canUndo,
    canRedo,
    recentMistakes: mistakes,
  };
}
