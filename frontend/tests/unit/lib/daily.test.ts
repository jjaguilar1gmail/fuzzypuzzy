import { describe, it, expect, beforeEach, afterEach, vi } from 'vitest';
import type { Puzzle } from '@/domain/puzzle';

const catalogEntries = [
  { pack_id: 'classic-pack', puzzle_id: 'c1', difficulty: 'classic', size: 5, intermediate_level: 1 },
  { pack_id: 'classic-pack', puzzle_id: 'c2', difficulty: 'classic', size: 6, intermediate_level: 2 },
  { pack_id: 'expert-pack', puzzle_id: 'e1', difficulty: 'expert', size: 5, intermediate_level: 1 },
  { pack_id: 'expert-pack', puzzle_id: 'e2', difficulty: 'expert', size: 6, intermediate_level: 3 },
];

const entryMap = new Map<string, (typeof catalogEntries)[number]>();
catalogEntries.forEach((entry) => {
  entryMap.set(`${entry.pack_id}/${entry.puzzle_id}`, entry);
});

vi.mock('@/lib/loaders/packs', () => ({
  loadPuzzle: vi.fn(async (packId: string, puzzleId: string): Promise<Puzzle> => {
    const entry = entryMap.get(`${packId}/${puzzleId}`);
    if (!entry) {
      throw new Error('Puzzle not found');
    }
    return {
      schema_version: '1.0',
      id: entry.puzzle_id,
      pack_id: entry.pack_id,
      size: entry.size,
      difficulty: entry.difficulty,
      seed: 1,
      clue_count: 1,
      givens: [],
      solution: null,
    } as Puzzle;
  }),
}));

const { loadPuzzle } = await import('@/lib/loaders/packs');
const loadPuzzleMock = vi.mocked(loadPuzzle);
const { getDailyPuzzle, getDailyPuzzleKey, getDefaultDailySelection } = await import('@/lib/daily');

describe('daily scheduling helpers', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-11-17T12:00:00Z')); // Monday -> level 1
    vi.stubGlobal('fetch', vi.fn(async () => ({
      ok: true,
      json: async () => ({ entries: catalogEntries }),
    })));
  });

  afterEach(() => {
    vi.useRealTimers();
    vi.unstubAllGlobals();
    loadPuzzleMock.mockClear();
  });

  it('builds unique daily keys with difficulty and size', () => {
    const key = getDailyPuzzleKey(
      { difficulty: 'classic', size: 5 },
      new Date(Date.UTC(2025, 11, 1, 12)),
    );
    expect(key).toBe('daily-2025-12-01-classic-5');

    const difficultyOnly = getDailyPuzzleKey(
      { difficulty: 'expert' },
      new Date(Date.UTC(2025, 11, 1, 12)),
    );
    expect(difficultyOnly).toBe('daily-2025-12-01-expert');
  });

  it('returns default selection from config', () => {
    const selection = getDefaultDailySelection();
    expect(selection.difficulty).toBeDefined();
  });

  it('returns deterministic puzzles per difficulty', async () => {
    const classic = await getDailyPuzzle({ difficulty: 'classic', size: 5 });
    expect(classic?.id).toBe('c1');

    const expert = await getDailyPuzzle({ difficulty: 'expert', size: 5 });
    expect(expert?.id).toBe('e1');

    expect(loadPuzzleMock).toHaveBeenCalledTimes(2);
  });
});
