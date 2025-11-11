#!/usr/bin/env python3
"""Pack Generator CLI

Generate Hidato puzzle packs with validated unique puzzles.
Outputs JSON files to frontend/public/packs/ directory structure.

Usage:
    python -m app.packgen.cli --outdir frontend/public/packs/daily-2025 \\
        --sizes 5,7 --difficulties easy,medium --count 20 --seed 12345
"""

import sys
import argparse
from pathlib import Path
from typing import List
import time

from .generate_pack import generate_pack
from .export import export_pack_metadata
from .report import GenerationReport, write_report


VALID_SIZES = list(range(5, 11))  # 5-10
VALID_DIFFICULTIES = ['easy', 'medium', 'hard', 'extreme']


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(
        description='Generate Hidato puzzle packs for web game',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate 10 easy 5x5 puzzles
  python -m app.packgen.cli --outdir frontend/public/packs/sample \\
      --sizes 5 --difficulties easy --count 10

  # Generate mixed pack with specific seed
  python -m app.packgen.cli --outdir frontend/public/packs/daily-2025 \\
      --sizes 5,7 --difficulties easy,medium,hard --count 30 --seed 42

  # High retry limit for difficult puzzles
  python -m app.packgen.cli --outdir frontend/public/packs/expert \\
      --sizes 8,9,10 --difficulties extreme --count 10 --retries 20
'''
    )
    
    parser.add_argument(
        '--outdir',
        type=str,
        required=True,
        help='Output directory for pack files (e.g., frontend/public/packs/my-pack)'
    )
    
    parser.add_argument(
        '--sizes',
        type=str,
        required=True,
        help=f'Comma-separated grid sizes (valid: {",".join(map(str, VALID_SIZES))})'
    )
    
    parser.add_argument(
        '--difficulties',
        type=str,
        required=True,
        help=f'Comma-separated difficulty levels (valid: {",".join(VALID_DIFFICULTIES)})'
    )
    
    parser.add_argument(
        '--count',
        type=int,
        required=True,
        help='Number of puzzles to generate'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=None,
        help='Random seed for reproducibility (optional)'
    )
    
    parser.add_argument(
        '--retries',
        type=int,
        default=5,
        help='Max retry attempts per puzzle (default: 5)'
    )
    
    parser.add_argument(
        '--title',
        type=str,
        default=None,
        help='Pack title (default: auto-generated from params)'
    )
    
    parser.add_argument(
        '--description',
        type=str,
        default=None,
        help='Pack description (optional)'
    )
    
    parser.add_argument(
        '--path-mode',
        type=str,
        default='backbite_v1',
        help='Path generation mode (default: backbite_v1)'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Validate arguments without generating puzzles'
    )
    
    parser.add_argument(
        '--include-solution',
        action='store_true',
        help='Include full solution in puzzle JSON (default: false)'
    )
    
    return parser.parse_args()


def validate_args(args):
    """Validate parsed arguments."""
    errors = []
    
    # Parse and validate sizes
    try:
        sizes = [int(s.strip()) for s in args.sizes.split(',')]
        for size in sizes:
            if size not in VALID_SIZES:
                errors.append(f"Invalid size {size}. Must be in {VALID_SIZES}")
        args.sizes = sizes
    except ValueError:
        errors.append(f"Invalid sizes format: {args.sizes}")
    
    # Parse and validate difficulties
    difficulties = [d.strip().lower() for d in args.difficulties.split(',')]
    for diff in difficulties:
        if diff not in VALID_DIFFICULTIES:
            errors.append(f"Invalid difficulty '{diff}'. Must be one of {VALID_DIFFICULTIES}")
    args.difficulties = difficulties
    
    # Validate count
    if args.count < 1:
        errors.append("Count must be at least 1")
    
    # Validate retries
    if args.retries < 1:
        errors.append("Retries must be at least 1")
    
    # Validate output directory
    outdir = Path(args.outdir)
    if outdir.exists() and any(outdir.iterdir()):
        errors.append(f"Output directory {outdir} already exists and is not empty")
    
    if errors:
        print("❌ Validation errors:", file=sys.stderr)
        for error in errors:
            print(f"  - {error}", file=sys.stderr)
        sys.exit(1)


def main():
    """Main CLI entry point."""
    args = parse_args()
    validate_args(args)
    
    if args.dry_run:
        print("✅ Dry run: Arguments are valid")
        print(f"   Output: {args.outdir}")
        print(f"   Sizes: {args.sizes}")
        print(f"   Difficulties: {args.difficulties}")
        print(f"   Count: {args.count}")
        print(f"   Seed: {args.seed}")
        print(f"   Retries: {args.retries}")
        print(f"   Path mode: {args.path_mode}")
        return 0
    
    print("="*70)
    print("🧩 Hidato Pack Generator")
    print("="*70)
    print(f"Output: {args.outdir}")
    print(f"Sizes: {', '.join(map(str, args.sizes))}")
    print(f"Difficulties: {', '.join(args.difficulties)}")
    print(f"Count: {args.count}")
    print(f"Seed: {args.seed or 'random'}")
    print(f"Max retries: {args.retries}")
    print(f"Path mode: {args.path_mode}")
    print()
    
    start_time = time.time()
    
    # Generate pack
    try:
        pack_id, report = generate_pack(
            outdir=Path(args.outdir),
            sizes=args.sizes,
            difficulties=args.difficulties,
            count=args.count,
            seed=args.seed,
            max_retries=args.retries,
            title=args.title,
            description=args.description,
            include_solution=args.include_solution,
            path_mode=args.path_mode,
        )
    except Exception as e:
        print(f"❌ Generation failed: {e}", file=sys.stderr)
        return 1
    
    total_time = time.time() - start_time
    report.total_time_sec = total_time
    
    # Write report
    report_file = Path(args.outdir) / "generation_report.json"
    write_report(report, report_file, format='json')
    
    # Write text summary to stdout
    print()
    print("="*70)
    print("📊 Generation Summary")
    print("="*70)
    print(f"Pack ID: {pack_id}")
    print(f"Requested: {report.total_requested}")
    print(f"Generated: {report.total_generated}")
    print(f"Skipped: {report.total_skipped}")
    print(f"Failed: {report.total_failed}")
    print(f"Success rate: {report.total_generated / report.total_requested * 100:.1f}%")
    print(f"Avg time: {report.average_generation_time_ms:.1f}ms")
    print(f"Total time: {total_time:.2f}s")
    print()
    print(f"✅ Pack generated at: {args.outdir}")
    print(f"📄 Report saved to: {report_file}")
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
