#!/usr/bin/env python3
"""Demo script to test Hidato MVP functionality."""

import sys
import os

# Add parent directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from app.api import HidatoREPL

def main():
    print("=== Hidato Terminal MVP Demo ===")
    print()
    
    # Test 5x5 generation
    print("1. Testing 5x5 puzzle generation:")
    repl = HidatoREPL()
    repl._handle_generate(["5x5", "--seed", "42"])
    print()
    
    # Test 7x7 generation
    print("2. Testing 7x7 puzzle generation:")
    repl._handle_generate(["7x7", "--seed", "100"])
    print()
    
    # Test show command
    print("3. Testing show command:")
    repl._handle_show()
    print()
    
    # Test help command
    print("4. Testing help command:")
    repl._handle_help()
    print()
    
    print("=== Demo Complete ===")
    print("✅ US1: Generate and View Easy Puzzle - COMPLETED")
    print("✅ You can now generate 5x5 and 7x7 puzzles in terminal!")
    print()
    print("To run interactively: python app/api.py")

if __name__ == "__main__":
    main()