import { useGameStore, getPuzzleIdentity } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo, useEffect, useState, useRef } from 'react';
import type { ReactNode } from 'react';
import { useGuidedSequenceFlow } from '@/sequence';
import type { Position, MistakeEvent, SequenceDirection } from '@/sequence/types';
import {
  cssVar,
  gridPalette,
  statusPalette,
  paletteB,
} from '@/styles/colorTokens';
import { deriveSymbolRange } from '@/symbolSets/valueRange';
import { getDefaultSymbolSet } from '@/symbolSets/registry';
import { getPaletteBColorContext } from '@/symbolSets/paletteBShapeSymbolSet';

const HOLD_DURATION_MS = 650;
const BOARD_PADDING = 8;
const GRID_SAFE_MARGIN = 32;
const HOLD_RING_MARGIN = 2;
const HOLD_RING_STROKE_WIDTH = 4;
const NEXT_PREVIEW_SIZE = 36;

const DIRECTION_OPTIONS: Array<{
  value: SequenceDirection;
  label: string;
  aria: string;
  icon: 'plus' | 'minus';
}> = [
  { value: 'forward', label: 'Forward', aria: 'Step forward to k plus 1', icon: 'plus' },
  { value: 'backward', label: 'Backward', aria: 'Step backward to k minus 1', icon: 'minus' },
];

const PlusMinusGlyph = ({ variant }: { variant: 'plus' | 'minus' }) => (
  <span className="relative flex h-6 w-6 items-center justify-center" aria-hidden="true">
    <span className="absolute left-1/2 top-1/2 h-0.5 w-4 -translate-x-1/2 -translate-y-1/2 rounded-full bg-current" />
    {variant === 'plus' && (
      <span className="absolute left-1/2 top-1/2 h-4 w-0.5 -translate-x-1/2 -translate-y-1/2 rounded-full bg-current" />
    )}
  </span>
);

/**
 * Grid component integrated with guided sequence flow
 */
const activeSymbolSet = getDefaultSymbolSet();
const paletteBSymbolSetIds = new Set([
  'paletteB-shapes',
  'paletteB-dice',
  'paletteB-dice-growing',
]);

