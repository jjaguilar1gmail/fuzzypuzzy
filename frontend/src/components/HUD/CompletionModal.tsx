import { useEffect, useCallback, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@/state/gameStore';
import { formatDuration, formatMoveStat } from '@/components/HUD/SessionStats';
import { Puzzle } from '@/domain/puzzle';
import type { CellMistakeHistory } from '@/state/cellMistakeHistory';
import { positionKey } from '@/domain/position';
import type { DailySizeId } from '@/lib/daily';
import { cssVar } from '@/styles/colorTokens';

interface CompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
  onPlayAgain?: () => void; // Optional callback for Play Again action
  dailySize?: DailySizeId;
  dateLabel?: string | null;
}

export default function CompletionModal({
  isOpen,
  onClose,
  onPlayAgain,
  dailySize,
  dateLabel,
}: CompletionModalProps) {
  const [shareFeedback, setShareFeedback] = useState<string | null>(null);
  const puzzle = useGameStore((state) => state.puzzle);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const moveCount = useGameStore((state) => state.moveCount);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const cellMistakeHistory = useGameStore((state) => state.cellMistakeHistory);
  const isCorrect = completionStatus !== 'incorrect';
  const moveStat = formatMoveStat(moveCount, puzzle);

  const sizeLabel =
    dailySize !== undefined
      ? dailySize.charAt(0).toUpperCase() + dailySize.slice(1)
      : null;

  const shareEnabled = isCorrect && puzzle;

  const handleShare = useCallback(async () => {
    if (!puzzle) return;
    const payload = buildShareText({
      puzzle,
      history: cellMistakeHistory,
      moveStat,
      elapsedMs,
      dateLabel,
      sizeLabel,
    });

    try {
      if (typeof navigator !== 'undefined' && navigator.share) {
        await navigator.share({
          title: 'Number Flow',
          text: payload,
        });
        setShareFeedback('Shared!');
        return;
      }

      await copyShareToClipboard(payload);
      setShareFeedback('Copied to clipboard');
    } catch (err) {
      console.error('Failed to share result', err);
    }
  }, [puzzle, cellMistakeHistory, moveStat, elapsedMs, dateLabel, sizeLabel]);

  useEffect(() => {
    if (!shareFeedback) return;
    const id = window.setTimeout(() => setShareFeedback(null), 2500);
    return () => window.clearTimeout(id);
  }, [shareFeedback]);

  const statsList = (
    <div className="space-y-2">
      {sizeLabel && (
        <div className="flex justify-between items-center gap-6">
          <span className="text-copy-muted">Size:</span>
          <span className="font-semibold">{sizeLabel}</span>
        </div>
      )}
      {dateLabel && (
        <div className="flex justify-between items-center gap-6">
          <span className="text-copy-muted">Date:</span>
          <span className="font-semibold">{dateLabel}</span>
        </div>
      )}
      <div className="flex justify-between items-center gap-6">
        <span className="text-copy-muted">Time:</span>
        <span className="font-semibold">{formatDuration(elapsedMs)}</span>
      </div>

      <div className="flex justify-between items-center gap-6">
        <span className="text-copy-muted">Moves:</span>
        <span className="font-semibold">{moveStat}</span>
      </div>
    </div>
  );

  const handlePrimaryAction = useCallback(() => {
    if (isCorrect) {
      // Use custom callback if provided, otherwise use default resetPuzzle
      if (onPlayAgain) {
        onPlayAgain();
      } else {
        useGameStore.getState().resetPuzzle();
      }
    }
    onClose();
  }, [isCorrect, onClose, onPlayAgain]);

  const handleSecondaryAction = useCallback(() => {
    if (!isCorrect) {
      useGameStore.getState().clearBoardEntries();
    }
    onClose();
  }, [isCorrect, onClose]);

  useEffect(() => {
    if (isOpen) {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.15, type: 'spring' }}
          >
            <div
              className="bg-surface rounded-lg shadow-xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-labelledby="completion-title"
              aria-modal="true"
            >
              <div className="mb-4 flex flex-col items-center gap-3">
                <h2
                  id="completion-title"
                  className={`text-3xl font-bold text-center ${
                    isCorrect ? 'text-success' : 'text-danger'
                  }`}
                >
                  {isCorrect ? 'Puzzle Complete!' : 'Incorrect Solution'}
                </h2>
                {shareEnabled && (
                  <div className="flex flex-col items-center gap-1">
                    <button
                      type="button"
                      onClick={handleShare}
                      className="inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-4 py-1.5 text-sm font-semibold text-primary shadow-sm transition hover:bg-primary/20 dark:border-primary/50 dark:bg-primary/20 dark:text-primary-foreground"
                      aria-label="Share puzzle result"
                    >
                      <ShareIcon />
                      <span className="-mr-1 pr-1">Share</span>
                    </button>
                    {shareFeedback && (
                      <span className="text-xs font-medium text-primary">
                        {shareFeedback}
                      </span>
                    )}
                  </div>
                )}
              </div>

              {isCorrect && puzzle ? (
                <div className="mb-8 mt-4 flex flex-col items-center gap-4 sm:flex-row sm:items-start sm:justify-center">
                  <AccuracyMiniGrid puzzle={puzzle} history={cellMistakeHistory} />
                  {statsList}
                </div>
              ) : (
                <div className="mb-8">{statsList}</div>
              )}

              <div className="flex gap-3">
                <motion.button
                  onClick={handlePrimaryAction}
                  className="flex-1 px-6 py-3 bg-surface text-copy rounded-lg font-medium hover:bg-surface-muted transition-colors border border-border shadow-sm"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isCorrect ? 'Play Again' : 'Keep Editing'}
                </motion.button>

                <motion.button
                  onClick={handleSecondaryAction}
                  className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors border ${
                    isCorrect
                      ? 'border-primary bg-primary text-primary-foreground hover:bg-primary-strong'
                      : 'border-danger bg-surface text-danger hover:bg-surface-muted'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isCorrect ? 'Close' : 'Clear Puzzle'}
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

function AccuracyMiniGrid({
  puzzle,
  history,
}: {
  puzzle: Puzzle;
  history: CellMistakeHistory;
}) {
  const givens = useMemo(() => {
    const set = new Set<string>();
    puzzle.givens.forEach(({ row, col }) => {
      set.add(positionKey({ row, col }));
    });
    return set;
  }, [puzzle]);

  const size = puzzle.size;
  const cellSize = Math.max(8, Math.min(18, Math.floor(140 / size)));
  const gap = 3;

  const grid = (
    <div
      className="grid"
      style={{
        gridTemplateColumns: `repeat(${size}, ${cellSize}px)`,
        gap,
      }}
    >
      {Array.from({ length: size }).map((_, row) =>
        Array.from({ length: size }).map((_, col) => {
          const key = positionKey({ row, col });
          const isGiven = givens.has(key);
          const hadMistake = Boolean(history[key]);

          let label = 'Never had a wrong value';
          let backgroundColor = cssVar('--color-accuracy-clean');
          if (isGiven) {
            backgroundColor = cssVar('--color-grid-given');
            label = 'Given cell';
          } else if (hadMistake) {
            backgroundColor = cssVar('--color-accuracy-mistake');
            label = 'Had a wrong value at some point';
          }

          return (
            <span
              key={key}
              className="rounded"
              style={{
                width: cellSize,
                height: cellSize,
                backgroundColor,
              }}
              title={label}
              aria-label={label}
            />
          );
        })
      )}
    </div>
  );

  return (
    <div
      className="flex flex-col items-center gap-2 text-xs text-copy-muted"
      aria-label="Accuracy map showing how many cells were ever incorrect"
    >
      <div className="rounded-2xl bg-surface p-3 shadow-inner border border-border">
        {grid}
      </div>
      {/* Legend temporarily hidden */}
      {/* <div className="flex gap-3">
        <LegendItem colorClass="bg-success-muted" label="Clean" />
        <LegendItem colorClass="bg-danger-muted" label="Had mistake" />
        <LegendItem colorClass="bg-grid-given" label="Given" />
      </div> */}
    </div>
  );
}

function LegendItem({ colorClass, label }: { colorClass: string; label: string }) {
  return (
    <span className="inline-flex items-center gap-1">
      <span className={`h-3 w-3 rounded-sm ${colorClass}`} aria-hidden="true" />
      {label}
    </span>
  );
}

function ShareIcon() {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 18 18"
      aria-hidden="true"
      className="text-primary"
    >
      <circle cx="6" cy="9" r="2" fill="currentColor" />
      <circle cx="12.5" cy="4.5" r="2" fill="currentColor" />
      <circle cx="12.5" cy="13.5" r="2" fill="currentColor" />
      <path
        d="M7.7 7.8 10.9 5.7M7.7 10.2l3.2 2.1"
        stroke="currentColor"
        strokeWidth="1.6"
        strokeLinecap="round"
      />
    </svg>
  );
}

