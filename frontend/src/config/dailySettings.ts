import { Difficulty, IntermediateLevel } from '@/domain/puzzle';

export type DailyDifficulty = Difficulty;

export interface DailySizeConfig {
  id: string;
  size: number;
  label: string;
}

export interface DailyConfig {
  difficulties: DailyDifficulty[];
  sizes: DailySizeConfig[];
  /** Optional overrides to restrict sizes per difficulty (using size IDs). */
  sizeOverrides?: Partial<Record<DailyDifficulty, string[]>>;
  /** When true, sizes are mixed within a difficulty and no size selector is shown. */
  mixSizes: boolean;
  /** Default difficulty pill selection. */
  defaultDifficulty: DailyDifficulty;
  /** Optional default size (if sizes are exposed individually). */
  defaultSize?: number;
}

export const DAILY_CONFIG: DailyConfig = {
  difficulties: ['classic','expert'],
  sizes: [
    { id: '5x5', size: 5, label: 'Small' },
    // { id: '6x6', size: 6, label: 'Medium' },
    // { id: '7x7', size: 7, label: 'Large' },
  ],
  sizeOverrides: {
    expert: ['5x5'],
  },
  mixSizes: false,
  defaultDifficulty: 'classic',
  defaultSize: 5,
};

export const WEEKLY_LEVEL_ROTATION: Record<number, IntermediateLevel> = {
  0: 3, // Sunday
  1: 1, // Monday
  2: 2, // Tuesday
  3: 2, // Wednesday
  4: 2, // Thursday
  5: 1, // Friday
  6: 3, // Saturday
};

const SIZE_LOOKUP = new Map(DAILY_CONFIG.sizes.map((size) => [size.id, size]));

export function getConfiguredSizesForDifficulty(
  difficulty?: DailyDifficulty,
): DailySizeConfig[] {
  if (!difficulty) {
    return DAILY_CONFIG.sizes;
  }
  const overrides = DAILY_CONFIG.sizeOverrides?.[difficulty];
  if (!overrides) {
    return DAILY_CONFIG.sizes;
  }
  return overrides
    .map((id) => SIZE_LOOKUP.get(id))
    .filter((value): value is DailySizeConfig => Boolean(value));
}
