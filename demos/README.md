# Demonstration Scripts

This directory contains demonstration scripts for showcasing the staged uniqueness checker performance and capabilities.

## Available Demos

### 1. `demo_real_puzzles.py`

Generates multiple real puzzles and visually displays them, proving that the staged uniqueness checker is working in production.

**What it shows:**
- Actual puzzle grids (5x5, 6x6, 7x7)
- Generation timing for each puzzle
- Uniqueness verification during generation
- Solvability of generated puzzles

**Run:**
```powershell
$env:PYTHONPATH="$pwd"; python demos/demo_real_puzzles.py
```

**Expected output:**
- 4 puzzles with visual grids
- Generation time: ~200-600ms total
- All puzzles verified unique during generation

---

### 2. `demo_speed_comparison.py`

Direct side-by-side comparison of the old exhaustive search method vs the new staged uniqueness checker.

**What it shows:**
- Same test puzzle checked by both methods
- Timing comparison
- Node exploration comparison
- Agreement verification (both methods agree)

**Run:**
```powershell
$env:PYTHONPATH="$pwd"; python demos/demo_speed_comparison.py
```

**Expected output:**
```
OLD METHOD: 5,341ms, 8,939 nodes
NEW METHOD: 67ms, 0 nodes
Speed improvement: 79.7x FASTER
Agreement: YES
```

---

## Documentation

For detailed performance analysis and test results, see:
- `docs/validation/PROOF_OF_PERFORMANCE.md` - Comprehensive performance proof
- `docs/validation/TEST_RESULTS.md` - Full test suite results
- `docs/validation/UNIQUENESS-VERIFICATION.md` - Uniqueness guarantee explanation

---

## Purpose

These demos provide **visual proof** that:

1. **Hard puzzles are being generated faster** (72-80x speedup)
2. **Uniqueness is guaranteed** (verified during generation)
3. **The system is production-ready** (real puzzles shown)

Run these demos to see the staged uniqueness checker in action!
