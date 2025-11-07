"""App façade: API

Contains the API class as a high-level façade for CLI/GUI.
"""
import sys
import os

# Add parent directory to path when running as script
if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    if current_dir not in sys.path:
        sys.path.insert(0, current_dir)

from hidato_io.exporters import ascii_print
from hidato_io.serializers import save_json, load_json
from generate.generator import Generator
from app.presets import Presets
from app.move_validator import MoveValidator
from solve.solver import Solver
from util.profiling import time_it

class HidatoREPL:
    """Simple REPL for Hidato MVP."""
    
    def __init__(self):
        self.current_puzzle = None
        self.current_metadata = None
        self.move_validator = None
        self.last_move = None  # Store (row, col, value) for rendering
        
    def run(self):
        """Run the REPL loop."""
        print("Hidato Terminal MVP - Advanced Solver Edition")
        print("Commands: generate <size>, show, move <row> <col> <value>, hint [--mode <mode>], solve [--mode <mode>], export <file>, import <file>, quit")
        print("Solver modes: logic_v0 (basic), logic_v1 (enhanced), logic_v2 (spatial), logic_v3 (search)")
        print("Example: generate 5x5, solve --mode logic_v1, hint --mode logic_v2")
        print("Type 'help' for detailed command information")
        print()
        
        while True:
            try:
                command = input("hidato> ").strip()
                if not command:
                    continue
                    
                parts = command.split()
                cmd = parts[0].lower()
                
                if cmd == "quit" or cmd == "exit":
                    print("Goodbye!")
                    break
                elif cmd == "generate":
                    self._handle_generate(parts[1:])
                elif cmd == "show":
                    self._handle_show()
                elif cmd == "move":
                    self._handle_move(parts[1:])
                elif cmd == "hint":
                    self._handle_hint(parts[1:])
                elif cmd == "solve":
                    self._handle_solve(parts[1:])
                elif cmd == "export":
                    self._handle_export(parts[1:])
                elif cmd == "import":
                    self._handle_import(parts[1:])
                elif cmd == "help":
                    self._handle_help()
                else:
                    print(f"Unknown command: {cmd}")
                    print("Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\nGoodbye!")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    def _handle_generate(self, args):
        """Handle generate command."""
        if not args:
            print("Usage: generate <size> [--seed <int>]")
            print("Supported sizes: 5x5, 7x7")
            return
        
        size_str = args[0]
        seed = None
        
        # Parse optional --seed argument
        if len(args) >= 3 and args[1] == "--seed":
            try:
                seed = int(args[2])
            except ValueError:
                print("Invalid seed value")
                return
        
        try:
            config = Presets.get_default_config(size_str)
            
            print(f"Generating {size_str} puzzle", end="")
            if seed is not None:
                print(f" with seed {seed}", end="")
            print("...")
            
            with time_it(f"Generate {size_str}"):
                puzzle, metadata = Generator.generate(
                    config["rows"], config["cols"],
                    difficulty=config["difficulty"],
                    path_mode=config["path_mode"],
                    clue_mode=config["clue_mode"],
                    seed=seed
                )
            
            self.current_puzzle = puzzle
            self.current_metadata = metadata
            self.move_validator = MoveValidator(puzzle)
            self.last_move = None  # Reset last move on new puzzle
            
            print(f"Seed: {metadata['seed']}, Givens: {metadata['num_givens']}")
            print()
            ascii_print(puzzle)
            
        except Exception as e:
            print(f"Generation failed: {e}")
    
    def _handle_show(self):
        """Handle show command."""
        if self.current_puzzle is None:
            print("No puzzle loaded. Use 'generate <size>' first.")
            return
        
        print(f"Current puzzle: {self.current_metadata['size'][0]}x{self.current_metadata['size'][1]}")
        print(f"Difficulty: {self.current_metadata['difficulty']}")
        print(f"Givens: {self.current_metadata['num_givens']}")
        print()
        ascii_print(self.current_puzzle)
    
    def _handle_move(self, args):
        """Handle move command."""
        if self.current_puzzle is None:
            print("No puzzle loaded. Use 'generate <size>' first.")
            return
        
        if len(args) != 3:
            print("Usage: move <row> <col> <value>")
            print("Example: move 2 3 15")
            return
        
        try:
            row = int(args[0])
            col = int(args[1])
            value = int(args[2])
        except ValueError:
            print("Error: row, col, and value must be integers")
            return
        
        # Convert to 0-based indexing (user inputs 1-based)
        row -= 1
        col -= 1
        
        is_valid, error_msg = self.move_validator.validate_move(row, col, value)
        if is_valid:
            if self.move_validator.apply_move(row, col, value):
                self.last_move = (row, col, value)
                print(f"✅ Placed {value} at ({row + 1}, {col + 1})")
                print()
                ascii_print(self.current_puzzle, highlight_move=(row, col))
            else:
                print("❌ Failed to apply move (unexpected error)")
        else:
            print(f"❌ Invalid move: {error_msg}")
    
    def _handle_hint(self, args):
        """Handle hint command with optional mode parameter."""
        if self.current_puzzle is None:
            print("No puzzle loaded. Use 'generate <size>' first.")
            return
        
        # Parse mode argument
        mode = "logic_v0"  # default
        config = {}
        
        i = 0
        while i < len(args):
            if args[i] == "--mode" and i + 1 < len(args):
                mode = args[i + 1]
                i += 2
            else:
                i += 1
        
        try:
            solver = Solver(self.current_puzzle)
            hint = solver.get_hint(mode=mode, **config)
            
            if hint:
                print(f"💡 Hint ({mode}): {hint}")
                pos = hint.position
                ascii_print(self.current_puzzle, highlight_move=(pos.row, pos.col))
            else:
                print(f"🤔 No hints available using {mode} - puzzle may require a different mode or be unsolvable")
        except Exception as e:
            print(f"❌ Error getting hint: {e}")
    
    def _handle_solve(self, args):
        """Handle solve command with optional mode parameter."""
        if self.current_puzzle is None:
            print("No puzzle loaded. Use 'generate <size>' first.")
            return
        
        # Parse mode argument
        mode = "logic_v0"  # default
        config = {}
        
        i = 0
        while i < len(args):
            if args[i] == "--mode" and i + 1 < len(args):
                mode = args[i + 1]
                i += 2
            else:
                i += 1
        
        # Set reasonable defaults for logic_v3 in REPL
        if mode == "logic_v3":
            config.setdefault('timeout_ms', 10000)  # 10 seconds default
            config.setdefault('max_nodes', 50000)   # More nodes
            config.setdefault('max_depth', 100)     # Deeper search
        
        try:
            print(f"🔍 Attempting to solve puzzle using {mode}...")
            
            with time_it(f"Solve puzzle ({mode})"):
                result = Solver.solve(self.current_puzzle, mode=mode, **config)
            
            if result.solved:
                print(f"✅ {result.message}")
                print(f"🎯 Solution found in {len(result.steps)} steps")
                print()
                
                # The solver modifies a copy, so we need to get the final puzzle
                # from the solver instance that was used
                solver = Solver(self.current_puzzle)
                if mode == "logic_v0":
                    solved_result = solver._solve_logic_v0()
                elif mode == "logic_v1":
                    solved_result = solver._solve_logic_v1(**config)
                elif mode == "logic_v2":
                    solved_result = solver._solve_logic_v2(**config)  
                elif mode == "logic_v3":
                    solved_result = solver._solve_logic_v3(**config)
                else:
                    solved_result = solver._solve_logic_v0()
                ascii_print(solver.puzzle)
                
                # Show summary of steps
                if len(result.steps) <= 10:
                    print("\nSolution steps:")
                    for i, step in enumerate(result.steps, 1):
                        print(f"  {i}. {step}")
                else:
                    print(f"\nFirst 5 steps:")
                    for i, step in enumerate(result.steps[:5], 1):
                        print(f"  {i}. {step}")
                    print(f"  ... ({len(result.steps) - 10} more steps)")
                    print(f"Last 5 steps:")
                    for i, step in enumerate(result.steps[-5:], len(result.steps) - 4):
                        print(f"  {i}. {step}")
            else:
                print(f"❌ {result.message}")
                if result.steps:
                    print(f"🔧 Made {len(result.steps)} logical moves before getting stuck:")
                    for step in result.steps[-3:]:  # Show last 3 moves
                        print(f"  {step}")
                
        except Exception as e:
            print(f"❌ Error solving puzzle: {e}")
    
    def _handle_export(self, args):
        """Handle export command."""
        if self.current_puzzle is None:
            print("No puzzle loaded. Use 'generate <size>' first.")
            return
        
        if not args:
            print("Usage: export <filename>")
            print("Example: export puzzle.json")
            return
        
        filename = args[0]
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            save_json(self.current_puzzle, filename, self.current_metadata)
            print(f"✅ Puzzle exported to {filename}")
        except Exception as e:
            print(f"❌ Export failed: {e}")
    
    def _handle_import(self, args):
        """Handle import command."""
        if not args:
            print("Usage: import <filename>")
            print("Example: import puzzle.json")
            return
        
        filename = args[0]
        if not filename.endswith('.json'):
            filename += '.json'
        
        try:
            puzzle, metadata = load_json(filename)
            self.current_puzzle = puzzle
            self.current_metadata = metadata
            self.move_validator = MoveValidator(puzzle)
            self.last_move = None
            
            print(f"✅ Puzzle imported from {filename}")
            print(f"Size: {metadata.get('size', 'Unknown')}")
            print(f"Difficulty: {metadata.get('difficulty', 'Unknown')}")
            print()
            ascii_print(puzzle)
        except FileNotFoundError:
            print(f"❌ File not found: {filename}")
        except Exception as e:
            print(f"❌ Import failed: {e}")
    
    def _handle_help(self):
        """Handle help command."""
        print("Available commands:")
        print("  generate <size> [--seed <int>]  Generate new puzzle (5x5, 7x7)")
        print("  show                            Show current puzzle")
        print("  move <row> <col> <value>        Place a number (1-based coordinates)")
        print("  hint [--mode <mode>]            Get a solving hint")
        print("  solve [--mode <mode>]           Auto-solve the puzzle")
        print("  export <filename>               Save puzzle to JSON file")
        print("  import <filename>               Load puzzle from JSON file")
        print("  help                            Show this help")
        print("  quit                            Exit REPL")
        print()
        print("Solver modes:")
        print("  logic_v0 (default)              Basic consecutive logic")
        print("  logic_v1                        Enhanced two-ended propagation") 
        print("  logic_v2                        Region-aware spatial reasoning")
        print("  logic_v3                        Bounded search with backtracking")
        print()
        print("Examples:")
        print("  hint --mode logic_v1")
        print("  solve --mode logic_v2")

class API:
    """High-level API façade."""
    
    @staticmethod
    def start_repl():
        """Start the REPL interface."""
        repl = HidatoREPL()
        repl.run()

# Entry point for script execution
if __name__ == "__main__":
    API.start_repl()
