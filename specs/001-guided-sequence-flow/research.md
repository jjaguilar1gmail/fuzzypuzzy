# Research & Decisions: Guided Sequence Flow Play

| Decision | Rationale | Alternatives Considered | Outcome |
|----------|-----------|-------------------------|---------|
| Local React Context + hooks (no Redux) | Simplicity, low overhead, limited feature scope | Redux (too heavy), Recoil (extra dependency) | Adopt Context + hooks |
| Show Guide optional toggle | Supports both assisted and minimalist play styles | Always on (less flexibility), Always off (hurts onboarding) | Implement toggle persisted per session |
| Longest contiguous chain definition anchored at 1 (or lowest given) | Stable next-number logic after removals | Dynamic anchor per last placed cell only (ambiguous after removal) | Implement chain walk from 1 upward |
| Removal by direct click on placed non-given cell | Intuitive, matches mental model of undo | Dedicated removal tool/button (extra UI friction) | Support click removal |
| Clearing next target when no legal extension exists | Avoids false error states, supports exploration | Force error banner; keep stale next number | Neutral state (clear indicator) |
| Mistake counting only on illegal placement attempts | Prevent inflation from exploratory clicks | Count any non-highlight click (punitive) | Count only invalid placement attempts |
| O(n) recompute for chain after each mutation | n ≤ 100 acceptable performance | Precompute graph; maintain complex incremental indexes | Simple recompute |
| Adjacency 8-neighbor with diagonals included | Standard Hidato rule; educative | Orthogonal only (wrong game rule) | Include diagonals |
| Undo stack capped at 50 | Bounded memory & complexity | Unlimited (risk runaway), Cap 10 (too restrictive) | Cap 50 |
| Highlight style: subtle fill + outline + accessible contrast | Usability + accessibility | Heavy glow (visual noise), color-only (fails WCAG) | Dual-channel styling |
| Next number visibility conditioned on legal placements existing | Avoid confusion in dead ends | Always show computed number even if unplaceable | Conditional display |
| Performance instrumentation using rAF timestamps (dev only) | Lightweight, avoids prod overhead | Add profiling library | Inline instrumentation |
| No backend changes | Frontend-only behavior shift | Add server validation endpoints | Keep existing backend |

## Clarifications Resolved
- State management: Use React Context; no new global store.
- Sequence neutral state: Clear next number when anchor has zero legal empties.
- Chain recomputation trigger: After every PLACE or REMOVE action.
- Removal effect: Recompute chain; if removed value disrupts contiguous tail, next number may shrink or clear.
- Guide OFF behavior: All legality checks still enforced; no highlights rendered.
- Mistake classification: Only attempting to place number where not legal (attempted PLACE_NEXT on invalid cell). Clicking non-highlight cell while exploring does not count if user didn’t explicitly attempt placement.
- Accessibility baseline: Provide toggle for high-contrast mode and ensure outline thickness ≥2px.
- Performance target: Per action total state update < 10ms worst-case for 10x10.
- Testing scope: Unit + integration; Cypress optional (documented as stretch goal).

## Risks & Mitigations
| Risk | Mitigation |
|------|------------|
| Chain ambiguity on boards starting without 1 | Use lowest given as chain start, document assumption |
| User confusion on neutral state | Tooltip/hover copy: "Select a number to continue sequence" |
| High mistake counts if mis-clicks frequent | Distinguish exploration vs explicit placement attempt |
| Mobile fat-finger false removals | Confirm removal via brief highlight before commit (optional future enhancement) |

## Open Deferred Considerations
- Possible future advanced mode: free-placement puzzle variant (explicitly out of scope now).
- Analytics on mistake rate (not included in this feature).
- Multi-anchor guidance (choose best of several candidate chains) not required for MVP.

## Final Outcome
All clarifications resolved; no remaining NEEDS CLARIFICATION markers. Ready for Phase 1 design artifacts.
