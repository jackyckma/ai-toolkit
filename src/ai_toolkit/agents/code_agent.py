"""
Code Generation Agent for the AI-Native Development Toolkit.

This agent specializes in writing high-quality, maintainable code
based on specifications and requirements.
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


class CodeGenerationAgent(Agent):
    """
    Code Generation agent that specializes in writing code.
    
    The code agent is responsible for:
    1. Writing clean, maintainable code based on specifications
    2. Following best practices and established patterns
    3. Ensuring code is secure, efficient, and well-documented
    4. Adapting to the style and conventions of the project
    """
    
    def __init__(self, knowledge_graph: KnowledgeGraph):
        """
        Initialize the code generation agent.
        
        Args:
            knowledge_graph: The knowledge graph to use for context
        """
        # Define the system message for the code generator
        code_system_message = """
        You are the Code Generation agent in the AI-Native Development Toolkit.
        
        Your primary responsibilities are:
        
        1. Write clean, maintainable, and efficient code based on specifications
        2. Follow best practices and established patterns for the target language
        3. Ensure code is secure, handles edge cases, and is well-documented
        4. Adapt to the style and conventions of the existing project
        5. Reuse existing components when appropriate
        
        When writing code:
        - Include all necessary imports and dependencies
        - Add comments to explain complex logic
        - Handle errors and edge cases appropriately
        - Follow language-specific conventions and style guides
        - Test your code mentally to ensure it works as expected
        
        Always return your final code within triple backticks with the language specified:
        ```python
        def example():
            # Your code here
            return "Hello, world!"
        ```
        
        For complex solutions, break down your approach before writing the actual code.
        Also provide any instructions needed for integrating the code into the project.
        """
        
        # Call the parent constructor with the code generator-specific parameters
        super().__init__(
            name="codegenerationagent",
            knowledge_graph=knowledge_graph,
            model=os.getenv("CODE_AGENT_MODEL", "gpt-4-turbo"),
            system_message=code_system_message,
        )
    
    def _process_result(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Process the result messages from the agent.
        
        Args:
            messages: The messages from the agent
            
        Returns:
            The processed result
        """
        self.logger.info(f"Processing {len(messages)} messages from code agent")
        
        # Find assistant messages with content
        assistant_messages = [m for m in messages if m.get("role") == "assistant" and m.get("content")]
        
        if not assistant_messages:
            return {
                "status": "error",
                "error": "No response from code generation agent",
                "agent": self.name,
                "agent_id": self.id,
            }
        
        # Get all code blocks from all messages
        all_code_blocks = []
        final_message = assistant_messages[-1]["content"]
        
        # Process each message to extract code blocks
        for message in assistant_messages:
            content = message.get("content", "")
            
            # Extract code blocks from the message
            pattern = r"```(?:python)?\s*\n(.*?)```"
            matches = re.findall(pattern, content, re.DOTALL)
            
            for match in matches:
                code_block = match.strip()
                if code_block and code_block not in all_code_blocks:
                    all_code_blocks.append(code_block)
        
        # Create the result object
        result = {
            "status": "success",
            "message": final_message,
            "code": all_code_blocks,
            "agent": self.name,
            "agent_id": self.id,
        }
        
        # Log what we found
        self.logger.info(f"Extracted {len(all_code_blocks)} code blocks from messages")
        
        return result
    
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