# Research: Daily Puzzle Size Options

## Decisions & Rationale

### 1. Track daily puzzles by size with deterministic rotation

- **Decision**: Extend the daily selection logic so that it chooses a puzzle deterministically per `(date, size)` and tracks exhaustion per size. When all eligible puzzles of a given size have been used for past dates, the sequence wraps and starts again from the first puzzle for that size.
- **Rationale**: Keeps daily play reproducible and fair while ensuring long-term variety. Wrapping after exhaustion avoids hard failures when packs are finite.
- **Alternatives considered**:
  - Pure random per day/size without tracking exhaustion (rejected: can repeat the same puzzle too often and breaks determinism expectations).
  - One global sequence ignoring size (rejected: contradicts requirement that each size has its own daily track and progress).

### 2. Per-size daily progress and stats

- **Decision**: Maintain separate game state and completion stats for each `(date, size)` combination instead of a single daily state.
- **Rationale**: Allows users to play multiple sizes in the same day, with sensible progress when switching between them; also keeps completion stats meaningful per size.
- **Alternatives considered**:
  - Single shared daily state regardless of size (rejected: switching sizes would overwrite or conflate progress between different boards).
  - Per-size global progress ignoring date (rejected: daily puzzles are date-based; we want fresh stats per day).

### 3. UI placement and style for size selector

- **Decision**: Use a compact pill/button group placed near the top of the daily page, aligned with or just below the title and stats (time/moves), with one pill active at a time (Small, Medium, Large). Styling should match existing pills (e.g., SessionStats) to avoid visual clutter.
- **Rationale**: Keeps the selector discoverable but out of the main play area, and visually consistent with existing UI tokens. Reduces clutter compared to large cards or separate panels.
- **Alternatives considered**:
  - Modal or dropdown for size selection (rejected: adds interaction friction and hides an important choice).
  - Left or right sidebar (rejected: more layout complexity and visual weight than necessary).

### 4. Handling exhaustion of daily puzzles per size

- **Decision**: When the daily rotation for a size reaches beyond the number of available puzzles, wrap around and restart from the beginning of that size’s pool while keeping determinism (i.e., a given `(date, size)` always maps to a specific index modulo count).
- **Rationale**: Satisfies the requirement to "reset and start over" when we run out of puzzles while keeping a simple, deterministic mapping.
- **Alternatives considered**:
  - Stop offering that size when exhausted (rejected: user-facing requirement is to reset and start over).
  - Auto-import or generate new puzzles (rejected: outside scope of current feature; belongs to generator pipeline).

### 5. Persistence keys and progress behavior when switching sizes

- **Decision**: Use distinct persistence keys for each `(date, size)` (e.g., `daily-YYYY-MM-DD-small`, `daily-YYYY-MM-DD-medium`, `daily-YYYY-MM-DD-large`) and store corresponding grid state and stats. When switching sizes, the UI loads or initializes the relevant state without affecting others.
- **Rationale**: Clean separation of progress and completion stats between sizes avoids collisions and makes behavior predictable when hopping between puzzles.
- **Alternatives considered**:
  - Encode size only in memory (rejected: would lose progress between sessions or reloads).
  - Store size in a single mixed state object (rejected: more fragile and harder to reason about than separate keys per size).
