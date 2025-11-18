import { describe, it, expect, beforeEach } from 'vitest';
import { loadGameState } from '@/lib/persistence';
import { useGameStore } from '@/state/gameStore';
import type { Puzzle } from '@/domain/puzzle';

const samplePuzzle: Puzzle = {
  id: '0001',
  pack_id: 'hard_5x5_soln',
  size: 5,
  difficulty: 'hard',
  seed: 1,
  clue_count: 5,
  givens: [],
};

describe('persistence identity checks', () => {
  beforeEach(() => {
    localStorage.clear();
    // Reset store state so loadGameState can call loadPuzzle cleanly
    const store = useGameStore.getState();
    store.resetPuzzle();
  });

  it('skips restoring when persisted puzzle identity mismatches', () => {
    const key = 'hpz:v1:state:daily-2025-11-18-small';
    const mismatchedState = {
      schema_version: '1.1',
      puzzle_id: 'daily-2025-11-18-small',
      pack_id: 'hard_5x5_soln',
      puzzle_identity: 'hard_5x5_soln:9999',
      cell_entries: {},
      candidates: {},
      elapsed_ms: 0,
      undo_count: 0,
    };

    localStorage.setItem(key, JSON.stringify(mismatchedState));

    const restored = loadGameState(samplePuzzle, undefined, 'daily-2025-11-18-small');
    expect(restored).toBe(false);
    expect(localStorage.getItem(key)).toBeNull();
  });

  it('skips restoring legacy daily saves that lack puzzle identity', () => {
    const key = 'hpz:v1:state:daily-2025-11-18-small';
    const legacyState = {
      schema_version: '1.1',
      puzzle_id: 'daily-2025-11-18-small',
      pack_id: 'hard_5x5_soln',
      cell_entries: {},
      candidates: {},
      elapsed_ms: 0,
      undo_count: 0,
    };

    localStorage.setItem(key, JSON.stringify(legacyState));

    const restored = loadGameState(samplePuzzle, undefined, 'daily-2025-11-18-small');
    expect(restored).toBe(false);
    expect(localStorage.getItem(key)).toBeNull();
  });
});
