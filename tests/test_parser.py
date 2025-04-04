#!/usr/bin/env python3
"""
Test script for the Parser component of the AI-Native Development Toolkit.

This script demonstrates the basic functionality of the Python parser by:
1. Creating a test Python file with various components
2. Parsing the file with PythonParser
3. Verifying that components and relationships are created correctly
"""

import os
import sys
import json
from pathlib import Path

# Add the src directory to the path so we can import the toolkit
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ai_toolkit.kb.graph import KnowledgeGraph
from src.ai_toolkit.parser.python import PythonParser

# Create a test directory and file if they don't exist
TEST_DIR = Path("tests/test_files")
TEST_DIR.mkdir(exist_ok=True, parents=True)

TEST_FILE = TEST_DIR / "test_sample.py"

# Create a sample Python file for testing
SAMPLE_CODE = '''"""
Sample module for testing the Parser component.
"""

import os
import sys
from pathlib import Path
from typing import List, Dict, Optional, Any

# A module-level constant
MAX_ITEMS = 100

class BaseClass:
    """A base class for testing inheritance."""
    
    def __init__(self, name: str):
        self.name = name
    
    def get_name(self) -> str:
        """Return the name."""
        return self.name

class TestClass(BaseClass):
    """A test class with various methods and attributes."""
    
    # Class attribute
    default_value = 42
    
    def __init__(self, name: str, value: int = 0):
        """Initialize the test class."""
        super().__init__(name)
        self.value = value
    
    def calculate(self, x: int, y: int) -> int:
        """Calculate something."""
        return x + y + self.value
    
    def process_items(self, items: List[str]) -> Dict[str, int]:
        """Process a list of items and return a dictionary."""
        result = {}
        for item in items:
            result[item] = len(item)
            if len(result) > MAX_ITEMS:
                break
        return result

def utility_function(value: int) -> bool:
    """A utility function."""
    return value > 0

def process_data(data: Dict[str, Any]) -> Optional[List[str]]:
    """Process some data using the TestClass."""
    if not data:
        return None
    
    test = TestClass("processor", value=10)
    
    # Call methods on the class
    result = test.calculate(len(data), 5)
    
    # Call other functions
    is_positive = utility_function(result)
    
    if is_positive:
        return list(data.keys())
    return None
'''

# Write the sample code to the test file
with open(TEST_FILE, "w") as f:
    f.write(SAMPLE_CODE)

def main():
    """Run the parser test."""
    print("Testing AI-Native Development Toolkit Parser Component")
    print("-" * 60)
    
    # Create a knowledge graph
    kb_dir = Path("tests/kb")
    kb_dir.mkdir(exist_ok=True, parents=True)
    
    # Create necessary directories for KB
    (kb_dir / "kb").mkdir(exist_ok=True, parents=True)
    (kb_dir / "config").mkdir(exist_ok=True, parents=True)
    
    graph = KnowledgeGraph(kb_dir)
    
    # Create a parser
    parser = PythonParser(graph)
    
    # Parse the test file
    print(f"Parsing file: {TEST_FILE}")
    module = parser.parse_file(TEST_FILE)
    
    if not module:
        print("Error: Failed to parse the test file")
        return
    
    print(f"Successfully parsed module: {module.name}")
    print(f"Module ID: {module.id}")
    
    # Print components in the knowledge graph
    components = list(graph.get_all_components())
    print(f"Total components found: {len(components)}")
    
    # Group components by type
    component_types = {}
    for comp in components:
        if comp.type not in component_types:
            component_types[comp.type] = []
        component_types[comp.type].append(comp)
    
    for comp_type, comps in component_types.items():
        print(f"{comp_type.capitalize()}s: {len(comps)}")
        for comp in comps:
            if comp_type == "module" and comp.metadata.get("imported", False):
                # Skip details for imported modules
                continue
            print(f"  - {comp.name}")
    
    # Get relationships
    relationships = list(graph.get_all_relationships())
    print(f"Total relationships found: {len(relationships)}")
    
    # Group relationships by type
    relationship_types = {}
    for rel in relationships:
        if rel.type not in relationship_types:
            relationship_types[rel.type] = []
        relationship_types[rel.type].append(rel)
    
    for rel_type, rels in relationship_types.items():
        print(f"{rel_type.capitalize()} relationships: {len(rels)}")
    
    # Find test class component
    test_class = None
    for comp in components:
        if comp.name == "TestClass" and comp.type == "class":
            test_class = comp
            break
    
    if test_class:
        print("\nInspecting TestClass component:")
        print(f"  ID: {test_class.id}")
        print(f"  Type: {test_class.type}")
        print(f"  File: {test_class.file_path}")
        print(f"  Line number: {test_class.line_number}-{test_class.line_end}")
        print(f"  Metadata:")
        for key, value in test_class.metadata.items():
            if key == "source":
                # Truncate source code in output
                print(f"    {key}: [truncated]")
            elif isinstance(value, list) and value:
                print(f"    {key}: {value}")
            elif not isinstance(value, list):
                print(f"    {key}: {value}")
    
    # Find process_data function component
    process_data_func = None
    for comp in components:
        if comp.name == "process_data" and comp.type == "function":
            process_data_func = comp
            break
    
    if process_data_func:
        print("\nInspecting process_data function component:")
        print(f"  ID: {process_data_func.id}")
        print(f"  Type: {process_data_func.type}")
        print(f"  File: {process_data_func.file_path}")
        print(f"  Line number: {process_data_func.line_number}-{process_data_func.line_end}")
        print(f"  Metadata:")
        for key, value in process_data_func.metadata.items():
            if key == "source":
                # Truncate source code in output
                print(f"    {key}: [truncated]")
            elif isinstance(value, list) and value:
                print(f"    {key}: {value}")
            elif not isinstance(value, list):
                print(f"    {key}: {value}")
            elif key == "function_calls":
                print(f"    {key}: {value}")
    
    print("\nTest completed successfully!")
    
    # Save the knowledge graph
    graph.save()

if __name__ == "__main__":
    main() 