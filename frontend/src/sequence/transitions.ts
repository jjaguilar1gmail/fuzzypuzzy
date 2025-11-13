/**
 * State transitions for guided sequence flow
 * Pure reducer functions implementing state machine
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type {
  BoardCell,
  Position,
  SequenceState,
  UndoAction,
  NextTargetChangeReason,
} from './types';
import { positionsEqual } from './adjacency';
import { computeChain } from './chain';
import { deriveNextTarget, computeLegalTargets } from './nextTarget';
import { classifyRemoval } from './removal';
import { createSequenceSnapshot } from './undoRedo';

/**
 * Action: SELECT_ANCHOR
 * User clicks a cell with a value to make it the anchor
 */
export function selectAnchor(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number,
  pos: Position
): { state: SequenceState; undoAction: null } {
  const cell = board[pos.row][pos.col];

  // Cell must have a value
  if (cell.value === null) {
    return { state, undoAction: null };
  }

  // Update anchor
  const anchorValue = cell.value;
  const anchorPos = { ...pos };

  // Recompute next target and legal targets
  const targetResult = deriveNextTarget(anchorValue, anchorPos, board);
  const finalAnchorValue = targetResult.newAnchorValue ?? anchorValue;
  const finalAnchorPos = targetResult.newAnchorPos ?? anchorPos;
  const legalTargets = computeLegalTargets(finalAnchorPos, board);

  const newState: SequenceState = {
    ...state,
    anchorValue: finalAnchorValue,
    anchorPos: finalAnchorPos,
    nextTarget: targetResult.nextTarget,
    legalTargets,
    nextTargetChangeReason: 'anchor-change',
  };

  // No undo action for anchor selection
  return { state: newState, undoAction: null };
}

/**
 * Action: PLACE_NEXT
 * User places the next target value at a legal position
 */
export function placeNext(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number,
  pos: Position
): { state: SequenceState; board: BoardCell[][]; undoAction: UndoAction | null } {
  // Must have a next target
  if (state.nextTarget === null) {
    return { state, board, undoAction: null };
  }

  // Position must be in legal targets
  const isLegal = state.legalTargets.some((target) =>
    positionsEqual(target, pos)
  );
  if (!isLegal) {
    return { state, board, undoAction: null };
  }

  // Create snapshot before modification
  const snapshot = createSequenceSnapshot(state);

  // Update board
  const newBoard = board.map((row) => [...row]);
  const cell = newBoard[pos.row][pos.col];
  const placedValue = state.nextTarget;
  cell.value = placedValue;

  // Create undo action
  const undoAction: UndoAction = {
    type: 'PLACE',
    position: { ...pos },
    value: placedValue,
    previousSequenceSnapshot: snapshot,
    timestamp: Date.now(),
    changeReason: 'placement',
  };

  // Update anchor to newly placed value
  const anchorValue = placedValue;
  const anchorPos = { ...pos };

  // Recompute chain info
  const chainInfo = computeChain(newBoard, maxValue);

  // Recompute next target and legal targets
  const targetResult = deriveNextTarget(anchorValue, anchorPos, newBoard);
  const finalAnchorValue = targetResult.newAnchorValue ?? anchorValue;
  const finalAnchorPos = targetResult.newAnchorPos ?? anchorPos;
  const legalTargets = computeLegalTargets(finalAnchorPos, newBoard);

  const newState: SequenceState = {
    ...state,
    anchorValue: finalAnchorValue,
    anchorPos: finalAnchorPos,
    nextTarget: targetResult.nextTarget,
    legalTargets,
    chainEndValue: chainInfo.chainEndValue,
    chainLength: chainInfo.chainLength,
    nextTargetChangeReason: 'placement',
  };

  return { state: newState, board: newBoard, undoAction };
}

/**
 * Action: REMOVE_CELL
 * User removes a value from a non-given cell
 */
export function removeCell(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number,
  pos: Position
): { state: SequenceState; board: BoardCell[][]; undoAction: UndoAction | null } {
  const cell = board[pos.row][pos.col];

  // Cannot remove from given or empty cells
  if (cell.value === null || cell.given) {
    return { state, board, undoAction: null };
  }

  // Create snapshot before modification
  const snapshot = createSequenceSnapshot(state);

  const removedValue = cell.value;
  const prevChainEnd = state.chainEndValue;

  // Update board
  const newBoard = board.map((row) => [...row]);
  newBoard[pos.row][pos.col].value = null;

  // Recompute chain info
  const chainInfo = computeChain(newBoard, maxValue);

  // Classify removal
  const classification = classifyRemoval(prevChainEnd, removedValue);
  const changeReason: NextTargetChangeReason =
    classification === 'tail-removal' ? 'tail-removal' : 'non-tail-removal';

  // Create undo action
  const undoAction: UndoAction = {
    type: 'REMOVE',
    position: { ...pos },
    value: removedValue,
    previousSequenceSnapshot: snapshot,
    timestamp: Date.now(),
    changeReason,
  };

  // Determine if anchor should be cleared
  const isAnchorRemoved =
    state.anchorPos !== null && positionsEqual(state.anchorPos, pos);
  const isTailRemoval = classification === 'tail-removal';

  let newState: SequenceState;

  if (isAnchorRemoved || isTailRemoval) {
    // Clear anchor and enter neutral state
    newState = {
      ...state,
      anchorValue: null,
      anchorPos: null,
      nextTarget: null,
      legalTargets: [],
      chainEndValue: chainInfo.chainEndValue,
      chainLength: chainInfo.chainLength,
      nextTargetChangeReason: changeReason,
    };
  } else {
    // Keep anchor but recompute next target
    const targetResult = deriveNextTarget(
      state.anchorValue,
      state.anchorPos,
      newBoard
    );
    const finalAnchorValue = targetResult.newAnchorValue ?? state.anchorValue;
    const finalAnchorPos = targetResult.newAnchorPos ?? state.anchorPos;
    const legalTargets = computeLegalTargets(finalAnchorPos, newBoard);

    newState = {
      ...state,
      anchorValue: finalAnchorValue,
      anchorPos: finalAnchorPos,
      nextTarget: targetResult.nextTarget,
      legalTargets,
      chainEndValue: chainInfo.chainEndValue,
      chainLength: chainInfo.chainLength,
      nextTargetChangeReason: changeReason,
    };
  }

  return { state: newState, board: newBoard, undoAction };
}

