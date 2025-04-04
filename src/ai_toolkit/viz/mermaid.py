"""
Mermaid visualization module for the AI-Native Development Toolkit.

This module generates Mermaid diagrams from the knowledge graph.
"""

from typing import Dict, List, Set, Optional, TextIO
import textwrap

from ..kb.graph import KnowledgeGraph
from ..kb.component import Component
from ..kb.relationship import Relationship
from .formats import DiagramGenerator


class MermaidGenerator(DiagramGenerator):
    """
    Generates Mermaid diagrams from the knowledge graph.
    
    Supports various types of diagrams, including:
    - Class diagrams
    - Flow charts
    - Dependency graphs
    """
    
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialize the generator.
        
        Args:
            graph: Knowledge graph to visualize
        """
        super().__init__(graph)
    
    def generate(self, 
                 output: TextIO,
                 diagram_type: str,
                 component_id: Optional[str] = None,
                 max_depth: int = 1) -> None:
        """
        Generate a diagram based on the specified type.
        
        Args:
            output: Output file or stream
            diagram_type: Type of diagram to generate
            component_id: Optional ID of component to center on
            max_depth: Maximum depth of relationships to include
        """
        if diagram_type == "component":
            self.generate_component_diagram(output, component_id, max_depth)
        elif diagram_type == "module":
            self.generate_module_diagram(output)
        elif diagram_type == "class":
            self.generate_class_diagram(output)
        else:
            raise ValueError(f"Unsupported diagram type: {diagram_type}")
    
    def generate_component_diagram(self, 
                                   output: TextIO, 
                                   component_id: Optional[str] = None,
                                   max_depth: int = 1,
                                   include_types: Optional[List[str]] = None) -> None:
        """
        Generate a component diagram in Mermaid format.
        
        Args:
            output: Output file or stream
            component_id: Optional ID of component to center on
            max_depth: Maximum depth of relationships to include
            include_types: Optional list of relationship types to include
        """
        # Write diagram header
        output.write("```mermaid\ngraph TD\n")
        
        # Include all components, or just the specified one and its neighbors
        included_components: Set[str] = set()
        included_relationships: List[Relationship] = []
        
        if component_id:
            # Start with the specified component
            component = self.graph.get_component(component_id)
            if not component:
                output.write("    %% Component not found\n")
                output.write("```\n")
                return
            
            # Include the component
            included_components.add(component_id)
            
            # Include related components up to max_depth
            current_depth = 0
            frontier = {component_id}
            
            while current_depth < max_depth and frontier:
                next_frontier = set()
                
                for current_id in frontier:
                    # Get relationships for this component
                    for relationship in self.graph.get_relationships_for_component(current_id):
                        # Check if relationship type should be included
                        if include_types and relationship.type not in include_types:
                            continue
                        
                        # Include the relationship
                        included_relationships.append(relationship)
                        
                        # Add the other end of the relationship to the next frontier
                        if relationship.source_id == current_id:
                            included_components.add(relationship.target_id)
                            next_frontier.add(relationship.target_id)
                        else:
                            included_components.add(relationship.source_id)
                            next_frontier.add(relationship.source_id)
                
                frontier = next_frontier
                current_depth += 1
        else:
            # Include all components
            for component in self.graph.get_all_components():
                included_components.add(component.id)
            
            # Include all relationships
            for relationship in self.graph.get_all_relationships():
                if not include_types or relationship.type in include_types:
                    included_relationships.append(relationship)
        
        # Generate component definitions
        for component_id in included_components:
            component = self.graph.get_component(component_id)
            if not component:
                continue
            
            # Generate component node with styling based on type
            node_style = self._get_node_style(component.type)
            label = self._format_label(component)
            output.write(f"    {component.id}[{label}]{node_style}\n")
        
        # Generate relationships
        for relationship in included_relationships:
            # Check if both components are included
            if (relationship.source_id in included_components and 
                relationship.target_id in included_components):
                # Generate relationship with styling based on type
                arrow_style = self._get_arrow_style(relationship.type)
                output.write(f"    {relationship.source_id} {arrow_style} {relationship.target_id}\n")
        
        # Write diagram footer
        output.write("```\n")
    
    def generate_module_diagram(self, output: TextIO) -> None:
        """
        Generate a module-level diagram in Mermaid format.
        
        Shows modules and their relationships, without classes or functions.
        
        Args:
            output: Output file or stream
        """
        # Write diagram header
        output.write("```mermaid\ngraph TD\n")
        
        # Get all modules
        modules = self.graph.get_components_by_type("module")
        module_ids = {module.id for module in modules}
        
        # Generate module definitions
        for module in modules:
            label = self._format_label(module)
            output.write(f"    {module.id}[{label}]:::module\n")
        
        # Generate module relationships
        for relationship in self.graph.get_all_relationships():
            # Only include relationships between modules
            if (relationship.source_id in module_ids and 
                relationship.target_id in module_ids):
                arrow_style = self._get_arrow_style(relationship.type)
                output.write(f"    {relationship.source_id} {arrow_style} {relationship.target_id}\n")
        
        # Write styling
        output.write("    %% Styling\n")
        output.write("    classDef module fill:#c4e2ff,stroke:#2980b9,stroke-width:2px\n")
        
        # Write diagram footer
        output.write("```\n")
    
    def generate_class_diagram(self, output: TextIO) -> None:
        """
        Generate a class diagram in Mermaid format.
        
        Shows classes, methods, and inheritance relationships.
        
        Args:
            output: Output file or stream
        """
        # Write diagram header
        output.write("```mermaid\nclassDiagram\n")
        
        # Get all classes
        classes = self.graph.get_components_by_type("class")
        
        # Track relationships between classes for later
        inheritance_relationships = []
        
        # Generate class definitions with methods
        for cls in classes:
            # Write class name
            output.write(f"    class {cls.name} {{\n")
            
            # Get methods for this class
            method_relationships = self.graph.get_outgoing_relationships(cls.id)
            for rel in method_relationships:
                if rel.type == "contains":
                    method = self.graph.get_component(rel.target_id)
                    if method and method.type == "method":
                        output.write(f"        +{method.name}()\n")
            
            output.write("    }\n")
            
            # Collect inheritance relationships
            for rel in self.graph.get_outgoing_relationships(cls.id):
                if rel.type == "inherits":
                    inheritance_relationships.append(rel)
        
        # Generate inheritance relationships
        for rel in inheritance_relationships:
            source = self.graph.get_component(rel.source_id)
            target = self.graph.get_component(rel.target_id)
            if source and target:
                output.write(f"    {source.name} --|> {target.name}\n")
        
        # Write diagram footer
        output.write("```\n")
    
    def _get_node_style(self, component_type: str) -> str:
        """Get the Mermaid style for a component node based on its type."""
        if component_type == "module":
            return ":::module"
        elif component_type == "class":
            return ":::class"
        elif component_type == "function":
            return ":::function"
        elif component_type == "method":
            return ":::method"
        else:
            return ""
    
    def _get_arrow_style(self, relationship_type: str) -> str:
        """Get the Mermaid arrow style for a relationship based on its type."""
        if relationship_type == "imports":
            return "-->"
        elif relationship_type == "contains":
            return "==>"
        elif relationship_type == "inherits":
            return "-.->|inherits|"
        elif relationship_type == "calls":
            return "-->|calls|"
        else:
            return "-->"
    
    def _format_label(self, component: Component) -> str:
        """Format a component label for display in Mermaid."""
        if component.type == "module":
            # Extract the filename for modules
            if component.file_path:
                return f"{component.name}.py"
            else:
                return f"{component.name}"
        elif component.type == "class":
            return f"Class<br/>{component.name}"
        elif component.type == "function":
            return f"fn {component.name}()"
        elif component.type == "method":
            return f"{component.name}()"
        else:
            return component.name
