// Lightweight sequence state snapshot utility for guided sequence flow
// Constitution: no external deps; pure function.

export interface SequenceState {
  anchorValue: number | null;
  nextTarget: number | null;
  legalTargets: { row: number; col: number }[];
  chainEndValue: number | null;
  chainLength: number;
  nextTargetChangeReason: 'placement' | 'anchor-change' | 'tail-removal' | 'non-tail-removal' | 'neutral' | string;
  guideEnabled: boolean;
}

export interface SequenceSnapshot {
  timestamp: number;
  anchorValue: number | null;
  nextTarget: number | null;
  chainEndValue: number | null;
  chainLength: number;
  reason: string;
  legalCount: number;
  guideEnabled: boolean;
}

export function captureSequenceSnapshot(state: SequenceState): SequenceSnapshot {
  return {
    timestamp: Date.now(),
    anchorValue: state.anchorValue,
    nextTarget: state.nextTarget,
    chainEndValue: state.chainEndValue,
    chainLength: state.chainLength,
    reason: state.nextTargetChangeReason,
    legalCount: state.legalTargets.length,
    guideEnabled: state.guideEnabled,
  };
}

// Optional debug formatter
export function formatSnapshot(s: SequenceSnapshot): string {
  return `[seq] t=${s.timestamp} anchor=${s.anchorValue ?? '-'} next=${s.nextTarget ?? '-'} chainEnd=${s.chainEndValue ?? '-'} len=${s.chainLength} reason=${s.reason} legal=${s.legalCount} guide=${s.guideEnabled}`;
}

// Example usage (dev only):
// console.debug(formatSnapshot(captureSequenceSnapshot(sequenceState)));
