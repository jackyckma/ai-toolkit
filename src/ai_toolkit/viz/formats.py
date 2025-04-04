"""
Visualization formats module for the AI-Native Development Toolkit.

This module defines an interface for visualization generators
and provides utility functions for handling different formats.
"""

from abc import ABC, abstractmethod
import sys
from typing import Optional, List, TextIO

from ..kb.graph import KnowledgeGraph


class DiagramGenerator(ABC):
    """
    Abstract base class for diagram generators.
    
    All diagram generators should implement this interface.
    """
    
    def __init__(self, graph: KnowledgeGraph):
        """
        Initialize the generator.
        
        Args:
            graph: Knowledge graph to visualize
        """
        self.graph = graph
    
    @abstractmethod
    def generate(self, 
                 output: TextIO,
                 diagram_type: str,
                 component_id: Optional[str] = None,
                 max_depth: int = 1) -> None:
        """
        Generate a diagram.
        
        Args:
            output: Output file or stream
            diagram_type: Type of diagram to generate
            component_id: Optional ID of component to center on
            max_depth: Maximum depth of relationships to include
        """
        pass


def create_output_file(output_path: Optional[str]) -> TextIO:
    """
    Create an output file or return sys.stdout if no path is provided.
    
    Args:
        output_path: Optional path to output file
        
    Returns:
        File-like object for writing
    """
    if output_path:
        return open(output_path, 'w')
    else:
        return sys.stdout
