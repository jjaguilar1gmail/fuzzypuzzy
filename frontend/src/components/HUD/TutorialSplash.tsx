import { useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import type { ReactNode } from 'react';

interface TutorialSplashProps {
  isOpen: boolean;
  onClose: () => void;
}

type MiniCellStatus = 'given' | 'path' | 'target' | 'anchor' | 'empty';

interface MiniCell {
  value?: number;
  status: MiniCellStatus;
}

const statusStyles: Record<MiniCellStatus, string> = {
  given: 'bg-copy-muted/20 text-copy font-bold border border-border',
  path: 'bg-primary/5 text-primary border border-primary-muted',
  anchor: 'bg-warning/30 text-copy border border-warning font-bold',
  target: 'bg-primary/5 text-primary border-2 border-dashed border-primary',
  empty: 'bg-surface text-copy-muted border border-border',
};

const goalExample: MiniCell[] = [
  { value: 1, status: 'given' },
  { value: 2, status: 'path' },
  { value: 3, status: 'path' },
  { value: 9, status: 'given' },
  { value: 8, status: 'path' },
  { value: 4, status: 'path' },
  { value: 7, status: 'path' },
  { value: 6, status: 'path' },
  { value: 5, status: 'path' },
];

const controlBadges = [
  { label: 'Guide', helper: 'Show / hide hints' },
  { label: 'Undo / Redo', helper: 'Step back or forward' },
  { label: 'Hold to erase', helper: 'Press + hold to clear' },
  { label: '+/- toggle', helper: 'Flip next vs previous' },
];

const MINI_CELL_SIZE = 46;
const MINI_GAP = 3;
const MINI_PADDING = 8;

function MiniGrid({
  cells,
  arrowSequence,
}: {
  cells: MiniCell[];
  arrowSequence?: number[];
}) {
  const gridSide =
    MINI_PADDING * 2 + MINI_CELL_SIZE * 3 + MINI_GAP * 2;
  const points =
    arrowSequence
      ?.map((value) => {
        if (value === undefined) return null;
        const idx = cells.findIndex((cell) => cell.value === value);
        if (idx === -1) return null;
        const row = Math.floor(idx / 3);
        const col = idx % 3;
        const x =
          MINI_PADDING +
          col * (MINI_CELL_SIZE + MINI_GAP) +
          MINI_CELL_SIZE / 2;
        const y =
          MINI_PADDING +
          row * (MINI_CELL_SIZE + MINI_GAP) +
          MINI_CELL_SIZE / 2;
        return `${x},${y}`;
      })
      .filter(Boolean)
      .join(' ');

  return (
    <div className="relative inline-flex" aria-hidden="true">
      <div
        className="relative grid grid-cols-3 rounded-2xl bg-surface-inverse/5 w-fit"
        style={{
          padding: MINI_PADDING,
          gap: MINI_GAP,
        }}
      >
        {cells.map((cell, idx) => (
          <div
            key={idx}
            className={`flex items-center justify-center rounded-lg text-base font-semibold ${statusStyles[cell.status]}`}
            style={{
              width: MINI_CELL_SIZE,
              height: MINI_CELL_SIZE,
            }}
          >
            {cell.value ?? ''}
          </div>
        ))}
      </div>
      {points && points.length > 0 && (
        <svg
          className="pointer-events-none absolute left-0 top-0"
          style={{ width: gridSide, height: gridSide }}
          viewBox={`0 0 ${gridSide} ${gridSide}`}
        >
          <defs>
            <marker
              id="tutorial-arrow"
              markerWidth="8"
              markerHeight="8"
              refX="7"
              refY="4"
              orient="auto"
              markerUnits="strokeWidth"
            >
              <path d="M0,0 L8,4 L0,8 z" fill="rgb(var(--color-primary))" />
            </marker>
          </defs>
          <polyline
            points={points}
            fill="none"
            stroke="rgb(var(--color-primary))"
            strokeWidth={3}
            strokeLinecap="round"
            strokeLinejoin="round"
            markerEnd="url(#tutorial-arrow)"
          />
        </svg>
      )}
    </div>
  );
}

interface TutorialCardProps {
  title: string;
  punchline: string;
  children: ReactNode;
  className?: string;
}

function TutorialCard({
  title,
  punchline,
  children,
  className,
}: TutorialCardProps) {
  return (
    <div
      className={`flex h-full flex-col gap-4 rounded-3xl border border-border bg-surface p-5 shadow-lg shadow-primary-strong/10 ${
        className ?? ''
      }`}
    >
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-primary">
          {title}
        </p>
        {punchline && (
          <p className="text-xl font-bold text-copy">{punchline}</p>
        )}
      </div>
      {children}
    </div>
  );
}

export function TutorialSplash({ isOpen, onClose }: TutorialSplashProps) {
  useEffect(() => {
    if (!isOpen) return;
    const handleKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') {
        onClose();
      }
    };
    document.addEventListener('keydown', handleKey);
    return () => document.removeEventListener('keydown', handleKey);
  }, [isOpen, onClose]);

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          <motion.div
            className="fixed inset-0 z-40 bg-surface-inverse/85 backdrop-blur-sm"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={onClose}
          />

          <motion.div
            className="fixed inset-0 z-50 overflow-y-auto"
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.96 }}
            transition={{ duration: 0.18, ease: 'easeOut' }}
          >
            <div className="flex min-h-full items-center justify-center p-4">
              <div
                role="dialog"
                aria-modal="true"
                aria-labelledby="tutorial-heading"
                className="relative flex w-full max-w-3xl flex-col gap-5 overflow-hidden rounded-3xl bg-gradient-to-br from-surface-muted via-surface to-primary-muted p-6 shadow-2xl shadow-primary-strong/10 ring-1 ring-surface-inverse max-h-[calc(100vh-2rem)] overflow-y-auto"
                onClick={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  aria-label="Close tutorial"
                  onClick={onClose}
                  className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-full border border-border bg-surface text-copy-muted transition hover:text-copy focus-visible:outline focus-visible:outline-2 focus-visible:outline-primary"
                >
                  x
                </button>

                <div className="grid gap-3 md:grid-cols-2">
                  <TutorialCard
                    title="Welcome to Number Flow"
                    punchline="Fill every square in order."
                    className="md:col-span-2"
                  >
                    <div className="flex flex-col gap-2 md:flex-row md:items-center">
                      <div className="flex-1">
                        <p className="text-base text-copy">
                          Tap any filled number, place the next value in a neighbor square (diagonals count) so the chain never breaks.
                        </p>
                      </div>
                      <div className="flex justify-center md:ml-4 md:justify-end">
                        <MiniGrid
                          cells={goalExample}
                          arrowSequence={[1, 2, 3, 4, 5, 6, 7, 8, 9]}
                        />
                      </div>
                    </div>
                  </TutorialCard>

                  <TutorialCard
                    title="Quick controls"
                    punchline="Keep the board in rhythm."
                  >
                    <div className="grid gap-2 sm:grid-cols-2">
                      {controlBadges.map((badge) => (
                        <div
                          key={badge.label}
                          className="rounded-2xl border border-border bg-surface px-3 py-2 text-sm font-semibold text-copy"
                        >
                          <p>{badge.label}</p>
                          <p className="text-xs font-normal text-copy-muted">
                            {badge.helper}
                          </p>
                        </div>
                      ))}
                    </div>
                  </TutorialCard>
                </div>

                <div className="flex flex-col gap-3 rounded-2xl bg-surface-inverse px-4 py-5 text-white md:flex-row md:items-center md:justify-between">
                  <p className="text-lg font-semibold">
                    Ready to chase the perfect flow?
                  </p>
                  <button
                    type="button"
                    onClick={onClose}
                    className="inline-flex items-center justify-center rounded-full bg-surface px-6 py-3 text-base font-semibold text-copy shadow-sm transition hover:bg-surface-muted"
                  >
                    Got it, let me play
                  </button>
                </div>
              </div>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
