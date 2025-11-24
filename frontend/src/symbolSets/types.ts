import type { ReactNode } from 'react';

export type CellSymbolProps = {
  value: number | null;
  isGiven: boolean;
  isSelected: boolean;
  isError: boolean;
  isEmpty: boolean;
  isGuideTarget: boolean;
  cellSize: number;
  isChainStart: boolean;
  isChainEnd: boolean;
  linearIndex?: number;
  totalCells?: number;
};

export type SymbolSetPreviewProps = {
  value: number;
  totalCells: number;
  cellSize: number;
};

export type SymbolSet = {
  id: string;
  name: string;
  kind?: 'numeric' | 'shape' | 'hybrid';
  renderCell: (props: CellSymbolProps) => ReactNode;
  renderPreview?: (props: SymbolSetPreviewProps) => ReactNode;
};
