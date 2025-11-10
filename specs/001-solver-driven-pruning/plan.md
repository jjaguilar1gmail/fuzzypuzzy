# Implementation Plan: Solver-Driven Pruning

**Branch**: `001-solver-driven-pruning` | **Date**: 2025-11-10 | **Spec**: specs/001-solver-driven-pruning/spec.md
**Input**: Feature specification from `/specs/001-solver-driven-pruning/spec.md`

**Note**: This template is filled in by the `/speckit.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Replace linear clue-removal with a solver-driven pruning loop using interval reduction (binary-search style) to quickly converge to minimal viable clues, and introduce a frequency-based uniqueness repair that injects a single mid-segment clue at common divergence points across alternates. Hard/extreme difficulties disable turn anchors (endpoints only) to avoid inflated clue counts. Outputs are deterministic per seed + config; metrics cover iterations, repairs, density, and time.

## Technical Context

<!--
  ACTION REQUIRED: Replace the content in this section with the technical details
  for the project. The structure here is presented in advisory capacity to guide
  the iteration process.
-->

**Language/Version**: Python 3.11 (stdlib only; dataclasses optional)  
**Primary Dependencies**: Internal modules only (core.*, generate.*, solve.*, util.*)  
**Storage**: N/A (in-memory puzzle state; optional JSON export)  
**Testing**: pytest (existing suite + new benchmarks/tests)  
**Target Platform**: Windows/macOS/Linux (CLI)  
**Project Type**: Single repository with modules under root directories (core, generate, solve, tests)  
**Performance Goals**: Hard 9x9 generation ≤ 6.0s median; pruning iterations reduced ≥ 40% vs legacy  
**Constraints**: Deterministic results by seed; no external deps; functions ≤ 60 LoC where feasible  
**Scale/Scope**: Applies to puzzle sizes up to 9x9 in current benchmarks

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- Clarity/SOC: Plan introduces Pipeline stages (PathBuilder → CluePruner → Validator → Uniqueness → Difficulty). PASS
- Determinism: All steps bound to RNG seeded from config; metrics logged. PASS
- Safety/Validation: Givens never overwritten; uniqueness validated before return. PASS
- Solver Rules: Logic-first then bounded search preserved; hints/explanations unaffected. PASS
- Generator Rules: Seeded; pipeline stages clear; never emit junk with validation; always return metadata. PASS
- Versioning/Composition: Modes via config strings; new strategies registered. PASS

## Project Structure

### Documentation (this feature)

```text
specs/001-solver-driven-pruning/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── tasks.md    (generated later by /speckit.tasks)
```

### Source Code (repository root)
<!--
  ACTION REQUIRED: Replace the placeholder tree below with the concrete layout
  for this feature. Delete unused options and expand the chosen structure with
  real paths (e.g., apps/admin, packages/something). The delivered plan must
  not include Option labels.
-->

```text
core/
generate/
solve/
util/
tests/
specs/001-solver-driven-pruning/
```

**Structure Decision**: Single-repo modular layout; feature adds no new top-level apps—only generator pipeline changes and docs/specs.

## Complexity Tracking

No violations anticipated; no additional subprojects or external dependencies introduced.

---

## Phase 0: Outline & Research

Unknowns: None critical (spec defines defaults). Research tasks target method details and tuning.

Research tasks:
- R1: Best practices for binary-search style pruning on discrete clue sets; stopping conditions and fallback to linear probing.
- R2: Efficient alternates sampling for frequency-based uniqueness repair; number of alternates vs. benefit curve.
- R3: Ambiguity scoring heuristics for mid-segment selection (distance from endpoints, corridor length, branching impact).
- R4: Metrics schema for iterations, interval contractions, repair count, time.

Deliverable: research.md documenting decisions, rationale, alternatives.

## Phase 1: Design & Contracts

Artifacts to produce:
- data-model.md: Entities (Pruning Session, Removal Batch, Ambiguity Profile, Repair Candidate, Metrics Report) with fields and validations.
- contracts/: Generator configuration knobs (difficulty bands, repair caps), CLI flags for toggles, and metrics output schema.
- quickstart.md: How to run with solver-driven pruning, example seeds, reading metrics.
- Update agent context: `.specify/scripts/powershell/update-agent-context.ps1 -AgentType copilot`.

Gate re-check: Ensure constitution compliance post-design; confirm no printing in core; determinism preserved.

## Phase 2: Handoff

Not part of /speckit.plan execution; will add tasks.md during /speckit.tasks phase.
