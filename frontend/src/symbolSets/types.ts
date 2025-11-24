import type { ReactNode } from 'react';

export type CellSymbolProps = {
  value: number | null;
  isGiven: boolean;
  isSelected: boolean;
  isError: boolean;
  isEmpty: boolean;
  isGuideTarget: boolean;
  cellSize: number;
};

export type SymbolSet = {
  id: string;
  name: string;
  kind?: 'numeric' | 'shape' | 'hybrid';
  renderCell: (props: CellSymbolProps) => ReactNode;
};
