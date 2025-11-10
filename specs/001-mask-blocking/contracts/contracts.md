# Contracts: Mask-Driven Blocking & Ambiguity Repair

Contract signatures are expressed in Python type-like pseudocode (stdlib only).

## generate.mask

- make_mask(size:int, difficulty:str, rng:RNG, attempt_idx:int) -> BlockMask
  - Raises: InvalidMaskError

- validate_mask(mask:BlockMask, size:int, start:Position, end:Position) -> None
  - Raises: InvalidMaskError

- apply_mask(grid:Grid, mask:BlockMask) -> Grid

## uniqueness.probes (enhancements)

- staged_check(grid:Grid, clues:list[Clue], mask_sig:str, budgets:Budgets) -> UniquenessResult
  - Notes: include mask_sig in transposition key.

## ambiguity.repair

- detect_ambiguity_regions(solution_a:Path, solution_b:Path, grid:Grid, clues:list[Clue]) -> list[AmbiguityRegion]

- score_region(region:AmbiguityRegion) -> float

- select_repair_action(regions:list[AmbiguityRegion], mask:BlockMask, grid:Grid, clues:list[Clue], rng:RNG) -> RepairAction|None

- apply_repair(grid:Grid, mask:BlockMask, action:RepairAction) -> tuple[Grid, BlockMask]
  - Notes: If action.block, add to mask; if action.clue, add to clues (fallback).

- attempt_structural_repairs(generator:Generator, max_attempts:int=2, timeout_ms:int=400) -> bool
  - Returns: whether uniqueness achieved after repairs.

## metrics

- record_generation_metrics(metrics:GenerationMetrics) -> None

