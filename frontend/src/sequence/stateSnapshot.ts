/**
 * State snapshot utility for debugging
 * Based on specs/001-guided-sequence-flow/contracts/stateSnapshot.ts
 */

import type { SequenceState, BoardCell } from './types';

export interface SequenceSnapshot {
  timestamp: number;
  state: SequenceState;
  boardSummary: {
    filledCells: number;
    givenCells: number;
    emptyCells: number;
  };
  chainSummary: string;
}

/**
 * Capture current sequence state as a snapshot for debugging
 */
export function captureSequenceSnapshot(
  state: SequenceState,
  board: BoardCell[][]
): SequenceSnapshot {
  let filledCells = 0;
  let givenCells = 0;
  let emptyCells = 0;

  for (const row of board) {
    for (const cell of row) {
      if (cell.value !== null) {
        filledCells++;
        if (cell.given) {
          givenCells++;
        }
      } else {
        emptyCells++;
      }
    }
  }

  const chainSummary =
    state.chainEndValue !== null
      ? `Chain: 1..${state.chainEndValue} (length ${state.chainLength})`
      : 'Chain: empty';

  return {
    timestamp: Date.now(),
    state: { ...state },
    boardSummary: {
      filledCells,
      givenCells,
      emptyCells,
    },
    chainSummary,
  };
}

/**
 * Format snapshot as human-readable string
 */
export function formatSnapshot(snapshot: SequenceSnapshot): string {
  const lines: string[] = [];

  lines.push(`=== Sequence Snapshot (${new Date(snapshot.timestamp).toISOString()}) ===`);
  lines.push('');
  lines.push(`Anchor: ${snapshot.state.anchorValue ?? 'none'} at ${snapshot.state.anchorPos ? `(${snapshot.state.anchorPos.row},${snapshot.state.anchorPos.col})` : 'N/A'}`);
  lines.push(`Next Target: ${snapshot.state.nextTarget ?? 'none'}`);
  lines.push(`Legal Targets: ${snapshot.state.legalTargets.length} positions`);
  lines.push(`Guide Enabled: ${snapshot.state.guideEnabled}`);
  lines.push('');
  lines.push(snapshot.chainSummary);
  lines.push(`Change Reason: ${snapshot.state.nextTargetChangeReason}`);
  lines.push('');
  lines.push(`Board: ${snapshot.boardSummary.filledCells} filled (${snapshot.boardSummary.givenCells} given), ${snapshot.boardSummary.emptyCells} empty`);

  return lines.join('\n');
}