const GuidedGrid = memo(function GuidedGrid() {
  const puzzle = useGameStore((state) => state.puzzle);
  const puzzleInstance = useGameStore((state) => state.puzzleInstance);
  const updateSequenceState = useGameStore((state) => state.updateSequenceState);
  const incrementMoveCount = useGameStore((state) => state.incrementMoveCount);
  const rawSequenceBoard = useGameStore((state) => state.sequenceBoard);
  const sequenceBoardKey = useGameStore((state) => state.sequenceBoardKey);
  const boardClearSignal = useGameStore((state) => state.boardClearSignal);
  const requestBoardClear = useGameStore((state) => state.clearBoardEntries);
  const puzzleIdentity = useMemo(() => getPuzzleIdentity(puzzle), [puzzle]);
  const restoredSequenceBoard = useMemo(() => {
    if (!rawSequenceBoard || !puzzleIdentity) return null;
    if (sequenceBoardKey !== puzzleIdentity) return null;
    return rawSequenceBoard;
  }, [rawSequenceBoard, sequenceBoardKey, puzzleIdentity]);

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
  }, [puzzle]);

  // Initialize guided sequence flow
  const {
    state,
    board,
    selectAnchor,
    placeNext,
    removeCell,
    toggleGuide,
    setStepDirection,
    undo,
    redo,
    canUndo,
    canRedo,
    clearBoard,
    recentMistakes,
  } = useGuidedSequenceFlow(
    puzzle?.size || 5,
    puzzle?.size || 5,
    givensMap,
    maxValue,
    puzzleInstance,
    { onPlacement: incrementMoveCount },
    restoredSequenceBoard  // Pass restored board for persistence
  );
  const globalSequenceState = useGameStore((store) => store.sequenceState);
  const isComplete = useGameStore((store) => store.isComplete);
  const reopenCompletionSummary = useGameStore(
    (store) => store.reopenCompletionSummary
  );
  const interactionsLocked = isComplete;

  const boardSize = board.length || puzzle?.size || 0;
  const columnCount = board[0]?.length ?? boardSize;
  const totalCells = boardSize * columnCount;
  const { startValue, endValue } = useMemo(
    () => deriveSymbolRange(puzzle, boardSize),
    [puzzle, boardSize]
  );

  // Sync sequence state with game store
  useEffect(() => {
    updateSequenceState(state, board, recentMistakes);
  }, [state, board, recentMistakes, updateSequenceState]);

  // Track focused cell for keyboard navigation
  const [focusedCell, setFocusedCell] = useState<Position | null>(null);

  // Determine whether there is anything to clear for button state
  const hasPlayerEntries = useMemo(() => {
    return board.some((row) =>
      row.some((cell) => !cell.given && cell.value !== null)
    );
  }, [board]);
  const lastClearSignalRef = useRef(boardClearSignal);

  // Respond to global clear requests (e.g., "Reset Puzzle" button on incorrect modal)
  useEffect(() => {
    if (boardClearSignal === 0) {
      lastClearSignalRef.current = 0;
      return;
    }
    if (boardClearSignal !== lastClearSignalRef.current) {
      lastClearSignalRef.current = boardClearSignal;
      clearBoard();
    }
  }, [boardClearSignal, clearBoard]);

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

  const [viewportWidth, setViewportWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth : 1024
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handleResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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
    if (interactionsLocked) return;
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
  }, [board]);

  const handleCellClick = (row: number, col: number) => {
    if (interactionsLocked) return;
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
    if (interactionsLocked) {
      if (
        e.key === 'Enter' ||
        e.key === ' ' ||
        e.key === 'Backspace' ||
        e.key === 'Delete' ||
        (e.key === 'z' && (e.ctrlKey || e.metaKey)) ||
        (e.key === 'y' && (e.ctrlKey || e.metaKey))
      ) {
        e.preventDefault();
      }
      return;
    }
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
  const baseRenderSize = totalSize;
  const availableWidth =
    viewportWidth > GRID_SAFE_MARGIN
      ? viewportWidth - GRID_SAFE_MARGIN
      : viewportWidth;
  const renderSize =
    availableWidth && availableWidth > 0
      ? Math.min(baseRenderSize, availableWidth)
      : baseRenderSize;

  const isPaletteBSet = paletteBSymbolSetIds.has(activeSymbolSet.id);
  const hideNumericNextLabel = isPaletteBSet;
  const showPaletteSwatch = isPaletteBSet;
  const shouldShowPreview =
    typeof activeSymbolSet.renderPreview === 'function' &&
    activeSymbolSet.id !== 'numeric';
  let nextIndicatorText: string;
  let nextIndicatorContent: React.ReactNode;
  if (isComplete) {
    nextIndicatorText = 'Puzzle complete!';
    nextIndicatorContent = nextIndicatorText;
  } else {
    const nextTargetValue =
      state.nextTarget ?? globalSequenceState?.nextTarget ?? null;
    if (nextTargetValue !== null) {
      nextIndicatorText = `Next: ${nextTargetValue}`;
      const previewNode =
        shouldShowPreview && typeof activeSymbolSet.renderPreview === 'function'
          ? activeSymbolSet.renderPreview({
              value: nextTargetValue,
              totalCells,
              cellSize: NEXT_PREVIEW_SIZE,
            })
          : null;
      const visibleLabel = hideNumericNextLabel ? 'Next:' : nextIndicatorText;
      nextIndicatorContent = (
        <span className="flex items-center gap-3">
          <span>{visibleLabel}</span>
          {previewNode && (
            <span
              className="inline-flex shrink-0 items-center justify-center"
              aria-hidden="true"
              style={{
                width: NEXT_PREVIEW_SIZE,
                height: NEXT_PREVIEW_SIZE,
              }}
            >
              {previewNode}
            </span>
          )}
        </span>
      );
    } else {
      nextIndicatorText = 'Select a clue to continue';
      nextIndicatorContent = nextIndicatorText;
    }
  }

  const pillClassName = `inline-flex h-12 items-center rounded-full border px-4 sm:px-6 text-base font-semibold transition-all ${
    pillPulseId
      ? 'shadow-[0_0_12px_2px_rgba(220,38,38,0.2)] text-white'
      : 'border-primary bg-primary/10 text-primary shadow-sm'
  }`;
  const pillStyle = pillPulseId
    ? {
        animation: 'pillPulse 0.6s ease-in-out forwards',
        borderColor: statusPalette.danger,
        backgroundColor: statusPalette.danger,
      }
    : undefined;

  const handleCompletionPillClick = () => {
    if (!isComplete) return;
    reopenCompletionSummary();
  };

  return (
    <div className="flex flex-col items-center">
      <style>{`
        @keyframes pillPulse {
          0% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0.05); }
          50% { box-shadow: 0 0 12px 2px rgba(220, 38, 38, 0.4); }
          100% { box-shadow: 0 0 0 0 rgba(220, 38, 38, 0); }
        }
      `}</style>
      <style>{`
        .cell-rect:focus {
          outline: none;
        }
      `}</style>
      <div className="mb-2 flex flex-wrap items-center justify-center gap-2">
        {isComplete ? (
          <button
            type="button"
            onClick={handleCompletionPillClick}
            aria-label="View puzzle completion details"
            className={`${pillClassName} focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary`}
            style={pillStyle}
          >
            {nextIndicatorContent}
          </button>
        ) : (
          <div
            className={pillClassName}
            style={pillStyle}
            aria-label={nextIndicatorText}
          >
            {nextIndicatorContent}
          </div>
        )}
        <div
          className="inline-flex h-12 overflow-hidden rounded-full border border-border bg-surface shadow-sm"
          role="group"
          aria-label="Choose sequence direction"
        >
          {DIRECTION_OPTIONS.map((option) => {
            const isActive = state.stepDirection === option.value;
            const buttonStyle = isActive
              ? {
                  backgroundColor: statusPalette.primary,
                  borderColor: statusPalette.primary,
                  color: statusPalette.primaryForeground,
                }
              : undefined;
            const computedButtonStyle = {
              WebkitTapHighlightColor: 'transparent',
              ...buttonStyle,
            };
            return (
              <button
                key={option.value}
                type="button"
                onClick={() => setStepDirection(option.value)}
                aria-pressed={isActive}
                aria-label={option.aria}
                style={computedButtonStyle}
                className={`flex h-full min-w-[44px] items-center justify-center gap-2 px-2.5 text-sm font-semibold leading-none transition-colors focus:outline-none focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 sm:min-w-0 sm:px-4 sm:leading-tight ${
                  isActive
                    ? 'focus-visible:outline-primary text-primary-foreground'
                    : 'bg-surface text-copy-muted hover:bg-surface-muted focus-visible:outline-border'
                }`}
              >
                <span className="flex h-12 w-12 items-center justify-center sm:h-auto sm:w-auto">
                  <PlusMinusGlyph variant={option.icon} />
                </span>
                <span className="hidden sm:inline">{option.label}</span>
              </button>
            );
          })}
        </div>
      </div>
      <div
        className="relative"
        style={{
          width: renderSize,
          height: renderSize,
        }}
      >
        <svg
          width="100%"
          height="100%"
          viewBox={`${-BOARD_PADDING} ${-BOARD_PADDING} ${totalSize + BOARD_PADDING * 2} ${totalSize + BOARD_PADDING * 2}`}
          className="mx-auto"
          role="grid"
          aria-label="Hidato puzzle grid"
          preserveAspectRatio="xMidYMid meet"
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
            const holdRadius = cellSize / 2 - HOLD_RING_MARGIN;
            const holdCircumference = 2 * Math.PI * holdRadius;
            const isChainStart = cell.value === startValue;
            const isChainEnd = cell.value === endValue;
            const chainRole = isChainStart ? 'start' : isChainEnd ? 'end' : null;
            let badgePath: string | null = null;
            if (chainRole === 'start') {
              const badgeInset = 2;
              const badgeSize = cellSize * 0.34;
              const startX = x + badgeInset;
              const startY = y + badgeInset;
              const cornerRadius = 3;
              badgePath = `M ${startX} ${startY + cornerRadius} Q ${startX} ${startY} ${
                startX + cornerRadius
              } ${startY} L ${startX + badgeSize} ${startY} L ${startX} ${
                startY + badgeSize
              } Z`;
            } else if (chainRole === 'end') {
              const badgeInset = 2;
              const badgeSize = cellSize * 0.34;
              const startX = x + cellSize - badgeInset;
              const startY = y + badgeInset;
              const cornerRadius = 3;
              badgePath = `M ${startX} ${startY + cornerRadius} Q ${startX} ${startY} ${
                startX - cornerRadius
              } ${startY} L ${startX - badgeSize} ${startY} L ${startX} ${
                startY + badgeSize
              } Z`;
            }
            const linearIndex =
              cell.value !== null ? cell.value - 1 : undefined;
            const paletteContext =
              isPaletteBSet && cell.value !== null
                ? getPaletteBColorContext(
                    cell.value,
                    totalCells || boardSize * boardSize,
                    typeof linearIndex === 'number' ? linearIndex : undefined
                  )
                : null;
            const symbolProps = {
              value: cell.value,
              isGiven,
              isSelected: isAnchor,
              isError: isMistake,
              isEmpty: !hasValue,
              isGuideTarget: isHighlighted,
              cellSize,
              isChainStart,
              isChainEnd,
              linearIndex,
              totalCells,
            };
            const symbolElement = activeSymbolSet.renderCell(symbolProps);
            const badgeFillColor =
              chainRole && paletteContext
                ? paletteContext.circleColor
                : chainRole === 'start'
                ? statusPalette.primary
                : chainRole === 'end'
                ? statusPalette.success
                : null;

            // Determine fill color based on cell state
            const anchorFillColor = paletteContext
              ? paletteContext.circleColor
              : gridPalette.anchorFill;
            let fillColor = gridPalette.cellSurface;
            if (isAnchor) fillColor = anchorFillColor;
            else if (isMistake) fillColor = gridPalette.mistakeFill;
            else if (isGiven) fillColor = gridPalette.given;

            // Determine stroke color
            const anchorStrokeColor = paletteContext
              ? paletteContext.circleColor
              : gridPalette.anchorStroke;
            let strokeColor = statusPalette.border;
            let strokeWidth = 1;
            if (isAnchor) {
              strokeColor = statusPalette.border;
              strokeWidth = 1;
            } else if (isMistake) {
              strokeColor = gridPalette.mistakeStroke;
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
                    stroke={statusPalette.primary}
                    strokeWidth={2}
                    strokeDasharray="4 2"
                    rx={3}
                    pointerEvents="none"
                    opacity={0.8}
                  />
                )}

                {/* Cell value */}
                {symbolElement && (
                  <g transform={`translate(${x} ${y})`}>{symbolElement}</g>
                )}

                {/* Given underline */}
                {isGiven && (
                  <rect
                    x={x + 6}
                    y={y + cellSize - 4}
                    width={cellSize - 12}
                    height={2}
                    fill={statusPalette.text}
                    rx={1}
                    pointerEvents="none"
                    opacity={0.85}
                  />
                )}

                {/* Chain baseline overlay */}
                {badgePath && badgeFillColor && (
                  <path
                    d={badgePath}
                    fill={badgeFillColor}
                    fillOpacity={1}
                    stroke="none"
                    pointerEvents="none"
                  />
                )}

                {/* Guide highlight overlay */}
                {isHighlighted && !hasValue && state.guideEnabled && (
                  <motion.rect
                    x={x + 3}
                    y={y + 3}
                    width={cellSize - 6}
                    height={cellSize - 6}
                    rx={3}
                    fill={cssVar('--color-grid-target', 0.35)}
                    stroke={statusPalette.primary}
                    strokeWidth={1.5}
                    pointerEvents="none"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{
                      opacity: [0.5, 0.9, 0.5],
                      scale: [0.98, 1, 0.98],
                    }}
                    transition={{
                      duration: 1.2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
                  />
                )}

                {/* Highlight pulse for anchor */}
                {isAnchor && (
                  <rect
                    x={x + 1.5}
                    y={y + 1.5}
                    width={cellSize - 3}
                    height={cellSize - 3}
                    fill="none"
                    stroke={anchorStrokeColor}
                    strokeWidth={isPaletteBSet ? 5 : 2}
                    rx={5}
                    pointerEvents="none"
                    opacity={1}
                  />
                )}

                {/* Long-press progress */}
                {isHoldTarget && (
                  <motion.circle
                    cx={x + cellSize / 2}
                    cy={y + cellSize / 2}
                    r={holdRadius}
                    fill="none"
                    stroke={cssVar('--color-grid-hold-stroke', 0.9)}
                    strokeWidth={HOLD_RING_STROKE_WIDTH}
                    strokeDasharray={holdCircumference}
                    strokeDashoffset={holdCircumference * (1 - holdProgress)}
                    strokeLinecap="round"
                    pointerEvents="none"
                    style={{
                      filter: `drop-shadow(0 0 6px ${cssVar('--color-grid-hold-stroke', 0.35)})`,
                    }}
                    animate={{
                      opacity: [0.75, 1, 0.9],
                      scale: [0.99, 1, 0.99],
                    }}
                    transition={{
                      duration: 1.2,
                      repeat: Infinity,
                      ease: 'easeInOut',
                    }}
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
                    fill={cssVar('--color-grid-mistake-fill', 0.55)}
                    stroke={cssVar('--color-grid-mistake-stroke')}
                    strokeWidth={2}
                    pointerEvents="none"
                    initial={{ opacity: 0, scale: 0.95 }}
                    animate={{ opacity: [0, 1, 0], scale: [0.95, 1.05, 1] }}
                    transition={{ duration: 0.6, ease: 'easeInOut' }}
                  />
                )}
              </g>
            );
          })
        )}
      </svg>
      </div>

      {/* Undo/Redo buttons */}
      <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
        <button
          onClick={() => toggleGuide(!state.guideEnabled)}
          disabled={interactionsLocked}
          className={`px-4 py-2 rounded-md font-medium transition-colors border disabled:cursor-not-allowed disabled:opacity-60 ${
            state.guideEnabled
              ? 'border-primary bg-primary text-primary-foreground hover:bg-primary-strong'
              : 'border-border bg-surface-muted text-copy hover:bg-surface'
          }`}
          aria-label={state.guideEnabled ? 'Hide guide highlights' : 'Show guide highlights'}
        >
          {state.guideEnabled ? 'Guide On' : 'Guide Off'}
        </button>
        <button
          onClick={undo}
          disabled={interactionsLocked || !canUndo}
          className="px-4 py-2 border border-border bg-surface-muted text-copy hover:bg-surface disabled:bg-disabled disabled:text-disabled-text disabled:border-disabled-border disabled:opacity-60 rounded-md font-medium transition-colors"
          aria-label="Undo last move"
        >
          Undo
        </button>
        <button
          onClick={redo}
          disabled={interactionsLocked || !canRedo}
          className="px-4 py-2 border border-border bg-surface-muted text-copy hover:bg-surface disabled:bg-disabled disabled:text-disabled-text disabled:border-disabled-border disabled:opacity-60 rounded-md font-medium transition-colors"
          aria-label="Redo last move"
        >
          Redo
        </button>
        <button
          type="button"
          onClick={requestBoardClear}
          disabled={interactionsLocked || !hasPlayerEntries}
          className="px-4 py-2 border border-border bg-surface-muted text-copy hover:bg-surface disabled:bg-disabled disabled:text-disabled-text disabled:border-disabled-border disabled:opacity-60 rounded-md font-medium transition-colors text-sm"
          aria-label="Clear all filled cells and start over"
        >
          Clear
        </button>
      </div>

      {/* Instructions - only show if puzzle is not complete */}
      {state.anchorValue === null && !isComplete && (
        <div className="mt-4 p-3 bg-surface-muted border border-border rounded-lg text-center">
          <p className="text-sm text-copy-muted">
            Click a number to start building the sequence
          </p>
        </div>
      )}
      {showPaletteSwatch && (
        <div className="mt-6 flex flex-col items-center text-xs text-copy-muted">
          <span className="font-semibold uppercase tracking-wide text-copy">
            Color progression
          </span>
          <div className="mt-1 flex gap-1" role="img" aria-label="Symbol color progression">
            {paletteB.map((color, idx) => (
              <span
                key={`${color}-${idx}`}
                className="h-3 w-8 rounded-full"
                style={{ backgroundColor: color }}
                aria-label={`Color ${idx + 1}`}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
});

export default GuidedGrid;

