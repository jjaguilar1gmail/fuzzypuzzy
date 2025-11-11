import { create } from 'zustand';
import { persist } from 'zustand/middleware';

/**
 * Progress tracking for individual puzzle within a pack.
 */
export interface PuzzleProgress {
  puzzleId: string;
  completed: boolean;
  completedAt?: string;
  moves: number;
  elapsedMs: number;
}

/**
 * Progress tracking for an entire pack.
 */
export interface PackProgress {
  packId: string;
  lastPlayedPuzzleId: string | null;
  lastPlayedAt: string;
  puzzles: Record<string, PuzzleProgress>;
}

interface ProgressState {
  packs: Record<string, PackProgress>;
  
  // Actions
  recordCompletion: (
    packId: string,
    puzzleId: string,
    moves: number,
    elapsedMs: number
  ) => void;
  recordProgress: (packId: string, puzzleId: string) => void;
  getPackProgress: (packId: string) => PackProgress | undefined;
  getPuzzleProgress: (packId: string, puzzleId: string) => PuzzleProgress | undefined;
  getCompletedCount: (packId: string) => number;
  isCompleted: (packId: string, puzzleId: string) => boolean;
  getLastPlayedPuzzle: (packId: string) => string | null;
  clearPackProgress: (packId: string) => void;
}

/**
 * Zustand store for tracking pack and puzzle progress.
 * Persisted to localStorage to maintain state across sessions.
 */
export const useProgressStore = create<ProgressState>()(
  persist(
    (set, get) => ({
      packs: {},

      recordCompletion: (packId, puzzleId, moves, elapsedMs) => {
        set((state) => {
          const pack = state.packs[packId] || {
            packId,
            lastPlayedPuzzleId: null,
            lastPlayedAt: new Date().toISOString(),
            puzzles: {},
          };

          return {
            packs: {
              ...state.packs,
              [packId]: {
                ...pack,
                lastPlayedPuzzleId: puzzleId,
                lastPlayedAt: new Date().toISOString(),
                puzzles: {
                  ...pack.puzzles,
                  [puzzleId]: {
                    puzzleId,
                    completed: true,
                    completedAt: new Date().toISOString(),
                    moves,
                    elapsedMs,
                  },
                },
              },
            },
          };
        });
      },

      recordProgress: (packId, puzzleId) => {
        set((state) => {
          const pack = state.packs[packId] || {
            packId,
            lastPlayedPuzzleId: null,
            lastPlayedAt: new Date().toISOString(),
            puzzles: {},
          };

          // Don't overwrite existing puzzle progress if it exists
          if (pack.puzzles[puzzleId]?.completed) {
            return state;
          }

          return {
            packs: {
              ...state.packs,
              [packId]: {
                ...pack,
                lastPlayedPuzzleId: puzzleId,
                lastPlayedAt: new Date().toISOString(),
              },
            },
          };
        });
      },

      getPackProgress: (packId) => {
        return get().packs[packId];
      },

      getPuzzleProgress: (packId, puzzleId) => {
        const pack = get().packs[packId];
        return pack?.puzzles[puzzleId];
      },

      getCompletedCount: (packId) => {
        const pack = get().packs[packId];
        if (!pack) return 0;
        return Object.values(pack.puzzles).filter((p) => p.completed).length;
      },

      isCompleted: (packId, puzzleId) => {
        const puzzle = get().getPuzzleProgress(packId, puzzleId);
        return puzzle?.completed ?? false;
      },

      getLastPlayedPuzzle: (packId) => {
        const pack = get().packs[packId];
        return pack?.lastPlayedPuzzleId ?? null;
      },

      clearPackProgress: (packId) => {
        set((state) => {
          const { [packId]: removed, ...rest } = state.packs;
          return { packs: rest };
        });
      },
    }),
    {
      name: 'hpz-progress',
      version: 1,
    }
  )
);
