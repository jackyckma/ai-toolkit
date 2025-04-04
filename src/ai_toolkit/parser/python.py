"""
Python parser for the AI-Native Development Toolkit.

This module implements a parser for Python code that extracts
components and relationships using the AST module.
"""

import ast
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

from ..kb.component import Component
from ..kb.relationship import Relationship
from ..kb.graph import KnowledgeGraph


class PythonParser:
    """
    Parser for Python code.
    
    Extracts components and relationships from Python code files
    using the AST module.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the parser.
        
        Args:
            knowledge_graph: Knowledge graph to update
        """
        self.knowledge_graph = knowledge_graph
        self.current_module: Optional[Component] = None
        self.current_class: Optional[Component] = None
        self.imported_modules: Dict[str, str] = {}  # Maps imported name to component ID
    
    def parse_directory(self, directory: Path) -> None:
        """
        Parse all Python files in a directory.
        
        Args:
            directory: Directory to parse
        """
        if not directory.exists():
            raise ValueError(f"Directory {directory} does not exist")
        
        for root, _, files in os.walk(directory):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    self.parse_file(file_path)
    
    def parse_file(self, file_path: Path) -> None:
        """
        Parse a Python file.
        
        Args:
            file_path: Path to the file to parse
        """
        if not file_path.exists():
            raise ValueError(f"File {file_path} does not exist")
        
        # Reset state for this file
        self.current_module = None
        self.current_class = None
        self.imported_modules = {}
        
        # Create a module component for the file
        module_name = file_path.stem
        self.current_module = Component(
            name=module_name,
            type="module",
            file_path=str(file_path),
            line_number=1,
            metadata={"path": str(file_path)}
        )
        self.knowledge_graph.add_component(self.current_module)
        
        # Parse the file
        with open(file_path, "r") as f:
            try:
                tree = ast.parse(f.read(), filename=str(file_path))
                self._process_module(tree)
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}")
    
    def _process_module(self, tree: ast.Module) -> None:
        """
        Process a module AST.
        
        Args:
            tree: AST of the module
        """
        if not self.current_module:
            return
        
        for node in tree.body:
            # Process imports
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                self._process_import(node)
            
            # Process classes
            elif isinstance(node, ast.ClassDef):
                self._process_class(node)
            
            # Process functions
            elif isinstance(node, ast.FunctionDef):
                self._process_function(node)
    
    def _process_import(self, node: Union[ast.Import, ast.ImportFrom]) -> None:
        """
        Process an import statement.
        
        Args:
            node: Import node
        """
        if not self.current_module:
            return
            
        module_id = self.current_module.id
        
        if isinstance(node, ast.Import):
            for name in node.names:
                imported_name = name.name
                alias = name.asname or imported_name
                
                # Create a component for the imported module if it doesn't exist
                imported_components = self.knowledge_graph.get_component_by_name(imported_name)
                if not imported_components:
                    imported_component = Component(
                        name=imported_name,
                        type="module",
                        metadata={"imported": True}
                    )
                    self.knowledge_graph.add_component(imported_component)
                    self.imported_modules[alias] = imported_component.id
                else:
                    self.imported_modules[alias] = imported_components[0].id
                
                # Create a relationship for the import
                relationship = Relationship(
                    source_id=module_id,
                    target_id=self.imported_modules[alias],
                    type="imports"
                )
                self.knowledge_graph.add_relationship(relationship)
        
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            
            # Create a component for the imported module if it doesn't exist
            imported_components = self.knowledge_graph.get_component_by_name(module_name)
            if not imported_components:
                imported_component = Component(
                    name=module_name,
                    type="module",
                    metadata={"imported": True}
                )
                self.knowledge_graph.add_component(imported_component)
                imported_module_id = imported_component.id
            else:
                imported_module_id = imported_components[0].id
            
            # Create a relationship for the import
            relationship = Relationship(
                source_id=module_id,
                target_id=imported_module_id,
                type="imports"
            )
            self.knowledge_graph.add_relationship(relationship)
            
            # Process imported names
            for name in node.names:
                imported_name = name.name
                alias = name.asname or imported_name
                
                # For now, we won't create components for individual imports from modules
                # Just track the module-level import
                self.imported_modules[alias] = imported_module_id
    
    def _process_class(self, node: ast.ClassDef) -> None:
        """
        Process a class definition.
        
        Args:
            node: Class definition node
        """
        if not self.current_module:
            return
            
        # Create a component for the class
        class_component = Component(
            name=node.name,
            type="class",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            metadata={
                "docstring": ast.get_docstring(node),
                "module_id": self.current_module.id
            }
        )
        self.knowledge_graph.add_component(class_component)
        
        # Create a relationship between the module and the class
        relationship = Relationship(
            source_id=self.current_module.id,
            target_id=class_component.id,
            type="contains"
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # Process inheritance
        for base in node.bases:
            if isinstance(base, ast.Name) and base.id in self.imported_modules:
                # Create a relationship for inheritance
                relationship = Relationship(
                    source_id=class_component.id,
                    target_id=self.imported_modules[base.id],
                    type="inherits"
                )
                self.knowledge_graph.add_relationship(relationship)
        
        # Set as current class for processing methods
        previous_class = self.current_class
        self.current_class = class_component
        
        # Process class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._process_method(item)
        
        # Restore previous class context
        self.current_class = previous_class
    
    def _process_function(self, node: ast.FunctionDef) -> None:
        """
        Process a function definition.
        
        Args:
            node: Function definition node
        """
        if not self.current_module:
            return
            
        # Create a component for the function
        function_component = Component(
            name=node.name,
            type="function",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            metadata={
                "docstring": ast.get_docstring(node),
                "module_id": self.current_module.id
            }
        )
        self.knowledge_graph.add_component(function_component)
        
        # Create a relationship between the module and the function
        relationship = Relationship(
            source_id=self.current_module.id,
            target_id=function_component.id,
            type="contains"
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # TODO: Analyze function calls and other relationships
    
    def _process_method(self, node: ast.FunctionDef) -> None:
        """
        Process a method definition.
        
        Args:
            node: Method definition node
        """
        if not self.current_module or not self.current_class:
            return
            
        # Create a component for the method
        method_component = Component(
            name=node.name,
            type="method",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            metadata={
                "docstring": ast.get_docstring(node),
                "class_id": self.current_class.id,
                "module_id": self.current_module.id
            }
        )
        self.knowledge_graph.add_component(method_component)
        
        # Create a relationship between the class and the method
        relationship = Relationship(
            source_id=self.current_class.id,
            target_id=method_component.id,
            type="contains"
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # TODO: Analyze method calls and other relationships
