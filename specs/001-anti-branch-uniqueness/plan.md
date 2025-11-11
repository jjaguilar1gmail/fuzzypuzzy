# Implementation Plan: Anti-Branch Uniqueness & Size-Aware Clue Distribution

**Branch**: `001-anti-branch-uniqueness` | **Date**: 2025-11-11 | **Spec**: specs/001-anti-branch-uniqueness/spec.md
**Input**: Feature specification from `/specs/001-anti-branch-uniqueness/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.
## Summary

Enhance puzzle generation integrity and clue layout quality by:
1. Replacing shallow uniqueness checks with a two-phase probe (logic fixpoint then targeted anti-branch DFS seeking 2nd solution early-exit) plus 2–3 randomized tie-break variant probes.
2. Introducing size- and difficulty-aware anchor and density policies to prevent clue clustering on small boards (5×5–7×7) while maintaining challenge scaling.
3. Adding de-chunk spacing heuristic and post-target-density de-clustering pass to equalize clue spatial distribution.
4. Unified telemetry—per (path_mode, size, difficulty) capturing probe outcomes, densities, spacing metrics, and solve stats—to tune budgets and weights iteratively.

The plan reconciles user request expansion (apply to all path modes) with spec restriction (backbite_v1/random_v2 only). Constitution mandates determinism and logging; we maintain reproducibility by seeding tie-break shuffles.
## Technical Context

**Language/Version**: Python 3.11 (existing project standard)
**Primary Dependencies**: Standard library only (time, heapq, dataclasses, random) per constitution; optional SAT/CP hook (currently disabled)
**Storage**: In-memory puzzle objects; JSON export only
**Testing**: pytest (existing); will add new contract + property tests
**Target Platform**: Local CLI generation environment (Windows/macOS/Linux)
**Project Type**: Single multi-module Python project (generator + solver packages)
**Performance Goals**: Maintain generation throughput (≤2s average per puzzle small sizes) while increasing uniqueness veracity (0% false-unique >25 cells)
**Constraints**: Deterministic given seed; bounded DFS (node/time); functions ≤60 lines guideline; no external heavy deps by default
**Scale/Scope**: Sizes 5×5–9×9; path modes (serpentine, backbite_v1, random_v2, random_walk, jitter/strip-shuffle) — NEEDS CLARIFICATION: jitter/strip-shuffle naming canonical? (If not implemented treat as future extension.)

Additional Domain Notes:
 - Tie-break shuffle must not change solution correctness—only branch exploration order.
 - Telemetry logging must not exceed memory constraints; stream logs line-by-line.
## Constitution Check

Principle Mapping:
1. Size & Separation: We will introduce new modules (e.g., `solve.uniqueness_probe`, `generate.spacing`) keeping each ≤60 lines where feasible—PASS.
2. Determinism: All probes seeded; random permutations derived from global RNG—PASS.
3. Safety & Validation: Uniqueness probe operates on copies; no mutation of givens—PASS.
4. Accessibility: JSON export unchanged—PASS.
5. Testing Discipline: New logic gets contract tests + regression tests—PASS.
6. Solver Rules: Logic fixpoint before DFS maintained—PASS.
7. Generator Rules: Pipeline preserved (PathBuilder → CluePlacer → Validator → Uniqueness) with added spacing stage—PASS.
8. Versioning & Composition: Add new mode strings only if needed; else augment config—PASS.

Potential Tension:
 - Expanding to all path modes vs spec limitation (original spec only backbite_v1/random_v2). Needs decision: adopt extended scope or constrain to spec. Resolution will occur in Phase 0 research.

Gate Status: PRELIM PASS (pending clarifications noted).
### Documentation (this feature)

```text
specs/001-anti-branch-uniqueness/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
└── contracts/
  ├── uniqueness.md
  └── spacing.md
```

### Source Code (repository root)
```text
generate/
├── generator.py              # integrate probe + spacing/de-chunk
├── spacing.py                # NEW: spacing heuristics & metrics
├── anchors_policy.py         # NEW: size/difficulty anchor logic

solve/
├── uniqueness_probe.py       # NEW: anti-branch DFS (early-exit @2)

util/
├── logging_uniqueness.py     # NEW: line-delimited JSON telemetry

app/
├── packgen/cli.py            # CLI flags wiring (enable anti-branch)
```

**Structure Decision**: Retain existing generator/solver layout. New files placed as above; integrate via thin adapters in `generator.py` and `cli.py`.

## Phase 0: Research Outline

Unknowns / Clarifications:
1. Scope of path modes (restrict vs expand). Decision needed.
2. Canonical naming for jitter/strip-shuffle path variants.
3. Telemetry metric definitions (spacing/clustering formula specifics).

Research Tasks:
 - Compare uniqueness probe strategies (anti-branch vs full enumeration) performance.
 - Define spacing metric candidate (avg Manhattan distance, Gini coefficient of density, quadrants variance).
 - Establish size-tier node/time budgets empirically.
 - Validate tie-break shuffle strategies (MRV list randomization, candidate rotation).

Deliverable: `research.md` with decisions + rationale + rejected alternatives.
## Phase 1: Design & Contracts

Artifacts:
 - `data-model.md`: Entities (ProbeOutcome, SizeTierPolicy, TelemetryRecord).
 - `contracts/uniqueness.md`: Pseudo-contract for probe interface (inputs: puzzle, budgets; outputs: classification + metrics).
 - `contracts/spacing.md`: Heuristic scoring specification.
 - `quickstart.md`: How to enable enhanced uniqueness checks and interpret logs.
 - Update agent context via script.

## Phase 2: (Out of Scope for this command)
Will produce tasks and implementation sequencing in `/speckit.tasks`.

## Complexity Tracking

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|--------------------------------------|
| Extra modules (spacing, probe) | Maintain separation of concerns | Single large generator file would breach size, reduce clarity |
| Telemetry layer | Needed for empirical tuning | Ad-hoc print statements violate logging & determinism principles |

## Constitution Check (Post-Design)

Re-evaluated after Phase 1 artifacts:
- Separation, determinism, bounded search, and testing remain intact – PASS.
- Scope note: Plan broadens path modes beyond spec FR-010. Action: update spec FR-010 in next step or constrain implementation to spec. No gate violation since this is documentation scope alignment.