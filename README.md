# fuzzypuzzy
A collection of puzzle games with terminal interfaces and solving capabilities.

## Current Feature: Hidato Terminal MVP ✅

A fully functional terminal-playable Hidato puzzle game with generation, solving, and ASCII rendering.

### 🚀 Quick Start

```bash
# Main entry point (recommended)
python hidato.py               # Start interactive REPL
python hidato.py --demo        # Run full feature demonstration
python hidato.py --version     # Show version information
python hidato.py --help        # Show all CLI options

# Alternative entry points
python app/api.py              # Direct REPL access
python complete_demo.py        # Comprehensive feature showcase

# Available commands in REPL:
generate 5x5           # Create a 5x5 puzzle
generate 7x7 --seed 42 # Create reproducible 7x7 puzzle
show                   # Display current puzzle
move 2 3 15           # Place number 15 at position (2,3)
hint                  # Get a solving hint
solve                 # Auto-solve the puzzle
export puzzle.json    # Save puzzle to file
import puzzle.json    # Load puzzle from file
help                  # Show all commands
quit                  # Exit
```

### ✨ Features

- **Puzzle Generation**: 5x5 and 7x7 Hidato puzzles with serpentine paths
- **Interactive Play**: Move validation with adjacency constraints
- **Intelligent Solving**: Hints and auto-solving with step explanations
- **Visual Display**: Clean ASCII rendering with highlighted moves
- **Save/Load**: JSON export/import with metadata preservation
- **Performance**: Sub-second generation, real-time timing feedback

### 🎯 Example Session

```
$ python hidato.py
🎯 Welcome to Hidato Terminal MVP!
Type 'help' for commands or 'quit' to exit.

hidato> generate 5x5 --seed 42
⏱️  Generate 5x5: 1.0ms
Seed: 42, Givens: 5

[ 1] .  .  .  .
 .  .  . [ 7] .
 .  . [13] .  .
 . [19] .  .  .
 .  .  .  . [25]

hidato> move 1 2 2
✅ Placed 2 at (1, 2)

[ 1]* 2* .  .  .
 .  .  . [ 7] .
 .  . [13] .  .
 . [19] .  .  .
 .  .  .  . [25]

hidato> export my-puzzle
✅ Puzzle exported to my-puzzle.json

hidato> hint
💡 Hint: Place 3 at (2, 1): Only possible value for this cell
```

### 🎮 Entry Points

| Command | Purpose | Features |
|---------|---------|----------|
| `python hidato.py` | **Main entry point** | CLI options, help, version info |
| `python hidato.py --demo` | Feature demonstration | Automated showcase of all capabilities |
| `python app/api.py` | Direct REPL | Immediate access to puzzle interface |
| `python complete_demo.py` | Comprehensive test | Full phase-by-phase feature validation |

### 📁 Project Structure

```
core/          # Domain model (Position, Cell, Grid, Puzzle)
generate/      # Puzzle generation pipeline
solve/         # Solving algorithms and strategies  
hidato_io/     # ASCII rendering and JSON serialization
app/           # REPL interface and move validation
util/          # Profiling and utilities
tests/         # Contract tests for core functionality
```

**Documentation**:
- [Feature Specification](specs/001-hidato-terminal-mvp/spec.md) - Requirements and user stories
- [Implementation Plan](specs/001-hidato-terminal-mvp/plan.md) - Technical approach and architecture  
- [Quickstart Guide](specs/001-hidato-terminal-mvp/quickstart.md) - How to run the MVP

