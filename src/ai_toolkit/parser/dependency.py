"""
Dependency analysis module for Python code.

This module analyzes the dependencies between components in a knowledge graph,
focusing on function calls, imports, and other relationships.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union
from collections import defaultdict

from ..kb.component import Component
from ..kb.relationship import Relationship
from ..kb.graph import KnowledgeGraph


class DependencyAnalyzer:
    """Analyzes dependencies between components in a knowledge graph."""
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the dependency analyzer.
        
        Args:
            knowledge_graph: The knowledge graph to analyze
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger(__name__)
        
        # Cache for dependency information
        self._import_dependencies: Dict[str, Set[str]] = {}
        self._call_dependencies: Dict[str, Set[str]] = {}
        self._component_dependencies: Dict[str, Dict[str, Set[str]]] = {}
    
    def analyze_imports(self) -> Dict[str, Set[str]]:
        """
        Analyze import dependencies in the knowledge graph.
        
        Returns:
            A dictionary mapping module IDs to sets of imported module IDs
        """
        if self._import_dependencies:
            return self._import_dependencies
        
        result = defaultdict(set)
        
        # Find all import relationships
        all_relationships = list(self.knowledge_graph.get_all_relationships())
        relationships = [rel for rel in all_relationships if rel.type == "imports"]
        
        for rel in relationships:
            source_id = rel.source_id
            target_id = rel.target_id
            
            # Add the dependency
            result[source_id].add(target_id)
        
        self._import_dependencies = result
        return result
    
    def analyze_calls(self) -> Dict[str, Set[str]]:
        """
        Analyze function call dependencies in the knowledge graph.
        
        Returns:
            A dictionary mapping function/method IDs to sets of called function/method IDs
        """
        if self._call_dependencies:
            return self._call_dependencies
        
        result = defaultdict(set)
        
        # Find all call relationships
        all_relationships = list(self.knowledge_graph.get_all_relationships())
        relationships = [rel for rel in all_relationships if rel.type == "calls"]
        
        for rel in relationships:
            source_id = rel.source_id
            target_id = rel.target_id
            
            # Add the dependency
            result[source_id].add(target_id)
        
        self._call_dependencies = result
        return result
    
    def analyze_component_dependencies(self, 
                                      component_id: str, 
                                      dependency_types: Optional[List[str]] = None,
                                      max_depth: int = 1) -> Dict[str, Set[str]]:
        """
        Analyze dependencies for a specific component.
        
        Args:
            component_id: ID of the component to analyze
            dependency_types: Types of relationships to consider as dependencies
                             (default: ["imports", "calls", "contains", "inherits"])
            max_depth: Maximum depth to traverse in the dependency graph
            
        Returns:
            A dictionary mapping relationship types to sets of component IDs
        """
        cache_key = f"{component_id}:{','.join(dependency_types or [])}:{max_depth}"
        if cache_key in self._component_dependencies:
            return self._component_dependencies[cache_key]
        
        if dependency_types is None:
            dependency_types = ["imports", "calls", "contains", "inherits", "defined_in"]
        
        result = defaultdict(set)
        visited = set()
        
        self._analyze_dependencies_recursive(
            component_id, result, visited, dependency_types, max_depth, 0
        )
        
        self._component_dependencies[cache_key] = result
        return result
    
    def _analyze_dependencies_recursive(self,
                                       component_id: str,
                                       result: Dict[str, Set[str]],
                                       visited: Set[str],
                                       dependency_types: List[str],
                                       max_depth: int,
                                       current_depth: int) -> None:
        """
        Recursively analyze dependencies for a component.
        
        Args:
            component_id: ID of the component to analyze
            result: Result dictionary to update
            visited: Set of visited component IDs to avoid cycles
            dependency_types: Types of relationships to consider as dependencies
            max_depth: Maximum depth to traverse
            current_depth: Current depth in the traversal
        """
        # Stop if we've visited this component already or exceeded the max depth
        if component_id in visited:
            return
            
        # Add to visited set to prevent cycles
        visited.add(component_id)
        
        # If we're beyond the max depth, don't add any more dependencies
        if current_depth > max_depth:
            return
            
        # Get outgoing relationships
        relationships = self.knowledge_graph.get_outgoing_relationships(component_id)
        
        # Filter for the requested relationship types
        filtered_rels = [rel for rel in relationships if rel.type in dependency_types]
        
        # Process each relationship
        for rel in filtered_rels:
            # Add the target as a dependency of the specified type
            result[rel.type].add(rel.target_id)
            
            # Only recurse if we haven't reached max depth yet
            if current_depth < max_depth:
                # Create a new visited set for the recursion to properly track paths
                new_visited = visited.copy()
                
                # Recursively process the target component
                self._analyze_dependencies_recursive(
                    rel.target_id, 
                    result,
                    new_visited,
                    dependency_types,
                    max_depth,
                    current_depth + 1
                )
    
    def calculate_complexity(self, component_id: str) -> Dict[str, Any]:
        """
        Calculate complexity metrics for a component based on its dependencies.
        
        Args:
            component_id: ID of the component to analyze
            
        Returns:
            Dictionary with complexity metrics
        """
        # Initialize metrics
        metrics = {
            "incoming_dependencies": 0,
            "outgoing_dependencies": 0,
            "dependency_types": defaultdict(int),
            "complexity_score": 0
        }
        
        # Get the component
        component = self.knowledge_graph.components.get(component_id)
        if not component:
            return metrics
        
        # Count outgoing dependencies
        dependencies = self.analyze_component_dependencies(
            component_id, ["imports", "calls", "inherits", "uses"]
        )
        
        for dep_type, deps in dependencies.items():
            metrics["outgoing_dependencies"] += len(deps)
            metrics["dependency_types"][dep_type] = len(deps)
        
        # Count incoming dependencies (how many components depend on this one)
        for rel_type in ["calls", "imports", "inherits", "uses"]:
            # Get incoming relationships of this type
            incoming_rels = self.knowledge_graph.get_incoming_relationships(component_id)
            incoming_rels = [rel for rel in incoming_rels if rel.type == rel_type]
            metrics["incoming_dependencies"] += len(incoming_rels)
            metrics["dependency_types"][f"incoming_{rel_type}"] = len(incoming_rels)
        
        # Calculate complexity score based on dependencies
        # More dependencies = higher complexity
        metrics["complexity_score"] = (
            metrics["incoming_dependencies"] * 0.7 + 
            metrics["outgoing_dependencies"] * 0.3
        )
        
        # Adjust score based on component type
        if component.type == "class":
            # Check inheritance depth
            inheritance_depth = self._calculate_inheritance_depth(component_id)
            metrics["inheritance_depth"] = inheritance_depth
            metrics["complexity_score"] += inheritance_depth * 0.5
            
            # Check number of methods
            methods = self.knowledge_graph.get_outgoing_relationships(component_id)
            methods = [rel for rel in methods if rel.type == "contains"]
            
            method_count = 0
            for rel in methods:
                target = self.knowledge_graph.components.get(rel.target_id)
                if target and target.type == "method":
                    method_count += 1
                    
            metrics["method_count"] = method_count
            metrics["complexity_score"] += method_count * 0.2
        
        elif component.type in ["function", "method"]:
            # Function complexity affected by number of parameters
            if "parameters" in component.metadata:
                param_count = len(component.metadata["parameters"])
                metrics["parameter_count"] = param_count
                metrics["complexity_score"] += param_count * 0.1
            
            # Function complexity affected by lines of code
            if component.line_end and component.line_number:
                loc = component.line_end - component.line_number + 1
                metrics["lines_of_code"] = loc
                metrics["complexity_score"] += loc * 0.05
        
        return metrics
    
    def _calculate_inheritance_depth(self, class_id: str) -> int:
        """Calculate inheritance depth for a class."""
        depth = 0
        current_id = class_id
        visited = set()
        
        while current_id and current_id not in visited:
            visited.add(current_id)
            
            # Find inheritance relationships
            relationships = self.knowledge_graph.get_outgoing_relationships(current_id)
            inheritance_rels = [rel for rel in relationships if rel.type == "inherits"]
            
            if not inheritance_rels:
                break
                
            # Use the first parent for depth calculation
            current_id = inheritance_rels[0].target_id
            depth += 1
        
        return depth
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies in the knowledge graph.
        
        Returns:
            List of circular dependency chains (lists of component IDs)
        """
        circular_deps = []
        call_deps = self.analyze_calls()
        
        for component_id in call_deps:
            path = []
            visited = set()
            self._find_circular_recursive(component_id, component_id, path, visited, call_deps, circular_deps)
        
        return circular_deps
    
    def _find_circular_recursive(self, 
                                start_id: str, 
                                current_id: str,
                                path: List[str],
                                visited: Set[str],
                                dependencies: Dict[str, Set[str]],
                                results: List[List[str]]) -> None:
        """
        Recursively search for circular dependencies.
        
        Args:
            start_id: ID of the starting component
            current_id: ID of the current component
            path: Current dependency path
            visited: Set of visited component IDs
            dependencies: Dependency map
            results: List to store found circular dependencies
        """
        if current_id in visited:
            return
            
        visited.add(current_id)
        path.append(current_id)
        
        for dep_id in dependencies.get(current_id, set()):
            if dep_id == start_id:
                # Found a circular dependency
                circular_path = path.copy()
                circular_path.append(start_id)
                results.append(circular_path)
            elif dep_id not in visited:
                self._find_circular_recursive(
                    start_id, dep_id, path, visited, dependencies, results
                )
        
        # Backtrack
        path.pop()
        visited.remove(current_id)
    
    def analyze_dependencies(self) -> Dict[str, Dict[str, List[str]]]:
        """
        Analyze dependencies between all components in the knowledge graph.
        
        Returns:
            Dictionary of module dependencies
            {module_name: {"imports": [...], "depends_on": [...], "used_by": [...]}}
        """
        self.logger.info("Analyzing dependencies between components")
        
        # Get all modules
        modules = self.knowledge_graph.get_components_by_type("module")
        
        # Initialize results dictionary
        dependencies = {}
        
        # Process each module
        for module in modules:
            module_name = module.name
            
            # Skip modules that are marked as imported (external)
            if module.metadata.get("imported", False):
                continue
                
            self.logger.debug(f"Analyzing dependencies for module {module_name}")
            
            # Initialize module entry
            dependencies[module_name] = {
                "imports": [],         # Direct imports
                "depends_on": [],      # Modules this module depends on (including transitive)
                "used_by": [],         # Modules that use this module
                "interfaces": [],      # Public interfaces (classes, functions)
                "complexity": 0        # Dependency complexity score
            }
            
            # Get import relationships
            import_relationships = self.knowledge_graph.get_relationships_by_source(
                module.id, relationship_type="imports"
            )
            
            # Extract imports
            for rel in import_relationships:
                # Get the target component
                target = self.knowledge_graph.get_component_by_id(rel.target_id)
                if target and target.type == "module":
                    dependencies[module_name]["imports"].append(target.name)
            
            # Find modules that use this module
            for other_module in modules:
                if other_module.id == module.id or other_module.metadata.get("imported", False):
                    continue
                    
                # Check if other_module imports this module
                other_imports = self.knowledge_graph.get_relationships_by_source(
                    other_module.id, relationship_type="imports"
                )
                
                for rel in other_imports:
                    if rel.target_id == module.id:
                        dependencies[module_name]["used_by"].append(other_module.name)
                        break
            
            # Find all public components (interfaces) in this module
            interfaces = self._find_module_interfaces(module)
            dependencies[module_name]["interfaces"] = interfaces
            
            # Calculate dependency complexity
            dependencies[module_name]["complexity"] = self._calculate_dependency_complexity(module)
            
        # Find transitive dependencies (depends_on)
        for module_name in dependencies:
            # Direct imports are the starting point for depends_on
            dependencies[module_name]["depends_on"] = list(dependencies[module_name]["imports"])
            
            # Add transitive dependencies
            self._add_transitive_dependencies(dependencies, module_name)
            
        self.logger.info(f"Analyzed dependencies for {len(dependencies)} modules")
        return dependencies
    
    def _find_module_interfaces(self, module: Component) -> List[str]:
        """
        Find public interfaces (classes, functions) in a module.
        
        Args:
            module: Module component
            
        Returns:
            List of interface names
        """
        interfaces = []
        
        # Get components contained in this module
        contained_relationships = self.knowledge_graph.get_relationships_by_source(
            module.id, relationship_type="contains"
        )
        
        for rel in contained_relationships:
            component = self.knowledge_graph.get_component_by_id(rel.target_id)
            if not component:
                continue
                
            # Classes and public functions are considered interfaces
            if component.type == "class":
                interfaces.append(component.name)
            elif component.type == "function" and not component.name.startswith("_"):
                interfaces.append(component.name)
                
        return interfaces
    
    def _calculate_dependency_complexity(self, module: Component) -> int:
        """
        Calculate dependency complexity for a module.
        
        Complexity is based on:
        - Number of imports
        - Number of components importing this module
        - Number of function/method calls to/from other modules
        
        Args:
            module: Module component
            
        Returns:
            Complexity score
        """
        score = 0
        
        # Count imports
        import_relationships = self.knowledge_graph.get_relationships_by_source(
            module.id, relationship_type="imports"
        )
        score += len(import_relationships)
        
        # Count components importing this module
        imported_by_relationships = self.knowledge_graph.get_relationships_by_target(
            module.id, relationship_type="imports"
        )
        score += len(imported_by_relationships)
        
        # Get all components in this module
        module_components = self.knowledge_graph.get_components_by_file(module.file_path or "")
        
        # Count external calls
        for component in module_components:
            # Get calls made by this component
            call_relationships = self.knowledge_graph.get_relationships_by_source(
                component.id, relationship_type="calls"
            )
            
            for rel in call_relationships:
                target = self.knowledge_graph.get_component_by_id(rel.target_id)
                if target and target.file_path != module.file_path:
                    # Call to external component
                    score += 1
            
            # Get calls made to this component
            called_by_relationships = self.knowledge_graph.get_relationships_by_target(
                component.id, relationship_type="calls"
            )
            
            for rel in called_by_relationships:
                source = self.knowledge_graph.get_component_by_id(rel.source_id)
                if source and source.file_path != module.file_path:
                    # Call from external component
                    score += 1
        
        return score
    
    def _add_transitive_dependencies(self, dependencies: Dict[str, Dict[str, List[str]]], module_name: str) -> None:
        """
        Add transitive dependencies to the depends_on list for a module.
        
        Args:
            dependencies: Dependencies dictionary
            module_name: Module name
        """
        if module_name not in dependencies:
            return
            
        # Get current direct dependencies
        direct_deps = set(dependencies[module_name]["imports"])
        
        # Current full dependency list
        all_deps = set(dependencies[module_name]["depends_on"])
        
        # Process each direct dependency
        for dep in direct_deps:
            if dep in dependencies:
                # Add this dependency's dependencies
                dep_dependencies = dependencies[dep]["imports"]
                for transitive_dep in dep_dependencies:
                    if transitive_dep not in all_deps and transitive_dep != module_name:
                        all_deps.add(transitive_dep)
                        dependencies[module_name]["depends_on"].append(transitive_dep)
        
        # Remove duplicates and sort
        dependencies[module_name]["depends_on"] = sorted(list(set(dependencies[module_name]["depends_on"])))
    
    def get_component_dependencies(self, component_id: str) -> Dict[str, List[str]]:
        """
        Get dependencies for a specific component.
        
        Args:
            component_id: Component ID
            
        Returns:
            Dictionary of dependencies:
            {
                "depends_on": [component_ids],
                "used_by": [component_ids],
                "imports": [component_ids],
                "calls": [component_ids],
                "called_by": [component_ids],
                "inherits": [component_ids],
                "inherited_by": [component_ids]
            }
        """
        component = self.knowledge_graph.get_component_by_id(component_id)
        if not component:
            raise ValueError(f"Component {component_id} not found")
            
        dependencies = {
            "depends_on": [],   # All components this component depends on
            "used_by": [],      # All components that use this component
            "imports": [],      # Imports (if module)
            "calls": [],        # Functions/methods called by this component
            "called_by": [],    # Components that call this component
            "inherits": [],     # Classes this component inherits from
            "inherited_by": []  # Classes that inherit from this component
        }
        
        # Get import relationships (for modules)
        if component.type == "module":
            import_relationships = self.knowledge_graph.get_relationships_by_source(
                component_id, relationship_type="imports"
            )
            for rel in import_relationships:
                dependencies["imports"].append(rel.target_id)
                dependencies["depends_on"].append(rel.target_id)
        
        # Get call relationships
        call_relationships = self.knowledge_graph.get_relationships_by_source(
            component_id, relationship_type="calls"
        )
        for rel in call_relationships:
            dependencies["calls"].append(rel.target_id)
            dependencies["depends_on"].append(rel.target_id)
        
        # Get called_by relationships
        called_by_relationships = self.knowledge_graph.get_relationships_by_target(
            component_id, relationship_type="calls"
        )
        for rel in called_by_relationships:
            dependencies["called_by"].append(rel.source_id)
            dependencies["used_by"].append(rel.source_id)
        
        # Get inheritance relationships (for classes)
        if component.type == "class":
            inherits_relationships = self.knowledge_graph.get_relationships_by_source(
                component_id, relationship_type="inherits"
            )
            for rel in inherits_relationships:
                dependencies["inherits"].append(rel.target_id)
                dependencies["depends_on"].append(rel.target_id)
            
            # Get inherited_by relationships
            inherited_by_relationships = self.knowledge_graph.get_relationships_by_target(
                component_id, relationship_type="inherits"
            )
            for rel in inherited_by_relationships:
                dependencies["inherited_by"].append(rel.source_id)
                dependencies["used_by"].append(rel.source_id)
        
        # Remove duplicates
        for key in dependencies:
            dependencies[key] = list(set(dependencies[key]))
        
        return dependencies
    
    def analyze_import_structure(self) -> Dict[str, Any]:
        """
        Analyze the import structure of the codebase.
        
        Returns:
            Dictionary with import analysis results
        """
        self.logger.info("Analyzing import structure")
        
        # Get all modules
        modules = self.knowledge_graph.get_components_by_type("module")
        
        # Skip external modules
        internal_modules = [m for m in modules if not m.metadata.get("imported", False)]
        
        # Initialize results
        analysis = {
            "total_modules": len(internal_modules),
            "import_counts": {},       # Module -> number of imports
            "imported_by_counts": {},  # Module -> number of times imported
            "most_imported": [],       # Most imported modules
            "most_importing": [],      # Modules with most imports
            "isolated_modules": [],    # Modules with no imports or importers
            "external_dependencies": {} # External module -> usage count
        }
        
        # Count imports and importers
        for module in internal_modules:
            # Count outgoing imports
            import_relationships = self.knowledge_graph.get_relationships_by_source(
                module.id, relationship_type="imports"
            )
            analysis["import_counts"][module.name] = len(import_relationships)
            
            # Count incoming imports (being imported)
            imported_by_relationships = self.knowledge_graph.get_relationships_by_target(
                module.id, relationship_type="imports"
            )
            analysis["imported_by_counts"][module.name] = len(imported_by_relationships)
            
            # Track external dependencies
            for rel in import_relationships:
                target = self.knowledge_graph.get_component_by_id(rel.target_id)
                if target and target.metadata.get("imported", False):
                    ext_name = target.name
                    if ext_name not in analysis["external_dependencies"]:
                        analysis["external_dependencies"][ext_name] = 0
                    analysis["external_dependencies"][ext_name] += 1
        
        # Find most imported modules
        most_imported = sorted(
            analysis["imported_by_counts"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        analysis["most_imported"] = most_imported[:10]  # Top 10
        
        # Find modules with most imports
        most_importing = sorted(
            analysis["import_counts"].items(),
            key=lambda x: x[1],
            reverse=True
        )
        analysis["most_importing"] = most_importing[:10]  # Top 10
        
        # Find isolated modules
        isolated_modules = []
        for module in internal_modules:
            if (analysis["import_counts"].get(module.name, 0) == 0 and
                analysis["imported_by_counts"].get(module.name, 0) == 0):
                isolated_modules.append(module.name)
        analysis["isolated_modules"] = isolated_modules
        
        # Most used external dependencies
        analysis["external_dependencies"] = dict(
            sorted(
                analysis["external_dependencies"].items(),
                key=lambda x: x[1],
                reverse=True
            )
        )
        
        self.logger.info("Import structure analysis complete")
        return analysis
