#!/usr/bin/env python3
"""
AI-Native Development Toolkit CLI
Main entry point for the command-line interface.
"""

import argparse
import sys
from importlib import import_module
from pathlib import Path

# Define the version
__version__ = "0.1.0"

def create_parser():
    """Create the main argument parser"""
    parser = argparse.ArgumentParser(
        description="AI-Native Development Toolkit",
        prog="ai-toolkit"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"ai-toolkit {__version__}"
    )
    
    # Create subparsers for each command
    subparsers = parser.add_subparsers(
        title="commands",
        dest="command",
        help="Command to execute"
    )
    
    # Add individual command parsers
    _add_init_parser(subparsers)
    _add_analyze_parser(subparsers)
    _add_query_parser(subparsers)
    _add_visualize_parser(subparsers)
    
    return parser

def _add_init_parser(subparsers):
    """Add the init command parser"""
    parser = subparsers.add_parser(
        "init", 
        help="Initialize a new project"
    )
    parser.add_argument(
        "project_name",
        nargs="?",
        help="Name of the project to initialize"
    )
    parser.add_argument(
        "--directory",
        help="Directory to initialize the project in"
    )

def _add_analyze_parser(subparsers):
    """Add the analyze command parser"""
    parser = subparsers.add_parser(
        "analyze", 
        help="Analyze code and update knowledge graph"
    )
    parser.add_argument(
        "--directory",
        required=True,
        help="Directory containing code to analyze"
    )
    parser.add_argument(
        "--language",
        default="python",
        choices=["python"],
        help="Programming language to analyze"
    )

def _add_query_parser(subparsers):
    """Add the query command parser"""
    parser = subparsers.add_parser(
        "query", 
        help="Query the knowledge graph"
    )
    parser.add_argument(
        "--component",
        help="Component to query"
    )
    parser.add_argument(
        "--relationships",
        action="store_true",
        help="Show relationships"
    )
    parser.add_argument(
        "--format",
        choices=["text", "json"],
        default="text",
        help="Output format"
    )

def _add_visualize_parser(subparsers):
    """Add the visualize command parser"""
    parser = subparsers.add_parser(
        "visualize", 
        help="Generate visualizations"
    )
    parser.add_argument(
        "--format",
        choices=["mermaid"],
        default="mermaid",
        help="Visualization format"
    )
    parser.add_argument(
        "--output",
        help="Output file path"
    )
    parser.add_argument(
        "--component",
        help="Component to visualize"
    )

def dispatch_command(args):
    """Dispatch to the appropriate command handler"""
    if not args.command:
        return 1
    
    try:
        # Dynamically import the command module
        # Check if we're running from 'src' directory
        if __name__.startswith('src.'):
            module_name = f"src.ai_toolkit.cli.commands.{args.command}"
        else:
            module_name = f"ai_toolkit.cli.commands.{args.command}"
            
        command_module = import_module(module_name)
        
        # Execute the command's main function
        return command_module.main(args)
    except ImportError as e:
        print(f"Error: Command '{args.command}' not implemented ({e})", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing command '{args.command}': {e}", file=sys.stderr)
        return 1

def main():
    """Main entry point for the CLI"""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return dispatch_command(args)

if __name__ == "__main__":
    sys.exit(main())
