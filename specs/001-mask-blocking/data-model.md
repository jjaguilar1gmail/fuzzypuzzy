# Data Model: Mask-Driven Blocking & Ambiguity Repair

## Entities

### BlockMask
Represents blocked cells applied before path generation.
- grid_size: int
- cells: set[Position]  (blocked positions)
- density: float (len(cells) / grid_size^2)
- pattern_id: str (e.g. "corridor", "ring", "procedural:v1")
- attempt_index: int
- seed: int
- signature(): str (stable hash e.g. f"{grid_size}:{sorted(cells)}")

### MaskPattern
Describes template or procedural generation parameters.
- name: str
- type: Literal["template","procedural"]
- min_size: int
- max_density: float
- params: dict[str, int|float|str]
- generate(size:int, rng) -> BlockMask (pre-validation)

### AmbiguityRegion
Cluster of cells where divergent solutions differ.
- cells: set[Position]
- divergence_count: int (number of distinct solution paths touching region)
- corridor_width: int (computed via flood outward until block/edge)
- distance_from_clues: int (min manhattan distance to any clue)
- score: float (calculated)

### RepairAction
Represents a structural modification attempt.
- action_type: Literal["block","clue"]
- position: Position
- reason: str
- applied: bool

### GenerationMetrics
Records generation diagnostics.
- mask_pattern_id: str
- mask_density: float
- mask_cells_count: int
- uniqueness_pass: bool
- uniqueness_method_used: str ("staged", "fallback-old")
- elapsed_ms: int
- ambiguity_regions_detected: int
- structural_repairs: list[RepairAction]

## Functions (Contracts TBD)
See contracts directory for signatures.

## Relationships
- Generator will hold optional BlockMask.
- Uniqueness checker consumes mask signature in transposition key.
- AmbiguityRegion derived after multi-solution detection.
- RepairAction applied sequentially; each attempt triggers re-check uniqueness.

## Error Modes
- InvalidMaskError: connectivity or orphan pocket violation.
- MaskDensityExceeded: requested density > template cap.
- StructuralRepairExhausted: repairs budget exceeded without uniqueness.

## Edge Cases
- Empty mask (density 0) -> skip validation; normal flow.
- Full ring on small grid causing isolated center -> validation fails, retry pattern.
- Repair picks cell already blocked/clue -> ignore and rescore next.

