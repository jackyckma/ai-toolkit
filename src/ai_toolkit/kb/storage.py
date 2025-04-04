"""
Storage module for the AI-Native Development Toolkit.

This module provides storage capabilities for saving and loading
knowledge graph data to/from JSON files.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Union


class JSONStorage:
    """
    JSON-based storage for knowledge graph data.
    
    Handles saving and loading components and relationships
    to/from JSON files in the .ai-toolkit directory.
    """
    
    def __init__(self, base_path: Optional[Union[str, Path]] = None):
        """
        Initialize the storage system.
        
        Args:
            base_path: Base path for storage (defaults to .ai-toolkit in current directory)
        """
        if base_path is None:
            base_path = Path.cwd() / ".ai-toolkit"
        elif isinstance(base_path, str):
            base_path = Path(base_path)
            
        self.base_path = base_path
        self.kb_path = base_path / "kb"
        
        # Ensure directories exist
        self.kb_path.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        self.components_file = self.kb_path / "components.json"
        self.relationships_file = self.kb_path / "relationships.json"
    
    def save_components(self, components: Dict[str, Any]) -> None:
        """
        Save components to JSON file.
        
        Args:
            components: Dictionary of components to save
        """
        with open(self.components_file, 'w') as f:
            json.dump(components, f, indent=2)
    
    def load_components(self) -> Dict[str, Any]:
        """
        Load components from JSON file.
        
        Returns:
            Dictionary of components
        """
        if not self.components_file.exists():
            return {}
        
        with open(self.components_file, 'r') as f:
            return json.load(f)
    
    def save_relationships(self, relationships: List[Dict[str, Any]]) -> None:
        """
        Save relationships to JSON file.
        
        Args:
            relationships: List of relationships to save
        """
        with open(self.relationships_file, 'w') as f:
            json.dump(relationships, f, indent=2)
    
    def load_relationships(self) -> List[Dict[str, Any]]:
        """
        Load relationships from JSON file.
        
        Returns:
            List of relationships
        """
        if not self.relationships_file.exists():
            return []
        
        with open(self.relationships_file, 'r') as f:
            return json.load(f)
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get project information from config file.
        
        Returns:
            Project information
        """
        config_file = self.base_path / "config" / "config.json"
        
        if not config_file.exists():
            return {"name": "unknown", "version": "0.1.0"}
        
        with open(config_file, 'r') as f:
            return json.load(f)
    
    def save_project_info(self, info: Dict[str, Any]) -> None:
        """
        Save project information to config file.
        
        Args:
            info: Project information to save
        """
        config_dir = self.base_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "config.json"
        
        with open(config_file, 'w') as f:
            json.dump(info, f, indent=2)
