"""
Component module for the AI-Native Development Toolkit.

This module defines the Component class used to represent
code components in the knowledge graph.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, Any


@dataclass
class Component:
    """
    Represents a code component (module, class, function, etc.).
    
    Components are the nodes in the knowledge graph.
    """
    
    name: str
    type: str  # module, class, function, etc.
    file_path: Optional[str] = None
    line_number: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "metadata": self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Component':
        """Create a component from a dictionary representation."""
        return cls(
            id=data.get("id"),
            name=data.get("name"),
            type=data.get("type"),
            file_path=data.get("file_path"),
            line_number=data.get("line_number"),
            metadata=data.get("metadata", {})
        )
    
    def __str__(self) -> str:
        """Return a string representation of the component."""
        location = f"{self.file_path}:{self.line_number}" if self.file_path else "unknown location"
        return f"{self.type} {self.name} ({location})"
