"""
Relationship module for the AI-Native Development Toolkit.

This module defines the Relationship class used to represent 
connections between components in the knowledge graph.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any, Optional, List
from datetime import datetime


# Common relationship types
RELATIONSHIP_TYPES = {
    "imports": "Import relationship (module imports)",
    "calls": "Function/method call relationship",
    "defines": "Definition relationship (module defines class/function)",
    "inherits": "Inheritance relationship (class inherits from another)",
    "contains": "Containment relationship (class contains method)",
    "uses": "Usage relationship (component uses another)",
    "depends": "Dependency relationship (component depends on another)",
    "implements": "Implementation relationship (class implements interface)",
    "overrides": "Override relationship (method overrides parent method)",
}


@dataclass
class Relationship:
    """
    Represents a relationship between components.
    
    Relationships are the edges in the knowledge graph.
    """
    
    source_id: str  # ID of the source component
    target_id: str  # ID of the target component
    type: str       # Type of relationship (imports, calls, inherits, etc.)
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary representation."""
        return cls(
            id=data.get("id"),
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            type=data.get("type"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )
    
    def update(self, **kwargs: Any) -> None:
        """
        Update the relationship with new values.
        
        Args:
            **kwargs: Keyword arguments with new values
        """
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        
        # Update the updated_at timestamp
        self.updated_at = datetime.utcnow().isoformat()
    
    def add_metadata(self, key: str, value: Any) -> None:
        """
        Add metadata to the relationship.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_description(self) -> str:
        """
        Get a human-readable description of the relationship.
        
        Returns:
            Description string
        """
        return RELATIONSHIP_TYPES.get(self.type, f"Unknown relationship type: {self.type}")
    
    def get_weight(self) -> float:
        """
        Get the weight of the relationship (if any).
        
        Returns:
            Weight value (default: 1.0)
        """
        return float(self.metadata.get("weight", 1.0))
    
    def get_occurrences(self) -> int:
        """
        Get the number of occurrences of this relationship.
        
        Returns:
            Number of occurrences (default: 1)
        """
        return int(self.metadata.get("occurrences", 1))
    
    def get_line_numbers(self) -> List[int]:
        """
        Get the line numbers where this relationship occurs.
        
        Returns:
            List of line numbers or empty list if not available
        """
        lines = self.metadata.get("line_numbers", [])
        return lines if isinstance(lines, list) else []
    
    def get_direction(self) -> str:
        """
        Get the direction of the relationship (forward, backward, bidirectional).
        
        Returns:
            Direction string (default: "forward")
        """
        return self.metadata.get("direction", "forward")
        
    def is_direct(self) -> bool:
        """
        Check if the relationship is direct (vs. indirect/inferred).
        
        Returns:
            True if direct, False otherwise
        """
        return self.metadata.get("direct", True)
    
    def with_source(self, source_id: str) -> 'Relationship':
        """
        Create a new relationship with a new source.
        
        Args:
            source_id: ID of the new source component
            
        Returns:
            New relationship object
        """
        new_relationship = Relationship(
            source_id=source_id,
            target_id=self.target_id,
            type=self.type,
            metadata=self.metadata.copy()
        )
        return new_relationship
    
    def with_target(self, target_id: str) -> 'Relationship':
        """
        Create a new relationship with a new target.
        
        Args:
            target_id: ID of the new target component
            
        Returns:
            New relationship object
        """
        new_relationship = Relationship(
            source_id=self.source_id,
            target_id=target_id,
            type=self.type,
            metadata=self.metadata.copy()
        )
        return new_relationship
    
    def reversed(self) -> 'Relationship':
        """
        Create a new relationship with reversed source and target.
        
        Returns:
            New relationship object with source and target swapped
        """
        new_relationship = Relationship(
            source_id=self.target_id,
            target_id=self.source_id,
            type=self.type,
            metadata=self.metadata.copy()
        )
        
        # Update direction if present
        if "direction" in new_relationship.metadata:
            if new_relationship.metadata["direction"] == "forward":
                new_relationship.metadata["direction"] = "backward"
            elif new_relationship.metadata["direction"] == "backward":
                new_relationship.metadata["direction"] = "forward"
        
        return new_relationship
    
    def __str__(self) -> str:
        """Return a string representation of the relationship."""
        return f"{self.source_id} --[{self.type}]--> {self.target_id}"
