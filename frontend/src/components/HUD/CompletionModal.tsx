import { useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useGameStore } from '@/state/gameStore';

interface CompletionModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function CompletionModal({ isOpen, onClose }: CompletionModalProps) {
  const puzzle = useGameStore((state) => state.puzzle);
  const elapsedMs = useGameStore((state) => state.elapsedMs);
  const mistakes = useGameStore((state) => state.mistakes);
  const undoStack = useGameStore((state) => state.undoStack);

  useEffect(() => {
    if (isOpen) {
      // Optional: play completion sound
      const handleEscape = (e: KeyboardEvent) => {
        if (e.key === 'Escape') onClose();
      };
      document.addEventListener('keydown', handleEscape);
      return () => document.removeEventListener('keydown', handleEscape);
    }
  }, [isOpen, onClose]);

  const formatTime = (ms: number) => {
    const seconds = Math.floor(ms / 1000);
    const minutes = Math.floor(seconds / 60);
    const remainingSeconds = seconds % 60;
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`;
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            className="fixed inset-0 bg-black/50 z-40"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          {/* Modal */}
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
                className="text-3xl font-bold text-center mb-6 text-green-600"
              >
                🎉 Puzzle Complete!
              </h2>

              <div className="space-y-4 mb-8">
                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Puzzle:</span>
                  <span className="font-semibold">
                    {puzzle?.size}×{puzzle?.size} · {puzzle?.difficulty}
                  </span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Time:</span>
                  <span className="font-semibold">{formatTime(elapsedMs)}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Moves:</span>
                  <span className="font-semibold">{undoStack.length}</span>
                </div>

                <div className="flex justify-between items-center">
                  <span className="text-gray-600">Mistakes:</span>
                  <span className="font-semibold">{mistakes}</span>
                </div>
              </div>

              <div className="flex gap-3">
                <motion.button
                  onClick={() => {
                    useGameStore.getState().resetPuzzle();
                    onClose();
                  }}
                  className="flex-1 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium hover:bg-gray-300 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Play Again
                </motion.button>

                <motion.button
                  onClick={onClose}
                  className="flex-1 px-6 py-3 bg-blue-500 text-white rounded-lg font-medium hover:bg-blue-600 transition-colors"
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  Close
                </motion.button>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
