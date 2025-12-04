import { useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Pack, Difficulty } from '@/domain/puzzle';
import { loadPack } from '@/lib/loaders/packs';

/**
 * Pack detail page showing metadata and puzzle list (US2).
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
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error || 'Pack not found'}</p>
          <Link href="/packs" className="text-primary hover:underline">
            ← Back to packs
          </Link>
        </div>
      </div>
    );
  }

  const difficultyColors: Record<Difficulty, string> = {
    classic: 'bg-blue-100 text-blue-800',
    expert: 'bg-purple-100 text-purple-800',
  };

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-4xl mx-auto">
        <Link href="/packs" className="text-primary hover:underline mb-6 inline-block">
          ← Back to packs
        </Link>
        
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15 }}
        >
          <h1 className="text-4xl font-bold mb-3">{pack.title}</h1>
          {pack.description && (
            <p className="text-lg text-gray-600 mb-6">{pack.description}</p>
          )}
          
          <div className="bg-gray-50 rounded-lg p-6 mb-8">
            <h2 className="text-xl font-semibold mb-4">Pack Statistics</h2>
            
            <div className="grid md:grid-cols-2 gap-6">
              <div>
                <p className="text-sm text-gray-600 mb-2">Total Puzzles</p>
                <p className="text-3xl font-bold text-primary">{pack.puzzles.length}</p>
              </div>

              {pack.difficulty_counts && Object.keys(pack.difficulty_counts).length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">By Difficulty</p>
                  <div className="flex flex-wrap gap-2">
                    {Object.entries(pack.difficulty_counts).map(([diff, count]) => (
                      <span
                        key={diff}
                        className={`px-3 py-1 rounded font-medium ${
                          difficultyColors[diff as Difficulty] ?? 'bg-gray-100 text-gray-700'
                        }`}
                      >
                        {count} {diff}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {pack.size_distribution && Object.keys(pack.size_distribution).length > 0 && (
                <div>
                  <p className="text-sm text-gray-600 mb-2">Grid Sizes</p>
                  <div className="flex flex-wrap gap-2 text-sm">
                    {Object.entries(pack.size_distribution).map(([size, count]) => (
                      <span key={size} className="bg-primary-muted text-primary px-3 py-1 rounded">
                        {count} puzzles - {size}x{size}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              <div>
                <p className="text-sm text-gray-600 mb-2">Created</p>
                <p className="font-medium">
                  {new Date(pack.created_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'long',
                    day: 'numeric',
                  })}
                </p>
              </div>
            </div>
          </div>

          <div>
            <h2 className="text-2xl font-semibold mb-4">Puzzles</h2>
            <p className="text-sm text-gray-600 mb-4">
              Select a puzzle to start playing
            </p>
            
            <div className="grid gap-3">
              {pack.puzzles.map((puzzleId, index) => (
                <motion.div
                  key={puzzleId}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ duration: 0.15, delay: index * 0.02 }}
                >
                  <Link
                    href={`/packs/${packId}/puzzles/${puzzleId}`}
                    className="flex items-center justify-between border rounded-lg p-4 hover:shadow-md hover:bg-gray-50 transition-all group"
                  >
                    <div className="flex items-center gap-4">
                      <div className="w-10 h-10 rounded-full bg-primary text-white flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <p className="font-semibold group-hover:text-primary transition-colors">
                          Puzzle #{index + 1}
                        </p>
                        <p className="text-sm text-gray-600">ID: {puzzleId}</p>
                      </div>
                    </div>
                    
                    <svg
                      className="w-6 h-6 text-gray-400 group-hover:text-primary transition-colors"
                      fill="none"
                      viewBox="0 0 24 24"
                      stroke="currentColor"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M9 5l7 7-7 7"
                      />
                    </svg>
                  </Link>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </main>
  );
}
