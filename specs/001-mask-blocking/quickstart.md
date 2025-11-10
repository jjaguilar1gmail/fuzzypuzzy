# Quickstart: Mask-Driven Blocking & Ambiguity-Aware Repair

## Enabling the Mask
```python
from generate.generator import GeneratorConfig, Generator

cfg = GeneratorConfig(
    seed=1234,
    size=9,
    difficulty="hard",
    mask_enabled=True,
    mask_mode="auto",        # "auto" | "template" | "procedural"
    mask_template="corridor", # when mask_mode == "template"
    mask_density=None,        # None => pick density heuristic by size+difficulty
    structural_repair_enabled=True,
    structural_repair_max=2,
)

puzzle = Generator(cfg).generate_puzzle()
print(puzzle.metrics.mask_pattern_id, puzzle.metrics.mask_cells_count)
```

## Configuration Knobs
- mask_enabled: Master switch (False → legacy behavior)
- mask_mode: auto selects template first fallback to procedural; template forces chosen pattern; procedural samples density
- mask_template: name from pattern set (corridor, ring, spiral, cross)
- mask_density: override heuristic; validated ≤10%
- mask_max_attempts: retries for invalid pattern/density
- structural_repair_enabled: attempt ambiguity-aware block insertion before clue fallback
- structural_repair_max: max block attempts (default 2)
- structural_repair_timeout_ms: guardrail against long repair sequences

## Metrics Fields (GenerationMetrics)
- mask_pattern_id
- mask_density / mask_cells_count
- mask_attempts
- ambiguity_regions_detected
- structural_repairs (list of actions)
- uniqueness_method_used

## Interpreting Results
- If uniqueness_method_used == "fallback-old": staged checker inconclusive; consider tuning mask density or repair budgets.
- structural_repairs empty & ambiguity_regions_detected >0 → repairs disabled or budget exhausted.

## Error Handling
- InvalidMaskError: adjust density or pattern; consider procedural mode.
- StructuralRepairExhausted: puzzle produced with clue fallback (still valid). Log contains repair_action with action_type=="clue".

## Testing Tips
- For deterministic comparisons, fix seed and toggle mask_enabled.
- Benchmark density sweep: vary mask_density in [0.01, 0.02, 0.03, 0.05].

## Fallback Behavior
If mask generation fails all attempts: generation proceeds without a mask (logged mask_pattern_id=="none").
If structural repairs fail uniqueness: clue fallback inserts minimal clue then re-check.

