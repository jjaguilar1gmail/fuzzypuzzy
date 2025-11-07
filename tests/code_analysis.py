#!/usr/bin/env python3
"""Code cleanup and optimization analysis for the advanced solver system."""

import ast
import os
from typing import Dict, List, Set, Tuple
from pathlib import Path

class CodeAnalyzer:
    """Analyze code quality and suggest optimizations."""
    
    def __init__(self, root_path: str):
        self.root_path = Path(root_path)
        self.solver_files = [
            "solve/solver.py",
            "solve/candidates.py", 
            "solve/regions.py",
            "solve/corridors.py",
            "solve/degree.py"
        ]
        self.issues = []
        self.suggestions = []
    
    def analyze_all(self) -> None:
        """Run complete code analysis."""
        print("🔍 ADVANCED SOLVER CODE ANALYSIS")
        print("=" * 50)
        
        for file_path in self.solver_files:
            full_path = self.root_path / file_path
            if full_path.exists():
                print(f"\nAnalyzing {file_path}...")
                self._analyze_file(full_path, file_path)
            else:
                print(f"⚠️  {file_path} not found")
        
        self._print_summary()
    
    def _analyze_file(self, file_path: Path, relative_path: str) -> None:
        """Analyze a single Python file."""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            tree = ast.parse(content)
            
            # Run various analyses
            self._check_docstrings(tree, relative_path)
            self._check_method_complexity(tree, relative_path)
            self._check_imports(tree, relative_path)
            self._check_error_handling(tree, relative_path)
            self._check_performance_patterns(content, relative_path)
            
        except Exception as e:
            self.issues.append(f"❌ {relative_path}: Failed to parse - {e}")
    
    def _check_docstrings(self, tree: ast.AST, file_path: str) -> None:
        """Check for proper docstring coverage."""
        missing_docstrings = []
        
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.ClassDef)):
                if not ast.get_docstring(node):
                    missing_docstrings.append(f"{node.name} (line {node.lineno})")
        
        if missing_docstrings:
            self.issues.append(f"📝 {file_path}: Missing docstrings: {', '.join(missing_docstrings[:3])}{'...' if len(missing_docstrings) > 3 else ''}")
    
    def _check_method_complexity(self, tree: ast.AST, file_path: str) -> None:
        """Check for overly complex methods."""
        complex_methods = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Count nested structures as complexity indicator
                complexity = 0
                for child in ast.walk(node):
                    if isinstance(child, (ast.If, ast.For, ast.While, ast.Try)):
                        complexity += 1
                
                if complexity > 8:  # Threshold for high complexity
                    complex_methods.append(f"{node.name} (complexity: {complexity})")
        
        if complex_methods:
            self.issues.append(f"🔀 {file_path}: High complexity methods: {', '.join(complex_methods)}")
    
    def _check_imports(self, tree: ast.AST, file_path: str) -> None:
        """Check import organization and usage."""
        imports = []
        used_names = set()
        
        # Collect imports
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    for alias in node.names:
                        imports.append(f"{node.module}.{alias.name}")
        
        # Collect used names (simplified check)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                used_names.add(node.id)
        
        # Basic unused import detection (simplified)
        potentially_unused = []
        for imp in imports[:5]:  # Check first few imports
            base_name = imp.split('.')[-1]
            if base_name not in used_names and base_name.lower() != 'typing':
                potentially_unused.append(base_name)
        
        if potentially_unused:
            self.suggestions.append(f"📦 {file_path}: Check if imports are used: {', '.join(potentially_unused)}")
    
    def _check_error_handling(self, tree: ast.AST, file_path: str) -> None:
        """Check for proper error handling patterns."""
        bare_excepts = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.ExceptHandler):
                if node.type is None:  # bare except:
                    bare_excepts.append(f"line {node.lineno}")
        
        if bare_excepts:
            self.issues.append(f"⚠️  {file_path}: Bare except clauses at: {', '.join(bare_excepts)}")
    
    def _check_performance_patterns(self, content: str, file_path: str) -> None:
        """Check for common performance anti-patterns."""
        lines = content.split('\n')
        perf_issues = []
        
        for i, line in enumerate(lines, 1):
            # Check for inefficient patterns
            if 'for' in line and 'range(len(' in line:
                perf_issues.append(f"line {i}: Consider enumerate() instead of range(len())")
            
            if line.strip().startswith('print(') and 'debug' not in line.lower():
                # Potential debug print left in
                perf_issues.append(f"line {i}: Debug print statement?")
        
        if perf_issues:
            for issue in perf_issues[:3]:  # Limit output
                self.suggestions.append(f"⚡ {file_path}: {issue}")
    
    def _print_summary(self) -> None:
        """Print analysis summary with recommendations."""
        print("\n" + "="*50)
        print("📋 CODE ANALYSIS SUMMARY")
        print("="*50)
        
        if not self.issues and not self.suggestions:
            print("✅ No significant issues found!")
            print("🎉 Code quality looks good!")
            return
        
        if self.issues:
            print("\n🔧 ISSUES TO ADDRESS:")
            for issue in self.issues:
                print(f"  {issue}")
        
        if self.suggestions:
            print("\n💡 OPTIMIZATION SUGGESTIONS:")
            for suggestion in self.suggestions:
                print(f"  {suggestion}")
        
        print("\n🎯 RECOMMENDED ACTIONS:")
        
        # Priority recommendations
        priority_actions = []
        
        if any("Missing docstrings" in issue for issue in self.issues):
            priority_actions.append("Add docstrings to public methods and classes")
        
        if any("complexity" in issue for issue in self.issues):
            priority_actions.append("Refactor complex methods (extract helper functions)")
        
        if any("except" in issue for issue in self.issues):
            priority_actions.append("Replace bare except clauses with specific exceptions")
        
        if not priority_actions:
            priority_actions = [
                "Consider adding type hints for better code documentation",
                "Add unit tests for edge cases if not already covered",
                "Consider performance profiling for optimization opportunities"
            ]
        
        for i, action in enumerate(priority_actions, 1):
            print(f"  {i}. {action}")

