import { useEffect, useMemo, useState, useCallback } from 'react';
import Head from 'next/head';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { Pack, PackSummary, Puzzle } from '@/domain/puzzle';
import {
  loadSandboxPack,
  loadSandboxPacksList,
  loadSandboxPuzzle,
} from '@/lib/loaders/playground';
import { useGameStore } from '@/state/gameStore';
import GuidedGrid from '@/components/Grid/GuidedGrid';
import { SessionStats } from '@/components/HUD/SessionStats';
import CompletionModal from '@/components/HUD/CompletionModal';

type LoadState = 'idle' | 'loading' | 'ready' | 'error';

const formatPercent = (value?: number) => {
  if (typeof value !== 'number') return '—';
  return `${(value * 100).toFixed(1)}%`;
};

const formatNumber = (value?: number) => {
  if (typeof value !== 'number' || Number.isNaN(value)) return '—';
  return value.toLocaleString();
};

const formatMs = (value?: number) => {
  if (typeof value !== 'number') return '—';
  return `${value.toFixed(0)} ms`;
};

export default function PlaygroundPage() {
  const [packs, setPacks] = useState<PackSummary[]>([]);
  const [packState, setPackState] = useState<LoadState>('idle');
  const [puzzleState, setPuzzleState] = useState<LoadState>('idle');
  const [packError, setPackError] = useState<string | null>(null);
  const [puzzleError, setPuzzleError] = useState<string | null>(null);
  const [selectedPackId, setSelectedPackId] = useState<string>('');
  const [selectedPuzzleId, setSelectedPuzzleId] = useState<string>('');
  const [currentPack, setCurrentPack] = useState<Pack | null>(null);
  const [currentPuzzle, setCurrentPuzzle] = useState<Puzzle | null>(null);

  const loadPuzzleIntoStore = useGameStore((state) => state.loadPuzzle);
  const completionStatus = useGameStore((state) => state.completionStatus);
  const dismissCompletionStatus = useGameStore((state) => state.dismissCompletionStatus);

  useEffect(() => {
    let mounted = true;
    loadSandboxPacksList()
      .then((list) => {
        if (!mounted) return;
        setPacks(list);
        if (list.length > 0) {
          setSelectedPackId((prev) => prev || list[0].id);
        }
      })
      .catch((err) => {
        console.error(err);
        if (mounted) {
          setPackError(err.message);
        }
      });
    return () => {
      mounted = false;
    };
  }, []);

  useEffect(() => {
    if (!selectedPackId) {
      setCurrentPack(null);
      setSelectedPuzzleId('');
      return;
    }
    setPackState('loading');
    setPackError(null);
    loadSandboxPack(selectedPackId)
      .then((pack) => {
        setCurrentPack(pack);
        if (!selectedPuzzleId || !pack.puzzles.includes(selectedPuzzleId)) {
          setSelectedPuzzleId(pack.puzzles[0] ?? '');
        }
        setPackState('ready');
      })
      .catch((err) => {
        console.error(err);
        setPackError(err.message);
        setPackState('error');
      });
  }, [selectedPackId]);

  useEffect(() => {
    if (!selectedPackId || !selectedPuzzleId) {
      setCurrentPuzzle(null);
      return;
    }
    setPuzzleState('loading');
    setPuzzleError(null);
    loadSandboxPuzzle(selectedPackId, selectedPuzzleId)
      .then((puzzle) => {
        setCurrentPuzzle(puzzle);
        loadPuzzleIntoStore(puzzle);
        setPuzzleState('ready');
      })
      .catch((err) => {
        console.error(err);
        setPuzzleError(err.message);
        setPuzzleState('error');
      });
  }, [selectedPackId, selectedPuzzleId, loadPuzzleIntoStore]);

  const currentPuzzleIndex = useMemo(() => {
    if (!currentPack || !selectedPuzzleId) return -1;
    return currentPack.puzzles.indexOf(selectedPuzzleId);
  }, [currentPack, selectedPuzzleId]);

  const handleNavigate = useCallback(
    (direction: 'prev' | 'next') => {
      if (!currentPack || currentPuzzleIndex === -1) return;
      const nextIndex = direction === 'prev' ? currentPuzzleIndex - 1 : currentPuzzleIndex + 1;
      if (nextIndex < 0 || nextIndex >= currentPack.puzzles.length) return;
      setSelectedPuzzleId(currentPack.puzzles[nextIndex]);
    },
    [currentPack, currentPuzzleIndex]
  );

  const metrics = currentPuzzle?.metrics;
  const solverMetrics = (metrics?.solver ?? {}) as Record<string, number>;
  const structureMetrics = (metrics?.structure ?? {}) as Record<string, any>;
  const branching = structureMetrics?.branching ?? {};
  const givensInfo = structureMetrics?.givens ?? {};
  const timings = metrics?.timings_ms ?? {};

  const metricCards = [
    { label: 'Clue Density', value: formatPercent(solverMetrics.clue_density) },
    { label: 'Logic Ratio', value: formatPercent(solverMetrics.logic_ratio) },
    {
      label: 'Avg Branching',
      value: formatNumber(branching.average_branching_factor),
    },
    { label: 'Search Nodes', value: formatNumber(solverMetrics.nodes) },
    { label: 'Search Depth', value: formatNumber(solverMetrics.depth) },
    {
      label: 'Generation Time',
      value: formatMs(timings.generation ?? timings.total),
    },
  ];

  return (
    <>
      <Head>
        <title>Metrics Playground | Hidato Sandbox</title>
      </Head>
      <main className="min-h-screen bg-slate-950 text-slate-100 p-4 md:p-8">
        <div className="max-w-7xl mx-auto grid gap-6 lg:grid-cols-[320px,1fr]">
          <aside className="bg-slate-900/60 border border-slate-800 rounded-2xl p-4 flex flex-col gap-4">
            <div>
              <p className="text-xs uppercase tracking-wide text-slate-400 mb-1">Environment</p>
              <h1 className="text-xl font-semibold">Sandbox Packs</h1>
              <p className="text-sm text-slate-400">
                Packs loaded from <code className="text-xs bg-slate-800 px-1 py-0.5 rounded">public/packs/playground</code>.
              </p>
            </div>
            {packs.length === 0 ? (
              <div className="text-sm text-slate-400 space-y-2">
                <p>No sandbox packs detected.</p>
                <p>
                  Generate a pack with the CLI and place it under{' '}
                  <code className="text-xs bg-slate-800 px-1 py-0.5 rounded">
                    frontend/public/packs/playground/&lt;pack-id&gt;
                  </code>
                  , then update <code className="text-xs bg-slate-800 px-1 py-0.5 rounded">index.json</code>.
                </p>
              </div>
            ) : (
              <>
                <label className="text-xs uppercase tracking-wide text-slate-400">
                  Select pack
                  <select
                    className="mt-1 w-full rounded-lg bg-slate-800/70 border border-slate-700 px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
                    value={selectedPackId}
                    onChange={(e) => setSelectedPackId(e.target.value)}
                  >
                    {packs.map((pack) => (
                      <option key={pack.id} value={pack.id}>
                        {pack.title}
                      </option>
                    ))}
                  </select>
                </label>
                <div className="space-y-2">
                  <p className="text-xs uppercase tracking-wide text-slate-400">Puzzles</p>
                  <div className="max-h-[50vh] overflow-auto pr-1 space-y-1">
                    {currentPack?.puzzles.map((puzzleId, index) => {
                      const isActive = puzzleId === selectedPuzzleId;
                      return (
                        <button
                          key={puzzleId}
                          onClick={() => setSelectedPuzzleId(puzzleId)}
                          className={`w-full text-left px-3 py-2 rounded-lg text-sm border ${
                            isActive
                              ? 'bg-primary/10 border-primary text-primary'
                              : 'bg-slate-900 border-slate-800 hover:border-slate-600'
                          }`}
                        >
                          <div className="font-semibold">Puzzle {index + 1}</div>
                          <div className="text-xs text-slate-400">{puzzleId}</div>
                        </button>
                      );
                    })}
                  </div>
                </div>
              </>
            )}
          </aside>

          <section className="bg-slate-900/40 border border-slate-800 rounded-3xl p-4 md:p-6 space-y-6">
            {packError && (
              <div className="rounded-xl bg-red-900/40 border border-red-800 text-red-200 p-4">
                {packError}
              </div>
            )}
            {puzzleError && (
              <div className="rounded-xl bg-red-900/40 border border-red-800 text-red-200 p-4">
                {puzzleError}
              </div>
            )}
            {packState === 'loading' && <p className="text-slate-400">Loading pack...</p>}
            {puzzleState === 'loading' && <p className="text-slate-400">Preparing puzzle...</p>}
            {currentPack && currentPuzzle && (
              <>
                <div className="flex flex-wrap items-center justify-between gap-4">
                  <div>
                    <p className="text-xs uppercase tracking-wide text-slate-400">Now testing</p>
                    <h2 className="text-3xl font-bold text-white">{currentPack.title}</h2>
                    <p className="text-sm text-slate-400">
                      Puzzle {currentPuzzleIndex + 1} of {currentPack.puzzles.length} · size{' '}
                      {currentPuzzle.size}×{currentPuzzle.size}
                    </p>
                  </div>
                  <div className="flex gap-2">
                    <button
                      className="px-4 py-2 rounded-lg border border-slate-700 text-sm disabled:opacity-40"
                      onClick={() => handleNavigate('prev')}
                      disabled={currentPuzzleIndex <= 0}
                    >
                      Previous
                    </button>
                    <button
                      className="px-4 py-2 rounded-lg border border-slate-700 text-sm disabled:opacity-40"
                      onClick={() => handleNavigate('next')}
                      disabled={
                        currentPuzzleIndex === -1 ||
                        !currentPack ||
                        currentPuzzleIndex >= currentPack.puzzles.length - 1
                      }
                    >
                      Next
                    </button>
                  </div>
                </div>

                <div className="flex justify-center">
                  <SessionStats />
                </div>

                <motion.div
                  initial={{ opacity: 0, y: 16 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.2 }}
                  className="grid xl:grid-cols-[minmax(0,1fr)_280px] gap-6"
                >
                  <div className="bg-slate-900/60 rounded-2xl p-4 border border-slate-800 flex flex-col items-center gap-4">
                    <GuidedGrid />
                  </div>

                  <div className="bg-slate-900/60 rounded-2xl p-4 border border-slate-800">
                    <h3 className="text-lg font-semibold mb-3 text-white">Metrics</h3>
                    <div className="space-y-3">
                      {metricCards.map((card) => (
                        <div
                          key={card.label}
                          className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-sm"
                        >
                          <span className="text-slate-400">{card.label}</span>
                          <span className="font-semibold text-white">{card.value}</span>
                        </div>
                      ))}
                      {givensInfo?.total && (
                        <div className="flex items-center justify-between px-3 py-2 rounded-lg bg-slate-900 border border-slate-800 text-sm">
                          <span className="text-slate-400">Givens</span>
                          <span className="font-semibold text-white">
                            {givensInfo.total} / {currentPuzzle.size * currentPuzzle.size}
                          </span>
                        </div>
                      )}
                    </div>
                    {currentPuzzle.metrics?.structure?.anchors && (
                      <div className="mt-4 text-xs text-slate-400">
                        <p className="font-semibold text-slate-300 mb-1">Anchor spacing</p>
                        <pre className="bg-slate-950/60 rounded-lg p-2 overflow-x-auto">
                          {JSON.stringify(currentPuzzle.metrics.structure.anchors, null, 2)}
                        </pre>
                      </div>
                    )}
                    {currentPuzzle.metrics?.mask && (
                      <div className="mt-4 text-xs text-slate-400">
                        <p className="font-semibold text-slate-300 mb-1">Mask</p>
                        <pre className="bg-slate-950/60 rounded-lg p-2 overflow-x-auto">
                          {JSON.stringify(currentPuzzle.metrics.mask, null, 2)}
                        </pre>
                      </div>
                    )}
                  </div>
                </motion.div>
              </>
            )}
          </section>
        </div>
        <div className="text-center text-slate-500 text-xs mt-6">
          <Link href="/" className="underline hover:text-slate-200">
            Return to daily experience
          </Link>
        </div>
        <CompletionModal isOpen={completionStatus !== null} onClose={dismissCompletionStatus} />
      </main>
    </>
  );
}
