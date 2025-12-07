import {
  DAILY_CONFIG,
  DAILY_CONFIG as DAILY_SETTINGS,
  WEEKLY_LEVEL_ROTATION,
  type DailyConfig,
  type DailySizeConfig,
  getConfiguredSizesForDifficulty,
} from '@/config/dailySettings';
import { Difficulty, IntermediateLevel, Puzzle } from '@/domain/puzzle';
import { loadPuzzle } from '@/lib/loaders/packs';

export type DailyDifficultyId = Difficulty;
export type DailySizeOption = DailySizeConfig;

export interface DailySelection {
  difficulty: DailyDifficultyId;
  size?: number;
}

export interface DailyPuzzleOptions {
  allowedSizes?: number[];
  allowedDifficulties?: Difficulty[];
}

interface DailyCatalogEntry {
  pack_id?: string;
  pack_slug: string;
  puzzle_id: string;
  difficulty: Difficulty;
  size: number;
  intermediate_level: IntermediateLevel;
}

interface DailyCatalogData {
  entries: DailyCatalogEntry[];
}

let catalogCache: DailyCatalogEntry[] | null = null;
let catalogPromise: Promise<DailyCatalogEntry[]> | null = null;

function resolveAllowedSizes(
  difficulty: Difficulty | undefined,
  override?: number[],
): number[] {
  if (override && override.length > 0) {
    return override;
  }
  return getConfiguredSizesForDifficulty(difficulty).map((option) => option.size);
}

function resolveAllowedDifficulties(
  selection: DailySelection,
  override?: Difficulty[],
): Difficulty[] {
  if (override && override.length > 0) {
    return override;
  }
  return [selection.difficulty];
}

export function getDailyConfig(): DailyConfig {
  return DAILY_CONFIG;
}

export function getDailySizeOptions(): DailySizeOption[] {
  return DAILY_SETTINGS.sizes;
}

export function getDefaultDailySelection(): DailySelection {
  return {
    difficulty: DAILY_SETTINGS.defaultDifficulty,
    size: DAILY_SETTINGS.mixSizes ? undefined : DAILY_SETTINGS.defaultSize,
  };
}

async function loadCatalog(): Promise<DailyCatalogEntry[]> {
  if (catalogCache) {
    return catalogCache;
  }
  if (!catalogPromise) {
    catalogPromise = fetch('/daily_catalog.json', { cache: 'no-store' })
      .then((res) => {
        if (!res.ok) {
          throw new Error('Failed to load daily catalog');
        }
        return res.json() as Promise<DailyCatalogData>;
      })
      .then((data) => data.entries);
  }
  catalogCache = await catalogPromise;
  return catalogCache;
}

