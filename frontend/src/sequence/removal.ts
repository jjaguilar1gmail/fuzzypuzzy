/**
 * Removal classification logic for guided sequence flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

import type { RemovalClassification } from './types';

/**
 * Classify a removal as tail or non-tail
 * @param prevChainEnd - Previous chain end value before removal
 * @param removedValue - Value that was removed
 * @returns Classification of removal type
 */
export function classifyRemoval(
  prevChainEnd: number | null,
  removedValue: number
): RemovalClassification {
  if (prevChainEnd === null) {
    return 'non-tail-removal';
  }

  return removedValue === prevChainEnd ? 'tail-removal' : 'non-tail-removal';
}