const SHARE_SYMBOLS = {
  clean: '🟩',
  mistake: '🟥',
  given: '⬜',
};

function buildShareText({
  puzzle,
  history,
  moveStat,
  elapsedMs,
  dateLabel,
  sizeLabel,
}: {
  puzzle: Puzzle;
  history: CellMistakeHistory;
  moveStat: string;
  elapsedMs: number;
  dateLabel?: string | null;
  sizeLabel?: string | null;
}): string {
  const lines = [
    `Number Flow — ${dateLabel ?? 'Daily Puzzle'}`,
    sizeLabel ? `Size: ${sizeLabel}` : `Size: ${puzzle.size}x${puzzle.size}`,
    `Time: ${formatDuration(elapsedMs)}`,
    `Moves: ${moveStat}`,
    ...generateAccuracyLines(puzzle, history),
  ];
  return lines.join('\n');
}

function generateAccuracyLines(puzzle: Puzzle, history: CellMistakeHistory): string[] {
  const givens = new Set<string>();
  puzzle.givens.forEach(({ row, col }) => givens.add(positionKey({ row, col })));
  const lines: string[] = [];
  for (let row = 0; row < puzzle.size; row++) {
    let line = '';
    for (let col = 0; col < puzzle.size; col++) {
      const key = positionKey({ row, col });
      if (givens.has(key)) {
        line += SHARE_SYMBOLS.given;
      } else if (history[key]) {
        line += SHARE_SYMBOLS.mistake;
      } else {
        line += SHARE_SYMBOLS.clean;
      }
    }
    lines.push(line);
  }
  return lines;
}

async function copyShareToClipboard(payload: string) {
  if (
    typeof navigator !== 'undefined' &&
    navigator.clipboard &&
    typeof window !== 'undefined' &&
    window.isSecureContext
  ) {
    await navigator.clipboard.writeText(payload);
    return;
  }

  if (typeof document !== 'undefined') {
    const textarea = document.createElement('textarea');
    textarea.value = payload;
    textarea.style.position = 'fixed';
    textarea.style.opacity = '0';
    textarea.style.pointerEvents = 'none';
    document.body.appendChild(textarea);
    textarea.focus();
    textarea.select();
    document.execCommand('copy');
    document.body.removeChild(textarea);
    return;
  }

  throw new Error('Clipboard unavailable');
}
