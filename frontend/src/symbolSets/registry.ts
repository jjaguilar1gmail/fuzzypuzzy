import type { SymbolSet } from './types';
import { numericSymbolSet } from './numericSymbolSet';
import { paletteBShapeSymbolSet } from './paletteBShapeSymbolSet';
import { paletteBDiceSymbolSet } from './paletteBDiceSymbolSet';
import { paletteBDiceGrowingSymbolSet } from './paletteBDiceGrowingSymbolSet';

const registry = {
  numeric: numericSymbolSet,
  'paletteB-shapes': paletteBShapeSymbolSet,
  'paletteB-dice': paletteBDiceSymbolSet,
  'paletteB-dice-growing': paletteBDiceGrowingSymbolSet,
} as const;

export type SymbolSetId = keyof typeof registry;

const DEFAULT_SYMBOL_SET_ID: SymbolSetId = 'paletteB-dice-growing';

export const listSymbolSets = (): SymbolSet[] => Object.values(registry);

export const getSymbolSetById = (id: SymbolSetId): SymbolSet => registry[id];

export const getDefaultSymbolSet = (): SymbolSet => registry[DEFAULT_SYMBOL_SET_ID];
