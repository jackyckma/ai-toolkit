#!/usr/bin/env python3
"""
AI-Native Development Toolkit CLI
Main entry point for the command-line interface.
"""

import argparse
import logging
import os
import sys
from importlib import import_module
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple, Any, Union

from ..kb.graph import KnowledgeGraph
from ..kb.component import Component
from ..kb.relationship import Relationship
from ..parser.extractor import ComponentExtractor
from ..viz.mermaid import MermaidGenerator
from ..viz.formats import create_output_file
from ..agents import CoordinatorAgent, CodeGenerationAgent, TestingAgent

# Define the version
__version__ = "0.1.0"

class CLI:
    """Main CLI class for the AI-Native Development Toolkit."""
    
    def __init__(self):
        """Initialize the CLI."""
        self.graph = None
        self.agent_system = None
        
    def initialize(self):
        """Initialize the CLI components."""
        # Check if we're in a toolkit directory
        toolkit_dir = Path.cwd() / ".ai-toolkit"
        if toolkit_dir.exists():
            self.graph = KnowledgeGraph(toolkit_dir)
            
            # Initialize agent system if requested
            try:
                self.agent_system = self._initialize_agent_system()
            except Exception as e:
                logging.error(f"Error initializing agent system: {e}")
                # Continue without agents if initialization fails
        
    def _initialize_agent_system(self):
        """Initialize the multi-agent system."""
        if self.graph is None:
            raise ValueError("Knowledge graph must be initialized before agent system")
            
        # Create a simple agent system with coordinator and speciality agents
        class AgentSystem:
            def __init__(self, graph):
                self.coordinator_agent = CoordinatorAgent(graph)
                self.code_generation_agent = CodeGenerationAgent(graph)
                self.testing_agent = TestingAgent(graph)
                
            def execute_task(self, task, context=None):
                """Execute a task using the coordinator agent."""
                return self.coordinator_agent.execute_task(task, context)
                
        return AgentSystem(self.graph)

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
    _add_agent_parser(subparsers)
    
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
    parser.add_argument(
        "--depth",
        type=int,
        default=2,
        help="Maximum depth of relationships to include"
    )
    parser.add_argument(
        "--type",
        choices=["component", "module", "class", "dependency", "call"],
        default="component",
        help="Type of diagram to generate"
    )

def _add_agent_parser(subparsers):
    """Add the agent command parser"""
    parser = subparsers.add_parser(
        "agent", 
        help="Use the multi-agent system for AI assistance"
    )
    parser.add_argument(
        "--task",
        help="Task description for the agent system"
    )
    parser.add_argument(
        "--context-file",
        help="JSON file with additional context for the task"
    )
    parser.add_argument(
        "--output",
        help="Output file path for the results"
    )
    parser.add_argument(
        "--direct-mode",
        choices=["code", "test"],
        help="Use a single agent directly instead of the coordinator"
    )

def dispatch_command(args):
    """Dispatch to the appropriate command handler"""
    if not args.command:
        return 1
    
    try:
        # Initialize CLI with shared functionality
        cli = CLI()
        cli.initialize()
        
        # Dynamically import the command module
        # Check if we're running from 'src' directory
        if __name__.startswith('src.'):
            module_name = f"src.ai_toolkit.cli.commands.{args.command}"
        else:
            module_name = f"ai_toolkit.cli.commands.{args.command}"
            
        command_module = import_module(module_name)
        
        # Check if we're using the new class-based command pattern
        if hasattr(command_module, f"{args.command.capitalize()}Command"):
            # Get the command class
            command_class = getattr(command_module, f"{args.command.capitalize()}Command")
            command_handler = command_class()
            return command_handler(args, cli)
        else:
            # Fall back to the legacy main function
            return command_module.main(args)
            
    except ImportError as e:
        print(f"Error: Command '{args.command}' not implemented ({e})", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error executing command '{args.command}': {e}", file=sys.stderr)
        logging.exception(f"Error in command {args.command}")
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
