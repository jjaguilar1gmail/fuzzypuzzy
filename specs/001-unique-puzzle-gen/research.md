# Research & Decisions: Uniqueness-Preserving Puzzle Generator

## Overview
Consolidated architectural and algorithmic decisions for generator pipeline.

## Topics & Decisions

### 1. Path Construction Strategy
- Decision: Support `serpentine` (deterministic scan) and `random_walk` (seeded backtracking ensuring full Hamiltonian path).
- Rationale: Serpentine fast & predictable; random_walk adds variety.
- Alternatives: Precomputed pattern library (less flexible), full DFS each time (slower for 9x9 but acceptable). Chosen hybrid for speed + diversity.

### 2. Initial Clue Seeding
- Decision: Always include 1, N (max value), and turn anchors (cells where path changes direction) plus optional symmetry (none, rotational, horizontal) applied after anchor selection.
- Rationale: Anchors stabilize uniqueness early, reduce branching.
- Alternatives: Pure random anchors (higher failure rate), dense early fill (slows removal loop).

### 3. Clue Removal Heuristic
- Decision: Score removable clue candidates by (a) distance from nearest anchor, (b) local redundancy (number of alternative adjacency paths between its neighbors), (c) inverse strategic value (avoid removing corridor bottlenecks). Remove highest score first.
- Rationale: Maximizes safe removals while preserving uniqueness potential.
- Alternatives: Random removal (unstable), pure degree-based (ignores spatial distribution).

### 4. Uniqueness Checking (count_solutions cap=2)
- Decision: Run logic fixpoint → if unsolved, bounded search that aborts after finding 2 solutions. If exactly 1, unique; if 2 found, non-unique.
- Rationale: Early exit reduces time; leverages existing solver capabilities.
- Alternatives: Full exhaustive search (too slow), SAT transform (overkill for scope).

### 5. Difficulty Estimation Metrics
- Decision: Use: clue_density, logic_fill_ratio (placements made without search), max_search_depth, nodes_explored, strategy_usage_counts (corridor, degree), and branching_factor_estimate (#candidate cells average for unsolved values).
- Rationale: Multi-dimensional view maps well to spec bands.
- Alternatives: Single metric (insufficient granularity), ML classifier (over-scope).

### 6. Blocked Cells Support
- Decision: Accept optional blocked cell positions; path builder treats them as invalid; uniqueness & removal skip blocked cells.
- Rationale: Extends future puzzle variety with minimal extra complexity.
- Alternatives: Defer entirely (reduced flexibility) or complex region masks (out-of-scope).

### 7. RNG & Determinism
- Decision: Single `Random` instance seeded; all stochastic functions receive it; record seed and derived sub-modes.
- Rationale: Constitution requires reproducibility.
- Alternatives: Multiple RNGs (risk divergence), global random (harder reproducibility).

### 8. Budgets & Timeouts
- Decision: Global generation timeout_ms and per uniqueness-check node/time caps; exponential backoff on aggressive removals (reduce removal batch size as attempts increase).
- Rationale: Ensures responsiveness and predictable upper bounds.
- Alternatives: Unbounded attempts (risk runaway), fixed removal schedule (less adaptive).

### 9. API Surface
- Decision: `generate_puzzle(size, difficulty=None, percent_fill=None, seed=None, allow_diagonal=True, blocked=None, path_mode='serpentine', clue_mode='anchor_removal_v1', symmetry=None, turn_anchors=True, timeout_ms=5000, max_attempts=5)` returning `GeneratedPuzzle` dataclass.
- Rationale: Clear, explicit knobs; consistent naming with solver config patterns.
- Alternatives: Builder object (more ceremony), minimal args (reduces control for packs).

### 10. Failure Handling
- Decision: If budgets exceeded, return best candidate with `success=False` and reason, including partial metrics & uniqueness_verified flag.
- Rationale: Never emit silent failure; preserves work for potential manual inspection.
- Alternatives: Raise exception (less ergonomic in batch mode), return None (loss of diagnostics).

### 11. Data Structures
- Decision: Use existing `Puzzle` + metadata wrapper; internal ephemeral working copies to avoid mutating external puzzle references.
- Rationale: Aligns with solver immutability stance.
- Alternatives: New puzzle type (duplication), in-place mutation (risk side effects).

### 12. Performance Considerations
- Decision: Cache neighbor lists per position for path building; reuse candidate sets during removal evaluations; micro-profile uniqueness early exit.
- Rationale: Keeps within P95 targets without new dependencies.
- Alternatives: Introduce C extensions (premature), parallelism (complex with determinism).

### 13. Symmetry Modes
- Decision: Implement optional symmetry filter (if requested) by mirroring chosen anchors and restricting removal to maintain symmetry unless impossible.
- Rationale: Adds aesthetic control with modest cost.
- Alternatives: Post-hoc symmetry enforcement (may reintroduce ambiguity), no symmetry (less variety for curated packs).

### 14. Logging & Trace
- Decision: Provide structured dict log (seed, path_mode, clue_mode, removals_attempted, removals_accepted, uniqueness_checks, final_metrics). CLI `--generate --trace` prints summarized view.
- Rationale: Debuggability & reproducibility.
- Alternatives: Free-form text (harder to parse), silent logs (less insight).

## Unresolved Items
None (all clarifications answered in spec decisions).

## Alternatives Summary Table
| Topic | Chosen | Key Alternatives | Reason Rejected |
|-------|--------|------------------|-----------------|
| Path | serpentine + random_walk | pure random DFS | variability + speed balance |
| Anchors | 1,N + turns | random subset | improves uniqueness stability |
| Removal | heuristic score | random, degree-only | better preservation of uniqueness potential |
| Uniqueness | cap=2 search | exhaustive | faster abort on non-unique |
| Difficulty | multi-metric | single metric | richer band discrimination |
| Blocked cells | basic support | defer | future flexibility |
| RNG | single instance | multiple | reproducibility risk |
| Failure handling | best-effort object | exception only | retains diagnostics |

## Final Statement
Research phase complete; ready to proceed to design (data model, contracts, quickstart) per plan.
