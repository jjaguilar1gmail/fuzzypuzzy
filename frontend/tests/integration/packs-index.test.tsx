import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';
import PacksIndexPage from '@/pages/packs/index';
import { loadPacksList } from '@/lib/loaders/packs';

// Mock the loaders
vi.mock('@/lib/loaders/packs', () => ({
  loadPacksList: vi.fn(),
}));

const mockPacks = [
  {
    id: 'classic-pack',
    title: 'Classic Puzzles',
    description: 'Beginner-friendly puzzles',
    puzzle_count: 10,
    difficulty_counts: { classic: 10, expert: 0 },
    created_at: '2025-01-01T00:00:00Z',
  },
  {
    id: 'mixed-pack',
    title: 'Mixed Challenge',
    description: 'Variety of difficulties',
    puzzle_count: 20,
    difficulty_counts: { classic: 12, expert: 8 },
    created_at: '2025-01-02T00:00:00Z',
  },
  {
    id: 'expert-pack',
    title: 'Expert Only',
    description: 'Advanced puzzles',
    puzzle_count: 8,
    difficulty_counts: { classic: 0, expert: 8 },
    created_at: '2025-01-03T00:00:00Z',
  },
];

describe('Packs Index Filtering', () => {
  beforeEach(() => {
    vi.mocked(loadPacksList).mockResolvedValue(mockPacks);
  });

  it('should render all packs by default', async () => {
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
      expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
      expect(screen.getByText('Expert Only')).toBeInTheDocument();
    });
  });

  it('should filter packs by classic difficulty', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
    });

    const classicFilter = screen.getByRole('button', { name: /classic/i });
    await user.click(classicFilter);

    expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.queryByText('Expert Only')).not.toBeInTheDocument();
  });

  it('should filter packs by expert difficulty', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
    });

    const expertFilter = screen.getByRole('button', { name: /expert/i });
    await user.click(expertFilter);

    expect(screen.queryByText('Classic Puzzles')).not.toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.getByText('Expert Only')).toBeInTheDocument();
  });

  it('should allow clearing filters', async () => {
    const user = userEvent.setup();
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
    });

    const classicFilter = screen.getByRole('button', { name: /classic/i });
    await user.click(classicFilter);

    expect(screen.queryByText('Expert Only')).not.toBeInTheDocument();

    // Clear filter
    const clearFilter = screen.getByRole('button', { name: /all/i });
    await user.click(clearFilter);

    // All packs should be visible again
    expect(screen.getByText('Classic Puzzles')).toBeInTheDocument();
    expect(screen.getByText('Mixed Challenge')).toBeInTheDocument();
    expect(screen.getByText('Expert Only')).toBeInTheDocument();
  });

  it('should handle loading state', () => {
    vi.mocked(loadPacksList).mockReturnValue(new Promise(() => {})); // Never resolves
    
    render(<PacksIndexPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should handle error state', async () => {
    vi.mocked(loadPacksList).mockRejectedValue(new Error('Failed to load packs'));
    
    render(<PacksIndexPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });
});
