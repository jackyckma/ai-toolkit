"""
Visualize command for the AI-Native Development Toolkit.

This module implements the 'visualize' command, which generates
diagrams from the knowledge graph.
"""

import sys
from argparse import Namespace
from pathlib import Path

# Import using absolute imports to avoid path issues
try:
    from ai_toolkit.kb.graph import KnowledgeGraph
    from ai_toolkit.viz.mermaid import MermaidGenerator
    from ai_toolkit.viz.formats import create_output_file
except ImportError:
    # Fallback for development
    from src.ai_toolkit.kb.graph import KnowledgeGraph
    from src.ai_toolkit.viz.mermaid import MermaidGenerator
    from src.ai_toolkit.viz.formats import create_output_file


def main(args: Namespace) -> int:
    """
    Execute the visualize command.
    
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
    
    # Initialize knowledge graph
    graph = KnowledgeGraph()
    
    # Select visualization generator based on format
    if args.format == "mermaid":
        generator = MermaidGenerator(graph)
    else:
        print(f"Error: Unsupported visualization format {args.format}")
        return 1
    
    # Open output file or use stdout
    try:
        with create_output_file(args.output) as output:
            print(f"Generating {args.format} diagram...")
            
            # Determine diagram type
            diagram_type = "component"  # Default
            
            # Generate the appropriate diagram type
            if diagram_type == "component":
                if args.component:
                    # Find component by name
                    components = graph.get_component_by_name(args.component)
                    if not components:
                        print(f"Error: Component {args.component} not found")
                        return 1
                    
                    # Use the first component found
                    component_id = components[0].id
                    generator.generate_component_diagram(output, component_id)
                else:
                    # Generate diagram for all components
                    generator.generate_component_diagram(output)
            
            print(f"Diagram generated successfully{' to ' + args.output if args.output else ''}")
            return 0
    except Exception as e:
        print(f"Error generating visualization: {e}")
        return 1
