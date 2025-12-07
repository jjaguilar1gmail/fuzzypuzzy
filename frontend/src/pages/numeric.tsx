import Link from 'next/link';
import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useGameStore } from '@/state/gameStore';
import {
  getDailyPuzzle,
  getDailyPuzzleKey,
} from '@/lib/daily';
import type { DailySelection, DailyDifficultyId } from '@/lib/daily';
import { loadGameState, saveGameState, clearGameState } from '@/lib/persistence';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import CompletionModal from '@/components/HUD/CompletionModal';
import { SessionStats } from '@/components/HUD/SessionStats';
import { SequenceAnnouncer } from '@/sequence/components';
import { TutorialSplash } from '@/components/HUD/TutorialSplash';
import { getSymbolSetById } from '@/symbolSets/registry';

const NUMERIC_SIZE_OPTIONS = [
  { id: '5x5', size: 5, label: 'Small' },
  { id: '6x6', size: 6, label: 'Medium' },
  { id: '7x7', size: 7, label: 'Large' },
] as const;
const NUMERIC_ALLOWED_SIZES = NUMERIC_SIZE_OPTIONS.map((option) => option.size);

const NUMERIC_DIFFICULTY: DailyDifficultyId = 'classic';
const NUMERIC_SELECTION_KEY = 'hpz:numeric:selection';
const TUTORIAL_SEEN_KEY = 'hpz:tutorial:seen';

type NumericSelection = DailySelection & { size: number };

function normalizeNumericSelection(raw?: Partial<DailySelection>): NumericSelection {
  const allowedSizes = new Set<number>(NUMERIC_SIZE_OPTIONS.map((option) => option.size));
  const fallbackSize: number = NUMERIC_SIZE_OPTIONS[0]?.size ?? 5;
  const size = raw?.size && allowedSizes.has(raw.size) ? raw.size : fallbackSize;
  return { difficulty: NUMERIC_DIFFICULTY, size };
}

function loadNumericSelection(): NumericSelection {
  if (typeof window === 'undefined') {
    return normalizeNumericSelection();
  }
  try {
    const saved = window.localStorage.getItem(NUMERIC_SELECTION_KEY);
    if (saved) {
      const parsed = JSON.parse(saved) as Partial<DailySelection>;
      return normalizeNumericSelection(parsed);
    }
  } catch (err) {
    console.warn('Failed to load numeric selection preference:', err);
  }
  return normalizeNumericSelection();
}

function saveNumericSelection(selection: NumericSelection): void {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    window.localStorage.setItem(NUMERIC_SELECTION_KEY, JSON.stringify(selection));
  } catch (err) {
    console.warn('Failed to save numeric selection preference:', err);
  }
}

function getNumericDailyKey(selection: NumericSelection, date = new Date()): string {
  return `${getDailyPuzzleKey(selection, date)}-numeric`;
}

