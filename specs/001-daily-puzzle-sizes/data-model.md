# Data Model: Daily Puzzle Size Options

## Entities

### DailySizeOption
- **id**: one of `"small" | "medium" | "large"`
- **rows**: 5, 6, or 7
- **cols**: 5, 6, or 7
- **label**: display name (e.g., "Small (5×5)")
- **order**: numeric ordering for UI (e.g., 1=small, 2=medium, 3=large)

### SizePreference
- **sizeId**: `"small" | "medium" | "large"`
- **updatedAt**: ISO date-time string of last change (optional for analytics)

### DailyPuzzleKey
- **date**: string `YYYY-MM-DD`
- **sizeId**: `"small" | "medium" | "large"`
- **storageKey**: derived string used for persistence (e.g., `daily-2025-11-16-medium`)

### DailyPuzzleState
- **storageKey**: link to `DailyPuzzleKey.storageKey`
- **puzzleId**: underlying puzzle identifier (e.g., from packs JSON)
- **packId**: pack identifier containing the puzzle
- **sizeId**: `"small" | "medium" | "large"`
- **gridState**: serialized game grid for this puzzle/size/date
- **elapsedMs**: total elapsed play time in milliseconds
- **moveCount**: number of moves taken
- **mistakes**: number of mistakes (if tracked)
- **completedAt**: ISO date-time when this size’s puzzle was completed (optional)

## Relationships

- `DailySizeOption` is a fixed, in-memory configuration (no dynamic creation) and is referenced by `SizePreference`, `DailyPuzzleKey`, and `DailyPuzzleState` via `sizeId`.
- `DailyPuzzleState.storageKey` is derived from `(date, sizeId)` and is unique per day and size.
- `DailyPuzzleState.puzzleId` + `DailyPuzzleState.packId` must reference a valid puzzle in the available packs; the daily selection logic ensures this.

## State Transitions (per (date, sizeId))

1. **Initial load (no saved state)**
   - Input: `(date, sizeId)` and puzzle pool filtered by size.
   - Behavior: Determine deterministic index for `(date, sizeId)`, select `packId`/`puzzleId`, initialize `DailyPuzzleState` with empty grid and zeroed stats.

2. **Resume existing state**
   - Input: `(date, sizeId)` and existing persisted `DailyPuzzleState`.
   - Behavior: Load gridState and stats from persistence, hydrate game store, and render current progress.

3. **In-play updates**
   - On move/time/mistake changes, update in-memory state and periodically persist `DailyPuzzleState` under its `storageKey`.

4. **Completion**
   - When a puzzle is solved, mark `completedAt` and keep stats for this `(date, sizeId)`.

5. **Switching sizes on the same date**
   - When user selects a different size, compute its `DailyPuzzleKey`, load or initialize its `DailyPuzzleState`, and update UI without modifying other sizes’ states.

6. **Exhaustion & wrap-around**
   - Over long periods, when the deterministic index exceeds the size-specific puzzle pool length, use modular arithmetic to wrap so each `(date, sizeId)` maps into the available puzzles.
