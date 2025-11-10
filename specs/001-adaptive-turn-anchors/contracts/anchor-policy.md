# Contracts: Anchor Policy & Repair

This repository is not a web service; contracts are module-level function contracts.

## Module: generate.anchor_policy (new)

### fn select_anchors(path: list[Position], difficulty: str, policy: AnchorPolicy, symmetry: Optional[str], rng: RNG) -> tuple[list[TurnAnchor], AnchorMetrics]
Input:
- path: Hamiltonian path positions
- difficulty: one of {easy, medium, hard, extreme}
- policy: AnchorPolicy (adaptive_v1 or legacy)
- symmetry: None | "rotational" | "horizontal"
- rng: shared RNG for determinism

Behavior:
- Tag endpoints as hard anchors (always)
- For easy: add 2–3 hard turn anchors (deterministic selection by index order)
- For medium: consider 1 soft anchor; drop if redundant after uniqueness dry-run
- For hard/extreme: no additional anchors unless flagged as `repair`
- Enforce symmetry when applicable (mirror anchors)
- Enforce min_index_gap when provided
- Populate AnchorMetrics

Errors:
- ValueError on invalid difficulty or malformed policy

### fn evaluate_soft_anchor(puzzle, soft_anchor: TurnAnchor) -> bool
Returns True if soft anchor is needed (kept); False if droppable (redundant).

### fn plan_repair(puzzle, solutions: list[Solution]) -> RepairDecision
Input: Multiple valid solutions
Process: Compute differing segments; score by branching factor; choose midpoint; return RepairDecision.

## Module: generate.generator (existing)

Integration points:
- Call select_anchors() after path built and before clue removal
- On uniqueness failure: call plan_repair(), add a repair TurnAnchor, re-verify
- Record AnchorMetrics in GeneratedPuzzle.solver_metrics

Determinism:
- All decisions based on seed-threaded RNG and stable orderings

