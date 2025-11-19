import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';

const packSummaries = [
  {
    id: 'aaa-small-pack',
    title: 'Small Pack',
    puzzle_count: 2,
    size_catalog: {
      '5': ['small-0001', 'small-0002'],
    },
    created_at: '2025-11-17T00:00:00Z',
  },
  {
    id: 'bbb-medium-pack',
    title: 'Medium Pack',
    puzzle_count: 2,
    size_catalog: {
      '6': ['medium-0001', 'medium-0002'],
    },
    created_at: '2025-11-17T00:00:00Z',
  },
  {
    id: 'ccc-large-pack',
    title: 'Large Pack',
    puzzle_count: 2,
    size_catalog: {
      '7': ['large-0001', 'large-0002'],
    },
    created_at: '2025-11-17T00:00:00Z',
  },
] as const;

const packs = {
  'aaa-small-pack': {
    schema_version: '1.0',
    id: 'aaa-small-pack',
    title: 'Small Pack',
    description: '',
    puzzles: ['small-0001', 'small-0002'],
    created_at: '2025-11-17T00:00:00Z',
  },
  'bbb-medium-pack': {
    schema_version: '1.0',
    id: 'bbb-medium-pack',
    title: 'Medium Pack',
    description: '',
    puzzles: ['medium-0001', 'medium-0002'],
    created_at: '2025-11-17T00:00:00Z',
  },
  'ccc-large-pack': {
    schema_version: '1.0',
    id: 'ccc-large-pack',
    title: 'Large Pack',
    description: '',
    puzzles: ['large-0001', 'large-0002'],
    created_at: '2025-11-17T00:00:00Z',
  },
} as const;

const puzzles = {
  'aaa-small-pack/small-0001': {
    id: 'small-0001',
    pack_id: 'aaa-small-pack',
    size: 5,
    difficulty: 'medium',
    seed: 1,
    clue_count: 5,
    givens: [],
  },
  'aaa-small-pack/small-0002': {
    id: 'small-0002',
    pack_id: 'aaa-small-pack',
    size: 5,
    difficulty: 'medium',
    seed: 2,
    clue_count: 5,
    givens: [],
  },
  'bbb-medium-pack/medium-0001': {
    id: 'medium-0001',
    pack_id: 'bbb-medium-pack',
    size: 6,
    difficulty: 'hard',
    seed: 3,
    clue_count: 5,
    givens: [],
  },
  'bbb-medium-pack/medium-0002': {
    id: 'medium-0002',
    pack_id: 'bbb-medium-pack',
    size: 6,
    difficulty: 'hard',
    seed: 4,
    clue_count: 5,
    givens: [],
  },
  'ccc-large-pack/large-0001': {
    id: 'large-0001',
    pack_id: 'ccc-large-pack',
    size: 7,
    difficulty: 'hard',
    seed: 5,
    clue_count: 5,
    givens: [],
  },
  'ccc-large-pack/large-0002': {
    id: 'large-0002',
    pack_id: 'ccc-large-pack',
    size: 7,
    difficulty: 'hard',
    seed: 6,
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

const loaders = await import('@/lib/loaders/packs');
const loadPacksListMock = vi.mocked(loaders.loadPacksList);
const loadPackMock = vi.mocked(loaders.loadPack);

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

  it('selects deterministic sequential puzzles for each size', async () => {
    const smallPuzzle = await getDailyPuzzle('small');
    expect(smallPuzzle?.id).toBe('small-0001');

    const mediumPuzzle = await getDailyPuzzle('medium');
    expect(mediumPuzzle?.id).toBe('medium-0002');
  });

  it('rotates to the next puzzle on the following day', async () => {
    const today = new Date('2025-11-17T12:00:00Z');
    vi.setSystemTime(today);
    const dayOneSmall = await getDailyPuzzle('small');
    expect(dayOneSmall?.id).toBe('small-0001');

    vi.setSystemTime(new Date('2025-11-18T12:00:00Z'));
    const dayTwoSmall = await getDailyPuzzle('small');
    expect(dayTwoSmall?.id).toBe('small-0002');
  });

  it('returns null when no puzzles match the requested size', async () => {
    loadPacksListMock.mockResolvedValueOnce(
      packSummaries.filter((pack) => pack.id !== 'aaa-small-pack')
    );

    const puzzle = await getDailyPuzzle('small');
    expect(puzzle).toBeNull();
  });

  it('avoids loading pack metadata when size catalog is present', async () => {
    loadPackMock.mockClear();
    await getDailyPuzzle('small');
    expect(loadPackMock).not.toHaveBeenCalled();
  });

  it('falls back to loading packs when catalog data is missing', async () => {
    loadPackMock.mockClear();
    loadPacksListMock.mockResolvedValueOnce(
      packSummaries.map(({ size_catalog, ...rest }) => ({ ...rest }))
    );

    await getDailyPuzzle('small');
    expect(loadPackMock).toHaveBeenCalled();
  });
});
