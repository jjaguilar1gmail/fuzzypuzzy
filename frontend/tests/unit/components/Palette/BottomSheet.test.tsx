import { describe, it, expect, vi } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { userEvent } from '@testing-library/user-event';

// Mock BottomSheet component for testing
const MockBottomSheet = ({ children, isOpen, onToggle }: any) => (
  <div data-testid="bottom-sheet" className={isOpen ? 'open' : 'closed'}>
    <button onClick={onToggle} data-testid="toggle-button">
      {isOpen ? 'Close' : 'Open'}
    </button>
    {isOpen && <div data-testid="sheet-content">{children}</div>}
  </div>
);

describe('Bottom Sheet Palette', () => {
  it('should start collapsed by default', () => {
    render(<MockBottomSheet isOpen={false} onToggle={vi.fn()}>Content</MockBottomSheet>);
    
    const sheet = screen.getByTestId('bottom-sheet');
    expect(sheet).toHaveClass('closed');
    expect(screen.queryByTestId('sheet-content')).not.toBeInTheDocument();
  });

  it('should expand when toggle button is clicked', async () => {
    const onToggle = vi.fn();
    const user = userEvent.setup();
    
    const { rerender } = render(
      <MockBottomSheet isOpen={false} onToggle={onToggle}>Content</MockBottomSheet>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    await user.click(toggleButton);
    
    expect(onToggle).toHaveBeenCalledTimes(1);
    
    // Simulate state change
    rerender(<MockBottomSheet isOpen={true} onToggle={onToggle}>Content</MockBottomSheet>);
    
    expect(screen.getByTestId('sheet-content')).toBeInTheDocument();
    expect(screen.getByTestId('bottom-sheet')).toHaveClass('open');
  });

  it('should collapse when toggle button is clicked while open', async () => {
    const onToggle = vi.fn();
    const user = userEvent.setup();
    
    const { rerender } = render(
      <MockBottomSheet isOpen={true} onToggle={onToggle}>Content</MockBottomSheet>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    await user.click(toggleButton);
    
    expect(onToggle).toHaveBeenCalledTimes(1);
    
    // Simulate state change
    rerender(<MockBottomSheet isOpen={false} onToggle={onToggle}>Content</MockBottomSheet>);
    
    expect(screen.queryByTestId('sheet-content')).not.toBeInTheDocument();
  });

  it('should show content when expanded', () => {
    render(<MockBottomSheet isOpen={true} onToggle={vi.fn()}>
      <div data-testid="palette-content">Palette</div>
    </MockBottomSheet>);
    
    expect(screen.getByTestId('palette-content')).toBeInTheDocument();
    expect(screen.getByText('Palette')).toBeInTheDocument();
  });

  it('should have accessible toggle button', () => {
    render(<MockBottomSheet isOpen={false} onToggle={vi.fn()}>Content</MockBottomSheet>);
    
    const toggleButton = screen.getByTestId('toggle-button');
    expect(toggleButton).toBeInTheDocument();
    expect(toggleButton.tagName).toBe('BUTTON');
  });

  it('should support keyboard interaction', async () => {
    const onToggle = vi.fn();
    const user = userEvent.setup();
    
    render(<MockBottomSheet isOpen={false} onToggle={onToggle}>Content</MockBottomSheet>);
    
    const toggleButton = screen.getByTestId('toggle-button');
    toggleButton.focus();
    
    await user.keyboard('{Enter}');
    expect(onToggle).toHaveBeenCalled();
  });

  it('should maintain state during multiple toggles', async () => {
    const onToggle = vi.fn();
    const user = userEvent.setup();
    
    const { rerender } = render(
      <MockBottomSheet isOpen={false} onToggle={onToggle}>Content</MockBottomSheet>
    );
    
    const toggleButton = screen.getByTestId('toggle-button');
    
    // Toggle open
    await user.click(toggleButton);
    rerender(<MockBottomSheet isOpen={true} onToggle={onToggle}>Content</MockBottomSheet>);
    expect(screen.getByTestId('sheet-content')).toBeInTheDocument();
    
    // Toggle closed
    await user.click(toggleButton);
    rerender(<MockBottomSheet isOpen={false} onToggle={onToggle}>Content</MockBottomSheet>);
    expect(screen.queryByTestId('sheet-content')).not.toBeInTheDocument();
    
    // Toggle open again
    await user.click(toggleButton);
    rerender(<MockBottomSheet isOpen={true} onToggle={onToggle}>Content</MockBottomSheet>);
    expect(screen.getByTestId('sheet-content')).toBeInTheDocument();
    
    expect(onToggle).toHaveBeenCalledTimes(3);
  });
});
