import { useEffect, useState } from 'react';
import { useGameStore } from '@/state/gameStore';
import { getDailyPuzzle } from '@/lib/daily';
import { loadGameState, saveGameState } from '@/lib/persistence';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import Palette from '@/components/Palette/Palette';
import BottomSheet from '@/components/Palette/BottomSheet';
import CompletionModal from '@/components/HUD/CompletionModal';
import { SessionStats } from '@/components/HUD/SessionStats';
import SettingsMenu from '@/components/HUD/SettingsMenu';
import { SequenceAnnouncer } from '@/sequence/components';

/**
 * Daily puzzle page (US1 implementation).
 */
export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore(
    (state) => state.dismissCompletionStatus
  );
  const sequenceState = useGameStore((state) => state.sequenceState);
  const sequenceBoard = useGameStore((state) => state.sequenceBoard);
  const recentMistakes = useGameStore((state) => state.recentMistakes);

  useEffect(() => {
    getDailyPuzzle()
      .then((puzzle) => {
        if (puzzle) {
          // Try to restore saved state
          const restored = loadGameState(puzzle);
          if (!restored) {
            loadPuzzle(puzzle);
          }
        } else {
          setError('No daily puzzle available. Generate packs using the CLI.');
        }
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [loadPuzzle]);

  // Auto-save on state changes
  useEffect(() => {
    if (puzzle && !loading) {
      const timer = setTimeout(() => {
        saveGameState(puzzle.id);
      }, 1000);
      return () => clearTimeout(timer);
    }
  }, [puzzle, loading, useGameStore((state) => state.grid)]);

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
            NumberFlow
          </h1>
          {/* <SettingsMenu /> */}
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
