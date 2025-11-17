import { PackSummary, Puzzle } from '@/domain/puzzle';
import { loadPacksList, loadPack, loadPuzzle } from '@/lib/loaders/packs';

/**
 * Daily puzzle size options.
 */
export type DailySizeId = 'small' | 'medium' | 'large';

export interface DailySizeOption {
  id: DailySizeId;
  rows: number;
  cols: number;
  label: string;
  order: number;
}

/**
 * Available daily puzzle size options.
 */
export const DAILY_SIZE_OPTIONS: Record<DailySizeId, DailySizeOption> = {
  small: { id: 'small', rows: 5, cols: 5, label: 'Small (5×5)', order: 1 },
  medium: { id: 'medium', rows: 6, cols: 6, label: 'Medium (6×6)', order: 2 },
  large: { id: 'large', rows: 7, cols: 7, label: 'Large (7×7)', order: 3 },
};

/**
 * Default daily puzzle size for first-time visitors.
 */
export const DEFAULT_DAILY_SIZE: DailySizeId = 'medium';

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
 * Hash function for (date, sizeId) -> number.
 * Provides deterministic selection per (date, size) combination.
 */
function hashDateAndSize(date: Date, sizeId: DailySizeId): number {
  const dateHash = hashDate(date);
  const sizeHash = DAILY_SIZE_OPTIONS[sizeId].order;
  // Combine hashes: date determines base, size provides offset
  return dateHash + (sizeHash * 1000);
}

/**
 * Get today's daily puzzle from available packs.
 * Deterministic: same (date, sizeId) -> same puzzle (modulo available pool).
 * Falls back to next available if target is missing.
 * @param sizeId - Optional size filter; if omitted, returns any size
 */
export async function getDailyPuzzle(sizeId?: DailySizeId): Promise<Puzzle | null> {
  try {
    // Load all packs
    const packs = await loadPacksList();
    if (packs.length === 0) return null;

    // Flatten all puzzle IDs from all packs, filtering by size if specified
    const targetSize = sizeId ? DAILY_SIZE_OPTIONS[sizeId].rows : null;
    const allPuzzleRefs: Array<{ packId: string; puzzleId: string }> = [];
    
    for (const packSummary of packs) {
      const pack = await loadPack(packSummary.id);
      for (const puzzleId of pack.puzzles) {
        // Load puzzle to check size if filtering
        if (targetSize !== null) {
          try {
            const puzzle = await loadPuzzle(pack.id, puzzleId);
            if (puzzle.size === targetSize) {
              allPuzzleRefs.push({ packId: pack.id, puzzleId });
            }
          } catch (err) {
            // Skip unavailable puzzles
            continue;
          }
        } else {
          allPuzzleRefs.push({ packId: pack.id, puzzleId });
        }
      }
    }

    if (allPuzzleRefs.length === 0) return null;

    // Deterministic selection per (date, size)
    const today = new Date();
    const hash = sizeId ? hashDateAndSize(today, sizeId) : hashDate(today);
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
 * @param sizeId - Optional size identifier for size-specific keys
 */
export function getDailyPuzzleKey(sizeId?: DailySizeId): string {
  const today = new Date();
  const dateStr = today.toISOString().split('T')[0];
  return sizeId ? `daily-${dateStr}-${sizeId}` : `daily-${dateStr}`;
}
