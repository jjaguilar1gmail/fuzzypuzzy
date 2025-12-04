"""Generate module: Generator

Contains the Generator class for overall puzzle generation pipeline.
"""
import time
from core import puzzle
from core.grid import Grid
from core.constraints import Constraints
from core.puzzle import Puzzle
from solve.solver import Solver
from .path_builder import PathBuilder
from .clue_placer import CluePlacer
from .validator import Validator
from .models import GenerationConfig, GeneratedPuzzle
from .difficulty_levels import (
    assign_intermediate_level,
    classify_primary_difficulty,
    compute_difficulty_scores,
    DEFAULT_THRESHOLDS,
)
from util.rng import RNG
from .anchor_policy import get_policy, select_anchors, ANCHOR_KIND_HARD, ANCHOR_KIND_SOFT, ANCHOR_KIND_REPAIR, ANCHOR_KIND_ENDPOINT
from .metrics import StructuralInputs, build_structural_metrics
from hidato_io.exporters import ascii_print

def show_current_puzzle(puzzle_size,cells):
    """Utility to display the current puzzle state for debugging using the hidato_io ascii render tool"""
    temp_puzzle = puzzle.Puzzle(
        grid=puzzle.Grid(puzzle_size, puzzle_size),
        constraints=puzzle.Constraints(1, puzzle_size * puzzle_size)
    )
    for (r, c, v) in cells:
        cell = temp_puzzle.grid.get_cell(puzzle.Position(r, c))
        cell.value = v
        cell.given = True

    ascii_print(temp_puzzle)

