import Link from 'next/link';
import { useEffect, useState, useRef, useCallback, useMemo } from 'react';
import { useGameStore } from '@/state/gameStore';
import {
  getDailyPuzzle,
  getDailyPuzzleKey,
  getDailyConfig,
  getDefaultDailySelection,
} from '@/lib/daily';
import { getConfiguredSizesForDifficulty } from '@/config/dailySettings';
import type { DailySelection, DailyDifficultyId } from '@/lib/daily';
import { loadGameState, saveGameState, clearGameState } from '@/lib/persistence';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import Palette from '@/components/Palette/Palette';
import BottomSheet from '@/components/Palette/BottomSheet';
import CompletionModal from '@/components/HUD/CompletionModal';
import { SessionStats } from '@/components/HUD/SessionStats';
import SettingsMenu from '@/components/HUD/SettingsMenu';
import { SequenceAnnouncer } from '@/sequence/components';
import { TutorialSplash } from '@/components/HUD/TutorialSplash';

const DAILY_SETTINGS_CONFIG = getDailyConfig();

const ALLOWED_DIFFICULTIES = new Set(DAILY_SETTINGS_CONFIG.difficulties);

const DAILY_SELECTION_PREFERENCE_KEY = 'hpz:daily:selection';
const TUTORIAL_SEEN_KEY = 'hpz:tutorial:seen';

function normalizeSelection(raw?: Partial<DailySelection>): DailySelection {
  const defaultSelection = getDefaultDailySelection();
  const difficulty =
    raw?.difficulty && ALLOWED_DIFFICULTIES.has(raw.difficulty)
      ? raw.difficulty
      : defaultSelection.difficulty;
  const sizeOptions = getConfiguredSizesForDifficulty(difficulty);
  const allowedSizes = new Set(sizeOptions.map((option) => option.size));
  let size = raw?.size && allowedSizes.has(raw.size) ? raw.size : defaultSelection.size;
  if (DAILY_SETTINGS_CONFIG.mixSizes || sizeOptions.length === 0) {
    size = undefined;
  } else if (size === undefined || !allowedSizes.has(size)) {
    size = sizeOptions[0]?.size;
  }
  return { difficulty, size };
}

function loadSelectionPreference(): DailySelection {
  if (typeof window === 'undefined') {
    return normalizeSelection();
  }
  try {
    const saved = localStorage.getItem(DAILY_SELECTION_PREFERENCE_KEY);
    if (saved) {
      const parsed = JSON.parse(saved) as Partial<DailySelection>;
      return normalizeSelection(parsed);
    }
  } catch (err) {
    console.warn('Failed to load selection preference:', err);
  }
  return normalizeSelection();
}

function saveSelectionPreference(selection: DailySelection): void {
  if (typeof window === 'undefined') {
    return;
  }
  try {
    localStorage.setItem(DAILY_SELECTION_PREFERENCE_KEY, JSON.stringify(selection));
  } catch (err) {
    console.warn('Failed to save selection preference:', err);
  }
}

/**
 * Daily puzzle page (US1 implementation).
 */
