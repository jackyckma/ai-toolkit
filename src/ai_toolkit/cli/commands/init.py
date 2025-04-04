"""
Init command for the AI-Native Development Toolkit.

This module implements the 'init' command, which initializes
a new AI-Native Development Toolkit project.
"""

import os
import sys
from argparse import Namespace
from datetime import datetime
from pathlib import Path

# Import using absolute imports to avoid path issues
try:
    from ai_toolkit.kb.graph import KnowledgeGraph
except ImportError:
    # Fallback for development
    from src.ai_toolkit.kb.graph import KnowledgeGraph


def main(args: Namespace) -> int:
    """
    Execute the init command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Determine project directory
    if args.directory:
        project_dir = Path(args.directory)
    else:
        project_dir = Path.cwd()
    
    # Create .ai-toolkit directory if it doesn't exist
    toolkit_dir = project_dir / ".ai-toolkit"
    
    if toolkit_dir.exists():
        print(f"AI-Native Development Toolkit already initialized in {toolkit_dir}")
        return 1
    
    # Create directory structure
    (toolkit_dir / "kb").mkdir(parents=True, exist_ok=True)
    (toolkit_dir / "config").mkdir(parents=True, exist_ok=True)
    (toolkit_dir / "cache").mkdir(parents=True, exist_ok=True)
    
    # Determine project name
    if args.project_name:
        project_name = args.project_name
    else:
        project_name = project_dir.name
    
    # Initialize knowledge graph with project info
    graph = KnowledgeGraph(toolkit_dir)
    graph.project_info = {
        "name": project_name,
        "version": "0.1.0",
        "created_at": datetime.now().isoformat(),
        "updated_at": datetime.now().isoformat()
    }
    graph.save()
    
    print(f"AI-Native Development Toolkit initialized for project: {project_name}")
    print(f"Knowledge graph created in: {toolkit_dir}")
    
    return 0
