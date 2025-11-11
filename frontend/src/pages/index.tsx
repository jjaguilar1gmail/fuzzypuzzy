import { useEffect, useState } from 'react';
import { useGameStore } from '@/state/gameStore';
import { getDailyPuzzle } from '@/lib/daily';
import { loadGameState, saveGameState } from '@/lib/persistence';
import Grid from '@/components/Grid/Grid';
import Palette from '@/components/Palette/Palette';
import CompletionModal from '@/components/HUD/CompletionModal';
import SettingsMenu from '@/components/HUD/SettingsMenu';

/**
 * Daily puzzle page (US1 implementation).
 */
export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showCompletion, setShowCompletion] = useState(false);
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);
  const puzzle = useGameStore((state) => state.puzzle);
  const isComplete = useGameStore((state) => state.isComplete);

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

  // Show completion modal
  useEffect(() => {
    if (isComplete) {
      setShowCompletion(true);
    }
  }, [isComplete]);

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
    <main className="flex min-h-screen flex-col items-center justify-center p-4 gap-8">
      <div className="text-center">
        <div className="flex items-center justify-center gap-4 mb-2">
          <h1 className="text-3xl font-bold">Hidato Daily Puzzle</h1>
          <SettingsMenu />
        </div>
        <p className="text-gray-600">
          {puzzle.size}×{puzzle.size} · {puzzle.difficulty}
        </p>
      </div>

      <Grid />
      <Palette />

      <CompletionModal
        isOpen={showCompletion}
        onClose={() => setShowCompletion(false)}
      />
    </main>
  );
}
