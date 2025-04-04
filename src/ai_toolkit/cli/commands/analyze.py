"""
Analyze command for the AI-Native Development Toolkit.

This module implements the 'analyze' command, which analyzes
code files and updates the knowledge graph.
"""

import sys
from argparse import Namespace
from pathlib import Path

# Import using absolute imports to avoid path issues
try:
    from ai_toolkit.kb.graph import KnowledgeGraph
    from ai_toolkit.parser.python import PythonParser
except ImportError:
    # Fallback for development
    from src.ai_toolkit.kb.graph import KnowledgeGraph
    from src.ai_toolkit.parser.python import PythonParser


def main(args: Namespace) -> int:
    """
    Execute the analyze command.
    
    Args:
        args: Command arguments
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    # Check if .ai-toolkit directory exists
    toolkit_dir = Path.cwd() / ".ai-toolkit"
    if not toolkit_dir.exists():
        print("Error: AI-Native Development Toolkit not initialized in this directory")
        print("Run 'ai-toolkit init' first")
        return 1
    
    # Get directory to analyze
    directory = Path(args.directory)
    if not directory.exists():
        print(f"Error: Directory {directory} does not exist")
        return 1
    
    # Initialize knowledge graph
    graph = KnowledgeGraph()
    
    # Select parser based on language
    if args.language == "python":
        parser = PythonParser(graph)
    else:
        print(f"Error: Unsupported language {args.language}")
        return 1
    
    print(f"Analyzing {args.language} code in {directory}...")
    
    try:
        # Parse directory
        parser.parse_directory(directory)
        
        # Save knowledge graph
        graph.save()
        
        # Print summary
        component_count = len(list(graph.get_all_components()))
        relationship_count = len(list(graph.get_all_relationships()))
        print(f"Analysis complete: Found {component_count} components and {relationship_count} relationships")
        
        return 0
    except Exception as e:
        print(f"Error analyzing code: {e}")
        return 1
