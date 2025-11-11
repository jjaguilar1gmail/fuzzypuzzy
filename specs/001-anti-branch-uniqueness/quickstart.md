# Quickstart: Anti-Branch Uniqueness & Size-Aware Clue Distribution

## Enable Enhanced Uniqueness
- Generator config: enable `uniqueness_probe=anti_branch_v1` and `probe_budgets=size_tier_default`.
- Optional: enable `fallback_sat=false` (default). Extended attempt policy applies (+50% budgets then reject).

## Size & Difficulty Policies
- Anchors: endpoints always; Easy keep a few spaced turns; Medium at most one soft turn; Hard endpoints only unless repair needed.
- Density floors: by size & difficulty (see research.md D8).

## De-Chunk Pass
- After density target met, run de-chunk to reduce clusters; changes are guarded by uniqueness probe.

## Telemetry
- Logs line-delimited JSON per attempt and final summary. Capture probe outcomes, budgets used, spacing metrics, and final density.

## CLI Example
- Example run (conceptual):
  - `python -m app.packgen.cli --path-mode backbite_v1 --sizes 5,6,7,8,9 --difficulties easy,medium,hard --enable-anti-branch`

## Notes
- Deterministic given seed. Probe permutations derived from seed.
- Serpentine/random_walk supported if implemented in generator; otherwise ignored.