/**
 * Action: TOGGLE_GUIDE
 * User toggles guide visibility
 */
export function toggleGuide(
  state: SequenceState,
  enabled: boolean
): SequenceState {
  return {
    ...state,
    guideEnabled: enabled,
  };
}

/**
 * Action: UNDO
 * Restore previous state from undo action
 */
export function applyUndo(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number,
  action: UndoAction
): { state: SequenceState; board: BoardCell[][] } {
  const newBoard = board.map((row) => [...row]);

  if (action.type === 'PLACE') {
    // Reverse placement: clear cell
    newBoard[action.position.row][action.position.col].value = null;
  } else if (action.type === 'REMOVE') {
    // Reverse removal: restore value
    newBoard[action.position.row][action.position.col].value = action.value;
  }

  // Restore snapshot
  const restoredState: SequenceState = {
    ...state,
    anchorValue: action.previousSequenceSnapshot.anchorValue ?? null,
    anchorPos: action.previousSequenceSnapshot.anchorPos
      ? { ...action.previousSequenceSnapshot.anchorPos }
      : null,
    nextTarget: action.previousSequenceSnapshot.nextTarget ?? null,
    chainEndValue: action.previousSequenceSnapshot.chainEndValue ?? null,
    chainLength: action.previousSequenceSnapshot.chainLength ?? 0,
    nextTargetChangeReason:
      action.previousSequenceSnapshot.nextTargetChangeReason ?? 'neutral',
  };

  // Recompute legal targets if anchor exists
  const legalTargets = computeLegalTargets(restoredState.anchorPos, newBoard);

  const newState: SequenceState = {
    ...restoredState,
    legalTargets,
  };

  return { state: newState, board: newBoard };
}

/**
 * Action: REDO
 * Reapply undone action
 */
export function applyRedo(
  state: SequenceState,
  board: BoardCell[][],
  maxValue: number,
  action: UndoAction
): { state: SequenceState; board: BoardCell[][] } {
  const newBoard = board.map((row) => [...row]);

  if (action.type === 'PLACE') {
    // Reapply placement
    newBoard[action.position.row][action.position.col].value = action.value;
  } else if (action.type === 'REMOVE') {
    // Reapply removal
    newBoard[action.position.row][action.position.col].value = null;
  }

  // Recompute chain info
  const chainInfo = computeChain(newBoard, maxValue);

  // Determine new state based on action type
  let newState: SequenceState;

  if (action.type === 'PLACE') {
    const anchorValue = action.value;
    const anchorPos = { ...action.position };
    const targetResult = deriveNextTarget(anchorValue, anchorPos, newBoard);
    const finalAnchorValue = targetResult.newAnchorValue ?? anchorValue;
    const finalAnchorPos = targetResult.newAnchorPos ?? anchorPos;
    const legalTargets = computeLegalTargets(finalAnchorPos, newBoard);

    newState = {
      ...state,
      anchorValue: finalAnchorValue,
      anchorPos: finalAnchorPos,
      nextTarget: targetResult.nextTarget,
      legalTargets,
      chainEndValue: chainInfo.chainEndValue,
      chainLength: chainInfo.chainLength,
      nextTargetChangeReason: action.changeReason,
    };
  } else {
    // REMOVE: use change reason to determine if anchor cleared
    if (action.changeReason === 'tail-removal') {
      newState = {
        ...state,
        anchorValue: null,
        anchorPos: null,
        nextTarget: null,
        legalTargets: [],
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
        nextTargetChangeReason: action.changeReason,
      };
    } else {
      // Check if anchor was removed
      const anchorStillValid =
        state.anchorPos !== null &&
        newBoard[state.anchorPos.row][state.anchorPos.col].value !== null;

      if (anchorStillValid) {
        const targetResult = deriveNextTarget(
          state.anchorValue,
          state.anchorPos,
          newBoard
        );
        const finalAnchorValue = targetResult.newAnchorValue ?? state.anchorValue;
        const finalAnchorPos = targetResult.newAnchorPos ?? state.anchorPos;
        const legalTargets = computeLegalTargets(finalAnchorPos, newBoard);

        newState = {
          ...state,
          anchorValue: finalAnchorValue,
          anchorPos: finalAnchorPos,
          nextTarget: targetResult.nextTarget,
          legalTargets,
          chainEndValue: chainInfo.chainEndValue,
          chainLength: chainInfo.chainLength,
          nextTargetChangeReason: action.changeReason,
        };
      } else {
        newState = {
          ...state,
          anchorValue: null,
          anchorPos: null,
          nextTarget: null,
          legalTargets: [],
          chainEndValue: chainInfo.chainEndValue,
          chainLength: chainInfo.chainLength,
          nextTargetChangeReason: action.changeReason,
        };
      }
    }
  }

  return { state: newState, board: newBoard };
}
