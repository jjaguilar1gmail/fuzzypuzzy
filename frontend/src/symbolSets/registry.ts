import type { SymbolSet } from './types';
import { numericSymbolSet } from './numericSymbolSet';
import { paletteBShapeSymbolSet } from './paletteBShapeSymbolSet';

const registry = {
  numeric: numericSymbolSet,
  'paletteB-shapes': paletteBShapeSymbolSet,
} as const;

export type SymbolSetId = keyof typeof registry;

const DEFAULT_SYMBOL_SET_ID: SymbolSetId = 'numeric';

export const listSymbolSets = (): SymbolSet[] => Object.values(registry);

export const getSymbolSetById = (id: SymbolSetId): SymbolSet => registry[id];

export const getDefaultSymbolSet = (): SymbolSet => registry[DEFAULT_SYMBOL_SET_ID];
