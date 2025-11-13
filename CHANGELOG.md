# Changelog

All notable changes to the fuzzypuzzy project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - Guided Sequence Flow Feature (001-guided-sequence-flow)

#### Core Functionality
- **Intelligent Placement Guidance**: Visual hints for valid next placements in Hidato puzzles
  - Automatic anchor detection from longest consecutive chain starting at 1
  - Legal target highlighting based on adjacency rules (4-directional + diagonal)
  - Next target indicator showing the number to place
  - Dynamic state management with automatic stale target recovery

- **Mistake Prevention & Feedback**:
  - Pre-validation layer prevents invalid placements (no-target, occupied-cell, not-adjacent)
  - Transient visual feedback with MistakeBadge toast notifications (1.2s auto-fade)
  - Cell-level mistake highlighting with red outlines and shake animation
  - Ring buffer tracking last 20 mistakes for debugging and UI feedback

- **Robust State Management**:
  - Neutral state support after tail removal (user can resume by selecting any chain value)
  - Automatic stale target detection with 3 recovery scenarios:
    - `anchor-invalid`: Anchor value changed or cleared
    - `chain-mutated`: Next target no longer follows chain end
    - `target-unreachable`: No legal targets available
  - Transparent auto-recovery via useEffect (no user intervention required)

- **Undo/Redo System**:
  - Full state snapshots with 50-action stack (LIFO)
  - Records placements and removals (excludes non-mutating actions)
  - Preserves board state, anchor, legal targets, and chain info

#### React Components
- `useGuidedSequenceFlow`: Main hook exposing 11 API methods
  - `selectAnchor`: Initialize anchor from chain value
  - `placeNext`: Place next sequential value with validation
  - `removeCell`: Remove player-placed cells (handles tail removal → neutral state)
  - `toggleGuide`: Show/hide visual guidance
  - `undo`/`redo`: Full state restoration
  - `canUndo`/`canRedo`: Stack availability checks
  - `state`: Current sequence state (anchor, nextTarget, legalTargets, etc.)
  - `board`: Current board cells with highlighting flags
  - `recentMistakes`: Last 20 validation errors

- **UI Components** (frontend/src/sequence/components/):
  - `NextNumberIndicator`: Displays next target with animated transitions
  - `HighlightLayer`: Overlays legal target positions with pulse effects
  - `MistakeBadge`: Toast notification for validation errors
  - `CellMistakeHighlight`: Red outline for mistake cells
  - `SequenceAnnouncer`: Invisible aria-live region for screen reader announcements

#### Accessibility Features
- **Screen Reader Support**:
  - SequenceAnnouncer component with aria-live="polite" announcements
  - Contextual messages: "Anchor set to 5. Next number is 6. 3 legal positions available."
  - Error announcements: "Invalid placement. Cell is already occupied."
  - State change notifications: "Tail removed. Chain now ends at 9. Select a chain value to continue."

- **Keyboard Navigation**:
  - `useKeyboardNavigation` hook for keyboard-only interaction
  - Tab/Shift+Tab: Cycle through legal target positions
  - Arrow keys: Navigate legal targets (Right/Down = next, Left/Up = prev)
  - Enter/Space: Place value at focused target
  - Escape: Clear focus and return to neutral
  - High-contrast mode CSS with 4px outline borders

- **WCAG Compliance**:
  - AA contrast ratios for all visual feedback
  - Reduced motion support (prefers-reduced-motion CSS)
  - Screen-reader-only content with sr-only utility class
  - Focus indicators with 3px outline (4px in high-contrast mode)

#### Performance Optimizations
- Memoized chain computation with `useMemo` (avoids redundant O(n) scans)
- GPU-accelerated CSS animations (transform + opacity only)
- Optimized state updates with useCallback for all action methods
- Minimal re-renders via React.memo on stateless components

#### Visual Effects
- CSS keyframe animations for state transitions:
  - `pulse-success`: Green scale pulse on valid placement (0.5s)
  - `highlight-anchor`: Yellow glow pulse on active anchor (1s loop)
  - `fade-neutral`: Opacity fade to gray on neutral entry (0.3s)
  - `mistakePulse`: Red shake + scale on validation error (0.4s)
  - `mistakeFadeOut`: Opacity fade for transient mistake display (1.2s)

#### Testing
- **57 unit + integration tests** (100% passing)
  - Adjacency helpers: 12 tests
  - Chain computation: 7 tests
  - Undo/redo stack: 7 tests
  - Mistake validation: 12 tests
  - Stale target detection: 13 tests
  - Neutral state resume: 6 tests
- Test framework: Vitest + React Testing Library
- Coverage: All core utilities, state transitions, and edge cases

#### Developer Experience
- **Comprehensive Documentation**:
  - `integration-guide.md`: Quick-start with code examples
  - `implementation-status.md`: Full progress tracking (27 tasks across 5 phases)
  - `phase-3-completion.md` & `phase-4-completion.md`: Phase summaries
  - JSDoc comments on all public APIs
  - Inline code comments explaining complex logic

- **Type Safety**:
  - Full TypeScript definitions for all APIs
  - 14 exported types (Position, BoardCell, SequenceState, MistakeEvent, etc.)
  - Strict null checks enforced

- **Modular Architecture**:
  - 12 utility modules (adjacency, chain, nextTarget, transitions, etc.)
  - 5 UI components (all composable and testable)
  - Single entry point with selective exports (tree-shakeable)

#### File Structure
```
frontend/src/sequence/
├── index.ts                      # Public API exports
├── types.ts                      # TypeScript definitions
├── useGuidedSequenceFlow.ts      # Main React hook (260 lines)
├── adjacency.ts                  # Adjacency helpers
├── chain.ts                      # Chain computation
├── nextTarget.ts                 # Target derivation
├── removal.ts                    # Removal classification
├── transitions.ts                # State transition functions
├── undoRedo.ts                   # Undo/redo stack
├── mistakes.ts                   # Validation logic
├── staleTarget.ts                # Stale detection + recovery
├── visualEffects.ts              # CSS animations + styles
├── keyboardNavigation.ts         # Keyboard navigation hook
├── components/
│   ├── index.ts
│   ├── NextNumberIndicator.tsx
│   ├── HighlightLayer.tsx
│   ├── MistakeBadge.tsx
│   ├── CellMistakeHighlight.tsx
│   └── SequenceAnnouncer.tsx
└── __tests__/
    ├── adjacency.test.ts
    ├── chain.test.ts
    ├── undoRedo.test.ts
    ├── mistakes.test.ts
    ├── staleTarget.test.ts
    └── neutralResume.test.ts
```

**Total Implementation**: ~2,200 lines (including 800 lines of tests)

#### Breaking Changes
None - Feature is additive and does not modify existing puzzle generation.

#### Migration Guide
No migration required. Feature is opt-in via `useGuidedSequenceFlow` hook.

See `specs/001-guided-sequence-flow/integration-guide.md` for usage examples.

---

## [0.1.0] - Initial Release

### Added
- Python puzzle generation engine
- Core Hidato puzzle solver
- Basic web frontend (React + Next.js)

---

[Unreleased]: https://github.com/jjaguilar1gmail/fuzzypuzzy/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/jjaguilar1gmail/fuzzypuzzy/releases/tag/v0.1.0
