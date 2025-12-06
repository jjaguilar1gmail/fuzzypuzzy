import { useGameStore } from '@/state/gameStore';
import { motion } from 'framer-motion';
import { memo, useMemo, useState, useEffect } from 'react';
import { gridPalette, statusPalette } from '@/styles/colorTokens';
import { deriveSymbolRange } from '@/symbolSets/valueRange';
import { getDefaultSymbolSet } from '@/symbolSets/registry';
import { getPaletteBColorContext } from '@/symbolSets/paletteBShapeSymbolSet';

const GRID_SAFE_MARGIN = 32;

const activeSymbolSet = getDefaultSymbolSet();
const paletteBSymbolSetIds = new Set([
  'paletteB-shapes',
  'paletteB-dice',
  'paletteB-dice-growing',
]);

const Grid = memo(function Grid() {
  const grid = useGameStore((state) => state.grid);
  const gridSize = grid?.size ?? 0;
  const puzzle = useGameStore((state) => state.puzzle);
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
    if (!gridSize) return null;
    const cellSize = 60;
    const gap = 2;
    const totalSize = gridSize * cellSize + (gridSize - 1) * gap;
    return { cellSize, gap, totalSize };
  }, [gridSize]);

  const { startValue, endValue } = useMemo(() => {
    return deriveSymbolRange(puzzle, gridSize);
  }, [puzzle, gridSize]);

  if (!grid || !dimensions) return null;

  const { cellSize, gap, totalSize } = dimensions;
  const totalCells = gridSize * gridSize;
  const isPaletteBSet = paletteBSymbolSetIds.has(activeSymbolSet.id);

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
          const isChainStart = cell.value === startValue;
          const isChainEnd = cell.value === endValue;
          const chainRole = isChainStart ? 'start' : isChainEnd ? 'end' : null;
          let badgePath: string | null = null;
          if (chainRole === 'start') {
            const badgeInset = 2;
            const badgeSize = cellSize * 0.34;
            const startX = x + badgeInset;
            const startY = y + badgeInset;
            const cornerRadius = 3;
            badgePath = `M ${startX} ${startY + cornerRadius} Q ${startX} ${startY} ${
              startX + cornerRadius
            } ${startY} L ${startX + badgeSize} ${startY} L ${startX} ${
              startY + badgeSize
            } Z`;
          } else if (chainRole === 'end') {
            const badgeInset = 2;
            const badgeSize = cellSize * 0.34;
            const startX = x + cellSize - badgeInset;
            const startY = y + badgeInset;
            const cornerRadius = 3;
            badgePath = `M ${startX} ${startY + cornerRadius} Q ${startX} ${startY} ${
              startX - cornerRadius
            } ${startY} L ${startX - badgeSize} ${startY} L ${startX} ${
              startY + badgeSize
            } Z`;
          }
          const linearIndex = cell.value !== null ? cell.value - 1 : undefined;
          const paletteContext =
            isPaletteBSet && cell.value !== null
              ? getPaletteBColorContext(
                  cell.value,
                  totalCells,
                  typeof linearIndex === 'number' ? linearIndex : undefined
                )
              : null;
          const symbolProps = {
            value: cell.value,
            isGiven,
            isSelected,
            isError: false,
            isEmpty: !hasValue,
            isGuideTarget: false,
            cellSize,
            isChainStart,
            isChainEnd,
            linearIndex,
            totalCells,
          };
          const symbolElement = activeSymbolSet.renderCell(symbolProps);
          const badgeFillColor =
            chainRole && paletteContext
              ? paletteContext.circleColor
              : chainRole === 'start'
              ? statusPalette.primary
              : chainRole === 'end'
              ? statusPalette.success
              : null;

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
              {symbolElement && (
                <g transform={`translate(${x} ${y})`}>{symbolElement}</g>
              )}

              {/* Given underline */}
              {isGiven && (
                <rect
                  x={x + 6}
                  y={y + cellSize - 4}
                  width={cellSize - 12}
                  height={2}
                  fill={statusPalette.text}
                  rx={1}
                  pointerEvents="none"
                  opacity={0.85}
                />
              )}

              {/* Chain baseline overlay */}
              {badgePath && badgeFillColor && (
                <path
                  d={badgePath}
                  fill={badgeFillColor}
                  fillOpacity={0.75}
                  stroke="none"
                  pointerEvents="none"
                />
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
