"""Generate module: Difficulty

Contains difficulty assessment and band mapping for generated puzzles.
"""

# Difficulty band profiles (T008)
DIFFICULTY_BANDS = {
    "easy": {
        "clue_density_min": 0.50,  # Increased for easier puzzles
        "clue_density_max": 1.0,
        "max_search_depth": 0,
        "expected_max_nodes": 0,
        "logic_ratio_min": 1.0,  # Pure logic
    },
    "medium": {
        "clue_density_min": 0.35,  # Adjusted
        "clue_density_max": 0.50,
        "max_search_depth": 10,
        "expected_max_nodes": 50,
        "logic_ratio_min": 0.7,
    },
    "hard": {
        "clue_density_min": 0.25,  # Adjusted
        "clue_density_max": 0.35,
        "max_search_depth": 20,
        "expected_max_nodes": 200,
        "logic_ratio_min": 0.4,
    },
    "extreme": {
        "clue_density_min": 0.15,  # Adjusted
        "clue_density_max": 0.25,
        "max_search_depth": 200,
        "expected_max_nodes": 500,
        "logic_ratio_min": 0.0,
    },
}


def compute_metrics(puzzle, solver_result):
    """Compute difficulty metrics from solver trace (T017).
    
    Args:
        puzzle: The puzzle
        solver_result: Result from Solver.solve()
        
    Returns:
        dict with clue_density, logic_ratio, nodes, depth, strategy_hits
    """
    total_cells = 0
    given_count = 0
    
    for cell in puzzle.grid.iter_cells():
        if not cell.blocked:
            total_cells += 1
            if cell.given:
                given_count += 1
    
    clue_density = given_count / total_cells if total_cells > 0 else 0.0
    
    # Logic ratio: steps that didn't require search
    # For v3 mode, steps before first search node are logic-only
    logic_steps = 0
    total_steps = len(solver_result.steps)
    
    for step in solver_result.steps:
        step_str = str(step).lower()
        if 'backtrack' not in step_str and 'search' not in step_str:
            logic_steps += 1
    
    logic_ratio = logic_steps / total_steps if total_steps > 0 else 1.0
    
    # Strategy hits - count occurrences of strategy names in steps
    strategy_hits = {
        'corridor': 0,
        'degree': 0,
        'neighbor': 0,
        'forced': 0,
    }
    
    for step in solver_result.steps:
        step_str = str(step).lower()
        if 'corridor' in step_str:
            strategy_hits['corridor'] += 1
        if 'degree' in step_str:
            strategy_hits['degree'] += 1
        if 'neighbor' in step_str:
            strategy_hits['neighbor'] += 1
        if 'forced' in step_str or 'only' in step_str:
            strategy_hits['forced'] += 1
    
    return {
        'clue_density': clue_density,
        'logic_ratio': logic_ratio,
        'nodes': solver_result.nodes,
        'depth': solver_result.depth,
        'steps': total_steps,
        'strategy_hits': strategy_hits,
    }


def assess_difficulty(metrics):
    """Map metrics to difficulty band label and score (T018).
    
    Args:
        metrics: dict from compute_metrics
        
    Returns:
        (difficulty_label: str, difficulty_score: float)
    """
    clue_density = metrics['clue_density']
    depth = metrics['depth']
    logic_ratio = metrics['logic_ratio']
    
    # Match to bands based on clue density primarily
    best_match = "medium"
    best_score = 0.5
    
    for band_name, band_def in DIFFICULTY_BANDS.items():
        # Check if metrics fall within band
        density_match = (band_def['clue_density_min'] <= clue_density <= band_def['clue_density_max'])
        depth_match = (depth <= band_def['max_search_depth'])
        logic_match = (logic_ratio >= band_def.get('logic_ratio_min', 0.0))
        
        # Score based on how well it matches
        if density_match:
            # Within density range
            match_quality = 1.0
            if depth_match and logic_match:
                match_quality = 1.0
            elif depth_match or logic_match:
                match_quality = 0.8
            else:
                match_quality = 0.6
            
            # Calculate normalized score within band
            density_range = band_def['clue_density_max'] - band_def['clue_density_min']
            if density_range > 0:
                normalized = (clue_density - band_def['clue_density_min']) / density_range
            else:
                normalized = 0.5
            
            # Assign band
            best_match = band_name
            best_score = match_quality * normalized
            break
    
    # Map band to numeric score (0.0 = easiest, 1.0 = hardest)
    band_order = {"easy": 0.0, "medium": 0.33, "hard": 0.66, "extreme": 1.0}
    base_score = band_order.get(best_match, 0.5)
    
    return (best_match, base_score)
