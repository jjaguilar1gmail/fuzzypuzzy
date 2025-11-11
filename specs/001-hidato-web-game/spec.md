# Feature Specification: Hidato Web Game & Puzzle Pack Generator

**Feature Branch**: `001-hidato-web-game`  
**Created**: 2025-11-11  
**Status**: Draft  
**Input**: User description summarized: "Transform Hidato engine into a responsive browser game with elegant tactile UX and provide Python-based puzzle pack generator for bulk pre-generated puzzles."

## User Scenarios & Testing *(mandatory)*

<!--
  IMPORTANT: User stories should be PRIORITIZED as user journeys ordered by importance.
  Each user story/journey must be INDEPENDENTLY TESTABLE - meaning if you implement just ONE of them,
  you should still have a viable MVP (Minimum Viable Product) that delivers value.
  
  Assign priorities (P1, P2, P3, etc.) to each story, where P1 is the most critical.
  Think of each story as a standalone slice of functionality that can be:
  - Developed independently
  - Tested independently
  - Deployed independently
  - Demonstrated to users independently
-->

### User Story 1 - Play a Daily Hidato Puzzle (Priority: P1)

As a casual player, I open the web app on any device and immediately play a curated Hidato puzzle with smooth interactions (tap/click to select cells, number palette, undo, pencil marks) and subtle animations.

**Why this priority**: Core value proposition—delivers immediate playable experience demonstrating puzzle logic + UI polish.

**Independent Test**: Load game, interact with cells, place numbers, finish puzzle; all without requiring account or ancillary features.

**Acceptance Scenarios**:
1. **Given** a loaded puzzle, **When** the player taps an empty cell then a number, **Then** the number appears with adjacency validation feedback (success highlight or error bounce).
2. **Given** a partially filled puzzle, **When** the player completes last correct number, **Then** a completion animation and stats modal appear (time, mistakes, path uniqueness note).
3. **Given** a filled incorrect number, **When** the player taps undo, **Then** the last move is reverted.
4. **Given** an empty cell, **When** the player toggles pencil mode and enters multiple candidate numbers, **Then** small candidate marks appear and can be cleared individually.

---
### User Story 2 - Browse & Select Puzzle Packs (Priority: P2)

As a motivated player, I want to browse available puzzle packs (sets of pre-generated puzzles by size/difficulty/theme) and select one to start a progression.

**Why this priority**: Enables extended engagement beyond single daily play; showcases generator breadth and curated distribution.

**Independent Test**: Load packs list, view metadata (count, difficulties), select pack, launch first puzzle—no dependency on scoring or account creation.

**Acceptance Scenarios**:
1. **Given** the packs catalog screen, **When** the user filters by difficulty = Hard, **Then** only packs with ≥1 hard puzzle remain listed.
2. **Given** a selected pack card, **When** the user taps “Start Pack”, **Then** puzzle #1 loads and pack progress indicator shows 1/N.
3. **Given** a completed puzzle in a pack, **When** the user clicks “Next”, **Then** subsequent puzzle loads and progress increments.

---
### User Story 3 - Generate Puzzle Packs via CLI (Priority: P3)

As an internal maintainer, I run a Python CLI tool to bulk-generate validated unique Hidato puzzles into a structured pack (JSON manifest + individual puzzle files) ready for web import.

**Why this priority**: Supports scalable content pipeline without manual puzzle curation; bridges existing Python engine to frontend asset workflow.

**Independent Test**: Run CLI with parameters (sizes, difficulties, count), verify output directory contains expected manifest and puzzles passing uniqueness and structural checks.

**Acceptance Scenarios**:
1. **Given** the CLI tool, **When** I execute with `--sizes 7,9 --difficulties easy,hard --count 25`, **Then** output includes 50 puzzles grouped by size/difficulty.
2. **Given** a generation run, **When** uniqueness validation fails on a candidate puzzle, **Then** that puzzle is skipped and logged in a summary report (total generated vs skipped).
3. **Given** successful generation, **When** I open the manifest, **Then** each puzzle references file path, size, difficulty, clue density, and seed.

---

### User Story 4 - Mobile Responsive Interaction (Priority: P3)

As a mobile player, I can comfortably play the puzzle with adaptive layout (number palette accessible with thumb, pinch zoom optional, no forced horizontal scroll).

**Why this priority**: Ensures accessibility across devices; expands potential audience reach.

**Independent Test**: Load game in a mobile viewport emulator; verify touch interactions, layout reflow, readable font sizing.

**Acceptance Scenarios**:
1. **Given** a mobile viewport < 480px width, **When** the user opens the game, **Then** puzzle grid scales to fit width and number palette becomes a collapsible bottom sheet.
2. **Given** the collapsed palette, **When** the user swipes up on its handle, **Then** the palette expands showing numbers and pencil toggle.

---

### Edge Cases

- User reloads page mid-puzzle: state should restore (if local persistence available) or clearly notify of reset.
- Puzzle pack selection while current puzzle unsolved: confirm before abandoning current puzzle.
- Attempt to enter non-adjacent number violating Hidato constraints: provide gentle error feedback without blocking other interactions.
- Pack generation request with conflicting parameters (e.g., extreme difficulty + tiny size impossible): tool should warn and skip invalid combos gracefully.
- Mobile device rotates orientation mid-play: layout reflows without losing progress.

