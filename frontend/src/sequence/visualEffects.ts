/**
 * Visual change reason effects
 * CSS-in-JS styles for nextTargetChangeReason visual treatments
 */

import type { NextTargetChangeReason } from './types';

export interface ChangeReasonStyle {
  className: string;
  animation?: string;
  description: string;
}

/**
 * Get style treatment for change reason
 */
export function getChangeReasonStyle(
  reason: NextTargetChangeReason
): ChangeReasonStyle {
  switch (reason) {
    case 'placement':
      return {
        className: 'change-reason-placement',
        animation: 'pulse-success',
        description: 'Number placed successfully',
      };

    case 'anchor-change':
      return {
        className: 'change-reason-anchor',
        animation: 'highlight-anchor',
        description: 'Anchor changed',
      };

    case 'tail-removal':
      return {
        className: 'change-reason-tail-removal',
        animation: 'fade-neutral',
        description: 'Chain tail removed',
      };

    case 'non-tail-removal':
      return {
        className: 'change-reason-non-tail',
        animation: 'fade-neutral',
        description: 'Value removed from chain',
      };

    case 'neutral':
      return {
        className: 'change-reason-neutral',
        description: 'Select a number to continue',
      };

    default:
      return {
        className: 'change-reason-default',
        description: '',
      };
  }
}

/**
 * CSS keyframes and classes (to be added to global styles)
 */
export const CHANGE_REASON_CSS = `
/* Placement success pulse */
@keyframes pulse-success {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.9; background-color: rgb(var(--color-success) / 0.2); }
  100% { transform: scale(1); opacity: 1; }
}

.change-reason-placement {
  animation: pulse-success 0.4s ease-out;
}

/* Anchor change highlight */
@keyframes highlight-anchor {
  0% { box-shadow: 0 0 0 0 rgb(var(--color-primary) / 0.7); }
  50% { box-shadow: 0 0 0 4px rgb(var(--color-primary) / 0.4); }
  100% { box-shadow: 0 0 0 0 rgb(var(--color-primary) / 0); }
}

.change-reason-anchor {
  animation: highlight-anchor 0.6s ease-out;
}

/* Neutral state fade */
@keyframes fade-neutral {
  0% { opacity: 1; }
  100% { opacity: 0.6; }
}

.change-reason-tail-removal,
.change-reason-non-tail {
  animation: fade-neutral 0.3s ease-out forwards;
}

.change-reason-neutral {
  opacity: 0.7;
  font-style: italic;
}

/* Indicator state classes */
.next-indicator-has-target {
  color: rgb(var(--color-success));
  font-weight: 600;
}

.next-indicator-neutral {
  color: rgb(var(--color-text-muted));
  font-weight: 400;
}

/* Cell visual states */
.cell-anchor {
  outline: 2px solid rgb(var(--color-primary) / 0.6);
  outline-offset: -2px;
}

.cell-legal-target {
  background-color: rgb(var(--color-success) / 0.15);
}

.cell-recent-placement {
  animation: pulse-success 0.4s ease-out;
}

/* Fade transitions */
.fade-in {
  animation: fadeIn 0.2s ease-in;
}

.fade-out {
  animation: fadeOut 0.3s ease-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(-10px); }
  to { opacity: 1; transform: translateY(0); }
}

@keyframes fadeOut {
  from { opacity: 1; }
  to { opacity: 0; }
}

/* Mistake pulse */
@keyframes mistakePulse {
  0% { transform: scale(1); opacity: 1; }
  50% { transform: scale(1.05); opacity: 0.8; }
  100% { transform: scale(1); opacity: 1; }
}

.cell-mistake {
  animation: mistakePulse 0.6s ease-in-out;
  border: 3px solid rgb(var(--color-danger) / 0.8) !important;
}

/* Accessibility: High contrast mode */
@media (prefers-contrast: high) {
  .cell-anchor {
    outline-width: 3px;
    outline-color: rgb(var(--color-primary-strong));
  }

  .cell-legal-target {
    background-color: rgb(var(--color-success) / 0.3);
    outline: 1px solid rgb(var(--color-success));
  }
}
`;
