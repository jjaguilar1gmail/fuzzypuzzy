import { useEffect, useState } from 'react';
import Link from 'next/link';
import { PackSummary } from '@/domain/puzzle';
import { loadPacksList } from '@/lib/loaders/packs';

/**
 * Packs listing page (US2 placeholder).
 */
export default function PacksIndexPage() {
  const [packs, setPacks] = useState<PackSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadPacksList()
      .then(setPacks)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

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

  return (
    <main className="min-h-screen p-8">
      <h1 className="text-3xl font-bold mb-8">Puzzle Packs</h1>
      {packs.length === 0 ? (
        <p className="text-gray-600">No packs available yet. Generate packs using the CLI.</p>
      ) : (
        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
          {packs.map((pack) => (
            <Link
              key={pack.id}
              href={`/packs/${pack.id}`}
              className="border rounded-lg p-6 hover:shadow-lg transition-shadow"
            >
              <h2 className="text-xl font-semibold mb-2">{pack.title}</h2>
              {pack.difficulty_counts && (
                <div className="text-sm text-gray-600">
                  {Object.entries(pack.difficulty_counts).map(([diff, count]) => (
                    <span key={diff} className="mr-3">
                      {diff}: {count}
                    </span>
                  ))}
                </div>
              )}
            </Link>
          ))}
        </div>
      )}
    </main>
  );
}
