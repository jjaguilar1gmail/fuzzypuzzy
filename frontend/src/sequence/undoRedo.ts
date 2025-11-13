/**
 * Undo/redo stack manager for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { UndoAction, SequenceState } from './types';

const MAX_UNDO_STACK_SIZE = 50;

/**
 * Undo/redo stack manager
 */
export class UndoRedoStack {
  private undoStack: UndoAction[] = [];
  private redoStack: UndoAction[] = [];

  /**
   * Push a new action onto the undo stack
   * Clears redo stack and trims undo stack if exceeds limit
   */
  push(action: UndoAction): void {
    this.undoStack.push(action);

    // Trim oldest if exceeds cap
    if (this.undoStack.length > MAX_UNDO_STACK_SIZE) {
      this.undoStack.shift();
    }

    // Clear redo stack on new action
    this.redoStack = [];
  }

  /**
   * Pop an action from undo stack and push to redo stack
   * @returns The undone action or null if stack empty
   */
  undo(): UndoAction | null {
    const action = this.undoStack.pop();
    if (action) {
      this.redoStack.push(action);
    }
    return action ?? null;
  }

  /**
   * Pop an action from redo stack and push to undo stack
   * @returns The redone action or null if stack empty
   */
  redo(): UndoAction | null {
    const action = this.redoStack.pop();
    if (action) {
      this.undoStack.push(action);
    }
    return action ?? null;
  }

  /**
   * Check if undo is available
   */
  canUndo(): boolean {
    return this.undoStack.length > 0;
  }

  /**
   * Check if redo is available
   */
  canRedo(): boolean {
    return this.redoStack.length > 0;
  }

  /**
   * Get current undo stack size
   */
  getUndoSize(): number {
    return this.undoStack.length;
  }

  /**
   * Get current redo stack size
   */
  getRedoSize(): number {
    return this.redoStack.length;
  }

  /**
   * Clear both stacks
   */
  clear(): void {
    this.undoStack = [];
    this.redoStack = [];
  }
}

/**
 * Create a sequence state snapshot for undo/redo
 * @param state - Current sequence state
 * @returns Partial sequence state for restoration
 */
export function createSequenceSnapshot(
  state: SequenceState
): Partial<SequenceState> {
  return {
    anchorValue: state.anchorValue,
    anchorPos: state.anchorPos ? { ...state.anchorPos } : null,
    nextTarget: state.nextTarget,
    chainEndValue: state.chainEndValue,
    chainLength: state.chainLength,
    nextTargetChangeReason: state.nextTargetChangeReason,
  };
}

/**
 * Restore sequence state from snapshot
 * @param currentState - Current sequence state
 * @param snapshot - Snapshot to restore from
 * @returns Updated sequence state
 */
export function restoreSequenceSnapshot(
  currentState: SequenceState,
  snapshot: Partial<SequenceState>
): SequenceState {
  return {
    ...currentState,
    anchorValue: snapshot.anchorValue ?? currentState.anchorValue,
    anchorPos: snapshot.anchorPos
      ? { ...snapshot.anchorPos }
      : currentState.anchorPos,
    nextTarget: snapshot.nextTarget ?? currentState.nextTarget,
    chainEndValue: snapshot.chainEndValue ?? currentState.chainEndValue,
    chainLength: snapshot.chainLength ?? currentState.chainLength,
    nextTargetChangeReason:
      snapshot.nextTargetChangeReason ?? currentState.nextTargetChangeReason,
  };
}
