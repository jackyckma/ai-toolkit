"""
Graph module for the AI-Native Development Toolkit.

This module defines the KnowledgeGraph class used to represent
the entire knowledge graph with components and relationships.
"""

from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Iterator, Union, Tuple
from collections import defaultdict
import logging

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
        
        # Build indexes for faster lookups
        self._component_by_name: Dict[str, List[Component]] = defaultdict(list)
        self._component_by_type: Dict[str, List[Component]] = defaultdict(list)
        self._component_by_path: Dict[str, List[Component]] = defaultdict(list)
        
        # Build relationship indexes
        self._outgoing_relationships: Dict[str, List[Relationship]] = defaultdict(list)
        self._incoming_relationships: Dict[str, List[Relationship]] = defaultdict(list)
        
        # Initialize logger
        self.logger = logging.getLogger("ai_toolkit.kb.graph")
        
        self._load()
        self._build_indexes()
    
    def _build_indexes(self) -> None:
        """Build indexes for faster lookups."""
        # Clear existing indexes
        self._component_by_name.clear()
        self._component_by_type.clear()
        self._component_by_path.clear()
        self._outgoing_relationships.clear()
        self._incoming_relationships.clear()
        
        # Build component indexes
        for component in self.components.values():
            self._component_by_name[component.name].append(component)
            self._component_by_type[component.type].append(component)
            
            if component.file_path:
                self._component_by_path[component.file_path].append(component)
        
        # Build relationship indexes
        for relationship in self.relationships:
            self._outgoing_relationships[relationship.source_id].append(relationship)
            self._incoming_relationships[relationship.target_id].append(relationship)
    
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
        
        # Build indexes
        self._build_indexes()
        
        self.logger.info(f"Loaded {len(self.components)} components and {len(self.relationships)} relationships")
    
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
        
        self.logger.info(f"Saved {len(self.components)} components and {len(self.relationships)} relationships")
    
    def add_component(self, component: Component) -> None:
        """
        Add a component to the knowledge graph.
        
        Args:
            component: Component to add
        """
        # Check if component already exists
        existing = self.components.get(component.id)
        if existing:
            self.logger.warning(f"Component {component.id} already exists, updating")
        
        self.components[component.id] = component
        
        # Update indexes
        self._component_by_name[component.name].append(component)
        self._component_by_type[component.type].append(component)
        
        if component.file_path:
            self._component_by_path[component.file_path].append(component)
    
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
        
        # Check for duplicate relationships
        for rel in self.relationships:
            if (rel.source_id == relationship.source_id and 
                rel.target_id == relationship.target_id and 
                rel.type == relationship.type):
                self.logger.warning(f"Relationship already exists: {relationship}")
                return
        
        # Add relationship
        self.relationships.append(relationship)
        
        # Update indexes
        self._outgoing_relationships[relationship.source_id].append(relationship)
        self._incoming_relationships[relationship.target_id].append(relationship)
    
    def remove_component(self, component_id: str) -> bool:
        """
        Remove a component and all its relationships from the knowledge graph.
        
        Args:
            component_id: ID of the component to remove
            
        Returns:
            True if component was removed, False if it did not exist
        """
        if component_id not in self.components:
            return False
        
        # Get the component
        component = self.components[component_id]
        
        # Remove component from indexes
        if component.name in self._component_by_name:
            self._component_by_name[component.name].remove(component)
            if not self._component_by_name[component.name]:
                del self._component_by_name[component.name]
                
        if component.type in self._component_by_type:
            self._component_by_type[component.type].remove(component)
            if not self._component_by_type[component.type]:
                del self._component_by_type[component.type]
                
        if component.file_path and component.file_path in self._component_by_path:
            self._component_by_path[component.file_path].remove(component)
            if not self._component_by_path[component.file_path]:
                del self._component_by_path[component.file_path]
        
        # Remove relationships involving this component
        self.relationships = [
            rel for rel in self.relationships 
            if rel.source_id != component_id and rel.target_id != component_id
        ]
        
        # Remove from relationship indexes
        if component_id in self._outgoing_relationships:
            del self._outgoing_relationships[component_id]
        
        if component_id in self._incoming_relationships:
            del self._incoming_relationships[component_id]
        
        # Remove component
        del self.components[component_id]
        
        return True
    
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
        return self._component_by_name.get(name, [])
    
    def get_components_by_type(self, type_name: str) -> List[Component]:
        """
        Get components by type.
        
        Args:
            type_name: Type of components to get
            
        Returns:
            List of components with the given type
        """
        return self._component_by_type.get(type_name, [])
    
    def get_components_by_file(self, file_path: str) -> List[Component]:
        """
        Get components by file path.
        
        Args:
            file_path: Path of the file containing components
            
        Returns:
            List of components in the given file
        """
        return self._component_by_path.get(file_path, [])
    
    def get_relationships_for_component(self, component_id: str) -> List[Relationship]:
        """
        Get relationships involving a component.
        
        Args:
            component_id: ID of the component
            
        Returns:
            List of relationships involving the component
        """
        outgoing = self._outgoing_relationships.get(component_id, [])
        incoming = self._incoming_relationships.get(component_id, [])
        
        return list(set(outgoing + incoming))
    
    def get_outgoing_relationships(self, component_id: str) -> List[Relationship]:
        """
        Get outgoing relationships from a component.
        
        Args:
            component_id: ID of the source component
            
        Returns:
            List of outgoing relationships
        """
        return self._outgoing_relationships.get(component_id, [])
    
    def get_incoming_relationships(self, component_id: str) -> List[Relationship]:
        """
        Get incoming relationships to a component.
        
        Args:
            component_id: ID of the target component
            
        Returns:
            List of incoming relationships
        """
        return self._incoming_relationships.get(component_id, [])
    
    def find_related_components(self, component_id: str, max_depth: int = 1) -> Dict[str, Tuple[Component, int]]:
        """
        Find components related to a component.
        
        Args:
            component_id: ID of the component
            max_depth: Maximum depth to traverse relationships (default: 1)
            
        Returns:
            Dictionary of related component IDs to (component, depth) tuples
        """
        if component_id not in self.components:
            return {}
        
        # Use BFS to find related components
        related: Dict[str, Tuple[Component, int]] = {}
        visited = {component_id}
        queue = [(component_id, 0)]  # (component_id, depth)
        
        while queue:
            current_id, depth = queue.pop(0)
            
            if depth >= max_depth:
                continue
            
            # Get relationships for this component
            for rel in self.get_relationships_for_component(current_id):
                next_id = rel.target_id if rel.source_id == current_id else rel.source_id
                
                if next_id in visited:
                    continue
                
                next_component = self.components.get(next_id)
                if not next_component:
                    continue
                
                related[next_id] = (next_component, depth + 1)
                visited.add(next_id)
                queue.append((next_id, depth + 1))
        
        return related
    
    def find_path(self, source_id: str, target_id: str) -> List[Tuple[Component, Relationship]]:
        """
        Find the shortest path between two components.
        
        Args:
            source_id: ID of the source component
            target_id: ID of the target component
            
        Returns:
            List of (component, relationship) tuples representing the path
        """
        if source_id not in self.components or target_id not in self.components:
            return []
        
        # Use BFS to find the shortest path
        visited = {source_id}
        queue = [(source_id, [])]  # (component_id, path)
        
        while queue:
            current_id, path = queue.pop(0)
            
            if current_id == target_id:
                # Construct final path
                result = []
                for i, rel_id in enumerate(path):
                    rel = next((r for r in self.relationships if r.id == rel_id), None)
                    if rel:
                        next_id = rel.target_id
                        result.append((self.components[next_id], rel))
                return result
            
            # Get outgoing relationships for this component
            for rel in self.get_outgoing_relationships(current_id):
                next_id = rel.target_id
                
                if next_id in visited:
                    continue
                
                visited.add(next_id)
                queue.append((next_id, path + [rel.id]))
        
        return []  # No path found
    
    def get_all_components(self) -> Iterator[Component]:
        """
        Get all components in the knowledge graph.
        
        Returns:
            Iterator of all components
        """
        return iter(self.components.values())
    
    def get_all_relationships(self) -> Iterator[Relationship]:
        """
        Get all relationships in the knowledge graph.
        
        Returns:
            Iterator of all relationships
        """
        return iter(self.relationships)
    
    def search_components(self, query: str, search_metadata: bool = False) -> List[Component]:
        """
        Search for components by name, type, or file path.
        
        Args:
            query: Search query string
            search_metadata: Whether to search in metadata
            
        Returns:
            List of matching components
        """
        results = []
        query = query.lower()
        
        for component in self.components.values():
            # Search in name
            if query in component.name.lower():
                results.append(component)
                continue
                
            # Search in type
            if query in component.type.lower():
                results.append(component)
                continue
                
            # Search in file path
            if component.file_path and query in component.file_path.lower():
                results.append(component)
                continue
                
            # Search in metadata
            if search_metadata and component.metadata:
                for key, value in component.metadata.items():
                    if isinstance(value, str) and query in value.lower():
                        results.append(component)
                        break
        
        return results
    
    def clear(self) -> None:
        """Clear all components and relationships from the knowledge graph."""
        self.components.clear()
        self.relationships.clear()
        self._component_by_name.clear()
        self._component_by_type.clear()
        self._component_by_path.clear()
        self._outgoing_relationships.clear()
        self._incoming_relationships.clear()
    
    def __str__(self) -> str:
        """Return a string representation of the knowledge graph."""
        return (f"KnowledgeGraph with {len(self.components)} components "
                f"and {len(self.relationships)} relationships")
