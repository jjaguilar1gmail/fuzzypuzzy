/**
 * Core types for Guided Sequence Flow
 * Based on specs/001-guided-sequence-flow/data-model.md
 */

/**
 * Grid position coordinates
 */
export interface Position {
  row: number;
  col: number;
}

/**
 * Reason for the latest nextTarget computation change
 */
export type NextTargetChangeReason =
  | 'placement'
  | 'anchor-change'
  | 'tail-removal'
  | 'non-tail-removal'
  | 'neutral';

/**
 * Direction to advance sequence placements
 */
export type SequenceDirection = 'forward' | 'backward';

/**
 * Individual board cell state
 */
export interface BoardCell {
  /** Grid coordinates */
  position: Position;
  /** Placed number or empty */
  value: number | null;
  /** True if original clue (immutable) */
  given: boolean;
  /** True if cell unusable */
  blocked: boolean;
  /** Derived: legal placement candidate (computed each render) */
  highlighted: boolean;
  /** Derived: currently selected anchor (at most one cell) */
  anchor: boolean;
  /** Indicates user placed illegal number (transient in MVP) */
  mistake: boolean;
}

/**
 * Current guided sequence state
 */
export interface SequenceState {
  /** Current selected value n */
  anchorValue: number | null;
  /** Position of anchor cell */
  anchorPos: Position | null;
  /** Value v+1 if chain can extend; null if neutral */
  nextTarget: number | null;
  /** Array of legal empty adjacent cells if nextTarget exists */
  legalTargets: Position[];
  /** "Show Guide" toggle */
  guideEnabled: boolean;
  /** Whether to step up or down the sequence */
  stepDirection: SequenceDirection;
  /** Highest contiguous value in primary chain */
  chainEndValue: number | null;
  /** Length of contiguous chain */
  chainLength: number;
  /** Cause of latest nextTarget recompute */
  nextTargetChangeReason: NextTargetChangeReason;
}

/**
 * Action type for undo/redo
 */
export type UndoActionType = 'PLACE' | 'REMOVE';

/**
 * Undo/redo action record
 */
export interface UndoAction {
  /** Action category */
  type: UndoActionType;
  /** Cell affected */
  position: Position;
  /** Number placed or removed */
  value: number;
  /** Snapshot for restoration of anchor/next target */
  previousSequenceSnapshot: Partial<SequenceState>;
  /** Epoch milliseconds */
  timestamp: number;
  /** Reason associated with this action outcome */
  changeReason: NextTargetChangeReason;
}

/**
 * Mistake attempt classification
 */
export type MistakeReason = 'not-adjacent' | 'occupied' | 'no-target';

/**
 * Mistake event record
 */
export interface MistakeEvent {
  /** Where invalid attempt occurred */
  position: Position;
  /** Value the system expected to place */
  attemptedValue: number;
  /** Classification */
  reason: MistakeReason;
  /** Epoch milliseconds */
  timestamp: number;
}

/**
 * Highlight intensity level
 */
export type HighlightIntensity = 'low' | 'medium' | 'high';

/**
 * Player preferences (persisted to local storage)
 */
export interface PlayerSettings {
  /** Persisted preference */
  guideEnabled: boolean;
  /** Visual strength */
  highlightIntensity: HighlightIntensity;
  /** Accessibility toggle */
  highContrast: boolean;
}

/**
 * Result of chain detection algorithm
 */
export interface ChainInfo {
  /** Highest contiguous value in chain */
  chainEndValue: number | null;
  /** Length of contiguous chain */
  chainLength: number;
  /** Next candidate value if extension possible */
  nextCandidate: number | null;
}

/**
 * Result of removal classification
 */
export type RemovalClassification = 'tail-removal' | 'non-tail-removal';

/**
 * API surface for guided sequence flow hook
 */
export interface GuidedSequenceFlowAPI {
  /** Current sequence state */
  state: SequenceState;
  /** 2D board grid */
  board: BoardCell[][];
  /** Select a cell with a value as anchor */
  selectAnchor: (pos: Position) => void;
  /** Place next target value at position */
  placeNext: (pos: Position) => void;
  /** Remove value from cell */
  removeCell: (pos: Position) => void;
  /** Clear all non-given entries and return to the original givens */
  clearBoard: () => void;
  /** Toggle guide visibility */
  toggleGuide: (enabled: boolean) => void;
  /** Change step direction */
  setStepDirection: (direction: SequenceDirection) => void;
  /** Undo last action */
  undo: () => void;
  /** Redo last undone action */
  redo: () => void;
  /** Can undo */
  canUndo: boolean;
  /** Can redo */
  canRedo: boolean;
  /** Recent mistakes (ring buffer size 20) */
  recentMistakes: MistakeEvent[];
}
