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

const DAILY_SIZE_PREFERENCE_KEY = 'hpz:daily:size-preference';

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

  // Handle "Play Again" - clear saved state and reset puzzle
  const handlePlayAgain = useCallback(() => {
    if (puzzle) {
      const dailyKey = getDailyPuzzleKey(selectedSize);
      
      // Clear saved state from localStorage
      clearGameState(dailyKey);
      
      // Clear sequenceBoard from store so it won't be used as initialBoard
      useGameStore.setState({ sequenceBoard: null });
      
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
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading daily puzzle...</p>
      </div>
    );
  }

  if (error || !puzzle) {
    return (
      <div className="flex min-h-screen items-center justify-center flex-col gap-4">
        <p className="text-red-600">Error: {error || 'Failed to load puzzle'}</p>
        <a href="/packs" className="text-blue-600 hover:underline">
          Browse puzzle packs →
        </a>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4 gap-6">
      <div className="flex flex-col items-center gap-2 text-center">
        <div className="flex items-center justify-center gap-4 mb-2">
          <h1
            className="text-3xl font-bold"
            style={{ fontFamily: 'IowanTitle, serif' }}
          >
            Number Flow
          </h1>
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
    </main>
  );
}
