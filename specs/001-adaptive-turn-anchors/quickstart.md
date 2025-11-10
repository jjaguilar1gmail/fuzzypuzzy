# Quickstart: Adaptive Turn Anchors

## What this adds
- Tiered, adaptive turn anchor selection by difficulty
- Soft anchors for medium; repair anchors for hard/extreme only when needed
- Surgical uniqueness repair targeting the most ambiguous segment
- Distribution controls to reduce clustering; prefer 4-neighbor on ultra-sparse hard puzzles

## How to use (CLI)

The default policy is `adaptive_v1` (planning stage). Once implemented, usage will look like this:

```bash
# Easy: endpoints + 2–3 anchors
python hidato.py --generate --size 7 --difficulty easy --seed 42 --verbose

# Medium: endpoints + 1 soft (droppable) anchor
python hidato.py --generate --size 7 --difficulty medium --seed 42 --verbose

# Hard/extreme: endpoints; repair anchors only if uniqueness needs it
python hidato.py --generate --size 9 --difficulty hard --seed 99 --verbose

# Opt-out (legacy anchors)
python hidato.py --generate --size 7 --difficulty medium --seed 42 --anchor-policy legacy
```

## Determinism
- Results reproduce when using the same seed and policy.
- Metrics include anchor_count, types (hard/soft/repair), and policy name.

## Notes
- Medium soft anchors may be removed if redundant.
- Hard/extreme avoid anchors unless required for uniqueness.
