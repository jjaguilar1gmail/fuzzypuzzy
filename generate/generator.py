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
from .anchor_policy import get_policy, select_anchors, ANCHOR_KIND_HARD, ANCHOR_KIND_SOFT, ANCHOR_KIND_REPAIR, ANCHOR_KIND_ENDPOINT


def _get_density_floor(difficulty: str, size: int) -> float:
    """
    Get minimum clue density based on difficulty and size tier.
    
    Per research.md D8: Dynamic floors prevent over-constraint on small boards
    while maintaining solvability.
    
    Args:
        difficulty: easy|medium|hard
        size: Board dimension (e.g., 5 for 5x5)
        
    Returns:
        Minimum density ratio (0.0-1.0)
    """
    cells = size * size
    
    # Determine size tier
    if cells <= 25:
        size_tier = "small"
    elif cells <= 64:
        size_tier = "medium"
    else:
        size_tier = "large"
    
    # Density floors by (difficulty, size_tier)
    floors = {
        ("easy", "small"): 0.34,
        ("easy", "medium"): 0.30,
        ("easy", "large"): 0.26,
        ("medium", "small"): 0.30,
        ("medium", "medium"): 0.26,
        ("medium", "large"): 0.22,
        ("hard", "small"): 0.26,
        ("hard", "medium"): 0.22,
        ("hard", "large"): 0.18,
    }
    
    difficulty_lower = difficulty.lower() if difficulty else "medium"
    return floors.get((difficulty_lower, size_tier), 0.22)


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
                       structural_repair_enabled=False, structural_repair_max=2,
                       enable_anti_branch=False):
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
            enable_anti_branch: Enable anti-branch uniqueness probe (experimental)
            
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
            # T017: Apply density floor (US2)
            density_floor = _get_density_floor(difficulty, size)
            min_clues_floor = int(total_cells * density_floor)
            band_min_clues = int(total_cells * band["clue_density_min"])
            target_clues = max(len(anchors), band_min_clues, min_clues_floor)
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
                solver_mode="logic_v2",
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
                
                # Score removal candidates (T018: enable spacing for US2)
                enable_spacing = enable_anti_branch and path_mode in {"backbite_v1", "random_v2"}
                candidates = score_candidates(current_givens, path, anchors, grid, enable_spacing)
                
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
                
                # Check uniqueness with anti-branch probe if enabled (T014)
                if enable_anti_branch and path_mode in {"backbite_v1", "random_v2"}:
                    from solve.uniqueness_probe import run_anti_branch_probe, UniquenessProbeConfig
                    from util.logging_uniqueness import get_size_tier_policy
                    
                    # Get size-tier policy
                    tier_policy = get_size_tier_policy(total_cells)
                    
                    # Configure probe
                    probe_config = UniquenessProbeConfig(
                        seed=rng.rng.randint(0, 2**31 - 1),
                        size_tier=tier_policy.tier_name,
                        max_nodes=tier_policy.max_nodes,
                        timeout_ms=tier_policy.timeout_ms,
                        probe_count=tier_policy.probe_count,
                        extended_factor=tier_policy.extended_factor
                    )
                    
                    # Run probe (no logger passed here; will be wired in packgen layer)
                    probe_result = run_anti_branch_probe(test_puzzle, probe_config, logger=None)
                    
                    is_unique = (probe_result.final_decision == "ACCEPT")
                else:
                    # Fall back to traditional count_solutions (T015)
                    uniqueness_result = count_solutions(
                        test_puzzle,
                        cap=2,
                        node_cap=config.uniqueness_node_cap,
                        timeout_ms=config.uniqueness_timeout_ms
                    )
                    is_unique = uniqueness_result.is_unique
                
                if is_unique:
                    # Accept removal
                    current_givens = test_givens
                    removals_accepted += 1
                
                attempts_used += 1
        
        # T019: De-chunk pass (US2) - run after target density reached
        if enable_anti_branch and path_mode in {"backbite_v1", "random_v2"}:
            from .spacing import detect_clusters, spacing_score
            from solve.uniqueness_probe import run_anti_branch_probe, UniquenessProbeConfig
            from util.logging_uniqueness import get_size_tier_policy
            
            max_dechunk_passes = 3
            dechunk_removals = 0
            
            for pass_idx in range(max_dechunk_passes):
                # Compute current clusters
                clues = [(pos.row, pos.col) for pos in current_givens]
                clusters = detect_clusters(clues)
                
                if not clusters:
                    break
                
                # Find largest cluster
                largest_cluster = max(clusters, key=len)
                
                # Stop if largest cluster is small enough (≤3 clues)
                if len(largest_cluster) <= 3:
                    break
                
                # Calculate baseline spacing
                baseline_spacing = spacing_score(clues, size)
                
                # Try removing clues from largest cluster
                improved = False
                for clue_pos in largest_cluster:
                    pos_obj = Position(clue_pos[0], clue_pos[1])
                    
                    # Skip if anchor
                    if pos_obj in anchors:
                        continue
                    
                    # Test removal
                    test_givens = current_givens - {pos_obj}
                    test_clues = [(p.row, p.col) for p in test_givens]
                    test_spacing = spacing_score(test_clues, size)
                    
                    # Skip if doesn't improve spacing
                    if test_spacing <= baseline_spacing:
                        continue
                    
                    # Create test puzzle
                    test_grid = Grid(size, size, allow_diagonal=allow_diagonal)
                    for r, c in all_blocked:
                        test_grid.get_cell(Position(r, c)).blocked = True
                    for pos in path:
                        test_grid.get_cell(pos).value = grid.get_cell(pos).value
                    for pos in test_givens:
                        test_grid.get_cell(pos).given = True
                    for pos in path:
                        if pos not in test_givens:
                            test_grid.get_cell(pos).value = None
                    test_puzzle = Puzzle(test_grid, constraints)
                    
                    # Run uniqueness probe
                    tier_policy = get_size_tier_policy(total_cells)
                    probe_config = UniquenessProbeConfig(
                        seed=rng.rng.randint(0, 2**31 - 1),
                        size_tier=tier_policy.tier_name,
                        max_nodes=tier_policy.max_nodes,
                        timeout_ms=tier_policy.timeout_ms,
                        probe_count=tier_policy.probe_count,
                        extended_factor=tier_policy.extended_factor
                    )
                    probe_result = run_anti_branch_probe(test_puzzle, probe_config, logger=None)
                    
                    # Accept if unique
                    if probe_result.final_decision == "ACCEPT":
                        current_givens = test_givens
                        dechunk_removals += 1
                        improved = True
                        break  # Try next pass with updated cluster
                
                # Stop if no improvement in this pass
                if not improved:
                    break
        
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
        
        # T020-T021: Prepare telemetry summary (US3)
        generation_summary = {
            "puzzle_id": f"{size}x{size}_{difficulty}_{actual_seed}",
            "size": size,
            "difficulty": difficulty,
            "path_mode": path_mode,
            "total_cells": total_cells,
            "final_clue_count": len(current_givens),
            "final_density": len(current_givens) / total_cells,
            "removals_accepted": removals_accepted,
            "attempts_used": attempts_used,
            "generation_time_ms": int((end_time - start_time) * 1000),
            "path_build_ms": path_build_ms,
            "anti_branch_enabled": enable_anti_branch,
            "assessed_difficulty": assessed_label,
            "assessed_score": assessed_score,
        }
        
        # Add de-chunk stats if applicable
        if enable_anti_branch and path_mode in {"backbite_v1", "random_v2"}:
            generation_summary["dechunk_removals"] = dechunk_removals if 'dechunk_removals' in locals() else 0
            
            # Calculate final spacing metrics
            from .spacing import spacing_score, detect_clusters
            final_clues = [(pos.row, pos.col) for pos in current_givens]
            final_spacing = spacing_score(final_clues, size)
            final_clusters = detect_clusters(final_clues)
            largest_cluster_size = max((len(c) for c in final_clusters), default=0)
            
            generation_summary["spacing_score"] = final_spacing
            generation_summary["largest_cluster_size"] = largest_cluster_size
            generation_summary["cluster_count"] = len(final_clusters)
        
        # T021: Optionally emit summary (placeholder - no logger instance yet)
        # When logger is wired: logger.log_summary(generation_summary)
        
        # Create result (T023: Include mask cells in blocked_cells)
        return GeneratedPuzzle(
            size=size,
            allow_diagonal=allow_diagonal,
            blocked_cells=all_blocked,  # Include mask cells
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
                "path_build": path_build_ms,
                "solve": 0,  # SolverResult doesn't track elapsed_ms currently
                "uniqueness": 0,  # TODO: track separately
            },
            solver_metrics={
                **solver_metrics,  # T019: Include computed metrics
                "path_coverage": path_result.coverage,
                "path_reason": path_result.reason,
                # T054: Include anchor metrics
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
                # T005/T010: Mask & repair metrics (populated from mask generation)
                "mask_enabled": config.mask_enabled,
                "mask_pattern_id": mask_pattern_id,
                "mask_cells_count": len(mask_cells),
                "mask_density": len(mask_cells) / (size * size) if size > 0 else 0.0,
                "mask_attempts": mask_attempts,
                "structural_repair_used": False,
                "ambiguity_regions_detected": 0,
            },
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

