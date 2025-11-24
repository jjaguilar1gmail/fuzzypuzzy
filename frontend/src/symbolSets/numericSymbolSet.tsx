import { motion } from 'framer-motion';
import { statusPalette } from '@/styles/colorTokens';
import type { SymbolSet, SymbolSetPreviewProps } from './types';

const GIVEN_FONT_RATIO = 24 / 60;
const PLAYER_FONT_RATIO = 22 / 60;
const PREVIEW_CORNER_RADIUS = 4;

const renderStaticGlyph = ({
  value,
  cellSize,
  isGiven = false,
}: {
  value: number;
  cellSize: number;
  isGiven?: boolean;
}) => {
  const fontSize = isGiven
    ? cellSize * GIVEN_FONT_RATIO
    : cellSize * PLAYER_FONT_RATIO;
  const center = cellSize / 2;
  return (
    <svg
      width={cellSize}
      height={cellSize}
      viewBox={`0 0 ${cellSize} ${cellSize}`}
      role="img"
      aria-hidden="true"
    >
      <rect
        x={0}
        y={0}
        width={cellSize}
        height={cellSize}
        rx={PREVIEW_CORNER_RADIUS}
        ry={PREVIEW_CORNER_RADIUS}
        fill="none"
      />
      <text
        x={center}
        y={center}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={fontSize}
        fontWeight={isGiven ? 'bold' : 'normal'}
        fill={isGiven ? statusPalette.text : statusPalette.primary}
      >
        {value}
      </text>
    </svg>
  );
};

export const numericSymbolSet: SymbolSet = {
  id: 'numeric',
  name: 'Numbers',
  kind: 'numeric',
  renderCell: ({ value, isGiven, isEmpty, cellSize }) => {
    if (isEmpty || value === null) {
      return null;
    }

    const center = cellSize / 2;
    const fontSize = isGiven
      ? cellSize * GIVEN_FONT_RATIO
      : cellSize * PLAYER_FONT_RATIO;

    return (
      <motion.text
        x={center}
        y={center}
        textAnchor="middle"
        dominantBaseline="central"
        fontSize={fontSize}
        fontWeight={isGiven ? 'bold' : 'normal'}
        fill={isGiven ? statusPalette.text : statusPalette.primary}
        pointerEvents="none"
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ duration: 0.15, type: 'spring' }}
      >
        {value}
      </motion.text>
    );
  },
  renderPreview: ({ value, cellSize }: SymbolSetPreviewProps) => {
    return renderStaticGlyph({ value, cellSize });
  },
};
