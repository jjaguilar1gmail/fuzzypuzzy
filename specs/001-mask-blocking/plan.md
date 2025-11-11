# Implementation Plan: Mask-Driven Blocking & Ambiguity-Aware Repair

**Branch**: `001-mask-blocking` | **Date**: 2025-11-10 | **Spec**: `specs/001-mask-blocking/spec.md`
**Input**: Feature specification generated in previous step.

## Summary
Add two structural enhancements to generation: (1) a pre-path BlockMask that deterministically introduces low-density blocked cells to shape Hamiltonian path formation and reduce branching; (2) an ambiguity-aware structural repair option that prefers adding a single strategic block over re-adding a clue when multi-solution ambiguity is detected. Integrate with existing path modes, uniqueness staged checker, pruning, and difficulty estimation without violating constitution constraints (determinism, reproducibility, validation, domain purity).

## Technical Context
**Language/Version**: Python 3.11 (stdlib only per constitution)  
**Primary Dependencies**: Internal modules only (`core.*`, `generate.*`, `solve.*`, `util.rng`)  
**Storage**: N/A (in‑memory puzzle state)  
**Testing**: pytest (existing suite extended)  
**Target Platform**: Local CLI / library execution (Windows, cross-platform)  
**Project Type**: Single repository with modular packages (no external services)  
**Performance Goals**: Maintain current generation latency; improve hard puzzle generation time by ≥25%; uniqueness repair within existing budgets (<700ms total for hard puzzles).  
**Constraints**: Deterministic given seed; mask density ≤10%; structural repair attempts ≤2; no increase in false UNIQUE classification; functions <60 lines where reasonable.  
**Scale/Scope**: Applies to sizes 5x5–9x9 initially; focus on Hard/Medium improvements; small boards auto-disable mask unless forced.

## Constitution Check (Pre-Design Gate)
| Principle | Status | Notes |
|-----------|--------|-------|
| Determinism & reproducibility | PASS | Mask & repair seeded; decisions logged. |
| Separation of concerns | PASS | New modules isolate mask logic; core untouched. |
| Safety & validation | PASS | Mask validated (connectivity, no orphan pockets). |
| Testing discipline | PASS | New tests: mask validation, repair decision, metrics. |
| Solver logic before search | PASS | v2 logic still runs; added probes unchanged except enabling logic each node. |
| Generator pipeline clarity | PASS | New stage inserted before PathBuilder; repair integrated into pruning phase. |
| No mutation of caller puzzle | PASS | Generation uses internal copies; structural modifications happen before final validation. |
| Logging seed/modes | PASS | Extend existing metrics output with mask fields. |
| No junk output | PASS | Post-mask solvability sanity check preserved. |

No violations identified; proceed to Phase 0.

## Project Structure (Feature Additions)
```text
generate/
  mask/
    __init__.py            # Public API: build_mask(config, rng)
    patterns.py            # Template pattern generators (corridor, ring, spiral)
    procedural.py          # Ratio-based procedural mask sampling
    validate.py            # Connectivity & orphan pocket validation utilities
    metrics.py             # Mask metrics dataclass & logging helpers
  repair/
    ambiguity.py           # Ambiguity region detection and scoring
    structural_block.py    # Candidate selection & connectivity re-check
    fallback.py            # Clue-based repair fallback logic
    metrics.py             # Repair metrics capture
  generator.py             # Integrate mask stage before path build (small edits)
  pruning.py               # Integrate ambiguity-aware structural repair option

tests/
  test_mask_generation.py
  test_mask_validation.py
  test_mask_metrics.py
  test_repair_ambiguity_detection.py
  test_repair_structural_block.py
  test_repair_fallback_clue.py
  test_integration_mask_vs_no_mask.py
  test_performance_mask_density_sweep.py (optional benchmark style)
```

**Structure Decision**: Extend existing `generate` package with two focused subpackages (`mask`, `repair`) to maintain separation of concerns while reusing existing RNG and pruning infrastructure.

## Phase 0: Research Plan
Unknowns to resolve: NONE (spec asserts defaults). Research will codify pattern ontology sizing rules, scoring formula components, and mask density heuristics.

`research.md` will document: pattern set, density caps per size/difficulty, ambiguity scoring formula (frequency × corridor width × distance weighting), reproducibility guarantees, and fallback ordering.

## Phase 1: Design & Contracts
Artifacts to produce:
- `data-model.md`: Define BlockMask, MaskPattern, AmbiguityRegion, RepairAction, GenerationMetrics extensions.
- `contracts/` (internal pseudo-API): Function signatures for mask/build, validate, repair decision, metrics emission.
- `quickstart.md`: How to enable mask, configure repair knobs, interpret metrics.
- Update agent context for new concepts (mask, ambiguity region, structural repair).

## Complexity Tracking
No constitution violations; table not required.

## Implementation Phases (High-Level)
1. Mask pattern templates (static shapes) & procedural sampler.
2. Validation (BFS connectivity + orphan pocket check + density threshold).
3. Integration hook in `Generator.generate_puzzle` before path builder call.
4. Metrics logging extension (add mask & repair fields).
5. Ambiguity detector: diff two found solutions → local divergence clustering.
6. Structural block scoring & insertion with solvability + uniqueness re-check.
7. Fallback to clue addition if structural insertion fails.
8. Enable logic passes at every uniqueness probe node + transposition table (key: placed_values hash + mask signature).
9. Difficulty scoring adjustment: incorporate logic ratio & node depth metrics for masked puzzles.
10. Test suite additions & benchmark sweeps.

## Risk Mitigation Summary
| Risk | Mitigation |
|------|------------|
| Overdense masks cause path failure | Retry with reduced density; cap attempts. |
| Repair block breaks solvability | Re-run solver fixpoint; abort if unsolved. |
| Ambiguity false positives | Require solution diff confirmation; fallback clue addition. |
| Performance regression | Budget validation & repair attempts; early abort path. |
| Non-deterministic heuristics | All randomness via existing RNG seeded path. |

## Logging & Metrics Additions
Extend existing generation result: `mask_pattern_id`, `mask_cells_count`, `mask_attempts`, `structural_repairs_used`, `repair_mode_used (block|clue|none)`, `branching_factor_before/after`, `ambiguity_regions_detected`.

## Next Steps
Proceed to Phase 0: create `research.md` capturing concrete decisions.

