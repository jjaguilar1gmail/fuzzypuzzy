"""Pack generation wrapper using existing Hidato engine."""

import time
import json
from pathlib import Path
from typing import List, Dict, Tuple
from datetime import datetime
import random

from generate.generator import Generator
from generate.models import GeneratedPuzzle
from .export import export_puzzle, export_pack_metadata
from .report import GenerationReport


def _update_packs_index(
    index_file: Path,
    pack_id: str,
    title: str,
    description: str | None,
    puzzle_count: int,
    difficulty_counts: Dict[str, int],
    size_distribution: Dict[str, int],
):
    """Update or create the packs index.json file.
    
    Args:
        index_file: Path to index.json
        pack_id: Pack identifier
        title: Pack title
        description: Pack description
        puzzle_count: Number of puzzles in pack
        difficulty_counts: Difficulty distribution
        size_distribution: Size distribution
    """
    # Load existing index or create new one
    if index_file.exists():
        with open(index_file, 'r') as f:
            packs = json.load(f)
    else:
        packs = []
    
    # Remove existing entry if present
    packs = [p for p in packs if p['id'] != pack_id]
    
    # Create new entry
    pack_summary = {
        'id': pack_id,
        'title': title,
        'puzzle_count': puzzle_count,
        'difficulty_counts': difficulty_counts,
        'created_at': datetime.utcnow().isoformat() + 'Z',
    }
    
    if description:
        pack_summary['description'] = description
    
    # Add to index
    packs.append(pack_summary)
    
    # Sort by ID for consistency
    packs.sort(key=lambda p: p['id'])
    
    # Write back
    index_file.parent.mkdir(parents=True, exist_ok=True)
    with open(index_file, 'w') as f:
        json.dump(packs, f, indent=2)


def generate_pack(
    outdir: Path,
    sizes: List[int],
    difficulties: List[str],
    count: int,
    seed: int | None = None,
    max_retries: int = 5,
    title: str | None = None,
    description: str | None = None,
    include_solution: bool = False,
    path_mode: str = "backbite_v1",
) -> Tuple[str, GenerationReport]:
    """Generate a puzzle pack using the existing engine.
    
    Args:
        outdir: Output directory for pack files
        sizes: List of grid sizes to generate
        difficulties: List of difficulty levels
        count: Number of puzzles to generate
        seed: Random seed for reproducibility
        max_retries: Max retry attempts per puzzle
        title: Pack title (auto-generated if None)
        description: Pack description
        include_solution: Include full solution in exports
        path_mode: Path generation mode (default: "backbite_v1")
        
    Returns:
        Tuple of (pack_id, GenerationReport)
    """
    # Create output directory structure
    outdir.mkdir(parents=True, exist_ok=True)
    puzzles_dir = outdir / "puzzles"
    puzzles_dir.mkdir(exist_ok=True)
    
    # Generate pack ID from output directory name
    pack_id = outdir.name
    
    # Auto-generate title if not provided
    if title is None:
        title = f"Hidato Pack {pack_id}"
    
    # Initialize RNG
    if seed is None:
        seed = random.randint(0, 2**31 - 1)
    
    rng = random.Random(seed)
    
    # Distribute puzzles across sizes and difficulties
    puzzle_specs = []
    for i in range(count):
        size = rng.choice(sizes)
        difficulty = rng.choice(difficulties)
        puzzle_seed = rng.randint(0, 2**31 - 1)
        puzzle_specs.append((size, difficulty, puzzle_seed))
    
    # Track generation statistics
    generated_puzzles: List[Tuple[str, GeneratedPuzzle, int, str]] = []
    failed_count = 0
    skipped_count = 0
    difficulty_stats: Dict[str, Dict[str, int]] = {
        diff: {'generated': 0, 'failed': 0} for diff in difficulties
    }
    size_counts: Dict[str, int] = {str(size): 0 for size in sizes}
    total_generation_time_ms = 0.0
    
    print(f"Generating {count} puzzles...")
    print()
    
    for i, (size, difficulty, puzzle_seed) in enumerate(puzzle_specs, 1):
        puzzle_id = f"{i:04d}"
        print(f"[{i}/{count}] Generating {size}×{size} {difficulty} (seed={puzzle_seed})...", end=" ")
        
        success = False
        attempt = 0
        result = None
        
        while attempt < max_retries and not success:
            attempt += 1
            try:
                start = time.time()
                result = Generator.generate_puzzle(
                    size=size,
                    difficulty=difficulty,
                    seed=puzzle_seed + attempt - 1,  # Vary seed on retry
                    path_mode=path_mode,
                    timeout_ms=10000,
                    max_attempts=5,
                )
                elapsed_ms = (time.time() - start) * 1000
                
                # Generator.generate_puzzle returns GeneratedPuzzle or None
                if result is not None and result.uniqueness_verified:
                    success = True
                    generated_puzzles.append((puzzle_id, result, size, difficulty))
                    difficulty_stats[difficulty]['generated'] += 1
                    size_counts[str(size)] += 1
                    total_generation_time_ms += elapsed_ms
                    print(f"✅ {elapsed_ms:.0f}ms")
                else:
                    if attempt >= max_retries:
                        print(f"❌ Failed after {max_retries} attempts")
                        difficulty_stats[difficulty]['failed'] += 1
                        failed_count += 1
            except Exception as e:
                if attempt >= max_retries:
                    print(f"❌ Error: {e}")
                    difficulty_stats[difficulty]['failed'] += 1
                    failed_count += 1
    
    # Export puzzles
    print()
    print("Exporting puzzles...")
    for puzzle_id, result, size, difficulty in generated_puzzles:
        puzzle_file = puzzles_dir / f"{puzzle_id}.json"
        export_puzzle(
            result,
            puzzle_file,
            puzzle_id=puzzle_id,
            pack_id=pack_id,
            include_solution=include_solution,
        )
    
    # Calculate difficulty and size distributions
    difficulty_counts = {
        diff: stats['generated'] 
        for diff, stats in difficulty_stats.items() 
        if stats['generated'] > 0
    }
    
    size_distribution = {
        size: count 
        for size, count in size_counts.items() 
        if count > 0
    }
    
    # Export pack metadata
    puzzle_ids = [puzzle_id for puzzle_id, _, _, _ in generated_puzzles]
    metadata_file = outdir / "metadata.json"
    export_pack_metadata(
        metadata_file,
        pack_id=pack_id,
        title=title,
        description=description,
        puzzle_ids=puzzle_ids,
        difficulty_counts=difficulty_counts,
        size_distribution=size_distribution,
    )
    
    # Update packs index.json
    _update_packs_index(
        outdir.parent / "index.json",
        pack_id=pack_id,
        title=title,
        description=description,
        puzzle_count=len(generated_puzzles),
        difficulty_counts=difficulty_counts,
        size_distribution=size_distribution,
    )
    
    # Build report
    avg_time_ms = total_generation_time_ms / len(generated_puzzles) if generated_puzzles else 0
    
    report = GenerationReport(
        pack_id=pack_id,
        total_requested=count,
        total_generated=len(generated_puzzles),
        total_skipped=skipped_count,
        total_failed=failed_count,
        difficulty_breakdown=difficulty_stats,
        size_breakdown=size_counts,
        average_generation_time_ms=avg_time_ms,
        total_time_sec=0,  # Will be set by CLI
    )
    
    return pack_id, report
