# Quickstart: v2/v3 fixes for 5x5 deterministic

## Prereqs
- Branch: 001-fix-v2-v3-solvers
- Python 3.11

## Run canonical solve (once implemented)
- Logic-only (v2): should reach fixpoint, perform at least one corridor/degree elimination, may stall.
- Bounded-search (v3): must solve ≤100 ms, nodes ≤2,000.

## Suggested commands
- Run tests:
  - cd src; pytest; ruff check .
- Demo run:
  - python app/hidato.py --mode logic_v3 --demo-5x5
  - Optional tracing: --trace --trace-limit 200

## Expected output highlights
- v2: status=no-more-logical-moves; eliminations>0 (corridor/degree)
- v3: solved=true; time≤100ms; nodes≤2000; stable result across runs
- Validator: PASS (givens preserved, contiguous 1..25)
