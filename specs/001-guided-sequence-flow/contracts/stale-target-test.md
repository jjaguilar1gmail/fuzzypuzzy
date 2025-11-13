# Contract Test Scenario: STALE_TARGET Recovery

## Purpose
Validate UI and state recovery when displayed `nextTarget` becomes invalid due to underlying chain mutation (e.g., removal).

## Preconditions
- Board has contiguous chain 1..10 placed.
- Anchor set to value 10; `nextTarget` shows 11 with two legalTargets.

## Steps
1. User removes cell containing value 10 (tail removal).
2. System processes REMOVE_CELL event.
3. Chain recomputation yields chainEndValue=9.
4. Previously displayed nextTarget=11 now invalid.

## Expected Events
- REMOVE_CELL response: { removed:true, chainEndValue:9, nextTarget:null, nextTargetChangeReason:'tail-removal' }
- Subsequent GET_SEQUENCE_STATE: nextTarget:null; nextTargetChangeReason:'tail-removal'; legalTargets:[]

## STALE_TARGET Handling
If UI still shows 11 after step 2 (race condition):
- Emission of error mode STALE_TARGET triggers silent recompute.
- UI clears indicator and highlights.

## Assertions
| Assertion | Condition |
|-----------|-----------|
| A1 | chainEndValue decreases from 10 to 9 |
| A2 | nextTarget becomes null immediately |
| A3 | nextTargetChangeReason == 'tail-removal' |
| A4 | legalTargets length == 0 |
| A5 | No mistake increment occurs |

## Non-tail Variant
Removing value 7 (middle of chain):
- REMOVE_CELL: chainEndValue stays 10; nextTargetChangeReason:'non-tail-removal'; nextTarget cleared; anchor cleared if removal matched anchor.

## Recovery UX
- Placeholder text displayed: "Select a number to continue sequence." (no error banner)

