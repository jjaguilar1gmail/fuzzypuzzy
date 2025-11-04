#!/usr/bin/env python3
"""Hidato Terminal MVP - Main Entry Point

A command-line interface for the Hidato puzzle game.
"""

import sys
import os
import argparse

# Add current directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.api import API, HidatoREPL

def main():
    """Main entry point with optional command-line arguments."""
    parser = argparse.ArgumentParser(
        description="Hidato Terminal MVP - Interactive puzzle game",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python hidato.py                    # Start interactive REPL
  python hidato.py --demo            # Run feature demonstration
  python hidato.py --version         # Show version info

Interactive Commands:
  generate 5x5 --seed 42             # Create reproducible puzzle
  move 2 3 15                        # Place number at position
  hint                               # Get solving hint
  solve                              # Auto-solve puzzle
  export puzzle.json                 # Save to file
  import puzzle.json                 # Load from file
  help                               # Show all commands
        """
    )
    
    parser.add_argument(
        '--demo', 
        action='store_true',
        help='Run a demonstration of all features'
    )
    
    parser.add_argument(
        '--version', 
        action='store_true',
        help='Show version information'
    )
    
    args = parser.parse_args()
    
    if args.version:
        print("Hidato Terminal MVP v1.0")
        print("Feature: 001-hidato-terminal-mvp")
        print("Python 3.11+ compatible")
        return
    
    if args.demo:
        print("🎯 Starting Hidato Terminal MVP Demo...")
        print("(Running complete_demo.py)")
        print()
        import complete_demo
        complete_demo.main()
        return
    
    # Default: start interactive REPL
    print("🎯 Welcome to Hidato Terminal MVP!")
    print("Type 'help' for commands or 'quit' to exit.")
    print()
    
    try:
        API.start_repl()
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing Hidato!")
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()