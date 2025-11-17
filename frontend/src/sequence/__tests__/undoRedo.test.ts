/**
 * Unit tests for undo/redo stack
 */

import { describe, it, expect, beforeEach } from 'vitest';
import { UndoRedoStack, createSequenceSnapshot, restoreSequenceSnapshot } from '../undoRedo';
import type { UndoAction, SequenceState } from '../types';

describe('UndoRedoStack', () => {
  let stack: UndoRedoStack;

  beforeEach(() => {
    stack = new UndoRedoStack();
  });

  describe('push and undo', () => {
    it('pushes action and allows undo', () => {
      const action: UndoAction = {
        type: 'PLACE',
        position: { row: 0, col: 0 },
        value: 1,
        previousSequenceSnapshot: {},
        timestamp: Date.now(),
        changeReason: 'placement',
      };

      stack.push(action);
      expect(stack.canUndo()).toBe(true);
      expect(stack.canRedo()).toBe(false);

      const undone = stack.undo();
      expect(undone).toEqual(action);
      expect(stack.canUndo()).toBe(false);
      expect(stack.canRedo()).toBe(true);
    });

    it('trims oldest action when exceeding cap', () => {
      // Push 51 actions
      for (let i = 0; i < 51; i++) {
        stack.push({
          type: 'PLACE',
          position: { row: 0, col: 0 },
          value: i,
          previousSequenceSnapshot: {},
          timestamp: Date.now(),
          changeReason: 'placement',
        });
      }

      expect(stack.getUndoSize()).toBe(50);
    });
  });

  describe('redo', () => {
    it('allows redo after undo', () => {
      const action: UndoAction = {
        type: 'PLACE',
        position: { row: 0, col: 0 },
        value: 1,
        previousSequenceSnapshot: {},
        timestamp: Date.now(),
        changeReason: 'placement',
      };

      stack.push(action);
      stack.undo();

      expect(stack.canRedo()).toBe(true);
      const redone = stack.redo();
      expect(redone).toEqual(action);
      expect(stack.canUndo()).toBe(true);
      expect(stack.canRedo()).toBe(false);
    });

    it('clears redo stack on new push', () => {
      const action1: UndoAction = {
        type: 'PLACE',
        position: { row: 0, col: 0 },
        value: 1,
        previousSequenceSnapshot: {},
        timestamp: Date.now(),
        changeReason: 'placement',
      };

      const action2: UndoAction = {
        type: 'PLACE',
        position: { row: 0, col: 1 },
        value: 2,
        previousSequenceSnapshot: {},
        timestamp: Date.now(),
        changeReason: 'placement',
      };

      stack.push(action1);
      stack.undo();
      expect(stack.canRedo()).toBe(true);

      stack.push(action2);
      expect(stack.canRedo()).toBe(false);
    });
  });

  describe('clear', () => {
    it('clears both stacks', () => {
      stack.push({
        type: 'PLACE',
        position: { row: 0, col: 0 },
        value: 1,
        previousSequenceSnapshot: {},
        timestamp: Date.now(),
        changeReason: 'placement',
      });

      stack.clear();
      expect(stack.canUndo()).toBe(false);
      expect(stack.canRedo()).toBe(false);
    });
  });
});

describe('sequence snapshot utilities', () => {
  describe('createSequenceSnapshot', () => {
    it('captures essential sequence state', () => {
      const state: SequenceState = {
        anchorValue: 5,
        anchorPos: { row: 2, col: 3 },
        nextTarget: 6,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 5,
        chainLength: 5,
        nextTargetChangeReason: 'placement',
      };

      const snapshot = createSequenceSnapshot(state);
      expect(snapshot.anchorValue).toBe(5);
      expect(snapshot.anchorPos).toEqual({ row: 2, col: 3 });
      expect(snapshot.nextTarget).toBe(6);
      expect(snapshot.chainEndValue).toBe(5);
      expect(snapshot.chainLength).toBe(5);
    });
  });

  describe('restoreSequenceSnapshot', () => {
    it('restores state from snapshot', () => {
      const currentState: SequenceState = {
        anchorValue: 10,
        anchorPos: { row: 5, col: 5 },
        nextTarget: 11,
        legalTargets: [],
        guideEnabled: true,
        stepDirection: 'forward',
        chainEndValue: 10,
        chainLength: 10,
        nextTargetChangeReason: 'placement',
      };

      const snapshot = {
        anchorValue: 5,
        anchorPos: { row: 2, col: 3 },
        nextTarget: 6,
        chainEndValue: 5,
        chainLength: 5,
      };

      const restored = restoreSequenceSnapshot(currentState, snapshot);
      expect(restored.anchorValue).toBe(5);
      expect(restored.anchorPos).toEqual({ row: 2, col: 3 });
      expect(restored.nextTarget).toBe(6);
      expect(restored.chainEndValue).toBe(5);
      expect(restored.chainLength).toBe(5);
    });
  });
});
