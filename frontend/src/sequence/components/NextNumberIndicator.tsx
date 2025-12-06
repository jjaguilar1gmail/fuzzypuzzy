/**
 * Next Number Indicator Component
 * Displays the next target value or neutral state
 */

import React from 'react';

interface NextNumberIndicatorProps {
  /** Next target value (null if neutral) */
  nextTarget: number | null;
  /** Guide enabled flag */
  guideEnabled: boolean;
  /** Optional custom class name */
  className?: string;
}

export const NextNumberIndicator: React.FC<NextNumberIndicatorProps> = ({
  nextTarget,
  guideEnabled,
  className = '',
}) => {
  if (!guideEnabled) {
    return null;
  }

  return (
    <div
      className={`next-number-indicator ${className}`}
      data-testid="next-number-indicator"
      role="status"
      aria-live="polite"
    >
      {nextTarget !== null ? (
        <div className="next-number-value" data-testid="next-number-value">
          <span className="label">Next symbol:</span>
          <span className="value">{nextTarget}</span>
        </div>
      ) : (
        <div className="next-number-neutral" data-testid="next-number-neutral">
          <span className="label">Select a symbol</span>
        </div>
      )}
    </div>
  );
};
