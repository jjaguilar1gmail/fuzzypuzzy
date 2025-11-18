import { useEffect, useState, useRef, useCallback } from 'react';
import { useGameStore } from '@/state/gameStore';
import { 
  getDailyPuzzle, 
  getDailyPuzzleKey,
  DAILY_SIZE_OPTIONS, 
  DEFAULT_DAILY_SIZE,
  type DailySizeId 
} from '@/lib/daily';
import { loadGameState, saveGameState, clearGameState } from '@/lib/persistence';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import Palette from '@/components/Palette/Palette';
import BottomSheet from '@/components/Palette/BottomSheet';
import CompletionModal from '@/components/HUD/CompletionModal';
import { SessionStats } from '@/components/HUD/SessionStats';
import SettingsMenu from '@/components/HUD/SettingsMenu';
import { SequenceAnnouncer } from '@/sequence/components';
import { TutorialSplash } from '@/components/HUD/TutorialSplash';

const DAILY_SIZE_PREFERENCE_KEY = 'hpz:daily:size-preference';
const TUTORIAL_SEEN_KEY = 'hpz:tutorial:seen';

/**
 * Load saved size preference from localStorage.
 */
function loadSizePreference(): DailySizeId {
  // Check if we're in browser context (not SSR)
  if (typeof window === 'undefined') {
    return DEFAULT_DAILY_SIZE;
  }
  
  try {
    const saved = localStorage.getItem(DAILY_SIZE_PREFERENCE_KEY);
    if (saved && (saved === 'small' || saved === 'medium' || saved === 'large')) {
      return saved;
    }
  } catch (err) {
    console.warn('Failed to load size preference:', err);
  }
  return DEFAULT_DAILY_SIZE;
}

/**
 * Save size preference to localStorage.
 */
function saveSizePreference(sizeId: DailySizeId): void {
  // Check if we're in browser context (not SSR)
  if (typeof window === 'undefined') {
    return;
  }
  
  try {
    localStorage.setItem(DAILY_SIZE_PREFERENCE_KEY, sizeId);
  } catch (err) {
    console.warn('Failed to save size preference:', err);
  }
}

/**
 * Daily puzzle page (US1 implementation).
 */
export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedSize, setSelectedSize] = useState<DailySizeId>(() => loadSizePreference());
  const [isTutorialOpen, setIsTutorialOpen] = useState(false);
  const previousSizeRef = useRef<DailySizeId>(selectedSize);
  
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore(
    (state) => state.dismissCompletionStatus
  );
  const sequenceState = useGameStore((state) => state.sequenceState);
  const sequenceBoard = useGameStore((state) => state.sequenceBoard);
  const recentMistakes = useGameStore((state) => state.recentMistakes);
  const pageViewportStyle = { minHeight: 'var(--app-viewport-height)' };

  // Handle "Play Again" - clear saved state and reset puzzle
  const handlePlayAgain = useCallback(() => {
    if (puzzle) {
      const dailyKey = getDailyPuzzleKey(selectedSize);
      
      // Clear saved state from localStorage
      clearGameState(dailyKey);
      
      // Clear sequenceBoard from store so it won't be used as initialBoard
      useGameStore.setState({ sequenceBoard: null, sequenceBoardKey: null });
      
      // Reset the puzzle (will call loadPuzzle)
      useGameStore.getState().resetPuzzle();
    }
  }, [puzzle, selectedSize]);

  // Handle size change: reload puzzle and clear state
  const handleSizeChange = (newSize: DailySizeId) => {
    // Don't do anything if clicking the same size
    if (newSize === selectedSize) {
      return;
    }
    
    setLoading(true);
    setError(null);
    setSelectedSize(newSize);
    saveSizePreference(newSize);
  };

  useEffect(() => {
    // IMPORTANT: Save current state BEFORE loading new puzzle
    // This prevents race conditions where auto-save timer fires after grid is cleared
    if (puzzle && previousSizeRef.current !== selectedSize) {
      const previousDailyKey = getDailyPuzzleKey(previousSizeRef.current);
      saveGameState(previousDailyKey);
    }
    previousSizeRef.current = selectedSize;
    
    getDailyPuzzle(selectedSize)
      .then((puzzle) => {
        if (puzzle) {
          // Use date-based key for daily puzzles so state persists across size changes
          const dailyKey = getDailyPuzzleKey(selectedSize);
          
          // Try to restore saved state for this (date, size) combination
          const restored = loadGameState(puzzle, undefined, dailyKey);
          if (!restored) {
            loadPuzzle(puzzle);
          }
        } else {
          setError('No daily puzzle available. Generate packs using the CLI.');
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [loadPuzzle, selectedSize]);

  // Subscribe to grid changes for auto-save
  const grid = useGameStore((state) => state.grid);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const isComplete = useGameStore((state) => state.isComplete);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }
    try {
      const hasSeenTutorial = window.localStorage.getItem(TUTORIAL_SEEN_KEY);
      if (!hasSeenTutorial) {
        setIsTutorialOpen(true);
      }
    } catch (err) {
      console.warn('Unable to read tutorial preference', err);
    }
  }, []);

  const openTutorial = () => setIsTutorialOpen(true);
  const closeTutorial = () => {
    setIsTutorialOpen(false);
    if (typeof window !== 'undefined') {
      try {
        window.localStorage.setItem(TUTORIAL_SEEN_KEY, 'true');
      } catch (err) {
        console.warn('Unable to save tutorial preference', err);
      }
    }
  };

  // Auto-save on state changes
  useEffect(() => {
    // Only auto-save if puzzle size matches selected size (prevents saving wrong board to wrong key during transitions)
    if (puzzle && !loading && puzzle.size === DAILY_SIZE_OPTIONS[selectedSize].rows) {
      const timer = setTimeout(() => {
        // Use date-based key for daily puzzles
        const dailyKey = getDailyPuzzleKey(selectedSize);
        saveGameState(dailyKey);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [puzzle, loading, selectedSize, grid, elapsedMs, isComplete]);

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
        <a href="/packs" className="text-blue-600 hover:underline">
          Browse puzzle packs 
        </a>
      </div>
    );
  }

  return (
    <main
      className="flex min-h-screen flex-col items-center justify-center p-4 gap-6"
      style={pageViewportStyle}
    >
      <div className="flex w-full max-w-3xl flex-col items-center gap-2 text-center">
        <div className="relative mb-2 flex w-full items-center justify-center">
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: 'IowanTitle, serif' }}
          >
            Number Flow
          </h1>
          <button
            type="button"
            onClick={openTutorial}
            aria-label="Open how to play tutorial"
            className="absolute right-0 inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white/70 text-lg font-bold text-slate-900 shadow-sm transition hover:bg-white hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-blue-500"
          >
            ?
          </button>
          {/* <SettingsMenu /> */}
        </div>

        {/* Size selector pills */}
        <div 
          className="flex gap-2 mb-2"
          role="group"
          aria-label="Select puzzle size"
        >
          {Object.values(DAILY_SIZE_OPTIONS).map((option) => (
            <button
              key={option.id}
              onClick={() => handleSizeChange(option.id)}
              disabled={loading}
              className={`
                px-3 py-1.5 rounded-full text-sm font-medium transition-colors
                ${selectedSize === option.id
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }
                disabled:opacity-50 disabled:cursor-not-allowed
              `}
              aria-pressed={selectedSize === option.id}
            >
              {option.label}
            </button>
          ))}
        </div>

        <SessionStats />
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