class Generator:
    """Orchestrates the puzzle generation pipeline."""
    
    @staticmethod
    def generate_puzzle(size, difficulty=None, percent_fill=None, seed=None,
                       allow_diagonal=True, blocked=None, path_mode="serpentine",
                       clue_mode="anchor_removal_v1", symmetry=None, turn_anchors=True,
                       timeout_ms=5000, max_attempts=5,
                       allow_partial_paths=False, min_cover_ratio=0.85, path_time_ms=None,
                       anchor_policy_name="adaptive_v1", adaptive_turn_anchors=True,
                       mask_enabled=False, mask_mode="auto", mask_template=None,
                       mask_density=0.10, mask_max_attempts=5,
                       structural_repair_enabled=False, structural_repair_max=2):
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
            anchor_policy_name: Anchor policy name (T055)
            adaptive_turn_anchors: Enable adaptive anchor selection (T055)
            mask_enabled: Enable mask-driven blocking (T001)
            mask_mode: Mask generation mode ("auto"|"template"|"procedural") (T001)
            mask_template: Template pattern name ("corridor"|"ring"|"spiral"|"cross") (T001)
            mask_density: Target mask density (0.0-0.12) (T001)
            mask_max_attempts: Max attempts for mask generation (T001)
            structural_repair_enabled: Enable ambiguity-aware structural repair (T029)
            structural_repair_max: Max repair attempts (T029)
            
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
            # T055: Include anchor policy config
            anchor_policy_name=anchor_policy_name,
            adaptive_turn_anchors=adaptive_turn_anchors,
            # T001: Include mask config
            mask_enabled=mask_enabled,
            mask_mode=mask_mode,
            mask_template=mask_template,
            mask_density=mask_density,
            mask_max_attempts=mask_max_attempts,
            structural_repair_enabled=structural_repair_enabled,
            structural_repair_max=structural_repair_max,
        )
        
        # T020: Validate difficulty parameter
        if difficulty and difficulty not in DIFFICULTY_BANDS:
            valid_difficulties = ', '.join(DIFFICULTY_BANDS.keys())
            raise ValueError(f"Invalid difficulty '{difficulty}'. Valid options: {valid_difficulties}")
        
        # Initialize RNG
        rng = RNG(seed)
        actual_seed = rng.get_seed()
        
        # T023: Generate and apply mask if enabled
        mask_cells = []
        mask_pattern_id = None
        mask_attempts = config.mask_max_attempts
        
        if config.mask_enabled:
            from generate.mask import build_mask
            
            # Determine start/end for validation
            # For now, assume corners (will be adjusted by path builder)
            start_pos = (0, 0)
            end_pos = (size - 1, size - 1)
            
            mask = build_mask(
                config=config,
                size=size,
                difficulty=difficulty or "medium",
                start=start_pos,
                end=end_pos,
                allow_diagonal=allow_diagonal
            )
            
            if mask is not None:
                mask_cells = list(mask.cells)
                mask_pattern_id = mask.pattern_id
                mask_attempts = mask.attempt_index + 1
        
        # Build solution path
        total_cells = size * size - len(config.blocked)
        
        grid = Grid(size, size, allow_diagonal=allow_diagonal)
        
        # Mark blocked cells BEFORE building path (original + mask)
        all_blocked = list(config.blocked) + mask_cells
        for r, c in all_blocked:
            pos = Position(r, c)
            cell = grid.get_cell(pos)
            cell.blocked = True
        
        # Build path (T032: now returns PathBuildResult) with all blocked cells
        path_result = PathBuilder.build(grid, mode=path_mode, rng=rng, blocked=all_blocked)
        path = path_result.positions
        path_build_ms = path_result.metrics.get("path_build_ms", 0)
        
        # Check if path generation failed (empty path)
        if not path or len(path) == 0:
            import sys
            print(f"WARNING: Path generation failed with {path_mode} - blocked cells incompatible", file=sys.stderr)
            
            # Try falling back to random_walk_v2 which can handle blocked cells
            if path_mode != 'random_walk_v2' and mask_cells:
                print(f"         Falling back to random_walk_v2 mode", file=sys.stderr)
                grid = Grid(size, size, allow_diagonal=allow_diagonal)
                for r, c in all_blocked:
                    pos = Position(r, c)
                    grid.get_cell(pos).blocked = True
                path_result = PathBuilder.build(grid, mode='random_walk_v2', rng=rng, blocked=all_blocked)
                path = path_result.positions
                path_build_ms = path_result.metrics.get("path_build_ms", 0)
                
                if not path or len(path) == 0:
                    print(f"ERROR: Even random_walk_v2 failed - mask configuration too restrictive", file=sys.stderr)
                    return None
            else:
                print(f"       Try a different path mode or mask configuration", file=sys.stderr)
                return None
        
        # T032: Handle partial coverage if enabled
        if allow_partial_paths and path_result.coverage < 1.0:
            if path_result.coverage >= min_cover_ratio:
                # Accept partial path - T033: block remainder cells
                all_cells = set()
                for row in range(size):
                    for col in range(size):
                        if (row, col) not in config.blocked:
                            all_cells.add((row, col))
                
                path_cells = {(p.row, p.col) for p in path}
                remainder_cells = all_cells - path_cells
                
                # Block remainder
                for r, c in remainder_cells:
                    pos = Position(r, c)
                    grid.get_cell(pos).blocked = True
                
                import sys
                print(f"INFO: Accepted partial path with {path_result.coverage:.1%} coverage", file=sys.stderr)
                print(f"      Blocked {len(remainder_cells)} remainder cells", file=sys.stderr)
            else:
                # Coverage too low - reject
                import sys
                print(f"WARNING: Path coverage {path_result.coverage:.1%} below threshold {min_cover_ratio:.0%}", file=sys.stderr)
                print(f"         Falling back to serpentine mode", file=sys.stderr)
                # Rebuild with serpentine
                grid = Grid(size, size, allow_diagonal=allow_diagonal)
                for r, c in all_blocked:
                    pos = Position(r, c)
                    grid.get_cell(pos).blocked = True
                path_result = PathBuilder.build(grid, mode="serpentine", rng=rng, blocked=all_blocked)
                path = path_result.positions
        
        # T034: Create constraints based on actual path length
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
        
        # T048: Select anchors using adaptive policy
        # Determine if we should use adaptive or legacy anchor selection
        use_adaptive = config.adaptive_turn_anchors and config.anchor_policy_name != "legacy"
        
        if use_adaptive:
            # Use adaptive policy
            policy = get_policy(config.anchor_policy_name)
            anchor_list, anchor_metrics = select_anchors(
                path=path,
                difficulty=difficulty or "medium",
                policy=policy,
                symmetry=config.symmetry,
                rng=rng
            )
            
            # Extract positions for anchors (hard, repair, and endpoints)
            anchors = set()
            for anchor in anchor_list:
                if anchor.kind in [ANCHOR_KIND_HARD, ANCHOR_KIND_REPAIR, ANCHOR_KIND_ENDPOINT]:
                    anchors.add(anchor.position)
            
            # Store metrics for later inclusion in result
            _anchor_metrics = anchor_metrics
        else:
            # Legacy behavior: inline turn anchor detection
            anchors = {path[0], path[-1]}  # Always keep 1 and N
            
            # T09: For hard/extreme with pruning enabled, use endpoints only
            skip_turn_anchors = (
                config.pruning_enabled and
                difficulty in ["hard", "extreme"]
            )
            
            # Add turn points to anchors based on difficulty and turn_anchors flag
            if turn_anchors and not skip_turn_anchors:
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
            
            # Build legacy metrics
            from .anchor_policy import AnchorMetrics
            _anchor_metrics = AnchorMetrics(
                anchor_count=len(anchors),
                hard_count=len(anchors) - 2 if turn_anchors else 0,
                soft_count=0,
                repair_count=0,
                endpoint_count=2,
                positions=[(a.row, a.col) for a in anchors],
                policy_name="legacy",
                anchor_selection_reason="legacy"
            )
        
        # Determine target clue count
        total_cells = len(path)
        if percent_fill:
            target_clues = max(len(anchors), int(total_cells * percent_fill))
        elif difficulty:
            band = DIFFICULTY_BANDS.get(difficulty, DIFFICULTY_BANDS["medium"])
            target_clues = max(len(anchors), int(total_cells * band["clue_density_min"]))
        else:
            target_clues = len(anchors) + (total_cells // 4)  # Default
        
        # T16: Solver-driven pruning (if enabled)
        if config.pruning_enabled:
            from .pruning import prune_puzzle
            
            # Build initial puzzle with all path cells as givens
            prune_grid = Grid(size, size, allow_diagonal=allow_diagonal)
            for r, c in all_blocked:
                pos = Position(r, c)
                prune_grid.get_cell(pos).blocked = True
            for pos in path:
                prune_grid.get_cell(pos).value = grid.get_cell(pos).value
                prune_grid.get_cell(pos).given = True
            prune_puzzle_obj = Puzzle(prune_grid, constraints)
            
            # Run pruning
            prune_result = prune_puzzle(
                prune_puzzle_obj, path, config, 
                solver_mode="logic_v3",
                difficulty=difficulty
            )

            # Extract final givens from pruned puzzle
            current_givens = {
                pos for pos in path
                if prune_result.puzzle.grid.get_cell(pos).given
            }
            attempts_used = prune_result.session.iteration_count
            removals_accepted = len(path) - len(current_givens)
            
            # Store pruning metrics for result
            _pruning_metrics = prune_result.to_dict()
        else:
            # Legacy removal loop (T011)
            current_givens = set(given_positions)
            attempts_used = 0
            removals_accepted = 0
            _pruning_metrics = None
        
        # Minimum viable clue density (prevent 100% clue puzzles)
        MIN_VIABLE_DENSITY = 0.60  # At least 40% of cells must be empty for a valid puzzle
        min_viable_clues = int(total_cells * MIN_VIABLE_DENSITY)
        
        if not config.pruning_enabled:
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
                for r, c in all_blocked:
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
        for r, c in all_blocked:
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
                                          max_nodes=2000, max_time_ms=80000,timeout_ms=80000)
        
        # T017: Compute metrics from solve
        if final_solve_result.solved:
            solver_metrics = compute_metrics(final_puzzle, final_solve_result)
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
            # Keep solver metrics usable downstream.
        
        # Extract givens for metadata
        givens = [(pos.row, pos.col, grid.get_cell(pos).value) 
                 for pos in current_givens]
        sorted_givens = sorted(givens)
        
        end_time = time.time()

        mask_metrics_block = {
            "mask_enabled": config.mask_enabled,
            "mask_pattern_id": mask_pattern_id,
            "mask_cells_count": len(mask_cells),
            "mask_density": len(mask_cells) / (size * size) if size > 0 else 0.0,
            "mask_attempts": mask_attempts,
        }

        extended_solver_metrics = {
            **solver_metrics,
            "path_coverage": path_result.coverage,
            "path_reason": path_result.reason,
            "anchor_count": _anchor_metrics.anchor_count,
            "anchor_hard_count": _anchor_metrics.hard_count,
            "anchor_soft_count": _anchor_metrics.soft_count,
            "anchor_repair_count": _anchor_metrics.repair_count,
            "anchor_endpoint_count": _anchor_metrics.endpoint_count,
            "anchor_positions": _anchor_metrics.positions,
            "anchor_policy_name": _anchor_metrics.policy_name,
            "anchor_selection_reason": _anchor_metrics.anchor_selection_reason,
            "anchor_min_index_gap_enforced": _anchor_metrics.min_index_gap_enforced,
            "anchor_adjacency_mode": _anchor_metrics.adjacency_mode,
            "mask_enabled": mask_metrics_block["mask_enabled"],
            "mask_pattern_id": mask_metrics_block["mask_pattern_id"],
            "mask_cells_count": mask_metrics_block["mask_cells_count"],
            "mask_density": mask_metrics_block["mask_density"],
            "mask_attempts": mask_metrics_block["mask_attempts"],
            "structural_repair_used": False,
            "ambiguity_regions_detected": 0,
        }

        structural_metrics = build_structural_metrics(
            StructuralInputs(
                size=size,
                givens=sorted_givens,
                path=path,
                anchor_positions=_anchor_metrics.positions,
                solver_metrics=extended_solver_metrics,
            )
        )

        branching_metrics = (structural_metrics or {}).get("branching", {})
        search_ratio = branching_metrics.get("search_ratio")
        avg_branching = branching_metrics.get("average_branching_factor")
        clue_count = len(current_givens)
        difficulty_score_1, difficulty_score_2 = compute_difficulty_scores(
            clue_count,
            search_ratio,
            avg_branching,
        )
        primary_difficulty = classify_primary_difficulty(clue_count)
        intermediate_level = assign_intermediate_level(
            primary_difficulty,
            difficulty_score_1,
            DEFAULT_THRESHOLDS,
        )

        timings_ms = {
            "total": int((end_time - start_time) * 1000),
            "path_build": path_build_ms,
            "solve": 0,  # SolverResult doesn't track elapsed_ms currently
            "uniqueness": 0,  # TODO: track separately
        }

        # Create result (T023: Include mask cells in blocked_cells)
        return GeneratedPuzzle(
            size=size,
            allow_diagonal=allow_diagonal,
            blocked_cells=all_blocked,  # Include mask cells
            givens=sorted_givens,
            solution=sorted(solution),
            difficulty_label=primary_difficulty,
            difficulty_score=difficulty_score_1,
            clue_count=clue_count,
            uniqueness_verified=True,
            attempts_used=attempts_used,
            seed=actual_seed,
            path_mode=path_mode,
            clue_mode=clue_mode,
            symmetry=symmetry,
            timings_ms=timings_ms,
            solver_metrics=extended_solver_metrics,
            difficulty_score_1=difficulty_score_1,
            difficulty_score_2=difficulty_score_2,
            intermediate_level=intermediate_level,
            mask_metrics=mask_metrics_block,
            repair_metrics=None,
            structural_metrics=structural_metrics,
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
        
        # Generate solution path (now returns PathBuildResult)
        path_result = PathBuilder.build(grid, mode=path_mode, rng=rng, blocked=None)
        path = path_result.positions
        
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

