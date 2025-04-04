"""
Relationship module for the AI-Native Development Toolkit.

This module defines the Relationship class used to represent 
connections between components in the knowledge graph.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Any


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
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the relationship to a dictionary representation."""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "type": self.type,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Relationship':
        """Create a relationship from a dictionary representation."""
        return cls(
            id=data.get("id"),
            source_id=data.get("source_id"),
            target_id=data.get("target_id"),
            type=data.get("type"),
            metadata=data.get("metadata", {})
        )
    
    def __str__(self) -> str:
        """Return a string representation of the relationship."""
        return f"{self.source_id} --[{self.type}]--> {self.target_id}"
