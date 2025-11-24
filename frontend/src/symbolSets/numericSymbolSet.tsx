import { motion } from 'framer-motion';
import { statusPalette } from '@/styles/colorTokens';
import type { SymbolSet } from './types';

const GIVEN_FONT_RATIO = 24 / 60;
const PLAYER_FONT_RATIO = 22 / 60;

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

    let indicator: ReactNode = null;
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
};
