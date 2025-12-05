import type { SymbolSet, SymbolSetPreviewProps } from './types';
import { getPaletteBColorContext } from './paletteBShapeSymbolSet';
import { getPipLayout } from './paletteBDiceUtils';

const CELL_CORNER_RADIUS = 4;
const PIP_RADIUS_RATIO = 0.085;

const renderPaletteBDiceGlyph = (
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
  const pipRadius = cellSize * PIP_RADIUS_RATIO;

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

export const paletteBDiceSymbolSet: SymbolSet = {
  id: 'paletteB-dice',
  name: 'Palette B Dice',
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
        {renderPaletteBDiceGlyph(
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
        {renderPaletteBDiceGlyph(value, totalCells, cellSize)}
      </svg>
    );
  },
};
