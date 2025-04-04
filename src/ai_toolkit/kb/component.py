"""
Component module for the AI-Native Development Toolkit.

This module defines the Component class used to represent
code components in the knowledge graph.
"""

import uuid
from dataclasses import dataclass, field
from typing import Dict, Optional, Any, List, Set
from datetime import datetime


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
    line_end: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert the component to a dictionary representation."""
        return {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "file_path": self.file_path,
            "line_number": self.line_number,
            "line_end": self.line_end,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "updated_at": self.updated_at
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
            line_end=data.get("line_end"),
            metadata=data.get("metadata", {}),
            created_at=data.get("created_at", datetime.utcnow().isoformat()),
            updated_at=data.get("updated_at", datetime.utcnow().isoformat())
        )
    
    def update(self, **kwargs: Any) -> None:
        """
        Update the component with new values.
        
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
        Add metadata to the component.
        
        Args:
            key: Metadata key
            value: Metadata value
        """
        self.metadata[key] = value
        self.updated_at = datetime.utcnow().isoformat()
    
    def get_scope(self) -> str:
        """
        Get the scope of the component (module, class, function, method)
        
        Returns:
            Scope string
        """
        # If this is a method, get the full scope including class
        if self.type == "method" and "." in self.name:
            return self.name.split(".")[0]
        
        # If this is a module-level component
        if self.type in ["function", "class"] and self.file_path:
            return self.file_path.split("/")[-1].split(".")[0]
        
        return ""
    
    def get_signature(self) -> str:
        """
        Get the signature of the component (for functions/methods)
        
        Returns:
            Signature string or empty string if not applicable
        """
        if self.type not in ["function", "method"]:
            return ""
            
        return self.metadata.get("signature", "")
    
    def get_doc_string(self) -> str:
        """
        Get the docstring of the component
        
        Returns:
            Docstring or empty string if not available
        """
        return self.metadata.get("docstring", "")
    
    def get_parameters(self) -> List[Dict[str, Any]]:
        """
        Get the parameters of the function/method
        
        Returns:
            List of parameter dictionaries or empty list if not applicable
        """
        if self.type not in ["function", "method"]:
            return []
            
        return self.metadata.get("parameters", [])
    
    def get_return_type(self) -> str:
        """
        Get the return type of the function/method
        
        Returns:
            Return type string or empty string if not available
        """
        if self.type not in ["function", "method"]:
            return ""
            
        return self.metadata.get("return_type", "")
    
    def get_source_code(self) -> str:
        """
        Get the source code of the component
        
        Returns:
            Source code string or empty string if not available
        """
        return self.metadata.get("source", "")
    
    def get_complexity(self) -> int:
        """
        Get the cyclomatic complexity of the component
        
        Returns:
            Complexity value or 0 if not available
        """
        return self.metadata.get("complexity", 0)
    
    def get_imports(self) -> Set[str]:
        """
        Get the imports used by this component
        
        Returns:
            Set of import strings or empty set if not available
        """
        imports = self.metadata.get("imports", [])
        return set(imports) if isinstance(imports, list) else set()
    
    def __str__(self) -> str:
        """Return a string representation of the component."""
        location = f"{self.file_path}:{self.line_number}" if self.file_path else "unknown location"
        return f"{self.type} {self.name} ({location})"
