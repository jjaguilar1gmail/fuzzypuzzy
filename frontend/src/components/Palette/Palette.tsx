import { useGameStore } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo } from 'react';

const Palette = memo(function Palette() {
  const puzzle = useGameStore((state) => state.puzzle);
  const pencilMode = useGameStore((state) => state.pencilMode);
  const togglePencilMode = useGameStore((state) => state.togglePencilMode);
  const placeValue = useGameStore((state) => state.placeValue);
  const undo = useGameStore((state) => state.undo);
  const redo = useGameStore((state) => state.redo);
  const undoStack = useGameStore((state) => state.undoStack);
  const redoStack = useGameStore((state) => state.redoStack);

  // Memoize number grid calculations
  const numberGrid = useMemo(() => {
    if (!puzzle) return null;
    const maxValue = puzzle.size * puzzle.size;
    const numbers = Array.from({ length: maxValue }, (_, i) => i + 1);
    const gridCols = Math.min(10, maxValue);
    return { numbers, gridCols };
  }, [puzzle?.size]);

  if (!puzzle || !numberGrid) return null;

  const { numbers, gridCols } = numberGrid;

  return (
    <div className="flex flex-col gap-4 items-center">
      {/* Toolbar */}
      <div className="flex gap-2">
        <motion.button
          onClick={togglePencilMode}
          aria-pressed={pencilMode}
          className={`px-4 py-3 min-h-[44px] rounded-lg font-medium transition-colors ${
            pencilMode
              ? 'bg-primary text-primary-foreground'
              : 'bg-surface-muted text-copy hover:bg-surface'
          }`}
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
        >
          ✏️ Pencil {pencilMode ? 'ON' : 'OFF'}
        </motion.button>

        <motion.button
          onClick={undo}
          disabled={undoStack.length === 0}
          className="px-4 py-3 min-h-[44px] rounded-lg bg-surface-muted text-copy hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Undo"
        >
          ↶ Undo
        </motion.button>

        <motion.button
          onClick={redo}
          disabled={redoStack.length === 0}
          className="px-4 py-3 min-h-[44px] rounded-lg bg-surface-muted text-copy hover:bg-surface disabled:opacity-50 disabled:cursor-not-allowed"
          whileHover={{ scale: 1.05 }}
          whileTap={{ scale: 0.95 }}
          aria-label="Redo"
        >
          ↷ Redo
        </motion.button>
      </div>

      {/* Number grid */}
      <div
        className="grid gap-2"
        style={{
          gridTemplateColumns: `repeat(${gridCols}, minmax(0, 1fr))`,
        }}
        role="toolbar"
        aria-label="Number palette"
      >
        {numbers.map((num) => (
          <motion.button
            key={num}
            onClick={() => placeValue(num)}
            className="w-12 h-12 rounded-lg bg-surface border-2 border-border hover:border-primary hover:bg-primary-muted font-semibold text-lg transition-colors"
            whileHover={{ scale: 1.1 }}
            whileTap={{ scale: 0.9 }}
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.1, delay: num * 0.01 }}
            aria-label={`Place ${num}`}
          >
            {num}
          </motion.button>
        ))}
      </div>
    </div>
  );
});

export default Palette;
