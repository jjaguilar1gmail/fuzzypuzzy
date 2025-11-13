# Feature Specification: Guided Sequence Flow Play

**Feature Branch**: `001-guided-sequence-flow`  
**Created**: 2025-11-13  
**Status**: Draft  
**Input**: User description: "Change the interaction model from 'click cell → click number' to a guided sequence flow: you click a clue (or current number), the UI shows the next number in the sequence, faintly highlights all legal adjacent empty cells, and one click on any of those cells places that number and advances the sequence. This matters because it makes the game feel intuitive and 'flowy,' reduces friction on every move, and visually teaches the adjacency rule (8-neighbor) while still tracking mistakes when players click out-of-bounds cells."

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

### User Story 1 - Flowing Guided Placement (Priority: P1)

As a player, I can select a clue (or the current number), see the next number to place, and immediately see faint highlights on all legal adjacent empty cells so that a single click places the next number and advances the sequence.

**Why this priority**: This is the core interaction change—removes friction, teaches the 8‑neighbor rule visually, and makes play feel intuitive and continuous.

**Independent Test**: Launch a puzzle, select a clue (e.g., 9), verify the UI displays "10" as the next number and highlights all legal 8‑neighbor empty cells; clicking any highlight places 10 and advances to 11 with new highlights.

**Acceptance Scenarios**:

1. Given a clue n on the board, when I click it, then the UI shows n+1 as the next number and faintly highlights all legal adjacent empty cells (8‑neighbor) around n.
2. Given n is selected and legal highlights are visible, when I click one highlighted cell, then that cell is filled with n+1, n+1 becomes the new current, and highlights recompute around n+1.
3. Given the selected number is the maximum value (e.g., 64), when I click it, then no next value is shown and no highlights are displayed.

---

### User Story 2 - Mistake Feedback and Safety (Priority: P2)

As a player, if I click outside the highlighted cells, the game prevents the move, shows brief visual feedback, and increments a mistakes counter so I learn the rule without corrupting the board.

**Why this priority**: Reinforces the adjacency rule and avoids accidental placements that harm progress.

**Independent Test**: With highlights visible, click a non-highlighted empty cell; verify no placement occurs, a brief feedback animation appears, and the mistakes counter increases by 1.

**Acceptance Scenarios**:

1. Given highlights are visible for n→n+1, when I click any non-highlighted cell (including out-of-bounds or blocked), then no number is placed and a short, non-intrusive feedback is shown (e.g., shake/flash) and the mistakes counter increments.
2. Given zero legal highlights (dead end), when I click anywhere, then no placement occurs and an unobtrusive hint explains there are no legal moves from the selected number.

---

### User Story 3 - Resume from Any Clue (Priority: P2)

As a player, I can click any placed number n to resume from there; the UI updates the next number to n+1 and shows the correct highlights from that anchor.

**Why this priority**: Lets players branch exploration, correct mistakes after undo, or continue from known anchors.

**Independent Test**: Place a few numbers, click an earlier clue; verify next target updates to that clue+1 and highlights recompute from that position only.

**Acceptance Scenarios**:

1. Given multiple numbers are placed, when I click n, then the next target becomes n+1 and highlights are computed relative to n.
2. Given n is the latest placed number and I click a different clue m (< n), then the current target switches to m+1 and highlights recompute accordingly.

---

[Add more user stories as needed, each with an assigned priority]

### Edge Cases

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right edge cases.
-->

- Selected number is the maximum value (no next): shows no highlights, no placement possible.
- Selected number has zero legal adjacent empties (dead end): show zero highlights and a brief explanation; no placement occurs.
- Multiple legal cells exist: all are highlighted equally; no auto‑choose.
- Selected cell is a given (clue): always allowed as anchor; cannot overwrite givens.
- Attempt to click a non-empty or blocked cell: treated as invalid (mistake feedback, no mutation).
- Rapid double-click/tap: processed as a single placement; no duplicate actions.
- Mobile/touch: tap-to-select clue and tap-to-place work equivalently to desktop clicks.
- Accessibility: highlights must be perceivable without color alone (e.g., outline + subtle fill).

## Requirements *(mandatory)*

<!--
  ACTION REQUIRED: The content in this section represents placeholders.
  Fill them out with the right functional requirements.
-->

### Functional Requirements

