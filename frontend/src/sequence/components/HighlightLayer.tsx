/**
 * Highlight Layer Component
 * Renders anchor and legal target highlights over the board
 */

import React from 'react';
import type { Position } from '../types';

interface HighlightLayerProps {
  /** Anchor position (or null) */
  anchorPos: Position | null;
  /** Legal target positions */
  legalTargets: Position[];
  /** Guide enabled flag */
  guideEnabled: boolean;
  /** Cell size in pixels */
  cellSize: number;
  /** Grid dimensions */
  rows: number;
  cols: number;
  /** Optional custom class name */
  className?: string;
}

export const HighlightLayer: React.FC<HighlightLayerProps> = ({
  anchorPos,
  legalTargets,
  guideEnabled,
  cellSize,
  rows,
  cols,
  className = '',
}) => {
  if (!guideEnabled) {
    return null;
  }

  return (
    <div
      className={`highlight-layer ${className}`}
      style={{
        position: 'absolute',
        top: 0,
        left: 0,
        width: cols * cellSize,
        height: rows * cellSize,
        pointerEvents: 'none',
      }}
      data-testid="highlight-layer"
    >
      {/* Anchor highlight */}
      {anchorPos && (
        <div
          className="highlight-anchor"
          data-testid="highlight-anchor"
          style={{
            position: 'absolute',
            left: anchorPos.col * cellSize,
            top: anchorPos.row * cellSize,
            width: cellSize,
            height: cellSize,
            border: '2px solid rgba(59, 130, 246, 0.6)',
            boxSizing: 'border-box',
          }}
        />
      )}

      {/* Legal target highlights */}
      {legalTargets.map((pos, idx) => (
        <div
          key={`${pos.row}-${pos.col}`}
          className="highlight-legal-target"
          data-testid={`highlight-legal-target-${pos.row}-${pos.col}`}
          style={{
            position: 'absolute',
            left: pos.col * cellSize,
            top: pos.row * cellSize,
            width: cellSize,
            height: cellSize,
            backgroundColor: 'rgba(34, 197, 94, 0.15)',
            boxSizing: 'border-box',
          }}
        />
      ))}
    </div>
  );
};
