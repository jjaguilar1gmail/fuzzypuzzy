/**
 * Screen reader announcements for sequence state changes
 * Provides accessible feedback for anchor selection, placement, and errors
 */

import { useEffect, useRef } from 'react';
import type { SequenceState, MistakeEvent } from '../types';

interface SequenceAnnouncerProps {
  /** Current sequence state */
  state: SequenceState;
  /** Recent mistakes for error announcements */
  recentMistakes?: MistakeEvent[];
}

/**
 * Generates human-readable announcement for current state
 */
function describeNextTarget(state: SequenceState): string {
  const legalCount = state.legalTargets.length;
  const legalText = `${legalCount} legal ${legalCount === 1 ? 'position' : 'positions'}`;
  const deltaLabel = state.stepDirection === 'forward' ? '+1' : '-1';
  return `Next ${deltaLabel} is ${state.nextTarget}. ${legalText} available.`;
}

function generateAnnouncement(
  state: SequenceState,
  prevState: SequenceState | null,
  latestMistake: MistakeEvent | null
): string {
  // Mistake announcements take priority
  if (latestMistake) {
    const reasonMessages: Record<string, string> = {
      'no-target': 'No target set. Please select an anchor first.',
      'occupied-cell': 'Cell is already occupied.',
      'not-adjacent': 'Cell must be adjacent to the anchor.',
    };
    const reasonText = reasonMessages[latestMistake.reason] || 'Invalid placement.';
    return `Invalid placement. ${reasonText}`;
  }

  // Anchor change
  if (state.anchorValue !== prevState?.anchorValue && state.anchorValue !== null) {
    const targetText = state.nextTarget
      ? describeNextTarget(state)
      : 'No legal moves available from this anchor.';
    return `Anchor set to ${state.anchorValue}. ${targetText}`;
  }

  // Neutral state (no anchor)
  if (state.anchorValue === null && state.nextTarget === null) {
    if (state.nextTargetChangeReason === 'tail-removal') {
      return `Tail removed. Chain now ends at ${state.chainEndValue}. Select a chain value to continue.`;
    }
    return 'Select a number to start guided placement.';
  }

  // Successful placement
  if (
    prevState &&
    prevState.nextTarget !== null &&
    state.nextTarget !== prevState.nextTarget &&
    state.nextTargetChangeReason === 'placement'
  ) {
    const prevTarget = prevState.nextTarget;
    const nextText = state.nextTarget
      ? describeNextTarget(state)
      : 'Sequence complete.';
    return `Placed ${prevTarget}. ${nextText}`;
  }

  // Note: undo/redo use existing change reasons ('placement', 'neutral', etc.)
  // so they don't need separate handling here

  return '';
}

/**
 * Invisible live region for screen reader announcements
 * Announces state changes, placements, and errors
 */
export function SequenceAnnouncer({ state, recentMistakes = [] }: SequenceAnnouncerProps) {
  const prevStateRef = useRef<SequenceState | null>(null);
  const prevMistakeCountRef = useRef(0);
  const announcementRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const prevState = prevStateRef.current;
    
    // Detect new mistake
    const latestMistake = recentMistakes.length > prevMistakeCountRef.current
      ? recentMistakes[recentMistakes.length - 1]
      : null;

    // Generate announcement
    const announcement = generateAnnouncement(state, prevState, latestMistake);

    // Update live region
    if (announcement && announcementRef.current) {
      announcementRef.current.textContent = announcement;
    }

    // Update refs
    prevStateRef.current = state;
    prevMistakeCountRef.current = recentMistakes.length;
  }, [
    state.anchorValue,
    state.nextTarget,
    state.nextTargetChangeReason,
    state.legalTargets.length,
    state.stepDirection,
    recentMistakes.length,
  ]);

  return (
    <div
      ref={announcementRef}
      role="status"
      aria-live="polite"
      aria-atomic="true"
      className="sr-only"
      style={{
        position: 'absolute',
        width: '1px',
        height: '1px',
        padding: 0,
        margin: '-1px',
        overflow: 'hidden',
        clip: 'rect(0, 0, 0, 0)',
        whiteSpace: 'nowrap',
        border: 0,
      }}
    />
  );
}

/**
 * CSS class for screen-reader-only content
 * Add to global stylesheet:
 * 
 * ```css
 * .sr-only {
 *   position: absolute;
 *   width: 1px;
 *   height: 1px;
 *   padding: 0;
 *   margin: -1px;
 *   overflow: hidden;
 *   clip: rect(0, 0, 0, 0);
 *   white-space: nowrap;
 *   border: 0;
 * }
 * ```
 */
