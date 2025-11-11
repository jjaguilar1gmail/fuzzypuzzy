import { useEffect, useState, useMemo } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { PackSummary, Difficulty } from '@/domain/puzzle';
import { loadPacksList } from '@/lib/loaders/packs';

type DifficultyFilter = Difficulty | 'all';

/**
 * Packs listing page with difficulty filtering (US2).
 */
export default function PacksIndexPage() {
  const [packs, setPacks] = useState<PackSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [difficultyFilter, setDifficultyFilter] = useState<DifficultyFilter>('all');

  useEffect(() => {
    loadPacksList()
      .then(setPacks)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const filteredPacks = useMemo(() => {
    if (difficultyFilter === 'all') {
      return packs;
    }
    return packs.filter((pack) => {
      return pack.difficulty_counts && pack.difficulty_counts[difficultyFilter] > 0;
    });
  }, [packs, difficultyFilter]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading packs...</p>
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

  const difficulties: DifficultyFilter[] = ['all', 'easy', 'medium', 'hard', 'extreme'];

  return (
    <main className="min-h-screen p-8">
      <div className="max-w-7xl mx-auto">
        <div className="mb-8">
          <h1 className="text-3xl font-bold mb-4">Puzzle Packs</h1>
          
          {/* Difficulty filter buttons */}
          <div className="flex flex-wrap gap-2">
            {difficulties.map((diff) => (
              <button
                key={diff}
                onClick={() => setDifficultyFilter(diff)}
                className={`px-4 py-2 rounded-lg font-medium transition-all ${
                  difficultyFilter === diff
                    ? 'bg-primary text-white shadow-md'
                    : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                }`}
                aria-pressed={difficultyFilter === diff}
              >
                {diff.charAt(0).toUpperCase() + diff.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {filteredPacks.length === 0 ? (
          <p className="text-gray-600">
            {packs.length === 0
              ? 'No packs available yet. Generate packs using the CLI.'
              : `No packs found with ${difficultyFilter} difficulty.`}
          </p>
        ) : (
          <motion.div
            className="grid gap-6 md:grid-cols-2 lg:grid-cols-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.15 }}
          >
            {filteredPacks.map((pack, index) => (
              <motion.div
                key={pack.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.15, delay: index * 0.02 }}
              >
                <Link
                  href={`/packs/${pack.id}`}
                  className="block border rounded-lg p-6 hover:shadow-lg transition-shadow bg-white"
                >
                  <h2 className="text-xl font-semibold mb-2">{pack.title}</h2>
                  {pack.description && (
                    <p className="text-sm text-gray-600 mb-4">{pack.description}</p>
                  )}
                  
                  <div className="text-sm mb-3">
                    <span className="font-medium text-gray-700">
                      {pack.puzzle_count} puzzle{pack.puzzle_count !== 1 ? 's' : ''}
                    </span>
                  </div>

                  {pack.difficulty_counts && (
                    <div className="flex flex-wrap gap-2 text-xs">
                      {Object.entries(pack.difficulty_counts).map(([diff, count]) => (
                        <span
                          key={diff}
                          className={`px-2 py-1 rounded ${
                            diff === 'easy'
                              ? 'bg-green-100 text-green-800'
                              : diff === 'medium'
                              ? 'bg-yellow-100 text-yellow-800'
                              : diff === 'hard'
                              ? 'bg-orange-100 text-orange-800'
                              : 'bg-red-100 text-red-800'
                          }`}
                        >
                          {count} {diff}
                        </span>
                      ))}
                    </div>
                  )}

                  {pack.created_at && (
                    <p className="text-xs text-gray-500 mt-3">
                      Created {new Date(pack.created_at).toLocaleDateString()}
                    </p>
                  )}
                </Link>
              </motion.div>
            ))}
          </motion.div>
        )}
      </div>
    </main>
  );
}
