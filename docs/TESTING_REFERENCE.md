# Development Test Archive Reference

During advanced solver development, many test and debug files were created in the root directory. These have been organized and moved to preserve development history while maintaining a clean project structure.

## 📁 Archived Files Location

All development test files have been moved to: **`testing_archive/`**

### Quick Navigation

| File Type | Location | Description |
|-----------|----------|-------------|
| **Debug Sessions** | `testing_archive/debug_sessions/` | Files used to debug specific issues during development |
| **Solver Tests** | `testing_archive/solver_tests/` | Tests for individual solver modes and functionality |
| **Validation Tests** | `testing_archive/validation_tests/` | Tests created to validate bug fixes |
| **Comprehensive Tests** | `testing_archive/comprehensive_tests/` | Full system integration tests |

### 🔍 Finding Specific Files

Common file patterns and their locations:

- `debug_*.py` → `testing_archive/debug_sessions/`
- `test_logic_*.py` → `testing_archive/solver_tests/`
- `test_*fix*.py` → `testing_archive/validation_tests/`
- `comprehensive_*.py` → `testing_archive/comprehensive_tests/`

### 📖 Full Documentation

See `testing_archive/README.md` for complete file inventory and development timeline.

### ⚠️ Important Notes

1. **Use `tests/` for current testing** - The organized tests directory contains the current test suite
2. **Archive is for reference only** - Files in `testing_archive/` may not run correctly due to development state dependencies
3. **Git ignored** - The `testing_archive/` directory is excluded from version control

## Current Testing

For current development and testing, use:
- `tests/` - Official test suite
- `python hidato.py --demo` - System demonstration
- `python complete_demo.py` - If available in testing archive

---
*Cleanup performed: November 7, 2025*