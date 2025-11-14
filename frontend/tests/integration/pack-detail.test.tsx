import { describe, it, expect, beforeEach, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import PackDetailPage from '@/pages/packs/[packId]/index';
import { useRouter } from 'next/router';

// Mock Next.js router
vi.mock('next/router', () => ({
  useRouter: vi.fn(),
}));

// Mock the loaders
vi.mock('@/lib/loaders/packs', () => ({
  loadPack: vi.fn(),
}));

const mockPack = {
  schema_version: '1.0',
  id: 'test-pack',
  title: 'Test Pack',
  description: 'A collection of test puzzles',
  puzzles: ['0001', '0002', '0003', '0004', '0005'],
  difficulty_counts: {
    easy: 2,
    medium: 2,
    hard: 1,
  },
  size_distribution: {
    '5': 3,
    '7': 2,
  },
  created_at: '2025-01-01T00:00:00Z',
};

describe('Pack Detail Page', () => {
  beforeEach(() => {
    const { loadPack } = require('@/lib/loaders/packs');
    loadPack.mockResolvedValue(mockPack);
    
    (useRouter as any).mockReturnValue({
      query: { packId: 'test-pack' },
      push: vi.fn(),
    });
  });

  it('should load and display pack metadata', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Test Pack')).toBeInTheDocument();
      expect(screen.getByText('A collection of test puzzles')).toBeInTheDocument();
    });
  });

  it('should display puzzle count', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/5 puzzles/i)).toBeInTheDocument();
    });
  });

  it('should display difficulty distribution', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/2 easy/i)).toBeInTheDocument();
      expect(screen.getByText(/2 medium/i)).toBeInTheDocument();
      expect(screen.getByText(/1 hard/i)).toBeInTheDocument();
    });
  });

  it('should display size distribution', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/3 puzzles - 5x5/)).toBeInTheDocument();
      expect(screen.getByText(/2 puzzles - 7x7/)).toBeInTheDocument();
    });
  });

  it('should list all puzzles with links', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText('Puzzle #1')).toBeInTheDocument();
      expect(screen.getByText('Puzzle #5')).toBeInTheDocument();
    });

    const puzzleLinks = screen.getAllByRole('link');
    expect(puzzleLinks.length).toBeGreaterThanOrEqual(5);
  });

  it('should handle loading state', () => {
    const { loadPack } = require('@/lib/loaders/packs');
    loadPack.mockReturnValue(new Promise(() => {})); // Never resolves
    
    render(<PackDetailPage />);
    expect(screen.getByText(/loading/i)).toBeInTheDocument();
  });

  it('should handle error state', async () => {
    const { loadPack } = require('@/lib/loaders/packs');
    loadPack.mockRejectedValue(new Error('Pack not found'));
    
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/error/i)).toBeInTheDocument();
    });
  });

  it('should display creation date', async () => {
    render(<PackDetailPage />);
    
    await waitFor(() => {
      expect(screen.getByText(/January 1, 2025/i)).toBeInTheDocument();
    });
  });
});
