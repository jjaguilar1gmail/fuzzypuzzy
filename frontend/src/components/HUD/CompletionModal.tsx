import { useEffect, useCallback, useMemo, useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@/state/gameStore';
import { formatDuration, formatMoveStat } from '@/components/HUD/SessionStats';
import { Puzzle } from '@/domain/puzzle';
import type { CellMistakeHistory } from '@/state/cellMistakeHistory';
import { positionKey } from '@/domain/position';
import type { DailySizeId } from '@/lib/daily';

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
      setShareFeedback('Unable to share');
    }
  }, [puzzle, cellMistakeHistory, moveStat, elapsedMs, dateLabel, sizeLabel]);

  useEffect(() => {
    if (!shareFeedback) return;
    const id = window.setTimeout(() => setShareFeedback(null), 2500);
    return () => window.clearTimeout(id);
  }, [shareFeedback]);

  const statsList = (
    <div className="space-y-4">
      {sizeLabel && (
        <div className="flex justify-between items-center gap-6">
          <span className="text-gray-600">Size:</span>
          <span className="font-semibold">{sizeLabel}</span>
        </div>
      )}
      {dateLabel && (
        <div className="flex justify-between items-center gap-6">
          <span className="text-gray-600">Date:</span>
          <span className="font-semibold">{dateLabel}</span>
        </div>
      )}
      <div className="flex justify-between items-center gap-6">
        <span className="text-gray-600">Time:</span>
        <span className="font-semibold">{formatDuration(elapsedMs)}</span>
      </div>

      <div className="flex justify-between items-center gap-6">
        <span className="text-gray-600">Moves:</span>
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
              className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-labelledby="completion-title"
              aria-modal="true"
            >
              <div className="mb-4 flex items-start justify-between gap-4">
                <h2
                  id="completion-title"
                  className={`text-3xl font-bold ${
                    isCorrect ? 'text-green-600' : 'text-red-600'
                  }`}
                >
                  {isCorrect ? 'Puzzle Complete!' : 'Incorrect Solution'}
                </h2>
                {shareEnabled && (
                  <div className="flex flex-col items-end gap-1">
                    <button
                      type="button"
                      onClick={handleShare}
                      className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1 text-sm font-medium text-blue-700 shadow-sm transition hover:bg-blue-100"
                      aria-label="Share puzzle result"
                    >
                      <ShareIcon />
                      Share
                    </button>
                    {shareFeedback && (
                      <span className="text-xs font-medium text-blue-500">
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
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isCorrect ? 'Play Again' : 'Keep Editing'}
                </motion.button>

                <motion.button
                  onClick={handleSecondaryAction}
                  className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                    isCorrect
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-red-500 text-white hover:bg-red-600'
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

          let colorClass = 'bg-emerald-300';
          let label = 'Never had a wrong value';
          if (isGiven) {
            colorClass = 'bg-gray-300';
            label = 'Given cell';
          } else if (hadMistake) {
            colorClass = 'bg-red-400';
            label = 'Had a wrong value at some point';
          }

          return (
            <span
              key={key}
              className={`rounded ${colorClass}`}
              style={{ width: cellSize, height: cellSize }}
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
      className="flex flex-col items-center gap-2 text-xs text-gray-500"
      aria-label="Accuracy map showing how many cells were ever incorrect"
    >
      <div className="rounded-2xl bg-white/80 p-3 shadow-inner ring-1 ring-gray-100">
        {grid}
      </div>
      <div className="flex gap-3">
        <LegendItem colorClass="bg-emerald-300" label="Clean" />
        <LegendItem colorClass="bg-red-400" label="Had mistake" />
        <LegendItem colorClass="bg-gray-300" label="Given" />
      </div>
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
      width="18"
      height="18"
      viewBox="0 0 18 18"
      aria-hidden="true"
      className="text-blue-600"
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
    'Accuracy:',
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
