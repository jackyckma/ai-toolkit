"""
Tests for the function call analyzer in the Python parser.
"""

import os
import tempfile
from pathlib import Path
import unittest

from ai_toolkit.kb.graph import KnowledgeGraph
from ai_toolkit.parser.python import PythonParser
from ai_toolkit.parser.dependency import DependencyAnalyzer


class TestFunctionCallAnalyzer(unittest.TestCase):
    """Test the function call analyzer functionality."""
    
    def setUp(self):
        """Set up the test environment."""
        self.knowledge_graph = KnowledgeGraph()
        self.parser = PythonParser(self.knowledge_graph)
        self.test_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up after tests."""
        for file in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, file))
        os.rmdir(self.test_dir)
    
    def test_simple_function_call(self):
        """Test analysis of simple function calls."""
        # Create a test file with functions that call each other
        test_file = os.path.join(self.test_dir, "test_simple_call.py")
        with open(test_file, "w") as f:
            f.write("""
def function1():
    return "Hello"

def function2():
    result = function1()
    return result

def function3():
    result = function2()
    return result
""")
        
        # Parse the file
        self.parser.parse_file(test_file)
        self.parser._process_function_calls()
        
        # Verify relationships
        # Get the components
        module = self.knowledge_graph.get_component_by_name("test_simple_call")[0]
        
        # Find the function components
        functions = {}
        for rel in self.knowledge_graph.get_relationships_by_source(module.id):
            target = self.knowledge_graph.get_component_by_id(rel.target_id)
            if target and target.type == "function":
                functions[target.name] = target
        
        # Check that we have all functions
        self.assertEqual(len(functions), 3)
        self.assertIn("function1", functions)
        self.assertIn("function2", functions)
        self.assertIn("function3", functions)
        
        # Check call relationships
        function1_calls = self.knowledge_graph.get_relationships_by_source(
            functions["function1"].id, relationship_type="calls"
        )
        self.assertEqual(len(function1_calls), 0, "function1 should not call any functions")
        
        function2_calls = self.knowledge_graph.get_relationships_by_source(
            functions["function2"].id, relationship_type="calls"
        )
        self.assertEqual(len(function2_calls), 1, "function2 should call one function")
        called_by_function2 = self.knowledge_graph.get_component_by_id(function2_calls[0].target_id)
        self.assertEqual(called_by_function2.name, "function1", "function2 should call function1")
        
        function3_calls = self.knowledge_graph.get_relationships_by_source(
            functions["function3"].id, relationship_type="calls"
        )
        self.assertEqual(len(function3_calls), 1, "function3 should call one function")
        called_by_function3 = self.knowledge_graph.get_component_by_id(function3_calls[0].target_id)
        self.assertEqual(called_by_function3.name, "function2", "function3 should call function2")
    
    def test_attribute_function_call(self):
        """Test analysis of attribute-based function calls (obj.method())."""
        # Create a test file with a class and method calls
        test_file = os.path.join(self.test_dir, "test_attribute_call.py")
        with open(test_file, "w") as f:
            f.write("""
class TestClass:
    def method1(self):
        return "Hello"
        
    def method2(self):
        return self.method1()
        
def function1():
    obj = TestClass()
    return obj.method2()
""")
        
        # Parse the file
        self.parser.parse_file(test_file)
        self.parser._process_function_calls()
        
        # Get the components
        module = self.knowledge_graph.get_component_by_name("test_attribute_call")[0]
        
        # Find the class and function components
        test_class = None
        function1 = None
        
        for rel in self.knowledge_graph.get_relationships_by_source(module.id):
            target = self.knowledge_graph.get_component_by_id(rel.target_id)
            if target:
                if target.type == "class":
                    test_class = target
                elif target.type == "function" and target.name == "function1":
                    function1 = target
        
        self.assertIsNotNone(test_class, "TestClass should exist")
        self.assertIsNotNone(function1, "function1 should exist")
        
        # Find the methods
        method1 = self.knowledge_graph.get_component_by_name("TestClass.method1")[0]
        method2 = self.knowledge_graph.get_component_by_name("TestClass.method2")[0]
        
        # Check call relationships
        method2_calls = self.knowledge_graph.get_relationships_by_source(
            method2.id, relationship_type="calls"
        )
        self.assertTrue(len(method2_calls) > 0, "method2 should call method1")
        
        # Check the call metadata
        if method2_calls:
            self.assertEqual(method2_calls[0].metadata.get("call_type"), "attribute")
    
    def test_circular_dependency_detection(self):
        """Test detection of circular dependencies."""
        # Create a test file with circular dependencies
        test_file = os.path.join(self.test_dir, "test_circular.py")
        with open(test_file, "w") as f:
            f.write("""
def function_a():
    return function_b()

def function_b():
    return function_c()
    
def function_c():
    return function_a()
""")
        
        # Parse the file
        self.parser.parse_file(test_file)
        self.parser._process_function_calls()
        
        # Use the dependency analyzer to detect circular dependencies
        dependency_analyzer = DependencyAnalyzer(self.knowledge_graph)
        circular_deps = dependency_analyzer.find_circular_dependencies()
        
        # Verify that we found a circular dependency
        self.assertTrue(len(circular_deps) > 0, "Should detect circular dependencies")
        
        # Get the components for verification
        module = self.knowledge_graph.get_component_by_name("test_circular")[0]
        
        # Find the function components
        functions = {}
        for rel in self.knowledge_graph.get_relationships_by_source(module.id):
            target = self.knowledge_graph.get_component_by_id(rel.target_id)
            if target and target.type == "function":
                functions[target.name] = target
        
        # Verify that the circular dependency involves all three functions
        if circular_deps:
            # Get the component names from the IDs in the circular dependency
            cycle = circular_deps[0]
            cycle_names = [self.knowledge_graph.get_component_by_id(comp_id).name 
                         for comp_id in cycle if self.knowledge_graph.get_component_by_id(comp_id)]
            
            self.assertEqual(len(cycle_names), 4, "Circular dependency should involve 3 functions plus a duplicate")
            self.assertIn("function_a", cycle_names, "function_a should be in the cycle")
            self.assertIn("function_b", cycle_names, "function_b should be in the cycle")
            self.assertIn("function_c", cycle_names, "function_c should be in the cycle")


if __name__ == "__main__":
    unittest.main() 