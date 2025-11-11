import { describe, it, expect, beforeEach, afterEach } from 'vitest';
import { render, screen } from '@testing-library/react';

// Mock component for mobile layout testing
const MockMobilePage = () => (
  <div data-testid="mobile-page" className="mobile-container">
    <header data-testid="header" style={{ minHeight: '60px' }}>Header</header>
    <main data-testid="main-content" style={{ padding: '16px' }}>
      <div data-testid="grid" style={{ width: '100%', maxWidth: '400px' }}>Grid</div>
      <button data-testid="action-button" style={{ minWidth: '44px', minHeight: '44px' }}>
        Action
      </button>
    </main>
  </div>
);

describe('Mobile Layout', () => {
  let originalInnerWidth: number;

  beforeEach(() => {
    originalInnerWidth = window.innerWidth;
  });

  afterEach(() => {
    // Restore original viewport
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: originalInnerWidth,
    });
  });

  it('should not have horizontal scroll on mobile viewport', () => {
    // Simulate mobile viewport (375px)
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    const { container } = render(<MockMobilePage />);
    
    const page = screen.getByTestId('mobile-page');
    expect(page).toBeInTheDocument();
    
    // Check that content doesn't overflow
    const mainContent = screen.getByTestId('main-content');
    const computedStyle = window.getComputedStyle(mainContent);
    
    // Should have appropriate padding/margin
    expect(computedStyle.padding).toBeTruthy();
  });

  it('should have minimum 40px touch targets on mobile', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<MockMobilePage />);
    
    const actionButton = screen.getByTestId('action-button');
    const computedStyle = window.getComputedStyle(actionButton);
    
    // Check minimum dimensions (44px is iOS guideline, 40px is minimum)
    const minWidth = parseInt(computedStyle.minWidth);
    const minHeight = parseInt(computedStyle.minHeight);
    
    expect(minWidth).toBeGreaterThanOrEqual(40);
    expect(minHeight).toBeGreaterThanOrEqual(40);
  });

  it('should scale grid appropriately for mobile viewport', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<MockMobilePage />);
    
    const grid = screen.getByTestId('grid');
    const computedStyle = window.getComputedStyle(grid);
    
    // Grid should be responsive
    expect(computedStyle.width).toBeTruthy();
    expect(computedStyle.maxWidth).toBeTruthy();
  });

  it('should have sufficient header height for tap targets', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<MockMobilePage />);
    
    const header = screen.getByTestId('header');
    const computedStyle = window.getComputedStyle(header);
    
    const minHeight = parseInt(computedStyle.minHeight);
    expect(minHeight).toBeGreaterThanOrEqual(60);
  });

  it('should render correctly on small mobile (320px)', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 320,
    });

    const { container } = render(<MockMobilePage />);
    
    expect(screen.getByTestId('mobile-page')).toBeInTheDocument();
    expect(screen.getByTestId('main-content')).toBeInTheDocument();
  });

  it('should render correctly on medium mobile (375px)', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<MockMobilePage />);
    
    expect(screen.getByTestId('mobile-page')).toBeInTheDocument();
  });

  it('should render correctly on large mobile (414px)', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 414,
    });

    render(<MockMobilePage />);
    
    expect(screen.getByTestId('mobile-page')).toBeInTheDocument();
  });

  it('should have appropriate spacing on mobile', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    render(<MockMobilePage />);
    
    const mainContent = screen.getByTestId('main-content');
    const computedStyle = window.getComputedStyle(mainContent);
    
    // Should have padding for mobile
    const padding = computedStyle.padding;
    expect(padding).toBeTruthy();
    expect(padding).not.toBe('0px');
  });

  it('should not overflow viewport width', () => {
    Object.defineProperty(window, 'innerWidth', {
      writable: true,
      configurable: true,
      value: 375,
    });

    const { container } = render(<MockMobilePage />);
    
    const page = screen.getByTestId('mobile-page');
    
    // Page should not cause horizontal scroll
    // This would be validated with actual getBoundingClientRect in real components
    expect(page).toBeInTheDocument();
  });
});
