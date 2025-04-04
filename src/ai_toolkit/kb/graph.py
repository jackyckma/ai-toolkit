"""
Graph module for the AI-Native Development Toolkit.

This module defines the KnowledgeGraph class used to represent
the entire knowledge graph with components and relationships.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Iterator, Union

from .component import Component
from .relationship import Relationship
from .storage import JSONStorage


class KnowledgeGraph:
    """
    Represents a knowledge graph of code components and their relationships.
    
    The knowledge graph contains components (nodes) and relationships (edges)
    and provides methods to query and manipulate them.
    """
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize a knowledge graph.
        
        Args:
            base_path: Base path for storage
        """
        self.storage = JSONStorage(base_path)
        self.components: Dict[str, Component] = {}
        self.relationships: List[Relationship] = []
        self.project_info: Dict[str, Any] = {}
        
        self._load()
    
    def _load(self) -> None:
        """Load the knowledge graph from storage."""
        # Load components
        components_data = self.storage.load_components()
        self.components = {
            component_id: Component.from_dict(component_data)
            for component_id, component_data in components_data.items()
        }
        
        # Load relationships
        relationships_data = self.storage.load_relationships()
        self.relationships = [
            Relationship.from_dict(relationship_data)
            for relationship_data in relationships_data
        ]
        
        # Load project info
        self.project_info = self.storage.get_project_info()
    
    def save(self) -> None:
        """Save the knowledge graph to storage."""
        # Save components
        components_data = {
            component_id: component.to_dict()
            for component_id, component in self.components.items()
        }
        self.storage.save_components(components_data)
        
        # Save relationships
        relationships_data = [
            relationship.to_dict()
            for relationship in self.relationships
        ]
        self.storage.save_relationships(relationships_data)
        
        # Save project info
        self.storage.save_project_info(self.project_info)
    
    def add_component(self, component: Component) -> None:
        """
        Add a component to the knowledge graph.
        
        Args:
            component: Component to add
        """
        self.components[component.id] = component
    
    def add_relationship(self, relationship: Relationship) -> None:
        """
        Add a relationship to the knowledge graph.
        
        Args:
            relationship: Relationship to add
        """
        # Check if source and target components exist
        if relationship.source_id not in self.components:
            raise ValueError(f"Source component {relationship.source_id} does not exist")
        if relationship.target_id not in self.components:
            raise ValueError(f"Target component {relationship.target_id} does not exist")
        
        self.relationships.append(relationship)
    
    def get_component(self, component_id: str) -> Optional[Component]:
        """
        Get a component by ID.
        
        Args:
            component_id: ID of the component to get
            
        Returns:
            Component if found, None otherwise
        """
        return self.components.get(component_id)
    
    def get_component_by_name(self, name: str) -> List[Component]:
        """
        Get components by name.
        
        Args:
            name: Name of the component to get
            
        Returns:
            List of components with the given name
        """
        return [
            component
            for component in self.components.values()
            if component.name == name
        ]
    
    def get_components_by_type(self, type_name: str) -> List[Component]:
        """
        Get components by type.
        
        Args:
            type_name: Type of components to get
            
        Returns:
            List of components with the given type
        """
        return [
            component
            for component in self.components.values()
            if component.type == type_name
        ]
    
    def get_relationships_for_component(self, component_id: str) -> List[Relationship]:
        """
        Get relationships involving a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of relationships involving the component
        """
        return [
            relationship
            for relationship in self.relationships
            if relationship.source_id == component_id or relationship.target_id == component_id
        ]
    
    def get_outgoing_relationships(self, component_id: str) -> List[Relationship]:
        """
        Get outgoing relationships from a component.
        
        Args:
            component_id: ID of the source component
            
        Returns:
            List of outgoing relationships
        """
        return [
            relationship
            for relationship in self.relationships
            if relationship.source_id == component_id
        ]
    
    def get_incoming_relationships(self, component_id: str) -> List[Relationship]:
        """
        Get incoming relationships to a component.
        
        Args:
            component_id: ID of the target component
            
        Returns:
            List of incoming relationships
        """
        return [
            relationship
            for relationship in self.relationships
            if relationship.target_id == component_id
        ]
    
    def find_related_components(self, component_id: str) -> Set[str]:
        """
        Find IDs of components related to a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            Set of IDs of related components
        """
        related_ids = set()
        
        for relationship in self.relationships:
            if relationship.source_id == component_id:
                related_ids.add(relationship.target_id)
            elif relationship.target_id == component_id:
                related_ids.add(relationship.source_id)
        
        return related_ids
    
    def get_all_components(self) -> Iterator[Component]:
        """Get all components in the knowledge graph."""
        return iter(self.components.values())
    
    def get_all_relationships(self) -> Iterator[Relationship]:
        """Get all relationships in the knowledge graph."""
        return iter(self.relationships)
    
    def __str__(self) -> str:
        """Return a string representation of the knowledge graph."""
        return f"KnowledgeGraph with {len(self.components)} components and {len(self.relationships)} relationships"
