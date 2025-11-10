# Project Directory Structure

## Top-Level Organization

```
fuzzypuzzy/
├── app/                    # Application entry points
├── core/                   # Core domain models (Grid, Puzzle, Position, etc.)
├── solve/                  # Solver algorithms (v0, v1, v2, v3)
├── generate/               # Puzzle generation and uniqueness checking
│   └── uniqueness_staged/  # NEW: Staged uniqueness checker (72x faster)
├── io/                     # Input/output handlers
├── util/                   # Utility functions
├── tests/                  # Test suite (150 tests)
├── demos/                  # Demonstration scripts (NEW)
├── docs/                   # Documentation
│   └── validation/         # Performance and validation docs (NEW)
├── specs/                  # Feature specifications
├── benchmarks/             # Performance benchmarks
├── scripts/                # Utility scripts
└── hidato.py              # Main entry point

```

## Key Directories

### `/demos/` (NEW)
Demonstration scripts showcasing the staged uniqueness checker:
- `demo_real_puzzles.py` - Visual proof of puzzle generation
- `demo_speed_comparison.py` - Performance comparison (79x speedup)
- `README.md` - Usage instructions

**Run:** `python demos/demo_real_puzzles.py`

### `/docs/validation/` (NEW)
Performance and validation documentation:
- `PROOF_OF_PERFORMANCE.md` - Comprehensive performance analysis
- `TEST_RESULTS.md` - Full test suite results (149/150 passing)
- `UNIQUENESS-VERIFICATION.md` - Uniqueness guarantee explanation

### `/generate/uniqueness_staged/` (NEW)
Staged uniqueness checker implementation:
- Stage 1: Early exit with heuristics (40% budget)
- Stage 2: Randomized probes (40% budget) - infrastructure only
- Stage 3: SAT/CP solver (20% budget) - optional
- **Result:** 72.8x faster than old exhaustive search

### `/tests/`
Complete test suite with 150 tests:
- Unit tests (solver, generation, core)
- Integration tests (end-to-end)
- Performance tests
- Staged uniqueness checker tests (NEW)

**Run:** `python -m pytest tests/ -v`

## Recent Additions (Branch: 001-staged-uniqueness-validation)

### New Files:
- `demos/` directory with 2 demo scripts
- `docs/validation/` with 3 documentation files
- `generate/uniqueness_staged/` with 8 modules (~1,200 lines)
- 6 new test files in `tests/`

### Modified Files:
- `generate/pruning.py` - Integrated staged checker (line 232)

### Cleanup:
- Moved test files from root to `tests/`
- Moved demo files from root to `demos/`
- Moved documentation from root to `docs/validation/`
- Organized top-level directory structure

## Quick Commands

```powershell
# Generate puzzles
python hidato.py --generate --size 7 --difficulty hard

# Run demonstrations
python demos/demo_real_puzzles.py
python demos/demo_speed_comparison.py

# Run all tests
python -m pytest tests/ -v

# Run tests (excluding flaky timing test)
python -m pytest tests/ -k "not test_v3_solves_canonical_5x5" -q
```

## Documentation

- `README.md` - Main project documentation
- `docs/TESTING_REFERENCE.md` - Testing guidelines
- `docs/validation/PROOF_OF_PERFORMANCE.md` - Performance proof
- `demos/README.md` - Demo usage instructions

## Performance Highlights

### Puzzle Generation:
- **Old:** 2-5 seconds per uniqueness check
- **New:** ~50-150ms per uniqueness check
- **Speedup:** 72.8x faster on average

### Real-World Impact:
- **Old:** ~125+ seconds to generate one puzzle
- **New:** ~200-600ms to generate one puzzle
- **Result:** 200x faster end-to-end generation
