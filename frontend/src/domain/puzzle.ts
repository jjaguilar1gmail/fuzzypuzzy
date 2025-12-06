/**
 * Position represents a cell coordinate in the grid.
 */
export interface Position {
  row: number;
  col: number;
}

/**
 * Difficulty levels for puzzles.
 */
export type Difficulty = 'classic' | 'expert';

export type IntermediateLevel = 1 | 2 | 3;

/**
 * Cell value with position.
 */
export interface CellValue {
  row: number;
  col: number;
  value: number;
}

/**
 * A single Hidato puzzle.
 */
export interface PuzzleMetrics {
  timings_ms?: Record<string, number>;
  solver?: Record<string, unknown>;
  structure?: Record<string, unknown>;
  mask?: Record<string, unknown>;
  repair?: Record<string, unknown>;
  [key: string]: unknown;
}

export interface Puzzle {
  schema_version?: string;
  id: string;
  pack_id?: string;
  size: number;
  difficulty: Difficulty;
  seed: number;
  clue_count: number;
  max_gap?: number | null;
  difficulty_score_1?: number;
  difficulty_score_2?: number;
  intermediate_level?: IntermediateLevel;
  givens: CellValue[];
  solution?: CellValue[] | null;
  metrics?: PuzzleMetrics;
}

/**
 * Puzzle pack metadata.
 */
export interface Pack {
  schema_version?: string;
  id: string;
  title: string;
  description?: string;
  puzzles: string[];
  difficulty_counts?: Record<Difficulty, number>;
  intermediate_level_counts?: Record<Difficulty, Partial<Record<`${IntermediateLevel}`, number>>>;
  difficulty_model?: {
    primary_split?: {
      metric?: string;
      classic_min_clues?: number;
    };
    intermediate_levels?: {
      metric?: string;
      thresholds?: Record<Difficulty, { p33: number; p66: number }>;
    };
    scores?: Record<string, string>;
  };
  size_distribution?: Record<string, number>;
  size_catalog?: Record<string, string[]>;
  created_at: string;
}

/**
 * Pack summary for listing.
 */
export interface PackSummary {
  id: string;
  title: string;
  description?: string;
  puzzle_count: number;
  difficulty_counts?: Record<Difficulty, number>;
  size_distribution?: Record<string, number>;
  /**
   * Optional mapping of puzzle size -> ordered puzzle IDs for that size.
   * Enables size-aware selection without fetching each puzzle file.
   */
  size_catalog?: Record<string, string[]>;
  created_at: string;
}
