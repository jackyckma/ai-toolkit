"""
Dependency analyzer for the AI-Native Development Toolkit.

This module implements dependency analysis capabilities for code components,
detecting and categorizing relationships between different parts of the codebase.
"""

import logging
import os
from pathlib import Path
from typing import Dict, List, Optional, Set, Any, Tuple, Union

from ..kb.component import Component
from ..kb.relationship import Relationship
from ..kb.graph import KnowledgeGraph


class DependencyAnalyzer:
    """
    Analyzes dependencies between components in the codebase.
    
    Uses the Knowledge Graph to detect and categorize relationships
    between different parts of the code.
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the dependency analyzer.
        
        Args:
            knowledge_graph: Knowledge graph to use for analysis
        """
        self.knowledge_graph = knowledge_graph
        self.logger = logging.getLogger("ai_toolkit.parser.dependency")
    
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
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """
        Find circular dependencies between modules.
        
        Returns:
            List of circular dependency chains
        """
        self.logger.info("Analyzing circular dependencies")
        
        # First get the dependency graph
        dependencies = self.analyze_dependencies()
        
        # Build adjacency list for dependency graph
        adjacency_list = {}
        for module_name, deps in dependencies.items():
            adjacency_list[module_name] = deps["imports"]
        
        # Find cycles using DFS
        def find_cycles_from_node(node, path=None, visited=None):
            if path is None:
                path = []
            if visited is None:
                visited = set()
                
            cycles = []
            path.append(node)
            visited.add(node)
            
            for neighbor in adjacency_list.get(node, []):
                if neighbor in path:
                    # Found a cycle
                    cycle_start = path.index(neighbor)
                    cycle = path[cycle_start:] + [neighbor]
                    cycles.append(cycle)
                elif neighbor not in visited:
                    new_cycles = find_cycles_from_node(neighbor, path.copy(), visited.copy())
                    cycles.extend(new_cycles)
            
            return cycles
        
        # Find all cycles
        all_cycles = []
        for node in adjacency_list:
            cycles = find_cycles_from_node(node)
            for cycle in cycles:
                if cycle not in all_cycles:
                    all_cycles.append(cycle)
        
        # Filter duplicates (cycles that are rotations of each other)
        unique_cycles = []
        for cycle in all_cycles:
            # Convert to canonical form (smallest element first)
            min_index = cycle.index(min(cycle))
            canonical = cycle[min_index:] + cycle[:min_index]
            
            # Check if already in unique_cycles
            is_duplicate = False
            for existing in unique_cycles:
                if len(existing) == len(canonical):
                    min_index = existing.index(min(existing))
                    existing_canonical = existing[min_index:] + existing[:min_index]
                    if existing_canonical == canonical:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                unique_cycles.append(cycle)
        
        self.logger.info(f"Found {len(unique_cycles)} circular dependencies")
        return unique_cycles
    
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
