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
  // Use local date (YYYY-MM-DD) so puzzle changes at local midnight
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const dateStr = `${year}-${month}-${day}`;
  
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

const DAY_MS = 24 * 60 * 60 * 1000;

function getLocalDayIndex(date: Date): number {
  const midnight = new Date(date.getFullYear(), date.getMonth(), date.getDate());
  return Math.floor(midnight.getTime() / DAY_MS);
}

function positiveModulo(value: number, modulus: number): number {
  return ((value % modulus) + modulus) % modulus;
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

    // Flatten all puzzle IDs from all packs
    // Note: We load all puzzles here without size filtering for simplicity.
    // For better performance, consider adding size metadata to pack manifests.
    const allPuzzleRefs: Array<{ packId: string; puzzleId: string }> = [];
    
    for (const packSummary of packs) {
      const pack = await loadPack(packSummary.id);
      for (const puzzleId of pack.puzzles) {
        allPuzzleRefs.push({ packId: pack.id, puzzleId });
      }
    }

    if (allPuzzleRefs.length === 0) return null;

    allPuzzleRefs.sort((a, b) => {
      if (a.packId === b.packId) {
        return a.puzzleId.localeCompare(b.puzzleId);
      }
      return a.packId.localeCompare(b.packId);
    });

    // Deterministic selection per (date, size)
    const today = new Date();

    if (sizeId) {
      const targetSize = DAILY_SIZE_OPTIONS[sizeId].rows;
      const matchingPuzzles: Puzzle[] = [];

      for (const ref of allPuzzleRefs) {
        try {
          const puzzle = await loadPuzzle(ref.packId, ref.puzzleId);
          if (puzzle.size === targetSize) {
            matchingPuzzles.push(puzzle);
          }
        } catch (err) {
          console.warn(
            `Puzzle ${ref.puzzleId} in pack ${ref.packId} not found while building daily pool`,
            err
          );
        }
      }

      if (matchingPuzzles.length === 0) {
        return null;
      }

      const dayIndex = getLocalDayIndex(today);
      const rotationSeed = dayIndex + DAILY_SIZE_OPTIONS[sizeId].order;
      const selectedIndex = positiveModulo(rotationSeed, matchingPuzzles.length);
      return matchingPuzzles[selectedIndex];
    }

    const hash = hashDate(today);
    let startIndex = hash % allPuzzleRefs.length;

    for (let attempts = 0; attempts < allPuzzleRefs.length; attempts++) {
      const index = (startIndex + attempts) % allPuzzleRefs.length;
      const ref = allPuzzleRefs[index];
      
      try {
        const puzzle = await loadPuzzle(ref.packId, ref.puzzleId);
        return puzzle;
      } catch (err) {
        // Puzzle missing; try next
        console.warn(`Puzzle ${ref.puzzleId} in pack ${ref.packId} not found, trying next`, err);
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
  // Use local date so puzzle changes at local midnight
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, '0');
  const day = String(today.getDate()).padStart(2, '0');
  const dateStr = `${year}-${month}-${day}`;
  
  return sizeId ? `daily-${dateStr}-${sizeId}` : `daily-${dateStr}`;
}
