"""
Query command for the AI-Native Development Toolkit.

This module implements the 'query' command, which allows
querying the knowledge graph for components and relationships.
"""

import json
import sys
from argparse import Namespace
from pathlib import Path
from typing import Dict, List, Any

# Import using absolute imports to avoid path issues
try:
    from ai_toolkit.kb.graph import KnowledgeGraph
    from ai_toolkit.kb.component import Component
    from ai_toolkit.kb.relationship import Relationship
except ImportError:
    # Fallback for development
    from src.ai_toolkit.kb.graph import KnowledgeGraph
    from src.ai_toolkit.kb.component import Component
    from src.ai_toolkit.kb.relationship import Relationship


def format_component(component: Component) -> Dict[str, Any]:
    """Format a component for display."""
    return {
        "id": component.id,
        "name": component.name,
        "type": component.type,
        "file": component.file_path,
        "line": component.line_number
    }


def format_relationship(relationship: Relationship, graph: KnowledgeGraph) -> Dict[str, Any]:
    """Format a relationship for display."""
    source = graph.get_component(relationship.source_id)
    target = graph.get_component(relationship.target_id)
    
    return {
        "type": relationship.type,
        "source": {
            "id": source.id if source else "unknown",
            "name": source.name if source else "unknown",
            "type": source.type if source else "unknown"
        },
        "target": {
            "id": target.id if target else "unknown",
            "name": target.name if target else "unknown",
            "type": target.type if target else "unknown"
        }
    }


def display_text_results(components: List[Component], relationships: List[Dict[str, Any]]) -> None:
    """Display results in text format."""
    if components:
        print("\nComponents:")
        for component in components:
            location = f"{component.file_path}:{component.line_number}" if component.file_path else "unknown location"
            print(f"  {component.type} {component.name} ({location})")
    
    if relationships:
        print("\nRelationships:")
        for rel in relationships:
            print(f"  {rel['source']['name']} --[{rel['type']}]--> {rel['target']['name']}")


def display_json_results(components: List[Component], relationships: List[Dict[str, Any]]) -> None:
    """Display results in JSON format."""
    results = {
        "components": [format_component(c) for c in components],
        "relationships": relationships
    }
    print(json.dumps(results, indent=2))


def main(args: Namespace) -> int:
    """
    Execute the query command.
    
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
    
    components = []
    relationships = []
    
    # Query for specific component
    if args.component:
        # Find components by name
        components = graph.get_component_by_name(args.component)
        
        if not components:
            print(f"No components found with name '{args.component}'")
            return 1
        
        # If relationships flag is set, find relationships
        if args.relationships:
            formatted_relationships = []
            for component in components:
                # Get all relationships for this component
                component_relationships = graph.get_relationships_for_component(component.id)
                
                # Format relationships for display
                for rel in component_relationships:
                    formatted_relationships.append(format_relationship(rel, graph))
                
                relationships = formatted_relationships
    else:
        # No specific component, list all components
        components = list(graph.get_all_components())
        
        if args.relationships:
            # Format all relationships
            formatted_relationships = []
            for rel in graph.get_all_relationships():
                formatted_relationships.append(format_relationship(rel, graph))
            
            relationships = formatted_relationships
    
    # Display results in the requested format
    if args.format == "json":
        display_json_results(components, relationships)
    else:
        display_text_results(components, relationships)
    
    return 0
