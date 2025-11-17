import { useEffect, useState } from 'react';
import { useGameStore } from '@/state/gameStore';
import { 
  getDailyPuzzle, 
  DAILY_SIZE_OPTIONS, 
  DEFAULT_DAILY_SIZE,
  type DailySizeId 
} from '@/lib/daily';
import { loadGameState, saveGameState } from '@/lib/persistence';
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
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore(
    (state) => state.dismissCompletionStatus
  );
  const sequenceState = useGameStore((state) => state.sequenceState);
  const sequenceBoard = useGameStore((state) => state.sequenceBoard);
  const recentMistakes = useGameStore((state) => state.recentMistakes);

  // Handle size change: reload puzzle and clear state
  const handleSizeChange = (newSize: DailySizeId) => {
    setLoading(true);
    setError(null);
    setSelectedSize(newSize);
    saveSizePreference(newSize);
  };

  useEffect(() => {
    getDailyPuzzle(selectedSize)
      .then((puzzle) => {
        if (puzzle) {
          // Try to restore saved state for this size
          const restored = loadGameState(puzzle, selectedSize);
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

  // Auto-save on state changes
  useEffect(() => {
    if (puzzle && !loading) {
      const timer = setTimeout(() => {
        saveGameState(puzzle.id, selectedSize);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [puzzle, loading, selectedSize, useGameStore((state) => state.grid)]);

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
