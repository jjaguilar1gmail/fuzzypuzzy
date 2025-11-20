import { useGameStore } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo, useState, useEffect } from 'react';
import { gridPalette, statusPalette } from '@/styles/colorTokens';

const GRID_SAFE_MARGIN = 32;

const Grid = memo(function Grid() {
  const grid = useGameStore((state) => state.grid);
  const selectedCell = useGameStore((state) => state.selectedCell);
  const selectCell = useGameStore((state) => state.selectCell);

  const [viewportWidth, setViewportWidth] = useState(() =>
    typeof window !== 'undefined' ? window.innerWidth : 1024
  );

  useEffect(() => {
    if (typeof window === 'undefined') return;
    const handleResize = () => setViewportWidth(window.innerWidth);
    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

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

  const baseRenderSize = totalSize;
  const availableWidth =
    viewportWidth > GRID_SAFE_MARGIN
      ? viewportWidth - GRID_SAFE_MARGIN
      : viewportWidth;
  const renderSize =
    availableWidth && availableWidth > 0
      ? Math.min(baseRenderSize, availableWidth)
      : baseRenderSize;

  return (
    <div
      className="relative"
      style={{
        width: renderSize,
        height: renderSize,
      }}
    >
      <svg
        width="100%"
        height="100%"
        viewBox={`0 0 ${totalSize} ${totalSize}`}
        className="mx-auto"
        role="grid"
        aria-label="Hidato puzzle grid"
        preserveAspectRatio="xMidYMid meet"
      >
      {grid.cells.map((row, r) =>
        row.map((cell, c) => {
          const x = c * (cellSize + gap);
          const y = r * (cellSize + gap);
          const isSelected =
            selectedCell?.row === r && selectedCell?.col === c;
          const isGiven = cell.given;
          const hasValue = cell.value !== null;

          const fillColor = isGiven
            ? gridPalette.given
            : isSelected
            ? gridPalette.selected
            : gridPalette.cellSurface;
          const strokeColor = isSelected
            ? statusPalette.primary
            : statusPalette.border;

          return (
            <g key={`${r}-${c}`}>
              {/* Cell background */}
              <motion.rect
                x={x}
                y={y}
                width={cellSize}
                height={cellSize}
                fill={fillColor}
                stroke={strokeColor}
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
                    fill={isGiven ? statusPalette.text : statusPalette.primary}
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
                        fill={statusPalette.textMuted}
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
    </div>
  );
});

export default Grid;
