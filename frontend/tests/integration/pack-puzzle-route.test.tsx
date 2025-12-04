import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import PackPuzzlePage from '@/pages/packs/[packId]/puzzles/[puzzleId]';
import { useRouter } from 'next/router';
import { loadPuzzle, loadPack } from '@/lib/loaders/packs';

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: vi.fn(),
}));

// Mock the loaders
vi.mock('@/lib/loaders/packs', () => ({
  loadPuzzle: vi.fn(),
  loadPack: vi.fn(),
}));

const mockPuzzle = {
  schema_version: '1.0',
  id: '0003',
  pack_id: 'test-pack',
  size: 5,
  difficulty: 'classic' as const,
  seed: 12345,
  clue_count: 8,
  max_gap: 8,
  givens: [
    { row: 0, col: 0, value: 1 },
    { row: 0, col: 4, value: 5 },
    { row: 2, col: 2, value: 13 },
    { row: 4, col: 0, value: 25 },
  ],
};

const mockPack = {
  schema_version: '1.0',
  id: 'test-pack',
  title: 'Test Pack',
  description: 'Test pack description',
  puzzles: ['0001', '0002', '0003', '0004', '0005'],
  difficulty_counts: { classic: 5 },
  size_distribution: { '5': 5 },
  created_at: '2025-01-01T00:00:00Z',
};

describe('Pack Puzzle Route with Progress', () => {
  beforeEach(() => {
    vi.mocked(loadPuzzle).mockResolvedValue(mockPuzzle);
    vi.mocked(loadPack).mockResolvedValue(mockPack);
    
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0003' },
      push: vi.fn(),
    });
  });

  it('should load and display puzzle from pack', async () => {
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      // Grid should be rendered
      const grid = screen.getByRole('grid');
      expect(grid).toBeInTheDocument();
    });
  });

  it('should show puzzle position in pack', async () => {
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      // Should show "Puzzle 3 of 5" or similar
      expect(screen.getByText(/3.*of.*5/i)).toBeInTheDocument();
    });
  });

  it('should provide navigation to previous puzzle', async () => {
    const mockPush = vi.fn();
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0003' },
      push: mockPush,
    });

    const user = userEvent.setup();
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    const prevButton = screen.getByRole('button', { name: /previous/i });
    expect(prevButton).not.toBeDisabled();
    
    await user.click(prevButton);
    expect(mockPush).toHaveBeenCalledWith('/packs/test-pack/puzzles/0002');
  });

  it('should provide navigation to next puzzle', async () => {
    const mockPush = vi.fn();
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0003' },
      push: mockPush,
    });

    const user = userEvent.setup();
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).not.toBeDisabled();
    
    await user.click(nextButton);
    expect(mockPush).toHaveBeenCalledWith('/packs/test-pack/puzzles/0004');
  });

  it('should disable previous button on first puzzle', async () => {
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0001' },
      push: vi.fn(),
    });

    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    const prevButton = screen.getByRole('button', { name: /previous/i });
    expect(prevButton).toBeDisabled();
  });

  it('should disable next button on last puzzle', async () => {
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0005' },
      push: vi.fn(),
    });

    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    const nextButton = screen.getByRole('button', { name: /next/i });
    expect(nextButton).toBeDisabled();
  });

  it('should record progress when completing puzzle', async () => {
    // This test verifies that progress store is updated
    // Mock will be implemented when progressStore is created
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    // TODO: Complete puzzle and verify progressStore.recordCompletion called
    expect(true).toBe(true); // Placeholder
  });

  it('should link back to pack detail', async () => {
    const mockPush = vi.fn();
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack', puzzleId: '0003' },
      push: mockPush,
    });

    const user = userEvent.setup();
    render(<PackPuzzlePage />);
    
    await waitFor(() => {
      expect(screen.getByRole('grid')).toBeInTheDocument();
    });

    const backLink = screen.getByRole('link', { name: /back to.*pack/i });
    expect(backLink).toHaveAttribute('href', '/packs/test-pack');
  });
});
