import { useGameStore } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo, useEffect, useState, useRef } from 'react';
import { useGuidedSequenceFlow } from '@/sequence';
import type { Position, MistakeEvent } from '@/sequence/types';

const HOLD_DURATION_MS = 650;
const BOARD_PADDING = 8;

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
  const globalSequenceState = useGameStore((store) => store.sequenceState);
  const completionStatus = useGameStore((store) => store.completionStatus);
  const isComplete = useGameStore((store) => store.isComplete);

  // Sync sequence state with game store
  useEffect(() => {
    updateSequenceState(state, board, recentMistakes);
  }, [state, board, recentMistakes, updateSequenceState]);

  // Track focused cell for keyboard navigation
  const [focusedCell, setFocusedCell] = useState<Position | null>(null);

  // Auto-dismiss the latest mistake after 3 seconds
  const [visibleMistake, setVisibleMistake] = useState<MistakeEvent | null>(null);
  const [pillPulseId, setPillPulseId] = useState<number | null>(null);

  useEffect(() => {
    if (recentMistakes.length === 0) {
      return;
    }

    const latest = recentMistakes[recentMistakes.length - 1];
    setVisibleMistake(latest);

    const timer = setTimeout(() => {
      setVisibleMistake((current) =>
        current?.timestamp === latest.timestamp ? null : current
      );
    }, 3000);

    return () => clearTimeout(timer);
  }, [recentMistakes]);

  useEffect(() => {
    if (!visibleMistake) return;
    setPillPulseId(visibleMistake.timestamp);
    const timer = setTimeout(() => setPillPulseId(null), 450);
    return () => clearTimeout(timer);
  }, [visibleMistake]);

  const [holdIndicator, setHoldIndicator] = useState<{
    pos: Position;
    progress: number;
  } | null>(null);
  const holdTimeoutRef = useRef<number | null>(null);
  const holdRafRef = useRef<number | null>(null);
  const holdStartRef = useRef<number>(0);
  const skipNextClickRef = useRef(false);

  useEffect(() => {
    return () => {
      if (holdTimeoutRef.current) {
        clearTimeout(holdTimeoutRef.current);
        holdTimeoutRef.current = null;
      }
      if (holdRafRef.current) {
        cancelAnimationFrame(holdRafRef.current);
        holdRafRef.current = null;
      }
    };
  }, []);

  const clearHoldState = () => {
    if (holdTimeoutRef.current !== null) {
      clearTimeout(holdTimeoutRef.current);
      holdTimeoutRef.current = null;
    }
    if (holdRafRef.current !== null) {
      cancelAnimationFrame(holdRafRef.current);
      holdRafRef.current = null;
    }
    setHoldIndicator(null);
  };

  const executeHoldRemoval = (pos: Position) => {
    clearHoldState();
    skipNextClickRef.current = true;
    removeCell(pos);
  };

  const startHold = (pos: Position) => {
    clearHoldState();
    holdStartRef.current = performance.now();
    setHoldIndicator({ pos, progress: 0 });

    const updateProgress = () => {
      const elapsed = performance.now() - holdStartRef.current;
      const progress = Math.min(elapsed / HOLD_DURATION_MS, 1);
      setHoldIndicator((current) =>
        current && current.pos.row === pos.row && current.pos.col === pos.col
          ? { ...current, progress }
          : current
      );
      if (progress < 1 && holdTimeoutRef.current !== null) {
        holdRafRef.current = requestAnimationFrame(updateProgress);
      }
    };

    holdRafRef.current = requestAnimationFrame(updateProgress);
    holdTimeoutRef.current = window.setTimeout(
      () => executeHoldRemoval(pos),
      HOLD_DURATION_MS
    );
  };

  const cancelHold = () => {
    clearHoldState();
  };

  const handlePointerDown = (
    e: React.PointerEvent<SVGRectElement>,
    cell: (typeof board)[number][number]
  ) => {
    if (cell.value !== null && !cell.given) {
      e.preventDefault();
      startHold(cell.position);
    }
  };

  const handlePointerEnd = () => {
    if (holdTimeoutRef.current !== null) {
      cancelHold();
    }
  };

  // Memoize grid dimensions to prevent recalculation
  const dimensions = useMemo(() => {
    if (!board) return null;
    const cellSize = 60;
    const gap = 2;
    const totalSize = board.length * cellSize + (board.length - 1) * gap;
    return { cellSize, gap, totalSize };
  }, [board?.length]);

  const handleCellClick = (row: number, col: number) => {
    if (skipNextClickRef.current) {
      skipNextClickRef.current = false;
      return;
    }

    const pos: Position = { row, col };
    const cell = board[row][col];

    // If cell has a value
    if (cell.value !== null) {
      selectAnchor(pos);
    }
    // If cell is empty, attempt placement (validate within hook)
    else {
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

  let nextIndicatorLabel: string;
  if (isComplete) {
    nextIndicatorLabel = 'Puzzle complete!';
  } else {
    const nextTargetValue =
      state.nextTarget ?? globalSequenceState?.nextTarget ?? null;
    nextIndicatorLabel =
      nextTargetValue !== null
        ? `Next number: ${nextTargetValue}`
        : 'Select a clue to continue';
  }

  return (
    <div className="flex flex-col items-center">
      <style>{`
        .cell-rect:focus {
          outline: none;
        }
      `}</style>
      <div
        className={`mb-2 inline-flex min-h-[28px] items-center rounded-full border px-4 py-1 text-sm font-semibold shadow transition-colors ${
          pillPulseId
            ? 'border-red-200 bg-red-50 text-red-600'
            : 'border-blue-200 bg-blue-50 text-blue-700'
        }`}
      >
        {nextIndicatorLabel}
      </div>
      <div className="relative">
        <svg
          width={totalSize}
          height={totalSize}
          viewBox={`${-BOARD_PADDING} ${-BOARD_PADDING} ${totalSize + BOARD_PADDING * 2} ${totalSize + BOARD_PADDING * 2}`}
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
            const isMistakeTarget =
              visibleMistake &&
              visibleMistake.position.row === r &&
              visibleMistake.position.col === c;
            const isHoldTarget =
              holdIndicator &&
              holdIndicator.pos.row === r &&
              holdIndicator.pos.col === c;
            const holdProgress = isHoldTarget ? holdIndicator.progress : 0;
            const holdRadius = cellSize / 2 - 6;
            const holdCircumference = 2 * Math.PI * holdRadius;

            // Determine fill color based on cell state
            let fillColor = 'white';
            if (isAnchor) fillColor = 'rgb(254, 240, 138)'; // yellow-200
            else if (isHighlighted) fillColor = 'rgb(191, 219, 254)'; // blue-200
            else if (isMistake) fillColor = 'rgb(254, 202, 202)'; // red-200
            else if (isGiven) fillColor = 'rgb(229, 231, 235)'; // gray-200

            // Determine stroke color
            let strokeColor = 'rgb(203, 213, 225)'; // slate-300
            let strokeWidth = 1;
            const showAnchorWarning = isAnchor && !!visibleMistake;

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
                  onPointerDown={(e) => handlePointerDown(e, cell)}
                  onPointerUp={handlePointerEnd}
                  onPointerLeave={handlePointerEnd}
                  onPointerCancel={handlePointerEnd}
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

                {/* Long-press progress */}
                {isHoldTarget && (
                  <circle
                    cx={x + cellSize / 2}
                    cy={y + cellSize / 2}
                    r={holdRadius}
                    fill="none"
                    stroke="rgba(239,68,68,0.85)"
                    strokeWidth={3}
                    strokeDasharray={holdCircumference}
                    strokeDashoffset={holdCircumference * (1 - holdProgress)}
                    strokeLinecap="round"
                    pointerEvents="none"
                  />
                )}

                {/* Subtle invalid indicator */}
                {isMistakeTarget && (
                  <motion.rect
                    key={visibleMistake?.timestamp ?? 'mistake'}
                    x={x + 2}
                    y={y + 2}
                    width={cellSize - 4}
                    height={cellSize - 4}
                    rx={4}
                    fill="rgba(239,68,68,0.12)"
                    stroke="rgba(239,68,68,0.35)"
                    strokeWidth={2}
                    pointerEvents="none"
                    initial={{ opacity: 0 }}
                    animate={{ opacity: [0, 1, 0] }}
                    transition={{ duration: 0.45, ease: 'easeOut' }}
                  />
                )}
              </g>
            );
          })
        )}
      </svg>
      </div>

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
          {state.guideEnabled ? 'Guide On' : 'Guide Off'}
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

