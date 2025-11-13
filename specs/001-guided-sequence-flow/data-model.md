# Data Model: Guided Sequence Flow Play

## Entities

### BoardCell
| Field | Type | Description | Validation |
|-------|------|-------------|------------|
| position | {row:int, col:int} | Grid coordinates | 0 ≤ row < rows; 0 ≤ col < cols |
| value | number|null | Placed number or empty | If value set: integer ≥1 ≤ maxValue |
| given | boolean | True if original clue | Immutable once true |
| blocked | boolean | True if cell unusable | Blocked implies value = null |
| highlighted | boolean | Derived: legal placement candidate | Computed each render (not stored persistently) |
| anchor | boolean | Derived: currently selected anchor | At most one cell anchor=true |
| mistake | boolean | Indicates user placed illegal number (future) | For MVP: only used transiently |

### SequenceState
| Field | Type | Description |
|-------|------|-------------|
| anchorValue | number|null | Current selected value n |
| anchorPos | position|null | Position of anchor cell |
| nextTarget | number|null | Value v+1 if chain can extend; null if neutral |
| legalTargets | position[] | Array of legal empty adjacent cells if nextTarget exists |
| guideEnabled | boolean | "Show Guide" toggle |
| chainEndValue | number|null | Highest contiguous value in primary chain (start at 1 or lowest given) |
| chainLength | number | Length of contiguous chain |
| nextTargetChangeReason | 'placement'|'anchor-change'|'tail-removal'|'non-tail-removal'|'neutral' | Cause of latest nextTarget recompute |

### UndoAction
| Field | Type | Description |
|-------|------|-------------|
| type | 'PLACE'|'REMOVE' | Action category |
| position | position | Cell affected |
| value | number | Number placed or removed |
| previousSequenceSnapshot | Partial<SequenceState> | For restoration of anchor/next target |
| timestamp | number | Epoch ms |
| changeReason | mirrors SequenceState.nextTargetChangeReason | Reason associated with this action outcome |

### MistakeEvent
| Field | Type | Description |
|-------|------|-------------|
| position | position | Where invalid attempt occurred |
| attemptedValue | number | Value the system expected to place |
| reason | 'not-adjacent'|'occupied'|'no-target' | Classification |
| timestamp | number | Epoch ms |

### PlayerSettings
| Field | Type | Description |
|-------|------|-------------|
| guideEnabled | boolean | Persisted preference (local storage) |
| highlightIntensity | 'low'|'medium'|'high' | Visual strength |
| highContrast | boolean | Accessibility toggle |

## Derived / Algorithms

### Adjacency
```
getAdjacents(pos): return all positions (r',c') with |r'-r| ≤ 1 and |c'-c| ≤ 1 excluding self
```
Filter to empties & non-blocked.

### Chain Detection
```
valuesMap = Map(value -> position)
start = (valuesMap contains 1) ? 1 : min(valuesMap.keys())
current = start
while valuesMap.has(current+1): current++
chainEnd = current
nextCandidate = chainEnd + 1 <= maxValue ? chainEnd + 1 : null
```
Validate nextCandidate has at least one legal adjacency from its predecessor; else nextTarget=null.

### Next Target Computation
```
if anchorValue == null: nextTarget=null
else if no legal adjacency for anchorValue+1: nextTarget=null
else nextTarget=anchorValue+1
```

### Legal Targets
```
legalTargets = adjacents(anchorPos).filter(cell empty & not blocked)
```

### Removal Handling
```
On REMOVE(value at pos):
	- clear cell
	- recompute chainEndValue & chainLength
	- determine tail involvement:
			 if removed value == previous chainEndValue ⇒ nextTargetChangeReason='tail-removal'
			 else ⇒ nextTargetChangeReason='non-tail-removal'
	- if anchor removed OR removed tail ⇒ clear anchor & nextTarget (neutral state)
	- otherwise keep anchor if still valid but may set nextTarget=null if no legal extension
```

## Validation Rules Summary
- Cannot place number if nextTarget=null.
- Cannot place number on occupied or blocked cell.
- Highlighted status never set on occupied/blocked cells.
- Removal allowed only on non-given cells.
- Undo stack length ≤ 50 (discard oldest beyond cap).

## State Transitions (Simplified)
| Action | Precondition | Effects |
|--------|--------------|---------|
| SELECT_ANCHOR(pos) | cell has value | anchorValue=cell.value; anchorPos=pos; recompute nextTarget & legalTargets |
| PLACE_NEXT(pos) | nextTarget != null AND pos ∈ legalTargets | set cell.value=nextTarget; anchorValue=nextTarget; recompute nextTarget & legalTargets; update chainEndValue; nextTargetChangeReason='placement'; push undo |
| REMOVE_CELL(pos) | cell.value != null AND !cell.given | value=null; recompute chain; set nextTargetChangeReason='tail-removal' or 'non-tail-removal'; clear anchor if pos==anchorPos or tail removed; push undo |
| TOGGLE_GUIDE(flag) | none | guideEnabled=flag |
| UNDO() | stack not empty | revert last action; recompute sequence state |
| REDO() | redo stack not empty | apply next action; recompute sequence state |

## Open Considerations
- Mistake marking not fully implemented in MVP (may be added later).
- High-contrast styling specifics delegated to CSS tokens.
