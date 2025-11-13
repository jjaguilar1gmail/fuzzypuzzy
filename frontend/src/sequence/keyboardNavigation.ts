/**
 * Keyboard navigation support for guided sequence flow
 * Enables Tab navigation through legal targets and Enter to place
 */

import { useEffect, useState, useCallback } from 'react';
import type { Position } from './types';

interface KeyboardNavigationProps {
  /** Legal target positions available for placement */
  legalTargets: Position[];
  /** Whether guidance is enabled */
  enabled: boolean;
  /** Callback when user presses Enter on a focused target */
  onSelectTarget: (pos: Position) => void;
  /** Callback when user presses Escape to clear focus */
  onClearFocus?: () => void;
}

interface KeyboardNavigationResult {
  /** Currently focused target position (null if none) */
  focusedTarget: Position | null;
  /** Index of focused target in legalTargets array */
  focusedIndex: number;
  /** Move focus to next legal target */
  focusNext: () => void;
  /** Move focus to previous legal target */
  focusPrev: () => void;
  /** Clear focus */
  clearFocus: () => void;
  /** Key event handler to attach to container */
  handleKeyDown: (e: React.KeyboardEvent) => void;
}

/**
 * Hook for keyboard navigation through legal targets
 * 
 * @example
 * ```tsx
 * const { focusedTarget, handleKeyDown } = useKeyboardNavigation({
 *   legalTargets: state.legalTargets,
 *   enabled: state.guideEnabled,
 *   onSelectTarget: (pos) => placeNext(pos),
 *   onClearFocus: () => selectAnchor(null),
 * });
 * 
 * return (
 *   <div onKeyDown={handleKeyDown} tabIndex={0}>
 *     {board.map((row, r) => 
 *       row.map((cell, c) => (
 *         <Cell
 *           focused={focusedTarget?.row === r && focusedTarget?.col === c}
 *           {...cell}
 *         />
 *       ))
 *     )}
 *   </div>
 * );
 * ```
 */
export function useKeyboardNavigation({
  legalTargets,
  enabled,
  onSelectTarget,
  onClearFocus,
}: KeyboardNavigationProps): KeyboardNavigationResult {
  const [focusedIndex, setFocusedIndex] = useState(-1);

  // Reset focus when legal targets change
  useEffect(() => {
    if (legalTargets.length === 0) {
      setFocusedIndex(-1);
    } else if (focusedIndex >= legalTargets.length) {
      // Clamp to valid range
      setFocusedIndex(legalTargets.length - 1);
    }
  }, [legalTargets, focusedIndex]);

  const focusNext = useCallback(() => {
    if (!enabled || legalTargets.length === 0) return;
    setFocusedIndex((prev) => {
      if (prev < 0) return 0; // Start at first
      return (prev + 1) % legalTargets.length; // Wrap around
    });
  }, [enabled, legalTargets.length]);

  const focusPrev = useCallback(() => {
    if (!enabled || legalTargets.length === 0) return;
    setFocusedIndex((prev) => {
      if (prev < 0) return legalTargets.length - 1; // Start at last
      return (prev - 1 + legalTargets.length) % legalTargets.length; // Wrap around
    });
  }, [enabled, legalTargets.length]);

  const clearFocus = useCallback(() => {
    setFocusedIndex(-1);
    onClearFocus?.();
  }, [onClearFocus]);

  const handleKeyDown = useCallback(
    (e: React.KeyboardEvent) => {
      if (!enabled) return;

      switch (e.key) {
        case 'Tab':
          e.preventDefault();
          if (e.shiftKey) {
            focusPrev();
          } else {
            focusNext();
          }
          break;

        case 'ArrowRight':
        case 'ArrowDown':
          e.preventDefault();
          focusNext();
          break;

        case 'ArrowLeft':
        case 'ArrowUp':
          e.preventDefault();
          focusPrev();
          break;

        case 'Enter':
        case ' ':
          e.preventDefault();
          if (focusedIndex >= 0 && focusedIndex < legalTargets.length) {
            onSelectTarget(legalTargets[focusedIndex]);
          }
          break;

        case 'Escape':
          e.preventDefault();
          clearFocus();
          break;

        default:
          // Allow other keys (e.g., Ctrl+Z for undo)
          break;
      }
    },
    [enabled, focusedIndex, legalTargets, focusNext, focusPrev, clearFocus, onSelectTarget]
  );

  const focusedTarget = focusedIndex >= 0 && focusedIndex < legalTargets.length
    ? legalTargets[focusedIndex]
    : null;

  return {
    focusedTarget,
    focusedIndex,
    focusNext,
    focusPrev,
    clearFocus,
    handleKeyDown,
  };
}

/**
 * Utility to check if two positions are equal
 */
export function isFocusedPosition(
  pos: Position,
  focusedTarget: Position | null
): boolean {
  if (!focusedTarget) return false;
  return pos.row === focusedTarget.row && pos.col === focusedTarget.col;
}

/**
 * CSS classes for keyboard focus styling
 * Add to global stylesheet or component styles
 * 
 * ```css
 * .cell-keyboard-focus {
 *   outline: 3px solid #0066cc;
 *   outline-offset: 2px;
 *   z-index: 10;
 * }
 * 
 * @media (prefers-contrast: high) {
 *   .cell-keyboard-focus {
 *     outline-width: 4px;
 *     outline-color: #000;
 *   }
 * }
 * 
 * @media (prefers-reduced-motion: reduce) {
 *   .cell-keyboard-focus {
 *     transition: none;
 *   }
 * }
 * ```
 */
