import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { Puzzle } from '@/domain/puzzle';
import { loadPuzzle } from '@/lib/loaders/packs';
import { useGameStore } from '@/state/gameStore';

/**
 * Individual puzzle page within a pack (US2 placeholder).
 * Will reuse Grid/Palette components from US1.
 */
export default function PackPuzzlePage() {
  const router = useRouter();
  const { packId, puzzleId } = router.query;
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const loadPuzzleToStore = useGameStore((state) => state.loadPuzzle);

  useEffect(() => {
    if (!packId || typeof packId !== 'string') return;
    if (!puzzleId || typeof puzzleId !== 'string') return;
    
    loadPuzzle(packId, puzzleId)
      .then((puzzle) => {
        loadPuzzleToStore(puzzle);
        setLoading(false);
      })
      .catch((err) => {
        setError(err.message);
        setLoading(false);
      });
  }, [packId, puzzleId, loadPuzzleToStore]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading puzzle...</p>
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
    <main className="min-h-screen p-4">
      <Link href={`/packs/${packId}`} className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to pack
      </Link>
      <h1 className="text-2xl font-bold mb-4">Puzzle {puzzleId}</h1>
      <p className="text-gray-600 mb-6">Grid and controls placeholder (US1 components)</p>
      {/* TODO: Render Grid, Palette, HUD components */}
    </main>
  );
}
