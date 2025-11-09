"""Generate module: Generator

Contains the Generator class for overall puzzle generation pipeline.
"""
import time
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver
from .path_builder import PathBuilder
from .clue_placer import CluePlacer
from .validator import Validator
from .models import GenerationConfig, GeneratedPuzzle
from util.rng import RNG


class Generator:
    """Orchestrates the puzzle generation pipeline."""
    
    @staticmethod
    def generate_puzzle(size, difficulty=None, percent_fill=None, seed=None,
                       allow_diagonal=True, blocked=None, path_mode="serpentine",
                       clue_mode="anchor_removal_v1", symmetry=None, turn_anchors=True,
                       timeout_ms=5000, max_attempts=5,
                       allow_partial_paths=False, min_cover_ratio=0.85, path_time_ms=None):
        """Generate a uniqueness-preserving puzzle (T009 new signature).
        
        Args:
            size: Grid size (NxN)
            difficulty: Target difficulty band (easy|medium|hard|extreme)
            percent_fill: Alternative to difficulty - target clue density
            seed: Random seed for reproducibility
            allow_diagonal: Allow diagonal adjacency
            blocked: List of (row, col) blocked positions
            path_mode: "serpentine" or "random_walk"
            clue_mode: "anchor_removal_v1" or "even"
            symmetry: Optional symmetry mode
            turn_anchors: Include turn points as anchors
            timeout_ms: Overall generation timeout
            max_attempts: Maximum generation attempts
            allow_partial_paths: Accept partial coverage paths (T007)
            min_cover_ratio: Minimum coverage for partial acceptance (T007)
            path_time_ms: Path building time budget (T007)
            
        Returns:
            GeneratedPuzzle object
        """
        from .uniqueness import count_solutions
        from .removal import score_candidates
        from .difficulty import DIFFICULTY_BANDS, compute_metrics, assess_difficulty
        from core.position import Position
        import copy
        
        start_time = time.time()
        
        # Validate config
        config = GenerationConfig(
            size=size,
            allow_diagonal=allow_diagonal,
            blocked=blocked or [],
            difficulty=difficulty,
            percent_fill=percent_fill,
            seed=seed,
            path_mode=path_mode,
            clue_mode=clue_mode,
            symmetry=symmetry,
            turn_anchors=turn_anchors,
            timeout_ms=timeout_ms,
            max_attempts=max_attempts,
            # T010: Include smart path config
            allow_partial_paths=allow_partial_paths,
            min_cover_ratio=min_cover_ratio,
            path_time_ms=path_time_ms,
        )
        
        # T020: Validate difficulty parameter
        if difficulty and difficulty not in DIFFICULTY_BANDS:
            valid_difficulties = ', '.join(DIFFICULTY_BANDS.keys())
            raise ValueError(f"Invalid difficulty '{difficulty}'. Valid options: {valid_difficulties}")
        
        # Initialize RNG
        rng = RNG(seed)
        actual_seed = rng.get_seed()
        
        # Build solution path
        total_cells = size * size - len(config.blocked)
        
        grid = Grid(size, size, allow_diagonal=allow_diagonal)
        
        # Mark blocked cells BEFORE building path
        for r, c in config.blocked:
            pos = Position(r, c)
            cell = grid.get_cell(pos)
            cell.blocked = True
        
        # Build path
        path = PathBuilder.build(grid, mode=path_mode, rng=rng, blocked=config.blocked)
        
        # Create constraints based on actual path length
        constraints = Constraints(
            min_value=1,
            max_value=len(path),
            allow_diagonal=allow_diagonal,
            must_be_connected=True
        )
        
        # Store full solution
        solution = [(pos.row, pos.col, grid.get_cell(pos).value) for pos in path]
        
        # Start with ALL cells as givens, then remove down to target
        # This ensures we can actually perform removal
        given_positions = list(path)  # Start with full solution as givens
        
        # Identify anchors (must keep)
        # Always keep 1 and N, but make turn anchors configurable by difficulty
        anchors = {path[0], path[-1]}  # Always keep 1 and N
        
        # Add turn points to anchors based on difficulty and turn_anchors flag
        if turn_anchors:
            turn_positions = []
            for i in range(1, len(path) - 1):
                prev_pos = path[i - 1]
                curr_pos = path[i]
                next_pos = path[i + 1]
                
                dr1 = curr_pos.row - prev_pos.row
                dc1 = curr_pos.col - prev_pos.col
                dr2 = next_pos.row - curr_pos.row
                dc2 = next_pos.col - curr_pos.col
                
                if (dr1, dc1) != (dr2, dc2):
                    turn_positions.append(curr_pos)
            
            # For easier difficulties, only keep some turn anchors
            if difficulty == "easy" and len(turn_positions) > 4:
                # Keep only every other turn for easy
                anchors.update(turn_positions[::2][:4])
            elif difficulty == "medium" and len(turn_positions) > 6:
                # Keep more turns for medium
                anchors.update(turn_positions[::2][:6])
            else:
                # Keep all turns for hard/extreme or if not many turns
                anchors.update(turn_positions)
        
        # Determine target clue count
        total_cells = len(path)
        if percent_fill:
            target_clues = max(len(anchors), int(total_cells * percent_fill))
        elif difficulty:
            band = DIFFICULTY_BANDS.get(difficulty, DIFFICULTY_BANDS["medium"])
            target_clues = max(len(anchors), int(total_cells * band["clue_density_min"]))
        else:
            target_clues = len(anchors) + (total_cells // 4)  # Default
        
        # Removal loop (T011)
        current_givens = set(given_positions)
        attempts_used = 0
        removals_accepted = 0
        
        # Minimum viable clue density (prevent 100% clue puzzles)
        MIN_VIABLE_DENSITY = 0.60  # At least 40% of cells must be empty for a valid puzzle
        min_viable_clues = int(total_cells * MIN_VIABLE_DENSITY)
        
        # Scale removal budget by difficulty (harder = more removals needed = more attempts)
        difficulty_multiplier = {
            "easy": 5,     # Need fewer removals
            "medium": 10,  # Default
            "hard": 20,    # Need many removals
            "extreme": 30  # Need maximum removals
        }
        budget_multiplier = difficulty_multiplier.get(difficulty, 10)
        removal_budget = max_attempts * budget_multiplier
        
        while len(current_givens) > target_clues and attempts_used < removal_budget:
            # Check timeout
            if (time.time() - start_time) * 1000 > timeout_ms:
                break
            
            # Score removal candidates
            candidates = score_candidates(current_givens, path, anchors, grid)
            
            if not candidates:
                break
            
            # Try removing best candidate
            candidate_pos, _ = candidates[0]
            
            # Create test puzzle without this clue
            test_grid = Grid(size, size, allow_diagonal=allow_diagonal)
            
            # Mark blocked cells in test grid
            for r, c in config.blocked:
                pos = Position(r, c)
                test_grid.get_cell(pos).blocked = True
            
            # Restore solution
            for pos in path:
                test_grid.get_cell(pos).value = grid.get_cell(pos).value
            
            # Mark current givens except candidate
            test_givens = current_givens - {candidate_pos}
            for pos in test_givens:
                test_grid.get_cell(pos).given = True
            
            # Clear non-givens
            for pos in path:
                if pos not in test_givens:
                    test_grid.get_cell(pos).value = None
            
            # Create test puzzle with same constraints
            test_puzzle = Puzzle(test_grid, constraints)
            
            # Check uniqueness
            uniqueness_result = count_solutions(
                test_puzzle,
                cap=2,
                node_cap=config.uniqueness_node_cap,
                timeout_ms=config.uniqueness_timeout_ms
            )
            
            if uniqueness_result.is_unique:
                # Accept removal
                current_givens = test_givens
                removals_accepted += 1
            
            attempts_used += 1
        
        # Check if we achieved a viable clue density
        final_density = len(current_givens) / total_cells
        if final_density > MIN_VIABLE_DENSITY:
            import sys
            print(f"\nWARNING: Could not achieve viable clue density!", file=sys.stderr)
            print(f"  Final density: {final_density:.1%} (target: ≤{MIN_VIABLE_DENSITY:.0%})", file=sys.stderr)
            print(f"  Clues: {len(current_givens)}/{total_cells}, Removals: {removals_accepted}, Attempts: {attempts_used}", file=sys.stderr)
            print(f"  This path mode ('{path_mode}') may be too constrained for unique solutions.", file=sys.stderr)
            print(f"  Try: smaller size, serpentine mode, or accept denser puzzles.\n", file=sys.stderr)
        
        # Check if requested difficulty was achieved
        if difficulty:
            band = DIFFICULTY_BANDS.get(difficulty)
            if band:
                target_min = band['clue_density_min']
                target_max = band['clue_density_max']
                if final_density < target_min or final_density > target_max:
                    import sys
                    print(f"\nWARNING: Could not achieve requested difficulty '{difficulty}'", file=sys.stderr)
                    print(f"  Target range: {target_min:.0%}-{target_max:.0%} clues", file=sys.stderr)
                    print(f"  Achieved: {final_density:.1%} ({len(current_givens)}/{total_cells} clues)", file=sys.stderr)
                    print(f"  The puzzle structure limited clue removal.", file=sys.stderr)
                    print(f"  Suggestion: Try a different seed or path mode.\n", file=sys.stderr)
        
        # Build final puzzle
        final_grid = Grid(size, size, allow_diagonal=allow_diagonal)
        
        # Mark blocked cells in final grid
        for r, c in config.blocked:
            pos = Position(r, c)
            final_grid.get_cell(pos).blocked = True
        
        # Restore solution
        for pos in path:
            final_grid.get_cell(pos).value = grid.get_cell(pos).value
        
        # Mark final givens
        for pos in current_givens:
            final_grid.get_cell(pos).given = True
        
        # Clear non-givens
        for pos in path:
            if pos not in current_givens:
                final_grid.get_cell(pos).value = None
        
        final_puzzle = Puzzle(final_grid, constraints)
        
        # Final validation (T016): Re-solve to confirm  
        # Note: We validated uniqueness during removal; this confirms solvability
        final_solve_result = Solver.solve(final_puzzle, mode='logic_v3', 
                                          max_nodes=2000, max_time_ms=10000)
        
        # T017: Compute metrics from solve
        if final_solve_result.solved:
            solver_metrics = compute_metrics(final_puzzle, final_solve_result)
            assessed_label, assessed_score = assess_difficulty(solver_metrics)
        else:
            # Puzzle may be very hard; use fallback metrics
            import sys
            print(f"WARNING: Final solve failed (but uniqueness was verified during removal)", file=sys.stderr)
            print(f"  Message: {final_solve_result.message}", file=sys.stderr)
            print(f"  This may indicate the puzzle is very hard.", file=sys.stderr)
            
            # Fallback metrics
            solver_metrics = {
                'clue_density': len(current_givens) / len(path),
                'logic_ratio': 0.0,
                'nodes': final_solve_result.nodes,
                'depth': final_solve_result.depth,
                'steps': len(final_solve_result.steps),
                'strategy_hits': {},
            }
            assessed_label = difficulty or "extreme"
            assessed_score = 1.0
        
        # Extract givens for metadata
        givens = [(pos.row, pos.col, grid.get_cell(pos).value) 
                 for pos in current_givens]
        
        end_time = time.time()
        
        # Create result
        return GeneratedPuzzle(
            size=size,
            allow_diagonal=allow_diagonal,
            blocked_cells=list(config.blocked),
            givens=sorted(givens),
            solution=sorted(solution),
            difficulty_label=assessed_label,  # T019: Use assessed difficulty
            difficulty_score=assessed_score,
            clue_count=len(current_givens),
            uniqueness_verified=True,
            attempts_used=attempts_used,
            seed=actual_seed,
            path_mode=path_mode,
            clue_mode=clue_mode,
            symmetry=symmetry,
            timings_ms={
                "total": int((end_time - start_time) * 1000),
                "solve": 0,  # SolverResult doesn't track elapsed_ms currently
                "uniqueness": 0,  # TODO: track separately
            },
            solver_metrics=solver_metrics,  # T019: Include computed metrics
        )
    
    @staticmethod
    def generate(rows, cols, difficulty="easy", path_mode="serpentine", 
                clue_mode="even", seed=None):
        """Generate a complete puzzle (legacy signature for compatibility).
        
        Args:
            rows, cols: Grid dimensions
            difficulty: Difficulty level (affects clue density)
            path_mode: Path building strategy
            clue_mode: Clue placement strategy  
            seed: Random seed for reproducibility
            
        Returns:
            (puzzle: Puzzle, metadata: dict)
        """
        start_time = time.time()
        
        # Initialize RNG
        rng = RNG(seed)
        actual_seed = rng.get_seed()
        
        # Create constraints (8-neighbor for Hidato)
        constraints = Constraints(
            min_value=1,
            max_value=rows * cols,
            allow_diagonal=True,
            must_be_connected=True
        )
        
        # Create grid
        grid = Grid(rows, cols, allow_diagonal=True)
        
        # Generate solution path
        path = PathBuilder.build(grid, mode=path_mode, rng=rng, blocked=None)
        
        # Choose clues
        given_positions = CluePlacer.choose(grid, path, mode=clue_mode, rng=rng,
                                           turn_anchors=True, symmetry=None)
        
        # Create puzzle (before clearing non-givens)
        puzzle = Puzzle(grid, constraints, difficulty)
        
        # Mark givens
        CluePlacer.mark_givens(grid, given_positions)
        
        # Clear non-givens to create the puzzle
        puzzle.clear_non_givens()
        
        # Validate
        is_valid, issues = Validator.validate_basic(puzzle)
        if not is_valid:
            raise ValueError(f"Generated invalid puzzle: {issues}")
        
        # Generate metadata
        end_time = time.time()
        metadata = {
            "seed": actual_seed,
            "path_mode": path_mode,
            "clue_mode": clue_mode,
            "difficulty": difficulty,
            "size": (rows, cols),
            "num_givens": len(given_positions),
            "timings_ms": {
                "total": round((end_time - start_time) * 1000, 2)
            },
            "generated_at": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        return puzzle, metadata

