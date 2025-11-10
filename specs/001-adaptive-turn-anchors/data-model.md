# Data Model: Adaptive Turn Anchors

## Entities

### AnchorPolicy
Fields:
- name: str (e.g., adaptive_v1, legacy)
- easy_range: tuple(int,int) (#hard anchors to keep beyond endpoints)
- medium_soft: bool (indicates presence of single soft anchor)
- hard_repairs_enabled: bool
- extreme_repairs_enabled: bool
- min_index_gap: int (default e.g. 2)
- prefer_four_neighbor_on_sparse: bool
- version: str

Validation:
- easy_range low>=0, high>=low
- min_index_gap>=0

### TurnAnchor
Fields:
- position: (row,col)
- kind: enum {hard, soft, repair}
- reason: str ("stability" | "option" | "repair" | "endpoints")

### AnchorMetrics
Fields:
- anchor_count: int
- hard_count: int
- soft_count: int
- repair_count: int
- positions: list[(row,col)]
- policy_name: str
- anchor_selection_reason: str ("policy" | "repair" | "legacy" | "disabled")
- min_index_gap_enforced: bool
- adjacency_mode: str ("4" | "8")

### UniquenessRepairCandidate
Fields:
- segment_start: int (path index)
- segment_end: int
- branching_factor: int
- midpoint_pos: (row,col)

### RepairDecision
Fields:
- chosen_pos: (row,col)
- rationale: str
- branching_factor: int
- alternative_positions: list[(row,col)]

## Relationships
- AnchorPolicy guides creation of TurnAnchor list.
- AnchorMetrics summarizes TurnAnchor after selection.
- UniquenessRepairCandidate produced during uniqueness verification; RepairDecision selects TurnAnchor(kind=repair).

## State Transitions
1. Path built → potential turn points derived → anchor policy applied → anchors tagged (hard/soft).
2. Soft anchor removal test: if uniqueness unchanged → anchor dropped.
3. Uniqueness failure → compute differing segments → produce candidates → choose repair anchor → add clue.

## Determinism Guarantees
- Policy application order stable by path index.
- Soft anchor evaluation deterministic using solver result + seed.
- Repair selection deterministic (highest branching_factor; tie-break by midpoint index then row,col ordering).

