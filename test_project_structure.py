#!/usr/bin/env python3
"""
Verify the AI-Native Development Toolkit project structure.

This script checks that all required files and directories exist.
"""

import os
import sys
from pathlib import Path


def check_file(file_path: Path) -> bool:
    """Check if a file exists and report result."""
    exists = file_path.exists()
    status = "✅" if exists else "❌"
    print(f"{status} {file_path}")
    return exists


def main() -> int:
    """Check project structure and return exit code."""
    project_root = Path(__file__).parent
    
    print("\nChecking AI-Native Development Toolkit project structure...\n")
    
    # Define required files
    required_files = [
        # CLI
        "src/ai_toolkit/cli/main.py",
        "src/ai_toolkit/cli/commands/init.py",
        "src/ai_toolkit/cli/commands/analyze.py",
        "src/ai_toolkit/cli/commands/query.py",
        "src/ai_toolkit/cli/commands/visualize.py",
        
        # Knowledge Graph
        "src/ai_toolkit/kb/graph.py",
        "src/ai_toolkit/kb/component.py",
        "src/ai_toolkit/kb/relationship.py",
        "src/ai_toolkit/kb/storage.py",
        
        # Parser
        "src/ai_toolkit/parser/python.py",
        "src/ai_toolkit/parser/extractor.py",
        "src/ai_toolkit/parser/dependency.py",
        
        # Visualization
        "src/ai_toolkit/viz/mermaid.py",
        "src/ai_toolkit/viz/formats.py",
        
        # Entry point
        "src/bin/ai-toolkit",
        
        # Other
        "scripts/install.sh",
        "pyproject.toml",
        "README.md"
    ]
    
    # Check all required files
    missing_count = 0
    for rel_path in required_files:
        if not check_file(project_root / rel_path):
            missing_count += 1
    
    # Report results
    print("\nSummary:")
    if missing_count == 0:
        print("✅ All required files are present")
        return 0
    else:
        print(f"❌ Missing {missing_count} required files")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 