export default function NumericModePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selection, setSelection] = useState<NumericSelection>(() => loadNumericSelection());
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);
  const [hasSeenTutorial, setHasSeenTutorial] = useState(true);
  const previousSelectionKeyRef = useRef<string>(getNumericDailyKey(selection));
  const [sessionDate] = useState(() => new Date());
  const sizeOptions = NUMERIC_SIZE_OPTIONS;
  const showSizeSelector = true;

  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore((state) => state.dismissCompletionStatus);
  const resetMistakeHistory = useGameStore((state) => state.resetMistakeHistory);
  const sequenceState = useGameStore((state) => state.sequenceState);
  const recentMistakes = useGameStore((state) => state.recentMistakes);
  const grid = useGameStore((state) => state.grid);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const isComplete = useGameStore((state) => state.isComplete);

  const activeSymbolSet = useMemo(() => getSymbolSetById('numeric'), []);
  const previewTotalCells = useMemo(() => {
    const size = puzzle?.size ?? selection.size ?? 6;
    return size * size;
  }, [puzzle?.size, selection.size]);
  const pageViewportStyle = { minHeight: 'var(--app-viewport-height)' };
  const dateLabel = useMemo(
    () =>
      sessionDate.toLocaleDateString(undefined, {
        month: 'short',
        day: 'numeric',
        year: 'numeric',
      }),
    [sessionDate]
  );
  const difficultyLabel = puzzle?.difficulty === 'expert' ? 'Expert' : 'Classic';
  const sizeDescriptor = puzzle
    ? `${puzzle.size}x${puzzle.size}`
    : `${selection.size}x${selection.size}`;
  const dailyDescriptor = `${difficultyLabel} - ${sizeDescriptor}`;

  const handlePlayAgain = useCallback(() => {
    if (puzzle) {
      const dailyKey = getNumericDailyKey(selection);
      clearGameState(dailyKey);
      useGameStore.setState({ sequenceBoard: null, sequenceBoardKey: null });
      resetMistakeHistory();
      useGameStore.getState().resetPuzzle();
    }
  }, [puzzle, selection, resetMistakeHistory]);

  const handleSizeChange = (newSize: number) => {
    if (selection.size === newSize) {
      return;
    }
    const nextSelection = normalizeNumericSelection({ size: newSize });
    setLoading(true);
    setError(null);
    setSelection(nextSelection);
    saveNumericSelection(nextSelection);
  };

  useEffect(() => {
    const previousKey = previousSelectionKeyRef.current;
    const nextKey = getNumericDailyKey(selection);
    if (previousKey !== nextKey) {
      saveGameState(previousKey);
    }
    previousSelectionKeyRef.current = nextKey;

    let cancelled = false;
    getDailyPuzzle(selection, undefined, {
      allowedSizes: NUMERIC_ALLOWED_SIZES,
      allowedDifficulties: ['classic', 'expert'],
    })
      .then((nextPuzzle) => {
        if (cancelled) {
          return;
        }
        if (nextPuzzle) {
          const dailyKey = getNumericDailyKey(selection);
          const restored = loadGameState(nextPuzzle, undefined, dailyKey);
          if (!restored) {
            loadPuzzle(nextPuzzle);
          }
        } else {
          setError('No numeric puzzle available. Generate packs using the CLI.');
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setError(err instanceof Error ? err.message : String(err));
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoading(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, [loadPuzzle, selection, puzzle]);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      const seen = window.localStorage.getItem(TUTORIAL_SEEN_KEY) === 'true';
      setHasSeenTutorial(seen);
    } catch (err) {
      console.warn('Unable to read tutorial preference', err);
    }
  }, []);

  const markTutorialSeen = useCallback(() => {
    setHasSeenTutorial(true);
    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem(TUTORIAL_SEEN_KEY, 'true');
      } catch (err) {
        console.warn('Unable to save tutorial preference', err);
      }
    }
  }, []);

  const openTutorial = () => {
    setIsTutorialOpen(true);
    if (!hasSeenTutorial) {
      markTutorialSeen();
    }
  };

  const closeTutorial = () => {
    setIsTutorialOpen(false);
    markTutorialSeen();
  };

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    const shouldSave = puzzle && !loading;
    if (shouldSave) {
      const timer = setTimeout(() => {
        const dailyKey = getNumericDailyKey(selection);
        saveGameState(dailyKey);
      }, 1000);
      return () => clearTimeout(timer);
    }
    return undefined;
  }, [puzzle, loading, selection, grid, elapsedMs, isComplete]);

  if (loading) {
    return (
      <div
        className="flex min-h-screen items-center justify-center"
        style={pageViewportStyle}
      >
        <p>Loading numeric puzzle...</p>
      </div>
    );
  }

  if (error || !puzzle) {
    return (
      <div
        className="flex min-h-screen items-center justify-center flex-col gap-4"
        style={pageViewportStyle}
      >
        <p className="text-red-600">Error: {error || 'Failed to load numeric puzzle'}</p>
        <Link href="/" className="text-primary hover:underline">
          Return to the main page
        </Link>
      </div>
    );
  }

  return (
    <main
      className="relative flex min-h-screen flex-col items-center justify-center p-4 gap-6"
      style={pageViewportStyle}
    >
      <div className="flex w-full max-w-3xl flex-col items-center gap-2 text-center">
        <div className="relative mb-1 flex w-full items-center justify-center">
          <Link
            href="/"
            aria-label="Return to Symbol Flow"
            className="absolute left-0 inline-flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface-elevated/70 text-lg font-bold text-copy shadow-sm transition hover:bg-surface-elevated hover:text-copy focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
          >
            ←
          </Link>
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: 'IowanTitle, serif' }}
          >
            Number Flow
          </h1>
          <div className="absolute right-0 flex gap-2">
            <button
              type="button"
              onClick={openTutorial}
              aria-label="Open how to play tutorial"
              className="relative inline-flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface-elevated/70 text-lg font-bold text-copy shadow-sm transition hover:bg-surface-elevated hover:text-copy focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-primary"
            >
              ?
              {!hasSeenTutorial && (
                <span className="pointer-events-none absolute -top-1 -right-1 rounded-full bg-primary px-1.5 py-0.5 text-[10px] font-bold uppercase leading-none text-primary-foreground shadow-sm">
                  New
                </span>
              )}
            </button>
          </div>
        </div>

        <div className="w-full">
          <div className="flex justify-center">
            <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-border bg-surface px-3 py-0.5 text-sm text-copy shadow-sm">
              <div className="inline-flex items-center gap-2">
                <SessionStats variant="inline" />
              </div>
              <span className="h-5 w-px bg-border/50" aria-hidden="true" />
              <span className="rounded-full bg-primary text-primary-foreground px-3 py-0.5 text-xs font-semibold uppercase tracking-wide">
                {difficultyLabel}
              </span>
            </div>
          </div>
        </div>

        {showSizeSelector && (
          <div
            className="flex flex-wrap gap-2"
            role="group"
            aria-label="Select puzzle size"
          >
            {sizeOptions.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSizeChange(option.size)}
                disabled={loading}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors border ${
                  selection.size === option.size
                    ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                    : 'border-border bg-surface-muted text-copy hover:bg-surface'
                } disabled:opacity-50 disabled:cursor-not-allowed`}
                aria-pressed={selection.size === option.size}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}

        <GuidedGrid symbolSetId="numeric" />
      </div>

      <CompletionModal
        isOpen={completionStatus !== null}
        onClose={dismissCompletionStatus}
        onPlayAgain={handlePlayAgain}
        dailyLabel={dailyDescriptor}
        dateLabel={dateLabel}
      />

      {sequenceState && (
        <SequenceAnnouncer
          state={sequenceState}
          recentMistakes={recentMistakes}
        />
      )}

      <TutorialSplash
        isOpen={isTutorialOpen}
        onClose={closeTutorial}
        symbolSet={activeSymbolSet}
        previewTotalCells={previewTotalCells}
      />
    </main>
  );
}
