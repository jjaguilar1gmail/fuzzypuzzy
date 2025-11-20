import { useEffect } from 'react';
import { Puzzle } from '@/domain/puzzle';
import { useGameStore } from '@/state/gameStore';

export function formatDuration(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
}

export function getFillableCellCount(puzzle: Puzzle | null): number | null {
  if (!puzzle) return null;
  const totalCells = puzzle.size * puzzle.size;
  const givenCount = puzzle.givens?.length ?? 0;
  const fillable = totalCells - givenCount;
  return fillable > 0 ? fillable : null;
}

export function formatMoveStat(moveCount: number, puzzle: Puzzle | null): string {
  const fillableCells = getFillableCellCount(puzzle);
  if (fillableCells !== null && fillableCells > 0) {
    return `${moveCount} / ${fillableCells}`;
  }
  return `${moveCount}`;
}

export function SessionStats() {
  const puzzle = useGameStore((state) => state.puzzle);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const moveCount = useGameStore((state) => state.moveCount);
  const timerRunning = useGameStore((state) => state.timerRunning);
  const tickTimer = useGameStore((state) => state.tickTimer);

  useEffect(() => {
    if (!timerRunning) return;
    const id = window.setInterval(() => {
      tickTimer();
    }, 1000);
    return () => window.clearInterval(id);
  }, [timerRunning, tickTimer]);

  if (!puzzle) return null;

  const moveDisplay = formatMoveStat(moveCount, puzzle);

  return (
    <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-copy-muted">
      <div className="flex items-center gap-1 px-4 py-1.5 rounded-full border border-border bg-surface-elevated/80 shadow-sm">
        <span className="font-medium text-copy">Time</span>
        <span className="font-semibold text-copy">{formatDuration(elapsedMs)}</span>
      </div>
      <div className="flex items-center gap-1 px-4 py-1.5 rounded-full border border-border bg-surface-elevated/80 shadow-sm">
        <span className="font-medium text-copy">Moves</span>
        <span className="font-semibold text-copy">{moveDisplay}</span>
      </div>
    </div>
  );
}
