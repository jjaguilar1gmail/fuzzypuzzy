import { useGameStore } from '@/state/gameStore';
import { getCell } from '@/domain/grid';
import { motion } from 'framer-motion';
import { memo, useMemo } from 'react';

const Grid = memo(function Grid() {
  const grid = useGameStore((state) => state.grid);
  const selectedCell = useGameStore((state) => state.selectedCell);
  const selectCell = useGameStore((state) => state.selectCell);

  // Memoize grid dimensions to prevent recalculation
  const dimensions = useMemo(() => {
    if (!grid) return null;
    const cellSize = 60;
    const gap = 2;
    const totalSize = grid.size * cellSize + (grid.size - 1) * gap;
    return { cellSize, gap, totalSize };
  }, [grid?.size]);

  if (!grid || !dimensions) return null;

  const { cellSize, gap, totalSize } = dimensions;

  return (
    <svg
      width={totalSize}
      height={totalSize}
      viewBox={`0 0 ${totalSize} ${totalSize}`}
      className="mx-auto"
      role="grid"
      aria-label="Hidato puzzle grid"
    >
      {grid.cells.map((row, r) =>
        row.map((cell, c) => {
          const x = c * (cellSize + gap);
          const y = r * (cellSize + gap);
          const isSelected =
            selectedCell?.row === r && selectedCell?.col === c;
          const isGiven = cell.given;
          const hasValue = cell.value !== null;

          return (
            <g key={`${r}-${c}`}>
              {/* Cell background */}
              <motion.rect
                x={x}
                y={y}
                width={cellSize}
                height={cellSize}
                fill={
                  isGiven
                    ? 'rgb(229, 231, 235)'
                    : isSelected
                    ? 'rgb(219, 234, 254)'
                    : 'white'
                }
                stroke={isSelected ? 'rgb(14, 165, 233)' : 'rgb(203, 213, 225)'}
                strokeWidth={isSelected ? 3 : 1}
                rx={4}
                onClick={() => selectCell(r, c)}
                className="cursor-pointer transition-colors"
                role="gridcell"
                aria-label={`Cell ${r},${c}${hasValue ? ` value ${cell.value}` : ' empty'}`}
                tabIndex={0}
                onKeyDown={(e) => {
                  if (e.key === 'Enter' || e.key === ' ') {
                    selectCell(r, c);
                  }
                }}
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                transition={{ duration: 0.15, delay: (r + c) * 0.02 }}
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
              />

              {/* Cell value */}
              {hasValue && (
                <motion.text
                  x={x + cellSize / 2}
                  y={y + cellSize / 2}
                  textAnchor="middle"
                  dominantBaseline="central"
                  fontSize={isGiven ? 24 : 22}
                  fontWeight={isGiven ? 'bold' : 'normal'}
                  fill={isGiven ? 'rgb(0, 0, 0)' : 'rgb(59, 130, 246)'}
                  pointerEvents="none"
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ duration: 0.15, type: 'spring' }}
                >
                  {cell.value}
                </motion.text>
              )}

              {/* Candidate marks */}
              {!hasValue && cell.candidates.length > 0 && (
                <g>
                  {cell.candidates.slice(0, 4).map((candidate, idx) => {
                    const positions = [
                      { x: x + 12, y: y + 12 },
                      { x: x + cellSize - 12, y: y + 12 },
                      { x: x + 12, y: y + cellSize - 12 },
                      { x: x + cellSize - 12, y: y + cellSize - 12 },
                    ];
                    const pos = positions[idx];

                    return (
                      <text
                        key={idx}
                        x={pos.x}
                        y={pos.y}
                        textAnchor="middle"
                        dominantBaseline="central"
                        fontSize={10}
                        fill="rgb(107, 114, 128)"
                        pointerEvents="none"
                      >
                        {candidate}
                      </text>
                    );
                  })}
                </g>
              )}
            </g>
          );
        })
      )}
    </svg>
  );
});

export default Grid;
