"""
Code extractor for the AI-Native Development Toolkit.

This module provides functionality to extract and structure code components
from files analyzed by the parser.
"""

import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

from ..kb.component import Component
from ..kb.graph import KnowledgeGraph


class CodeExtractor:
    """
    Extracts code components and structure from analyzed files.
    
    Provides methods to extract code snippets, function signatures,
    and other structured information from parsed files.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the code extractor.
        
        Args:
            knowledge_graph: Knowledge graph to use for extraction
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger("ai_toolkit.parser.extractor")
    
    def extract_component_code(self, component_id: str) -> Optional[str]:
        """
        Extract the source code for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Source code string or None if component doesn't exist or has no source
        """
        component = self.knowledge_graph.get_component_by_id(component_id)
        if not component:
            self.logger.warning(f"Component {component_id} not found")
            return None
        
        # Check if source is directly available in metadata
        if "source" in component.metadata:
            return component.metadata["source"]
        
        # If not, try to extract from file
        if not component.file_path or not os.path.exists(component.file_path):
            self.logger.warning(f"Component {component.name} has no valid file path")
            return None
        
        # Check if we have line information
        if not component.line_number:
            self.logger.warning(f"Component {component.name} has no line number information")
            return None
        
        # Determine end line
        end_line = component.line_end if component.line_end else component.line_number
        
        # Read the file and extract the source
        try:
            with open(component.file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()
            
            # Adjust for 1-indexed line numbers
            source_lines = lines[component.line_number - 1:end_line]
            return "".join(source_lines)
        except Exception as e:
            self.logger.error(f"Error extracting source for {component.name}: {e}")
            return None
    
    def extract_function_signature(self, component_id: str) -> Optional[str]:
        """
        Extract the function signature for a function or method component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Function signature string or None if not a function/method
        """
        component = self.knowledge_graph.get_component_by_id(component_id)
        if not component:
            return None
        
        # Check if this is a function or method
        if component.type not in ["function", "method"]:
            return None
        
        # Check if we already have the signature in metadata
        if "signature" in component.metadata:
            return component.metadata["signature"]
        
        # Extract from source code
        source = self.extract_component_code(component_id)
        if not source:
            return None
        
        # Extract the function definition line
        first_line = source.split("\n")[0].strip()
        
        # Simple regex to extract signature
        match = re.match(r"def\s+([^:]+):", first_line)
        if match:
            return match.group(1)
        
        return None
    
    def extract_class_structure(self, class_id: str) -> Dict[str, Any]:
        """
        Extract the structure of a class.
        
        Args:
            class_id: Class component ID
            
        Returns:
            Dictionary with class structure information
        """
        component = self.knowledge_graph.get_component_by_id(class_id)
        if not component or component.type != "class":
            self.logger.warning(f"Component {class_id} is not a class")
            return {}
        
        # Build the class structure
        structure = {
            "name": component.name,
            "docstring": component.metadata.get("docstring", ""),
            "bases": component.metadata.get("bases", []),
            "decorators": component.metadata.get("decorators", []),
            "methods": [],
            "attributes": [],
            "source": self.extract_component_code(class_id)
        }
        
        # Find all methods and attributes
        contained_relationships = self.knowledge_graph.get_relationships_by_source(
            class_id, relationship_type="contains"
        )
        
        for rel in contained_relationships:
            contained_component = self.knowledge_graph.get_component_by_id(rel.target_id)
            if not contained_component:
                continue
            
            if contained_component.type == "method":
                method = {
                    "name": contained_component.name.split(".")[-1],  # Remove class prefix
                    "signature": self.extract_function_signature(contained_component.id),
                    "docstring": contained_component.metadata.get("docstring", ""),
                    "decorators": contained_component.metadata.get("decorators", []),
                    "is_special": contained_component.metadata.get("is_special", False),
                    "line_number": contained_component.line_number,
                    "id": contained_component.id
                }
                structure["methods"].append(method)
            
            elif contained_component.type == "attribute":
                attribute = {
                    "name": contained_component.name.split(".")[-1],  # Remove class prefix
                    "line_number": contained_component.line_number,
                    "id": contained_component.id
                }
                structure["attributes"].append(attribute)
        
        # Sort methods and attributes by line number
        structure["methods"].sort(key=lambda x: x["line_number"] or 0)
        structure["attributes"].sort(key=lambda x: x["line_number"] or 0)
        
        return structure
    
    def extract_module_structure(self, module_id: str) -> Dict[str, Any]:
        """
        Extract the structure of a module.
        
        Args:
            module_id: Module component ID
            
        Returns:
            Dictionary with module structure information
        """
        component = self.knowledge_graph.get_component_by_id(module_id)
        if not component or component.type != "module":
            self.logger.warning(f"Component {module_id} is not a module")
            return {}
        
        # Build the module structure
        structure = {
            "name": component.name,
            "file_path": component.file_path,
            "docstring": component.metadata.get("docstring", ""),
            "imports": component.metadata.get("imports", []),
            "classes": [],
            "functions": [],
            "constants": []
        }
        
        # Find all classes, functions, and constants
        contained_relationships = self.knowledge_graph.get_relationships_by_source(
            module_id, relationship_type="contains"
        )
        
        for rel in contained_relationships:
            contained_component = self.knowledge_graph.get_component_by_id(rel.target_id)
            if not contained_component:
                continue
            
            if contained_component.type == "class":
                class_info = {
                    "name": contained_component.name,
                    "line_number": contained_component.line_number,
                    "id": contained_component.id,
                    "docstring": contained_component.metadata.get("docstring", ""),
                    "bases": contained_component.metadata.get("bases", [])
                }
                structure["classes"].append(class_info)
            
            elif contained_component.type == "function":
                func_info = {
                    "name": contained_component.name,
                    "line_number": contained_component.line_number,
                    "id": contained_component.id,
                    "signature": self.extract_function_signature(contained_component.id),
                    "docstring": contained_component.metadata.get("docstring", "")
                }
                structure["functions"].append(func_info)
            
            elif contained_component.type == "constant":
                const_info = {
                    "name": contained_component.name,
                    "line_number": contained_component.line_number,
                    "id": contained_component.id
                }
                structure["constants"].append(const_info)
        
        # Sort components by line number
        structure["classes"].sort(key=lambda x: x["line_number"] or 0)
        structure["functions"].sort(key=lambda x: x["line_number"] or 0)
        structure["constants"].sort(key=lambda x: x["line_number"] or 0)
        
        return structure
    
    def extract_call_hierarchy(self, function_id: str) -> Dict[str, Any]:
        """
        Extract the call hierarchy for a function or method.
        
        Args:
            function_id: Function or method component ID
            
        Returns:
            Dictionary with call hierarchy information:
            {
                "calls": [list of functions called by this function],
                "called_by": [list of functions that call this function]
            }
        """
        component = self.knowledge_graph.get_component_by_id(function_id)
        if not component or component.type not in ["function", "method"]:
            self.logger.warning(f"Component {function_id} is not a function or method")
            return {}
        
        hierarchy = {
            "name": component.name,
            "signature": self.extract_function_signature(function_id),
            "calls": [],
            "called_by": []
        }
        
        # Find functions called by this function
        call_relationships = self.knowledge_graph.get_relationships_by_source(
            function_id, relationship_type="calls"
        )
        
        for rel in call_relationships:
            called_component = self.knowledge_graph.get_component_by_id(rel.target_id)
            if not called_component:
                continue
            
            call_info = {
                "name": called_component.name,
                "id": called_component.id,
                "line_numbers": rel.metadata.get("line_numbers", [])
            }
            hierarchy["calls"].append(call_info)
        
        # Find functions that call this function
        called_by_relationships = self.knowledge_graph.get_relationships_by_target(
            function_id, relationship_type="calls"
        )
        
        for rel in called_by_relationships:
            caller_component = self.knowledge_graph.get_component_by_id(rel.source_id)
            if not caller_component:
                continue
            
            caller_info = {
                "name": caller_component.name,
                "id": caller_component.id,
                "line_numbers": rel.metadata.get("line_numbers", [])
            }
            hierarchy["called_by"].append(caller_info)
        
        # Sort by name
        hierarchy["calls"].sort(key=lambda x: x["name"])
        hierarchy["called_by"].sort(key=lambda x: x["name"])
        
        return hierarchy
    
    def extract_inheritance_hierarchy(self, class_id: str) -> Dict[str, Any]:
        """
        Extract the inheritance hierarchy for a class.
        
        Args:
            class_id: Class component ID
            
        Returns:
            Dictionary with inheritance hierarchy information:
            {
                "inherits_from": [list of base classes],
                "inherited_by": [list of derived classes]
            }
        """
        component = self.knowledge_graph.get_component_by_id(class_id)
        if not component or component.type != "class":
            self.logger.warning(f"Component {class_id} is not a class")
            return {}
        
        hierarchy = {
            "name": component.name,
            "inherits_from": [],
            "inherited_by": []
        }
        
        # Find base classes
        inherits_relationships = self.knowledge_graph.get_relationships_by_source(
            class_id, relationship_type="inherits"
        )
        
        for rel in inherits_relationships:
            base_component = self.knowledge_graph.get_component_by_id(rel.target_id)
            if not base_component:
                continue
            
            base_info = {
                "name": base_component.name,
                "id": base_component.id,
                "module": base_component.metadata.get("module_id", "")
            }
            hierarchy["inherits_from"].append(base_info)
        
        # Find derived classes
        inherited_by_relationships = self.knowledge_graph.get_relationships_by_target(
            class_id, relationship_type="inherits"
        )
        
        for rel in inherited_by_relationships:
            derived_component = self.knowledge_graph.get_component_by_id(rel.source_id)
            if not derived_component:
                continue
            
            derived_info = {
                "name": derived_component.name,
                "id": derived_component.id,
                "module": derived_component.metadata.get("module_id", "")
            }
            hierarchy["inherited_by"].append(derived_info)
        
        # Sort by name
        hierarchy["inherits_from"].sort(key=lambda x: x["name"])
        hierarchy["inherited_by"].sort(key=lambda x: x["name"])
        
        return hierarchy
    
    def extract_component_references(self, component_id: str) -> Dict[str, List[Dict[str, Any]]]:
        """
        Extract references to a component from other components.
        
        Args:
            component_id: Component ID
            
        Returns:
            Dictionary of references to the component
        """
        component = self.knowledge_graph.get_component_by_id(component_id)
        if not component:
            self.logger.warning(f"Component {component_id} not found")
            return {}
        
        references = {
            "imports": [],    # Components that import this component
            "calls": [],      # Components that call this component
            "inherits": [],   # Classes that inherit from this component
            "contains": [],   # Components that contain this component
            "references": []  # Other references to this component
        }
        
        # Find import references (if module)
        if component.type == "module":
            import_references = self.knowledge_graph.get_relationships_by_target(
                component_id, relationship_type="imports"
            )
            
            for rel in import_references:
                ref_component = self.knowledge_graph.get_component_by_id(rel.source_id)
                if not ref_component:
                    continue
                
                ref_info = {
                    "name": ref_component.name,
                    "id": ref_component.id,
                    "type": ref_component.type,
                    "line_numbers": rel.metadata.get("line_numbers", [])
                }
                references["imports"].append(ref_info)
        
        # Find call references (if function or method)
        if component.type in ["function", "method"]:
            call_references = self.knowledge_graph.get_relationships_by_target(
                component_id, relationship_type="calls"
            )
            
            for rel in call_references:
                ref_component = self.knowledge_graph.get_component_by_id(rel.source_id)
                if not ref_component:
                    continue
                
                ref_info = {
                    "name": ref_component.name,
                    "id": ref_component.id,
                    "type": ref_component.type,
                    "line_numbers": rel.metadata.get("line_numbers", [])
                }
                references["calls"].append(ref_info)
        
        # Find inheritance references (if class)
        if component.type == "class":
            inherits_references = self.knowledge_graph.get_relationships_by_target(
                component_id, relationship_type="inherits"
            )
            
            for rel in inherits_references:
                ref_component = self.knowledge_graph.get_component_by_id(rel.source_id)
                if not ref_component:
                    continue
                
                ref_info = {
                    "name": ref_component.name,
                    "id": ref_component.id,
                    "type": ref_component.type,
                    "line_numbers": rel.metadata.get("line_numbers", [])
                }
                references["inherits"].append(ref_info)
        
        # Find container references
        contains_references = self.knowledge_graph.get_relationships_by_target(
            component_id, relationship_type="contains"
        )
        
        for rel in contains_references:
            ref_component = self.knowledge_graph.get_component_by_id(rel.source_id)
            if not ref_component:
                continue
            
            ref_info = {
                "name": ref_component.name,
                "id": ref_component.id,
                "type": ref_component.type,
                "line_numbers": rel.metadata.get("line_numbers", [])
            }
            references["contains"].append(ref_info)
        
        # Sort references by name
        for ref_type in references:
            references[ref_type].sort(key=lambda x: x["name"])
        
        return references
    
    def get_component_documentation(self, component_id: str) -> Dict[str, Any]:
        """
        Extract comprehensive documentation for a component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Dictionary with component documentation
        """
        component = self.knowledge_graph.get_component_by_id(component_id)
        if not component:
            self.logger.warning(f"Component {component_id} not found")
            return {}
        
        documentation = {
            "id": component.id,
            "name": component.name,
            "type": component.type,
            "file_path": component.file_path,
            "line_number": component.line_number,
            "line_end": component.line_end,
            "docstring": component.metadata.get("docstring", ""),
            "source": self.extract_component_code(component_id),
            "metadata": component.metadata
        }
        
        # Add type-specific documentation
        if component.type == "class":
            documentation["structure"] = self.extract_class_structure(component_id)
            documentation["inheritance"] = self.extract_inheritance_hierarchy(component_id)
        
        elif component.type in ["function", "method"]:
            documentation["signature"] = self.extract_function_signature(component_id)
            documentation["call_hierarchy"] = self.extract_call_hierarchy(component_id)
        
        elif component.type == "module":
            documentation["structure"] = self.extract_module_structure(component_id)
        
        # Add references
        documentation["references"] = self.extract_component_references(component_id)
        
        return documentation
