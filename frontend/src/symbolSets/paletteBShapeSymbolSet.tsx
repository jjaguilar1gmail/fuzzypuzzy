import { paletteB } from '@/styles/colorTokens';
import type { SymbolSet, SymbolSetPreviewProps } from './types';

const NUM_BUCKETS = paletteB.length;
const RADIUS_RATIO = 0.4;
const CELL_CORNER_RADIUS = 4;

const computeBucketCounts = (totalCells: number): number[] => {
  const safeTotal = Math.max(totalCells, NUM_BUCKETS);
  const base = Math.floor(safeTotal / NUM_BUCKETS);
  const remainder = safeTotal % NUM_BUCKETS;
  const counts: number[] = [];
  for (let i = 0; i < NUM_BUCKETS; i++) {
    counts.push(base + (i < remainder ? 1 : 0));
  }
  return counts;
};

const getBucketMeta = (
  linearIndex: number,
  bucketCounts: number[]
): { bucketIdx: number; idxInBucket: number; bucketSize: number } => {
  let accumulated = 0;
  for (let i = 0; i < bucketCounts.length; i++) {
    const size = bucketCounts[i];
    if (linearIndex < accumulated + size) {
      return { bucketIdx: i, idxInBucket: linearIndex - accumulated, bucketSize: size };
    }
    accumulated += size;
  }
  const lastIdx = bucketCounts.length - 1;
  return {
    bucketIdx: lastIdx,
    idxInBucket: Math.max(0, linearIndex - accumulated),
    bucketSize: bucketCounts[lastIdx] ?? 1,
  };
};

const getRadius = (idxInBucket: number, bucketSize: number, cellSize: number): number => {
  if (bucketSize <= 1) {
    return cellSize * RADIUS_RATIO;
  }
  const t = idxInBucket / (bucketSize - 1);
  return t * cellSize * RADIUS_RATIO;
};

export const getPaletteBColorContext = (
  value: number,
  totalCells: number,
  overrideLinearIndex?: number
) => {
  const counts = computeBucketCounts(totalCells || value);
  const effectiveIndex =
    typeof overrideLinearIndex === 'number'
      ? overrideLinearIndex
      : Math.max(0, value - 1);
  const { bucketIdx, idxInBucket, bucketSize } = getBucketMeta(
    effectiveIndex,
    counts
  );
  return {
    bucketIdx,
    idxInBucket,
    bucketSize,
    bucketColor: paletteB[bucketIdx % NUM_BUCKETS],
    circleColor: paletteB[(bucketIdx + 1) % NUM_BUCKETS],
  };
};

const renderPaletteBGlyph = (
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
  const radius = getRadius(context.idxInBucket, context.bucketSize, cellSize);
  const center = cellSize / 2;

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
      {radius > 0 && (
        <circle
          cx={center}
          cy={center}
          r={radius}
          fill={context.circleColor}
          pointerEvents="none"
        />
      )}
    </>
  );
};

export const paletteBShapeSymbolSet: SymbolSet = {
  id: 'paletteB-shapes',
  name: 'Palette B Shapes',
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
        {renderPaletteBGlyph(
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
        {renderPaletteBGlyph(value, totalCells, cellSize)}
      </svg>
    );
  },
};
