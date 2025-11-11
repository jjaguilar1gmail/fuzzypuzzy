/**
 * Position helper utilities.
 */

export interface Position {
  row: number;
  col: number;
}

export function positionKey(pos: Position): string {
  return `${pos.row},${pos.col}`;
}

export function parsePositionKey(key: string): Position {
  const [row, col] = key.split(',').map(Number);
  return { row, col };
}

export function positionsEqual(a: Position, b: Position): boolean {
  return a.row === b.row && a.col === b.col;
}
