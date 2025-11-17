# Quickstart: Daily Puzzle Size Options

## Goal

Enable three daily puzzle sizes (Small 5×5, Medium 6×6, Large 7×7) on the daily page with:
- Medium 6×6 auto-loaded by default for first-time visitors
- Per-size deterministic daily puzzle selection
- Separate progress and completion stats per size
- A clean, unobtrusive size selector that fits the existing HUD.

## Where to work

- Daily selection logic: `frontend/src/lib/daily.ts`
- Daily page UI & layout: `frontend/src/pages/index.tsx`
- Game & progress state: `frontend/src/state/gameStore.ts`, `frontend/src/state/progressStore.ts`
- Persistence helpers: `frontend/src/lib/persistence.ts`
- Tests to extend:
  - `frontend/tests/integration/daily-play.test.tsx`
  - `frontend/tests/unit/components/Grid.test.tsx` (if grid behavior changes)
  - Any new tests for size selector UX.

## Implementation steps (high level)

1. **Extend daily selection to be size-aware**
   - Add a notion of `sizeId` (small/medium/large) and filter packs by puzzle size.
   - For each `(date, sizeId)`, compute a deterministic index into that size’s puzzle list with wrap-around.

2. **Introduce per-size persistence keys**
   - Change or extend `getDailyPuzzleKey()` to incorporate size (e.g., `daily-YYYY-MM-DD-medium`).
   - Ensure game state save/load functions use the size-aware key.

3. **Add a size selector UI to the daily page**
   - Place a pill/button group near the title and stats at the top.
   - Style it consistently with existing pills (e.g., SessionStats) with clear active state.
   - Wire it to select size and trigger loading of the corresponding daily puzzle.

4. **Track size preference**
   - Store the last selected size in local storage.
   - On first visit without preference, default to Medium 6×6 and auto-load.
   - On subsequent visits, auto-load the preferred size.

5. **Ensure sensible progress when switching sizes**
   - When switching size, save the current size’s progress, then load or initialize the target size’s state from its key.
   - Keep stats (time, moves, mistakes, completion) separate per size.

6. **Update tests**
   - Add or extend tests to cover:
     - Default Medium 6×6 auto-load on first visit.
     - Size selector visibility and active state.
     - Per-size daily selection determinism.
     - Per-size progress persistence when switching.

You can implement these steps incrementally; the tests and daily page will give quick feedback as you wire things up.
