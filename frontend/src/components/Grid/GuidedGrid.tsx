import { useGameStore } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo, useEffect, useState } from 'react';
import { useGuidedSequenceFlow } from '@/sequence';
import type { Position } from '@/sequence/types';

/**
 * Grid component integrated with guided sequence flow
 */
const GuidedGrid = memo(function GuidedGrid() {
  const puzzle = useGameStore((state) => state.puzzle);
  const puzzleInstance = useGameStore((state) => state.puzzleInstance);
  const updateSequenceState = useGameStore((state) => state.updateSequenceState);

  // Convert puzzle givens to Map format
  const givensMap = useMemo(() => {
    if (!puzzle) return new Map<string, number>();
    const map = new Map<string, number>();
    puzzle.givens.forEach(({ row, col, value }) => {
      map.set(`${row},${col}`, value);
    });
    return map;
  }, [puzzle]);

  // Calculate max value (size^2 for Hidato)
  const maxValue = useMemo(() => {
    return puzzle ? puzzle.size * puzzle.size : 25;
  }, [puzzle?.size]);

  // Initialize guided sequence flow
  const {
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
    recentMistakes,
  } = useGuidedSequenceFlow(
    puzzle?.size || 5,
    puzzle?.size || 5,
    givensMap,
    maxValue,
    puzzleInstance
  );

  // Sync sequence state with game store
  useEffect(() => {
    updateSequenceState(state, board, recentMistakes);
  }, [state, board, recentMistakes, updateSequenceState]);

  // Track focused cell for keyboard navigation
  const [focusedCell, setFocusedCell] = useState<Position | null>(null);

  // Auto-dismiss mistakes after 3 seconds
  const [visibleMistakes, setVisibleMistakes] = useState<typeof recentMistakes>([]);

  useEffect(() => {
    if (recentMistakes.length > 0) {
      setVisibleMistakes(recentMistakes);
      const latestMistake = recentMistakes[0];
      const timer = setTimeout(() => {
        setVisibleMistakes((current) =>
          current.filter((m) => m.timestamp !== latestMistake.timestamp)
        );
      }, 3000); // Dismiss after 3 seconds

      return () => clearTimeout(timer);
    }
  }, [recentMistakes]);

  // Memoize grid dimensions to prevent recalculation
  const dimensions = useMemo(() => {
    if (!board) return null;
    const cellSize = 60;
    const gap = 2;
    const totalSize = board.length * cellSize + (board.length - 1) * gap;
    return { cellSize, gap, totalSize };
  }, [board?.length]);

  const handleCellClick = (row: number, col: number) => {
    const pos: Position = { row, col };
    const cell = board[row][col];

    // If cell has a value
    if (cell.value !== null) {
      // If it's a given (immutable), select as anchor
      if (cell.given) {
        selectAnchor(pos);
      }
      // If it's player-placed, remove it
      else {
        removeCell(pos);
      }
    }
    // If cell is empty and is a legal target, place next value
    else if (state.legalTargets.some((t) => t.row === row && t.col === col)) {
      placeNext(pos);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent, row: number, col: number) => {
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      handleCellClick(row, col);
    } else if (e.key === 'z' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      undo();
    } else if (e.key === 'y' && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      redo();
    } else if (e.key === 'Backspace' || e.key === 'Delete') {
      e.preventDefault();
      const cell = board[row][col];
      if (cell.value !== null && !cell.given) {
        removeCell({ row, col });
      }
    }
  };

  if (!puzzle || !board || !dimensions) return null;

  const { cellSize, gap, totalSize } = dimensions;

  return (
    <div className="relative">
      <style>{`
        .cell-rect:focus {
          outline: none;
        }
      `}</style>
      <svg
        width={totalSize}
        height={totalSize}
        viewBox={`0 0 ${totalSize} ${totalSize}`}
        className="mx-auto"
        role="grid"
        aria-label="Hidato puzzle grid"
      >
        {board.map((row, r) =>
          row.map((cell, c) => {
            const x = c * (cellSize + gap);
            const y = r * (cellSize + gap);
            const isAnchor = cell.anchor;
            const isHighlighted = cell.highlighted && state.guideEnabled; // Only show highlights if guide is enabled
            const isMistake = cell.mistake;
            const isGiven = cell.given;
            const hasValue = cell.value !== null;
            const isFocused = focusedCell?.row === r && focusedCell?.col === c;

            // Determine fill color based on cell state
            let fillColor = 'white';
            if (isAnchor) fillColor = 'rgb(254, 240, 138)'; // yellow-200
            else if (isHighlighted) fillColor = 'rgb(191, 219, 254)'; // blue-200
            else if (isMistake) fillColor = 'rgb(254, 202, 202)'; // red-200
            else if (isGiven) fillColor = 'rgb(229, 231, 235)'; // gray-200

            // Determine stroke color
            let strokeColor = 'rgb(203, 213, 225)'; // slate-300
            let strokeWidth = 1;
            if (isAnchor) {
              strokeColor = 'rgb(234, 179, 8)'; // yellow-600
              strokeWidth = 3;
            } else if (isHighlighted) {
              strokeColor = 'rgb(59, 130, 246)'; // blue-500
              strokeWidth = 2;
            } else if (isMistake) {
              strokeColor = 'rgb(239, 68, 68)'; // red-500
              strokeWidth = 2;
            }

            return (
              <g key={`${r}-${c}`}>
                {/* Cell background */}
                <motion.rect
                  x={x}
                  y={y}
                  width={cellSize}
                  height={cellSize}
                  fill={fillColor}
                  stroke={strokeColor}
                  strokeWidth={strokeWidth}
                  rx={4}
                  onClick={() => handleCellClick(r, c)}
                  className="cell-rect cursor-pointer transition-colors"
                  role="gridcell"
                  aria-label={`Cell ${r},${c}${hasValue ? ` value ${cell.value}` : ' empty'}${isAnchor ? ' anchor' : ''}${isHighlighted ? ' legal target' : ''}`}
                  tabIndex={0}
                  onKeyDown={(e) => handleKeyDown(e, r, c)}
                  onFocus={() => setFocusedCell({ row: r, col: c })}
                  onBlur={() => setFocusedCell(null)}
                  initial={{ scale: 0.95, opacity: 0 }}
                  animate={{ scale: 1, opacity: 1 }}
                  transition={{ duration: 0.15, delay: (r + c) * 0.02 }}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                />

                {/* Focus ring (visible only when focused via keyboard) */}
                {isFocused && (
                  <rect
                    x={x + 2}
                    y={y + 2}
                    width={cellSize - 4}
                    height={cellSize - 4}
                    fill="none"
                    stroke="rgb(99, 102, 241)"
                    strokeWidth={2}
                    strokeDasharray="4 2"
                    rx={3}
                    pointerEvents="none"
                    opacity={0.8}
                  />
                )}

                {/* Cell value */}
                {hasValue && (
                  <motion.text
                    x={x + cellSize / 2}
                    y={y + cellSize / 2}
                    textAnchor="middle"
                    dominantBaseline="central"
                    fontSize={isGiven ? 24 : 22}
                    fontWeight={isGiven ? 'bold' : 'normal'}
                    fill={isGiven ? 'rgb(0, 0, 0)' : 'rgb(59, 130, 246)'}
                    pointerEvents="none"
                    initial={{ scale: 0 }}
                    animate={{ scale: 1 }}
                    transition={{ duration: 0.15, type: 'spring' }}
                  >
                    {cell.value}
                  </motion.text>
                )}

                {/* Highlight pulse for anchor */}
                {isAnchor && (
                  <motion.rect
                    x={x}
                    y={y}
                    width={cellSize}
                    height={cellSize}
                    fill="none"
                    stroke="rgb(234, 179, 8)"
                    strokeWidth={2}
                    rx={4}
                    pointerEvents="none"
                    initial={{ opacity: 0.5, scale: 1 }}
                    animate={{
                      opacity: [0.5, 1, 0.5],
                      scale: [1, 1.05, 1],
                    }}
                    transition={{
                      duration: 1.5,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />
                )}
              </g>
            );
          })
        )}
      </svg>

      {/* Next target indicator */}
      {state.nextTarget !== null && (
        <div className="mt-4 text-center">
          <div className="inline-flex items-center gap-2 px-4 py-2 bg-blue-100 rounded-lg border-2 border-blue-500">
            <span className="text-sm font-medium text-gray-700">Next number:</span>
            <span className="text-2xl font-bold text-blue-600">{state.nextTarget}</span>
          </div>
        </div>
      )}

      {/* Undo/Redo buttons */}
      <div className="mt-4 flex justify-center gap-2">
        <button
          onClick={() => toggleGuide(!state.guideEnabled)}
          className={`px-4 py-2 rounded-md font-medium transition-colors ${
            state.guideEnabled
              ? 'bg-blue-500 text-white hover:bg-blue-600'
              : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
          }`}
          aria-label={state.guideEnabled ? 'Hide guide highlights' : 'Show guide highlights'}
        >
          {state.guideEnabled ? '👁️ Guide On' : '👁️‍🗨️ Guide Off'}
        </button>
        <button
          onClick={undo}
          disabled={!canUndo}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 rounded-md font-medium transition-colors"
          aria-label="Undo last move"
        >
          Undo (Ctrl+Z)
        </button>
        <button
          onClick={redo}
          disabled={!canRedo}
          className="px-4 py-2 bg-gray-200 hover:bg-gray-300 disabled:bg-gray-100 disabled:text-gray-400 rounded-md font-medium transition-colors"
          aria-label="Redo last move"
        >
          Redo (Ctrl+Y)
        </button>
      </div>

      {/* Mistake indicator */}
      {visibleMistakes.length > 0 && (
        <motion.div
          className="mt-4 p-3 bg-red-100 border-2 border-red-500 rounded-lg text-center"
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -10 }}
        >
          <p className="text-sm font-medium text-red-700">
            {visibleMistakes[0].reason === 'no-target'
              ? 'No anchor selected! Click a number first.'
              : visibleMistakes[0].reason === 'occupied'
              ? 'Cell already has a value!'
              : visibleMistakes[0].reason === 'not-adjacent'
              ? 'Must place next to the anchor!'
              : 'Invalid move!'}
          </p>
        </motion.div>
      )}

      {/* Instructions */}
      {state.anchorValue === null && (
        <div className="mt-4 p-3 bg-gray-100 rounded-lg text-center">
          <p className="text-sm text-gray-600">
            Click a number to start building the sequence
          </p>
        </div>
      )}
    </div>
  );
});

export default GuidedGrid;
