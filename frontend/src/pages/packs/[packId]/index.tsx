import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { Pack } from '@/domain/puzzle';
import { loadPack } from '@/lib/loaders/packs';

/**
 * Pack detail page showing metadata and puzzle list (US2 placeholder).
 */
export default function PackDetailPage() {
  const router = useRouter();
  const { packId } = router.query;
  
  const [pack, setPack] = useState<Pack | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!packId || typeof packId !== 'string') return;
    
    loadPack(packId)
      .then(setPack)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [packId]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading pack...</p>
      </div>
    );
  }

  if (error || !pack) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p className="text-red-600">Error: {error || 'Pack not found'}</p>
      </div>
    );
  }

  return (
    <main className="min-h-screen p-8">
      <Link href="/packs" className="text-blue-600 hover:underline mb-4 inline-block">
        ← Back to packs
      </Link>
      <h1 className="text-3xl font-bold mb-2">{pack.title}</h1>
      {pack.description && <p className="text-gray-600 mb-6">{pack.description}</p>}
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-2">Pack Info</h2>
        <p className="text-sm text-gray-600">Total puzzles: {pack.puzzles.length}</p>
        {pack.difficulty_counts && (
          <div className="text-sm text-gray-600 mt-2">
            {Object.entries(pack.difficulty_counts).map(([diff, count]) => (
              <span key={diff} className="mr-4">
                {diff}: {count}
              </span>
            ))}
          </div>
        )}
      </div>

      <div>
        <h2 className="text-xl font-semibold mb-4">Puzzles</h2>
        <div className="grid gap-2">
          {pack.puzzles.map((puzzleId, index) => (
            <Link
              key={puzzleId}
              href={`/packs/${packId}/puzzles/${puzzleId}`}
              className="border rounded p-4 hover:bg-gray-50 transition-colors"
            >
              Puzzle #{index + 1} ({puzzleId})
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
