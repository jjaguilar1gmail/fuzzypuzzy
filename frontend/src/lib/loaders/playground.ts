import { Pack, PackSummary, Puzzle } from '@/domain/puzzle';
import { PackSchema, PackSummarySchema } from '@/lib/schemas/pack';
import { PuzzleSchema } from '@/lib/schemas/puzzle';

const NO_STORE_FETCH: RequestInit = { cache: 'no-store' };
const SANDBOX_BASE = '/packs/playground';

function sortById<T extends { id: string }>(items: T[]): T[] {
  return [...items].sort((a, b) => a.id.localeCompare(b.id));
}

type CacheEntry<T> = {
  data: T | null;
  promise: Promise<T> | null;
};

const packListCache: CacheEntry<PackSummary[]> = { data: null, promise: null };
const packCache = new Map<string, Pack>();
const puzzleCache = new Map<string, Puzzle>();

async function fetchJson<T>(path: string): Promise<T> {
  const response = await fetch(path, NO_STORE_FETCH);
  if (!response.ok) {
    throw new Error(`Failed to load ${path}: ${response.statusText}`);
  }
  return response.json();
}

export async function loadSandboxPacksList(): Promise<PackSummary[]> {
  if (packListCache.data) {
    return packListCache.data;
  }
  if (packListCache.promise) {
    return packListCache.promise;
  }

  packListCache.promise = (async () => {
    try {
      const data = await fetchJson<unknown[]>(`${SANDBOX_BASE}/index.json`);
      const summaries = data.map((item) => PackSummarySchema.parse(item)) as PackSummary[];
      const sorted = sortById(summaries);
      packListCache.data = sorted;
      packListCache.promise = null;
      return sorted;
    } catch (error) {
      console.warn('Sandbox pack index missing or invalid, returning empty set.', error);
      packListCache.data = [];
      packListCache.promise = null;
      return [];
    }
  })();

  return packListCache.promise;
}

export async function loadSandboxPack(packId: string): Promise<Pack> {
  if (packCache.has(packId)) {
    return packCache.get(packId)!;
  }
  const data = await fetchJson(`${SANDBOX_BASE}/${packId}/metadata.json`);
  const parsed = PackSchema.parse(data) as Pack;
  const normalized: Pack = {
    ...parsed,
    puzzles: [...parsed.puzzles].sort((a, b) => a.localeCompare(b)),
  };
  packCache.set(packId, normalized);
  return normalized;
}

export async function loadSandboxPuzzle(packId: string, puzzleId: string): Promise<Puzzle> {
  const cacheKey = `${packId}/${puzzleId}`;
  if (puzzleCache.has(cacheKey)) {
    return puzzleCache.get(cacheKey)!;
  }
  const data = await fetchJson(`${SANDBOX_BASE}/${packId}/puzzles/${puzzleId}.json`);
  const parsed = PuzzleSchema.parse(data) as Puzzle;
  puzzleCache.set(cacheKey, parsed);
  return parsed;
}
