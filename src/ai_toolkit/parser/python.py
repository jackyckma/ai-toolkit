"""
Python parser for the AI-Native Development Toolkit.

This module implements a parser for Python code that extracts
components and relationships using the AST module.
"""

import ast
import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union, cast

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
        self.logger = logging.getLogger("ai_toolkit.parser.python")
        
        # For tracking function calls
        self.function_calls: Dict[str, List[Tuple[int, str]]] = {}  # name -> [(line_number, target_id)]
        
        # For tracking name bindings
        self.name_bindings: Dict[str, str] = {}  # name -> component_id
        
        # For tracking analyze status
        self.analyzed_files: Set[str] = set()
    
    def parse_directory(self, directory: Union[str, Path]) -> Set[str]:
        """
        Parse all Python files in a directory.
        
        Args:
            directory: Directory to parse
            
        Returns:
            Set of parsed file paths
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise ValueError(f"Directory {directory} does not exist")
        
        self.logger.info(f"Parsing Python files in {directory}")
        
        parsed_files = set()
        for root, _, files in os.walk(directory_path):
            for file in files:
                if file.endswith(".py"):
                    file_path = Path(root) / file
                    try:
                        self.parse_file(file_path)
                        parsed_files.add(str(file_path))
                    except Exception as e:
                        self.logger.error(f"Error parsing {file_path}: {e}")
        
        self.logger.info(f"Parsed {len(parsed_files)} Python files")
        return parsed_files
    
    def parse_file(self, file_path: Union[str, Path]) -> Optional[Component]:
        """
        Parse a Python file.
        
        Args:
            file_path: Path to the file to parse
            
        Returns:
            Module component if successful, None otherwise
        """
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"File {file_path} does not exist")
        
        file_path_str = str(path)
        
        # Check if file has already been analyzed
        if file_path_str in self.analyzed_files:
            self.logger.debug(f"File {file_path} already analyzed, skipping")
            # Return the existing module component
            for component in self.knowledge_graph.get_components_by_file(file_path_str):
                if component.type == "module":
                    return component
            return None
        
        self.logger.info(f"Parsing {file_path}")
        
        # Reset state for this file
        self.current_module = None
        self.current_class = None
        self.imported_modules = {}
        self.function_calls = {}
        self.name_bindings = {}
        
        # Read the file content
        try:
            with open(path, "r", encoding="utf-8") as f:
                file_content = f.read()
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None
        
        # Create a module component for the file
        module_name = path.stem
        self.current_module = Component(
            name=module_name,
            type="module",
            file_path=file_path_str,
            line_number=1,
            line_end=file_content.count('\n') + 1,
            metadata={
                "path": file_path_str,
                "source": file_content
            }
        )
        self.knowledge_graph.add_component(self.current_module)
        self.name_bindings[module_name] = self.current_module.id
        
        # Parse the file
        try:
            tree = ast.parse(file_content, filename=file_path_str)
            self._process_module(tree)
            
            # Process function calls in a second pass
            self._process_function_calls()
            
            # Mark file as analyzed
            self.analyzed_files.add(file_path_str)
            
            return self.current_module
        except SyntaxError as e:
            self.logger.error(f"Syntax error in {file_path}: {e}")
            return None
        except Exception as e:
            self.logger.error(f"Error parsing {file_path}: {e}")
            return None
    
    def _process_function_calls(self) -> None:
        """Process collected function calls to create relationship components."""
        for name, calls in self.function_calls.items():
            # Check if we have a binding for this name
            if name in self.name_bindings:
                target_id = self.name_bindings[name]
                
                for call_data in calls:
                    # Handle both formats (backward compatibility)
                    if len(call_data) == 3:
                        # New format: (line_number, caller_id, call_info)
                        line_number, caller_id, call_info = call_data
                        
                        # Create a relationship for the call
                        relationship = Relationship(
                            source_id=caller_id,
                            target_id=target_id,
                            type="calls",
                            metadata={
                                "line_numbers": [line_number],
                                "call_type": call_info.get("call_type", "direct"),
                                "args_count": len(call_info.get("args", [])),
                                "kwargs_count": len(call_info.get("kwargs", {})),
                                "args": call_info.get("args", []),
                                "kwargs": call_info.get("kwargs", {})
                            }
                        )
                    else:
                        # Old format: (line_number, caller_id)
                        line_number, caller_id = call_data
                        
                        # Create a relationship for the call
                        relationship = Relationship(
                            source_id=caller_id,
                            target_id=target_id,
                            type="calls",
                            metadata={
                                "line_numbers": [line_number]
                            }
                        )
                    
                    try:
                        self.knowledge_graph.add_relationship(relationship)
                    except ValueError:
                        # One of the components may not exist - this is fine
                        pass
    
    def _process_module(self, tree: ast.Module) -> None:
        """
        Process a module AST.
        
        Args:
            tree: AST of the module
        """
        if not self.current_module:
            return
        
        # Extract module docstring
        docstring = ast.get_docstring(tree)
        if docstring:
            self.current_module.add_metadata("docstring", docstring)
        
        # Process module body
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
            
            # Process assignments for constant definitions
            elif isinstance(node, ast.Assign):
                self._process_assignment(node)
    
    def _get_node_end_line(self, node: ast.AST) -> int:
        """Get the last line number of a node."""
        # Try to get end_lineno attribute (Python 3.8+)
        if hasattr(node, 'end_lineno') and node.end_lineno is not None:
            return node.end_lineno
        
        # Fall back to the start line (not accurate but better than nothing)
        return node.lineno
    
    def _extract_function_signature(self, node: ast.FunctionDef) -> str:
        """Extract a function signature from a FunctionDef node."""
        # Basic implementation - can be expanded to handle more complex cases
        args = []
        
        if node.args.args:
            for arg in node.args.args:
                arg_str = arg.arg
                if hasattr(arg, 'annotation') and arg.annotation:
                    # Handle type annotations
                    annotation = ""
                    if isinstance(arg.annotation, ast.Name):
                        annotation = arg.annotation.id
                    elif isinstance(arg.annotation, ast.Attribute):
                        annotation = f"{self._get_attribute_name(arg.annotation)}"
                    
                    if annotation:
                        arg_str += f": {annotation}"
                args.append(arg_str)
        
        # Add *args if present
        if node.args.vararg:
            args.append(f"*{node.args.vararg.arg}")
        
        # Add **kwargs if present
        if node.args.kwarg:
            args.append(f"**{node.args.kwarg.arg}")
        
        # Get return annotation if present
        returns = ""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                returns = f" -> {node.returns.id}"
            elif isinstance(node.returns, ast.Attribute):
                returns = f" -> {self._get_attribute_name(node.returns)}"
        
        return f"{node.name}({', '.join(args)}){returns}"
    
    def _get_attribute_name(self, node: ast.Attribute) -> str:
        """Get the full name of an attribute (e.g., module.Class)."""
        if isinstance(node.value, ast.Name):
            return f"{node.value.id}.{node.attr}"
        elif isinstance(node.value, ast.Attribute):
            return f"{self._get_attribute_name(node.value)}.{node.attr}"
        return node.attr
    
    def _extract_parameters(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract parameters from a function definition."""
        parameters = []
        
        if node.args.args:
            for arg in node.args.args:
                param = {"name": arg.arg, "type": None}
                
                # Handle type annotations
                if hasattr(arg, 'annotation') and arg.annotation:
                    if isinstance(arg.annotation, ast.Name):
                        param["type"] = arg.annotation.id
                    elif isinstance(arg.annotation, ast.Attribute):
                        param["type"] = self._get_attribute_name(arg.annotation)
                
                parameters.append(param)
        
        # Handle *args
        if node.args.vararg:
            param = {"name": f"*{node.args.vararg.arg}", "type": None}
            if hasattr(node.args.vararg, 'annotation') and node.args.vararg.annotation:
                if isinstance(node.args.vararg.annotation, ast.Name):
                    param["type"] = node.args.vararg.annotation.id
            parameters.append(param)
        
        # Handle **kwargs
        if node.args.kwarg:
            param = {"name": f"**{node.args.kwarg.arg}", "type": None}
            if hasattr(node.args.kwarg, 'annotation') and node.args.kwarg.annotation:
                if isinstance(node.args.kwarg.annotation, ast.Name):
                    param["type"] = node.args.kwarg.annotation.id
            parameters.append(param)
        
        return parameters
    
    def _extract_return_type(self, node: ast.FunctionDef) -> Optional[str]:
        """Extract return type from a function definition."""
        if node.returns:
            if isinstance(node.returns, ast.Name):
                return node.returns.id
            elif isinstance(node.returns, ast.Attribute):
                return self._get_attribute_name(node.returns)
        return None
    
    def _process_import(self, node: Union[ast.Import, ast.ImportFrom]) -> None:
        """
        Process an import statement.
        
        Args:
            node: Import node
        """
        if not self.current_module:
            return
            
        module_id = self.current_module.id
        
        # Track imports for this module
        imports = self.current_module.metadata.get("imports", [])
        
        if isinstance(node, ast.Import):
            for name in node.names:
                imported_name = name.name
                alias = name.asname or imported_name
                
                # Add to module imports
                imports.append(imported_name)
                
                # Create a component for the imported module if it doesn't exist
                imported_components = self.knowledge_graph.get_component_by_name(imported_name)
                if not imported_components:
                    imported_component = Component(
                        name=imported_name,
                        type="module",
                        metadata={
                            "imported": True,
                            "imported_by": [self.current_module.name]
                        }
                    )
                    self.knowledge_graph.add_component(imported_component)
                    self.imported_modules[alias] = imported_component.id
                    self.name_bindings[alias] = imported_component.id
                else:
                    self.imported_modules[alias] = imported_components[0].id
                    self.name_bindings[alias] = imported_components[0].id
                    
                    # Update imported_by in metadata
                    imported_by = imported_components[0].metadata.get("imported_by", [])
                    if self.current_module.name not in imported_by:
                        imported_by.append(self.current_module.name)
                        imported_components[0].add_metadata("imported_by", imported_by)
                
                # Create a relationship for the import
                relationship = Relationship(
                    source_id=module_id,
                    target_id=self.imported_modules[alias],
                    type="imports",
                    metadata={
                        "line_numbers": [node.lineno],
                        "alias": alias if alias != imported_name else None
                    }
                )
                self.knowledge_graph.add_relationship(relationship)
        
        elif isinstance(node, ast.ImportFrom):
            module_name = node.module or ""
            
            # Add to module imports
            if module_name:
                imports.append(module_name)
            
            # Create a component for the imported module if it doesn't exist
            imported_components = self.knowledge_graph.get_component_by_name(module_name)
            if not imported_components and module_name:
                imported_component = Component(
                    name=module_name,
                    type="module",
                    metadata={
                        "imported": True,
                        "imported_by": [self.current_module.name]
                    }
                )
                self.knowledge_graph.add_component(imported_component)
                imported_module_id = imported_component.id
            else:
                imported_module_id = imported_components[0].id if imported_components else None
                
                # Update imported_by in metadata
                if imported_components:
                    imported_by = imported_components[0].metadata.get("imported_by", [])
                    if self.current_module.name not in imported_by:
                        imported_by.append(self.current_module.name)
                        imported_components[0].add_metadata("imported_by", imported_by)
            
            # Create a relationship for the import
            if imported_module_id:
                relationship = Relationship(
                    source_id=module_id,
                    target_id=imported_module_id,
                    type="imports",
                    metadata={
                        "line_numbers": [node.lineno],
                        "imported_names": [name.name for name in node.names]
                    }
                )
                self.knowledge_graph.add_relationship(relationship)
            
            # Process imported names
            for name in node.names:
                imported_name = name.name
                alias = name.asname or imported_name
                
                # Track the import for name resolution
                if imported_module_id:
                    # For objects imported from modules, we create a placeholder component
                    # with a full name that includes the module
                    full_name = f"{module_name}.{imported_name}" if module_name else imported_name
                    
                    # Check if the component exists
                    existing_components = self.knowledge_graph.get_component_by_name(full_name)
                    if not existing_components:
                        # Create a placeholder component
                        imported_component = Component(
                            name=full_name,
                            type="import",
                            metadata={
                                "imported": True,
                                "module": module_name,
                                "alias": alias if alias != imported_name else None,
                                "imported_by": [self.current_module.name]
                            }
                        )
                        self.knowledge_graph.add_component(imported_component)
                        self.imported_modules[alias] = imported_component.id
                        self.name_bindings[alias] = imported_component.id
                    else:
                        self.imported_modules[alias] = existing_components[0].id
                        self.name_bindings[alias] = existing_components[0].id
                        
                        # Update imported_by in metadata
                        imported_by = existing_components[0].metadata.get("imported_by", [])
                        if self.current_module.name not in imported_by:
                            imported_by.append(self.current_module.name)
                            existing_components[0].add_metadata("imported_by", imported_by)
        
        # Update module imports
        self.current_module.add_metadata("imports", imports)
    
    def _process_assignment(self, node: ast.Assign) -> None:
        """
        Process an assignment statement.
        
        Args:
            node: Assignment node
        """
        if not self.current_module:
            return
            
        # Only process module-level assignments
        if self.current_class:
            return
            
        # Only process simple assignments to names
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Create a component for the constant
                constant_component = Component(
                    name=target.id,
                    type="constant",
                    file_path=self.current_module.file_path,
                    line_number=node.lineno,
                    line_end=self._get_node_end_line(node),
                    metadata={
                        "module_id": self.current_module.id
                    }
                )
                self.knowledge_graph.add_component(constant_component)
                
                # Create a relationship between the module and the constant
                relationship = Relationship(
                    source_id=self.current_module.id,
                    target_id=constant_component.id,
                    type="contains",
                    metadata={
                        "line_numbers": [node.lineno]
                    }
                )
                self.knowledge_graph.add_relationship(relationship)
                
                # Register the name binding for later reference
                self.name_bindings[target.id] = constant_component.id
    
    def _process_class(self, node: ast.ClassDef) -> None:
        """
        Process a class definition.
        
        Args:
            node: Class definition node
        """
        if not self.current_module:
            return
            
        # Extract class source code
        if self.current_module.file_path:
            try:
                with open(self.current_module.file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                source = "".join(lines[node.lineno-1:self._get_node_end_line(node)])
            except Exception:
                source = ""
        else:
            source = ""
        
        # Create a component for the class
        class_component = Component(
            name=node.name,
            type="class",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            line_end=self._get_node_end_line(node),
            metadata={
                "docstring": ast.get_docstring(node),
                "module_id": self.current_module.id,
                "source": source,
                "bases": [self._get_base_name(base) for base in node.bases],
                "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list]
            }
        )
        self.knowledge_graph.add_component(class_component)
        
        # Register the name binding for later reference
        self.name_bindings[node.name] = class_component.id
        
        # Create a relationship between the module and the class
        relationship = Relationship(
            source_id=self.current_module.id,
            target_id=class_component.id,
            type="contains",
            metadata={
                "line_numbers": [node.lineno]
            }
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # Process inheritance
        for base in node.bases:
            base_name = self._get_base_name(base)
            
            # Try to resolve the base class
            if isinstance(base, ast.Name) and base.id in self.name_bindings:
                # We have a direct reference to a known component
                base_id = self.name_bindings[base.id]
                
                # Create a relationship for inheritance
                relationship = Relationship(
                    source_id=class_component.id,
                    target_id=base_id,
                    type="inherits",
                    metadata={
                        "line_numbers": [node.lineno]
                    }
                )
                self.knowledge_graph.add_relationship(relationship)
            elif isinstance(base, ast.Attribute) and isinstance(base.value, ast.Name):
                # It's a reference to a class from an imported module
                module_name = base.value.id
                if module_name in self.name_bindings:
                    # Try to find or create the target class component
                    module_id = self.name_bindings[module_name]
                    class_name = f"{module_name}.{base.attr}"
                    
                    # Check if we already have this class
                    existing_classes = self.knowledge_graph.get_component_by_name(class_name)
                    if existing_classes:
                        target_id = existing_classes[0].id
                    else:
                        # Create a placeholder component for the base class
                        base_class = Component(
                            name=class_name,
                            type="class",
                            metadata={
                                "imported": True,
                                "module_id": module_id
                            }
                        )
                        self.knowledge_graph.add_component(base_class)
                        target_id = base_class.id
                    
                    # Create a relationship for inheritance
                    relationship = Relationship(
                        source_id=class_component.id,
                        target_id=target_id,
                        type="inherits",
                        metadata={
                            "line_numbers": [node.lineno]
                        }
                    )
                    self.knowledge_graph.add_relationship(relationship)
        
        # Set as current class for processing methods
        previous_class = self.current_class
        self.current_class = class_component
        
        # Process class body
        for item in node.body:
            if isinstance(item, ast.FunctionDef):
                self._process_method(item)
            elif isinstance(item, ast.ClassDef):
                # Handle nested classes
                self._process_class(item)
            elif isinstance(item, ast.Assign):
                # Handle class attributes
                self._process_class_attribute(item)
        
        # Restore previous class context
        self.current_class = previous_class
    
    def _get_base_name(self, node: ast.expr) -> str:
        """Get the name of a base class from its AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        return str(node)
    
    def _get_decorator_name(self, node: ast.expr) -> str:
        """Get the name of a decorator from its AST node."""
        if isinstance(node, ast.Name):
            return node.id
        elif isinstance(node, ast.Call):
            if isinstance(node.func, ast.Name):
                return node.func.id
            elif isinstance(node.func, ast.Attribute):
                return self._get_attribute_name(node.func)
        elif isinstance(node, ast.Attribute):
            return self._get_attribute_name(node)
        return str(node)
    
    def _process_class_attribute(self, node: ast.Assign) -> None:
        """
        Process a class attribute.
        
        Args:
            node: Assignment node
        """
        if not self.current_module or not self.current_class:
            return
            
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Create a component for the attribute
                attr_component = Component(
                    name=f"{self.current_class.name}.{target.id}",
                    type="attribute",
                    file_path=self.current_module.file_path,
                    line_number=node.lineno,
                    line_end=self._get_node_end_line(node),
                    metadata={
                        "class_id": self.current_class.id,
                        "module_id": self.current_module.id
                    }
                )
                self.knowledge_graph.add_component(attr_component)
                
                # Create a relationship between the class and the attribute
                relationship = Relationship(
                    source_id=self.current_class.id,
                    target_id=attr_component.id,
                    type="contains",
                    metadata={
                        "line_numbers": [node.lineno]
                    }
                )
                self.knowledge_graph.add_relationship(relationship)
    
    def _process_function(self, node: ast.FunctionDef) -> None:
        """
        Process a function definition.
        
        Args:
            node: Function definition node
        """
        if not self.current_module:
            return
            
        # Extract function source code
        if self.current_module.file_path:
            try:
                with open(self.current_module.file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                source = "".join(lines[node.lineno-1:self._get_node_end_line(node)])
            except Exception:
                source = ""
        else:
            source = ""
        
        # Extract function signature, parameters, and return type
        signature = self._extract_function_signature(node)
        parameters = self._extract_parameters(node)
        return_type = self._extract_return_type(node)
        
        # Extract function calls for later processing
        function_calls = self._extract_function_calls(node)
        
        # Create a component for the function
        function_component = Component(
            name=node.name,
            type="function",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            line_end=self._get_node_end_line(node),
            metadata={
                "docstring": ast.get_docstring(node),
                "module_id": self.current_module.id,
                "source": source,
                "signature": signature,
                "parameters": parameters,
                "return_type": return_type,
                "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list],
                "function_calls": function_calls
            }
        )
        self.knowledge_graph.add_component(function_component)
        
        # Register the name binding for later reference
        self.name_bindings[node.name] = function_component.id
        
        # Create a relationship between the module and the function
        relationship = Relationship(
            source_id=self.current_module.id,
            target_id=function_component.id,
            type="contains",
            metadata={
                "line_numbers": [node.lineno]
            }
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # Process function calls
        self._analyze_function_calls(node, function_component.id)
    
    def _extract_function_calls(self, node: ast.FunctionDef) -> List[Dict[str, Any]]:
        """Extract function calls from a function body."""
        calls = []
        
        # Use a visitor to find all Call nodes
        class CallVisitor(ast.NodeVisitor):
            def __init__(self):
                self.calls = []
                
            def visit_Call(self, node):
                call_info = {}
                
                # Get the name of the function being called
                if isinstance(node.func, ast.Name):
                    call_info["name"] = node.func.id
                elif isinstance(node.func, ast.Attribute):
                    call_info["name"] = f"{self._get_attribute_name(node.func)}"
                
                if "name" in call_info:
                    call_info["line"] = node.lineno
                    self.calls.append(call_info)
                
                # Continue visiting children
                self.generic_visit(node)
                
            def _get_attribute_name(self, node):
                if isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
                elif isinstance(node.value, ast.Attribute):
                    return f"{self._get_attribute_name(node.value)}.{node.attr}"
                return node.attr
        
        visitor = CallVisitor()
        visitor.visit(node)
        return visitor.calls
    
    def _analyze_function_calls(self, node: ast.FunctionDef, function_id: str) -> None:
        """
        Analyze function calls in the function body and create relationships.
        
        Args:
            node: Function definition node
            function_id: ID of the function component
        """
        # Use a visitor to find all Call nodes
        class CallVisitor(ast.NodeVisitor):
            def __init__(self, parser):
                self.parser = parser
                self.current_function_id = function_id
                
            def visit_Call(self, node):
                call_info = {
                    "line": node.lineno,
                    "caller_id": self.current_function_id
                }
                
                # Extract arguments for deeper analysis
                args = []
                for arg in node.args:
                    if isinstance(arg, ast.Constant):
                        args.append({"type": "constant", "value": str(arg.value)})
                    elif isinstance(arg, ast.Name):
                        args.append({"type": "variable", "name": arg.id})
                    elif isinstance(arg, ast.Call):
                        args.append({"type": "nested_call"})
                    else:
                        args.append({"type": "expression"})
                
                # Extract keyword arguments
                kwargs = {}
                for keyword in node.keywords:
                    if isinstance(keyword.value, ast.Constant):
                        kwargs[keyword.arg] = {"type": "constant", "value": str(keyword.value.value)}
                    elif isinstance(keyword.value, ast.Name):
                        kwargs[keyword.arg] = {"type": "variable", "name": keyword.value.id}
                    else:
                        kwargs[keyword.arg] = {"type": "expression"}
                
                call_info["args"] = args
                call_info["kwargs"] = kwargs
                
                # Process different types of call patterns
                if isinstance(node.func, ast.Name):
                    # Simple function call: function_name()
                    func_name = node.func.id
                    call_info["name"] = func_name
                    call_info["call_type"] = "direct"
                    
                    # Check if this is a reference to a known function
                    if func_name in self.parser.name_bindings:
                        target_id = self.parser.name_bindings[func_name]
                        self._create_call_relationship(target_id, call_info)
                    else:
                        # Store for later resolution (might be defined later in the file)
                        if func_name not in self.parser.function_calls:
                            self.parser.function_calls[func_name] = []
                        self.parser.function_calls[func_name].append((node.lineno, function_id, call_info))
                
                elif isinstance(node.func, ast.Attribute):
                    # Method or attribute call: object.method() or module.function()
                    call_info["call_type"] = "attribute"
                    call_info["name"] = self._get_attribute_name(node.func)
                    
                    # Check for common patterns
                    if isinstance(node.func.value, ast.Name):
                        base_name = node.func.value.id
                        attr_name = node.func.attr
                        call_info["base"] = base_name
                        call_info["attr"] = attr_name
                        
                        # Check if the base is a known import
                        if base_name in self.parser.imported_modules:
                            # This might be a call to an imported module's function
                            module_id = self.parser.imported_modules[base_name]
                            full_name = f"{base_name}.{attr_name}"
                            
                            # Look for the target function/method in the knowledge graph
                            target_components = self.parser.knowledge_graph.get_component_by_name(full_name)
                            if target_components:
                                self._create_call_relationship(target_components[0].id, call_info)
                            else:
                                # Create a placeholder component for the external function
                                external_component = Component(
                                    name=full_name,
                                    type="external_function",
                                    metadata={
                                        "module": base_name,
                                        "function": attr_name,
                                        "external": True
                                    }
                                )
                                self.parser.knowledge_graph.add_component(external_component)
                                self._create_call_relationship(external_component.id, call_info)
                                
                                # Also create a relationship to the module
                                module_rel = Relationship(
                                    source_id=external_component.id,
                                    target_id=module_id,
                                    type="defined_in",
                                    metadata={}
                                )
                                try:
                                    self.parser.knowledge_graph.add_relationship(module_rel)
                                except ValueError:
                                    pass
                
                # Continue visiting children (for nested calls)
                self.generic_visit(node)
                
            def _get_attribute_name(self, node):
                if isinstance(node.value, ast.Name):
                    return f"{node.value.id}.{node.attr}"
                elif isinstance(node.value, ast.Attribute):
                    return f"{self._get_attribute_name(node.value)}.{node.attr}"
                return node.attr
                
            def _create_call_relationship(self, target_id, call_info):
                """Create a relationship for a function call."""
                relationship = Relationship(
                    source_id=self.current_function_id,
                    target_id=target_id,
                    type="calls",
                    metadata={
                        "line_numbers": [call_info["line"]],
                        "call_type": call_info.get("call_type", "unknown"),
                        "args_count": len(call_info.get("args", [])),
                        "kwargs_count": len(call_info.get("kwargs", {})),
                        "args": call_info.get("args", []),
                        "kwargs": call_info.get("kwargs", {})
                    }
                )
                try:
                    self.parser.knowledge_graph.add_relationship(relationship)
                except ValueError:
                    # One of the components may not exist
                    pass
        
        visitor = CallVisitor(self)
        visitor.visit(node)
    
    def _process_method(self, node: ast.FunctionDef) -> None:
        """
        Process a method definition.
        
        Args:
            node: Method definition node
        """
        if not self.current_module or not self.current_class:
            return
            
        # Extract method source code
        if self.current_module.file_path:
            try:
                with open(self.current_module.file_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
                source = "".join(lines[node.lineno-1:self._get_node_end_line(node)])
            except Exception:
                source = ""
        else:
            source = ""
        
        # Check if this is a special method
        is_special = node.name.startswith('__') and node.name.endswith('__')
        
        # Extract method signature, parameters, and return type
        signature = self._extract_function_signature(node)
        parameters = self._extract_parameters(node)
        return_type = self._extract_return_type(node)
        
        # Extract function calls for later processing
        function_calls = self._extract_function_calls(node)
        
        # Create a component for the method
        method_name = f"{self.current_class.name}.{node.name}"
        method_component = Component(
            name=method_name,
            type="method",
            file_path=self.current_module.file_path,
            line_number=node.lineno,
            line_end=self._get_node_end_line(node),
            metadata={
                "docstring": ast.get_docstring(node),
                "class_id": self.current_class.id,
                "module_id": self.current_module.id,
                "source": source,
                "signature": signature,
                "parameters": parameters,
                "return_type": return_type,
                "is_special": is_special,
                "decorators": [self._get_decorator_name(dec) for dec in node.decorator_list],
                "function_calls": function_calls
            }
        )
        self.knowledge_graph.add_component(method_component)
        
        # Register the name binding for later reference
        self.name_bindings[method_name] = method_component.id
        
        # Create a relationship between the class and the method
        relationship = Relationship(
            source_id=self.current_class.id,
            target_id=method_component.id,
            type="contains",
            metadata={
                "line_numbers": [node.lineno]
            }
        )
        self.knowledge_graph.add_relationship(relationship)
        
        # Check for method overrides
        # For each base class, check if this method overrides a method in the base class
        if hasattr(self.current_class, 'metadata') and 'bases' in self.current_class.metadata:
            for base_name in self.current_class.metadata['bases']:
                base_components = self.knowledge_graph.get_component_by_name(base_name)
                if base_components:
                    base_id = base_components[0].id
                    base_method_name = f"{base_name}.{node.name}"
                    base_methods = self.knowledge_graph.get_component_by_name(base_method_name)
                    
                    if base_methods:
                        # Create a relationship for method override
                        relationship = Relationship(
                            source_id=method_component.id,
                            target_id=base_methods[0].id,
                            type="overrides",
                            metadata={
                                "line_numbers": [node.lineno]
                            }
                        )
                        self.knowledge_graph.add_relationship(relationship)
        
        # Process method calls
        self._analyze_function_calls(node, method_component.id)