class OptimizationSuggestions:
    """Specific optimization recommendations for the solver system."""
    
    @staticmethod
    def print_recommendations() -> None:
        """Print detailed optimization recommendations."""
        print("\n🚀 PERFORMANCE OPTIMIZATION GUIDE")
        print("="*50)
        
        recommendations = [
            {
                "area": "Candidate Management",
                "current": "Full grid scans in candidates.py",
                "optimization": "Cache single-candidate positions for O(1) access",
                "impact": "Medium",
                "implementation": "Add _single_candidates_cache set, update on assign/unassign"
            },
            {
                "area": "Region Analysis", 
                "current": "Flood fill on every call in regions.py",
                "optimization": "Cache region boundaries, invalidate on grid changes",
                "impact": "High",
                "implementation": "Add region cache with dirty flags per grid cell"
            },
            {
                "area": "Corridor Mapping",
                "current": "BFS pathfinding in corridors.py",
                "optimization": "Pre-compute distance matrices for small grids",
                "impact": "Medium",
                "implementation": "Floyd-Warshall for grids < 6x6, BFS for larger"
            },
            {
                "area": "Search Heuristics",
                "current": "MRV calculation loops through all candidates",
                "optimization": "Priority queue with candidate counts",
                "impact": "Medium", 
                "implementation": "Use heapq for O(log n) MRV position selection"
            },
            {
                "area": "Validation",
                "current": "Full path validation on every check",
                "optimization": "Incremental validation during construction",
                "impact": "High",
                "implementation": "Track path segments, validate only changes"
            }
        ]
        
        for i, rec in enumerate(recommendations, 1):
            print(f"\n{i}. {rec['area']} ({rec['impact']} Impact)")
            print(f"   Current: {rec['current']}")
            print(f"   ➡️  Optimization: {rec['optimization']}")
            print(f"   💻 Implementation: {rec['implementation']}")
        
        print("\n🎯 IMPLEMENTATION PRIORITY:")
        print("1. Region Analysis caching (highest impact)")
        print("2. Incremental validation (reduces redundant work)")
        print("3. Candidate management optimization")
        print("4. Search heuristic improvements")
        print("5. Corridor pre-computation (for small grids)")


def main():
    """Run code analysis and optimization recommendations."""
    # Determine root path
    current_dir = Path.cwd()
    
    # Try to find the project root
    root_candidates = [
        current_dir,
        current_dir.parent,
        current_dir / "fuzzypuzzy"
    ]
    
    root_path = None
    for candidate in root_candidates:
        if (candidate / "solve").exists():
            root_path = candidate
            break
    
    if not root_path:
        print("❌ Could not find solver files. Run from project root.")
        return
    
    print(f"📁 Analyzing code in: {root_path}")
    
    # Run code analysis
    analyzer = CodeAnalyzer(str(root_path))
    analyzer.analyze_all()
    
    # Print optimization recommendations
    OptimizationSuggestions.print_recommendations()
    
    print("\n🏁 CODE ANALYSIS COMPLETE")
    print("Review recommendations above for next steps")


if __name__ == "__main__":
    main()