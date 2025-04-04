"""
Component extractor for the AI-Native Development Toolkit.

This module implements component extraction from various file types,
focusing on extracting high-level components like classes, functions,
and modules from source code.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Union, Tuple

from ai_toolkit.kb.graph import KnowledgeGraph
from ai_toolkit.kb.component import Component
from ai_toolkit.kb.relationship import Relationship
from ai_toolkit.parser.python import PythonParser


class ComponentExtractor:
    """Extracts components from source code files."""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the component extractor.
        
        Args:
            knowledge_graph: Knowledge graph to populate with extracted components
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Initialize parsers
        self.python_parser = PythonParser(knowledge_graph)
        
        # Track extracted files
        self.extracted_files: Set[str] = set()
    
    def extract_directory(self, directory: Union[str, Path]) -> Dict[str, int]:
        """
        Extract components from all supported files in a directory.
        
        Args:
            directory: Directory to analyze
            
        Returns:
            Dictionary with count of extracted components by type
        """
        self.logger.info(f"Extracting components from directory: {directory}")
        directory_path = Path(directory)
        
        if not directory_path.exists() or not directory_path.is_dir():
            self.logger.error(f"Directory does not exist: {directory}")
            return {}
        
        # Track extraction statistics
        stats = {
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "methods": 0,
            "files_processed": 0,
            "skipped_files": 0
        }
        
        # Walk through directory
        for root, _, files in os.walk(directory_path):
            for file in files:
                file_path = Path(root) / file
                
                # Skip already extracted files
                if str(file_path) in self.extracted_files:
                    stats["skipped_files"] += 1
                    continue
                
                # Process based on file extension
                if file.endswith(".py"):
                    file_stats = self.extract_python_file(file_path)
                    
                    # Update stats
                    for key, value in file_stats.items():
                        if key in stats:
                            stats[key] += value
                    
                    stats["files_processed"] += 1
                    self.extracted_files.add(str(file_path))
        
        self.logger.info(f"Extracted {sum(value for key, value in stats.items() if key != 'files_processed' and key != 'skipped_files')} components from {stats['files_processed']} files")
        return stats
    
    def extract_python_file(self, file_path: Union[str, Path]) -> Dict[str, int]:
        """
        Extract components from a Python file.
        
        Args:
            file_path: Path to the Python file
            
        Returns:
            Dictionary with count of extracted components by type
        """
        self.logger.debug(f"Extracting components from Python file: {file_path}")
        
        # Use the Python parser to extract components
        module = self.python_parser.parse_file(file_path)
        
        # Track statistics
        stats = {
            "modules": 0,
            "classes": 0,
            "functions": 0,
            "methods": 0
        }
        
        if module:
            stats["modules"] += 1
            
            # Count classes in the module
            class_relationships = self.knowledge_graph.get_relationships_by_source_and_type(
                module.id, "contains"
            )
            
            for rel in class_relationships:
                target = self.knowledge_graph.get_component_by_id(rel.target_id)
                if target and target.type == "class":
                    stats["classes"] += 1
                    
                    # Count methods in the class
                    method_relationships = self.knowledge_graph.get_relationships_by_source_and_type(
                        target.id, "contains"
                    )
                    
                    for method_rel in method_relationships:
                        method = self.knowledge_graph.get_component_by_id(method_rel.target_id)
                        if method and method.type == "method":
                            stats["methods"] += 1
                
                elif target and target.type == "function":
                    stats["functions"] += 1
        
        return stats
    
    def extract_call_graph(self) -> Dict[str, Any]:
        """
        Extract the call graph from analyzed files.
        
        This should be called after extracting components to resolve
        function call relationships.
        
        Returns:
            Dictionary with call graph statistics
        """
        self.logger.info("Extracting call graph from analyzed components")
        
        # Process collected function calls
        self.python_parser._process_function_calls()
        
        # Get statistics
        call_relationships = self.knowledge_graph.get_relationships_by_type("calls")
        
        stats = {
            "total_calls": len(call_relationships),
            "caller_components": set(),
            "called_components": set()
        }
        
        for rel in call_relationships:
            stats["caller_components"].add(rel.source_id)
            stats["called_components"].add(rel.target_id)
        
        stats["caller_components"] = len(stats["caller_components"])
        stats["called_components"] = len(stats["called_components"])
        
        self.logger.info(f"Extracted {stats['total_calls']} call relationships between {stats['caller_components']} callers and {stats['called_components']} callees")
        return stats
    
    def get_extracted_files(self) -> Set[str]:
        """Get the set of files that have been extracted."""
        return self.extracted_files
