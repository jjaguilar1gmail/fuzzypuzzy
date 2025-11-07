# Internal Contracts: v2/v3 improvements

Created: 2025-11-07 | Branch: 001-fix-v2-v3-solvers

## Contract 1: Logic fixpoint
- Name: apply_logic_fixpoint(state) -> (progress: bool, solved: bool, steps: list)
- Inputs: current search state (copy of Puzzle + CandidateModel)
- Behavior: Repeatedly apply v2 strategies (singles, single-position, corridor, degree, minimal region capacity) until no changes; record steps with reasons.
- Errors: If contradiction detected (empty candidates for a value or position), return progress=True, solved=False and state marked unsat.

## Contract 2: Value MRV with LCV/frontier
- Name: choose_value_mrv(candidates) -> int
- Behavior: Select value k minimizing |value_to_positions[k]|; tie-break by k ascending.
- Name: order_positions_lcv_frontier(k, state) -> list[Position]
- Behavior: Order candidate positions by increasing impact: prefer higher empty-neighbor counts and frontier connectivity for k±1.

## Contract 3: Corridor helpers
- Name: compute_corridor(start:int, end:int, state) -> set[Position]
- Behavior: Dual multi-source BFS from empty neighbors of anchors; return positions p with distA[p] + distB[p] ≤ (t-1), t = end-start. Return empty set if anchors not both present.
- Name: prune_by_corridor(k, state) -> (eliminations:int, affected:list[Position])
- Behavior: For gap (k,k+t), limit candidates of values in (k,k+t) to the union of corridor cells; remove others with reason.

## Contract 4: Degree helpers
- Name: compute_degree_map(state) -> dict[Position,int]
- Behavior: For each cell, count empty neighbors only.
- Name: prune_by_degree(k, pos, degree_map, state) -> bool
- Behavior: Eliminate (k,pos) if endpoint (k=1 or N) and degree_map[pos] < 1, or middle and degree_map[pos] < 2; record reason.

## Contract 5: Region capacity (coarse)
- Name: compute_regions(state) -> list[set[Position]]
- Behavior: Connected components of empty cells.
- Name: infer_region_capacity(gap:(start,end), corridor:set[Position], regions:list[set]) -> int
- Behavior: Return maximum empties available among regions intersecting corridor; if max < (t-1), prune choices outside feasible regions.

## Contract 6: Transposition table (optional)
- Name: make_state_key(state) -> tuple[int,...]
- Behavior: Value→pos array of length N using -1 for unplaced; pos encoded as row*W+col.
- Name: transposition_lookup(key) -> Optional[result]
- Name: transposition_store(key, result)
- Behavior: Bounded map (e.g., 10k entries), eviction policy simple FIFO/LRU; must not affect determinism of search order.

## Contract 7: Trace hooks
- Every elimination/placement adds a record: {strategy, value, pos, count_before, count_after, note}
- Final solve includes validator PASS section (givens preserved, 1..N contiguous).
