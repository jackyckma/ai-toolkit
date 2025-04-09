"""
Testing Agent for the AI-Native Development Toolkit.

This agent specializes in creating comprehensive tests and
identifying edge cases for code.
"""

import logging
import os
from typing import Dict, List, Optional, Any
import json
import re

from dotenv import load_dotenv

from ai_toolkit.kb.graph import KnowledgeGraph
from .base import Agent

# Load environment variables
load_dotenv()


class TestingAgent(Agent):
    """
    Testing agent that specializes in creating tests.
    
    The testing agent is responsible for:
    1. Creating comprehensive tests for code
    2. Identifying edge cases and boundary conditions
    3. Ensuring test coverage is adequate
    4. Following testing best practices
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the testing agent.
        
        Args:
            knowledge_graph: The knowledge graph to use for context
        """
        # Define the system message for the testing agent
        testing_system_message = """
        You are the Testing agent in the AI-Native Development Toolkit.
        
        Your primary responsibilities are:
        
        1. Create comprehensive tests for code components
        2. Identify edge cases, boundary conditions, and failure modes
        3. Ensure adequate test coverage for all code paths
        4. Follow testing best practices for the target language and framework
        5. Consider both unit tests and integration tests when appropriate
        
        When writing tests:
        - Include all necessary imports and test setup
        - Test both happy paths and error cases
        - Use appropriate assertions for validation
        - Organize tests logically and make them maintainable
        - Follow testing conventions for the target language
        
        Always return your final test code within triple backticks with the language specified:
        ```python
        def test_example():
            # Arrange
            input_data = "test"
            
            # Act
            result = example(input_data)
            
            # Assert
            assert result == "Hello, test!"
        ```
        
        Also provide a test coverage analysis that lists:
        1. What cases are being tested
        2. Any edge cases or error conditions being verified
        3. Suggestions for additional tests that might be useful
        """
        
        # Call the parent constructor with the testing-specific parameters
        super().__init__(
            name="testingagent",
            knowledge_graph=knowledge_graph,
            model=os.getenv("TEST_AGENT_MODEL", "gpt-4-turbo"),
            system_message=testing_system_message,
        )
    
    def _process_result(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process the result from the Autogen agent, extracting test code blocks.
        
        Args:
            messages: The messages from the Autogen agent
            
        Returns:
            The processed result with extracted test code
        """
        if not messages:
            return {"status": "error", "error": "No response from testing agent"}
        
        last_message = messages[-1]["content"]
        
        # Extract code blocks from the message
        test_blocks = self._extract_code_blocks(last_message)
        
        # Extract test coverage analysis
        coverage_analysis = self._extract_coverage_analysis(last_message)
        
        # Return the message, extracted test blocks, and coverage analysis
        return {
            "status": "success",
            "content": last_message,
            "test_blocks": test_blocks,
            "coverage_analysis": coverage_analysis,
            "agent": self.name,
            "agent_id": self.id,
        }
    
    def _extract_code_blocks(self, text: str) -> List[Dict[str, str]]:
        """
        Extract code blocks from text.
        
        Args:
            text: The text to extract code blocks from
            
        Returns:
            A list of dictionaries containing language and code
        """
        # Regex pattern to match code blocks with optional language
        pattern = r"```([\w\-+#]*)\n([\s\S]*?)```"
        
        # Find all code blocks
        matches = re.findall(pattern, text)
        
        # Convert matches to dictionaries
        code_blocks = []
        for language, code in matches:
            code_blocks.append({
                "language": language.strip() or "text",
                "code": code.strip(),
            })
        
        return code_blocks
    
    def _extract_coverage_analysis(self, text: str) -> Dict[str, List[str]]:
        """
        Extract test coverage analysis from text.
        
        Args:
            text: The text to extract coverage analysis from
            
        Returns:
            A dictionary with coverage analysis categories
        """
        # Initialize coverage categories
        coverage = {
            "tested_cases": [],
            "edge_cases": [],
            "suggestions": []
        }
        
        # Look for coverage analysis sections
        lines = text.split("\n")
        current_section = None
        
        for line in lines:
            line = line.strip()
            
            # Check for section headers
            if re.match(r"^#+\s+Test(ed)?\s+Cases", line, re.IGNORECASE):
                current_section = "tested_cases"
                continue
            elif re.match(r"^#+\s+Edge\s+Cases", line, re.IGNORECASE):
                current_section = "edge_cases"
                continue
            elif re.match(r"^#+\s+Suggestions", line, re.IGNORECASE) or re.match(r"^#+\s+Additional\s+Tests", line, re.IGNORECASE):
                current_section = "suggestions"
                continue
            
            # Add content to the current section
            if current_section and line and line.startswith("- "):
                item = line[2:].strip()
                coverage[current_section].append(item)
            elif current_section and line and line.startswith("* "):
                item = line[2:].strip()
                coverage[current_section].append(item)
            elif current_section and line and re.match(r"^\d+\.\s+", line):
                item = re.sub(r"^\d+\.\s+", "", line).strip()
                coverage[current_section].append(item)
        
        return coverage 