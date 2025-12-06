import type { SymbolSet, SymbolSetPreviewProps } from './types';
import { getPaletteBColorContext } from './paletteBShapeSymbolSet';
import { getPipLayout } from './paletteBDiceUtils';

const CELL_CORNER_RADIUS = 4;
const MIN_PIP_RADIUS_RATIO = 0.06;
const MAX_PIP_RADIUS_RATIO = 0.235;
const MAX_SCALED_PIP_COUNT = 12;

const getScaledPipRadius = (pipCount: number, cellSize: number): number => {
  if (pipCount <= 1) {
    return cellSize * MIN_PIP_RADIUS_RATIO;
  }

  const capped = Math.min(pipCount, MAX_SCALED_PIP_COUNT);
  const denominator = MAX_SCALED_PIP_COUNT - 1;
  const t = denominator <= 0 ? 1 : (capped - 1) / denominator;
  const ratio =
    MIN_PIP_RADIUS_RATIO + t * (MAX_PIP_RADIUS_RATIO - MIN_PIP_RADIUS_RATIO);
  return cellSize * ratio;
};

const renderPaletteBDiceGrowingGlyph = (
  value: number,
  totalCells: number,
  cellSize: number,
  overrideLinearIndex?: number
) => {
  const context = getPaletteBColorContext(
    value,
    totalCells,
    overrideLinearIndex
  );
  const pipCount = Math.max(1, context.idxInBucket + 1);
  const pips = getPipLayout(pipCount);
  const pipRadius = getScaledPipRadius(pipCount, cellSize);

  return (
    <>
      <rect
        x={0}
        y={0}
        width={cellSize}
        height={cellSize}
        fill={context.bucketColor}
        rx={CELL_CORNER_RADIUS}
        ry={CELL_CORNER_RADIUS}
        pointerEvents="none"
      />
      {pips.map((pip, index) => (
        <circle
          key={`pip-${index}`}
          cx={pip.x * cellSize}
          cy={pip.y * cellSize}
          r={pipRadius}
          fill={context.circleColor}
          pointerEvents="none"
        />
      ))}
    </>
  );
};

export const paletteBDiceGrowingSymbolSet: SymbolSet = {
  id: 'paletteB-dice-growing',
  name: 'Palette B Dice (Growing Pips)',
  kind: 'shape',
  renderCell: ({
    value,
    isEmpty,
    cellSize,
    linearIndex,
    totalCells = 0,
  }) => {
    if (isEmpty || value === null) {
      return null;
    }

    return (
      <g>
        {renderPaletteBDiceGrowingGlyph(
          value,
          totalCells || value,
          cellSize,
          typeof linearIndex === 'number' ? linearIndex : undefined
        )}
      </g>
    );
  },
  renderPreview: ({ value, totalCells, cellSize }: SymbolSetPreviewProps) => {
    return (
      <svg
        width={cellSize}
        height={cellSize}
        viewBox={`0 0 ${cellSize} ${cellSize}`}
        role="img"
        aria-hidden="true"
      >
        {renderPaletteBDiceGrowingGlyph(value, totalCells, cellSize)}
      </svg>
    );
  },
};
