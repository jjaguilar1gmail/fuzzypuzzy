/**
 * Guided Sequence Flow - Public API
 * Entry point for all sequence flow functionality
 */

// Main hook
export { useGuidedSequenceFlow } from './useGuidedSequenceFlow';

// Types
export type {
  Position,
  BoardCell,
  SequenceState,
  UndoAction,
  UndoActionType,
  MistakeEvent,
  MistakeReason,
  PlayerSettings,
  HighlightIntensity,
  NextTargetChangeReason,
  ChainInfo,
  RemovalClassification,
  GuidedSequenceFlowAPI,
} from './types';

// Utilities (for testing and advanced usage)
export { getAdjacents, getLegalAdjacents, positionsEqual, areAdjacent } from './adjacency';
export { computeChain, buildValuesMap } from './chain';
export { deriveNextTarget, computeLegalTargets } from './nextTarget';
export { classifyRemoval } from './removal';
export { UndoRedoStack, createSequenceSnapshot, restoreSequenceSnapshot } from './undoRedo';
export { validatePlacement, validateRemoval, isInvalidEmptyCellClick } from './mistakes';
