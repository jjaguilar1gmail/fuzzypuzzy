/**
 * Example: Basic Integration of Guided Sequence Flow
 * 
 * This demonstrates minimal integration of the guided sequence flow hook
 * into an existing Hidato puzzle component.
 */

import React from 'react';
import { useGuidedSequenceFlow } from '@/sequence';
import { NextNumberIndicator, HighlightLayer } from '@/sequence/components';

interface SimplePuzzleProps {
  rows: number;
  cols: number;
  givens: Map<string, number>; // Map of "row,col" -> value
  maxValue: number;
}

export const SimplePuzzleExample: React.FC<SimplePuzzleProps> = ({
  rows,
  cols,
  givens,
  maxValue,
}) => {
  const api = useGuidedSequenceFlow(rows, cols, givens, maxValue);

  const cellSize = 60; // pixels

  return (
    <div className="puzzle-container">
      {/* Next Number Indicator */}
      <div className="puzzle-header">
        <NextNumberIndicator
          nextTarget={api.state.nextTarget}
          guideEnabled={api.state.guideEnabled}
        />
        
        {/* Guide Toggle */}
        <button
          onClick={() => api.toggleGuide(!api.state.guideEnabled)}
          className="guide-toggle"
        >
          {api.state.guideEnabled ? 'Hide Guide' : 'Show Guide'}
        </button>

        {/* Undo/Redo */}
        <div className="undo-redo-controls">
          <button onClick={api.undo} disabled={!api.canUndo}>
            Undo
          </button>
          <button onClick={api.redo} disabled={!api.canRedo}>
            Redo
          </button>
        </div>
      </div>

      {/* Puzzle Board */}
      <div
        className="puzzle-board"
        style={{
          position: 'relative',
          width: cols * cellSize,
          height: rows * cellSize,
        }}
      >
        {/* Highlight Layer (rendered below cells) */}
        <HighlightLayer
          anchorPos={api.state.anchorPos}
          legalTargets={api.state.legalTargets}
          guideEnabled={api.state.guideEnabled}
          cellSize={cellSize}
          rows={rows}
          cols={cols}
        />

        {/* Board Grid */}
        <div className="board-grid">
          {api.board.map((row, rowIdx) =>
            row.map((cell, colIdx) => (
              <div
                key={`${rowIdx}-${colIdx}`}
                data-testid={`cell-${rowIdx}-${colIdx}`}
                className={`cell ${cell.given ? 'given' : ''} ${cell.blocked ? 'blocked' : ''}`}
                style={{
                  position: 'absolute',
                  left: colIdx * cellSize,
                  top: rowIdx * cellSize,
                  width: cellSize,
                  height: cellSize,
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  border: '1px solid #ccc',
                  cursor: cell.value !== null ? 'pointer' : 'default',
                }}
                onClick={() => {
                  if (cell.value !== null) {
                    // Select anchor
                    api.selectAnchor(cell.position);
                  } else if (
                    api.state.nextTarget !== null &&
                    api.state.legalTargets.some(
                      (t) => t.row === rowIdx && t.col === colIdx
                    )
                  ) {
                    // Place next value
                    api.placeNext(cell.position);
                  }
                }}
                onContextMenu={(e) => {
                  e.preventDefault();
                  if (cell.value !== null && !cell.given) {
                    // Remove cell (right-click)
                    api.removeCell(cell.position);
                  }
                }}
              >
                {cell.value !== null && (
                  <span className={cell.given ? 'value-given' : 'value-player'}>
                    {cell.value}
                  </span>
                )}
              </div>
            ))
          )}
        </div>
      </div>

      {/* Debug Info (development only) */}
      {process.env.NODE_ENV === 'development' && (
        <div className="debug-info" style={{ marginTop: 20, fontSize: 12 }}>
          <div>Anchor: {api.state.anchorValue ?? 'none'}</div>
          <div>Next: {api.state.nextTarget ?? 'none'}</div>
          <div>Chain: {api.state.chainEndValue ?? 'empty'} (length {api.state.chainLength})</div>
          <div>Change Reason: {api.state.nextTargetChangeReason}</div>
          <div>Legal Targets: {api.state.legalTargets.length}</div>
        </div>
      )}
    </div>
  );
};

/**
 * Usage Example:
 * 
 * const givens = new Map([
 *   ['0,0', 1],
 *   ['2,2', 5],
 *   ['4,4', 9],
 * ]);
 * 
 * <SimplePuzzleExample
 *   rows={5}
 *   cols={5}
 *   givens={givens}
 *   maxValue={25}
 * />
 */