function hashDate(date: Date): number {
  const iso = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}-${String(
    date.getDate(),
  ).padStart(2, '0')}`;
  let hash = 0;
  for (let i = 0; i < iso.length; i += 1) {
    hash = (hash << 5) - hash + iso.charCodeAt(i);
    hash |= 0;
  }
  return Math.abs(hash);
}

function positiveModulo(value: number, modulus: number): number {
  return ((value % modulus) + modulus) % modulus;
}

export function getIntermediateLevelForDate(date = new Date()): IntermediateLevel {
  const day = date.getDay();
  return WEEKLY_LEVEL_ROTATION[day] ?? 1;
}

function computeSeed(date: Date, selection: DailySelection, level: number): number {
  const base = hashDate(date);
  const diffOffset = selection.difficulty === 'classic' ? 211 : 977;
  const sizeOffset = selection.size ? selection.size * 131 : 0;
  return base + diffOffset + sizeOffset + level * 17;
}

function filterEntries(
  entries: DailyCatalogEntry[],
  selection: DailySelection,
  targetLevel: IntermediateLevel,
  options?: DailyPuzzleOptions,
) {
  const allowedSizeSet = new Set(
    resolveAllowedSizes(selection.difficulty, options?.allowedSizes),
  );
  const allowedDifficultyList = resolveAllowedDifficulties(
    selection,
    options?.allowedDifficulties,
  );
  const allowedDifficultySet = new Set(allowedDifficultyList);

  const availableSizes = new Set<number>();
  entries.forEach((entry) => {
    if (allowedDifficultySet.has(entry.difficulty) && allowedSizeSet.has(entry.size)) {
      availableSizes.add(entry.size);
    }
  });

  const desiredSize =
    selection.size && availableSizes.has(selection.size) ? selection.size : undefined;

  const applyFilters = (opts?: { ignoreSizePreference?: boolean; ignoreSizeLimit?: boolean }) =>
    entries.filter((entry) => {
      if (!allowedDifficultySet.has(entry.difficulty)) {
        return false;
      }
      if (!opts?.ignoreSizeLimit && !allowedSizeSet.has(entry.size)) {
        return false;
      }
      if (!opts?.ignoreSizePreference && desiredSize) {
        return entry.size === desiredSize;
      }
      return true;
    });

  let matches = applyFilters();

  if (matches.length === 0) {
    matches = applyFilters({ ignoreSizePreference: true });
  }

  if (matches.length === 0) {
    matches = applyFilters({ ignoreSizePreference: true, ignoreSizeLimit: true });
  }

  if (matches.length === 0) {
    matches = entries.filter((entry) => allowedSizeSet.has(entry.size));
  }

  if (matches.length === 0) {
    return [];
  }

  const levelMatches = matches.filter((entry) => entry.intermediate_level === targetLevel);
  if (levelMatches.length > 0) {
    return levelMatches;
  }

  // fallback: find closest level buckets by absolute difference
  const grouped = matches.reduce<Record<number, DailyCatalogEntry[]>>((acc, entry) => {
    acc[entry.intermediate_level] = acc[entry.intermediate_level] || [];
    acc[entry.intermediate_level].push(entry);
    return acc;
  }, {});

  const sortedLevels = Object.keys(grouped)
    .map((lvl) => Number(lvl))
    .sort((a, b) => Math.abs(a - targetLevel) - Math.abs(b - targetLevel));

  for (const lvl of sortedLevels) {
    if (grouped[lvl]?.length) {
      return grouped[lvl];
    }
  }
  return matches;
}

async function loadPuzzleFromEntries(
  entries: DailyCatalogEntry[],
  startIndex: number,
): Promise<Puzzle | null> {
  if (entries.length === 0) {
    return null;
  }
  const normalizedStart = positiveModulo(startIndex, entries.length);
  for (let attempts = 0; attempts < entries.length; attempts += 1) {
    const index = (normalizedStart + attempts) % entries.length;
    const entry = entries[index];
    try {
      const slug = entry.pack_slug || entry.pack_id;
      if (!slug) {
        continue;
      }
      // eslint-disable-next-line no-await-in-loop
      const puzzle = await loadPuzzle(slug, entry.puzzle_id);
      return puzzle;
    } catch (err) {
      console.warn(
        `Failed to load puzzle ${entry.puzzle_id} from pack ${entry.pack_id}, trying fallback`,
        err,
      );
    }
  }
  return null;
}

export async function getDailyPuzzle(
  selection: DailySelection,
  date = new Date(),
  options?: DailyPuzzleOptions,
): Promise<Puzzle | null> {
  const catalog = await loadCatalog();
  const targetLevel = getIntermediateLevelForDate(date);
  const pool = filterEntries(catalog, selection, targetLevel, options);
  if (pool.length === 0) {
    return null;
  }
  const seed = computeSeed(date, selection, targetLevel);
  return loadPuzzleFromEntries(pool, seed);
}

export function getDailyPuzzleKey(selection: DailySelection, date = new Date()): string {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, '0');
  const day = String(date.getDate()).padStart(2, '0');
  const base = `daily-${year}-${month}-${day}-${selection.difficulty}`;
  return selection.size ? `${base}-${selection.size}` : base;
}
