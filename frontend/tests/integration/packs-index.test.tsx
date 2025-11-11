import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import PacksIndexPage from '@/pages/packs/index';

// Mock the loaders
vi.mock('@/lib/loaders/packs', () => ({
  loadPacksList: vi.fn(),
}));

const mockPacks = [
  {
    id: 'easy-pack',
    title: 'Easy Puzzles',
    description: 'Beginner-friendly puzzles',
    puzzle_count: 10,
    difficulty_counts: { easy: 10 },
    created_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'mixed-pack',
    title: 'Mixed Challenge',
    description: 'Variety of difficulties',
    puzzle_count: 20,
    difficulty_counts: { easy: 5, medium: 10, hard: 5 },
    created_at: '2025-01-02T00:00:00Z',
  },
  {
    id: 'hard-pack',
    title: 'Expert Only',
    description: 'Advanced puzzles',
    puzzle_count: 8,
    difficulty_counts: { hard: 5, extreme: 3 },
    created_at: '2025-01-03T00:00:00Z',
  },
];

describe('Packs Index Filtering', () => {
  beforeEach(() => {
    const { loadPacksList } = require('@/lib/loaders/packs');
    loadPacksList.mockResolvedValue(mockPacks);
  });

  it('should render all packs by default', async () => {
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
      expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
      expect(screen.getByText('Expert Only')).toBeInTheDocument();
    });
  });

  it('should filter packs by easy difficulty', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
    });

    // Click easy filter
    const easyFilter = screen.getByRole('button', { name: /easy/i });
    await user.click(easyFilter);

    // Should show packs with easy puzzles
    expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.queryByText('Expert Only')).not.toBeInTheDocument();
  });

  it('should filter packs by hard difficulty', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
    });

    const hardFilter = screen.getByRole('button', { name: /hard/i });
    await user.click(hardFilter);

    // Should show only packs with hard puzzles
    expect(screen.queryByText('Easy Puzzles')).not.toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.getByText('Expert Only')).toBeInTheDocument();
  });

  it('should allow clearing filters', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
    });

    // Apply filter
    const easyFilter = screen.getByRole('button', { name: /easy/i });
    await user.click(easyFilter);

    expect(screen.queryByText('Expert Only')).not.toBeInTheDocument();

    // Clear filter
    const clearFilter = screen.getByRole('button', { name: /all/i });
    await user.click(clearFilter);

    // All packs should be visible again
    expect(screen.getByText('Easy Puzzles')).toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.getByText('Expert Only')).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    const { loadPacksList } = require('@/lib/loaders/packs');
    loadPacksList.mockReturnValue(new Promise(() => {})); // Never resolves
    
    render(<PacksIndexPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should handle error state', async () => {
    const { loadPacksList } = require('@/lib/loaders/packs');
    loadPacksList.mockRejectedValue(new Error('Failed to load packs'));
    
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
