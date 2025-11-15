import { useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@/state/gameStore';
import { formatDuration } from '@/components/HUD/SessionStats';

interface CompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CompletionModal({ isOpen, onClose }: CompletionModalProps) {
  const puzzle = useGameStore((state) => state.puzzle);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const moveCount = useGameStore((state) => state.moveCount);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const isCorrect = completionStatus !== 'incorrect';

  const handlePrimaryAction = useCallback(() => {
    if (isCorrect) {
      useGameStore.getState().resetPuzzle();
    }
    onClose();
  }, [isCorrect, onClose]);

  const handleSecondaryAction = useCallback(() => {
    if (!isCorrect) {
      useGameStore.getState().resetPuzzle();
    }
    onClose();
  }, [isCorrect, onClose]);

  useEffect(() => {
    if (isOpen) {
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="fixed inset-0 flex items-center justify-center z-50 p-4"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.8 }}
            transition={{ duration: 0.15, type: 'spring' }}
          >
            <div
              className="bg-white rounded-lg shadow-xl p-8 max-w-md w-full"
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-labelledby="completion-title"
              aria-modal="true"
            >
              <h2
                id="completion-title"
                className={`text-3xl font-bold text-center mb-4 ${
                  isCorrect ? 'text-green-600' : 'text-red-600'
                }`}
              >
                {isCorrect ? 'Puzzle Complete!' : 'Incorrect Solution'}
              </h2>

              <p
                className={`text-center mb-6 ${
                  isCorrect ? 'text-gray-600' : 'text-red-600'
                }`}
              >
                {isCorrect
                  ? 'Great job! Every cell matches the official solution.'
                  : 'Your filled board does not match the official solution. Review the numbers and try again.'}
              </p>

              <div className="space-y-4 mb-8">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Puzzle:</span>
                  <span className="font-semibold">
                    {puzzle ? `${puzzle.size}x${puzzle.size} - ${puzzle.difficulty}` : 'N/A'}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Time:</span>
                  <span className="font-semibold">{formatDuration(elapsedMs)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Moves:</span>
                  <span className="font-semibold">{moveCount}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <motion.button
                  onClick={handlePrimaryAction}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isCorrect ? 'Play Again' : 'Keep Editing'}
                </motion.button>

                <motion.button
                  onClick={handleSecondaryAction}
                  className={`flex-1 px-6 py-3 rounded-lg font-medium transition-colors ${
                    isCorrect
                      ? 'bg-blue-500 text-white hover:bg-blue-600'
                      : 'bg-red-500 text-white hover:bg-red-600'
                  }`}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  {isCorrect ? 'Close' : 'Reset Puzzle'}
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
