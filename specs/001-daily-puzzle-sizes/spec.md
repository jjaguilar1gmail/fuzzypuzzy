# Feature Specification: Daily Puzzle Size Options

**Feature Branch**: `001-daily-puzzle-sizes`  
**Created**: 2025-11-16  
**Status**: Draft  
**Input**: User description: "I want to make the front end user interface provide 3 different options for daily puzzle (small - 5x5, medium - 6x6, large - 7x7). The reason is so that people can have more options for play size."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Select Daily Puzzle Size (Priority: P1)

As a player visiting the daily puzzle page, I can see three size options (Small 5×5, Medium 6×6, Large 7×7) and select one, so the puzzle loads with my preferred size for today's challenge.

**Why this priority**: This is the core feature—giving players choice in puzzle complexity and time commitment. A small puzzle might take 2-3 minutes while a large puzzle could take 10-15 minutes, accommodating different play sessions.

**Independent Test**: Navigate to the daily puzzle page, verify three size buttons are visible, click "Medium 6×6", confirm a 6×6 puzzle loads with the correct number of cells (36 total).

**Acceptance Scenarios**:

1. **Given** I am on the daily puzzle page, **When** the page loads, **Then** I see three clearly labeled size options: "Small (5×5)", "Medium (6×6)", and "Large (7×7)"
2. **Given** the size options are displayed, **When** I click "Small (5×5)", **Then** a 5×5 puzzle (25 cells) loads and gameplay begins
3. **Given** the size options are displayed, **When** I click "Medium (6×6)", **Then** a 6×6 puzzle (36 cells) loads and gameplay begins
4. **Given** the size options are displayed, **When** I click "Large (7×7)", **Then** a 7×7 puzzle (49 cells) loads and gameplay begins

---

### User Story 2 - Persistent Size Preference (Priority: P2)

As a player who has selected a preferred puzzle size, I want my choice to be remembered on subsequent visits, so I don't have to reselect my preferred size each day.

**Why this priority**: Reduces friction for returning players. If someone prefers medium puzzles, they shouldn't need to click the same button every day.

**Independent Test**: For a first-time visitor, load the daily puzzle page and verify that a Medium (6×6) puzzle is automatically selected and loaded without extra clicks. Then change the size to "Large (7×7)", complete or leave the puzzle, close the browser, return to the daily puzzle page, and verify "Large" is pre-selected or automatically loads instead of Medium.

**Acceptance Scenarios**:

1. **Given** I have selected "Medium (6×6)" on a previous visit, **When** I return to the daily puzzle page, **Then** the Medium option is highlighted or automatically loads
2. **Given** I have never visited before, **When** I land on the daily puzzle page, **Then** a default size (Medium 6×6) is pre-selected and a Medium (6×6) puzzle is automatically loaded
3. **Given** I have a saved preference for "Small", **When** I explicitly select "Large", **Then** my preference updates to "Large" for future visits

---

### User Story 3 - Different Puzzle per Size (Priority: P1)

As a player who wants variety, I expect each size option to load a different puzzle, so I can play multiple puzzles on the same day if I choose different sizes.

**Why this priority**: Core value proposition—allows engaged players to play up to 3 puzzles daily (one per size). Without this, size selection would only affect difficulty, not content.

**Independent Test**: Play "Small (5×5)" puzzle to completion, then select "Large (7×7)" and verify a completely different puzzle loads (different seed, different givens, not just scaled).

**Acceptance Scenarios**:

1. **Given** I complete a "Small (5×5)" puzzle, **When** I select "Medium (6×6)", **Then** a different puzzle with different clues and solution loads
2. **Given** I have played "Medium" today, **When** I select "Small" or "Large", **Then** each loads a unique puzzle I haven't seen today
3. **Given** it is the same date, **When** I reload "Small (5×5)" multiple times, **Then** the same small puzzle loads consistently (deterministic per date+size)

---

### Edge Cases

- What happens when no puzzles of the selected size are available in the puzzle pool (e.g., only 5×5 and 7×7 puzzles exist)? System should show unavailable sizes as disabled/grayed out or display an error message after selection.
- What if a user's saved preference size is no longer available? System should fall back to an available size (preferably closest to saved preference) and optionally notify the user.
- How does the system handle the transition between days? At midnight local time, all three sizes should reset to new puzzles for the new date.
- What if the user is mid-puzzle when selecting a different size? Unsaved progress on the current puzzle should be auto-saved (per existing persistence logic) before loading the new size.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST display three size options on the daily puzzle page: Small (5×5), Medium (6×6), and Large (7×7)
- **FR-002**: System MUST load a puzzle matching the selected size when a size option is clicked
- **FR-003**: System MUST select a deterministic puzzle for each size+date combination (same size on same date always returns the same puzzle)
- **FR-004**: System MUST filter the puzzle pool by size when selecting the daily puzzle (only 5×5 puzzles for Small, only 6×6 for Medium, only 7×7 for Large)
- **FR-005**: Users MUST be able to switch between size options at any time, loading a different puzzle for each size
- **FR-006**: System MUST persist the user's last selected size preference in local storage
- **FR-007**: System MUST restore the saved size preference on subsequent page visits
- **FR-008**: System MUST apply the default size (Medium 6×6) when no preference is saved
- **FR-009**: System MUST auto-save the current puzzle state before switching to a different size
- **FR-010**: System MUST maintain separate game states (progress, time, mistakes) for each size on the same date
- **FR-011**: System MUST show visual feedback indicating which size is currently selected (e.g., highlighted button, bold text, active state styling)
- **FR-012**: System MUST disable or indicate unavailable size options when no puzzles of that size exist in the available packs
- **FR-013**: System MUST generate unique persistence keys for each size+date combination to prevent state conflicts (e.g., "daily-2025-11-16-small", "daily-2025-11-16-medium")

### Key Entities

- **DailySizeOption**: Represents a size choice (small/medium/large) with associated dimensions (5×5, 6×6, 7×7) and display label
- **SizePreference**: User's saved preference for puzzle size, stored in local storage, with timestamp of last update
- **DailyPuzzleState**: Extended game state that includes size identifier, allowing separate progress tracking per size per day

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Users can select any of three size options and see a puzzle load within 2 seconds
- **SC-002**: Each size option loads a unique puzzle on the same date (verified by different seeds or givens)
- **SC-003**: 95% of users with a saved size preference see their preferred size load automatically on return visits
- **SC-004**: Users can complete puzzles in all three sizes on the same day, with progress tracked separately for each
- **SC-005**: Switching between sizes preserves current progress for each size without data loss or corruption
- **SC-006**: The size selection UI is immediately understandable (measured by first-time users selecting a size within 5 seconds of page load)

## Clarifications

### Session 2025-11-16

- Q: What should be the default daily puzzle size and behavior on first visit vs. later visits? → A: Default to Medium (6×6) and auto-load it on first visit; on later visits, auto-load the user's last chosen size instead.
