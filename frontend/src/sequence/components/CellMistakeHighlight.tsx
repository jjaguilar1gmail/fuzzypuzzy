/**
 * Cell Mistake Highlight Component
 * Shows a red outline on cells with invalid placement attempts
 */

import React, { useEffect, useState } from 'react';
import type { Position } from '../types';

interface CellMistakeHighlightProps {
  /** Position of the mistake */
  mistakePos: Position | null;
  /** Cell size in pixels */
  cellSize: number;
  /** Display duration in milliseconds */
  duration?: number;
}

export const CellMistakeHighlight: React.FC<CellMistakeHighlightProps> = ({
  mistakePos,
  cellSize,
  duration = 1200,
}) => {
  const [visible, setVisible] = useState(false);
  const [position, setPosition] = useState<Position | null>(null);

  useEffect(() => {
    if (mistakePos) {
      setPosition(mistakePos);
      setVisible(true);

      const timer = setTimeout(() => {
        setVisible(false);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [mistakePos, duration]);

  if (!visible || !position) {
    return null;
  }

  return (
    <div
      className="cell-mistake-highlight"
      data-testid={`mistake-highlight-${position.row}-${position.col}`}
      style={{
        position: 'absolute',
        left: position.col * cellSize,
        top: position.row * cellSize,
        width: cellSize,
        height: cellSize,
        border: '3px solid rgba(239, 68, 68, 0.8)',
        borderRadius: '4px',
        boxSizing: 'border-box',
        pointerEvents: 'none',
        animation: 'mistakePulse 0.6s ease-in-out',
        zIndex: 10,
      }}
    />
  );
};

/**
 * CSS animation (add to global styles)
 * 
 * @keyframes mistakePulse {
 *   0% { transform: scale(1); opacity: 1; }
 *   50% { transform: scale(1.05); opacity: 0.8; }
 *   100% { transform: scale(1); opacity: 1; }
 * }
 */
