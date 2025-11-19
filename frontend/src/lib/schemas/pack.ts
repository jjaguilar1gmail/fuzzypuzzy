import { z } from 'zod';

/**
 * Zod schema for Pack from contracts/pack.schema.json (draft-07)
 */
export const PackSchema = z.object({
  schema_version: z.string().optional().default('1.0'),
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  puzzles: z.array(z.string()).min(1),
  difficulty_counts: z
    .record(z.enum(['easy', 'medium', 'hard', 'extreme']), z.number().int().min(0))
    .optional(),
  size_distribution: z.record(z.string(), z.number().int().min(0)).optional(),
  size_catalog: z.record(z.string(), z.array(z.string()).min(1)).optional(),
  created_at: z.string().datetime(),
});

export type PackInput = z.input<typeof PackSchema>;
export type PackOutput = z.output<typeof PackSchema>;

/**
 * Zod schema for PackSummary (listing view)
 */
export const PackSummarySchema = z.object({
  id: z.string(),
  title: z.string(),
  description: z.string().optional(),
  puzzle_count: z.number().int().min(1),
  difficulty_counts: z
    .record(z.enum(['easy', 'medium', 'hard', 'extreme']), z.number().int().min(0))
    .optional(),
  size_distribution: z.record(z.string(), z.number().int().min(0)).optional(),
  size_catalog: z.record(z.string(), z.array(z.string()).min(1)).optional(),
  created_at: z.string().datetime(),
});

export type PackSummaryInput = z.input<typeof PackSummarySchema>;
export type PackSummaryOutput = z.output<typeof PackSummarySchema>;
