# Feature Specification: Hidato Terminal MVP

**Feature Branch**: `001-hidato-terminal-mvp`  
**Created**: 2025-11-04  
**Status**: Draft  
**Input**: User description: "I am building a fuzzy puzzy hidato MVP that I can play in the terminal and print to the screen with easy puzzles first. I can generate 5x5 or 7x7 puzzles and see them in the terminal as a neat grid. The puzzle shows a handful of givens (including 1 and N). We're starting with a simple puzzle generator (serpentine) and a simple solver (consecutive logic)."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Generate and View Easy Puzzle (Priority: P1)

As a player, I can create an easy Hidato puzzle (5x5 or 7x7) and see it printed neatly in my terminal, including a handful of givens such as 1 and N, so I can start playing immediately.

**Why this priority**: Core value of the MVP is to produce a playable puzzle and render it clearly in the terminal.

**Independent Test**: Run the command to generate a 5x5 puzzle; verify the grid renders with 1 and 25 shown, a small set of other givens, and proper blocked/empty cell display.

**Acceptance Scenarios**:

1. Given no prior puzzle, When the user asks for a 5x5 easy puzzle, Then a 5x5 grid is printed with 1 and 25 among the givens and consistent formatting.
2. Given no prior puzzle, When the user asks for a 7x7 easy puzzle, Then a 7x7 grid is printed with 1 and 49 among the givens and consistent formatting.

---

### User Story 2 - Make a Move with Validation (Priority: P2)

As a player, I can enter a number into an empty cell; the system validates whether the move is legal (consecutive to an adjacent number and within range) and accepts or rejects it with a clear message.

**Why this priority**: Enables actual play, not just viewing; validation ensures a guided experience for beginners.

**Independent Test**: On a generated easy puzzle, attempt both valid and invalid moves; confirm valid moves are accepted and invalid moves are rejected with a clear reason.

**Acceptance Scenarios**:

1. Given an empty cell adjacent to a placed k, When the user places k+1 in that cell, Then the move is accepted and the grid updates.
2. Given an empty cell not adjacent to k, When the user places k+1 in that cell, Then the move is rejected with a message indicating adjacency rules.

---

### User Story 3 - Get a Hint or Auto-Solve (Priority: P3)

As a player, I can request a single hint (next safe placement) or ask the system to solve the puzzle completely using consecutive-logic, so I can learn or finish quickly.

**Why this priority**: Demonstrates built-in solver capabilities for presentation; helps users progress if stuck.

**Independent Test**: On a generated easy puzzle, request a hint and verify it points to a valid next placement; request auto-solve and verify a complete valid path is produced.

**Acceptance Scenarios**:

1. Given a valid partial board, When the user requests a hint, Then the system highlights one legal next placement consistent with the givens and constraints.
2. Given a valid partial board, When the user requests auto-solve, Then the puzzle completes with a valid sequence respecting adjacency and no duplicates.

---

### Edge Cases

- Requesting a size other than 5x5 or 7x7 returns a clear message listing supported sizes.
- Generator fails to find a valid serpentine path within time limit: prints a friendly error and suggests trying again.
- Duplicate number attempt or number out of allowed range is rejected with a specific message.
- Attempt to overwrite a given or blocked cell is rejected.
- Terminal window too narrow to display full grid results in wrapped lines; the system indicates recommended minimum width.

## Requirements *(mandatory)*

### Functional Requirements

- FR-001: Users MUST be able to generate an easy Hidato puzzle in the terminal for sizes 5x5 and 7x7.
- FR-002: Generated puzzles MUST include a small set of givens, explicitly containing 1 and N (N = grid size squared minus blocked cells, if any).
- FR-003: The generator MUST produce a simple serpentine solution path as the underlying valid sequence for easy puzzles.
- FR-004: The terminal renderer MUST display a clean, aligned grid indicating numbers, empty cells, and blocked cells distinctly.
- FR-005: Users MUST be able to attempt moves (placing a number) and receive immediate validation feedback.
- FR-006: The system MUST enforce Hidato constraints: values are within min..max and consecutive numbers occupy adjacent cells per 4- or 8-neighbor rule defined for the puzzle.
- FR-007: Users MUST be able to request a single-step hint that returns a valid next placement without altering givens.
- FR-008: Users MUST be able to trigger an auto-solve that fills remaining cells if the puzzle is solvable under the given constraints.
- FR-009: The system MUST ensure puzzles presented for play have a valid complete path (internally verified before display).
- FR-010: If the system cannot generate a valid puzzle within a reasonable time, it MUST inform the user and allow retry.

### Key Entities

- Puzzle: A playable instance containing grid layout, givens, rules (adjacency, range), and difficulty label.
- Grid/Cell: The board structure and its cells, including blocked, given, empty, and filled states.
- Constraints: Rules controlling allowed values, adjacency (4 vs 8), and connectivity.
- Move: A user-intended placement of a specific number at a position, subject to validation.
- Preset: A named configuration capturing size (5x5, 7x7) and easy difficulty (serpentine generation, consecutive solver).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- SC-001: A 5x5 easy puzzle generates and renders in the terminal in under 2 seconds on a typical laptop.
- SC-002: A 7x7 easy puzzle generates and renders in the terminal in under 3 seconds on a typical laptop.
- SC-003: Auto-solve completes for 5x5 in under 2 seconds and for 7x7 in under 4 seconds.
- SC-004: At least 90% of attempted invalid moves produce clear, actionable error messages understood by first-time users in a hallway test.
- SC-005: In a demo run, users can complete a 5x5 easy puzzle using at most 3 hints on average.