export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selection, setSelection] = useState<DailySelection>(() => loadSelectionPreference());
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);
  const [hasSeenTutorial, setHasSeenTutorial] = useState(true);
  const previousSelectionKeyRef = useRef<string>(getDailyPuzzleKey(selection));
  const [sessionDate] = useState(() => new Date());
  const difficultyOptions = DAILY_SETTINGS_CONFIG.difficulties;
  const sizeOptionsForDifficulty = getConfiguredSizesForDifficulty(selection.difficulty);
  const showSizeSelector =
    !DAILY_SETTINGS_CONFIG.mixSizes && sizeOptionsForDifficulty.length > 1;
  
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore(
    (state) => state.dismissCompletionStatus
  );
  const resetMistakeHistory = useGameStore((state) => state.resetMistakeHistory);
  const sequenceState = useGameStore((state) => state.sequenceState);
  const recentMistakes = useGameStore((state) => state.recentMistakes);
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
  const difficultyLabel = selection.difficulty === 'classic' ? 'Classic' : 'Expert';
  const sizeDescriptor = puzzle ? `${puzzle.size}x${puzzle.size}` : selection.size ? `${selection.size}x${selection.size}` : undefined;
  const dailyDescriptor = sizeDescriptor ? `${difficultyLabel} · ${sizeDescriptor}` : difficultyLabel;

  // Handle "Play Again" - clear saved state and reset puzzle
  const handlePlayAgain = useCallback(() => {
    if (puzzle) {
      const dailyKey = getDailyPuzzleKey(selection);
      clearGameState(dailyKey);
      useGameStore.setState({ sequenceBoard: null, sequenceBoardKey: null });
      resetMistakeHistory();
      useGameStore.getState().resetPuzzle();
    }
  }, [puzzle, selection, resetMistakeHistory]);

  const handleDifficultyChange = (difficulty: DailyDifficultyId) => {
    if (difficulty === selection.difficulty) {
      return;
    }
    const nextSelection = normalizeSelection({ ...selection, difficulty });
    setLoading(true);
    setError(null);
    setSelection(nextSelection);
    saveSelectionPreference(nextSelection);
  };

  const handleSizeChange = (newSize: number) => {
    if (selection.size === newSize) {
      return;
    }
    const nextSelection = normalizeSelection({ ...selection, size: newSize });
    setLoading(true);
    setError(null);
    setSelection(nextSelection);
    saveSelectionPreference(nextSelection);
  };

  useEffect(() => {
    if (DAILY_SETTINGS_CONFIG.mixSizes) {
      if (selection.size !== undefined) {
        const next = { ...selection, size: undefined };
        setSelection(next);
        saveSelectionPreference(next);
      }
      return;
    }

    const options = getConfiguredSizesForDifficulty(selection.difficulty);
    if (options.length === 0) {
      if (selection.size !== undefined) {
        const next = { ...selection, size: undefined };
        setSelection(next);
        saveSelectionPreference(next);
      }
      return;
    }

    const allowed = new Set(options.map((option) => option.size));
    if (selection.size && allowed.has(selection.size)) {
      return;
    }

    const fallback = options[0]?.size;
    if (fallback !== undefined && selection.size !== fallback) {
      const next = { ...selection, size: fallback };
      setSelection(next);
      saveSelectionPreference(next);
    }
  }, [selection.difficulty, selection.size, setSelection]);

  useEffect(() => {
    if (puzzle) {
      const previousKey = previousSelectionKeyRef.current;
      const nextKey = getDailyPuzzleKey(selection);
      if (previousKey !== nextKey) {
        saveGameState(previousKey);
      }
      previousSelectionKeyRef.current = nextKey;
    }

    let cancelled = false;
    getDailyPuzzle(selection)
      .then((nextPuzzle) => {
        if (cancelled) {
          return;
        }

        if (nextPuzzle) {
          const dailyKey = getDailyPuzzleKey(selection);
          const restored = loadGameState(nextPuzzle, undefined, dailyKey);
          if (!restored) {
            loadPuzzle(nextPuzzle);
          }
        } else {
          setError('No daily puzzle available. Generate packs using the CLI.');
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

  // Subscribe to grid changes for auto-save
  const grid = useGameStore((state) => state.grid);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const isComplete = useGameStore((state) => state.isComplete);

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

  // Auto-save on state changes
  useEffect(() => {
    const shouldSave =
      puzzle &&
      !loading &&
      (selection.size === undefined || puzzle.size === selection.size);
    if (shouldSave) {
      const timer = setTimeout(() => {
        const dailyKey = getDailyPuzzleKey(selection);
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
        <p>Loading daily puzzle...</p>
      </div>
    );
  }

  if (error || !puzzle) {
    return (
      <div
        className="flex min-h-screen items-center justify-center flex-col gap-4"
        style={pageViewportStyle}
      >
        <p className="text-red-600">Error: {error || 'Failed to load puzzle'}</p>
        <Link href="/packs" className="text-primary hover:underline">
          Browse puzzle packs
        </Link>
      </div>
    );
  }

  return (
    <main
      className="flex min-h-screen flex-col items-center justify-center p-4 gap-6"
      style={pageViewportStyle}
    >
      <div className="flex w-full max-w-3xl flex-col items-center gap-2 text-center">
        <div className="relative mb-6 flex w-full items-center justify-center">
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: 'IowanTitle, serif' }}
          >
            Number Flow
          </h1>
          <div className="absolute right-0 flex">
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

        {showSizeSelector && (
          <div
            className="mb-2 flex flex-wrap gap-2"
            role="group"
            aria-label="Select puzzle size"
          >
            {sizeOptionsForDifficulty.map((option) => (
              <button
                key={option.id}
                onClick={() => handleSizeChange(option.size)}
                disabled={loading}
                className={`
                  px-3 py-1.5 rounded-full text-sm font-medium transition-colors border
                  ${selection.size === option.size
                    ? 'border-primary bg-primary text-primary-foreground shadow-sm'
                    : 'border-border bg-surface-muted text-copy hover:bg-surface'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                aria-pressed={selection.size === option.size}
              >
                {option.label}
              </button>
            ))}
          </div>
        )}

        <div className="w-full">
          <div className="flex justify-center">
            <div className="inline-flex flex-wrap items-center gap-2 rounded-full border border-border bg-surface px-3 py-0.5 text-sm text-copy shadow-sm">
              <div className="inline-flex items-center gap-2">
                <SessionStats variant="inline" />
              </div>
              <span className="h-5 w-px bg-border/50" aria-hidden="true" />
              <div className="inline-flex items-center gap-0 rounded-full bg-surface-muted px-0 py-0">
                {difficultyOptions.map((diff) => {
                  const isActive = selection.difficulty === diff;
                  const label = diff === 'classic' ? 'Classic' : 'Expert';
                  return (
                    <button
                      key={diff}
                      type="button"
                      onClick={() => handleDifficultyChange(diff)}
                      className={`rounded-full px-2 py-0 text-xs font-semibold uppercase tracking-wide transition-colors ${
                        isActive
                          ? 'bg-primary text-primary-foreground'
                          : 'text-copy-muted hover:text-copy'
                      }`}
                      aria-pressed={isActive}
                      disabled={loading}
                    >
                      {label}
                    </button>
                  );
                })}
              </div>
            </div>
          </div>
        </div>
      </div>

      <GuidedGrid />
      
      {/* Old number palette hidden - using guided sequence flow instead */}
      {/* <BottomSheet>
        <Palette />
      </BottomSheet> */}

      <CompletionModal
        isOpen={completionStatus !== null}
        onClose={dismissCompletionStatus}
        onPlayAgain={handlePlayAgain}
        dailyLabel={dailyDescriptor}
        dateLabel={dateLabel}
      />
      
      {/* Screen reader announcements for accessibility */}
      {sequenceState && (
        <SequenceAnnouncer
          state={sequenceState}
          recentMistakes={recentMistakes}
        />
      )}

      <TutorialSplash isOpen={isTutorialOpen} onClose={closeTutorial} />
    </main>
  );
}
