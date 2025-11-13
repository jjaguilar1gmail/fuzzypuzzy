# UI Interaction Contracts: Guided Sequence Flow

All interactions treated as event contracts. State machine driven by SequenceState and Board state.

## Event: SELECT_ANCHOR
- Input: { position }
- Preconditions: position holds a value (cell.value != null)
- Effects: anchorValue=cell.value; anchorPos=position; compute nextTarget + legalTargets; recompute chainEndValue/chainLength
- Errors: If cell empty → ignore
- Response: { anchorValue, nextTarget, legalTargets, chainEndValue, chainLength, nextTargetChangeReason:'anchor-change'|'neutral' }

## Event: PLACE_NEXT
- Input: { position }
- Preconditions: nextTarget != null; position in legalTargets
- Effects: cell.value = nextTarget; anchorValue=nextTarget; recompute nextTarget & legalTargets; update chainEndValue/chainLength; push undo
- Errors: position not in legalTargets ⇒ ignore or mistake event
- Response: { placed: true, value: nextTarget, nextTarget, legalTargets, chainEndValue, chainLength, nextTargetChangeReason:'placement'|'neutral' }

## Event: REMOVE_CELL
- Input: { position }
- Preconditions: cell.value != null && !cell.given
- Effects: cell.value=null; recompute chainEndValue/chainLength; determine tail involvement; clear anchor if removed anchor or tail; push undo; may clear nextTarget
- Errors: given cell ⇒ ignore
- Response: { removed: true, chainEndValue, chainLength, nextTarget:null|number, nextTargetChangeReason:'tail-removal'|'non-tail-removal'|'neutral' }

## Event: TOGGLE_GUIDE
- Input: { enabled:boolean }
- Effects: guideEnabled updated
- Response: { guideEnabled }

## Event: UNDO
- Preconditions: undoStack not empty
- Effects: revert last action; recompute sequence state & chainEndValue/chainLength
- Response: { undone: true, anchorValue, nextTarget, chainEndValue, chainLength, nextTargetChangeReason }

## Event: REDO
- Preconditions: redoStack not empty
- Effects: reapply action; recompute sequence state & chainEndValue/chainLength
- Response: { redone: true, anchorValue, nextTarget, chainEndValue, chainLength, nextTargetChangeReason }

## Query: GET_SEQUENCE_STATE
- Input: none
- Output: { anchorValue, anchorPos, nextTarget, legalTargets, guideEnabled, chainEndValue, chainLength, nextTargetChangeReason }

## Query: COMPUTE_LEGAL
- Input: { anchorPos }
- Preconditions: anchorPos valid & has value
- Output: { legalTargets, anchorValue, nextTarget, chainEndValue, chainLength }

## Error Modes
| Code | Description | Recovery |
|------|-------------|----------|
| INVALID_TARGET | Attempted PLACE_NEXT where not legal | Ignore + optional mistake feedback |
| NO_ANCHOR | Action requires anchor but none set | Return neutral state |
| GIVEN_REMOVAL | Attempted removal on clue | Ignore |
| EMPTY_ANCHOR | SELECT_ANCHOR on empty cell | Ignore |
| STALE_TARGET | nextTarget inconsistent with chainEndValue after mutation | Force recompute; emit updated neutral or placement-ready state |

## Mistake Event Emission
When INVALID_TARGET and user intention to place confirmed: emit MistakeEvent { position, attemptedValue, reason, anchorValue, nextTargetChangeReason }.
