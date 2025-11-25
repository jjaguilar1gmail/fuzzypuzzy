import { useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Puzzle, Pack } from '@/domain/puzzle';
import { loadPuzzle, loadPack } from '@/lib/loaders/packs';
import { useGameStore } from '@/state/gameStore';
import { useProgressStore } from '@/state/progressStore';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import CompletionModal from '@/components/HUD/CompletionModal';
import { SessionStats } from '@/components/HUD/SessionStats';

/**
 * Individual puzzle page within a pack (US2).
 * Reuses Grid/Palette components from US1 with pack navigation and progress tracking.
 */
export default function PackPuzzlePage() {
  const router = useRouter();
  const { packId, puzzleId } = router.query;
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [pack, setPack] = useState<Pack | null>(null);
  const [currentIndex, setCurrentIndex] = useState<number>(-1);
  
  const loadPuzzleToStore = useGameStore((state) => state.loadPuzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore(
    (state) => state.dismissCompletionStatus
  );
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const moveCount = useGameStore((state) => state.moveCount);
  
  const recordCompletion = useProgressStore((state) => state.recordCompletion);
  const recordProgress = useProgressStore((state) => state.recordProgress);
  const isCompleted = useProgressStore((state) => state.isCompleted);

  useEffect(() => {
    if (!packId || typeof packId !== 'string') return;
    if (!puzzleId || typeof puzzleId !== 'string') return;
    
    const loadData = async () => {
      try {
        const [puzzle, packData] = await Promise.all([
          loadPuzzle(packId, puzzleId),
          loadPack(packId),
        ]);
        
        loadPuzzleToStore(puzzle);
        setPack(packData);
        
        const index = packData.puzzles.indexOf(puzzleId);
        setCurrentIndex(index);
        
        // Record that user started/continued this puzzle
        recordProgress(packId, puzzleId);
        
        setLoading(false);
      } catch (err: any) {
        setError(err.message);
        setLoading(false);
      }
    };

    loadData();
  }, [packId, puzzleId, loadPuzzleToStore, recordProgress]);

  useEffect(() => {
    if (
      completionStatus === 'success' &&
      packId &&
      typeof packId === 'string' &&
      puzzleId &&
      typeof puzzleId === 'string'
    ) {
      recordCompletion(packId, puzzleId, moveCount, elapsedMs);
    }
  }, [completionStatus, packId, puzzleId, elapsedMs, moveCount, recordCompletion]);

  const handleNavigate = useCallback((direction: 'prev' | 'next') => {
    if (!pack || currentIndex === -1) return;
    
    const newIndex = direction === 'prev' ? currentIndex - 1 : currentIndex + 1;
    if (newIndex < 0 || newIndex >= pack.puzzles.length) return;
    
    const newPuzzleId = pack.puzzles[newIndex];
    router.push(`/packs/${packId}/puzzles/${newPuzzleId}`);
  }, [pack, currentIndex, packId, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <p>Loading puzzle...</p>
      </div>
    );
  }

  if (error || !pack) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-center">
          <p className="text-red-600 mb-4">Error: {error || 'Failed to load puzzle'}</p>
          <Link href={`/packs/${packId}`} className="text-primary hover:underline">
            ← Back to pack
          </Link>
        </div>
      </div>
    );
  }

  const hasPrev = currentIndex > 0;
  const hasNext = currentIndex < pack.puzzles.length - 1;
  const completed = typeof packId === 'string' && typeof puzzleId === 'string' 
    ? isCompleted(packId, puzzleId) 
    : false;

  return (
    <main className="min-h-screen p-4 md:p-8">
      <div className="max-w-6xl mx-auto">
        {/* Header with navigation */}
        <div className="mb-6 flex items-center justify-between flex-wrap gap-4">
          <Link
            href={`/packs/${packId}`}
            className="text-primary hover:underline inline-flex items-center gap-2"
          >
            <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 19l-7-7 7-7" />
            </svg>
            Back to {pack.title}
          </Link>

          <div className="flex items-center gap-3">
            <span className="text-sm text-gray-600">
              Puzzle {currentIndex + 1} of {pack.puzzles.length}
            </span>
            {completed && (
              <span className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded font-medium">
                ✓ Completed
              </span>
            )}
          </div>
        </div>

        <div className="mb-6 flex justify-center">
          <SessionStats />
        </div>

        {/* Main game area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.15 }}
          className="flex justify-center"
        >
          <GuidedGrid />
        </motion.div>

        {/* Navigation controls */}
        <div className="mt-8 flex justify-between items-center">
          <button
            onClick={() => handleNavigate('prev')}
            disabled={!hasPrev}
            className="px-6 py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed bg-gray-200 hover:bg-gray-300 disabled:hover:bg-gray-200"
            aria-label="Previous puzzle"
          >
            ← Previous
          </button>

          <button
            onClick={() => handleNavigate('next')}
            disabled={!hasNext}
            className="px-6 py-3 rounded-lg font-medium transition-all disabled:opacity-50 disabled:cursor-not-allowed bg-primary text-primary-foreground hover:bg-primary-strong disabled:hover:bg-primary"
            aria-label="Next puzzle"
          >
            Next →
          </button>
        </div>

        {/* Completion modal */}
        <CompletionModal
          isOpen={completionStatus !== null}
          onClose={dismissCompletionStatus}
        />
      </div>
    </main>
  );
}
