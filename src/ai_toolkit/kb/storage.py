"""
Storage module for the AI-Native Development Toolkit.

This module provides storage capabilities for saving and loading
knowledge graph data to/from JSON files.
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Union, Set
from datetime import datetime


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
        self.cache_path = base_path / "cache"
        
        # Ensure directories exist
        self.kb_path.mkdir(parents=True, exist_ok=True)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        
        # Define file paths
        self.components_file = self.kb_path / "components.json"
        self.relationships_file = self.kb_path / "relationships.json"
        
        # Setup logging
        self.logger = logging.getLogger("ai_toolkit.kb.storage")
        
        # Memory cache
        self._components_cache: Optional[Dict[str, Any]] = None
        self._relationships_cache: Optional[List[Dict[str, Any]]] = None
        self._cache_timestamp = 0
        self._cache_dirty = False
    
    def save_components(self, components: Dict[str, Any]) -> None:
        """
        Save components to JSON file.
        
        Args:
            components: Dictionary of components to save
        """
        start_time = time.time()
        self.logger.debug(f"Saving {len(components)} components to {self.components_file}")
        
        # Update cache
        self._components_cache = components
        self._cache_timestamp = time.time()
        self._cache_dirty = False
        
        try:
            with open(self.components_file, 'w') as f:
                json.dump(components, f, indent=2)
                
            self.logger.debug(f"Components saved in {time.time() - start_time:.2f}s")
        except Exception as e:
            self.logger.error(f"Error saving components: {e}")
            raise
    
    def load_components(self) -> Dict[str, Any]:
        """
        Load components from JSON file.
        
        Returns:
            Dictionary of components
        """
        # Check if cache is valid
        if self._components_cache is not None and not self._cache_dirty:
            self.logger.debug("Using cached components")
            return self._components_cache
        
        start_time = time.time()
        self.logger.debug(f"Loading components from {self.components_file}")
        
        if not self.components_file.exists():
            self.logger.warning(f"Components file {self.components_file} not found, returning empty dictionary")
            self._components_cache = {}
            self._cache_timestamp = time.time()
            return {}
        
        try:
            with open(self.components_file, 'r') as f:
                components = json.load(f)
            
            # Update cache
            self._components_cache = components
            self._cache_timestamp = time.time()
            
            self.logger.debug(f"Loaded {len(components)} components in {time.time() - start_time:.2f}s")
            return components
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing components file: {e}")
            return {}
        except Exception as e:
            self.logger.error(f"Error loading components: {e}")
            return {}
    
    def save_relationships(self, relationships: List[Dict[str, Any]]) -> None:
        """
        Save relationships to JSON file.
        
        Args:
            relationships: List of relationships to save
        """
        start_time = time.time()
        self.logger.debug(f"Saving {len(relationships)} relationships to {self.relationships_file}")
        
        # Update cache
        self._relationships_cache = relationships
        self._cache_timestamp = time.time()
        self._cache_dirty = False
        
        try:
            with open(self.relationships_file, 'w') as f:
                json.dump(relationships, f, indent=2)
                
            self.logger.debug(f"Relationships saved in {time.time() - start_time:.2f}s")
        except Exception as e:
            self.logger.error(f"Error saving relationships: {e}")
            raise
    
    def load_relationships(self) -> List[Dict[str, Any]]:
        """
        Load relationships from JSON file.
        
        Returns:
            List of relationships
        """
        # Check if cache is valid
        if self._relationships_cache is not None and not self._cache_dirty:
            self.logger.debug("Using cached relationships")
            return self._relationships_cache
        
        start_time = time.time()
        self.logger.debug(f"Loading relationships from {self.relationships_file}")
        
        if not self.relationships_file.exists():
            self.logger.warning(f"Relationships file {self.relationships_file} not found, returning empty list")
            self._relationships_cache = []
            self._cache_timestamp = time.time()
            return []
        
        try:
            with open(self.relationships_file, 'r') as f:
                relationships = json.load(f)
            
            # Update cache
            self._relationships_cache = relationships
            self._cache_timestamp = time.time()
            
            self.logger.debug(f"Loaded {len(relationships)} relationships in {time.time() - start_time:.2f}s")
            return relationships
        except json.JSONDecodeError as e:
            self.logger.error(f"Error parsing relationships file: {e}")
            return []
        except Exception as e:
            self.logger.error(f"Error loading relationships: {e}")
            return []
    
    def invalidate_cache(self) -> None:
        """Invalidate the memory cache."""
        self._components_cache = None
        self._relationships_cache = None
        self._cache_dirty = True
    
    def mark_dirty(self) -> None:
        """Mark the cache as dirty, requiring reload from disk."""
        self._cache_dirty = True
    
    def backup(self, suffix: Optional[str] = None) -> Dict[str, Path]:
        """
        Create a backup of the current knowledge graph.
        
        Args:
            suffix: Optional suffix for backup files (default: timestamp)
            
        Returns:
            Dictionary of original file paths to backup file paths
        """
        if suffix is None:
            suffix = datetime.now().strftime("%Y%m%d_%H%M%S")
            
        backup_files = {}
        
        # Backup components
        if self.components_file.exists():
            backup_path = self.kb_path / f"components_{suffix}.json"
            try:
                import shutil
                shutil.copy2(self.components_file, backup_path)
                backup_files[str(self.components_file)] = backup_path
                self.logger.info(f"Created backup of components at {backup_path}")
            except Exception as e:
                self.logger.error(f"Error backing up components: {e}")
        
        # Backup relationships
        if self.relationships_file.exists():
            backup_path = self.kb_path / f"relationships_{suffix}.json"
            try:
                import shutil
                shutil.copy2(self.relationships_file, backup_path)
                backup_files[str(self.relationships_file)] = backup_path
                self.logger.info(f"Created backup of relationships at {backup_path}")
            except Exception as e:
                self.logger.error(f"Error backing up relationships: {e}")
                
        return backup_files
    
    def get_analyzed_files(self) -> Set[str]:
        """
        Get the set of files that have been analyzed.
        
        Returns:
            Set of file paths
        """
        analyzed_files_path = self.cache_path / "analyzed_files.json"
        
        if not analyzed_files_path.exists():
            return set()
            
        try:
            with open(analyzed_files_path, 'r') as f:
                return set(json.load(f))
        except Exception as e:
            self.logger.error(f"Error loading analyzed files: {e}")
            return set()
    
    def add_analyzed_file(self, file_path: str) -> None:
        """
        Add a file to the set of analyzed files.
        
        Args:
            file_path: Path of the analyzed file
        """
        analyzed_files = self.get_analyzed_files()
        analyzed_files.add(file_path)
        
        try:
            with open(self.cache_path / "analyzed_files.json", 'w') as f:
                json.dump(list(analyzed_files), f)
        except Exception as e:
            self.logger.error(f"Error saving analyzed files: {e}")
    
    def get_project_info(self) -> Dict[str, Any]:
        """
        Get project information from config file.
        
        Returns:
            Project information
        """
        config_file = self.base_path / "config" / "config.json"
        
        if not config_file.exists():
            self.logger.warning(f"Config file {config_file} not found, returning default project info")
            return {
                "name": Path.cwd().name,
                "version": "0.1.0",
                "created_at": datetime.utcnow().isoformat()
            }
        
        try:
            with open(config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading project info: {e}")
            return {
                "name": Path.cwd().name,
                "version": "0.1.0",
                "created_at": datetime.utcnow().isoformat()
            }
    
    def save_project_info(self, info: Dict[str, Any]) -> None:
        """
        Save project information to config file.
        
        Args:
            info: Project information to save
        """
        config_dir = self.base_path / "config"
        config_dir.mkdir(parents=True, exist_ok=True)
        
        config_file = config_dir / "config.json"
        
        # Ensure updated_at is included
        if "updated_at" not in info:
            info["updated_at"] = datetime.utcnow().isoformat()
        
        try:
            with open(config_file, 'w') as f:
                json.dump(info, f, indent=2)
                
            self.logger.debug(f"Project info saved to {config_file}")
        except Exception as e:
            self.logger.error(f"Error saving project info: {e}")
    
    def save_cache_file(self, name: str, data: Any) -> None:
        """
        Save data to a cache file.
        
        Args:
            name: Name of the cache file
            data: Data to save (must be JSON-serializable)
        """
        cache_file = self.cache_path / f"{name}.json"
        
        try:
            with open(cache_file, 'w') as f:
                json.dump(data, f, indent=2)
                
            self.logger.debug(f"Cache data saved to {cache_file}")
        except Exception as e:
            self.logger.error(f"Error saving cache data: {e}")
    
    def load_cache_file(self, name: str) -> Any:
        """
        Load data from a cache file.
        
        Args:
            name: Name of the cache file
            
        Returns:
            Cached data or None if not found
        """
        cache_file = self.cache_path / f"{name}.json"
        
        if not cache_file.exists():
            return None
            
        try:
            with open(cache_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Error loading cache data: {e}")
            return None
