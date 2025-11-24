import type { Puzzle } from '@/domain/puzzle';

const DEFAULT_START_VALUE = 1;

export function deriveSymbolRange(
  puzzle: Puzzle | null,
  fallbackSize: number
): { startValue: number; endValue: number } {
  const fallbackEnd =
    fallbackSize > 0 ? fallbackSize * fallbackSize : DEFAULT_START_VALUE;

  if (!puzzle) {
    return {
      startValue: DEFAULT_START_VALUE,
      endValue: fallbackEnd,
    };
  }

  const candidateValues: number[] = [];
  if (puzzle.givens?.length) {
    candidateValues.push(...puzzle.givens.map((entry) => entry.value));
  }
  if (puzzle.solution?.length) {
    candidateValues.push(...(puzzle.solution?.map((entry) => entry.value) ?? []));
  }

  if (candidateValues.length === 0) {
    return {
      startValue: DEFAULT_START_VALUE,
      endValue: puzzle.size * puzzle.size,
    };
  }

  let minValue = candidateValues[0];
  let maxValue = candidateValues[0];
  for (let i = 1; i < candidateValues.length; i++) {
    const value = candidateValues[i];
    if (value < minValue) minValue = value;
    if (value > maxValue) maxValue = value;
  }

  return {
    startValue: minValue,
    endValue: maxValue,
  };
}
