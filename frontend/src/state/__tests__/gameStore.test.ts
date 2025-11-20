import { describe, beforeEach, it, expect } from 'vitest';
import { useGameStore } from '@/state/gameStore';

describe('gameStore.reopenCompletionSummary', () => {
  beforeEach(() => {
    useGameStore.setState({
      completionStatus: null,
      isComplete: false,
    });
  });

  it('does nothing when the puzzle is not complete', () => {
    useGameStore.getState().reopenCompletionSummary();
    expect(useGameStore.getState().completionStatus).toBeNull();
  });

  it('reapplies the success status when the puzzle is complete', () => {
    useGameStore.setState({ isComplete: true, completionStatus: null });

    useGameStore.getState().reopenCompletionSummary();

    expect(useGameStore.getState().completionStatus).toBe('success');
  });
});