- **FR-001**: Selecting any placed number n sets the current anchor to n and the next target to n+1 (unless n is the maximum value).
- **FR-002**: The UI must faintly highlight all legal adjacent empty cells (8‑neighbor) for the current target from the selected anchor.
- **FR-003**: Clicking a highlighted cell places the next number (n+1) in that cell, advances the current anchor to n+1, and recomputes highlights.
- **FR-004**: Non-highlight clicks (including blocked or already-filled cells) must not change the board and must trigger brief mistake feedback and increment a visible mistakes counter.
- **FR-005**: Highlights must never include non-empty or blocked cells and must always match the 8‑neighbor legality exactly.
- **FR-006**: When no legal adjacent empty cells exist for the current anchor, the system displays zero highlights and a non-intrusive hint (e.g., tooltip/toast).
- **FR-007 (UPDATED)**: The “Next Number” indicator appears only when an anchor is selected AND at least one legal empty adjacent cell exists for anchorValue+1; otherwise it is hidden (neutral state).
- **FR-008**: Maintain an action history supporting Undo/Redo for at least the last 50 placement actions (undo reverts both placement and anchor/target state).
- **FR-009**: Track and display a mistakes counter for the current play session; do not count taps on UI chrome (outside the board).
- **FR-010**: Touch input must support the same interaction model as mouse clicks (tap to select anchor, tap to place next).
- **FR-011**: Provide a “Show Guide” toggle controlling whether legal target highlights are rendered; underlying legality rules still enforced when off.
- **FR-012**: Provide settings to adjust highlight intensity and enable/disable mistake feedback animations (persist per session).
- **FR-013**: Clicking a non-given, previously placed cell removes that number (atomic REMOVE action) and triggers recomputation of the longest contiguous chain and next target visibility rules.
- **FR-014**: After a REMOVE, if the removed value belonged to the tail of the longest contiguous chain, the next target becomes the smallest missing consecutive number after the new chain end; if it did not affect the chain tail, next target is cleared until a new anchor is selected.
- **FR-015**: Neutral state handling: when an anchor has no legal extension the system must clear next target, render no highlights, and avoid mistake increments for exploratory clicks.
- **FR-016**: Mistake classification: an attempted placement on a cell that is not a legal adjacent empty target while a next target exists increments the mistake counter and applies visual feedback; simply clicking elsewhere without attempting placement when guide OFF does not increment.
- **FR-017**: Visual styling: anchor cells use a gentle outline (not harsh black); legal targets (guide ON) use faint unobtrusive highlight; mistakes are marked with clear red indicator; all must meet accessibility contrast guidelines.

### Key Entities *(include if feature involves data)*

- **Sequence State**: currentAnchor (n), nextTarget (n+1/max), selection source (position of n).
- **Board Cell**: position, value, given flag, blocked flag, highlighted flag (derived/display-only).
- **Mistake Event**: timestamp, selectedAnchor, clickedCell, reason (non-highlight/blocked/occupied).
- **Player Settings**: highlightIntensity, mistakeFeedbackEnabled.

## Success Criteria *(mandatory)*

<!--
  ACTION REQUIRED: Define measurable success criteria.
  These must be technology-agnostic and measurable.
-->

### Measurable Outcomes

- **SC-001**: 95% of valid placement clicks result in the number placed and new highlights rendered within 100 ms.
- **SC-002**: 100% of invalid clicks show visible feedback within 150 ms and never mutate board state.
- **SC-003**: In a moderated usability test, first-time players complete their first 10 placements at least 25% faster compared to the prior interaction model.
- **SC-004**: Automated tests confirm that for any selected anchor, highlights exactly match legal 8‑neighbor empty cells (no false positives/negatives) across at least 50 board configurations.

### Assumptions

- The base game enforces sequential placement as the only standard play mode for this feature; prior free-placement mode is removed from standard play. Any experimental/custom modes are out of scope.
- “Out-of-bounds” user intent in original description is interpreted as any click that attempts placement outside the legal adjacency set; true DOM out-of-bounds clicks are ignored by browser and not counted.
- Chain recomputation walks from 1 (or lowest given) upward to establish contiguous tail used for FR-014 logic.
- Visual style of highlights and feedback is consistent with existing design language; exact colors/animations are left to design but must meet accessibility contrast guidelines.
- Undo/Redo is limited to placements introduced via this guided flow and does not retroactively modify clues.
