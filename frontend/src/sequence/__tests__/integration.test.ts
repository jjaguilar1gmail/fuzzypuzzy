/**
 * Integration tests for complete guided sequence flow workflows
 * Tests full user journeys from start to completion
 */

import { describe, it, expect } from 'vitest';
import { selectAnchor, placeNext, removeCell } from '../transitions';
import { applyUndo, applyRedo } from '../transitions';
import type { BoardCell, SequenceState, UndoAction } from '../types';
import { computeChain } from '../chain';

function createTestBoard(values: Map<string, number>, rows = 5, cols = 5): BoardCell[][] {
  const board: BoardCell[][] = [];
  for (let row = 0; row < rows; row++) {
    const rowCells: BoardCell[] = [];
    for (let col = 0; col < cols; col++) {
      const key = `${row},${col}`;
      const value = values.get(key) ?? null;
      rowCells.push({
        position: { row, col },
        value,
        given: value !== null && value <= 3, // First 3 are givens
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

function createInitialState(): SequenceState {
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

describe('integration: full user flows', () => {
  describe('complete placement sequence', () => {
    it('places sequence from start to finish', () => {
      // Setup: Board with 1,2,3 as givens in a row
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      let currentBoard = board;

      // Step 1: Select anchor (value 3)
      const anchor = selectAnchor(state, currentBoard, 25, { row: 0, col: 2 });
      state = anchor.state;
      expect(state.anchorValue).toBe(3);
      expect(state.nextTarget).toBe(4);
      expect(state.legalTargets.length).toBeGreaterThan(0);

      // Step 2: Place 4
      const place4 = placeNext(state, currentBoard, 25, { row: 0, col: 3 });
      state = place4.state;
      currentBoard = place4.board;
      expect(state.anchorValue).toBe(4);
      expect(state.nextTarget).toBe(5);
      expect(currentBoard[0][3].value).toBe(4);

      // Step 3: Place 5
      const place5 = placeNext(state, currentBoard, 25, { row: 0, col: 4 });
      state = place5.state;
      currentBoard = place5.board;
      expect(state.anchorValue).toBe(5);
      expect(state.nextTarget).toBe(6);
      expect(currentBoard[0][4].value).toBe(5);

      // Step 4: Place 6 (wraps to next row)
      const place6 = placeNext(state, currentBoard, 25, { row: 1, col: 4 });
      state = place6.state;
      currentBoard = place6.board;
      expect(state.anchorValue).toBe(6);
      expect(state.nextTarget).toBe(7);
      expect(currentBoard[1][4].value).toBe(6);

      // Verify chain updated
      const finalChain = computeChain(currentBoard, 25);
      expect(finalChain.chainEndValue).toBe(6);
      expect(finalChain.chainLength).toBe(6);
    });

    it('handles diagonal placements', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      // Select anchor
      const anchor = selectAnchor(state, board, 25, { row: 0, col: 1 });
      state = anchor.state;

      // Place diagonally
      const diagonal = placeNext(state, board, 25, { row: 1, col: 2 });
      expect(diagonal.state.anchorValue).toBe(3);
      expect(diagonal.board[1][2].value).toBe(3);
    });
  });

  describe('undo/redo flow', () => {
    it('undoes and redoes multiple placements', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      let currentBoard = board;
      const undoStack: UndoAction[] = [];

      // Select anchor and place 3, 4, 5
      const anchor = selectAnchor(state, currentBoard, 25, { row: 0, col: 1 });
      state = anchor.state;

      const place3 = placeNext(state, currentBoard, 25, { row: 0, col: 2 });
      state = place3.state;
      currentBoard = place3.board;
      if (place3.undoAction) undoStack.push(place3.undoAction);

      const place4 = placeNext(state, currentBoard, 25, { row: 0, col: 3 });
      state = place4.state;
      currentBoard = place4.board;
      if (place4.undoAction) undoStack.push(place4.undoAction);

      const place5 = placeNext(state, currentBoard, 25, { row: 0, col: 4 });
      state = place5.state;
      currentBoard = place5.board;
      if (place5.undoAction) undoStack.push(place5.undoAction);

      expect(currentBoard[0][2].value).toBe(3);
      expect(currentBoard[0][3].value).toBe(4);
      expect(currentBoard[0][4].value).toBe(5);

      // Undo 5
      const undo5Action = undoStack.pop()!;
      const undo5 = applyUndo(state, currentBoard, 25, undo5Action);
      state = undo5.state;
      currentBoard = undo5.board;
      expect(currentBoard[0][4].value).toBe(null);
      expect(state.anchorValue).toBe(4);

      // Undo 4
      const undo4Action = undoStack.pop()!;
      const undo4 = applyUndo(state, currentBoard, 25, undo4Action);
      state = undo4.state;
      currentBoard = undo4.board;
      expect(currentBoard[0][3].value).toBe(null);
      expect(state.anchorValue).toBe(3);

      // Redo 4
      const redo4 = applyRedo(state, currentBoard, 25, undo4Action);
      state = redo4.state;
      currentBoard = redo4.board;
      expect(currentBoard[0][3].value).toBe(4);
      expect(state.anchorValue).toBe(4);

      // Redo 5
      const redo5 = applyRedo(state, currentBoard, 25, undo5Action);
      state = redo5.state;
      currentBoard = redo5.board;
      expect(currentBoard[0][4].value).toBe(5);
      expect(state.anchorValue).toBe(5);
    });
  });

  describe('removal and resume flow', () => {
    it('removes tail, enters neutral, and resumes', () => {
      // Setup: Chain 1->2->3->4
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
        ['0,3', 4],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      let currentBoard = board;

      // Select anchor at 4
      const anchor = selectAnchor(state, currentBoard, 25, { row: 0, col: 3 });
      state = anchor.state;
      expect(state.anchorValue).toBe(4);
      expect(state.nextTarget).toBe(5);

      // Remove tail (value 4) -> neutral state
      const removal = removeCell(state, currentBoard, 25, { row: 0, col: 3 });
      state = removal.state;
      currentBoard = removal.board;
      expect(state.anchorValue).toBe(null);
      expect(state.nextTarget).toBe(null);
      expect(state.nextTargetChangeReason).toBe('tail-removal');
      expect(state.chainEndValue).toBe(3);

      // Resume by selecting value 3
      const resume = selectAnchor(state, currentBoard, 25, { row: 0, col: 2 });
      state = resume.state;
      expect(state.anchorValue).toBe(3);
      expect(state.nextTarget).toBe(4);
      expect(state.legalTargets.length).toBeGreaterThan(0);

      // Continue placing from 4
      const place4 = placeNext(state, currentBoard, 25, { row: 1, col: 2 });
      state = place4.state;
      currentBoard = place4.board;
      expect(currentBoard[1][2].value).toBe(4);
      expect(state.anchorValue).toBe(4);
    });

    it('removes non-tail value - anchor preserved', () => {
      // Setup: Chain 1->2->3->4->5
      // Note: computeChain only checks value existence, not adjacency
      // So removing a middle value doesn't break the "chain" count
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['1,1', 3],
        ['2,1', 4],
        ['2,2', 5],
      ]));

      // Override given flags to allow removal of value 4
      board[2][1].given = false;

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      let currentBoard = board;

      // Select anchor at 5
      const anchor = selectAnchor(state, currentBoard, 25, { row: 2, col: 2 });
      state = anchor.state;
      expect(state.anchorValue).toBe(5);

      // Remove non-tail value (4) - not anchor, not tail (tail is 5)
      const removal = removeCell(state, currentBoard, 25, { row: 2, col: 1 });
      state = removal.state;
      currentBoard = removal.board;
      
      // Anchor preserved (not removed, not tail)
      expect(state.anchorValue).toBe(5);
      expect(state.nextTarget).toBe(6);
      expect(state.nextTargetChangeReason).toBe('non-tail-removal');
      
      // Chain now reports 1->3 (value 4 removed, so chain stops at 3)
      expect(state.chainEndValue).toBe(3);

      // Can still place from 5
      const place6 = placeNext(state, currentBoard, 25, { row: 2, col: 3 });
      expect(place6.board[2][3].value).toBe(6);
    });
  });

  describe('edge cases', () => {
    it('handles surrounded anchor (no legal targets)', () => {
      // Setup: Anchor surrounded by filled cells
      const board = createTestBoard(new Map([
        ['0,0', 10],
        ['0,1', 2],
        ['0,2', 11],
        ['1,0', 3],
        ['1,1', 1], // Anchor
        ['1,2', 12],
        ['2,0', 13],
        ['2,1', 14],
        ['2,2', 15],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      const anchor = selectAnchor(state, board, 25, { row: 1, col: 1 });
      state = anchor.state;
      
      // Should have nextTarget but no legal targets
      expect(state.anchorValue).toBe(1);
      expect(state.nextTarget).toBe(null); // Computed as null when no legal moves
      expect(state.legalTargets.length).toBe(0);
    });

    it('handles large board (10x10)', () => {
      const values = new Map<string, number>();
      for (let i = 1; i <= 10; i++) {
        values.set(`0,${i - 1}`, i);
      }
      const board = createTestBoard(values, 10, 10);

      const chainInfo = computeChain(board, 100);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      // Select anchor and place
      const anchor = selectAnchor(state, board, 100, { row: 0, col: 9 });
      state = anchor.state;
      expect(state.anchorValue).toBe(10);
      expect(state.nextTarget).toBe(11);

      const place = placeNext(state, board, 100, { row: 1, col: 9 });
      expect(place.board[1][9].value).toBe(11);
      expect(place.state.chainEndValue).toBe(11);
    });

    it('handles chain reaching maxValue', () => {
      // Setup: Chain 1->2->3 on 3x3 board (maxValue = 9)
      const values = new Map<string, number>();
      for (let i = 1; i <= 8; i++) {
        const row = Math.floor((i - 1) / 3);
        const col = (i - 1) % 3;
        values.set(`${row},${col}`, i);
      }
      const board = createTestBoard(values, 3, 3);

      const chainInfo = computeChain(board, 9);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      // Select anchor at 8
      const anchor = selectAnchor(state, board, 9, { row: 2, col: 1 });
      state = anchor.state;
      expect(state.nextTarget).toBe(9);

      // Place final value
      const final = placeNext(state, board, 9, { row: 2, col: 2 });
      state = final.state;
      expect(final.board[2][2].value).toBe(9);
      expect(state.nextTarget).toBe(null); // No more values
    });

    it('handles multi-chain board (only tracks longest from 1)', () => {
      // Setup: Two chains - 1->2->3 and 10->11->12
      const board = createTestBoard(new Map([
        ['0,0', 1],
        ['0,1', 2],
        ['0,2', 3],
        ['2,0', 10],
        ['2,1', 11],
        ['2,2', 12],
      ]));

      const chainInfo = computeChain(board, 25);
      // Should only track chain from 1
      expect(chainInfo.chainEndValue).toBe(3);
      expect(chainInfo.chainLength).toBe(3);

      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      // Select anchor from first chain
      const anchor1 = selectAnchor(state, board, 25, { row: 0, col: 2 });
      expect(anchor1.state.anchorValue).toBe(3);
      expect(anchor1.state.nextTarget).toBe(4);

      // Can also select from second chain (creates new sequence)
      const anchor2 = selectAnchor(state, board, 25, { row: 2, col: 2 });
      expect(anchor2.state.anchorValue).toBe(12);
      expect(anchor2.state.nextTarget).toBe(13);
    });
  });

  describe('boundary conditions', () => {
    it('handles corner cell placements', () => {
      const board = createTestBoard(new Map([
        ['0,0', 1],
      ]));

      const chainInfo = computeChain(board, 25);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      const anchor = selectAnchor(state, board, 25, { row: 0, col: 0 });
      state = anchor.state;
      
      // Corner has only 3 adjacents (no wrapping)
      expect(state.legalTargets.length).toBeLessThanOrEqual(3);
      
      // Place at adjacent corner
      const place = placeNext(state, board, 25, { row: 0, col: 1 });
      expect(place.board[0][1].value).toBe(2);
    });

    it('handles single cell board', () => {
      const board = createTestBoard(new Map([['0,0', 1]]), 1, 1);

      const chainInfo = computeChain(board, 1);
      let state: SequenceState = {
        ...createInitialState(),
        chainEndValue: chainInfo.chainEndValue,
        chainLength: chainInfo.chainLength,
      };

      const anchor = selectAnchor(state, board, 1, { row: 0, col: 0 });
      
      // No legal targets (no adjacents)
      expect(anchor.state.legalTargets.length).toBe(0);
      expect(anchor.state.nextTarget).toBe(null);
    });

    it('handles empty board', () => {
      const board = createTestBoard(new Map());

      const chainInfo = computeChain(board, 25);
      
      // No chain on empty board
      expect(chainInfo.chainEndValue).toBe(null);
      expect(chainInfo.chainLength).toBe(0);
      expect(chainInfo.nextCandidate).toBe(null);
    });
  });
});
