import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const packSummaries = [
  {
    id: 'pack-alpha',
    title: 'Alpha Pack',
    puzzle_count: 2,
    created_at: '2025-11-17T00:00:00Z',
  },
  {
    id: 'pack-beta',
    title: 'Beta Pack',
    puzzle_count: 2,
    created_at: '2025-11-17T00:00:00Z',
  },
] as const;

const packs = {
  'pack-alpha': {
    schema_version: '1.0',
    id: 'pack-alpha',
    title: 'Alpha Pack',
    description: '',
    puzzles: ['0001', '0002'],
    created_at: '2025-11-17T00:00:00Z',
  },
  'pack-beta': {
    schema_version: '1.0',
    id: 'pack-beta',
    title: 'Beta Pack',
    description: '',
    puzzles: ['0003', '0004'],
    created_at: '2025-11-17T00:00:00Z',
  },
} as const;

const puzzles = {
  'pack-alpha/0001': {
    id: '0001',
    pack_id: 'pack-alpha',
    size: 5,
    difficulty: 'medium',
    seed: 1,
    clue_count: 5,
    givens: [],
  },
  'pack-alpha/0002': {
    id: '0002',
    pack_id: 'pack-alpha',
    size: 5,
    difficulty: 'medium',
    seed: 2,
    clue_count: 5,
    givens: [],
  },
  'pack-beta/0003': {
    id: '0003',
    pack_id: 'pack-beta',
    size: 5,
    difficulty: 'hard',
    seed: 3,
    clue_count: 5,
    givens: [],
  },
  'pack-beta/0004': {
    id: '0004',
    pack_id: 'pack-beta',
    size: 5,
    difficulty: 'hard',
    seed: 4,
    clue_count: 5,
    givens: [],
  },
} as const;

let toggleOrder = false;

vi.mock('@/lib/loaders/packs', () => {
  return {
    loadPacksList: vi.fn(async () => {
      toggleOrder = !toggleOrder;
      return toggleOrder ? [...packSummaries] : [...packSummaries].reverse();
    }),
    loadPack: vi.fn(async (packId: keyof typeof packs) => packs[packId]),
    loadPuzzle: vi.fn(async (packId: string, puzzleId: string) => {
      const key = `${packId}/${puzzleId}` as keyof typeof puzzles;
      return puzzles[key];
    }),
  };
});

const { getDailyPuzzle } = await import('@/lib/daily');

describe('getDailyPuzzle determinism', () => {
  beforeEach(() => {
    vi.useFakeTimers();
    vi.setSystemTime(new Date('2025-11-17T12:00:00Z'));
    toggleOrder = false;
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('returns the same puzzle even if pack order changes between calls', async () => {
    const first = await getDailyPuzzle('small');
    const second = await getDailyPuzzle('small');

    expect(first).not.toBeNull();
    expect(second).not.toBeNull();
    expect(second?.id).toBe(first?.id);
    expect(second?.pack_id).toBe(first?.pack_id);
  });
});
