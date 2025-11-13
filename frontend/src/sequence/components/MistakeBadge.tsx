/**
 * Mistake Badge Component
 * Shows transient feedback for invalid placement attempts
 */

import React, { useEffect, useState } from 'react';
import type { MistakeEvent } from '../types';

interface MistakeBadgeProps {
  /** Most recent mistake event */
  mistake: MistakeEvent | null;
  /** Display duration in milliseconds */
  duration?: number;
  /** Optional custom class name */
  className?: string;
}

export const MistakeBadge: React.FC<MistakeBadgeProps> = ({
  mistake,
  duration = 1200,
  className = '',
}) => {
  const [visible, setVisible] = useState(false);
  const [currentMistake, setCurrentMistake] = useState<MistakeEvent | null>(null);

  useEffect(() => {
    if (mistake) {
      setCurrentMistake(mistake);
      setVisible(true);

      const timer = setTimeout(() => {
        setVisible(false);
      }, duration);

      return () => clearTimeout(timer);
    }
  }, [mistake, duration]);

  if (!visible || !currentMistake) {
    return null;
  }

  const getMessage = (): string => {
    switch (currentMistake.reason) {
      case 'not-adjacent':
        return 'Must be adjacent to anchor';
      case 'occupied':
        return 'Cell is occupied or blocked';
      case 'no-target':
        return 'No valid placement available';
      default:
        return 'Invalid placement';
    }
  };

  return (
    <div
      className={`mistake-badge ${className} ${visible ? 'visible' : 'hidden'}`}
      data-testid="mistake-badge"
      role="alert"
      aria-live="polite"
      style={{
        position: 'fixed',
        top: '20px',
        right: '20px',
        padding: '12px 16px',
        backgroundColor: 'rgba(239, 68, 68, 0.95)',
        color: 'white',
        borderRadius: '8px',
        boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
        fontSize: '14px',
        fontWeight: 500,
        zIndex: 1000,
        animation: visible ? 'fadeIn 0.2s ease-in' : 'fadeOut 0.3s ease-out',
        pointerEvents: 'none',
      }}
    >
      <div className="mistake-icon" style={{ display: 'inline-block', marginRight: '8px' }}>
        ⚠️
      </div>
      <span className="mistake-message">{getMessage()}</span>
    </div>
  );
};

/**
 * CSS animations (add to global styles)
 * 
 * @keyframes fadeIn {
 *   from { opacity: 0; transform: translateY(-10px); }
 *   to { opacity: 1; transform: translateY(0); }
 * }
 * 
 * @keyframes fadeOut {
 *   from { opacity: 1; }
 *   to { opacity: 0; }
 * }
 */
