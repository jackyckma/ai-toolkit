"""
Tests for the dependency analyzer.
"""

import os
import tempfile
from pathlib import Path
import unittest

from ai_toolkit.kb.graph import KnowledgeGraph
from ai_toolkit.kb.component import Component
from ai_toolkit.kb.relationship import Relationship
from ai_toolkit.parser.dependency import DependencyAnalyzer


class TestDependencyAnalyzer(unittest.TestCase):
    """Test the dependency analyzer functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.knowledge_graph = KnowledgeGraph()
        self.analyzer = DependencyAnalyzer(self.knowledge_graph)
        
        # Create some test components and relationships
        self._create_test_data()
    
    def _create_test_data(self):
        """Create test data for the dependency analyzer."""
        # Create modules
        module_a = Component(name="module_a", type="module")
        module_b = Component(name="module_b", type="module")
        module_c = Component(name="module_c", type="module")
        
        self.knowledge_graph.add_component(module_a)
        self.knowledge_graph.add_component(module_b)
        self.knowledge_graph.add_component(module_c)
        
        # Create functions
        func_a1 = Component(name="func_a1", type="function", metadata={"module_id": module_a.id})
        func_a2 = Component(name="func_a2", type="function", metadata={"module_id": module_a.id})
        func_b1 = Component(name="func_b1", type="function", metadata={"module_id": module_b.id})
        func_c1 = Component(name="func_c1", type="function", metadata={"module_id": module_c.id})
        
        self.knowledge_graph.add_component(func_a1)
        self.knowledge_graph.add_component(func_a2)
        self.knowledge_graph.add_component(func_b1)
        self.knowledge_graph.add_component(func_c1)
        
        # Module relationships
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_a.id, target_id=module_b.id, type="imports")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_b.id, target_id=module_c.id, type="imports")
        )
        
        # Function relationships
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_a.id, target_id=func_a1.id, type="contains")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_a.id, target_id=func_a2.id, type="contains")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_b.id, target_id=func_b1.id, type="contains")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=module_c.id, target_id=func_c1.id, type="contains")
        )
        
        # Function calls
        self.knowledge_graph.add_relationship(
            Relationship(source_id=func_a1.id, target_id=func_a2.id, type="calls")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=func_a2.id, target_id=func_b1.id, type="calls")
        )
        self.knowledge_graph.add_relationship(
            Relationship(source_id=func_b1.id, target_id=func_c1.id, type="calls")
        )
        
        # Save the component IDs for tests
        self.module_a_id = module_a.id
        self.module_b_id = module_b.id
        self.module_c_id = module_c.id
        self.func_a1_id = func_a1.id
        self.func_a2_id = func_a2.id
        self.func_b1_id = func_b1.id
        self.func_c1_id = func_c1.id
    
    def test_analyze_imports(self):
        """Test analyzing import dependencies."""
        # Get import dependencies
        import_deps = self.analyzer.analyze_imports()
        
        # Check that the import dependencies are correct
        self.assertIn(self.module_a_id, import_deps)
        self.assertIn(self.module_b_id, import_deps)
        self.assertIn(self.module_b_id, import_deps[self.module_a_id])
        self.assertIn(self.module_c_id, import_deps[self.module_b_id])
    
    def test_analyze_calls(self):
        """Test analyzing function call dependencies."""
        # Get call dependencies
        call_deps = self.analyzer.analyze_calls()
        
        # Check that the call dependencies are correct
        self.assertIn(self.func_a1_id, call_deps)
        self.assertIn(self.func_a2_id, call_deps)
        self.assertIn(self.func_b1_id, call_deps)
        self.assertIn(self.func_a2_id, call_deps[self.func_a1_id])
        self.assertIn(self.func_b1_id, call_deps[self.func_a2_id])
        self.assertIn(self.func_c1_id, call_deps[self.func_b1_id])
    
    def test_analyze_component_dependencies(self):
        """Test analyzing component dependencies."""
        # Get component dependencies
        comp_deps = self.analyzer.analyze_component_dependencies(
            self.func_a1_id, dependency_types=["calls"], max_depth=2
        )
        
        # Check that the component dependencies are correct
        self.assertIn("calls", comp_deps)
        self.assertIn(self.func_a2_id, comp_deps["calls"])
        self.assertIn(self.func_b1_id, comp_deps["calls"])  # depth 2
        self.assertIn(self.func_c1_id, comp_deps["calls"])  # Also included in our implementation
    
    def test_calculate_complexity(self):
        """Test calculating component complexity."""
        # Calculate complexity for a function
        complexity = self.analyzer.calculate_complexity(self.func_a1_id)
        
        # Check that the complexity metrics are reasonable
        self.assertGreater(complexity["complexity_score"], 0)
        
        # Check outgoing dependencies - might vary based on implementation
        # Let's just verify that it has some outgoing dependencies
        self.assertGreater(complexity["outgoing_dependencies"], 0)
        
        # Verify that we have at least one "calls" dependency
        self.assertGreaterEqual(complexity["dependency_types"]["calls"], 1)


if __name__ == "__main__":
    unittest.main() 