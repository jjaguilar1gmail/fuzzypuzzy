import { useEffect, useState } from 'react';
import { useGameStore } from '@/state/gameStore';
import { Puzzle } from '@/domain/puzzle';

/**
 * Daily puzzle page (MVP placeholder).
 * Will integrate with daily selection util (T012) and Grid component (US1).
 */
export default function HomePage() {
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loadPuzzle = useGameStore((state) => state.loadPuzzle);

  useEffect(() => {
    // TODO: Integrate getDailyPuzzle() from lib/daily.ts (T012)
    // For now, placeholder
    setLoading(false);
  }, []);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading daily puzzle...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-600">Error: {error}</p>
      </div>
    );
  }

  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-4">
      <h1 className="text-3xl font-bold mb-8">Hidato Daily Puzzle</h1>
      <p className="text-gray-600">Grid component placeholder (US1 implementation)</p>
      {/* TODO: Render Grid, Palette, HUD components */}
    </main>
  );
}
