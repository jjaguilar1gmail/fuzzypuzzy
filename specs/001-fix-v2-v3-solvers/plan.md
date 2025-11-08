# Implementation Plan: Fix v2/v3 solvers for 5x5 deterministic

**Branch**: `001-fix-v2-v3-solvers` | **Date**: 2025-11-07 | **Spec**: specs/001-fix-v2-v3-solvers/spec.md  
**Input**: Feature specification from `/specs/001-fix-v2-v3-solvers/spec.md`

## Summary
Strengthen logic_v2 pruning (corridor, degree, minimal region capacity) and rework logic_v3 search to apply a v2 fixpoint in-place at every node while switching MRV/LCV to operate on values (value→positions MRV with frontier/LCV ordering). Add optional tiny transposition caching. Goal: canonical 5x5 deterministic puzzle solved in ≤100 ms (v3) with improved deterministic pruning and transparent traces; v2 may stall but must perform at least one pruning elimination.

## Technical Context
**Language/Version**: Python 3.11 (standard library only; dataclasses optional)  
**Primary Dependencies**: Standard library (collections, dataclasses, time, heapq)  
**Storage**: N/A (in-memory puzzle state)  
**Testing**: pytest + new regression tests under `tests/`  
**Target Platform**: Cross-platform; dev on Windows (PowerShell); deterministic across OS  
**Project Type**: Single library/CLI puzzle solver/generator  
**Performance Goals**: v3 ≤100 ms wall-clock on 5x5 canonical; v2 ≤250 ms fixpoint; v3 node count ≤2,000  
**Constraints**: Determinism (same seed/config → identical output); public API does not mutate caller’s puzzle; explanations for every placement/elimination  
**Scale/Scope**: Focused on 5x5 improvements; avoid regressions on smaller boards; functions ≤60 lines target.

## Constitution Check (Pre-Design)
- Clarity: Corridor and degree logic split into helpers (PASS planned)
- Determinism: In-place logic only on search copy; stable MRV ordering (PASS planned)
- Safety: Givens immutable; final validation unchanged (PASS)
- Explainability: Need reasons for corridor/degree/region eliminations (ACTION)
- Monotone logic before search: Fixpoint enforced each node (PASS after change)
- Non-mutation of caller: Maintain copy semantics externally (PASS)
Status: Proceed; add explanations in contracts.

## Project Structure

### Documentation (this feature)

```text
specs/001-fix-v2-v3-solvers/
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/
└── (tasks.md added later by /speckit.tasks)
```

### Source Code (repository root)

```text
src/
├── core/
├── solve/
├── util/
├── io/
├── generate/
├── app/
tests/
├── unit/
├── integration/
├── contract/
specs/001-fix-v2-v3-solvers/
```

**Structure Decision**: Retain single-project; only solver internals extended.

## Phase 0: Outline & Research

Change Areas & Decisions (to document in research.md):
1. In-place logic pass application at each search node
2. MRV by value + LCV/frontier ordering definition
3. Corridor computation via dual multi-source BFS distance-sum ≤ (t-1)
4. Corridor cache life-cycle (invalidate on placements; mark clean after build)
5. Degree metric = count of empty neighbors (endpoints need ≥1, middles ≥2)
6. Region capacity check (minimum empties to host a gap)
7. Off-by-one inequality audit (confirm ≤ t-1 corridor condition)
8. Logic pass return signature (progress_made + solved)
9. Tiny transposition table (key design, capacity, replacement policy)

Deliverable: `research.md` with Decision / Rationale / Alternatives for each.

## Phase 1: Design & Contracts

Artifacts:
- `data-model.md`: CandidateModel, CorridorMap, DegreeIndex, RegionCache, TranspositionTable, SearchConfig.
- `contracts/solver-internal.md`: Function contracts for logic fixpoint, corridor & degree pruning, region capacity, MRV/LCV choice, transposition lookup, trace hook.
- `quickstart.md`: Run canonical 5x5 with v2 and v3, expected timings and trace snippet.
- Agent context update (copilot) via script.

## Phase 1 Constitution Re-check (Post-Design Target)
- Explanations: pruning steps produce strategy-tagged reasons → PASS
- Determinism: Stable ordering; transposition key deterministic → PASS
- Public API: solve() unchanged; internal search state isolated → PASS

## Phase 2 (Future Implementation Tasks)
1. Refactor logic_v2 corridor & degree helpers
2. Implement region capacity pruning (coarse)
3. Add logic fixpoint (progress, solved)
4. Integrate into v3 search expansion
5. Rework MRV to values
6. Add LCV/frontier ordering
7. Add optional transposition table
8. Add trace reasons for pruning
9. Regression & performance tests
10. Benchmark canonical puzzle

## Complexity Tracking
No constitution violations introduced; explanation logging new but compliant.

## Next Steps
Create research.md, data-model.md, contracts/solver-internal.md, quickstart.md; update agent context.
