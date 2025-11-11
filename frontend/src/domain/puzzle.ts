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
export type Difficulty = 'easy' | 'medium' | 'hard' | 'extreme';

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
export interface Puzzle {
  schema_version?: string;
  id: string;
  pack_id?: string;
  size: number;
  difficulty: Difficulty;
  seed: number;
  clue_count: number;
  max_gap?: number | null;
  givens: CellValue[];
  solution?: CellValue[] | null;
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
  size_distribution?: Record<string, number>;
  created_at: string;
}

/**
 * Pack summary for listing.
 */
export interface PackSummary {
  id: string;
  title: string;
  difficulty_counts?: Record<Difficulty, number>;
  size_distribution?: Record<string, number>;
}
