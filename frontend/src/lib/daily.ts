import { PackSummary, Puzzle } from '@/domain/puzzle';
import { loadPacksList, loadPack, loadPuzzle } from '@/lib/loaders/packs';

/**
 * Simple hash function for date -> number.
 */
function hashDate(date: Date): number {
  const dateStr = date.toISOString().split('T')[0]; // YYYY-MM-DD
  let hash = 0;
  for (let i = 0; i < dateStr.length; i++) {
    hash = (hash << 5) - hash + dateStr.charCodeAt(i);
    hash = hash & hash; // Convert to 32-bit integer
  }
  return Math.abs(hash);
}

/**
 * Get today's daily puzzle from available packs.
 * Deterministic: same date -> same puzzle (modulo available pool).
 * Falls back to next available if target is missing.
 */
export async function getDailyPuzzle(): Promise<Puzzle | null> {
  try {
    // Load all packs
    const packs = await loadPacksList();
    if (packs.length === 0) return null;

    // Flatten all puzzle IDs from all packs
    const allPuzzleRefs: Array<{ packId: string; puzzleId: string }> = [];
    for (const packSummary of packs) {
      const pack = await loadPack(packSummary.id);
      pack.puzzles.forEach((puzzleId) => {
        allPuzzleRefs.push({ packId: pack.id, puzzleId });
      });
    }

    if (allPuzzleRefs.length === 0) return null;

    // Deterministic selection
    const today = new Date();
    const hash = hashDate(today);
    let index = hash % allPuzzleRefs.length;

    // Try loading the selected puzzle; fallback to next if missing
    for (let attempts = 0; attempts < allPuzzleRefs.length; attempts++) {
      const ref = allPuzzleRefs[index];
      try {
        const puzzle = await loadPuzzle(ref.packId, ref.puzzleId);
        return puzzle;
      } catch (err) {
        // Puzzle missing; try next
        console.warn(`Puzzle ${ref.puzzleId} in pack ${ref.packId} not found, trying next`);
        index = (index + 1) % allPuzzleRefs.length;
      }
    }

    return null;
  } catch (err) {
    console.error('Failed to load daily puzzle:', err);
    return null;
  }
}

/**
 * Get the daily puzzle ID (for caching/persistence keys).
 */
export function getDailyPuzzleKey(): string {
  const today = new Date();
  return `daily-${today.toISOString().split('T')[0]}`;
}
