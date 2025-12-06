import { z } from 'zod';

/**
 * Zod schema for CellValue from contracts/puzzle.schema.json
 */
export const CellValueSchema = z.object({
  row: z.number().int().min(0),
  col: z.number().int().min(0),
  value: z.number().int().min(1),
});

/**
 * Zod schema for Puzzle from contracts/puzzle.schema.json (draft-07)
 */
const MetricsSchema = z
  .object({
    timings_ms: z.record(z.string(), z.number()).optional(),
    solver: z.record(z.string(), z.unknown()).optional(),
    structure: z.record(z.string(), z.unknown()).optional(),
    mask: z.record(z.string(), z.unknown()).optional(),
    repair: z.record(z.string(), z.unknown()).optional(),
  })
  .passthrough()
  .optional();

const DifficultyEnum = z.enum(['classic', 'expert']);

export const PuzzleSchema = z.object({
  schema_version: z.string().optional().default('1.0'),
  id: z.string(),
  pack_id: z.string().optional(),
  size: z.number().int().min(5).max(10),
  difficulty: DifficultyEnum,
  seed: z.number().int(),
  clue_count: z.number().int().min(1),
  max_gap: z.union([z.number().int().max(12), z.null()]).optional(),
  difficulty_score_1: z.number().optional(),
  difficulty_score_2: z.number().optional(),
  intermediate_level: z.union([z.literal(1), z.literal(2), z.literal(3)]).optional(),
  givens: z.array(CellValueSchema).min(1),
  solution: z.array(CellValueSchema).nullable().optional(),
  metrics: MetricsSchema,
});

export type PuzzleInput = z.input<typeof PuzzleSchema>;
export type PuzzleOutput = z.output<typeof PuzzleSchema>;
