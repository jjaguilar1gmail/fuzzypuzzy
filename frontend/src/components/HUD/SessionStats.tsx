import { useEffect } from 'react';
import { useGameStore } from '@/state/gameStore';

export function formatDuration(ms: number): string {
  const totalSeconds = Math.floor(ms / 1000);
  const minutes = Math.floor(totalSeconds / 60);
  const seconds = totalSeconds % 60;
  return `${minutes}:${seconds.toString().padStart(2, '0')}`;
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

  return (
    <div className="flex flex-wrap items-center justify-center gap-3 text-sm text-gray-600">
      <div className="flex items-center gap-1 px-4 py-1.5 rounded-full border border-gray-200 bg-white/80 shadow-sm">
        <span className="font-medium text-gray-800">Time</span>
        <span className="font-semibold text-gray-900">{formatDuration(elapsedMs)}</span>
      </div>
      <div className="flex items-center gap-1 px-4 py-1.5 rounded-full border border-gray-200 bg-white/80 shadow-sm">
        <span className="font-medium text-gray-800">Moves</span>
        <span className="font-semibold text-gray-900">{moveCount}</span>
      </div>
    </div>
  );
}