---

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Web game MUST render a playable Hidato grid for selected puzzle (supports sizes 5–10 initially).
- **FR-002**: Player MUST be able to select a cell and place a number from available palette respecting adjacency constraints (invalid moves signaled visually but not permanently blocked).
- **FR-003**: System MUST support undo/redo stack for moves (at least last 100 actions).
- **FR-004**: Player MUST be able to toggle pencil mode and add/remove candidate numbers per cell (up to 4 candidates per cell).
- **FR-005**: On puzzle completion, system MUST show a results modal with time taken, moves, mistakes count.
- **FR-006**: System MUST load puzzle packs from a static manifest (JSON) and allow sequential navigation within a pack.
- **FR-007**: Puzzle pack view MUST display pack metadata: name, description (optional), counts by difficulty, total puzzles.
- **FR-008**: Python CLI generator MUST produce puzzle packs with uniqueness-verified puzzles meeting target density ranges per difficulty.
- **FR-009**: CLI MUST output manifest containing puzzle relative paths, size, difficulty, seed, clue count, max gap.
- **FR-010**: CLI MUST provide summary statistics: generated, skipped (failed uniqueness), average generation time.
- **FR-011**: Web client MUST persist in-progress puzzle state locally (e.g., local storage) to restore after reload.
- **FR-012**: UI MUST be responsive (layout adapts for widths <480px, 480–1024px, >1024px) with no horizontal scroll on mobile.
- **FR-013**: System MUST provide accessible color contrast for key states (selected cell, invalid move) meeting WCAG AA.
- **FR-014**: System SHOULD animate cell state changes (fade or scale ≤150ms) without hindering performance.
- **FR-015**: Loading a new puzzle MUST clear prior interaction state (candidates, undo stack) while preserving global settings.
- **FR-016**: Generator MUST allow configurable counts per size/difficulty via CLI parameters.
- **FR-017**: Generator MUST log failures with reason (e.g., uniqueness check timeout, structural ambiguity) to a report file.
- **FR-018**: System MUST prevent simultaneous pack generation processes from overwriting each other (unique output directory per run timestamp).
- **FR-019**: System MUST expose a lightweight puzzle metadata endpoint or static file for frontend consumption.
- **FR-020**: Frontend MUST validate puzzle integrity (start/end present, contiguous value range) before rendering; invalid puzzles trigger fallback error UI.
- **FR-021**: Frontend MUST allow optional help overlay explaining Hidato rules.
- **FR-022**: Player MUST be able to toggle sound effects (placement, completion) on/off.
- **FR-023**: System SHOULD provide dark/light theme toggle retained locally.
- **FR-024**: Pack progression MUST remember last puzzle index per pack locally.
- **FR-025**: If generator cannot meet requested count after retries, MUST produce partial pack with clear warning in summary.

Clarifications resolved:
- **FR-026**: Daily puzzle selection will use a deterministic seed-of-day mapping to the pre-generated pool (reproducible). If the mapped puzzle is missing, select the next available entry by wrap-around.
- **FR-027**: Sharing features (e.g., copy link to puzzle) are deferred and excluded from MVP.
- **FR-028**: Authentication and user accounts are excluded for MVP; progress is stored locally only.

### Key Entities

- **Puzzle**: id, size, difficulty, seed, clue_count, max_gap, givens layout, solution (optional for validator), pack_id.
- **Pack**: id, title, description, created_at, puzzle_ids[], difficulty_counts, size_distribution.
- **PlayerState (local only)**: puzzle_id, cell_entries, candidates, elapsed_time, undo_stack, settings (theme, sound, pencil_mode default).
- **GenerationRun**: timestamp, parameters (sizes[], difficulties[], count), generated_count, skipped_count, average_ms, failures[].

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 95% of puzzles load and become interactive in <1.2s on median mobile connection (after assets cached).
- **SC-002**: Players complete a daily puzzle with ≤3 misplacements median (indicates clarity of UI & constraints) in first release.
- **SC-003**: Pack generation tool produces ≥95% valid unique puzzles (skip rate ≤5%) for standard parameters (sizes 7 & 9, difficulties easy–hard) within average ≤2.0s per puzzle.
- **SC-004**: Mobile layout maintains tap target sizes ≥40px with no horizontal scroll across tested devices (10 popular viewport sizes).
- **SC-005**: Undo latency per action ≤100ms for puzzles up to 10x10.
- **SC-006**: Local restore accuracy ≥99% (cells & candidates) after manual page reload for in-progress puzzle.
- **SC-007**: Player satisfaction survey (post-completion modal optional feedback) achieves ≥80% “smooth experience” rating in pilot sample (N≥50).
- **SC-008**: Accessibility audit: all interactive elements have focus outlines and contrast ratios meeting WCAG AA (contrast ≥4.5:1) in both themes.

## Assumptions
- MVP excludes account system; progress stored locally.
- Daily puzzle selection will default to deterministic seed-of-day (YYYYMMDD hashed) if algorithm not clarified.
- Sharing and authentication deferred unless clarified as scope-critical.
- Puzzle sizes >10 deferred until performance validated.
- Generator reuses existing Python uniqueness pipeline; no external SAT solver required initial phase.

## Risks & Mitigations
- Risk: High skip rate for hard puzzles inflates generation time → Mitigation: implement retry cap & density relaxation fallback.
- Risk: Mobile performance degraded by animation overhead → Mitigation: cap animation duration ≤150ms & disable on low-power mode.
- Risk: Local persistence corruption → Mitigation: version key & safe parse with fallback to fresh puzzle.
- Risk: Unclear daily rotation spec delays feature → Mitigation: placeholder deterministic approach plus clarifying marker.

## Out of Scope (MVP)
- User authentication & cloud sync
- Leaderboards / global statistics
- Social sharing deep links (unless clarified)
- Multi-language localization

## Next Steps
- Proceed to planning breakdown (/speckit.plan) with clarified FR-026..028.

