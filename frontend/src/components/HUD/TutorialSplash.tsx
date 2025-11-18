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
  given: 'bg-slate-200 text-slate-700 font-bold',
  path: 'bg-white text-blue-600 border border-blue-200',
  anchor: 'bg-amber-200 text-slate-900 border border-amber-400 font-bold',
  target: 'bg-white text-blue-600 border-2 border-dashed border-blue-400',
  empty: 'bg-white text-slate-300 border border-slate-200',
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
        className="relative grid grid-cols-3 rounded-2xl bg-slate-900/5 w-fit"
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
              <path d="M0,0 L8,4 L0,8 z" fill="#2563eb" />
            </marker>
          </defs>
          <polyline
            points={points}
            fill="none"
            stroke="#2563eb"
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
      className={`flex h-full flex-col gap-4 rounded-3xl border border-slate-200 bg-white/95 p-5 shadow-lg shadow-slate-500/10 ${
        className ?? ''
      }`}
    >
      <div>
        <p className="text-sm font-semibold uppercase tracking-wide text-blue-600">
          {title}
        </p>
        {punchline && (
          <p className="text-xl font-bold text-slate-900">{punchline}</p>
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
            className="fixed inset-0 z-40 bg-slate-900/70 backdrop-blur-sm"
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
                className="relative flex w-full max-w-3xl flex-col gap-5 overflow-hidden rounded-3xl bg-gradient-to-br from-slate-50 via-white to-blue-50 p-6 shadow-2xl shadow-blue-900/10 ring-1 ring-slate-900/10 max-h-[calc(100vh-2rem)] overflow-y-auto"
                onClick={(event) => event.stopPropagation()}
              >
                <button
                  type="button"
                  aria-label="Close tutorial"
                  onClick={onClose}
                  className="absolute right-4 top-4 inline-flex h-10 w-10 items-center justify-center rounded-full border border-slate-200 bg-white text-slate-500 transition hover:text-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-blue-500"
                >
                  x
                </button>

                <div className="grid gap-3 md:grid-cols-2">
                  <TutorialCard
                    title="Welcome to Number Flow"
                    punchline=""
                    className="md:col-span-2"
                  >
                    <div className="flex flex-col gap-4 md:flex-row md:items-center">
                      <div className="flex-1">
                        <p
                          id="tutorial-heading"
                          className="text-2xl font-extrabold text-slate-900"
                        >
                          Fill every square from 1 to N without breaking the path.
                        </p>
                        <p className="text-base text-slate-700">
                          Tap any filled number to steer the anchor, then place the next value in a touching square (diagonals count) so the chain never breaks&mdash;flip on Guide if you want the legal squares to glow.
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
                          className="rounded-2xl border border-slate-200 bg-white px-3 py-2 text-sm font-semibold text-slate-900"
                        >
                          <p>{badge.label}</p>
                          <p className="text-xs font-normal text-slate-500">
                            {badge.helper}
                          </p>
                        </div>
                      ))}
                    </div>
                  </TutorialCard>
                </div>

                <div className="flex flex-col gap-3 rounded-2xl bg-slate-900/80 px-4 py-5 text-white md:flex-row md:items-center md:justify-between">
                  <p className="text-lg font-semibold">
                    Ready to chase the perfect flow?
                  </p>
                  <button
                    type="button"
                    onClick={onClose}
                    className="inline-flex items-center justify-center rounded-full bg-white/95 px-6 py-3 text-base font-semibold text-slate-900 shadow-sm transition hover:bg-white"
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
