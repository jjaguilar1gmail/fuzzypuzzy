import { describe, it, expect } from 'vitest';
import { createEmptyGrid, getCell } from '@/domain/grid';
import { isValidPlacement, isPuzzleComplete } from '@/lib/validation/hidato';

describe('Hidato Validation', () => {
  describe('isValidPlacement', () => {
    it('should reject placement on a given cell', () => {
      const grid = createEmptyGrid(3);
      const cell = getCell(grid, 0, 0);
      if (cell) {
        cell.given = true;
        cell.value = 1;
      }
      
      expect(isValidPlacement(grid, 0, 0, 2)).toBe(false);
    });

    it('should reject duplicate values', () => {
      const grid = createEmptyGrid(3);
      const cell1 = getCell(grid, 0, 0);
      const cell2 = getCell(grid, 1, 1);
      if (cell1) cell1.value = 5;
      
      expect(isValidPlacement(grid, 1, 1, 5)).toBe(false);
    });

    it('should accept value adjacent to value-1', () => {
      const grid = createEmptyGrid(3);
      const cell1 = getCell(grid, 0, 0);
      if (cell1) {
        cell1.value = 4;
        cell1.given = true;
      }
      
      // Place 5 adjacent to 4
      expect(isValidPlacement(grid, 0, 1, 5)).toBe(true);
    });

    it('should accept value adjacent to value+1', () => {
      const grid = createEmptyGrid(3);
      const cell1 = getCell(grid, 0, 0);
      if (cell1) {
        cell1.value = 6;
        cell1.given = true;
      }
      
      // Place 5 adjacent to 6
      expect(isValidPlacement(grid, 0, 1, 5)).toBe(true);
    });

    it('should allow early game placements for flexibility', () => {
      const grid = createEmptyGrid(5);
      const cell1 = getCell(grid, 0, 0);
      if (cell1) {
        cell1.value = 1;
        cell1.given = true;
      }
      
      // With only 1 cell filled, allow placement anywhere
      expect(isValidPlacement(grid, 2, 2, 10)).toBe(true);
    });

    it('should reject out-of-range values', () => {
      const grid = createEmptyGrid(3);
      
      expect(isValidPlacement(grid, 0, 0, 0)).toBe(false);
      expect(isValidPlacement(grid, 0, 0, 10)).toBe(false);
    });
  });

  describe('isPuzzleComplete', () => {
    it('should return false for incomplete puzzle', () => {
      const grid = createEmptyGrid(3);
      const cell1 = getCell(grid, 0, 0);
      if (cell1) cell1.value = 1;
      
      expect(isPuzzleComplete(grid)).toBe(false);
    });

    it('should return true for valid complete puzzle', () => {
      const grid = createEmptyGrid(3);
      
      // Create a valid path with proper adjacency: 
      // 1-2-3
      // 9-8-4
      // 7-6-5
      const values = [
        [1, 2, 3],
        [9, 8, 4],
        [7, 6, 5],
      ];
      
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const cell = getCell(grid, r, c);
          if (cell) cell.value = values[r][c];
        }
      }
      
      expect(isPuzzleComplete(grid)).toBe(true);
    });

    it('should return false for non-contiguous complete grid', () => {
      const grid = createEmptyGrid(3);
      
      // Fill but break contiguity
      const values = [
        [1, 3, 5],
        [2, 4, 6],
        [7, 8, 9],
      ];
      
      for (let r = 0; r < 3; r++) {
        for (let c = 0; c < 3; c++) {
          const cell = getCell(grid, r, c);
          if (cell) cell.value = values[r][c];
        }
      }
      
      expect(isPuzzleComplete(grid)).toBe(false);
    });
  });
});
